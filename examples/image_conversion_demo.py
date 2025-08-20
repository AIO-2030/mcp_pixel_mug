#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug Image Conversion Demo
Demonstrates image-to-pixel conversion capabilities
"""

import json
import asyncio
import sys
import os
import base64

# Add parent directory to path for importing service modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer


class ImageConversionDemo:
    """PixelMug Image Conversion demonstration class"""
    
    def __init__(self):
        self.server = MCPServer()
        self.request_id = 1
    
    def get_next_id(self):
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    async def convert_image(self, name: str, image_data: str, target_width: int = 16, target_height: int = 16, resize_method: str = "nearest"):
        """Convert image to pixel matrix"""
        request = {
            "jsonrpc": "2.0",
            "method": "convert_image_to_pixels",
            "params": {
                "image_data": image_data,
                "target_width": target_width,
                "target_height": target_height,
                "resize_method": resize_method
            },
            "id": self.get_next_id()
        }
        
        print(f"🖼️ Converting: {name}")
        print(f"📏 Target size: {target_width}x{target_height}")
        print(f"🔄 Resize method: {resize_method}")
        
        try:
            response_str = await self.server.handle_request(json.dumps(request))
            response = json.loads(response_str)
            
            if "error" in response:
                print(f"❌ Error: {response['error']['message']}")
                return None
            else:
                result = response["result"]
                original_size = result["original_size"]
                print(f"✅ Converted from {original_size['width']}x{original_size['height']} to {target_width}x{target_height}")
                print(f"📊 Total pixels: {result['total_pixels']}")
                return result
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return None
        finally:
            print("-" * 60)
    
    async def convert_and_display(self, device_id: str, name: str, image_data: str, target_width: int = 16, target_height: int = 16, duration: int = 20):
        """Convert image and display on device"""
        # First convert the image
        conversion_result = await self.convert_image(name, image_data, target_width, target_height)
        
        if conversion_result is None:
            return False
        
        # Then send to device using pixel_art action
        pixel_matrix = conversion_result["pixel_matrix"]
        
        request = {
            "jsonrpc": "2.0",
            "method": "publish_action",
            "params": {
                "device_id": device_id,
                "action": "pixel_art",
                "params": {
                    "pattern": pixel_matrix,
                    "width": target_width,
                    "height": target_height,
                    "duration": duration
                }
            },
            "id": self.get_next_id()
        }
        
        print(f"📤 Sending converted image to device: {device_id}")
        
        try:
            response_str = await self.server.handle_request(json.dumps(request))
            response = json.loads(response_str)
            
            if "error" in response:
                print(f"❌ Display Error: {response['error']['message']}")
                return False
            else:
                print(f"✅ Successfully displayed converted image on device")
                return True
                
        except Exception as e:
            print(f"💥 Display Exception: {str(e)}")
            return False
        finally:
            print("-" * 60)
    
    def get_sample_images(self):
        """Get sample base64 encoded images for testing"""
        # These are simple test images in base64 format
        return {
            "simple_2x2": {
                "name": "Simple 2x2 Test Pattern",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA==",
                "description": "2x2 pixel test image (white and black)"
            },
            "gradient_4x4": {
                "name": "4x4 Gradient Pattern",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAYAAACp8Z5+AAAANklEQVQIHWNgwAH+//9vwKXm////RlxqDh8+bMClBpcaXGpwqcGlBpcaXGpwqcGlBhYAAP//DUAAATYhQs8AAAAASUVORK5CYII=",
                "description": "4x4 gradient pattern"
            }
        }
    
    async def demo_basic_conversion(self):
        """Demonstrate basic image conversion"""
        print("\n🖼️ Basic Image Conversion Demo")
        print("=" * 60)
        
        sample_images = self.get_sample_images()
        
        for image_id, image_info in sample_images.items():
            print(f"\n📸 Testing: {image_info['description']}")
            
            # Convert to different sizes
            sizes = [(8, 8), (16, 16), (12, 8)]
            
            for width, height in sizes:
                await self.convert_image(
                    f"{image_info['name']} -> {width}x{height}",
                    image_info["data"],
                    width,
                    height
                )
                await asyncio.sleep(0.5)
    
    async def demo_resize_methods(self):
        """Demonstrate different resize methods"""
        print("\n🔄 Resize Methods Demo")
        print("=" * 60)
        
        sample_images = self.get_sample_images()
        test_image = sample_images["simple_2x2"]
        
        resize_methods = ["nearest", "bilinear", "bicubic"]
        
        for method in resize_methods:
            print(f"\n🎯 Testing resize method: {method}")
            await self.convert_image(
                f"{test_image['name']} ({method})",
                test_image["data"],
                8, 8,
                method
            )
            await asyncio.sleep(0.5)
    
    async def demo_convert_and_display(self):
        """Demonstrate converting and displaying images"""
        print("\n📺 Convert and Display Demo")
        print("=" * 60)
        
        device_id = "mug_001"
        sample_images = self.get_sample_images()
        
        for image_id, image_info in sample_images.items():
            await self.convert_and_display(
                device_id,
                image_info["name"],
                image_info["data"],
                target_width=8,
                target_height=8,
                duration=15
            )
            await asyncio.sleep(1)
    
    async def demo_error_handling(self):
        """Demonstrate error handling"""
        print("\n⚠️ Error Handling Demo")
        print("=" * 60)
        
        # Test with invalid base64
        print("\n🧪 Testing invalid base64 data:")
        await self.convert_image(
            "Invalid Base64",
            "invalid_base64_data",
            8, 8
        )
        
        # Test with invalid dimensions
        print("\n🧪 Testing invalid dimensions:")
        sample_images = self.get_sample_images()
        test_image = sample_images["simple_2x2"]
        
        await self.convert_image(
            "Invalid Size (200x200)",
            test_image["data"],
            200, 200  # Should fail - too large
        )
    
    async def show_pixel_preview(self, pixel_matrix, width, height, name):
        """Show a text preview of the pixel matrix"""
        print(f"\n🎨 Pixel Preview: {name}")
        print("=" * min(width * 3, 60))
        
        for y in range(min(height, 20)):  # Limit display height
            row_str = ""
            for x in range(min(width, 20)):  # Limit display width
                color = pixel_matrix[y][x]
                # Convert hex color to a simple character representation
                if color == "#000000":
                    row_str += "██"
                elif color == "#ffffff":
                    row_str += "  "
                else:
                    # Use a medium character for other colors
                    row_str += "▓▓"
            print(row_str)
        
        if height > 20 or width > 20:
            print("... (truncated for display)")
        print("")
    
    async def demo_with_preview(self):
        """Demonstrate conversion with text preview"""
        print("\n👁️ Conversion with Preview Demo")
        print("=" * 60)
        
        sample_images = self.get_sample_images()
        test_image = sample_images["simple_2x2"]
        
        sizes = [(4, 4), (8, 8), (16, 8)]
        
        for width, height in sizes:
            result = await self.convert_image(
                f"Preview Test {width}x{height}",
                test_image["data"],
                width, height
            )
            
            if result:
                await self.show_pixel_preview(
                    result["pixel_matrix"],
                    width, height,
                    f"{width}x{height} Pattern"
                )
    
    async def run_all_demos(self):
        """Run all image conversion demonstrations"""
        print("🎯 PixelMug Image Conversion Demo Program")
        print("=" * 80)
        
        demos = [
            self.demo_basic_conversion,
            self.demo_resize_methods,
            self.demo_with_preview,
            self.demo_convert_and_display,
            self.demo_error_handling
        ]
        
        for demo in demos:
            try:
                await demo()
                await asyncio.sleep(2)  # Pause between demo sections
            except KeyboardInterrupt:
                print("\n\n⏸️ Demo interrupted by user")
                break
            except Exception as e:
                print(f"\n💥 Error occurred during demo: {str(e)}")
        
        print("\n🎉 Image Conversion Demo completed!")
        print("=" * 80)


async def interactive_image_conversion():
    """Interactive image conversion mode"""
    demo = ImageConversionDemo()
    
    print("🖼️ PixelMug Image Conversion Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  demo - Run all demonstrations")
    print("  convert - Convert sample image")
    print("  display - Convert and display on device")
    print("  preview - Show text preview of conversion")
    print("  methods - Test different resize methods")
    print("  errors - Test error handling")
    print("  exit - Exit")
    print("=" * 60)
    
    while True:
        try:
            command = input("\n🖼️ Enter command: ").strip().lower()
            
            if command == "exit":
                print("👋 Goodbye!")
                break
            elif command == "demo":
                await demo.run_all_demos()
            elif command == "convert":
                await demo.demo_basic_conversion()
            elif command == "display":
                await demo.demo_convert_and_display()
            elif command == "preview":
                await demo.demo_with_preview()
            elif command == "methods":
                await demo.demo_resize_methods()
            elif command == "errors":
                await demo.demo_error_handling()
            else:
                print("❌ Unknown command. Available: demo, convert, display, preview, methods, errors, exit")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error occurred: {str(e)}")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo = ImageConversionDemo()
            await demo.run_all_demos()
        elif sys.argv[1] == "interactive":
            await interactive_image_conversion()
        else:
            print("Usage: python image_conversion_demo.py [demo|interactive]")
    else:
        # Default run demo
        demo = ImageConversionDemo()
        await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
