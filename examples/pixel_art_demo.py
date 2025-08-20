#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug Pixel Art Demo
Demonstrates various pixel art capabilities of PixelMug
"""

import json
import asyncio
import sys
import os
import base64

# Add parent directory to path for importing service modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer


class PixelArtDemo:
    """PixelMug Pixel Art demonstration class"""
    
    def __init__(self):
        self.server = MCPServer()
        self.request_id = 1
    
    def get_next_id(self):
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    async def send_pixel_art(self, device_id: str, name: str, pattern, width: int, height: int, duration: int = 20):
        """Send pixel art to device"""
        request = {
            "jsonrpc": "2.0",
            "method": "publish_action",
            "params": {
                "device_id": device_id,
                "action": "pixel_art",
                "params": {
                    "pattern": pattern,
                    "width": width,
                    "height": height,
                    "duration": duration
                }
            },
            "id": self.get_next_id()
        }
        
        print(f"🎨 Displaying: {name} ({width}x{height})")
        print(f"📤 Sending to device: {device_id}")
        
        try:
            response_str = await self.server.handle_request(json.dumps(request))
            response = json.loads(response_str)
            
            if "error" in response:
                print(f"❌ Error: {response['error']['message']}")
                return False
            else:
                print(f"✅ Successfully sent pixel art")
                return True
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return False
        finally:
            print("-" * 60)
    
    def create_simple_patterns(self):
        """Create simple pixel art patterns"""
        patterns = {}
        
        # 4x4 Checkboard
        patterns["checkboard_4x4"] = {
            "name": "4x4 Checkboard",
            "pattern": [
                ["#000000", "#FFFFFF", "#000000", "#FFFFFF"],
                ["#FFFFFF", "#000000", "#FFFFFF", "#000000"],
                ["#000000", "#FFFFFF", "#000000", "#FFFFFF"],
                ["#FFFFFF", "#000000", "#FFFFFF", "#000000"]
            ],
            "width": 4,
            "height": 4
        }
        
        # 6x6 Target
        patterns["target_6x6"] = {
            "name": "6x6 Target",
            "pattern": [
                ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                ["#FF0000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FF0000"],
                ["#FF0000", "#FFFFFF", "#FF0000", "#FF0000", "#FFFFFF", "#FF0000"],
                ["#FF0000", "#FFFFFF", "#FF0000", "#FF0000", "#FFFFFF", "#FF0000"],
                ["#FF0000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FF0000"],
                ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"]
            ],
            "width": 6,
            "height": 6
        }
        
        # 8x8 Diamond
        patterns["diamond_8x8"] = {
            "name": "8x8 Diamond",
            "pattern": [
                ["#000000", "#000000", "#000000", "#00FF00", "#00FF00", "#000000", "#000000", "#000000"],
                ["#000000", "#000000", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#000000", "#000000"],
                ["#000000", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#000000"],
                ["#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00"],
                ["#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00"],
                ["#000000", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#000000"],
                ["#000000", "#000000", "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#000000", "#000000"],
                ["#000000", "#000000", "#000000", "#00FF00", "#00FF00", "#000000", "#000000", "#000000"]
            ],
            "width": 8,
            "height": 8
        }
        
        # 6x6 Star
        patterns["star_6x6"] = {
            "name": "6x6 Star",
            "pattern": [
                ["#000000", "#000000", "#FFFF00", "#FFFF00", "#000000", "#000000"],
                ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
                ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
                ["#000000", "#FFFF00", "#000000", "#000000", "#FFFF00", "#000000"],
                ["#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00"]
            ],
            "width": 6,
            "height": 6
        }
        
        return patterns
    
    def create_coffee_themed_patterns(self):
        """Create coffee-themed pixel art patterns"""
        patterns = {}
        
        # Coffee Bean
        patterns["coffee_bean"] = {
            "name": "Coffee Bean",
            "pattern": [
                ["#000000", "#654321", "#654321", "#654321", "#654321", "#000000"],
                ["#654321", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#654321"],
                ["#654321", "#8B4513", "#DEB887", "#DEB887", "#8B4513", "#654321"],
                ["#654321", "#8B4513", "#DEB887", "#DEB887", "#8B4513", "#654321"],
                ["#654321", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#654321"],
                ["#000000", "#654321", "#654321", "#654321", "#654321", "#000000"]
            ],
            "width": 6,
            "height": 6
        }
        
        # Steam (animated effect suggestion)
        patterns["steam"] = {
            "name": "Steam Pattern",
            "pattern": [
                ["#000000", "#E6E6FA", "#000000", "#E6E6FA", "#000000", "#E6E6FA"],
                ["#E6E6FA", "#000000", "#E6E6FA", "#000000", "#E6E6FA", "#000000"],
                ["#000000", "#E6E6FA", "#000000", "#E6E6FA", "#000000", "#E6E6FA"],
                ["#E6E6FA", "#000000", "#E6E6FA", "#000000", "#E6E6FA", "#000000"],
                ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
                ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
            ],
            "width": 6,
            "height": 6
        }
        
        return patterns
    
    def create_rgb_pattern_example(self):
        """Create RGB tuple pattern example"""
        return {
            "name": "RGB Gradient",
            "pattern": [
                [[255, 0, 0], [255, 64, 0], [255, 128, 0], [255, 192, 0]],
                [[255, 64, 0], [255, 128, 0], [255, 192, 0], [255, 255, 0]],
                [[255, 128, 0], [255, 192, 0], [255, 255, 0], [192, 255, 0]],
                [[255, 192, 0], [255, 255, 0], [192, 255, 0], [128, 255, 0]]
            ],
            "width": 4,
            "height": 4
        }
    
    def create_base64_example(self):
        """Create a simple base64 encoded image example"""
        # This is a 2x2 PNG image with red, green, blue, white pixels
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWP8DwQMDAxwAEEB5gAAAAoAAf8IAFx+AAA=="
        
        return {
            "name": "Base64 2x2 Pattern",
            "pattern": base64_data,
            "width": 2,
            "height": 2
        }
    
    async def demo_basic_patterns(self):
        """Demonstrate basic patterns"""
        print("\n🎨 Basic Pixel Art Patterns Demo")
        print("=" * 60)
        
        device_id = "mug_001"
        patterns = self.create_simple_patterns()
        
        for pattern_id, pattern_info in patterns.items():
            await self.send_pixel_art(
                device_id,
                pattern_info["name"],
                pattern_info["pattern"],
                pattern_info["width"],
                pattern_info["height"],
                duration=15
            )
            await asyncio.sleep(1)  # Pause between patterns
    
    async def demo_coffee_patterns(self):
        """Demonstrate coffee-themed patterns"""
        print("\n☕ Coffee-Themed Pixel Art Demo")
        print("=" * 60)
        
        device_id = "mug_001"
        patterns = self.create_coffee_themed_patterns()
        
        for pattern_id, pattern_info in patterns.items():
            await self.send_pixel_art(
                device_id,
                pattern_info["name"],
                pattern_info["pattern"],
                pattern_info["width"],
                pattern_info["height"],
                duration=20
            )
            await asyncio.sleep(1)
    
    async def demo_different_formats(self):
        """Demonstrate different pattern formats"""
        print("\n🌈 Different Pattern Formats Demo")
        print("=" * 60)
        
        device_id = "mug_001"
        
        # RGB pattern
        rgb_pattern = self.create_rgb_pattern_example()
        await self.send_pixel_art(
            device_id,
            rgb_pattern["name"],
            rgb_pattern["pattern"],
            rgb_pattern["width"],
            rgb_pattern["height"],
            duration=15
        )
        
        await asyncio.sleep(1)
        
        # Base64 pattern
        base64_pattern = self.create_base64_example()
        await self.send_pixel_art(
            device_id,
            base64_pattern["name"],
            base64_pattern["pattern"],
            base64_pattern["width"],
            base64_pattern["height"],
            duration=15
        )
    
    async def demo_predefined_examples(self):
        """Demonstrate predefined examples from the service"""
        print("\n⭐ Predefined Examples Demo")
        print("=" * 60)
        
        device_id = "mug_001"
        
        # Get examples from the service
        help_info = await self.get_help_info()
        examples = help_info.get("pixel_art_examples", {})
        
        for example_name, example_info in examples.items():
            await self.send_pixel_art(
                device_id,
                example_info["description"],
                example_info["pattern"],
                example_info["width"],
                example_info["height"],
                duration=25
            )
            await asyncio.sleep(1)
    
    async def get_help_info(self):
        """Get service help information"""
        request = {
            "jsonrpc": "2.0",
            "method": "help",
            "params": {},
            "id": self.get_next_id()
        }
        
        response_str = await self.server.handle_request(json.dumps(request))
        response = json.loads(response_str)
        
        return response.get("result", {})
    
    async def run_all_demos(self):
        """Run all pixel art demonstrations"""
        print("🎯 PixelMug Pixel Art Demo Program")
        print("=" * 80)
        
        demos = [
            self.demo_predefined_examples,
            self.demo_basic_patterns,
            self.demo_coffee_patterns,
            self.demo_different_formats
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
        
        print("\n🎉 Pixel Art Demo completed!")
        print("=" * 80)


async def interactive_pixel_art():
    """Interactive pixel art mode"""
    demo = PixelArtDemo()
    
    print("🎨 PixelMug Pixel Art Interactive Mode")
    print("=" * 50)
    print("Commands:")
    print("  demo - Run all demonstrations")
    print("  basic - Show basic patterns")
    print("  coffee - Show coffee-themed patterns")
    print("  formats - Show different format examples")
    print("  examples - Show predefined examples")
    print("  custom - Create custom pattern")
    print("  exit - Exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n🎨 Enter command: ").strip().lower()
            
            if command == "exit":
                print("👋 Goodbye!")
                break
            elif command == "demo":
                await demo.run_all_demos()
            elif command == "basic":
                await demo.demo_basic_patterns()
            elif command == "coffee":
                await demo.demo_coffee_patterns()
            elif command == "formats":
                await demo.demo_different_formats()
            elif command == "examples":
                await demo.demo_predefined_examples()
            elif command == "custom":
                print("🔧 Custom pattern creation:")
                print("Example: 2x2 red-green-blue-white pattern")
                pattern = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
                await demo.send_pixel_art("mug_001", "Custom 2x2", pattern, 2, 2)
            else:
                print("❌ Unknown command. Available: demo, basic, coffee, formats, examples, custom, exit")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error occurred: {str(e)}")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo = PixelArtDemo()
            await demo.run_all_demos()
        elif sys.argv[1] == "interactive":
            await interactive_pixel_art()
        else:
            print("Usage: python pixel_art_demo.py [demo|interactive]")
    else:
        # Default run demo
        demo = PixelArtDemo()
        await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
