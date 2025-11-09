# MCP Communication Debug Enhancement

## ✅ Changes Made

Added comprehensive error handling and logging to the `call_mcp_tool` function to diagnose MCP server communication issues.

---

## 🔍 Problem

Error reported:
```
Tool Result: check_user_entitlement
error: No result from MCP server
username: kannan.velusamy
```

This suggests the MCP server is responding but the response format doesn't match expectations.

---

## 🛠️ Solution

Enhanced `call_mcp_tool` with detailed logging at every step:

### 1. **Process Execution Logging**
```python
print(f"   MCP return code: {result.returncode}")
print(f"   MCP stdout length: {len(result.stdout)}")
print(f"   MCP stderr: {result.stderr[:200] if result.stderr else 'None'}")
```

**Shows:**
- Whether MCP process executed successfully
- How much data was returned
- Any error output

---

### 2. **Empty Response Detection**
```python
if not result.stdout.strip():
    print(f"❌ MCP returned empty stdout")
    return {"error": "MCP server returned empty response"}
```

**Catches:** MCP runs but returns nothing

---

### 3. **JSON Parsing Errors**
```python
try:
    response = json.loads(result.stdout)
    print(f"   MCP response keys: {response.keys()}")
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse MCP stdout as JSON: {e}")
    print(f"   Stdout content: {result.stdout[:500]}")
    return {"error": f"Invalid JSON from MCP: {str(e)}"}
```

**Shows:**
- Response structure (keys)
- First 500 chars if JSON parsing fails
- Exact error message

---

### 4. **Response Structure Validation**
```python
if "result" in response:
    if "content" in response["result"] and len(response["result"]["content"]) > 0:
        data = json.loads(response["result"]["content"][0]["text"])
        return data
    else:
        print(f"❌ MCP result missing content: {response['result']}")
        return {"error": "MCP result missing content"}
else:
    print(f"❌ No result field in MCP response: {list(response.keys())}")
    # Fallback: try direct data field
    if "data" in response:
        return response
```

**Checks:**
- Does response have "result" field?
- Does result have "content" array?
- Is content array populated?
- **Fallback**: If no "result", try direct "data" field

---

### 5. **Timeout Handling**
```python
except subprocess.TimeoutExpired:
    print(f"❌ MCP call timed out after 30 seconds")
    return {"error": "MCP server timeout"}
```

**Catches:** MCP server hangs

---

### 6. **Full Exception Trace**
```python
except Exception as e:
    print(f"❌ Exception calling MCP: {str(e)}")
    import traceback
    print(traceback.format_exc())
    return {"error": f"Failed to call MCP: {str(e)}"}
```

**Shows:** Complete stack trace for debugging

---

## 📊 What You'll See Now

### When MCP Works:
```
🔧 Calling MCP: check_user_entitlement at /path/to/entitlement_mcp.py
   Using MCP venv Python: /path/to/venv/bin/python
   MCP return code: 0
   MCP stdout length: 1234
   MCP stderr: None
   MCP response keys: dict_keys(['jsonrpc', 'id', 'result'])
✅ MCP call successful: check_user_entitlement
```

### When MCP Has Issues:
```
🔧 Calling MCP: check_user_entitlement at /path/to/entitlement_mcp.py
   Using MCP venv Python: /path/to/venv/bin/python
   MCP return code: 0
   MCP stdout length: 856
   MCP stderr: None
   MCP response keys: dict_keys(['jsonrpc', 'id', 'error'])
❌ No result field in MCP response: ['jsonrpc', 'id', 'error']
```

This will tell us exactly what the MCP server is returning!

---

## 🧪 Next Steps to Debug

### 1. Check Backend Logs
Restart the backend and watch for detailed MCP logs:
```bash
cd /Users/kannan/DPAS/discovery/backend/agent
langgraph dev
```

### 2. Test the MCP Server Directly
Test if MCP server works standalone:
```bash
cd /Users/kannan/DPAS/discovery/mcp
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"check_user_entitlement","arguments":{"username":"kannan.velusamy"}}}' | ./venv/bin/python entitlement_mcp.py
```

### 3. Check Profile API Connectivity
Verify the profile API is accessible:
```bash
curl -k -X POST https://127.0.0.1:8080/services/security/profile \
  -d "uuname=kannan.velusamy" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

---

## 🎯 Expected Diagnostic Output

The enhanced logging will reveal one of these issues:

| Issue | Log Pattern | Solution |
|-------|-------------|----------|
| Empty response | `MCP stdout length: 0` | MCP server not outputting |
| Invalid JSON | `Failed to parse MCP stdout as JSON` | MCP returning non-JSON |
| Wrong structure | `No result field in MCP response` | Response format mismatch |
| Process error | `MCP return code: 1` | MCP server crash |
| Timeout | `MCP call timed out` | API/network issue |

---

## 🔧 Possible Root Causes

### 1. MCP Server Not Running in Stdio Mode
The MCP server uses `stdio_server()` which requires async communication, but we're calling it synchronously via subprocess.

**Fix**: The server might need a wrapper or direct HTTP endpoint.

### 2. Profile API Connection Issues
The MCP tries to connect to `https://localhost:8080` which might:
- Not be running
- Using IPv6 instead of IPv4
- Certificate issues

**Fix**: Ensure API is at `127.0.0.1:8080`

### 3. Response Format Changed
MCP might be returning a different structure than expected.

**Fix**: Logs will show exact structure

---

## ✅ Status

- [x] Enhanced logging added
- [x] Multiple error conditions handled
- [x] Fallback parsing added
- [x] Full traceback on exceptions
- [x] No linter errors

**Next**: Run the agent and check logs to see exact error!

---

## 📝 How to Use

1. **Restart backend**:
   ```bash
   cd /Users/kannan/DPAS/discovery/backend/agent
   langgraph dev
   ```

2. **Test in frontend**: Ask "What are my roles?"

3. **Check backend terminal** for detailed logs showing exactly what the MCP server returned

4. **Share logs** if issue persists - we'll see the exact problem now!

The enhanced logging will reveal exactly what's happening! 🔍

