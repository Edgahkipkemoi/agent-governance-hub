#!/bin/bash

echo "🔍 Agent Audit System - Status Check"
echo "====================================="
echo ""

# Check if backend dependencies are installed
echo "Backend Dependencies:"
if [ -f "backend/venv/bin/python" ]; then
    if backend/venv/bin/python -c "import fastapi" 2>/dev/null; then
        echo "  ✓ FastAPI installed"
    else
        echo "  ✗ FastAPI not installed (pip might still be running)"
    fi
else
    echo "  ✗ Virtual environment not found"
fi

# Check if frontend is running
echo ""
echo "Frontend:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✓ Running on http://localhost:3000"
else
    echo "  ✗ Not running"
fi

# Check if backend is running
echo ""
echo "Backend:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Running on http://localhost:8000"
else
    echo "  ✗ Not running"
fi

# Check environment files
echo ""
echo "Environment Files:"
if [ -f "backend/.env" ]; then
    echo "  ✓ backend/.env exists"
else
    echo "  ✗ backend/.env missing"
fi

if [ -f "frontend/.env.local" ]; then
    echo "  ✓ frontend/.env.local exists"
else
    echo "  ✗ frontend/.env.local missing"
fi

echo ""
