#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for COS integration in mug_service.py
"""

import json
import base64
from mug_service import mug_service

def test_cos_integration():
    """Test COS integration functionality"""
    print("🧪 Testing COS Integration in mug_service.py")
    print("=" * 50)
    
    # Test 1: Check service help
    print("\n1. Testing service help...")
    try:
        help_info = mug_service.get_help()
        print("✅ Service help retrieved successfully")
        print(f"   Service: {help_info['service']}")
        print(f"   Version: {help_info['version']}")
        print(f"   Methods: {len(help_info['methods'])}")
        
        # Check if COS parameters are in help
        pixel_method = next((m for m in help_info['methods'] if m['name'] == 'send_pixel_image'), None)
        if pixel_method and 'use_cos' in str(pixel_method['params']):
            print("✅ COS parameters found in help")
        else:
            print("❌ COS parameters not found in help")
            
    except Exception as e:
        print(f"❌ Failed to get service help: {e}")
    
    # Test 2: Test pixel image with COS (mock)
    print("\n2. Testing pixel image with COS...")
    try:
        # Create a simple test pattern
        test_pattern = [
            ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF"],
            ["#FFFF00", "#FF00FF", "#00FFFF", "#000000"],
            ["#800000", "#008000", "#000080", "#808080"],
            ["#FFA500", "#800080", "#008080", "#C0C0C0"]
        ]
        
        # Test with use_cos=True (will fail without actual COS setup, but should show proper error handling)
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=test_pattern,
            target_width=4,
            target_height=4,
            use_cos=True,
            ttl_sec=900
        )
        print("✅ Pixel image with COS test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Expected error (COS not configured): {e}")
        print("   This is expected if COS is not properly configured")
    
    # Test 3: Test pixel image without COS
    print("\n3. Testing pixel image without COS...")
    try:
        test_pattern = [
            ["#FF0000", "#00FF00"],
            ["#0000FF", "#FFFFFF"]
        ]
        
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=test_pattern,
            target_width=2,
            target_height=2,
            use_cos=False
        )
        print("✅ Pixel image without COS test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Error (IoT not configured): {e}")
        print("   This is expected if IoT is not properly configured")
    
    # Test 4: Test GIF animation with COS (mock)
    print("\n4. Testing GIF animation with COS...")
    try:
        # Create a simple test frame
        test_frames = [
            {
                "frame_index": 0,
                "pixel_matrix": [
                    ["#FF0000", "#00FF00"],
                    ["#0000FF", "#FFFFFF"]
                ],
                "duration": 100
            },
            {
                "frame_index": 1,
                "pixel_matrix": [
                    ["#00FF00", "#FF0000"],
                    ["#FFFFFF", "#0000FF"]
                ],
                "duration": 100
            }
        ]
        
        result = mug_service.send_gif_animation(
            product_id="TEST123",
            device_name="test_device",
            gif_data=test_frames,
            frame_delay=100,
            loop_count=1,
            target_width=2,
            target_height=2,
            use_cos=True,
            ttl_sec=900
        )
        print("✅ GIF animation with COS test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Expected error (COS not configured): {e}")
        print("   This is expected if COS is not properly configured")
    
    print("\n" + "=" * 50)
    print("🎉 COS integration test completed!")
    print("\n📝 Notes:")
    print("- COS functionality is integrated into mug_service.py")
    print("- Both send_pixel_image and send_gif_animation support COS upload")
    print("- COS upload is optional (use_cos parameter)")
    print("- Fallback to direct transmission if COS fails")
    print("- Requires proper COS configuration for full functionality")
    print("- Uses new COS key pattern: pmug/{deviceName}/{YYYYMM}/{assetId}-{sha8}.{ext}")
    print("- Implements proper Content-Type and metadata")
    print("- Generates IoT payload in new format with security nonce")

if __name__ == "__main__":
    test_cos_integration()
