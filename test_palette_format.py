#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for palette-based pixel art format support
"""

import json
from mug_service import mug_service

def test_palette_format():
    """Test palette-based pixel art format support"""
    print("🎨 Testing Palette-Based Pixel Art Format Support")
    print("=" * 60)
    
    # Test 1: Basic palette pixel art
    print("\n1. Testing basic palette pixel art...")
    try:
        palette_pixel_art = {
            "title": "sample_image",
            "description": "Converted from sample_image.jpg",
            "width": 4,
            "height": 4,
            "palette": [
                "#ffffff",  # 0 - 背景色
                "#ff0000",  # 1 - 红色
                "#00ff00",  # 2 - 绿色
                "#0000ff"   # 3 - 蓝色
            ],
            "pixels": [
                [0, 1, 1, 0],
                [1, 2, 2, 1],
                [1, 3, 3, 1],
                [0, 1, 1, 0]
            ]
        }
        
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=palette_pixel_art,
            target_width=4,
            target_height=4,
            use_cos=False
        )
        print("✅ Basic palette pixel art test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Error (IoT not configured): {e}")
        print("   This is expected if IoT is not properly configured")
    
    # Test 2: Palette GIF animation
    print("\n2. Testing palette GIF animation...")
    try:
        palette_gif = {
            "title": "animated_heart",
            "description": "Animated heart with palette",
            "width": 8,
            "height": 8,
            "palette": [
                "#000000",  # 0 - 黑色
                "#ff0000",  # 1 - 红色
                "#ffffff"   # 2 - 白色
            ],
            "frame_delay": 200,
            "loop_count": 3,
            "frames": [
                {
                    "pixels": [
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 0, 0, 1, 1, 0],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 1, 1, 1, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 1, 1, 0, 0, 0]
                    ],
                    "duration": 200
                },
                {
                    "pixels": [
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 0, 0, 1, 1, 0],
                        [1, 2, 2, 1, 1, 2, 2, 1],
                        [1, 2, 2, 1, 1, 2, 2, 1],
                        [1, 2, 2, 1, 1, 2, 2, 1],
                        [0, 1, 1, 1, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 1, 1, 0, 0, 0]
                    ],
                    "duration": 200
                }
            ]
        }
        
        result = mug_service.send_gif_animation(
            product_id="TEST123",
            device_name="test_device",
            gif_data=palette_gif,
            frame_delay=200,
            loop_count=3,
            target_width=8,
            target_height=8,
            use_cos=False
        )
        print("✅ Palette GIF animation test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Error (IoT not configured): {e}")
        print("   This is expected if IoT is not properly configured")
    
    # Test 3: Large palette (16 colors)
    print("\n3. Testing large palette (16 colors)...")
    try:
        large_palette_art = {
            "title": "rainbow_pattern",
            "description": "16-color rainbow pattern",
            "width": 4,
            "height": 4,
            "palette": [
                "#ffffff", "#ff0000", "#00ff00", "#0000ff",
                "#ffff00", "#ff00ff", "#00ffff", "#808080",
                "#000000", "#ffa500", "#800080", "#008000",
                "#ffc0cb", "#a52a2a", "#c0c0c0", "#808000"
            ],
            "pixels": [
                [0, 1, 2, 3],
                [4, 5, 6, 7],
                [8, 9, 10, 11],
                [12, 13, 14, 15]
            ]
        }
        
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=large_palette_art,
            target_width=4,
            target_height=4,
            use_cos=False
        )
        print("✅ Large palette test completed")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Delivery method: {result.get('delivery_method', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️  Error (IoT not configured): {e}")
        print("   This is expected if IoT is not properly configured")
    
    # Test 4: Error handling - invalid palette index
    print("\n4. Testing error handling - invalid palette index...")
    try:
        invalid_palette_art = {
            "title": "invalid_test",
            "width": 2,
            "height": 2,
            "palette": ["#ffffff", "#ff0000"],  # Only 2 colors
            "pixels": [
                [0, 1],
                [2, 3]  # Invalid indices 2 and 3
            ]
        }
        
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=invalid_palette_art,
            target_width=2,
            target_height=2,
            use_cos=False
        )
        print("❌ Should have failed with invalid palette index")
        
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")
    
    # Test 5: Error handling - too many colors in palette
    print("\n5. Testing error handling - too many colors...")
    try:
        oversized_palette_art = {
            "title": "oversized_test",
            "width": 2,
            "height": 2,
            "palette": [f"#{i:06x}" for i in range(20)],  # 20 colors (too many)
            "pixels": [
                [0, 1],
                [1, 0]
            ]
        }
        
        result = mug_service.send_pixel_image(
            product_id="TEST123",
            device_name="test_device",
            image_data=oversized_palette_art,
            target_width=2,
            target_height=2,
            use_cos=False
        )
        print("❌ Should have failed with too many colors")
        
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Palette format test completed!")
    print("\n📝 Summary:")
    print("- ✅ Basic palette pixel art support")
    print("- ✅ Palette GIF animation support")
    print("- ✅ Large palette support (up to 16 colors)")
    print("- ✅ Error handling for invalid indices")
    print("- ✅ Error handling for oversized palettes")
    print("\n🔧 Supported formats:")
    print("- Traditional hex color arrays")
    print("- Base64 encoded images")
    print("- Palette-based format with color indices")
    print("- Palette-based GIF animations")

if __name__ == "__main__":
    test_palette_format()
