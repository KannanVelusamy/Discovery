"""Simplified LangGraph agent using DeepAgents with MCP integration.

This implementation uses create_deep_agent from the deepagents library
with Runtime Context pattern for username handling.

Key Features:
- Uses ToolRuntime for accessing username in tools
- Username passed as immutable context (not mutable state)
- Tools automatically get username via runtime.context.username
- Follows official LangChain best practices
"""
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from deepagents import create_deep_agent
import subprocess
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MCP server paths
MCP_BASE_PATH = os.getenv("MCP_BASE_PATH", "/Users/kannan/DPAS/discovery/mcp")
ENTITLEMENT_MCP = f"{MCP_BASE_PATH}/entitlement_mcp.py"
# Using mock Denodo for testing (no real database required)
DENODO_MCP = f"{MCP_BASE_PATH}/denodo_mcp_mock.py"


# Define Custom State Schema (username from frontend)
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from typing_extensions import NotRequired

class CustomAgentState(AgentState):
    """Custom agent state that includes username from frontend.
    
    Frontend sends: { messages: [...], username: "pe06003" }
    Tools access: runtime.state["username"]
    """
    username: NotRequired[str]  # Username from SSO authentication


# Middleware to define state schema and validate username
class UsernameMiddleware(AgentMiddleware[CustomAgentState]):
    """Middleware that defines custom state schema with username."""
    
    state_schema = CustomAgentState
    
    def before_agent(self, state: CustomAgentState, runtime) -> dict | None:
        """Validate username is present and log it."""
        username = state.get("username")
        
        if not username:
            print("⚠️  Warning: Username not provided in state")
            return None
        
        print(f"🔑 User: {username}")
        return None


