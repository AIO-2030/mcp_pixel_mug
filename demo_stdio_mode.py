#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stdio模式演示脚本
展示如何使用子账号密钥调用IoT云服务
"""

import json
import os
from mug_service import mug_service

def demo_stdio_mode():
    """演示stdio模式的使用"""
    print("🚀 stdio模式演示")
    print("="*50)
    
    # 配置参数
    product_id = "H3PI4FBTV5"
    device_name = "mug_001"
    
    print(f"产品ID: {product_id}")
    print(f"设备名: {device_name}")
    print()
    
    # 1. 获取服务信息
    print("1️⃣ 获取服务信息...")
    help_info = mug_service.get_help()
    print(f"   服务名称: {help_info.get('service', 'unknown')}")
    print(f"   版本: {help_info.get('version', 'unknown')}")
    print(f"   描述: {help_info.get('description', 'unknown')}")
    print()
    
    # 2. 查询设备状态
    print("2️⃣ 查询设备状态...")
    try:
        status = mug_service.get_device_status(product_id, device_name)
        print(f"   状态: {status.get('status', 'unknown')}")
        print(f"   在线状态: {status.get('device_status', {}).get('online', 'unknown')}")
        print(f"   最后在线时间: {status.get('device_status', {}).get('last_online_time', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 查询失败: {str(e)}")
    print()
    
    # 3. 发送文本消息
    print("3️⃣ 发送文本消息...")
    try:
        text_result = mug_service.send_display_text(product_id, device_name, "stdio模式测试")
        print(f"   发送状态: {text_result.get('status', 'unknown')}")
        print(f"   凭证类型: {text_result.get('credential_type', 'unknown')}")
        print(f"   发送的文本: {text_result.get('text_info', {}).get('text', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 发送失败: {str(e)}")
    print()
    
    # 4. 发送像素图像
    print("4️⃣ 发送像素图像...")
    try:
        # 创建一个简单的笑脸图案
        smiley_pattern = [
            ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
            ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
            ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"],
            ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
            ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"],
            ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"],
            ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
            ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]
        ]
        
        pixel_result = mug_service.send_pixel_image(
            product_id, 
            device_name, 
            smiley_pattern,
            target_width=8,
            target_height=8,
            use_cos=True  # 直接传输，不使用COS
        )
        print(f"   发送状态: {pixel_result.get('status', 'unknown')}")
        print(f"   传输方式: {pixel_result.get('delivery_method', 'unknown')}")
        print(f"   图像尺寸: {pixel_result.get('image_info', {}).get('width', 0)}x{pixel_result.get('image_info', {}).get('height', 0)}")
    except Exception as e:
        print(f"   ❌ 发送失败: {str(e)}")
    print()
    
    # 5. 发送GIF动画
    print("5️⃣ 发送GIF动画...")
    try:
        # 创建一个简单的闪烁动画
        frames = [
            {
                "frame_index": 0,
                "pixel_matrix": [
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000"]
                ],
                "duration": 500
            },
            {
                "frame_index": 1,
                "pixel_matrix": [
                    ["#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#000000"]
                ],
                "duration": 500
            }
        ]
        
        gif_result = mug_service.send_gif_animation(
            product_id,
            device_name,
            frames,
            frame_delay=500,
            loop_count=1,
            target_width=4,
            target_height=4,
            use_cos=True 
        )
        print(f"   发送状态: {gif_result.get('status', 'unknown')}")
        print(f"   传输方式: {gif_result.get('delivery_method', 'unknown')}")
        print(f"   动画信息: {gif_result.get('animation_info', {})}")
    except Exception as e:
        print(f"   ❌ 发送失败: {str(e)}")
    print()
    
    print("✅ stdio模式演示完成！")
    print("💡 所有操作都使用子账号密钥，无需STS临时凭证")

def main():
    """主函数"""
    # 检查环境变量
    if not os.getenv("TC_SECRET_ID") or not os.getenv("TC_SECRET_KEY"):
        print("❌ 请设置环境变量:")
        print("   export TC_SECRET_ID=your_secret_id")
        print("   export TC_SECRET_KEY=your_secret_key")
        return False
    
    demo_stdio_mode()
    return True

if __name__ == "__main__":
    main()
