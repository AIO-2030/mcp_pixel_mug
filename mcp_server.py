#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP PixelMug Server Implementation
Provides MCP interface for PixelMug IoT device control
"""

import json
import asyncio
import logging
import time
import os
from typing import Dict, Any, Optional
from mug_service import mug_service

# 腾讯云IoT Explorer相关依赖
try:
    from tencentcloud.iotexplorer.v20190423 import iotexplorer_client, models
    from tencentcloud.common import credential
    IOT_EXPLORER_AVAILABLE = True
except ImportError:
    IOT_EXPLORER_AVAILABLE = False


class MCPServer:
    """MCP Server class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def handle_request(self, request_data: str) -> str:
        """Handle JSON-RPC requests"""
        try:
            request = json.loads(request_data)
            self.logger.info(f"Received request: {request}")
            
            # Validate JSON-RPC format
            if not self._validate_jsonrpc_request(request):
                return self._create_error_response(
                    request.get('id'),
                    -32600,
                    "Invalid Request"
                )
            
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')
            
            # Route to corresponding handler method
            if method == 'help':
                result = await self._handle_help(params)
            elif method == 'issue_sts':
                result = await self._handle_issue_sts(params)
            elif method == 'send_pixel_image':
                result = await self._handle_send_pixel_image(params)
            elif method == 'send_gif_animation':
                result = await self._handle_send_gif_animation(params)
            elif method == 'convert_image_to_pixels':
                result = await self._handle_convert_image_to_pixels(params)
            elif method == 'get_device_status':
                result = await self._handle_get_device_status(params)
            else:
                return self._create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
            
            return self._create_success_response(request_id, result)
            
        except json.JSONDecodeError:
            return self._create_error_response(
                None,
                -32700,
                "Parse error"
            )
        except Exception as e:
            self.logger.error(f"Error occurred while handling request: {str(e)}")
            return self._create_error_response(
                request.get('id') if 'request' in locals() else None,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    def _validate_jsonrpc_request(self, request: Dict[str, Any]) -> bool:
        """Validate JSON-RPC request format"""
        return (
            isinstance(request, dict) and
            request.get('jsonrpc') == '2.0' and
            'method' in request and
            isinstance(request['method'], str)
        )
    
    async def _handle_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle help request"""
        return mug_service.get_help()
    
    async def _handle_issue_sts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle issue_sts request"""
        product_id = params.get('product_id')
        device_name = params.get('device_name')
        
        if not product_id:
            raise ValueError("Missing required parameter: product_id")
        if not device_name:
            raise ValueError("Missing required parameter: device_name")
        
        return mug_service.issue_sts(product_id, device_name)
    
    async def _handle_send_pixel_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_pixel_image request"""
        product_id = params.get('product_id')
        device_name = params.get('device_name')
        image_data = params.get('image_data')
        target_width = params.get('target_width', 16)
        target_height = params.get('target_height', 16)
        
        if not product_id:
            raise ValueError("Missing required parameter: product_id")
        if not device_name:
            raise ValueError("Missing required parameter: device_name")
        if not image_data:
            raise ValueError("Missing required parameter: image_data")
        
        return mug_service.send_pixel_image(product_id, device_name, image_data, target_width, target_height)
    
    async def _handle_send_gif_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_gif_animation request"""
        product_id = params.get('product_id')
        device_name = params.get('device_name')
        gif_data = params.get('gif_data')
        frame_delay = params.get('frame_delay', 100)
        loop_count = params.get('loop_count', 0)
        target_width = params.get('target_width', 16)
        target_height = params.get('target_height', 16)
        
        if not product_id:
            raise ValueError("Missing required parameter: product_id")
        if not device_name:
            raise ValueError("Missing required parameter: device_name")
        if not gif_data:
            raise ValueError("Missing required parameter: gif_data")
        
        return mug_service.send_gif_animation(product_id, device_name, gif_data, frame_delay, loop_count, target_width, target_height)
    
    async def _handle_convert_image_to_pixels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle convert_image_to_pixels request"""
        image_data = params.get('image_data')
        if not image_data:
            raise ValueError("Missing required parameter: image_data")
        
        target_width = params.get('target_width', 16)
        target_height = params.get('target_height', 16)
        resize_method = params.get('resize_method', 'nearest')
        
        return mug_service.convert_image_to_pixels(image_data, target_width, target_height, resize_method)
    
    async def _handle_get_device_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_device_status request"""
        product_id = params.get("product_id")
        device_name = params.get("device_name")
        
        if not product_id or not device_name:
            return {
                "status": "error",
                "error": "Missing required parameters: product_id and device_name",
                "timestamp": int(time.time()),
                "request_id": f"status_{int(time.time())}"
            }
        
        # 调用腾讯云 IoT Explorer API 查询设备状态
        device_status = await query_device_status_from_tencent_iot(product_id, device_name)
        
        return {
            "status": "success",
            "device_info": {
                "product_id": product_id,
                "device_name": device_name,
                "is_online": device_status.get("is_online", False),
                "last_seen": device_status.get("last_seen", 0),
                "connection_status": device_status.get("connection_status", "disconnected"),
                "ip_address": device_status.get("ip_address"),
                "signal_strength": device_status.get("signal_strength"),
                "battery_level": device_status.get("battery_level")
            },
            "timestamp": int(time.time()),
            "request_id": f"status_{int(time.time())}"
        }
    
    def _create_success_response(self, request_id: Any, result: Any) -> str:
        """Create success response"""
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
        return json.dumps(response, ensure_ascii=False, indent=2)
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> str:
        """Create error response"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
        return json.dumps(response, ensure_ascii=False, indent=2)


async def query_device_status_from_tencent_iot(product_id: str, device_name: str) -> dict:
    """
    Query device status from Tencent Cloud IoT Explorer
    
    Args:
        product_id: Product ID
        device_name: Device name
        
    Returns:
        dict: Device status information
    """
    try:
        if not IOT_EXPLORER_AVAILABLE:
            raise Exception("Tencent Cloud IoT Explorer SDK not available")
        
        # 获取 STS 临时凭证
        sts_result = mug_service.issue_sts(product_id, device_name)
        
        # 创建临时凭证对象
        sts_credentials = credential.Credential(
            sts_result["tmpSecretId"],
            sts_result["tmpSecretKey"],
            sts_result["token"]
        )
        
        # 创建 IoT Explorer 客户端
        iot_client = iotexplorer_client.IotExplorerClient(
            credential=sts_credentials,
            region=os.getenv("DEFAULT_REGION", "ap-guangzhou")
        )
        
        # 调用 DescribeDevice 接口查询设备信息
        req = models.DescribeDeviceRequest()
        req.ProductId = product_id
        req.DeviceName = device_name
        
        resp = iot_client.DescribeDevice(req)
        
        # 解析响应并返回设备状态
        return {
            "is_online": resp.DeviceInfo.OnlineStatus == 1,  # 1表示在线，0表示离线
            "last_seen": int(resp.DeviceInfo.LastOnlineTime) if resp.DeviceInfo.LastOnlineTime else 0,
            "connection_status": "connected" if resp.DeviceInfo.OnlineStatus == 1 else "disconnected",
            "ip_address": getattr(resp.DeviceInfo, 'IpAddress', None),
            "signal_strength": getattr(resp.DeviceInfo, 'SignalStrength', None),
            "battery_level": getattr(resp.DeviceInfo, 'BatteryLevel', None)
        }
        
    except Exception as e:
        logging.error(f"Failed to query device status from Tencent IoT: {e}")
        # 返回默认状态
        return {
            "is_online": False,
            "last_seen": 0,
            "connection_status": "disconnected",
            "ip_address": None,
            "signal_strength": None,
            "battery_level": None
        }


async def run_server():
    """Run MCP server"""
    server = MCPServer()
    
    print("MCP PixelMug server started, waiting for requests...")
    print("Supported methods: help, issue_sts, send_pixel_image, send_gif_animation, convert_image_to_pixels, get_device_status")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            # In actual applications, this would read requests from network or other input sources
            # Here we provide a simple command-line interaction example
            try:
                request_input = input("\nPlease enter JSON-RPC request (or 'exit' to quit): \n")
                if request_input.strip().lower() == 'exit':
                    break
                
                if request_input.strip():
                    response = await server.handle_request(request_input)
                    print(f"\nResponse:\n{response}")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
                
    except KeyboardInterrupt:
        pass
    
    print("\nServer stopped")


if __name__ == "__main__":
    asyncio.run(run_server())
