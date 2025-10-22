#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试stdio模式下的IoT云设备交互方法
验证所有方法都默认使用子账号密钥调用
"""

import json
import asyncio
import logging
import sys
import os
from mug_service import mug_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StdioModeTester:
    """stdio模式测试类"""
    
    def __init__(self):
        self.test_product_id = os.getenv("TEST_PRODUCT_ID", "H3PI4FBTV5")
        self.test_device_name = os.getenv("TEST_DEVICE_NAME", "3CDC7580F950")
        
    def test_help(self):
        """测试help方法"""
        logger.info("=== 测试 help 方法 ===")
        try:
            result = mug_service.get_help()
            logger.info(f"help方法调用成功: {result.get('service', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"help方法调用失败: {str(e)}")
            return False
    
    def test_get_device_status(self):
        """测试get_device_status方法"""
        logger.info("=== 测试 get_device_status 方法 ===")
        try:
            result = mug_service.get_device_status(
                self.test_product_id, 
                self.test_device_name,
                use_direct_credentials=True  # 显式使用子账号密钥
            )
            logger.info(f"设备状态查询成功: {result.get('status', 'unknown')}")
            logger.info(f"设备在线状态: {result.get('device_status', {}).get('online', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"设备状态查询失败: {str(e)}")
            return False
    
    def test_send_display_text(self):
        """测试send_display_text方法"""
        logger.info("=== 测试 send_display_text 方法 ===")
        try:
            test_text = "stdio模式测试"
            result = mug_service.send_display_text(
                self.test_product_id,
                self.test_device_name,
                test_text,
                use_direct_credentials=True  # 显式使用子账号密钥
            )
            logger.info(f"文本发送成功: {result.get('status', 'unknown')}")
            logger.info(f"发送的文本: {result.get('text_info', {}).get('text', 'unknown')}")
            logger.info(f"凭证类型: {result.get('credential_type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"文本发送失败: {str(e)}")
            return False
    
    def test_send_pixel_image(self):
        """测试send_pixel_image方法"""
        logger.info("=== 测试 send_pixel_image 方法 ===")
        try:
            # 创建一个简单的像素图案
            pixel_pattern = [
                ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"],
                ["#00FF00", "#0000FF", "#FFFF00", "#FF0000"],
                ["#0000FF", "#FFFF00", "#FF0000", "#00FF00"],
                ["#FFFF00", "#FF0000", "#00FF00", "#0000FF"]
            ]
            
            result = mug_service.send_pixel_image(
                self.test_product_id,
                self.test_device_name,
                pixel_pattern,
                target_width=4,
                target_height=4,
                use_cos=True,  # 禁用COS上传，直接传输
                use_direct_credentials=True  # 显式使用子账号密钥
            )
            logger.info(f"像素图像发送成功: {result.get('status', 'unknown')}")
            logger.info(f"图像信息: {result.get('image_info', {})}")
            logger.info(f"传输方式: {result.get('delivery_method', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"像素图像发送失败: {str(e)}")
            return False
    
    def test_send_gif_animation(self):
        """测试send_gif_animation方法"""
        logger.info("=== 测试 send_gif_animation 方法 ===")
        try:
            # 创建一个简单的GIF动画帧
            frames = [
                {
                    "frame_index": 0,
                    "pixel_matrix": [
                        ["#FF0000", "#000000", "#000000", "#000000"],
                        ["#000000", "#FF0000", "#000000", "#000000"],
                        ["#000000", "#000000", "#FF0000", "#000000"],
                        ["#000000", "#000000", "#000000", "#FF0000"]
                    ],
                    "duration": 200
                },
                {
                    "frame_index": 1,
                    "pixel_matrix": [
                        ["#000000", "#FF0000", "#000000", "#000000"],
                        ["#000000", "#000000", "#FF0000", "#000000"],
                        ["#000000", "#000000", "#000000", "#FF0000"],
                        ["#FF0000", "#000000", "#000000", "#000000"]
                    ],
                    "duration": 200
                }
            ]
            
            result = mug_service.send_gif_animation(
                self.test_product_id,
                self.test_device_name,
                frames,
                frame_delay=200,
                loop_count=1,
                target_width=4,
                target_height=4,
                use_cos=True,  # 禁用COS上传，直接传输
                use_direct_credentials=True  # 显式使用子账号密钥
            )
            logger.info(f"GIF动画发送成功: {result.get('status', 'unknown')}")
            logger.info(f"动画信息: {result.get('animation_info', {})}")
            logger.info(f"传输方式: {result.get('delivery_method', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"GIF动画发送失败: {str(e)}")
            return False
    
    def test_convert_image_to_pixels(self):
        """测试convert_image_to_pixels方法"""
        logger.info("=== 测试 convert_image_to_pixels 方法 ===")
        try:
            # 创建一个简单的base64图像数据（1x1像素的红色PNG）
            # 这是一个1x1像素的红色PNG图像的base64编码
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            
            result = mug_service.convert_image_to_pixels(
                test_image_base64,
                target_width=2,
                target_height=2,
                resize_method="nearest"
            )
            logger.info(f"图像转换成功: {result.get('width', 0)}x{result.get('height', 0)}")
            logger.info(f"像素矩阵: {result.get('pixel_matrix', [])}")
            logger.info(f"转换方法: {result.get('resize_method', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"图像转换失败: {str(e)}")
            return False
    
    def test_default_credentials_usage(self):
        """测试默认使用子账号密钥的行为"""
        logger.info("=== 测试默认子账号密钥使用 ===")
        try:
            # 不显式指定use_direct_credentials参数，应该默认使用子账号密钥
            result = mug_service.send_display_text(
                self.test_product_id,
                self.test_device_name,
                "默认子账号测试"
            )
            logger.info(f"默认凭证测试成功: {result.get('status', 'unknown')}")
            logger.info(f"凭证类型: {result.get('credential_type', 'unknown')}")
            
            # 验证是否使用了子账号密钥
            if result.get('credential_type') == 'direct_subaccount':
                logger.info("✓ 确认使用了子账号密钥")
                return True
            else:
                logger.warning(f"⚠ 凭证类型不是预期的子账号密钥: {result.get('credential_type')}")
                return False
        except Exception as e:
            logger.error(f"默认凭证测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始stdio模式测试...")
        logger.info(f"测试产品ID: {self.test_product_id}")
        logger.info(f"测试设备名: {self.test_device_name}")
        
        tests = [
            ("help方法", self.test_help),
            ("get_device_status方法", self.test_get_device_status),
            ("send_display_text方法", self.test_send_display_text),
            ("send_pixel_image方法", self.test_send_pixel_image),
            ("send_gif_animation方法", self.test_send_gif_animation),
            ("convert_image_to_pixels方法", self.test_convert_image_to_pixels),
            ("默认子账号密钥使用", self.test_default_credentials_usage),
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"开始测试: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                success = test_func()
                results.append((test_name, success))
                if success:
                    logger.info(f"✓ {test_name} 测试通过")
                else:
                    logger.error(f"✗ {test_name} 测试失败")
            except Exception as e:
                logger.error(f"✗ {test_name} 测试异常: {str(e)}")
                results.append((test_name, False))
        
        # 输出测试结果汇总
        logger.info(f"\n{'='*50}")
        logger.info("测试结果汇总")
        logger.info(f"{'='*50}")
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✓ 通过" if success else "✗ 失败"
            logger.info(f"{test_name}: {status}")
            if success:
                passed += 1
        
        logger.info(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            logger.info("🎉 所有测试都通过了！stdio模式配置正确。")
            return True
        else:
            logger.error(f"❌ 有 {total - passed} 个测试失败，请检查配置。")
            return False

def main():
    """主函数"""
    print("stdio模式IoT云设备交互测试")
    print("="*50)
    
    # 检查环境变量
    required_env_vars = ["TC_SECRET_ID", "TC_SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请设置以下环境变量:")
        for var in missing_vars:
            print(f"  export {var}=your_value")
        return False
    
    print("✓ 环境变量检查通过")
    
    # 运行测试
    tester = StdioModeTester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
