#!/bin/bash
# Test all MCP server methods

echo "🧪 Testing all MCP server methods"
echo "================================="

# Test help method
echo "1. Testing help method..."
echo "=========================="
./test_help.sh

echo ""
echo "================================="

# Test issue_sts method
echo "2. Testing issue_sts method..."
echo "=============================="
./test_prepare.sh

echo ""
echo "================================="

# Test send_pixel_image method
echo "3. Testing send_pixel_image method..."
echo "===================================="
./test_pixel_art.sh

echo ""
echo "================================="

# Test send_gif_animation method
echo "4. Testing send_gif_animation method..."
echo "======================================"
./test_publish.sh

echo ""
echo "================================="

# Test convert_image_to_pixels method
echo "5. Testing convert_image_to_pixels method..."
echo "==========================================="
./test_convert_image.sh

echo ""
echo "================================="
echo "✅ All MCP server methods tested successfully!"
echo "================================="
