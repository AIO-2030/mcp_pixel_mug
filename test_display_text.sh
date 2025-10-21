#!/bin/bash
# Test send_display_text method

echo "🧪 Testing send_display_text method"
echo "=================================="

# Test case 1: Normal short text
echo "Test case 1: Normal short text"
REQUEST1='{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001", "text": "Hello Pixel Mug!"}, "id": 1}'

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

# Test case 2: Empty string (allowed)
echo "Test case 2: Empty string"
REQUEST2='{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001", "text": ""}, "id": 2}'

echo "Sending request:"
echo "Empty text"
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

# Test case 3: Over 200 chars (should fail)
echo "Test case 3: Over 200 characters (expect validation error)"
LONG_TEXT=$(python3 - <<'PY'
text = 'A' * 205
import json
print(json.dumps(text))
PY
)
REQUEST3='{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001", "text": '"$LONG_TEXT"'}, "id": 3}'

echo "Sending request:"
echo "Text length: 205"
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

# Test case 4: Missing required params (no text)
echo "Test case 4: Missing required parameter 'text'"
REQUEST4='{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001"}, "id": 4}'

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

# Test case 5: Non-string text (should fail type validation in service)
echo "Test case 5: Non-string text (number)"
REQUEST5='{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001", "text": 12345}, "id": 5}'

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
echo "✅ send_display_text method test completed"


