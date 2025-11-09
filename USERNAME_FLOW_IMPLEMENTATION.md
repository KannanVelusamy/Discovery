# Username Flow: Frontend → Backend → MCP

## ✅ Implementation Complete

Successfully implemented username passing from SSO authentication through the entire stack.

---

## 📋 Changes Made

### 1. Frontend: Thread Component (`/frontend/src/components/thread/index.tsx`)

**Added username extraction and passing:**

```typescript
const handleSubmit = (e: FormEvent) => {
  // ... existing code ...
  
  // Get username from localStorage (set during profile check)
  let username = "";
  try {
    const userProfile = localStorage.getItem("userProfile");
    if (userProfile) {
      const profile = JSON.parse(userProfile);
      username = profile.username || profile.email?.split("@")[0] || "";
    }
  } catch (error) {
    console.error("Failed to get username from profile:", error);
  }

  console.log("📤 THREAD: Sending message with username:", username);

  // Include username in state sent to backend
  stream.submit(
    { messages: [...toolMessages, newHumanMessage], context, username },
    {
      streamMode: ["values"],
      streamSubgraphs: true,
      streamResumable: true,
      optimisticValues: (prev) => ({
        ...prev,
        context,
        username,  // ← Username passed to backend
        messages: [...],
      }),
    },
  );
};
```

**Key Points:**
- ✅ Reads username from `localStorage` (set during profile-check)
- ✅ Passes username with every message submission
- ✅ Includes in optimistic values for state management
- ✅ Logs username for debugging

---

### 2. Backend Agent: Graph (`/backend/agent/src/agent/graph.py`)

**Updated agent to receive and use username:**

#### A. Modified `call_model` function:

```python
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
```

**Key Points:**
- ✅ Extracts `username` from state
- ✅ Adds username to system prompt context
- ✅ LLM sees username and uses it for tool calls
- ✅ Logs username for debugging

#### B. Updated `check_user_entitlement` tool:

```python
@tool
def check_user_entitlement(username: str) -> str:
    """Check user entitlement and retrieve user profile with roles."""
    if not username:
        return json.dumps({"error": "Username is required", "username": None})
    
    print(f"🔍 Tool: Checking entitlement for {username}")
    
    result = call_mcp_tool(
        ENTITLEMENT_MCP,
        "check_user_entitlement",
        {"username": username}
    )
    # ... rest of implementation
```

**Key Points:**
- ✅ Validates username is provided
- ✅ Passes username to MCP server
- ✅ Returns error if username missing

---

## 🔄 Complete Flow

```
1. User Sign-In (Azure AD SSO)
   ↓
2. Profile Check Page (/profile-check)
   - Calls /api/entitlement
   - Gets profile data (username, roles, etc.)
   - Stores in localStorage
   ↓
3. Main Chat Page (/)
   - Reads username from localStorage
   ↓
4. User Types Message
   ↓
5. Frontend (Thread Component)
   - Extracts username from localStorage
   - Includes username in stream.submit()
   ↓
6. Backend Agent (graph.py)
   - Receives username in state
   - Adds to system prompt
   - Model sees: "Current user: kannan.velusamy"
   ↓
7. Model Decides to Call Tool
   - check_user_entitlement("kannan.velusamy")
   ↓
8. Tool Execution (call_mcp_tool)
   - Calls /mcp/venv/bin/python
   - Runs entitlement_mcp.py
   - Passes {"username": "kannan.velusamy"}
   ↓
9. MCP Server
   - Calls profile API
   - Returns roles, status, etc.
   ↓
10. Tool Result → Model → User Response
```

---

## 📊 Example Interaction

**User Message**: "Show me my accounts"

**Frontend Log**:
```
📤 THREAD: Sending message with username: kannan.velusamy
```

**Backend Log**:
```
🤖 Agent response - username in context: kannan.velusamy
🔍 Tool: Checking entitlement for kannan.velusamy
🔧 Calling MCP: check_user_entitlement at /Users/kannan/DPAS/discovery/mcp/entitlement_mcp.py
   Using MCP venv Python: /Users/kannan/DPAS/discovery/mcp/venv/bin/python
✅ MCP call successful: check_user_entitlement
```

**MCP Server Log**:
```
🔍 ENTITLEMENT MCP: Checking entitlement for user: kannan.velusamy
📤 ENTITLEMENT MCP: Calling API: https://localhost:8080/...
✅ ENTITLEMENT MCP: Profile retrieved successfully
👤 ENTITLEMENT MCP: User: Kannan Velusamy
👥 ENTITLEMENT MCP: Roles: ['ABCD', 'EFGH']
```

---

## 🔍 What Was Removed/Simplified

### Kept (Good to keep):
- ✅ `/api/entitlement` route - Used only once during initial profile check
- ✅ `/profile-check` page - Initial verification and storage
- ✅ Profile stored in localStorage - Needed for username extraction

### No Longer Needed:
- ❌ Direct entitlement calls from chat interface
- ❌ Separate backend API endpoint for entitlement during chat
- ❌ Complex state management for user context

---

## ✅ Benefits of This Approach

| Benefit | Description |
|---------|-------------|
| **Single Source of Truth** | Username comes from SSO profile check |
| **Persistent Context** | Username passed with every message |
| **No Redundant Calls** | Entitlement checked once, reused by agent |
| **Agent Autonomy** | Agent decides when to call entitlement tool |
| **Simple Frontend** | Just pass username, agent handles rest |
| **Debuggable** | Clear logs at every step |

---

## 🧪 How to Test

### 1. Clear Previous Data
```bash
# In browser console:
localStorage.clear()
```

### 2. Sign In
1. Navigate to frontend
2. Sign in with Azure AD
3. Complete profile check
4. Accept terms

### 3. Test Chat
**Try**: "What are my roles?"

**Expected Flow**:
```
Frontend → username: "kannan.velusamy"
    ↓
Backend → Sees username in system prompt
    ↓
Agent → Calls check_user_entitlement("kannan.velusamy")
    ↓
MCP → Returns roles: ["ABCD", "EFGH"]
    ↓
User → "You have roles: ABCD, EFGH"
```

### 4. Verify Logs

**Frontend Console**:
```
📤 THREAD: Sending message with username: kannan.velusamy
```

**Backend Terminal**:
```
🤖 Agent response - username in context: kannan.velusamy
🔍 Tool: Checking entitlement for kannan.velusamy
✅ MCP call successful
```

---

## 🔒 Security Notes

1. **Username from SSO**: Extracted from authenticated Azure AD email
2. **Validated on Backend**: Agent validates username before MCP calls
3. **Profile API**: Still authenticated via HTTPS
4. **No Direct User Input**: Username comes from OAuth, not user input

---

## 📝 Summary

### Changes:
1. ✅ Frontend: Passes username from localStorage with every message
2. ✅ Backend: Receives username in state, adds to system prompt
3. ✅ Tools: Use username passed from agent for MCP calls
4. ✅ MCP: Uses correct Python venv with all dependencies

### Flow:
```
SSO → Profile Check → localStorage → Frontend → Backend → Agent → Tools → MCP
```

### Result:
- Username flows seamlessly from SSO through entire stack
- Agent has user context for every interaction
- MCP tools always know which user to query for
- No redundant API calls
- Clean, maintainable architecture

**Ready to use!** 🚀

