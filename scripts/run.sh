#!/bin/bash

# Document Q&A System - Run Script
# This script sets up the virtual environment, cleans up caches, and runs the application

echo "🚀 Document Q&A System - Run Script"
echo "===================================="

# -------------------------------------------------------------------
# 🧹 Step 0: Cleanup junk files before starting
# -------------------------------------------------------------------
echo ""
echo "🧹 Cleaning up caches, logs, and old environments..."

# remove python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
rm -rf .mypy_cache .coverage coverage.xml htmlcov

# remove virtual environments (if present)
rm -rf venv .venv

# remove logs and database (if they are local only)
rm -rf logs/*.log data/database/*.db

# remove stray pyc/pyo files
find . -name "*.py[co]" -delete

echo "✅ Cleanup done"
echo ""

# -------------------------------------------------------------------
# Step 1: Python check
# -------------------------------------------------------------------
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"

# -------------------------------------------------------------------
# Step 2: Create virtual environment
# -------------------------------------------------------------------
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# -------------------------------------------------------------------
# Step 3: Install dependencies
# -------------------------------------------------------------------
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

echo ""
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# -------------------------------------------------------------------
# Step 4: Environment setup
# -------------------------------------------------------------------
echo ""
echo "⚙️  Checking configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env with your actual Gemini API key"
    else
        echo "❌ No .env or .env.example file found"
        exit 1
    fi
fi

if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
    echo "⚠️  Warning: Default API key detected in .env"
    read -p "❓ Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# -------------------------------------------------------------------
# Step 5: Create necessary directories
# -------------------------------------------------------------------
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data/database
mkdir -p data/documents
mkdir -p logs
echo "✅ Directories created"

# -------------------------------------------------------------------
# Step 6: Health check
# -------------------------------------------------------------------
echo ""
echo "🔍 Running system health check..."
python main.py --check
if [ $? -ne 0 ]; then
    echo "❌ System health check failed"
    exit 1
fi

# -------------------------------------------------------------------
# Step 7: Main menu
# -------------------------------------------------------------------
echo ""
echo "🎯 What would you like to do?"
echo "   1) Start web interface (recommended)"
echo "   2) Run system check only"
echo "   3) Initialize system only"
echo "   4) Run tests"
echo ""
read -p "Choose an option (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        echo ""
        echo "🌐 Starting web interface..."
        echo "   URL: http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        python main.py --web
        ;;
    2)
        echo ""
        echo "🔍 Running system check..."
        python main.py --check
        ;;
    3)
        echo ""
        echo "🔧 Initializing system..."
        python main.py --init
        ;;
    4)
        echo ""
        echo "🧪 Running tests..."
        python -m pytest tests/ -v
        ;;
    *)
        echo ""
        echo "🌐 Starting web interface (default)..."
        echo "   URL: http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        python main.py --web
        ;;
esac

echo ""
echo "🎉 Thanks for using Document Q&A System!"
echo ""
echo "💡 Useful commands:"
echo "   ./run.sh          - Run this script again"
echo "   ./cleanup.sh      - Clean up all data and deactivate venv"
echo "   python main.py    - Run with current environment"
echo ""
