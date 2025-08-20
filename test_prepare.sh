#!/bin/bash
# Test prepare_mqtt_connection method

echo "🧪 Testing prepare_mqtt_connection method"
echo "===================================="

# Test case 1: Normal device
echo "Test case 1: Normal device mug_001"
REQUEST1='{"jsonrpc": "2.0", "method": "prepare_mqtt_connection", "params": {"device_id": "mug_001"}, "id": 1}'

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

# Test case 2: Unregistered device
echo "Test case 2: Unregistered device mug_999"
REQUEST2='{"jsonrpc": "2.0", "method": "prepare_mqtt_connection", "params": {"device_id": "mug_999"}, "id": 2}'

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

# Test case 3: Missing parameter
echo "Test case 3: Missing device_id parameter"
REQUEST3='{"jsonrpc": "2.0", "method": "prepare_mqtt_connection", "params": {}, "id": 3}'

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
echo "✅ prepare_mqtt_connection method test completed"
