#!/bin/bash
# Test convert_image_to_pixels method

echo "🧪 Testing convert_image_to_pixels method"
echo "======================================="

# Test case 1: Simple 1x1 pixel image
echo "Test case 1: Simple 1x1 pixel image"
REQUEST1='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "target_width": 4, "target_height": 4}, "id": 1}'

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

# Test case 2: Different resize methods
echo "Test case 2: Different resize methods"
echo "Testing with nearest neighbor method..."
REQUEST2='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "target_width": 8, "target_height": 8, "resize_method": "nearest"}, "id": 2}'

echo "Sending request:"
echo "$REQUEST2"
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

# Test case 3: Bilinear resize method
echo "Test case 3: Bilinear resize method"
REQUEST3='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "target_width": 6, "target_height": 6, "resize_method": "bilinear"}, "id": 3}'

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
REQUEST4='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {}, "id": 4}'

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

# Test case 5: Invalid resize method
echo "Test case 5: Invalid resize method"
REQUEST5='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "target_width": 4, "target_height": 4, "resize_method": "invalid_method"}, "id": 5}'

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
echo "----------------------------------------"

# Test case 6: Invalid target dimensions
echo "Test case 6: Invalid target dimensions"
REQUEST6='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "target_width": 200, "target_height": 200}, "id": 6}'

echo "Sending request:"
echo "$REQUEST6"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST6'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "----------------------------------------"

# Test case 7: Invalid base64 data
echo "Test case 7: Invalid base64 data"
REQUEST7='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "invalid_base64_data", "target_width": 4, "target_height": 4}, "id": 7}'

echo "Sending request:"
echo "$REQUEST7"
echo ""

echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST7'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "✅ convert_image_to_pixels method test completed"
