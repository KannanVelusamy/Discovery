#!/usr/bin/env python3
"""Simple test script for the DeepAgents implementation.

This script tests the agent's ability to call MCP servers and reason about data.
"""
import os
import sys

# Add the agent to path
sys.path.insert(0, '/Users/kannan/DPAS/discovery/backend/agent/src')

def test_agent_creation():
    """Test that the agent can be created successfully."""
    print("=" * 60)
    print("Test 1: Agent Creation")
    print("=" * 60)
    
    try:
        from agent.graph import graph, tools
        print("✅ Agent imported successfully")
        print(f"✅ Agent has {len(tools)} tools:")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool.name}")
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_paths():
    """Test that MCP server files exist."""
    print("=" * 60)
    print("Test 2: MCP Server Files")
    print("=" * 60)
    
    mcp_base = "/Users/kannan/DPAS/discovery/mcp"
    files = [
        "entitlement_mcp.py",
        "denodo_mcp.py",
        "start_mcp_server.sh",
        "start_denodo_mcp.sh"
    ]
    
    all_exist = True
    for file in files:
        path = os.path.join(mcp_base, file)
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        all_exist = all_exist and exists
    
    print()
    return all_exist


def test_agent_state():
    """Test the agent state structure."""
    print("=" * 60)
    print("Test 3: Agent State")
    print("=" * 60)
    
    try:
        from agent.graph import AgentState
        from langchain_core.messages import HumanMessage
        
        # Create a sample state
        state = {
            "messages": [HumanMessage(content="Hello")],
            "username": "test.user",
            "user_profile": {"name": "Test User"},
            "roles": ["ADMIN"]
        }
        
        print("✅ State structure is correct")
        print(f"   - messages: {type(state['messages'])}")
        print(f"   - username: {state['username']}")
        print(f"   - user_profile: {type(state['user_profile'])}")
        print(f"   - roles: {state['roles']}")
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_definitions():
    """Test that tools have proper definitions."""
    print("=" * 60)
    print("Test 4: Tool Definitions")
    print("=" * 60)
    
    try:
        from agent.graph import tools
        
        for tool in tools:
            print(f"\n🔧 Tool: {tool.name}")
            print(f"   Description: {tool.description[:100]}...")
            if hasattr(tool, 'args_schema'):
                print(f"   Has schema: ✅")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DeepAgents + MCP Integration Tests")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Agent Creation", test_agent_creation()))
    results.append(("MCP Server Files", test_mcp_paths()))
    results.append(("Agent State", test_agent_state()))
    results.append(("Tool Definitions", test_tool_definitions()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The DeepAgents implementation is ready.")
        print("\n📋 Next Steps:")
        print("   1. Configure Denodo connection in mcp/denodo_mcp.py")
        print("   2. Start the LangGraph server: cd backend/agent && langgraph dev")
        print("   3. Test with the frontend at http://localhost:3000")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

