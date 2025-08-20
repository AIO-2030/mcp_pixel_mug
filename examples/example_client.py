#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug MCP Client Usage Example
Demonstrates how to call various MCP service functions
"""

import json
import asyncio
import sys
import os

# Add parent directory to path for importing service modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer


class PixelMugClient:
    """PixelMug client example class"""
    
    def __init__(self):
        self.server = MCPServer()
        self.request_id = 1
    
    def get_next_id(self):
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    async def call_method(self, method: str, params: dict = None):
        """Call MCP method"""
        if params is None:
            params = {}
            
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.get_next_id()
        }
        
        print(f"🔄 Calling method: {method}")
        print(f"📤 Request: {json.dumps(request, ensure_ascii=False, indent=2)}")
        
        try:
            response_str = await self.server.handle_request(json.dumps(request))
            response = json.loads(response_str)
            
            print(f"📥 Response: {json.dumps(response, ensure_ascii=False, indent=2)}")
            
            if "error" in response:
                print(f"❌ Error: {response['error']['message']}")
                return None
            else:
                print(f"✅ Success")
                return response.get("result")
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return None
        finally:
            print("-" * 60)
    
    async def demo_help(self):
        """Demonstrate getting help information"""
        print("\n🆘 Getting Help Information")
        print("=" * 60)
        
        result = await self.call_method("help")
        if result:
            print(f"📋 Service Information:")
            print(f"   Name: {result.get('service')}")
            print(f"   Version: {result.get('version')}")
            print(f"   Description: {result.get('description')}")
            
            print(f"\n🔧 Supported Methods:")
            for method in result.get('methods', []):
                print(f"   • {method['name']}: {method['description']}")
            
            print(f"\n🎮 Supported Operations:")
            for action in result.get('supported_actions', []):
                print(f"   • {action['action']}: {action['description']}")
    
    async def demo_prepare_connection(self):
        """Demonstrate MQTT connection preparation"""
        print("\n🔌 Preparing MQTT Connection")
        print("=" * 60)
        
        # Test normal device
        device_id = "mug_001"
        result = await self.call_method("prepare_mqtt_connection", {"device_id": device_id})
        
        if result:
            print(f"🏠 Connection Information:")
            print(f"   Host: {result.get('host')}")
            print(f"   Port: {result.get('port')}")
            print(f"   Protocol: {result.get('protocol')}")
            print(f"   Client ID: {result.get('client_id')}")
            print(f"   Command Topic: {result.get('topic')}")
            print(f"   Status Topic: {result.get('status_topic')}")
            
            # Display certificate information (abbreviated)
            cert = result.get('cert', '')
            if cert:
                print(f"   Certificate: {cert[:50]}... ({len(cert)} characters)")
    
    async def demo_device_operations(self):
        """Demonstrate various device operations"""
        print("\n🎛️ Device Operation Demonstration")
        print("=" * 60)
        
        device_id = "mug_001"
        
        # 1. Heat operation
        print("\n🔥 Heat Operation")
        await self.call_method("publish_action", {
            "device_id": device_id,
            "action": "heat",
            "params": {"temperature": 65}
        })
        
        # 2. Display information
        print("\n📺 Display Information")
        await self.call_method("publish_action", {
            "device_id": device_id,
            "action": "display", 
            "params": {
                "text": "Good Morning!",
                "duration": 20
            }
        })
        
        # 3. Color operation
        print("\n🌈 Color Operation")
        await self.call_method("publish_action", {
            "device_id": device_id,
            "action": "color",
            "params": {
                "color": "#FF6B6B",
                "mode": "gradient"
            }
        })
        
        # 4. Brew coffee
        print("\n☕ Brew Coffee")
        await self.call_method("publish_action", {
            "device_id": device_id,
            "action": "brew",
            "params": {
                "type": "americano",
                "strength": "medium"
            }
        })
    
    async def demo_error_handling(self):
        """Demonstrate error handling"""
        print("\n🚫 Error Handling Demonstration")
        print("=" * 60)
        
        # 1. Unregistered device
        print("\n❌ Unregistered Device")
        await self.call_method("prepare_mqtt_connection", {"device_id": "mug_999"})
        
        # 2. Invalid operation
        print("\n❌ Invalid Operation")
        await self.call_method("publish_action", {
            "device_id": "mug_001",
            "action": "fly",
            "params": {}
        })
        
        # 3. Parameter validation failure
        print("\n❌ Parameter Out of Range")
        await self.call_method("publish_action", {
            "device_id": "mug_001", 
            "action": "heat",
            "params": {"temperature": 150}
        })
        
        # 4. Missing required parameter
        print("\n❌ Missing Required Parameter")
        await self.call_method("prepare_mqtt_connection", {})
        
        # 5. Invalid JSON-RPC method
        print("\n❌ Invalid Method")
        await self.call_method("invalid_method", {})
    
    async def demo_batch_operations(self):
        """Demonstrate batch operations"""
        print("\n📦 Batch Operations Demonstration")
        print("=" * 60)
        
        device_id = "mug_001"
        
        # Simulate a complete morning usage workflow
        operations = [
            ("heat", {"temperature": 70}, "Preheat to 70 degrees"),
            ("display", {"text": "Good Morning!", "duration": 10}, "Display morning greeting"),
            ("color", {"color": "#FFD700", "mode": "solid"}, "Set gold color theme"),
            ("brew", {"type": "espresso", "strength": "strong"}, "Make espresso"),
            ("display", {"text": "Enjoy your coffee!", "duration": 15}, "Display enjoy message")
        ]
        
        print("🌅 Morning Usage Workflow:")
        for i, (action, params, description) in enumerate(operations, 1):
            print(f"\nStep {i}: {description}")
            await self.call_method("publish_action", {
                "device_id": device_id,
                "action": action,
                "params": params
            })
            
            # Simulate operation interval
            await asyncio.sleep(0.5)
    
    async def run_all_demos(self):
        """Run all demonstrations"""
        print("🎯 PixelMug MCP Client Demonstration Program")
        print("=" * 80)
        
        demos = [
            self.demo_help,
            self.demo_prepare_connection,
            self.demo_device_operations,
            self.demo_batch_operations,
            self.demo_error_handling
        ]
        
        for demo in demos:
            try:
                await demo()
                await asyncio.sleep(1)  # Demo interval
            except KeyboardInterrupt:
                print("\n\n⏸️ Demo interrupted by user")
                break
            except Exception as e:
                print(f"\n💥 Error occurred during demo: {str(e)}")
        
        print("\n🎉 Demo completed!")
        print("=" * 80)


async def interactive_mode():
    """Interactive mode"""
    client = PixelMugClient()
    
    print("🎮 PixelMug MCP Interactive Client")
    print("=" * 50)
    print("Available commands:")
    print("  help - Get help information")
    print("  prepare <device_id> - Prepare connection")
    print("  heat <device_id> <temperature> - Heat mug")
    print("  display <device_id> <text> [duration] - Display information")
    print("  color <device_id> <color> [mode] - Change color")
    print("  brew <device_id> <type> [strength] - Brew coffee")
    print("  demo - Run complete demonstration")
    print("  exit - Exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n🔧 Enter command: ").strip()
            
            if not command:
                continue
                
            if command == "exit":
                print("👋 Goodbye!")
                break
            elif command == "demo":
                await client.run_all_demos()
            elif command == "help":
                await client.demo_help()
            elif command.startswith("prepare "):
                parts = command.split()
                if len(parts) >= 2:
                    device_id = parts[1]
                    await client.call_method("prepare_mqtt_connection", {"device_id": device_id})
                else:
                    print("❌ Usage: prepare <device_id>")
            elif command.startswith("heat "):
                parts = command.split()
                if len(parts) >= 3:
                    device_id = parts[1]
                    temperature = int(parts[2])
                    await client.call_method("publish_action", {
                        "device_id": device_id,
                        "action": "heat",
                        "params": {"temperature": temperature}
                    })
                else:
                    print("❌ Usage: heat <device_id> <temperature>")
            elif command.startswith("display "):
                parts = command.split(maxsplit=3)
                if len(parts) >= 3:
                    device_id = parts[1]
                    text = parts[2]
                    duration = int(parts[3]) if len(parts) > 3 else 10
                    await client.call_method("publish_action", {
                        "device_id": device_id,
                        "action": "display",
                        "params": {"text": text, "duration": duration}
                    })
                else:
                    print("❌ Usage: display <device_id> <text> [duration]")
            elif command.startswith("color "):
                parts = command.split()
                if len(parts) >= 3:
                    device_id = parts[1]
                    color = parts[2]
                    mode = parts[3] if len(parts) > 3 else "solid"
                    await client.call_method("publish_action", {
                        "device_id": device_id,
                        "action": "color",
                        "params": {"color": color, "mode": mode}
                    })
                else:
                    print("❌ Usage: color <device_id> <color> [mode]")
            elif command.startswith("brew "):
                parts = command.split()
                if len(parts) >= 3:
                    device_id = parts[1]
                    brew_type = parts[2]
                    strength = parts[3] if len(parts) > 3 else "medium"
                    await client.call_method("publish_action", {
                        "device_id": device_id,
                        "action": "brew",
                        "params": {"type": brew_type, "strength": strength}
                    })
                else:
                    print("❌ Usage: brew <device_id> <type> [strength]")
            else:
                print("❌ Unknown command, type available commands to see help")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except ValueError as e:
            print(f"❌ Parameter error: {str(e)}")
        except Exception as e:
            print(f"💥 Error occurred: {str(e)}")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            # Run demonstration
            client = PixelMugClient()
            await client.run_all_demos()
        elif sys.argv[1] == "interactive":
            # Interactive mode
            await interactive_mode()
        else:
            print("Usage: python example_client.py [demo|interactive]")
    else:
        # Default run demonstration
        client = PixelMugClient()
        await client.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
