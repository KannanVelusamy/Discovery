# MCP Virtual Environment Fix

## ❌ Problem

The error showed:
```
MCP error: Traceback (most recent call last):
  File "/Users/kannan/DPAS/discovery/mcp/entitlement_mcp.py", line 12, in <module>
    from mcp.server import Server
ModuleNotFoundError: No module named 'mcp'
```

**Root Cause**: The agent was calling MCP scripts with the system `python3`, but the `mcp` package is installed in the MCP virtual environment at `/mcp/venv/`.

## ✅ Solution

Updated the `call_mcp_tool` function to use the **MCP virtual environment's Python** instead of system Python.

### Code Changes

**File**: `/backend/agent/src/agent/graph.py`

**Before**:
```python
# Use system python3
python_cmd = "python3"

result = subprocess.run(
    [python_cmd, mcp_path],  # ❌ System python doesn't have 'mcp' package
    ...
)
```

**After**:
```python
# Determine the Python executable to use
# MCP servers have their own venv in the mcp directory
mcp_dir = os.path.dirname(mcp_path)
mcp_venv_python = os.path.join(mcp_dir, "venv", "bin", "python")

# Use MCP venv python if it exists, otherwise fall back to system python3
if os.path.exists(mcp_venv_python):
    python_cmd = mcp_venv_python
    print(f"   Using MCP venv Python: {python_cmd}")
else:
    python_cmd = "python3"
    print(f"   ⚠️  MCP venv not found, using system python3")

result = subprocess.run(
    [python_cmd, mcp_path],  # ✅ Uses venv python with 'mcp' package
    ...
)
```

## 🔍 How It Works

### 1. Detect MCP Directory
```python
mcp_dir = os.path.dirname(mcp_path)
# Example: /Users/kannan/DPAS/discovery/mcp
```

### 2. Build venv Python Path
```python
mcp_venv_python = os.path.join(mcp_dir, "venv", "bin", "python")
# Result: /Users/kannan/DPAS/discovery/mcp/venv/bin/python
```

### 3. Check if venv Exists
```python
if os.path.exists(mcp_venv_python):
    python_cmd = mcp_venv_python  # ✅ Use venv
else:
    python_cmd = "python3"  # ⚠️ Fallback
```

### 4. Log Which Python is Used
```python
print(f"   Using MCP venv Python: {python_cmd}")
```

## 📊 Python Selection Logic

| MCP Script Location | Python Used |
|---------------------|-------------|
| `/mcp/entitlement_mcp.py` | `/mcp/venv/bin/python` ✅ |
| `/mcp/denodo_mcp.py` | `/mcp/venv/bin/python` ✅ |
| No venv exists | `python3` (system) ⚠️ |

## ✅ Verified

Checked that:
1. ✅ MCP venv exists: `/Users/kannan/DPAS/discovery/mcp/venv/bin/python`
2. ✅ MCP package installed in venv
3. ✅ No linter errors

## 🧪 Expected Behavior

When the agent calls MCP tools, you'll see in the logs:

```
🔧 Calling MCP: check_user_entitlement at /Users/kannan/DPAS/discovery/mcp/entitlement_mcp.py
   Using MCP venv Python: /Users/kannan/DPAS/discovery/mcp/venv/bin/python
✅ MCP call successful: check_user_entitlement
```

## 🎯 Benefits

1. **Isolated Dependencies**: MCP packages in separate venv
2. **No Conflicts**: System Python unchanged
3. **Automatic Detection**: Finds venv automatically
4. **Fallback Safe**: Uses system python3 if venv missing
5. **Clear Logging**: Shows which Python is used

## 🚀 Test Again

The agent should now successfully call MCP tools:

1. **Restart backend** (if running):
   ```bash
   cd /Users/kannan/DPAS/discovery/backend/agent
   langgraph dev
   ```

2. **Test in frontend**:
   - "What are my roles?"
   - "Show me my accounts"

**Expected Result**: MCP tools work correctly! ✅

## 📝 Summary

- **Before**: Used system `python3` → `mcp` module not found ❌
- **After**: Uses MCP venv Python → `mcp` module available ✅

The fix ensures MCP scripts always run in their isolated virtual environment with all required dependencies installed.

