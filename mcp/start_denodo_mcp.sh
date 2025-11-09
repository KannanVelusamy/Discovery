#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Starting Denodo MCP Server"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not installed"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# Create/activate venv
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Install dependencies
python -c "import httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install httpx mcp
fi

echo "✅ Dependencies ready"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  📋 Configuration"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Denodo URL: http://localhost:9090/denodo-restfulws"
echo "  Database: your_database"
echo "  Tables: RCAT0300, RPBT0100, RPBT0200"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🎯 Denodo MCP Server Ready"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Starting server..."
echo ""

python denodo_mcp.py

