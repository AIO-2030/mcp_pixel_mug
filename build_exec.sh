#!/bin/bash
# PixelMug MCP Executable Build Script
# Wrapper script that calls build_simple_exe.py for reliable building

set -e

echo "🚀 PixelMug MCP Executable Builder"
echo "=================================="
echo "📋 Using Python build script for maximum reliability..."
echo ""

# Check if build_simple_exe.py exists
if [ ! -f "build_simple_exe.py" ]; then
    echo "❌ Error: build_simple_exe.py not found in current directory"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    echo "   Please ensure Python 3 is installed and available"
    exit 1
fi

# Use python3 if available, otherwise fall back to python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Parse arguments
MODE=${1:-all}

if [ "$MODE" == "stdio" ]; then
    echo "🔧 Building Standard I/O Mode only..."
    echo "⚠️  Note: build_simple_exe.py builds both modes by default"
    echo "   For single mode builds, use Python script directly:"
    echo "   python3 -c \"from build_simple_exe import *; build_simple_executable('stdio_server.py', 'pixelmug_stdio')\""
    echo ""
elif [ "$MODE" == "mcp" ]; then
    echo "🔧 Building Interactive Mode only..."
    echo "⚠️  Note: build_simple_exe.py builds both modes by default"
    echo "   For single mode builds, use Python script directly:"
    echo "   python3 -c \"from build_simple_exe import *; build_simple_executable('mcp_server.py', 'pixelmug_interactive')\""
    echo ""
else
    echo "🔧 Building both Standard I/O and Interactive modes..."
fi

# Call the Python build script
echo "▶️  Executing: $PYTHON_CMD build_simple_exe.py"
echo ""

if $PYTHON_CMD build_simple_exe.py; then
    echo ""
    echo "🎉 Build completed successfully!"
    echo ""
    echo "📦 Generated executables:"
    if [ -f "dist/pixelmug_stdio" ]; then
        echo "   ✅ dist/pixelmug_stdio (Standard I/O mode)"
        SIZE=$(du -h dist/pixelmug_stdio 2>/dev/null | cut -f1 || echo "Unknown")
        echo "      Size: $SIZE"
    fi
    if [ -f "dist/pixelmug_interactive" ]; then
        echo "   ✅ dist/pixelmug_interactive (Interactive mode)"
        SIZE=$(du -h dist/pixelmug_interactive 2>/dev/null | cut -f1 || echo "Unknown")
        echo "      Size: $SIZE"
    fi
    
    echo ""
    echo "🚀 Usage Examples:"
    echo "   # Test Standard I/O mode:"
    echo "   echo '{\"jsonrpc\":\"2.0\",\"method\":\"help\",\"id\":1}' | ./dist/pixelmug_stdio"
    echo ""
    echo "   # Run Interactive mode:"
    echo "   ./dist/pixelmug_interactive"
    echo ""
    echo "   # Test pixel art feature:"
    echo "   echo '{\"jsonrpc\":\"2.0\",\"method\":\"publish_action\",\"params\":{\"device_id\":\"mug_001\",\"action\":\"pixel_art\",\"params\":{\"pattern\":[[\"#FF0000\",\"#00FF00\"],[\"#0000FF\",\"#FFFFFF\"]],\"width\":2,\"height\":2,\"duration\":10}},\"id\":1}' | ./dist/pixelmug_stdio"
    
else
    echo ""
    echo "❌ Build failed!"
    echo "   Check the output above for error details"
    echo "   You can also try running the Python script directly:"
    echo "   $PYTHON_CMD build_simple_exe.py"
    exit 1
fi

echo ""
echo "🔧 Additional Options:"
echo "   ./build_exec.sh          # Build both executables (default)"
echo "   ./build_exec.sh stdio    # Build Standard I/O server only"
echo "   ./build_exec.sh mcp      # Build Interactive server only"
echo "   python3 build_simple_exe.py  # Direct Python build script"
echo ""
echo "📚 For more information, see README.md"
