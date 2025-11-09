#!/bin/bash

# Start Entitlement MCP Server
# This script starts the MCP server for entitlement checking

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Starting Entitlement MCP Server"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# Virtual environment setup
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

echo ""
echo "🔄 Activating virtual environment..."

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo "✅ Virtual environment activated"
echo ""

# Check and install dependencies
echo "📦 Checking dependencies..."

python -c "import httpx" 2>/dev/null
HTTPX_INSTALLED=$?

python -c "import mcp" 2>/dev/null
MCP_INSTALLED=$?

if [ $HTTPX_INSTALLED -ne 0 ] || [ $MCP_INSTALLED -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install httpx>=0.27.0 mcp>=1.0.0
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ All dependencies already installed"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  📋 Configuration"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Profile API: https://localhost:8080/services/security/profile"
echo "  SSL Verification: Disabled (Development Mode)"
echo "  Virtual Environment: $(pwd)/$VENV_DIR"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🎯 MCP Server Ready"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Starting entitlement MCP server..."
echo "Press Ctrl+C to stop"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Run the MCP server
python entitlement_mcp.py

