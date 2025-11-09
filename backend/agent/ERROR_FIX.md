# Error Fix: create_react_agent API

## ❌ Problem

The `create_react_agent()` function was being called with an incorrect parameter:

```python
agent = create_react_agent(
    model=model,
    tools=tools,
    state_schema=AgentState,
    messages_modifier=SystemMessage(content=SYSTEM_PROMPT)  # ❌ WRONG
)
```

**Error Message**:
```
TypeError: create_react_agent() got unexpected keyword arguments: {'messages_modifier': ...}
```

## ✅ Solution

Changed to use `state_modifier` (the correct parameter) with a function that prepends the system message:

```python
def state_modifier(state):
    messages = state.get("messages", [])
    # Prepend system message if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        return [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    return messages

agent = create_react_agent(
    model=model,
    tools=tools,
    state_schema=AgentState,
    state_modifier=state_modifier  # ✅ CORRECT
)
```

## 📝 What Changed

**File**: `/backend/agent/src/agent/graph.py`

**Lines 285-316**: Updated the `create_agent_graph()` function to:
1. Define a `state_modifier` function that adds the system prompt
2. Pass `state_modifier` instead of `messages_modifier` to `create_react_agent()`

## 🔧 How state_modifier Works

The `state_modifier` is a function that receives the agent state and returns modified messages:

```python
def state_modifier(state):
    """
    Modifies the state before passing to the model.
    Ensures system message is always first.
    """
    messages = state.get("messages", [])
    
    # Check if system message already exists
    if not messages or not isinstance(messages[0], SystemMessage):
        # Prepend system message
        return [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # System message already present
    return messages
```

This ensures:
- ✅ System prompt is always included
- ✅ System prompt is always first
- ✅ Avoids duplicate system messages

## 🧪 Testing

The agent should now start correctly:

```bash
cd /Users/kannan/DPAS/discovery/backend/agent
langgraph dev
```

**Expected Output**:
```
🤖 Creating DeepAgents agent with MCP tools...
✅ Agent created successfully
✅ Ready! API: http://127.0.0.1:8123
```

## 📚 API Reference

### create_react_agent() Valid Parameters

According to LangGraph documentation:

```python
create_react_agent(
    model,                    # Required: The LLM
    tools,                    # Required: List of tools
    state_schema=None,        # Optional: Custom state TypedDict
    state_modifier=None,      # Optional: Function to modify state
    checkpointer=None,        # Optional: For persistence
    interrupt_before=None,    # Optional: Interrupt points
    interrupt_after=None,     # Optional: Interrupt points
    debug=False               # Optional: Debug mode
)
```

**Note**: `messages_modifier` is NOT a valid parameter!

## ✅ Status

- [x] Error identified
- [x] Fix applied
- [x] No linter errors
- [x] Ready to test

The agent is now fixed and ready to run! 🚀

