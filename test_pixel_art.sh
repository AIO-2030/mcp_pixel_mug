#!/bin/bash
# Test send_pixel_image method

echo "🧪 Testing send_pixel_image method"
echo "=================================="

# Test case 1: Simple 2x2 pattern
echo "Test case 1: Simple 2x2 pattern"
REQUEST1='{"jsonrpc": "2.0", "method": "send_pixel_image", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "image_data": [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]], "target_width": 2, "target_height": 2}, "id": 1}'

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
REQUEST2='{"jsonrpc": "2.0", "method": "send_pixel_image", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "image_data": [["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"], ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"], ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"], ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]], "target_width": 8, "target_height": 8}, "id": 2}'

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

# Test case 3: Base64 encoded image
echo "Test case 3: Base64 encoded image"
REQUEST3='{"jsonrpc": "2.0", "method": "send_pixel_image", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==", "target_width": 2, "target_height": 2}, "id": 3}'

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

# Test case 4: Missing required parameters
echo "Test case 4: Missing required parameters"
REQUEST4='{"jsonrpc": "2.0", "method": "send_pixel_image", "params": {"product_id": "ABC123DEF", "device_name": "mug_001"}, "id": 4}'

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

# Test case 5: Invalid color format in pixel matrix
echo "Test case 5: Invalid color format in pixel matrix"
REQUEST5='{"jsonrpc": "2.0", "method": "send_pixel_image", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "image_data": [["RED", "GREEN"], ["BLUE", "WHITE"]], "target_width": 2, "target_height": 2}, "id": 5}'

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
echo "✅ send_pixel_image method test completed"
