#!/bin/bash
# PixelMug MCP Executable Build Script
# Builds standalone executables for easy distribution

set -e

echo "🚀 PixelMug MCP Executable Builder"
echo "=================================="

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller==6.3.0
fi

# Create build directories
mkdir -p dist
mkdir -p build

# Determine build mode
MODE=${1:-stdio}

if [ "$MODE" == "mcp" ]; then
    echo "🔧 Building MCP Interactive Mode Executable..."
    SCRIPT="mcp_server.py"
    OUTPUT_NAME="pixelmug_mcp_interactive"
    DESCRIPTION="PixelMug MCP Interactive Server"
else
    echo "🔧 Building Standard I/O Mode Executable..."
    SCRIPT="stdio_server.py"
    OUTPUT_NAME="pixelmug_mcp_stdio"
    DESCRIPTION="PixelMug MCP Standard I/O Server"
fi

echo "📋 Build Configuration:"
echo "   Mode: $MODE"
echo "   Script: $SCRIPT"
echo "   Output: $OUTPUT_NAME"
echo "   Description: $DESCRIPTION"

# Build executable with PyInstaller
echo "⚙️ Building executable..."
pyinstaller \
    --onefile \
    --name="$OUTPUT_NAME" \
    --distpath="dist" \
    --workpath="build" \
    --specpath="build" \
    --add-data="requirements.txt:." \
    --add-data="README.md:." \
    --add-data="LICENSE:." \
    --hidden-import="asyncio" \
    --hidden-import="asyncio_mqtt" \
    --hidden-import="paho.mqtt.client" \
    --hidden-import="ssl" \
    --hidden-import="json" \
    --hidden-import="uuid" \
    --hidden-import="datetime" \
    --hidden-import="logging" \
    --console \
    --clean \
    "$SCRIPT"

# Check if build was successful
if [ -f "dist/$OUTPUT_NAME" ] || [ -f "dist/$OUTPUT_NAME.exe" ]; then
    echo "✅ Build successful!"
    echo "📦 Executable created: dist/$OUTPUT_NAME"
    
    # Make executable (Linux/Mac)
    if [ -f "dist/$OUTPUT_NAME" ]; then
        chmod +x "dist/$OUTPUT_NAME"
    fi
    
    # Show file info
    echo "📊 File Information:"
    ls -lh dist/$OUTPUT_NAME* 2>/dev/null || echo "   File not found in expected location"
    
    echo ""
    echo "🎉 Build Complete!"
    echo "To run the executable:"
    if [ "$MODE" == "mcp" ]; then
        echo "   ./dist/$OUTPUT_NAME"
        echo "   (Interactive mode - follow prompts)"
    else
        echo "   echo '{\"jsonrpc\":\"2.0\",\"method\":\"help\",\"id\":1}' | ./dist/$OUTPUT_NAME"
        echo "   (Standard I/O mode - pipe JSON-RPC commands)"
    fi
    
else
    echo "❌ Build failed!"
    echo "Check the build output above for errors."
    exit 1
fi

echo ""
echo "🔧 Additional Build Options:"
echo "   ./build_exec.sh stdio    # Build Standard I/O server (default)"
echo "   ./build_exec.sh mcp      # Build Interactive MCP server"
echo ""
echo "📚 For more information, see README.md"
