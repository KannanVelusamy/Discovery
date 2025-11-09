# MCP Servers

This directory contains Model Context Protocol (MCP) servers for the Discovery Agent project.

## What is MCP?

MCP (Model Context Protocol) is a standardized way for AI agents to interact with external tools and services. MCP servers expose tools that AI agents can discover and use.

## Available MCP Servers

### 1. Entitlement MCP Server (`entitlement_mcp.py`)

**Purpose:** Provides user entitlement and profile checking capabilities.

**Tool:** `check_user_entitlement`

**Description:** Checks user entitlement and profile information from the security API.

**Input:**
```json
{
  "username": "string (e.g., pe06003)"
}
```

**Output:**
```json
{
  "data": {
    "profile": {
      "email": "user@company.com",
      "employeeId": "PE06003",
      "firstName": "John",
      "lastName": "Doe",
      "role": ["ABCD", "EFGH", "XYZ1"],
      "status": "Active",
      "username": "pe06003"
    }
  }
}
```

---

## Running MCP Servers

### Entitlement MCP Server

```bash
cd /Users/kannan/DPAS/discovery/mcp
python entitlement_mcp.py
```

**Requirements:**
- Python 3.8+
- Required packages: `httpx`, `mcp`

**Environment:**
- Uses the profile API at `https://localhost:8080/services/security/profile`
- Disables SSL verification for development (configure for production)

---

## How AI Agents Use MCP Servers

MCP servers run as standalone processes that AI agents can connect to via stdio (standard input/output). The agent can:

1. **Discover available tools** - Query what tools the MCP server provides
2. **Call tools** - Execute tools with specific parameters
3. **Receive results** - Get structured responses back

### Example: Agent Using Entitlement MCP

```python
# AI agent code (conceptual)
async with mcp_client.connect("entitlement-server") as client:
    # List available tools
    tools = await client.list_tools()
    
    # Call the entitlement check tool
    result = await client.call_tool(
        "check_user_entitlement",
        {"username": "pe06003"}
    )
    
    # Process the result
    profile = json.loads(result.content)
    print(f"User status: {profile['data']['profile']['status']}")
```

---

## Integration with LangGraph

MCP servers can be integrated with LangGraph agents to provide additional capabilities:

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

# Wrap MCP tool as a LangChain tool
@tool
async def check_entitlement(username: str) -> dict:
    """Check user entitlement and profile."""
    # Call MCP server via stdio or HTTP
    result = await mcp_client.call_tool(
        "check_user_entitlement",
        {"username": username}
    )
    return json.loads(result.content)

# Add to agent
agent = create_react_agent(
    model,
    tools=[check_entitlement],
)
```

---

## Development

### Adding a New MCP Server

1. Create a new Python file in this directory (e.g., `my_mcp.py`)
2. Import required dependencies:
   ```python
   from mcp.server import Server
   from mcp.server.stdio import stdio_server
   from mcp.types import Tool, TextContent
   ```
3. Define your server:
   ```python
   app = Server("my-server-name")
   ```
4. Add tools using decorators:
   ```python
   @app.list_tools()
   async def list_tools() -> list[Tool]:
       return [...]
   
   @app.call_tool()
   async def call_tool(name: str, arguments: Any) -> list[TextContent]:
       # Your tool logic
       pass
   ```
5. Add main entry point:
   ```python
   async def main():
       async with stdio_server() as (read_stream, write_stream):
           await app.run(read_stream, write_stream, app.create_initialization_options())
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

### Testing MCP Servers

```bash
# Run the server
python entitlement_mcp.py

# In another terminal, test with MCP inspector (if available)
mcp inspect entitlement_mcp.py
```

---

## Configuration

### Profile API URL

Update in `entitlement_mcp.py`:
```python
PROFILE_API_URL = "https://localhost:8080/services/security/profile"
```

### SSL Certificate Verification

For production, enable SSL verification:
```python
async with httpx.AsyncClient(verify=True) as client:  # Change to True
    # ...
```

---

## Logging

All MCP servers use Python's built-in logging with emoji prefixes:

- 🚀 = Server startup
- 🔍 = Operation start
- 📤 = Outgoing request
- ✅ = Success
- ❌ = Error

View logs in the terminal where the MCP server is running.

---

## Future MCP Servers

Planned additions:
- **Document Search MCP** - Search through documentation and knowledge bases
- **Database Query MCP** - Safe database querying capabilities
- **File Operations MCP** - File system operations for agents
- **API Integration MCP** - Call various internal APIs

---

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

**Last Updated:** November 9, 2025

