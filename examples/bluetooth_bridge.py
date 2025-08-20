#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug 蓝牙桥接示例
演示如何通过蓝牙发现设备，然后使用 MCP 进行控制
"""

import asyncio
import json
import sys
import os
import time
from typing import Dict, List, Optional

# 添加父目录到路径，以便导入服务模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer

# 模拟蓝牙模块（在实际应用中应该使用真实的蓝牙库如 pybluez）
class MockBluetooth:
    """模拟蓝牙功能类"""
    
    @staticmethod
    def discover_devices(lookup_names=True, duration=8):
        """模拟蓝牙设备发现"""
        print(f"🔍 开始蓝牙设备扫描（{duration}秒）...")
        time.sleep(2)  # 模拟扫描时间
        
        # 模拟发现的设备
        mock_devices = [
            ("AA:BB:CC:DD:EE:01", "PixelMug-001"),
            ("AA:BB:CC:DD:EE:02", "PixelMug-002"), 
            ("FF:EE:DD:CC:BB:AA", "iPhone"),
            ("11:22:33:44:55:66", "PixelMug-Pro-003"),
        ]
        
        if lookup_names:
            return mock_devices
        else:
            return [addr for addr, _ in mock_devices]
    
    @staticmethod
    def lookup_name(address, timeout=10):
        """模拟查找设备名称"""
        device_names = {
            "AA:BB:CC:DD:EE:01": "PixelMug-001",
            "AA:BB:CC:DD:EE:02": "PixelMug-002",
            "11:22:33:44:55:66": "PixelMug-Pro-003",
        }
        return device_names.get(address, "Unknown Device")


class BluetoothPixelMugBridge:
    """蓝牙 PixelMug 桥接器"""
    
    def __init__(self):
        self.mcp_server = MCPServer()
        self.discovered_mugs: Dict[str, Dict] = {}
        self.request_id = 1
    
    def get_next_id(self):
        """获取下一个请求ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    def extract_device_id(self, bluetooth_addr: str, device_name: str) -> str:
        """从蓝牙地址和设备名提取设备ID"""
        # 尝试从设备名中提取ID
        if "PixelMug-" in device_name:
            name_parts = device_name.split("-")
            if len(name_parts) >= 2:
                return f"mug_{name_parts[-1].lower()}"
        
        # 如果无法从名称提取，使用蓝牙地址
        addr_suffix = bluetooth_addr.replace(":", "")[-6:].lower()
        return f"mug_{addr_suffix}"
    
    async def discover_pixelmug_devices(self) -> List[Dict]:
        """发现 PixelMug 设备"""
        print("🔍 开始扫描 PixelMug 设备...")
        
        try:
            # 使用模拟蓝牙（在实际应用中替换为真实蓝牙库）
            devices = MockBluetooth.discover_devices(lookup_names=True, duration=5)
            
            pixelmug_devices = []
            
            for addr, name in devices:
                if "PixelMug" in name:
                    device_id = self.extract_device_id(addr, name)
                    
                    device_info = {
                        "bluetooth_addr": addr,
                        "device_name": name,
                        "device_id": device_id,
                        "discovered_at": time.time()
                    }
                    
                    pixelmug_devices.append(device_info)
                    self.discovered_mugs[device_id] = device_info
                    
                    print(f"   ✅ 发现设备: {name} ({addr}) -> {device_id}")
            
            if not pixelmug_devices:
                print("   ❌ 未发现 PixelMug 设备")
            else:
                print(f"   🎉 共发现 {len(pixelmug_devices)} 台 PixelMug 设备")
            
            return pixelmug_devices
            
        except Exception as e:
            print(f"   💥 蓝牙扫描失败: {str(e)}")
            return []
    
    async def call_mcp_method(self, method: str, params: dict = None) -> Optional[dict]:
        """调用 MCP 方法"""
        if params is None:
            params = {}
            
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.get_next_id()
        }
        
        try:
            response_str = await self.mcp_server.handle_request(json.dumps(request))
            response = json.loads(response_str)
            
            if "error" in response:
                print(f"   ❌ MCP 错误: {response['error']['message']}")
                return None
            else:
                return response.get("result")
                
        except Exception as e:
            print(f"   💥 MCP 调用异常: {str(e)}")
            return None
    
    async def prepare_device_connection(self, device_id: str) -> bool:
        """为设备准备 MQTT 连接"""
        print(f"🔌 为设备 {device_id} 准备连接...")
        
        result = await self.call_mcp_method("prepare_mqtt_connection", {"device_id": device_id})
        
        if result:
            print(f"   ✅ 连接准备成功")
            print(f"   📡 MQTT 主机: {result.get('host')}")
            print(f"   📺 命令主题: {result.get('topic')}")
            return True
        else:
            print(f"   ❌ 连接准备失败")
            return False
    
    async def send_device_command(self, device_id: str, action: str, params: dict) -> bool:
        """向设备发送命令"""
        print(f"📤 向设备 {device_id} 发送 {action} 命令...")
        
        result = await self.call_mcp_method("publish_action", {
            "device_id": device_id,
            "action": action,
            "params": params
        })
        
        if result:
            print(f"   ✅ 命令发送成功")
            print(f"   🕐 时间戳: {result.get('timestamp')}")
            print(f"   🔖 请求ID: {result.get('request_id')}")
            return True
        else:
            print(f"   ❌ 命令发送失败")
            return False
    
    async def demo_device_control_flow(self, device_id: str):
        """演示完整的设备控制流程"""
        print(f"\n🎮 设备 {device_id} 控制流程演示")
        print("=" * 60)
        
        # 1. 准备连接
        if not await self.prepare_device_connection(device_id):
            return
        
        await asyncio.sleep(1)
        
        # 2. 设备初始化序列
        print(f"\n🚀 设备初始化...")
        initialization_steps = [
            ("display", {"text": "Connecting...", "duration": 5}, "显示连接状态"),
            ("color", {"color": "#00FF00", "mode": "blink"}, "绿色闪烁表示连接成功"),
            ("display", {"text": "Ready!", "duration": 3}, "显示就绪状态"),
        ]
        
        for action, params, description in initialization_steps:
            print(f"   📋 {description}")
            await self.send_device_command(device_id, action, params)
            await asyncio.sleep(1)
        
        # 3. 模拟用户使用场景
        print(f"\n☕ 模拟冲泡咖啡场景...")
        coffee_workflow = [
            ("heat", {"temperature": 85}, "预热到最佳冲泡温度"),
            ("display", {"text": "Heating...", "duration": 10}, "显示加热状态"),
            ("color", {"color": "#FF4500", "mode": "solid"}, "橙色表示加热中"),
            ("brew", {"type": "americano", "strength": "medium"}, "开始冲泡美式咖啡"),
            ("display", {"text": "Brewing...", "duration": 15}, "显示冲泡状态"),
            ("color", {"color": "#8B4513", "mode": "solid"}, "棕色表示咖啡颜色"),
            ("display", {"text": "Enjoy!", "duration": 20}, "完成提示"),
            ("color", {"color": "#FFD700", "mode": "solid"}, "金色表示完成"),
        ]
        
        for action, params, description in coffee_workflow:
            print(f"   ☕ {description}")
            await self.send_device_command(device_id, action, params)
            await asyncio.sleep(1.5)
        
        print(f"   🎉 咖啡制作完成!")
    
    async def batch_device_control(self):
        """批量设备控制演示"""
        if not self.discovered_mugs:
            print("❌ 没有发现的设备可供控制")
            return
        
        print(f"\n📦 批量设备控制演示")
        print("=" * 60)
        
        # 为所有设备设置同步显示
        sync_message = f"Sync at {time.strftime('%H:%M:%S')}"
        
        tasks = []
        for device_id in self.discovered_mugs.keys():
            task = self.send_device_command(device_id, "display", {
                "text": sync_message,
                "duration": 10
            })
            tasks.append(task)
        
        print(f"📡 向 {len(tasks)} 台设备同时发送同步消息...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        print(f"   ✅ {success_count}/{len(tasks)} 台设备响应成功")
    
    async def run_bridge_demo(self):
        """运行完整的桥接演示"""
        print("🌉 PixelMug 蓝牙桥接演示")
        print("=" * 80)
        
        try:
            # 1. 发现设备
            devices = await self.discover_pixelmug_devices()
            
            if not devices:
                print("❌ 未发现设备，演示结束")
                return
            
            await asyncio.sleep(2)
            
            # 2. 单设备控制演示
            first_device_id = devices[0]["device_id"]
            await self.demo_device_control_flow(first_device_id)
            
            await asyncio.sleep(2)
            
            # 3. 批量控制演示（如果有多个设备）
            if len(devices) > 1:
                await self.batch_device_control()
            
            # 4. 设备状态查询演示
            print(f"\n📊 设备状态查询")
            print("=" * 60)
            
            for device_id, device_info in self.discovered_mugs.items():
                print(f"设备: {device_id}")
                print(f"   蓝牙地址: {device_info['bluetooth_addr']}")
                print(f"   设备名称: {device_info['device_name']}")
                print(f"   发现时间: {time.ctime(device_info['discovered_at'])}")
                
                # 获取连接信息
                conn_info = await self.call_mcp_method("prepare_mqtt_connection", {"device_id": device_id})
                if conn_info:
                    print(f"   MQTT 主题: {conn_info.get('topic')}")
                print()
            
            print("🎉 桥接演示完成!")
            
        except KeyboardInterrupt:
            print("\n⏸️ 演示被用户中断")
        except Exception as e:
            print(f"💥 演示过程中发生错误: {str(e)}")


async def interactive_bridge_mode():
    """交互式桥接模式"""
    bridge = BluetoothPixelMugBridge()
    
    print("🌉 PixelMug 蓝牙桥接交互模式")
    print("=" * 50)
    print("可用命令:")
    print("  scan - 扫描 PixelMug 设备")
    print("  list - 列出已发现的设备")
    print("  connect <device_id> - 准备设备连接")
    print("  send <device_id> <action> [params] - 发送命令")
    print("  demo [device_id] - 运行控制演示")
    print("  batch - 批量设备控制")
    print("  exit - 退出")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n🔧 请输入命令: ").strip()
            
            if not command:
                continue
                
            if command == "exit":
                print("👋 再见!")
                break
            elif command == "scan":
                await bridge.discover_pixelmug_devices()
            elif command == "list":
                if bridge.discovered_mugs:
                    print("📱 已发现的设备:")
                    for device_id, info in bridge.discovered_mugs.items():
                        print(f"   • {device_id}: {info['device_name']} ({info['bluetooth_addr']})")
                else:
                    print("❌ 没有发现的设备，请先运行 scan 命令")
            elif command.startswith("connect "):
                parts = command.split()
                if len(parts) >= 2:
                    device_id = parts[1]
                    await bridge.prepare_device_connection(device_id)
                else:
                    print("❌ 用法: connect <device_id>")
            elif command.startswith("demo"):
                parts = command.split()
                if len(parts) >= 2:
                    device_id = parts[1]
                    await bridge.demo_device_control_flow(device_id)
                elif bridge.discovered_mugs:
                    device_id = list(bridge.discovered_mugs.keys())[0]
                    await bridge.demo_device_control_flow(device_id)
                else:
                    print("❌ 没有可用设备，请先运行 scan 命令")
            elif command == "batch":
                await bridge.batch_device_control()
            elif command.startswith("send "):
                parts = command.split()
                if len(parts) >= 3:
                    device_id = parts[1]
                    action = parts[2]
                    # 简化参数处理
                    if action == "heat" and len(parts) >= 4:
                        params = {"temperature": int(parts[3])}
                    elif action == "display" and len(parts) >= 4:
                        text = " ".join(parts[3:])
                        params = {"text": text, "duration": 10}
                    elif action == "color" and len(parts) >= 4:
                        params = {"color": parts[3], "mode": "solid"}
                    elif action == "brew" and len(parts) >= 4:
                        params = {"type": parts[3], "strength": "medium"}
                    else:
                        params = {}
                    
                    await bridge.send_device_command(device_id, action, params)
                else:
                    print("❌ 用法: send <device_id> <action> [params]")
            else:
                print("❌ 未知命令，输入可用命令查看帮助")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except ValueError as e:
            print(f"❌ 参数错误: {str(e)}")
        except Exception as e:
            print(f"💥 发生错误: {str(e)}")


async def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            # 运行演示
            bridge = BluetoothPixelMugBridge()
            await bridge.run_bridge_demo()
        elif sys.argv[1] == "interactive":
            # 交互式模式
            await interactive_bridge_mode()
        else:
            print("用法: python bluetooth_bridge.py [demo|interactive]")
    else:
        # 默认运行演示
        bridge = BluetoothPixelMugBridge()
        await bridge.run_bridge_demo()


if __name__ == "__main__":
    asyncio.run(main())
