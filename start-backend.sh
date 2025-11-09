#!/bin/bash

echo "🚀 Starting Backend Server (LangGraph + DeepAgents)"
echo "===================================================="
echo ""

cd "$(dirname "$0")/backend/agent"

# Check if venv exists
if [ ! -d "../venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "Please create it first:"
    echo "  cd backend && python3 -m venv venv"
    exit 1
fi

# Activate venv
echo "📦 Activating virtual environment..."
source ../venv/bin/activate

# Check if deepagents is installed
if ! python -c "import deepagents" 2>/dev/null; then
    echo "❌ Error: DeepAgents not installed!"
    echo "Installing now..."
    pip install deepagents
fi

# Check if langgraph-cli is installed
if ! command -v langgraph &> /dev/null; then
    echo "📦 Installing LangGraph CLI..."
    pip install langgraph-cli
fi

echo ""
echo "✅ Starting LangGraph server..."
echo "   Backend API: http://localhost:2024"
echo "   LangGraph Studio: http://localhost:2024/studio"
echo ""
echo "📝 Using:"
echo "   - DeepAgents for agent creation"
echo "   - Mock Denodo MCP (no database required)"
echo "   - Real Entitlement MCP"
echo ""
echo "Press Ctrl+C to stop"
echo ""

langgraph dev

