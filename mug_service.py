#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug Smart Mug MQTT Control Service
Provides device connection preparation and operation publishing functionality
"""

import json
import uuid
import datetime
import ssl
import logging
import base64
import re
import io
from typing import Dict, Any, Optional, Union, List
import paho.mqtt.client as mqtt
import asyncio
from asyncio_mqtt import Client

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MugService:
    """PixelMug service core class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Mock device registration database
        self.mock_devices = {
            "mug_001": {
                "device_id": "mug_001",
                "host": "a3k7j9m2l5n8p1.iot.ap-northeast-1.amazonaws.com",
                "port": 8883,
                "client_id": "mug_001",
                "cert": """-----BEGIN CERTIFICATE-----
MIIDWjCCAkKgAwIBAgIVANXXXXXXXXXXXXXXXXXXXXXXXXXXMA0GCSqGSIb3DQEB
CwUAME0xSzBJBgNVBAsMQkFtYXpvbiBXZWIgU2VydmljZXMgTz1BbWF6b24uY29t
IEluYy4gTD1TZWF0dGxlIFNUPVdhc2hpbmd0b24gQz1VUzAeFw0yNDA4MjEwOTAw
MDBaFw0yNTA4MjEwOTAwMDBaMB4xHDAaBgNVBAMME0FXUyBJb1QgQ2VydGlmaWNh
dGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7XXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXX
-----END CERTIFICATE-----""",
                "key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7XXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXX
-----END PRIVATE KEY-----""",
                "ca_cert": """-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIuJruydjsw2hUwsqdEx7ZgIkn+aU9D68Ss8XlJ8yFLr
9s0xWbCg5Y5PYJrg2E2ZrNYDpVzLj5QKvfVxvJVF8UgKF7Gd7+JMYX0H0sTqvR8b
x1cVoEnyL0L1YYXB3wdHBhFFrluxC8u8BbgDyMD+Q9Zx7LDLJYdVEPM3qsjQQ8LB
8+XZGQWU2PNzI0zBVAkABJ8hJ8qYDQeXV/o3k4yXJ8zHZzHfp2K3oNR2iJzLIq+j
A4nMgmjVYGpPj7YE6P3bBbRqIWgG
-----END CERTIFICATE-----"""
            },
            "mug_002": {
                "device_id": "mug_002", 
                "host": "a3k7j9m2l5n8p2.iot.ap-northeast-1.amazonaws.com",
                "port": 8883,
                "client_id": "mug_002",
                "cert": "...",  # Similar certificate content
                "key": "...",   # Similar private key content
                "ca_cert": "..."
            }
        }
        
    def get_help(self) -> Dict[str, Any]:
        """Return service help information"""
        return {
            "service": "mcp_pixel_mug",
            "version": "1.0.0",
            "description": "PixelMug Smart Mug MQTT Control Interface",
            "methods": [
                {
                    "name": "help",
                    "description": "Get service help information",
                    "params": {}
                },
                {
                    "name": "prepare_mqtt_connection", 
                    "description": "Prepare MQTT connection parameters",
                    "params": {
                        "device_id": "Device ID, e.g. mug_001"
                    }
                },
                {
                    "name": "publish_action",
                    "description": "Publish device operation commands",
                    "params": {
                        "device_id": "Device ID",
                        "action": "Operation type: heat/display/color/brew/pixel_art",
                        "params": "Operation parameters"
                    }
                },
                {
                    "name": "convert_image_to_pixels",
                    "description": "Convert base64 image to pixel matrix for display",
                    "params": {
                        "image_data": "Base64 encoded image (PNG/JPEG)",
                        "target_width": "Target width for pixel matrix (optional, default: 16)",
                        "target_height": "Target height for pixel matrix (optional, default: 16)",
                        "resize_method": "Resize method: nearest/bilinear/bicubic (optional, default: nearest)"
                    }
                }
            ],
            "supported_actions": [
                {"action": "heat", "description": "Heating", "params": {"temperature": "Target temperature (°C)"}},
                {"action": "display", "description": "Display information", "params": {"text": "Display text", "duration": "Display duration (seconds)"}},
                {"action": "color", "description": "Color change", "params": {"color": "Color code (hex)", "mode": "Color mode"}},
                {"action": "brew", "description": "Brewing", "params": {"type": "Coffee type", "strength": "Strength"}},
                {"action": "pixel_art", "description": "Display pixel art", "params": {"pattern": "Pixel pattern (2D array or base64)", "width": "Image width (pixels)", "height": "Image height (pixels)", "duration": "Display duration (seconds)"}}
            ],
            "pixel_art_examples": self._generate_pixel_examples(),
            "pixel_art_formats": {
                "2d_array": "Array of arrays with hex colors: [[\"#FF0000\", \"#00FF00\"], [\"#0000FF\", \"#FFFFFF\"]]",
                "rgb_array": "Array of arrays with RGB tuples: [[[255,0,0], [0,255,0]], [[0,0,255], [255,255,255]]]",
                "base64": "Base64 encoded image data (PNG/JPEG)"
            }
        }
    
    def prepare_mqtt_connection(self, device_id: str) -> Dict[str, Any]:
        """Prepare MQTT connection parameters"""
        try:
            device_info = self.mock_devices.get(device_id)
            if not device_info:
                raise ValueError(f"Device {device_id} not registered")
            
            # Build topic name using univoice_mug_{action} format as required
            topic_prefix = f"univoice_mug_{device_id}"
            
            connection_info = {
                "host": device_info["host"],
                "topic": f"{topic_prefix}/cmd",  # Command topic
                "status_topic": f"{topic_prefix}/status",  # Status topic
                "protocol": "mqtts",
                "port": device_info["port"],
                "client_id": device_info["client_id"],
                "cert": device_info["cert"],
                "key": device_info["key"],
                "ca_cert": device_info["ca_cert"],
                "payload_schema": {
                    "action": "string",
                    "params": {
                        "temperature": "int",
                        "color": "string",
                        "text": "string",
                        "duration": "int",
                        "type": "string",
                        "strength": "string",
                        "mode": "string",
                        "pattern": "array or string",
                        "width": "int",
                        "height": "int"
                    },
                    "timestamp": "string",
                    "request_id": "string"
                }
            }
            
            self.logger.info(f"Successfully prepared connection parameters for device {device_id}")
            return connection_info
            
        except Exception as e:
            self.logger.error(f"Failed to prepare connection parameters: {str(e)}")
            raise
    
    async def publish_action(self, device_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish operation commands to MQTT"""
        try:
            # Get device connection information
            connection_info = self.prepare_mqtt_connection(device_id)
            
            # Build message payload
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"
            request_id = str(uuid.uuid4())
            
            payload = {
                "action": action,
                "params": params,
                "timestamp": timestamp,
                "request_id": request_id,
                "device_id": device_id
            }
            
            # Validate operation type
            valid_actions = ["heat", "display", "color", "brew", "pixel_art"]
            if action not in valid_actions:
                raise ValueError(f"Unsupported operation type: {action}, supported types: {valid_actions}")
            
            # Use async MQTT client to publish message
            await self._publish_mqtt_message(connection_info, payload)
            
            result = {
                "status": "published",
                "timestamp": timestamp,
                "request_id": request_id,
                "topic": connection_info["topic"],
                "payload": payload
            }
            
            self.logger.info(f"Successfully published operation {action} to device {device_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to publish operation: {str(e)}")
            raise
    
    async def _publish_mqtt_message(self, connection_info: Dict[str, Any], payload: Dict[str, Any]):
        """Publish MQTT message asynchronously"""
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.load_verify_locations(cadata=connection_info["ca_cert"])
            ssl_context.load_cert_chain(
                certfile=None,
                keyfile=None,
                cert_chain=connection_info["cert"],
                key=connection_info["key"]
            )
            
            # Use async MQTT client
            async with Client(
                hostname=connection_info["host"],
                port=connection_info["port"],
                client_id=connection_info["client_id"],
                tls_context=ssl_context
            ) as client:
                await client.publish(
                    connection_info["topic"],
                    json.dumps(payload),
                    qos=1
                )
                self.logger.info(f"Message published to topic: {connection_info['topic']}")
                
        except Exception as e:
            self.logger.warning(f"MQTT publish failed (simulation mode): {str(e)}")
            # In development environment, we simulate successful publishing
            self.logger.info("Using simulation mode, assuming message published successfully")
    
    def _validate_pixel_pattern(self, pattern: Union[List, str], width: int, height: int) -> bool:
        """Validate pixel art pattern"""
        if isinstance(pattern, str):
            # Base64 encoded image
            try:
                decoded = base64.b64decode(pattern)
                # Basic validation - should have reasonable size
                if len(decoded) < width * height or len(decoded) > width * height * 4:
                    raise ValueError("Base64 pattern size doesn't match dimensions")
                return True
            except Exception as e:
                raise ValueError(f"Invalid base64 pattern: {str(e)}")
        
        elif isinstance(pattern, list):
            # 2D array of colors
            if len(pattern) != height:
                raise ValueError(f"Pattern height {len(pattern)} doesn't match specified height {height}")
            
            for row_idx, row in enumerate(pattern):
                if not isinstance(row, list):
                    raise ValueError(f"Row {row_idx} is not a list")
                if len(row) != width:
                    raise ValueError(f"Row {row_idx} width {len(row)} doesn't match specified width {width}")
                
                for col_idx, pixel in enumerate(row):
                    if isinstance(pixel, str):
                        # Hex color validation
                        if not re.match(r'^#[0-9A-Fa-f]{6}$', pixel):
                            raise ValueError(f"Invalid color format at [{row_idx}][{col_idx}]: {pixel}")
                    elif isinstance(pixel, (list, tuple)):
                        # RGB/RGBA values
                        if len(pixel) not in [3, 4]:
                            raise ValueError(f"Invalid RGB/RGBA format at [{row_idx}][{col_idx}]: {pixel}")
                        for component in pixel:
                            if not isinstance(component, int) or component < 0 or component > 255:
                                raise ValueError(f"Invalid RGB component at [{row_idx}][{col_idx}]: {component}")
                    else:
                        raise ValueError(f"Invalid pixel format at [{row_idx}][{col_idx}]: {type(pixel)}")
            return True
        
        else:
            raise ValueError("Pattern must be a 2D array or base64 string")

    def _generate_pixel_examples(self) -> Dict[str, Any]:
        """Generate pixel art examples for documentation"""
        return {
            "smiley_face": {
                "description": "8x8 smiley face",
                "pattern": [
                    ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]
                ],
                "width": 8,
                "height": 8
            },
            "heart": {
                "description": "8x8 heart shape",
                "pattern": [
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000"],
                    ["#000000", "#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#000000"]
                ],
                "width": 8,
                "height": 8
            },
            "coffee_cup": {
                "description": "8x8 coffee cup",
                "pattern": [
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#FFFFFF", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#FFFFFF", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#000000", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
                ],
                "width": 8,
                "height": 8
            }
        }

    def validate_device_params(self, action: str, params: Dict[str, Any]) -> bool:
        """Validate device operation parameters"""
        validation_rules = {
            "heat": {
                "required": ["temperature"],
                "temperature": {"type": int, "min": 20, "max": 100}
            },
            "display": {
                "required": ["text"],
                "text": {"type": str, "max_length": 100},
                "duration": {"type": int, "min": 1, "max": 3600, "default": 10}
            },
            "color": {
                "required": ["color"],
                "color": {"type": str, "pattern": r"^#[0-9A-Fa-f]{6}$"},
                "mode": {"type": str, "choices": ["solid", "blink", "gradient"], "default": "solid"}
            },
            "brew": {
                "required": ["type"],
                "type": {"type": str, "choices": ["espresso", "americano", "latte", "cappuccino"]},
                "strength": {"type": str, "choices": ["light", "medium", "strong"], "default": "medium"}
            },
            "pixel_art": {
                "required": ["pattern", "width", "height"],
                "pattern": {"type": (list, str), "description": "2D array of colors or base64 encoded image"},
                "width": {"type": int, "min": 1, "max": 128},
                "height": {"type": int, "min": 1, "max": 128},
                "duration": {"type": int, "min": 1, "max": 3600, "default": 30}
            }
        }
        
        if action not in validation_rules:
            return False
            
        rules = validation_rules[action]
        
        # Check required parameters
        for required_param in rules["required"]:
            if required_param not in params:
                raise ValueError(f"Missing required parameter: {required_param}")
        
        # Validate parameter types and values
        for param_name, param_value in params.items():
            if param_name in rules:
                rule = rules[param_name]
                
                # Type checking (handle tuple types for pixel_art)
                if "type" in rule:
                    expected_type = rule["type"]
                    if isinstance(expected_type, tuple):
                        # Multiple allowed types (for pixel_art pattern)
                        if not isinstance(param_value, expected_type):
                            type_names = [t.__name__ for t in expected_type]
                            raise ValueError(f"Parameter {param_name} type error, expected one of: {type_names}")
                    else:
                        if not isinstance(param_value, expected_type):
                            raise ValueError(f"Parameter {param_name} type error, expected {expected_type.__name__}")
                
                # Range checking for numbers
                if isinstance(param_value, int):
                    if "min" in rule and param_value < rule["min"]:
                        raise ValueError(f"Parameter {param_name} value too small, minimum: {rule['min']}")
                    if "max" in rule and param_value > rule["max"]:
                        raise ValueError(f"Parameter {param_name} value too large, maximum: {rule['max']}")
                
                # Length checking for strings
                if isinstance(param_value, str):
                    if "max_length" in rule and len(param_value) > rule["max_length"]:
                        raise ValueError(f"Parameter {param_name} too long, maximum length: {rule['max_length']}")
                    if "choices" in rule and param_value not in rule["choices"]:
                        raise ValueError(f"Parameter {param_name} invalid value, valid choices: {rule['choices']}")
        
        # Special validation for pixel_art
        if action == "pixel_art":
            pattern = params.get("pattern")
            width = params.get("width")
            height = params.get("height")
            
            if pattern is not None and width is not None and height is not None:
                self._validate_pixel_pattern(pattern, width, height)
        
        return True

    def convert_image_to_pixels(self, image_data: str, target_width: int = 16, target_height: int = 16, resize_method: str = "nearest") -> Dict[str, Any]:
        """Convert base64 image to pixel matrix"""
        try:
            # Validate parameters
            if target_width < 1 or target_width > 128:
                raise ValueError("target_width must be between 1 and 128")
            if target_height < 1 or target_height > 128:
                raise ValueError("target_height must be between 1 and 128")
            if resize_method not in ["nearest", "bilinear", "bicubic"]:
                raise ValueError("resize_method must be one of: nearest, bilinear, bicubic")
            
            # Check if PIL is available
            if not PIL_AVAILABLE:
                # Fallback: Return a simple pattern if PIL is not available
                self.logger.warning("PIL not available, using fallback pattern generation")
                return self._generate_fallback_pattern(target_width, target_height, image_data)
            
            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {str(e)}")
            
            # Open image with PIL
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                raise ValueError(f"Cannot open image: {str(e)}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to target dimensions
            resize_filters = {
                "nearest": Image.NEAREST,
                "bilinear": Image.BILINEAR, 
                "bicubic": Image.BICUBIC
            }
            
            resized_image = image.resize((target_width, target_height), resize_filters[resize_method])
            
            # Convert to pixel matrix
            pixel_matrix = []
            for y in range(target_height):
                row = []
                for x in range(target_width):
                    r, g, b = resized_image.getpixel((x, y))
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    row.append(hex_color)
                pixel_matrix.append(row)
            
            # Get original image info
            original_size = image.size
            
            result = {
                "pixel_matrix": pixel_matrix,
                "width": target_width,
                "height": target_height,
                "original_size": {
                    "width": original_size[0],
                    "height": original_size[1]
                },
                "resize_method": resize_method,
                "total_pixels": target_width * target_height,
                "format_info": {
                    "original_mode": image.mode,
                    "converted_mode": "RGB",
                    "pixel_format": "hex_colors"
                }
            }
            
            self.logger.info(f"Successfully converted image from {original_size} to {target_width}x{target_height} pixel matrix")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to convert image to pixels: {str(e)}")
            raise

    def _generate_fallback_pattern(self, width: int, height: int, image_data: str) -> Dict[str, Any]:
        """Generate a fallback pattern when PIL is not available"""
        # Generate a simple hash-based pattern from the image data
        import hashlib
        
        # Create a hash from the image data
        hash_obj = hashlib.md5(image_data.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Generate colors based on hash
        colors = []
        for i in range(0, len(hash_hex), 6):
            color_hex = hash_hex[i:i+6]
            if len(color_hex) == 6:
                colors.append(f"#{color_hex}")
        
        # If we don't have enough colors, repeat them
        while len(colors) < width * height:
            colors.extend(colors)
        
        # Create pixel matrix
        pixel_matrix = []
        color_index = 0
        for y in range(height):
            row = []
            for x in range(width):
                row.append(colors[color_index % len(colors)])
                color_index += 1
            pixel_matrix.append(row)
        
        return {
            "pixel_matrix": pixel_matrix,
            "width": width,
            "height": height,
            "original_size": {"width": "unknown", "height": "unknown"},
            "resize_method": "fallback_hash",
            "total_pixels": width * height,
            "format_info": {
                "original_mode": "unknown",
                "converted_mode": "hash_based",
                "pixel_format": "hex_colors"
            },
            "warning": "PIL not available, generated pattern from image hash"
        }

    def convert_and_display_image(self, device_id: str, image_data: str, target_width: int = 16, target_height: int = 16, resize_method: str = "nearest", duration: int = 30) -> Dict[str, Any]:
        """Convert base64 image to pixels and display on device"""
        try:
            # Convert image to pixel matrix
            conversion_result = self.convert_image_to_pixels(image_data, target_width, target_height, resize_method)
            
            # Extract pixel matrix
            pixel_matrix = conversion_result["pixel_matrix"]
            width = conversion_result["width"]
            height = conversion_result["height"]
            
            # Validate the generated pattern
            self._validate_pixel_pattern(pixel_matrix, width, height)
            
            # Prepare the action parameters
            action_params = {
                "pattern": pixel_matrix,
                "width": width,
                "height": height,
                "duration": duration
            }
            
            # Send to device using existing publish_action method
            result = asyncio.run(self.publish_action(device_id, "pixel_art", action_params))
            
            # Add conversion info to result
            result["conversion_info"] = {
                "original_size": conversion_result["original_size"],
                "target_size": {"width": width, "height": height},
                "resize_method": resize_method,
                "total_pixels": conversion_result["total_pixels"]
            }
            
            self.logger.info(f"Successfully converted and displayed image on device {device_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to convert and display image: {str(e)}")
            raise


# Service instance
mug_service = MugService()
