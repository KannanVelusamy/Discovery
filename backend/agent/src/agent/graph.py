"""LangGraph agent using DeepAgents with MCP tool integration.

This agent uses DeepAgents framework to handle:
- Entitlement checking via entitlement_mcp
- Account data retrieval via denodo_mcp
- Dynamic role-based access control
"""
from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
import subprocess
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System prompt for the agent
SYSTEM_PROMPT = """You are an intelligent AI assistant with access to user entitlement and account data.

You can help users with:
- Checking their account information and balances
- Viewing account details based on their access permissions
- Getting summaries of their accessible accounts
- Answering questions about their financial data

You have access to the following capabilities:
1. Check user entitlements and roles
2. Query account data from Denodo database (filtered by user roles)
3. Get account summaries and specific account details

Always respect user permissions and only show data they are authorized to access based on their roles.
Be helpful, accurate, and security-conscious in your responses."""


# Define the enhanced state for the agent
class AgentState(TypedDict):
    """State for the conversational agent with user context."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    username: str | None
    user_profile: dict | None
    roles: List[str] | None


# MCP server paths
MCP_BASE_PATH = os.getenv("MCP_BASE_PATH", "/Users/kannan/DPAS/discovery/mcp")
ENTITLEMENT_MCP = f"{MCP_BASE_PATH}/entitlement_mcp.py"
DENODO_MCP = f"{MCP_BASE_PATH}/denodo_mcp.py"


def call_mcp_tool(mcp_path: str, tool_name: str, arguments: dict) -> dict:
    """
    Generic function to call any MCP server tool.
    
    Args:
        mcp_path: Path to MCP server Python file
        tool_name: Name of the tool to call
        arguments: Tool arguments as dictionary
        
    Returns:
        Result dictionary from MCP server
    """
    try:
        print(f"🔧 Calling MCP: {tool_name} at {mcp_path}")
        
        # Determine the Python executable to use
        mcp_dir = os.path.dirname(mcp_path)
        mcp_venv_python = os.path.join(mcp_dir, "venv", "bin", "python")
        
        if os.path.exists(mcp_venv_python):
            python_cmd = mcp_venv_python
            print(f"   Using MCP venv Python: {python_cmd}")
        else:
            python_cmd = "python3"
            print(f"   ⚠️  MCP venv not found, using system python3")
        
        # MCP protocol requires initialization before tool calls
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "discovery-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Use Popen for real-time communication with MCP server
        import time
        process = subprocess.Popen(
            [python_cmd, mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        try:
            # Send initialization request first
            print(f"   Sending initialization request...")
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response
            init_response_line = process.stdout.readline()
            print(f"   Init response: {init_response_line.strip()[:100]}")
            
            # Now send tool call request
            print(f"   Sending tool call request...")
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            # Read tool response
            tool_response_line = process.stdout.readline()
            print(f"   Tool response: {tool_response_line.strip()[:100]}")
            
            # Collect both responses
            stdout = init_response_line + tool_response_line
            
            # Now we can close stdin
            process.stdin.close()
            
            # Give it a moment to finish
            time.sleep(0.5)
            
            # Terminate the server gracefully
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            stderr = process.stderr.read() if process.stderr else ""
            
            print(f"   MCP return code: {process.returncode}")
            print(f"   Collected responses")
            
        except Exception as e:
            process.kill()
            process.wait()
            print(f"❌ Error during MCP communication: {e}")
            import traceback
            print(traceback.format_exc())
            return {"error": f"MCP communication error: {str(e)}"}
        
        # Parse stdout even if return code is non-zero
        if not stdout.strip():
            print(f"❌ MCP returned empty stdout")
            if stderr:
                print(f"   stderr: {stderr[:500]}")
            return {"error": "MCP server returned empty response"}
        
        # Parse responses - MCP returns multiple JSON-RPC responses
        responses = []
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            # Skip non-JSON lines (like log messages)
            if not line.startswith('{'):
                continue
            try:
                resp = json.loads(line)
                responses.append(resp)
                print(f"   Parsed response: id={resp.get('id')}, keys={list(resp.keys())}")
            except json.JSONDecodeError as e:
                print(f"   Skipping non-JSON line: {line[:100]} (error: {e})")
        
        print(f"   Received {len(responses)} JSON-RPC responses from MCP")
        
        if not responses:
            print(f"❌ No valid JSON-RPC responses found")
            print(f"   Full stdout ({len(stdout)} chars):")
            for i, line in enumerate(stdout.split('\n')[:20]):  # First 20 lines
                print(f"   Line {i}: {line[:150]}")
            return {"error": "No valid responses from MCP server"}
        
        # Find the tool call response (id=1)
        tool_response = None
        for resp in responses:
            if resp.get("id") == 1:
                tool_response = resp
                break
        
        if not tool_response:
            print(f"❌ No tool response found (id=1)")
            print(f"   Available response IDs: {[r.get('id') for r in responses]}")
            return {"error": "No tool response from MCP server"}
        
        print(f"   Tool response keys: {tool_response.keys()}")
        
        if "error" in tool_response:
            error = tool_response["error"]
            print(f"❌ MCP returned error in response: {error}")
            return {"error": f"MCP error: {error.get('message', str(error))}"}
        
        if "result" not in tool_response:
            print(f"❌ No result field in tool response")
            return {"error": "No result from MCP server"}
        
        # Parse the result
        result_data = tool_response["result"]
        
        # MCP returns result with content array
        if "content" in result_data and len(result_data["content"]) > 0:
            text_content = result_data["content"][0]["text"]
            data = json.loads(text_content)
            print(f"✅ MCP call successful: {tool_name}")
            if process.returncode != 0:
                print(f"   ℹ️  MCP process exited with code {process.returncode} after sending response")
            return data
        else:
            print(f"❌ MCP result missing content: {result_data}")
            return {"error": "MCP result missing content"}
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        if 'stdout' in locals():
            print(f"   Stdout: {stdout[:500]}")
        return {"error": f"Invalid JSON from MCP: {str(e)}"}
    except Exception as e:
        print(f"❌ Exception calling MCP: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"error": f"Failed to call MCP: {str(e)}"}


# Define LangChain tools that wrap MCP servers
@tool
def check_user_entitlement(username: str) -> str:
    """
    Check user entitlement and retrieve user profile with roles.
    
    This tool calls the entitlement MCP server to get user information including
    their roles, which determine what data they can access.
    
    Args:
        username: The username to check entitlement for
        
    Returns:
        JSON string with user profile including roles, status, and permissions
    """
    if not username:
        return json.dumps({"error": "Username is required", "username": None})
    
    print(f"🔍 Tool: Checking entitlement for {username}")
    
    result = call_mcp_tool(
        ENTITLEMENT_MCP,
        "check_user_entitlement",
        {"username": username}
    )
    
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
    
    This tool retrieves account information that the user is authorized to access
    based on their entitlement roles. It queries three tables:
    - RCAT0300: Account-role mapping
    - RPBT0100: Account details
    - RPBT0200: Account balances
    
    Args:
        roles: List of user roles from entitlement check
        filters: Optional filters (account_number, account_status, min_balance, limit)
        include_balance: Whether to include balance information
        include_details: Whether to include detailed account information
        
    Returns:
        JSON string with account data filtered by user roles
    """
    print(f"📊 Tool: Querying accounts for roles: {roles}")
    
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
        "roles_used": roles,
        "query_metadata": result.get("query_metadata", {})
    })


