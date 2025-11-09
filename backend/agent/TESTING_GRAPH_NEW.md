# Testing graph_new.py - Step-by-Step Guide

## ✅ What Was Changed

**File Updated**: `/Users/kannan/DPAS/discovery/backend/agent/src/agent/__init__.py`

**Change**:
```python
# Before:
from agent.graph import graph

# After:
from agent.graph_new import graph
```

The backend will now use the **simplified agent** (`graph_new.py`) instead of the manual StateGraph implementation.

---

## 🧪 Testing Options

### Option 1: Test Standalone (Quick Verification)

**Purpose**: Verify the agent works independently before testing with frontend.

```bash
cd /Users/kannan/DPAS/discovery/backend/agent
python src/agent/graph_new.py
```

**Expected Output**:
```
🤖 Creating agent with create_agent...
✅ Agent created successfully

============================================================
Testing simplified agent with create_agent
============================================================

🔍 Checking entitlement for: kannan.velusamy
🔧 Calling MCP: check_user_entitlement
   Using MCP venv Python: /Users/kannan/DPAS/discovery/mcp/venv/bin/python
   Sending initialization request...
   Sending tool call request...
   ...
✅ MCP call successful: check_user_entitlement

Agent Response:
[Response with user profile and roles]
```

**What to Check**:
- ✅ Agent creates successfully
- ✅ MCP tools are called
- ✅ Username is extracted from state
- ✅ Response includes user profile

---

### Option 2: Test with Backend Server (Full Integration)

**Purpose**: Test the agent with the LangGraph server and frontend.

#### Step 1: Stop Current Backend (if running)

In the terminal where `langgraph dev` is running:
- Press `Ctrl+C` to stop

#### Step 2: Start Backend with New Agent

```bash
cd /Users/kannan/DPAS/discovery/backend/agent
langgraph dev
```

**Expected Output**:
```
Ready!
- API: http://127.0.0.1:2024
```

**What to Check**:
- ✅ Server starts without errors
- ✅ No import errors
- ✅ API is accessible

#### Step 3: Test Frontend

1. **Open Frontend** (if not already running):
   ```bash
   cd /Users/kannan/DPAS/discovery/frontend
   pnpm dev
   ```

2. **Navigate to**: http://localhost:3000

3. **Login with Azure AD**

4. **Accept Terms & Conditions**

5. **Test Chat**:
   - Ask: "What are my roles?"
   - Ask: "Show me my account balance"
   - Ask: "Can you check my entitlement?"

**What to Check**:
- ✅ Username is passed from frontend to backend
- ✅ Agent receives username in state
- ✅ MCP tools are called with username
- ✅ Responses are accurate
- ✅ No errors in browser console
- ✅ No errors in backend terminal

---

## 🔍 Verification Checklist

### Backend Logs

**Look for these in backend terminal**:

```
✅ Good Signs:
🤖 Creating agent with create_agent...
✅ Agent created successfully
🔍 Checking entitlement for: [username]
🔧 Calling MCP: check_user_entitlement
✅ MCP call successful: check_user_entitlement

❌ Bad Signs:
ImportError: cannot import name 'create_agent'
ModuleNotFoundError: No module named 'langchain.agents'
AttributeError: module 'langchain.agents' has no attribute 'create_agent'
```

### Frontend Console

**Look for these in browser console (F12)**:

```
✅ Good Signs:
📤 THREAD: Sending message with username: kannan.velusamy
✅ Message sent successfully

❌ Bad Signs:
Failed to send message
Network error
500 Internal Server Error
```

### Agent Behavior

**Test these scenarios**:

1. **Username Context**:
   - Ask: "Who am I?"
   - Expected: Agent should know your username

2. **Entitlement Check**:
   - Ask: "What are my roles?"
   - Expected: Agent calls `check_user_entitlement` with your username

3. **Account Query**:
   - Ask: "Show my accounts"
   - Expected: Agent first checks entitlement, then queries accounts

4. **Error Handling**:
   - Ask about non-existent account
   - Expected: Graceful error message

---

## 🐛 Troubleshooting

### Issue 1: ImportError for create_agent

**Error**:
```
ImportError: cannot import name 'create_agent' from 'langchain.agents'
```

**Solution**:
```bash
cd /Users/kannan/DPAS/discovery/backend/agent
pip install --upgrade langchain langchain-core langchain-openai
```

