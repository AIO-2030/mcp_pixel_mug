#!/bin/bash
# Test pixel_art method

echo "🧪 Testing pixel_art method"
echo "============================"

# Test case 1: Simple 2x2 pattern
echo "Test case 1: Simple 2x2 pattern"
REQUEST1='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "pixel_art", "params": {"pattern": [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]], "width": 2, "height": 2, "duration": 10}}, "id": 1}'

echo "Sending request:"
echo "$REQUEST1"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST1'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "----------------------------------------"

# Test case 2: Smiley face example
echo "Test case 2: 8x8 Smiley face pattern"
REQUEST2='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "pixel_art", "params": {"pattern": [["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"], ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]], "width": 8, "height": 8, "duration": 20}}, "id": 2}'

echo "Sending request:"
echo "8x8 Smiley face pattern..."
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST2'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "----------------------------------------"

# Test case 3: Base64 encoded image (mock)
echo "Test case 3: Base64 encoded image"
REQUEST3='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "pixel_art", "params": {"pattern": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==", "width": 2, "height": 2, "duration": 15}}, "id": 3}'

echo "Sending request:"
echo "$REQUEST3"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST3'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "----------------------------------------"

# Test case 4: Invalid pattern (wrong dimensions)
echo "Test case 4: Invalid pattern - wrong dimensions"
REQUEST4='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "pixel_art", "params": {"pattern": [["#FF0000", "#00FF00"]], "width": 2, "height": 2, "duration": 10}}, "id": 4}'

echo "Sending request:"
echo "$REQUEST4"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST4'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "----------------------------------------"

# Test case 5: Invalid color format
echo "Test case 5: Invalid color format"
REQUEST5='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "pixel_art", "params": {"pattern": [["RED", "GREEN"], ["BLUE", "WHITE"]], "width": 2, "height": 2, "duration": 10}}, "id": 5}'

echo "Sending request:"
echo "$REQUEST5"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST5'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "✅ pixel_art method test completed"