@tool
def get_account_summary(roles: List[str]) -> str:
    """
    Get summary statistics of accounts accessible to the user.
    
    Provides aggregate information like total accounts, total balance,
    and total clients accessible based on user roles.
    
    Args:
        roles: List of user roles from entitlement check
        
    Returns:
        JSON string with account summary statistics
    """
    print(f"📈 Tool: Getting account summary for roles: {roles}")
    
    result = call_mcp_tool(
        DENODO_MCP,
        "get_account_summary",
        {"roles": roles}
    )
    
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
    
    Retrieves complete account information including balance and client details,
    but only if the user's roles grant access to this account.
    
    Args:
        account_number: The account number to query
        roles: User's roles for access verification
        
    Returns:
        JSON string with detailed account information or access denied message
    """
    print(f"🔍 Tool: Getting detail for account {account_number}")
    
    result = call_mcp_tool(
        DENODO_MCP,
        "get_account_detail",
        {
            "account_number": account_number,
            "roles": roles
        }
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


# Collect all tools
tools = [
    check_user_entitlement,
    query_accounts_by_roles,
    get_account_summary,
    get_account_detail
]


# Initialize the LLM with tools bound
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    streaming=True
)

# Bind tools to the model
model_with_tools = model.bind_tools(tools)


def call_model(state: AgentState) -> dict:
    """Call the model with the current state."""
    messages = state["messages"]
    
    # Get username from state (passed from frontend)
    username = state.get("username")
    
    # Prepend system message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        # Include username context in system message if available
        system_content = SYSTEM_PROMPT
        if username:
            system_content += f"\n\nCurrent user: {username}\nWhen checking entitlements or querying accounts, use this username."
        messages = [SystemMessage(content=system_content)] + list(messages)
    
    # Call the model
    response = model_with_tools.invoke(messages)
    
    print(f"🤖 Agent response - username in context: {username}")
    
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Determine whether to continue or end the agent loop."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are no tool calls, end the loop
    if not last_message.tool_calls:
        return END
    return "tools"


def create_agent_graph():
    """
    Create the DeepAgents-powered agent graph with MCP tools.
    
    This creates a ReAct-style agent that can:
    1. Check user entitlements
    2. Query Denodo based on roles
    3. Reason about what data to retrieve
    4. Respond to user queries with appropriate data
    """
    print("🤖 Creating DeepAgents agent with MCP tools...")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set the entry point
    workflow.add_edge(START, "agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tools are called, go back to the agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    agent = workflow.compile()
    
    print("✅ Agent created successfully")
    
    return agent


# Export the compiled graph
graph = create_agent_graph()


# Utility function for manual testing
def test_agent(username: str, query: str):
    """
    Test the agent with a username and query.
    
    Args:
        username: User to test with
        query: Query to ask the agent
    """
    from langchain_core.messages import HumanMessage
    
    state = {
        "messages": [HumanMessage(content=query)],
        "username": username,
        "user_profile": None,
        "roles": None
    }
    
    result = graph.invoke(state)
    
    return result["messages"][-1].content


if __name__ == "__main__":
    # Test the agent
    print("\n" + "="*60)
    print("Testing DeepAgents with MCP integration")
    print("="*60 + "\n")
    
    # Example test
    response = test_agent(
        username="kannan.velusamy",
        query="Can you check my entitlement and show me my accessible accounts?"
    )
    
    print(f"\nAgent Response:\n{response}\n")