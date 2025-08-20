#!/bin/bash
# Test publish_action method

echo "🧪 Testing publish_action method"
echo "============================="

# Test case 1: Heat operation
echo "Test case 1: Heat operation"
REQUEST1='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "heat", "params": {"temperature": 60}}, "id": 1}'

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

# Test case 2: Display information
echo "Test case 2: Display information"
REQUEST2='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "display", "params": {"text": "Hello PixelMug!", "duration": 30}}, "id": 2}'

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

# Test case 3: Color change operation
echo "Test case 3: Color change operation"
REQUEST3='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "color", "params": {"color": "#FF5733", "mode": "gradient"}}, "id": 3}'

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

# Test case 4: Brewing operation
echo "Test case 4: Brewing operation"
REQUEST4='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "brew", "params": {"type": "espresso", "strength": "strong"}}, "id": 4}'

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

# Test case 5: Invalid operation
echo "Test case 5: Invalid operation"
REQUEST5='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "invalid_action", "params": {}}, "id": 5}'

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

# Test case 6: Parameter validation failure
echo "Test case 6: Temperature parameter out of range"
REQUEST6='{"jsonrpc": "2.0", "method": "publish_action", "params": {"device_id": "mug_001", "action": "heat", "params": {"temperature": 150}}, "id": 6}'

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
echo "✅ publish_action method test completed"
