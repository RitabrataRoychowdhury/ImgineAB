#!/bin/bash

# Document Q&A System - Cleanup Script
# This script cleans up all runtime data, databases, logs, and deactivates the virtual environment

echo "🧹 Document Q&A System - Cleanup Script"
echo "========================================"

# Function to safely remove files/directories
safe_remove() {
    if [ -e "$1" ]; then
        echo "🗑️  Removing: $1"
        rm -rf "$1"
    else
        echo "ℹ️  Not found: $1 (already clean)"
    fi
}

# Stop any running processes
echo ""
echo "🛑 Stopping any running processes..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f "python main.py" 2>/dev/null || true
sleep 2

# Clean up database files
echo ""
echo "🗄️ Cleaning up database files..."
safe_remove "data/database/documents.db"
safe_remove "data/database/documents.db-journal"
safe_remove "data/database/documents.db-wal"
safe_remove "data/database/documents.db-shm"

# Clean up document storage
echo ""
echo "📄 Cleaning up document storage..."
safe_remove "data/documents"

# Clean up entire data directory if empty
if [ -d "data" ]; then
    if [ -z "$(ls -A data 2>/dev/null)" ]; then
        echo "🗑️  Removing empty data directory"
        rmdir data
    else
        echo "ℹ️  Data directory not empty, keeping structure"
    fi
fi

# Clean up log files
echo ""
echo "📋 Cleaning up log files..."
safe_remove "logs"

# Clean up Python cache files
echo ""
echo "🐍 Cleaning up Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Clean up test files
echo ""
echo "🧪 Cleaning up test files..."
safe_remove "test_simple_processor.py"
safe_remove "test_fallback_processor.py"
safe_remove "test_document_storage.py"
safe_remove "test_comprehensive_processing.py"

# Clean up temporary files
echo ""
echo "🗂️ Cleaning up temporary files..."
safe_remove ".pytest_cache"
safe_remove ".coverage"
safe_remove "htmlcov"
safe_remove "*.tmp"
safe_remove "*.temp"

# Clean up Streamlit cache
echo ""
echo "📱 Cleaning up Streamlit cache..."
safe_remove ".streamlit"

# Deactivate virtual environment if active
echo ""
echo "🔌 Checking virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "📤 Deactivating virtual environment: $(basename $VIRTUAL_ENV)"
    deactivate 2>/dev/null || true
    echo "✅ Virtual environment deactivated"
else
    echo "ℹ️  No virtual environment currently active"
fi

# Optional: Remove virtual environment entirely
echo ""
read -p "❓ Do you want to remove the virtual environment entirely? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "venv" ]; then
        echo "🗑️  Removing virtual environment directory..."
        rm -rf venv
        echo "✅ Virtual environment removed"
    else
        echo "ℹ️  Virtual environment directory not found"
    fi
else
    echo "ℹ️  Keeping virtual environment directory"
fi

# Show final status
echo ""
echo "🎉 Cleanup completed!"
echo ""
echo "📊 Cleanup Summary:"
echo "   ✅ Database files removed"
echo "   ✅ Document storage cleared"
echo "   ✅ Log files removed"
echo "   ✅ Python cache cleared"
echo "   ✅ Test files removed"
echo "   ✅ Temporary files cleared"
echo "   ✅ Virtual environment deactivated"
echo ""
echo "🚀 System is now clean and ready for fresh start!"
echo ""
echo "💡 To run the system again:"
echo "   ./run.sh"
echo ""