def call_mcp_tool(mcp_path: str, tool_name: str, arguments: dict) -> dict:
    """
    Call MCP server tool via subprocess with JSON-RPC protocol.
    
    Args:
        mcp_path: Path to MCP server Python file
        tool_name: Name of the tool to call
        arguments: Tool arguments as dictionary
        
    Returns:
        Result dictionary from MCP server
    """
    try:
        print(f"🔧 Calling MCP: {tool_name}")
        
        # Determine Python executable
        mcp_dir = os.path.dirname(mcp_path)
        mcp_venv_python = os.path.join(mcp_dir, "venv", "bin", "python")
        python_cmd = mcp_venv_python if os.path.exists(mcp_venv_python) else "python3"
        
        # MCP JSON-RPC requests
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "discovery-agent", "version": "1.0.0"}
            }
        }
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }
        
        # Execute MCP server
        import time
        process = subprocess.Popen(
            [python_cmd, mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        try:
            # Send init request
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            init_response = process.stdout.readline()
            
            # Send tool request
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            tool_response = process.stdout.readline()
            
            # Cleanup
            process.stdin.close()
            time.sleep(0.5)
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Parse responses
            responses = []
            for line in [init_response, tool_response]:
                line = line.strip()
                if line and line.startswith('{'):
                    try:
                        responses.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Find tool response (id=1)
            tool_resp = next((r for r in responses if r.get("id") == 1), None)
            
            if not tool_resp:
                return {"error": "No tool response from MCP server"}
            
            if "error" in tool_resp:
                return {"error": f"MCP error: {tool_resp['error'].get('message', str(tool_resp['error']))}"}
            
            if "result" not in tool_resp:
                return {"error": "No result from MCP server"}
            
            # Extract content
            result_data = tool_resp["result"]
            if "content" in result_data and len(result_data["content"]) > 0:
                text_content = result_data["content"][0]["text"]
                return json.loads(text_content)
            
            return {"error": "MCP result missing content"}
            
        except Exception as e:
            process.kill()
            process.wait()
            print(f"❌ MCP communication error: {e}")
            return {"error": f"MCP communication error: {str(e)}"}
            
    except Exception as e:
        print(f"❌ MCP call failed: {e}")
        return {"error": f"Failed to call MCP: {str(e)}"}


# Define tools with ToolRuntime for state access
@tool
def check_user_entitlement(runtime: ToolRuntime[CustomAgentState]) -> str:
    """
    Check user entitlement and retrieve user profile with roles.
    
    Automatically uses the username from the runtime state (SSO authentication).
    No need to pass username as a parameter - it's available via runtime.state["username"].
        
    Returns:
        JSON string with user profile including roles, status, and permissions
    """
    # Access username from runtime state (from frontend)
    username = runtime.state.get("username", "unknown")
    
    if not username:
        return json.dumps({"error": "Username is required"})
    
    print(f"🔍 Checking entitlement for: {username}")
    
    result = call_mcp_tool(ENTITLEMENT_MCP, "check_user_entitlement", {"username": username})
    
    if "error" in result:
        return json.dumps({"error": result["error"], "username": username})
    
    profile = result.get("data", {}).get("profile", {})
    
    return json.dumps({
        "success": True,
        "username": username,
        "profile": profile,
        "roles": profile.get("role", []),
        "status": profile.get("status"),
        "email": profile.get("email"),
        "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
        "employee_id": profile.get("employeeId")
    })


@tool
def query_accounts_by_roles(
    roles: List[str],
    filters: dict = None,
    include_balance: bool = True,
    include_details: bool = True
) -> str:
    """
    Query account data from Denodo database based on user roles.
    
    Args:
        roles: List of user roles from entitlement check
        filters: Optional filters (account_number, account_status, min_balance, limit)
        include_balance: Whether to include balance information
        include_details: Whether to include detailed account information
        
    Returns:
        JSON string with account data filtered by user roles
    """
    print(f"📊 Querying accounts for roles: {roles}")
    
    result = call_mcp_tool(
        DENODO_MCP,
        "query_accounts_by_roles",
        {
            "roles": roles,
            "filters": filters or {},
            "include_balance": include_balance,
            "include_details": include_details
        }
    )
    
    if "error" in result:
        return json.dumps({"error": result["error"], "roles": roles})
    
    return json.dumps({
        "success": True,
        "accounts": result.get("accounts", []),
        "total_count": result.get("total_count", 0),
        "roles_used": roles
    })


@tool
def get_account_summary(roles: List[str]) -> str:
    """
    Get summary statistics of accounts accessible to the user.
    
    Args:
        roles: List of user roles from entitlement check
        
    Returns:
        JSON string with account summary statistics
    """
    print(f"📈 Getting account summary for roles: {roles}")
    
    result = call_mcp_tool(DENODO_MCP, "get_account_summary", {"roles": roles})
    
    if "error" in result:
        return json.dumps({"error": result["error"], "roles": roles})
    
    return json.dumps({
        "success": True,
        "summary": result.get("summary", []),
        "roles": roles
    })


@tool
def get_account_detail(account_number: str, roles: List[str]) -> str:
    """
    Get detailed information for a specific account.
    
    Args:
        account_number: The account number to query
        roles: User's roles for access verification
        
    Returns:
        JSON string with detailed account information or access denied message
    """
    print(f"🔍 Getting detail for account: {account_number}")
    
    result = call_mcp_tool(
        DENODO_MCP,
        "get_account_detail",
        {"account_number": account_number, "roles": roles}
    )
    
    if "error" in result:
        return json.dumps({
            "error": result["error"],
            "account_number": account_number,
            "access_denied": True
        })
    
    return json.dumps({
        "success": True,
        "account": result.get("account", {}),
        "access_granted": result.get("access_granted", False)
    })


# System prompt template - will be enhanced with username dynamically
BASE_SYSTEM_PROMPT = """You are an intelligent AI assistant with access to user entitlement and account data.

You can help users with:
- Checking their account information and balances
- Viewing account details based on their access permissions
- Getting summaries of their accessible accounts
- Answering questions about their financial data

## Available Tools
You have access to the following tools that automatically use the authenticated user's credentials:

1. **check_user_entitlement**: Retrieves the user's profile, roles, and permissions
   - Use this when you need to know what the user can access
   - No parameters needed - automatically uses the authenticated username

2. **query_accounts_by_roles**: Queries accounts based on user's roles
   - Use this to get a list of accounts the user can access
   - Requires roles from check_user_entitlement

3. **get_account_summary**: Gets summary statistics of accessible accounts
   - Use this for overview/summary requests

4. **get_account_detail**: Gets detailed information for a specific account
   - Use this when user asks about a specific account number

## Workflow for Account Queries
When a user asks about accounts or balances:
1. **First**, call check_user_entitlement to get their roles and permissions
2. **Then**, use the returned roles with query_accounts_by_roles or other tools
3. **Finally**, present the information in a clear, user-friendly format

## Important Notes
- The username is automatically provided to all tools - you don't need to ask for it
- Always check entitlements FIRST before accessing any account data
- Only show data the user is authorized to access based on their roles
- Be transparent about access restrictions
- Protect sensitive financial information

## Conversational Guidelines
- Be helpful, accurate, and security-conscious
- If the user asks a general question, answer it directly without calling tools
- Only call tools when you actually need to retrieve or check data
- Explain what you're doing when you call tools

Always respect user permissions and provide clear, helpful responses."""


# Dynamic prompt middleware - injects username into system prompt
@dynamic_prompt
def username_prompt(request: ModelRequest) -> str:
    """
    Dynamically inject username into system prompt.
    
    This middleware:
    1. Accesses username from request.state (NOT runtime.state)
    2. Enhances base system prompt with username
    3. Returns the enhanced prompt to the agent
    
    The agent sees the username and can reference it in responses.
    """
    # Access username directly from request.state
    username = request.state.get("username", "unknown")
    
    print(f"🔑 User: {username}")
    
    # Enhance base prompt with username
    enhanced_prompt = BASE_SYSTEM_PROMPT
    if username and username != "unknown":
        enhanced_prompt += f"\n\n## Current User\nUsername: {username}\nAll tools automatically use this username - no need to pass it as a parameter."
    
    return enhanced_prompt


# Create DeepAgent with middleware (state schema defined in UsernameMiddleware)
# DeepAgents automatically creates the graph with nodes and edges
# Username flows: Frontend → State → Tools/Middleware
graph = create_deep_agent(
    model=ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True),
    tools=[
        check_user_entitlement,
        query_accounts_by_roles,
        get_account_summary,
        get_account_detail
    ],
    system_prompt=BASE_SYSTEM_PROMPT,  # Base prompt (enhanced by middleware)
    middleware=[
        UsernameMiddleware(),  # Defines state schema with username field
        username_prompt,  # Dynamic prompt injection
    ],
)


# Utility function for testing (optional - mainly for frontend integration)
def test_agent(username: str, query: str):
    """
    Test the agent with a username and query.
    This is mainly for standalone testing. Frontend integration works differently.
    
    Args:
        username: User to test with
        query: Query to ask the agent
    """
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Include username in the system prompt for the test
    system_prompt = get_system_prompt(username)
    
    state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ],
    }
    
    result = graph.invoke(state)
    
    return result["messages"][-1].content


if __name__ == "__main__":
    # Standalone test - only runs when executing this file directly
    # For production use: langgraph dev
    print("\n" + "="*60)
    print("✅ DeepAgents Graph Loaded Successfully")
    print("="*60)
    print("\nTo start the LangGraph server:")
    print("  cd /Users/kannan/DPAS/discovery/backend/agent")
    print("  source ../venv/bin/activate")
    print("  langgraph dev")
    print("\nServer will be available at:")
    print("  - Backend API: http://localhost:2024")
    print("  - LangGraph Studio: http://localhost:2024/studio")
    print("\n" + "="*60 + "\n")

