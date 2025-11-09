#!/bin/bash

echo "🎨 Starting Frontend Server (Next.js)"
echo "======================================"
echo ""

cd "$(dirname "$0")/frontend"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found!"
    echo "Copying from .env.example..."
    cp env.local.example .env.local
    echo "⚠️  Please edit .env.local with your credentials"
    echo ""
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    pnpm install
    echo ""
fi

echo "✅ Starting Next.js server..."
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

pnpm dev

