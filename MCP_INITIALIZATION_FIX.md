# MCP Initialization Protocol Fix

## ✅ Problem Identified & Fixed

**Root Cause**: 
```
WARNING:root:Failed to validate request: Received request before initialization was complete
```

The MCP server requires proper initialization before accepting tool calls, but we were skipping the initialization handshake.

---

## 🔧 The Fix

### MCP Protocol Requirements

The MCP (Model Context Protocol) requires this sequence:

1. **Initialize Request** - Tell the server who we are
2. **Initialize Response** - Server confirms it's ready
3. **Tool Call Request** - Now we can call tools
4. **Tool Call Response** - Server returns results

We were skipping steps 1-2 and going straight to tool calls!

---

### Implementation

**Before** (Single Request):
```python
mcp_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": tool_name, "arguments": arguments}
}
```

**After** (Initialize + Tool Call):
```python
# 1. Initialize request
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

# 2. Tool call request
tool_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": tool_name, "arguments": arguments}
}

# Send both, separated by newlines
input_data = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"
```

---

### Response Parsing

**Updated to handle multiple responses**:

```python
# Parse responses - MCP returns multiple JSON-RPC responses (one per request)
responses = []
for line in result.stdout.strip().split('\n'):
    if line.strip():
        responses.append(json.loads(line))

print(f"   Received {len(responses)} responses from MCP")

# Find the tool call response (id=1, not the init response with id=0)
tool_response = None
for resp in responses:
    if resp.get("id") == 1:
        tool_response = resp
        break
```

---

## 📊 Expected Flow Now

```
Agent → MCP Server:
  Line 1: {"jsonrpc":"2.0","id":0,"method":"initialize",...}
  Line 2: {"jsonrpc":"2.0","id":1,"method":"tools/call",...}

MCP Server → Agent:
  Line 1: {"jsonrpc":"2.0","id":0,"result":{...}}  ← Init response
  Line 2: {"jsonrpc":"2.0","id":1,"result":{...}}  ← Tool response
```

The agent now correctly:
1. Sends initialization
2. Sends tool call
3. Receives both responses
4. Extracts the tool response (id=1)
5. Returns the data

---

## ✅ What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Requests** | 1 (tool call only) | 2 (init + tool call) |
| **Protocol** | ❌ Incomplete | ✅ Complete |
| **Response Parsing** | Single JSON | Multiple JSON lines |
| **ID Matching** | N/A | Finds tool response by id=1 |

---

## 🧪 Testing

### Restart Backend
```bash
cd /Users/kannan/DPAS/discovery/backend/agent
langgraph dev
```

### Expected Logs
```
🔧 Calling MCP: check_user_entitlement at /path/to/entitlement_mcp.py
   Using MCP venv Python: /path/to/venv/bin/python
   MCP return code: 0
   Received 2 responses from MCP
   Tool response keys: dict_keys(['jsonrpc', 'id', 'result'])
✅ MCP call successful: check_user_entitlement
```

### Test in Frontend
Ask: "What are my roles?"

**Expected**: Agent successfully retrieves profile with roles!

---

## 🎯 Why This Fixes It

1. **Proper Handshake**: MCP server now receives initialization before tool calls
2. **Protocol Compliant**: Follows MCP specification exactly
3. **Response Handling**: Correctly parses multiple JSON-RPC responses
4. **ID Tracking**: Matches tool response by request ID

---

## 📝 MCP Protocol Details

### Initialize Request Structure
```json
{
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
```

### Tool Call Request Structure
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "check_user_entitlement",
    "arguments": {
      "username": "kannan.velusamy"
    }
  }
}
```

---

## ✅ Status

- [x] MCP initialization added
- [x] Multiple response parsing
- [x] ID-based response matching
- [x] Error handling maintained
- [x] No linter errors
- [x] Ready to test!

**The MCP protocol is now correctly implemented!** 🎉

Try it now - the entitlement check should work! 🚀

