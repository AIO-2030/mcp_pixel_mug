#!/bin/bash
# Test help method

echo "🧪 Testing help method"
echo "===================="

# Test request
REQUEST='{"jsonrpc": "2.0", "method": "help", "params": {}, "id": 1}'

echo "Sending request:"
echo "$REQUEST"
echo ""

# Use Python to test directly
echo "Response:"
python3 -c "
import sys
import asyncio
sys.path.append('.')
from mcp_server import MCPServer

async def test():
    server = MCPServer()
    request = '$REQUEST'
    response = await server.handle_request(request)
    print(response)

asyncio.run(test())
"

echo ""
echo "✅ Help method test completed"
