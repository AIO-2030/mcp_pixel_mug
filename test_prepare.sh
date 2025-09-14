#!/bin/bash
# Test issue_sts method

echo "🧪 Testing issue_sts method"
echo "=========================="

# Test case 1: Normal device
echo "Test case 1: Normal device mug_001"
REQUEST1='{"jsonrpc": "2.0", "method": "issue_sts", "params": {"product_id": "ABC123DEF", "device_name": "mug_001"}, "id": 1}'

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

# Test case 2: Different device
echo "Test case 2: Different device mug_002"
REQUEST2='{"jsonrpc": "2.0", "method": "issue_sts", "params": {"product_id": "ABC123DEF", "device_name": "mug_002"}, "id": 2}'

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

# Test case 3: Missing required parameters
echo "Test case 3: Missing required parameters"
REQUEST3='{"jsonrpc": "2.0", "method": "issue_sts", "params": {}, "id": 3}'

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
echo "✅ issue_sts method test completed"