**Required versions**:
- `langchain >= 0.3.0`
- `langchain-core >= 0.3.0`
- `langchain-openai >= 0.2.0`

---

### Issue 2: Username Not Extracted

**Symptom**: Agent doesn't know the username

**Check**:
1. Frontend is sending username:
   ```typescript
   // In thread/index.tsx
   stream.submit(
     { messages: [...], username: username },
     ...
   );
   ```

2. Backend is receiving it:
   ```python
   # In graph_new.py
   username = request.state.get("username", "Unknown")
   ```

**Solution**: Verify localStorage has username:
```javascript
// In browser console
JSON.parse(localStorage.getItem("userProfile"))
```

---

### Issue 3: MCP Tools Not Working

**Symptom**: "No tool response from MCP server"

**Check**:
1. MCP venv exists:
   ```bash
   ls -la /Users/kannan/DPAS/discovery/mcp/venv/
   ```

2. MCP dependencies installed:
   ```bash
   /Users/kannan/DPAS/discovery/mcp/venv/bin/python -c "import mcp; print('OK')"
   ```

**Solution**: Reinstall MCP venv:
```bash
cd /Users/kannan/DPAS/discovery/mcp
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install mcp httpx python-dotenv
deactivate
```

---

### Issue 4: Agent Not Responding

**Symptom**: Agent hangs or doesn't respond

**Check Backend Logs**:
- Look for errors or exceptions
- Check if MCP calls are timing out

**Solution**:
1. Test MCP standalone:
   ```bash
   cd /Users/kannan/DPAS/discovery/mcp
   ./venv/bin/python entitlement_mcp.py
   ```

2. Check network connectivity to profile API

3. Increase timeout in `graph_new.py` if needed

---

## 📊 Comparison Test

**Test both implementations side-by-side**:

### Test graph.py (Old)
```bash
# In __init__.py, change to:
from agent.graph import graph

# Restart backend and test
```

### Test graph_new.py (New)
```bash
# In __init__.py, change to:
from agent.graph_new import graph

# Restart backend and test
```

**Compare**:
- Response quality
- Response time
- Error handling
- Code simplicity

---

## ✅ Success Criteria

The test is successful if:

1. ✅ Backend starts without errors
2. ✅ Agent is created successfully
3. ✅ Username is extracted from state
4. ✅ MCP tools are called correctly
5. ✅ Entitlement check works
6. ✅ Account queries work
7. ✅ Responses are accurate
8. ✅ No errors in console/logs
9. ✅ Frontend integration works
10. ✅ User experience is smooth

---

## 🔄 Rollback Plan

If issues arise, rollback to graph.py:

```bash
# Edit __init__.py
cd /Users/kannan/DPAS/discovery/backend/agent/src/agent

# Change back to:
# from agent.graph import graph

# Restart backend
cd ../..
langgraph dev
```

---

## 📝 Test Results Template

```markdown
## Test Results - graph_new.py

**Date**: 2024-11-09
**Tester**: [Your Name]

### Standalone Test
- [ ] Agent creates successfully
- [ ] MCP tools work
- [ ] Username extracted
- [ ] Response accurate

### Backend Integration
- [ ] Server starts
- [ ] No import errors
- [ ] API accessible

### Frontend Integration
- [ ] Username passed correctly
- [ ] Entitlement check works
- [ ] Account queries work
- [ ] No console errors

### Performance
- Response time: ___ seconds
- Memory usage: ___
- CPU usage: ___

### Issues Found
1. [List any issues]

### Recommendation
- [ ] Approve migration to graph_new.py
- [ ] Need fixes before migration
- [ ] Rollback to graph.py

### Notes
[Additional observations]
```

---

## 🎯 Next Steps After Testing

### If Successful ✅
1. Archive old implementation:
   ```bash
   mv src/agent/graph.py src/agent/graph_old.py
   ```

2. Update documentation:
   - Update README with new architecture
   - Document middleware pattern

3. Deploy to production

### If Issues Found ❌
1. Document issues in GitHub/Jira
2. Fix issues in graph_new.py
3. Retest
4. Or rollback to graph.py

---

**Happy Testing! 🚀**

**Need Help?**
- Check `GRAPH_NEW_COMPARISON.md` for details
- Review `.cursor/deepagents_reference.md` for API reference
- Ask in team chat

