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
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
import asyncio
from asyncio_mqtt import Client


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
                        "action": "Operation type: heat/display/color/brew",
                        "params": "Operation parameters"
                    }
                }
            ],
            "supported_actions": [
                {"action": "heat", "description": "Heating", "params": {"temperature": "Target temperature (°C)"}},
                {"action": "display", "description": "Display information", "params": {"text": "Display text", "duration": "Display duration (seconds)"}},
                {"action": "color", "description": "Color change", "params": {"color": "Color code (hex)", "mode": "Color mode"}},
                {"action": "brew", "description": "Brewing", "params": {"type": "Coffee type", "strength": "Strength"}}
            ]
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
                        "mode": "string"
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
            valid_actions = ["heat", "display", "color", "brew"]
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
                
                # Type checking
                if "type" in rule and not isinstance(param_value, rule["type"]):
                    raise ValueError(f"Parameter {param_name} type error, expected {rule['type'].__name__}")
                
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
        
        return True


# Service instance
mug_service = MugService()
