#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP PixelMug Server Implementation
Provides MCP interface compliant with AIO JSON-RPC standard
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from mug_service import mug_service


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
            elif method == 'prepare_mqtt_connection':
                result = await self._handle_prepare_mqtt_connection(params)
            elif method == 'publish_action':
                result = await self._handle_publish_action(params)
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
    
    async def _handle_prepare_mqtt_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prepare_mqtt_connection request"""
        device_id = params.get('device_id')
        if not device_id:
            raise ValueError("Missing required parameter: device_id")
        
        return mug_service.prepare_mqtt_connection(device_id)
    
    async def _handle_publish_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle publish_action request"""
        device_id = params.get('device_id')
        action = params.get('action')
        action_params = params.get('params', {})
        
        if not device_id:
            raise ValueError("Missing required parameter: device_id")
        if not action:
            raise ValueError("Missing required parameter: action")
        
        # Validate parameters
        mug_service.validate_device_params(action, action_params)
        
        return await mug_service.publish_action(device_id, action, action_params)
    
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


async def run_server():
    """Run MCP server"""
    server = MCPServer()
    
    print("MCP PixelMug server started, waiting for requests...")
    print("Supported methods: help, prepare_mqtt_connection, publish_action")
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
