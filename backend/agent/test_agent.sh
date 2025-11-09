#!/bin/bash

# Test script for DeepAgents implementation
# This script activates the virtual environment and runs the agent test

echo "🧪 Testing DeepAgents Implementation"
echo "===================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Navigate to agent directory
cd agent

# Run the test
echo "🚀 Running agent test..."
echo ""
python src/agent/graph_new.py

echo ""
echo "✅ Test complete!"

