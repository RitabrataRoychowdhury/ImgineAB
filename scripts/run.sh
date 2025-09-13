#!/bin/bash

# Document Q&A System - Run Script
# This script sets up the virtual environment and runs the application

echo "🚀 Document Q&A System - Run Script"
echo "===================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        echo "   Check requirements.txt and try again"
        exit 1
    fi
    
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    echo "   Please ensure requirements.txt exists in the project directory"
    exit 1
fi

# Check environment configuration
echo ""
echo "⚙️  Checking configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env with your actual Gemini API key"
        echo "   You can get an API key from: https://makersuite.google.com/app/apikey"
    else
        echo "❌ No .env or .env.example file found"
        echo "   Please create a .env file with your configuration"
        exit 1
    fi
fi

# Check if API key is configured
if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
    echo "⚠️  Warning: Default API key detected in .env"
    echo "   Please update .env with your actual Gemini API key"
    echo "   You can get one from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "❓ Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Please update your .env file and run this script again"
        exit 1
    fi
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data/database
mkdir -p data/documents
mkdir -p logs
echo "✅ Directories created"

# Run system health check
echo ""
echo "🔍 Running system health check..."
python main.py --check

if [ $? -ne 0 ]; then
    echo "❌ System health check failed"
    echo "   Please check your configuration and try again"
    exit 1
fi

# Ask user what they want to do
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