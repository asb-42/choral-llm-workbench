#!/bin/bash

echo "🎵 Choral LLM Workbench - Dependency Installation"
echo "===================================="

echo -n "🔍 Checking Environment..."
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"

# Check Python
if command -v python >/dev/null 2>&1; then
    echo -n "✅ Python: $(python --version)"
else
    echo -n "❌ Python not found"
    echo -n "   Install Python: https://www.python.org/downloads/"
fi

# Check pyenv
if command -v pyenv >/dev/null 2>&1; then
    echo -n "✅ pyenv: $(pyenv --version)"
else
    echo -n "❌ pyenv not found"
    echo -n "   Install pyenv: https://github.com/pyenv/pyenv#installation"
fi

# Check npm/yarn
if command -v npm >/dev/null 2>&1; then
    echo -n "✅ npm: $(npm --version)"
elif command -v yarn >/dev/null 2>&1; then
    echo -n "✅ yarn: $(yarn --version)"
else
    echo -n "❌ Neither npm nor yarn found"
    echo -n "   Install Node.js: https://nodejs.org/"
fi

echo ""
echo -n "🔧 Available Installation Commands:"
echo ""
echo -n "1. Install Backend Dependencies:"
echo -n "   cd backend && npm install"
echo -n "   npm install xml2js tone web-audio-api"
echo ""
echo -n "2. Install Frontend Dependencies:"
echo -n "   cd frontend && npm install vue@3 @vitejs/plugin-vue pinia element-plus"
echo ""
echo -n "3. Alternative Package Install:"
echo -n "   npm install xml2js"
echo -n "   npm install music21 # Professional music notation"
echo -n ""
echo -n "4. Ollama Setup (Optional):"
echo "   curl -fsSL https://ollama.ai/install.sh | sh"
echo -n ""
echo -n "   Ollama CLI for better control"
echo ""
echo -n "🚀 Automatic Setup Command:"
echo -n "   npm run setup   # Install all dependencies and create launch scripts"
echo ""

echo ""
echo -n "📚 For manual installation issues:"
echo -n "   Check DEPENDENCY_STATUS.md for detailed workarounds"
echo -n ""
echo -n "📁 Repository Status: git status"
echo -n "   Node.js v18+ and npm 9+ recommended"
echo -n "   Python 3.11+ with pip install works best"