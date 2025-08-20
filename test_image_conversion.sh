#!/bin/bash
# Test convert_image_to_pixels method

echo "🖼️ Testing convert_image_to_pixels method"
echo "==========================================="

# Test case 1: Basic image conversion (using a simple base64 encoded 2x2 image)
echo "Test case 1: Basic image conversion"
REQUEST1='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==", "target_width": 4, "target_height": 4}, "id": 1}'

echo "Sending request:"
echo "Converting 2x2 base64 image to 4x4 pixel matrix..."
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

# Test case 2: Different target size
echo "Test case 2: Convert to 8x8 pixel matrix"
REQUEST2='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==", "target_width": 8, "target_height": 8, "resize_method": "nearest"}, "id": 2}'

echo "Sending request:"
echo "Converting to 8x8 with nearest neighbor..."
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

# Test case 3: Invalid parameters
echo "Test case 3: Invalid target size"
REQUEST3='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"image_data": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==", "target_width": 200, "target_height": 8}, "id": 3}'

echo "Sending request:"
echo "Testing with invalid target_width (200, should fail)..."
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

# Test case 4: Missing image_data
echo "Test case 4: Missing image_data parameter"
REQUEST4='{"jsonrpc": "2.0", "method": "convert_image_to_pixels", "params": {"target_width": 8, "target_height": 8}, "id": 4}'

echo "Sending request:"
echo "Testing without image_data parameter..."
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

# Test case 5: Test help method includes new function
echo "Test case 5: Verify help includes convert_image_to_pixels"
echo "Testing help method for new function description..."
echo ""

python3 -c "
import sys
import asyncio
import json
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '{\"jsonrpc\": \"2.0\", \"method\": \"help\", \"params\": {}, \"id\": 5}'
    response = await server.handle_request(request)
    result = json.loads(response)
    
    methods = result.get('result', {}).get('methods', [])
    convert_method = None
    for method in methods:
        if method.get('name') == 'convert_image_to_pixels':
            convert_method = method
            break
    
    if convert_method:
        print('✅ convert_image_to_pixels method found in help:')
        print(json.dumps(convert_method, indent=2))
    else:
        print('❌ convert_image_to_pixels method NOT found in help')

asyncio.run(test())
"

echo ""
echo "✅ convert_image_to_pixels method test completed"
