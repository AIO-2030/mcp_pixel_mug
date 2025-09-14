#!/bin/bash
# Test send_gif_animation method

echo "🧪 Testing send_gif_animation method"
echo "==================================="

# Test case 1: Simple GIF animation
echo "Test case 1: Simple GIF animation"
REQUEST1='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "frame_delay": 100, "loop_count": 0, "target_width": 16, "target_height": 16}, "id": 1}'

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

# Test case 2: GIF with custom frame delay
echo "Test case 2: GIF with custom frame delay"
REQUEST2='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "frame_delay": 200, "loop_count": 3, "target_width": 8, "target_height": 8}, "id": 2}'

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

# Test case 3: Frame array format
echo "Test case 3: Frame array format"
REQUEST3='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "gif_data": [{"frame_index": 0, "pixel_matrix": [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]], "duration": 100}, {"frame_index": 1, "pixel_matrix": [["#FFFFFF", "#000000"], ["#FFFF00", "#FF00FF"]], "duration": 100}], "frame_delay": 150, "loop_count": 1, "target_width": 2, "target_height": 2}, "id": 3}'

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
REQUEST4='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001"}, "id": 4}'

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

# Test case 5: Invalid frame delay
echo "Test case 5: Invalid frame delay"
REQUEST5='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "frame_delay": 5000, "loop_count": 0, "target_width": 16, "target_height": 16}, "id": 5}'

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

# Test case 6: Invalid loop count
echo "Test case 6: Invalid loop count"
REQUEST6='{"jsonrpc": "2.0", "method": "send_gif_animation", "params": {"product_id": "ABC123DEF", "device_name": "mug_001", "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "frame_delay": 100, "loop_count": 1001, "target_width": 16, "target_height": 16}, "id": 6}'

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
echo "✅ send_gif_animation method test completed"
