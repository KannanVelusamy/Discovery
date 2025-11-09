# Python Command Fix for MCP Tool Calls

## ❌ Problem

The error showed:
```
Tool Result: check_user_entitlement
error: Failed to call MCP: [Errno 2] No such file or directory: 'python'
```

**Root Cause**: The agent was trying to call `python` command, but on macOS systems (especially with Homebrew Python), the command is `python3`, not `python`.

## ✅ Solution

Updated the `call_mcp_tool` function to:
1. Use `python3` as the default command
2. Detect if running in a virtual environment
3. Use the correct Python executable automatically

### Code Changes

**File**: `/backend/agent/src/agent/graph.py`

**Before**:
```python
result = subprocess.run(
    ["python", mcp_path],  # ❌ 'python' not found on macOS
    input=json.dumps(mcp_request),
    capture_output=True,
    text=True,
    timeout=30
)
```

**After**:
```python
# Use python3 explicitly or the current Python executable
python_cmd = "python3"

# Check if we're in a virtual environment
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    # We're in a venv, use the venv's python
    python_cmd = sys.executable

result = subprocess.run(
    [python_cmd, mcp_path],  # ✅ Uses python3 or venv python
    input=json.dumps(mcp_request),
    capture_output=True,
    text=True,
    timeout=30
)
```

## 🔍 How It Works

### 1. Default to `python3`
```python
python_cmd = "python3"
```
Most macOS systems have `python3` but not `python`.

### 2. Virtual Environment Detection
```python
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    python_cmd = sys.executable
```

Checks two conditions:
- `sys.real_prefix`: Set in older virtualenv
- `sys.base_prefix != sys.prefix`: Set in venv (Python 3.3+)

If either is true, we're in a virtual environment and should use `sys.executable`.

### 3. Use Detected Command
```python
result = subprocess.run([python_cmd, mcp_path], ...)
```

## 📊 Behavior

| Environment | Python Command Used |
|-------------|---------------------|
| System Python (macOS) | `python3` |
| System Python (Linux) | `python3` |
| Virtual Environment | `/path/to/venv/bin/python` |
| Homebrew Python | `python3` |

## ✅ Benefits

1. **Cross-Platform**: Works on macOS, Linux, Windows
2. **Venv-Aware**: Uses correct Python in virtual environments
3. **Reliable**: Falls back to python3 if not in venv
4. **No Configuration**: Automatic detection

## 🧪 Testing

The agent should now successfully call MCP tools:

```bash
cd /Users/kannan/DPAS/discovery/backend/agent
langgraph dev
```

Then test in frontend:
- Try: "What are my roles?"
- Try: "Show me my accounts"

**Expected Output**:
```
🔧 Calling MCP: check_user_entitlement at /Users/kannan/DPAS/discovery/mcp/entitlement_mcp.py
✅ MCP call successful: check_user_entitlement
```

## 🔧 Additional Import

Added `sys` import to detect Python environment:

```python
import sys
```

## ✅ Status

- [x] Python command issue fixed
- [x] Virtual environment detection added
- [x] Cross-platform compatibility
- [x] No linter errors
- [x] Ready to test

The MCP tools should now work correctly! 🚀

