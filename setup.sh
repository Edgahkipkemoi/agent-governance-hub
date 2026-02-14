#!/bin/bash

# Agent Audit System - Setup Script
# This script helps you set up the project step by step

set -e

echo "🚀 Agent Audit System - Setup Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Checking system requirements...${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    echo "  Install with: sudo apt install python3"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
    echo "  Install from: https://nodejs.org/"
    exit 1
fi

# Check pip
if python3 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip found"
else
    echo -e "${YELLOW}⚠${NC} pip not found - installing..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv
fi

echo ""
echo -e "${BLUE}Step 2: Setting up backend...${NC}"
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} Backend .env file not found"
    echo "  Copying from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC} Please edit backend/.env and add your API keys"
else
    echo -e "${GREEN}✓${NC} Backend .env file exists"
fi

cd ..

echo ""
echo -e "${BLUE}Step 3: Setting up frontend...${NC}"
echo ""

cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓${NC} Node.js dependencies installed"
else
    echo -e "${GREEN}✓${NC} Node.js dependencies already installed"
fi

# Check .env.local file
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠${NC} Frontend .env.local file not found"
    echo "  Copying from .env.example..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠${NC} Please edit frontend/.env.local and add your Supabase keys"
else
    echo -e "${GREEN}✓${NC} Frontend .env.local file exists"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. ${YELLOW}Get your Supabase API keys:${NC}"
echo "   - Go to: https://supabase.com/dashboard"
echo "   - Select your project"
echo "   - Go to Settings → API"
echo "   - Copy the 'anon public' key (for frontend)"
echo "   - Copy the 'service_role' key (for backend)"
echo ""
echo "2. ${YELLOW}Update environment files:${NC}"
echo "   - Edit backend/.env and add:"
echo "     SUPABASE_SERVICE_ROLE_KEY=<your_service_role_key>"
echo "   - Edit frontend/.env.local and add:"
echo "     NEXT_PUBLIC_SUPABASE_ANON_KEY=<your_anon_key>"
echo ""
echo "3. ${YELLOW}Run database migration:${NC}"
echo "   - Go to Supabase Dashboard → SQL Editor"
echo "   - Copy contents of: backend/migrations/001_create_logs_table.sql"
echo "   - Paste and run the SQL"
echo ""
echo "4. ${YELLOW}Enable real-time replication:${NC}"
echo "   - Go to Database → Replication"
echo "   - Enable replication for 'logs' table"
echo ""
echo "5. ${YELLOW}Start the servers:${NC}"
echo ""
echo "   Terminal 1 (Backend):"
echo "   ${GREEN}cd backend${NC}"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}uvicorn main:app --reload --port 8000${NC}"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   ${GREEN}cd frontend${NC}"
echo "   ${GREEN}npm run dev${NC}"
echo ""
echo "6. ${YELLOW}Open your browser:${NC}"
echo "   http://localhost:3000"
echo ""
echo -e "${BLUE}For detailed instructions, see:${NC}"
echo "  - QUICKSTART.md"
echo "  - SETUP_CHECKLIST.md"
echo "  - TROUBLESHOOTING.md"
echo ""
