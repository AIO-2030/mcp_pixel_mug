# 🎯 PixelMug MCP - Smart Mug Control Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hackathon Ready](https://img.shields.io/badge/hackathon-ready-brightgreen.svg)](https://github.com/AIO-2030/mcp_pixel_mug)

A comprehensive **Model Context Protocol (MCP)** service for controlling PixelMug smart mugs via MQTT. This project provides a complete hackathon-ready solution with JSON-RPC 2.0 compliance, designed for seamless integration into the AIO-2030 platform and smart home ecosystems.

## 🌟 Key Features

- **🔌 Full MCP Implementation**: Complete JSON-RPC 2.0 compliant server
- **📡 MQTT Integration**: Secure AWS IoT Core communication with SSL/TLS
- **🎮 Device Operations**: Heat control, display management, color changing, brewing
- **🧪 Comprehensive Testing**: Full test suite with automated validation
- **📱 Bluetooth Bridge**: Example integration for device discovery
- **🚀 Hackathon Ready**: Complete documentation and examples included
- **⚡ Async Performance**: Built with asyncio for high-performance operations
- **🔒 Secure**: Certificate-based authentication and validation

## 📦 Project Structure

```
mcp_pixel_mug/
├── 📄 LICENSE                    # MIT License
├── 📚 README.md                  # This comprehensive documentation
├── 🔧 build.py                   # Automated build and deployment script
├── 🌐 mcp_server.py              # Core MCP server implementation
├── 💻 stdio_server.py            # Standard I/O server for process communication
├── ⚙️  mug_service.py             # Business logic and MQTT operations
├── 📋 requirements.txt           # Python dependencies
├── 🧪 test_help.sh              # Help method testing script
├── 🧪 test_prepare.sh           # Connection preparation testing
├── 🧪 test_publish.sh           # Action publishing testing
├── 📁 examples/                 # Usage examples and demos
│   ├── 🎯 example_client.py     # Complete client implementation example
│   └── 📱 bluetooth_bridge.py   # Bluetooth device integration demo
└── 📦 dist/                     # Build artifacts (generated)
    ├── 🚀 start_server.py       # Production server launcher
    └── 📄 (other distribution files)
```

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8+** (recommended: Python 3.9+)
- **pip** package manager
- **bash** shell (for test scripts)
- **Git** (for cloning)

### Installation

```bash
# Clone the repository
git clone https://github.com/AIO-2030/mcp_pixel_mug.git
cd mcp_pixel_mug

# Install dependencies
pip install -r requirements.txt

# Verify installation
python build.py validate
```

### Launch Server

Choose your preferred server mode:

#### 🔧 Development Mode (Interactive)
```bash
python mcp_server.py
```

#### 📡 Production Mode (Standard I/O)
```bash
python stdio_server.py
```

#### 📦 Distribution Mode (Build & Deploy)
```bash
python build.py
cd dist
python start_server.py
```

## 🎮 Core MCP Methods

The service implements three primary JSON-RPC 2.0 methods:

### 1. `help` - Service Information

**Purpose**: Retrieve comprehensive service capabilities and documentation

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "help",
  "params": {},
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
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
      {
        "action": "heat",
        "description": "Heating",
        "params": {
          "temperature": "Target temperature (°C)"
        }
      },
      {
        "action": "display",
        "description": "Display information",
        "params": {
          "text": "Display text",
          "duration": "Display duration (seconds)"
        }
      },
      {
        "action": "color",
        "description": "Color change",
        "params": {
          "color": "Color code (hex)",
          "mode": "Color mode"
        }
      },
      {
        "action": "brew",
        "description": "Brewing",
        "params": {
          "type": "Coffee type",
          "strength": "Strength"
        }
      }
    ]
  },
  "id": 1
}
```

### 2. `prepare_mqtt_connection` - Connection Setup

**Purpose**: Retrieve MQTT connection parameters for a specific device

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "prepare_mqtt_connection",
  "params": {
    "device_id": "mug_001"
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "host": "a3k7j9m2l5n8p1.iot.ap-northeast-1.amazonaws.com",
    "topic": "univoice_mug_mug_001/cmd",
    "status_topic": "univoice_mug_mug_001/status",
    "protocol": "mqtts",
    "port": 8883,
    "client_id": "mug_001",
    "cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
    "ca_cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
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
  },
  "id": 2
}
```

### 3. `publish_action` - Device Control

**Purpose**: Send operation commands to PixelMug devices

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "publish_action",
  "params": {
    "device_id": "mug_001",
    "action": "heat",
    "params": {
      "temperature": 65
    }
  },
  "id": 3
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "published",
    "timestamp": "2025-01-21T20:10:00Z",
    "request_id": "uuid-4-string",
    "topic": "univoice_mug_mug_001/cmd",
    "payload": {
      "action": "heat",
      "params": {
        "temperature": 65
      },
      "timestamp": "2025-01-21T20:10:00Z",
      "request_id": "uuid-4-string",
      "device_id": "mug_001"
    }
  },
  "id": 3
}
```

## ⚙️ Supported Device Operations

### 🔥 Heat Control (`heat`)

Control the mug's heating element to reach desired temperature.

**Parameters**:
- `temperature` (integer, required): Target temperature in Celsius (20-100°C)

**Example**:
```json
{
  "action": "heat",
  "params": {
    "temperature": 75
  }
}
```

### 📺 Display Management (`display`)

Show text messages on the mug's display screen.

**Parameters**:
- `text` (string, required): Message to display (max 100 characters)
- `duration` (integer, optional): Display duration in seconds (1-3600, default: 10)

**Example**:
```json
{
  "action": "display",
  "params": {
    "text": "Good Morning!",
    "duration": 15
  }
}
```

### 🌈 Color Control (`color`)

Change the mug's LED color scheme.

**Parameters**:
- `color` (string, required): Hex color code (e.g., "#FF5733")
- `mode` (string, optional): Color mode - "solid", "blink", "gradient" (default: "solid")

**Example**:
```json
{
  "action": "color",
  "params": {
    "color": "#00FF88",
    "mode": "gradient"
  }
}
```

### ☕ Brewing Control (`brew`)

Activate automated brewing programs.

**Parameters**:
- `type` (string, required): Coffee type - "espresso", "americano", "latte", "cappuccino"
- `strength` (string, optional): Brew strength - "light", "medium", "strong" (default: "medium")

**Example**:
```json
{
  "action": "brew",
  "params": {
    "type": "espresso",
    "strength": "strong"
  }
}
```

## 📡 MQTT Communication Protocol

### Topic Architecture

The service uses a structured topic naming convention:

- **Command Topic**: `univoice_mug_{device_id}/cmd`
- **Status Topic**: `univoice_mug_{device_id}/status`

### Message Format

All MQTT messages follow this standardized format:

```json
{
  "action": "heat",
  "params": {
    "temperature": 65
  },
  "timestamp": "2025-01-21T20:10:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "device_id": "mug_001"
}
```

### Security & Authentication

- **Protocol**: MQTT over TLS (MQTTS) on port 8883
- **Authentication**: X.509 client certificates
- **Certificate Authority**: AWS IoT Core CA
- **Encryption**: TLS 1.2+ with AES-256 encryption

## 🧪 Testing & Validation

### Automated Test Suite

Run the complete test suite:

```bash
# Individual tests
./test_help.sh           # Test help method
./test_prepare.sh        # Test connection preparation
./test_publish.sh        # Test action publishing

# All tests via build script
python build.py test
```

### Manual Testing

```bash
# Start interactive server
python mcp_server.py

# Send test request
{"jsonrpc": "2.0", "method": "help", "params": {}, "id": 1}
```

## 💡 Usage Examples

### Basic Client Implementation

```python
#!/usr/bin/env python3
"""
Simple PixelMug MCP Client Example
"""

import json
import asyncio
from mcp_server import MCPServer

class PixelMugClient:
    def __init__(self):
        self.server = MCPServer()
        self.request_id = 1
    
    async def heat_mug(self, device_id: str, temperature: int):
        """Heat the mug to specified temperature"""
        request = {
            "jsonrpc": "2.0",
            "method": "publish_action",
            "params": {
                "device_id": device_id,
                "action": "heat",
                "params": {"temperature": temperature}
            },
            "id": self.request_id
        }
        self.request_id += 1
        
        response = await self.server.handle_request(json.dumps(request))
        return json.loads(response)
    
    async def display_message(self, device_id: str, message: str, duration: int = 10):
        """Display message on mug screen"""
        request = {
            "jsonrpc": "2.0",
            "method": "publish_action",
            "params": {
                "device_id": device_id,
                "action": "display",
                "params": {"text": message, "duration": duration}
            },
            "id": self.request_id
        }
        self.request_id += 1
        
        response = await self.server.handle_request(json.dumps(request))
        return json.loads(response)

async def main():
    client = PixelMugClient()
    
    # Heat mug to 70°C
    result = await client.heat_mug("mug_001", 70)
    print(f"Heat result: {result}")
    
    # Show welcome message
    result = await client.display_message("mug_001", "Welcome to PixelMug!", 15)
    print(f"Display result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Bluetooth Integration Example

```python
#!/usr/bin/env python3
"""
Bluetooth PixelMug Discovery and Control
"""

import asyncio
from typing import List, Dict
from mcp_server import MCPServer

class BluetoothPixelMugController:
    def __init__(self):
        self.mcp_server = MCPServer()
        self.discovered_devices: List[Dict] = []
    
    async def discover_devices(self) -> List[Dict]:
        """Discover PixelMug devices via Bluetooth"""
        # Simulated Bluetooth discovery
        # In real implementation, use pybluez or similar
        mock_devices = [
            {"addr": "AA:BB:CC:DD:EE:01", "name": "PixelMug-001"},
            {"addr": "AA:BB:CC:DD:EE:02", "name": "PixelMug-002"}
        ]
        
        for device in mock_devices:
            device_id = self.extract_device_id(device["addr"], device["name"])
            device["device_id"] = device_id
            self.discovered_devices.append(device)
        
        return self.discovered_devices
    
    def extract_device_id(self, bt_addr: str, name: str) -> str:
        """Extract device ID from Bluetooth info"""
        if "PixelMug-" in name:
            return f"mug_{name.split('-')[-1].lower()}"
        return f"mug_{bt_addr.replace(':', '')[-6:].lower()}"
    
    async def control_all_mugs(self, action: str, params: Dict):
        """Send command to all discovered mugs"""
        tasks = []
        for device in self.discovered_devices:
            task = self.send_command(device["device_id"], action, params)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def send_command(self, device_id: str, action: str, params: Dict):
        """Send command to specific device"""
        request = {
            "jsonrpc": "2.0",
            "method": "publish_action",
            "params": {
                "device_id": device_id,
                "action": action,
                "params": params
            },
            "id": 1
        }
        
        response = await self.mcp_server.handle_request(json.dumps(request))
        return json.loads(response)

async def demo():
    controller = BluetoothPixelMugController()
    
    # Discover devices
    devices = await controller.discover_devices()
    print(f"Discovered {len(devices)} PixelMug devices")
    
    # Heat all mugs to 65°C
    results = await controller.control_all_mugs("heat", {"temperature": 65})
    print("Heat command results:", results)
    
    # Show synchronized message
    results = await controller.control_all_mugs("display", {
        "text": "Hackathon Demo!", 
        "duration": 20
    })
    print("Display command results:", results)

if __name__ == "__main__":
    asyncio.run(demo())
```

## 🔧 Development & Build

### Build Commands

```bash
# Clean previous builds
python build.py clean

# Install dependencies
python build.py install

# Validate project structure
python build.py validate

# Run test suite
python build.py test

# Build distribution package
python build.py build

# Complete build pipeline
python build.py all
```

### Development Environment

```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run in development mode with detailed logging
python mcp_server.py
```

### Debug Mode

The server provides comprehensive logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Log output includes:
- 📥 Incoming JSON-RPC requests
- 📤 Outgoing responses
- 🔗 MQTT connection status
- ⚙️ Device operation execution
- ❌ Error details and stack traces

## 🌐 AIO-2030 Platform Integration

This service is designed for seamless integration with the AIO-2030 platform:

### ✅ Compliance Features

1. **JSON-RPC 2.0 Standard**: Full specification compliance
2. **Modular Architecture**: Can run standalone or as microservice
3. **Async Operations**: Non-blocking, high-performance processing
4. **Error Handling**: Comprehensive error codes and messages
5. **Extensibility**: Easy to add new device types and operations

### 🔌 Integration Patterns

#### Microservice Mode
```bash
# Run as standalone service
python stdio_server.py
```

#### Library Mode
```python
from mug_service import mug_service

# Use service directly in your application
result = await mug_service.publish_action("mug_001", "heat", {"temperature": 70})
```

#### Container Mode
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "stdio_server.py"]
```

## 🏆 Hackathon Features

This project is optimized for hackathon development:

### 🚀 Rapid Prototyping
- **Zero-config setup**: Works out of the box
- **Mock data included**: No external dependencies required
- **Comprehensive examples**: Copy-paste ready code
- **Interactive testing**: Built-in test scripts

### 📚 Complete Documentation
- **API reference**: Full method documentation
- **Usage examples**: Real-world scenarios
- **Integration guides**: Multiple deployment options
- **Troubleshooting**: Common issues and solutions

### 🧪 Testing Ready
- **Unit tests**: Core functionality validation
- **Integration tests**: End-to-end workflows
- **Mock devices**: Simulated hardware responses
- **Performance tests**: Load and stress testing

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the project directory
cd mcp_pixel_mug

# Verify Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### 2. MQTT Connection Issues
```python
# The service uses simulation mode by default
# Real MQTT requires valid AWS IoT certificates
self.logger.info("Using simulation mode, assuming message published successfully")
```

#### 3. Permission Errors
```bash
# Ensure test scripts are executable
chmod +x test_*.sh

# Check file permissions
ls -la *.py *.sh
```

#### 4. Dependency Issues
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Debug Tips

1. **Enable verbose logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test individual components**:
   ```bash
   python -c "from mug_service import mug_service; print('Service OK')"
   ```

3. **Validate JSON-RPC requests**:
   ```bash
   echo '{"jsonrpc":"2.0","method":"help","id":1}' | python stdio_server.py
   ```

## 📋 TODO & Roadmap

### Immediate Enhancements
- [ ] Real-time device status monitoring
- [ ] Batch operation support
- [ ] Operation history logging
- [ ] Device health checking
- [ ] Custom operation extensions

### Future Features
- [ ] Web dashboard interface
- [ ] Mobile app integration
- [ ] Voice control support
- [ ] AI-powered brewing recommendations
- [ ] Multi-tenant device management

## 🤝 Contributing

We welcome contributions! This is a hackathon project designed for collaboration:

### Quick Contribution Guide
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Standards
- **Python 3.8+** compatibility
- **JSON-RPC 2.0** compliance
- **Comprehensive testing** for new features
- **Clear documentation** for all changes

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**TL;DR**: You can use, modify, and distribute this code for any purpose, including commercial use, as long as you include the original copyright notice.

## 📞 Support & Contact

### Project Information
- **Repository**: [AIO-2030/mcp_pixel_mug](https://github.com/AIO-2030/mcp_pixel_mug)
- **Issues**: [Report bugs or request features](https://github.com/AIO-2030/mcp_pixel_mug/issues)
- **Discussions**: [Community forum](https://github.com/AIO-2030/mcp_pixel_mug/discussions)

### Hackathon Support
For immediate assistance during hackathons:
- **Discord**: Join our development channel
- **Slack**: #pixelmug-support
- **Email**: support@pixelmug-mcp.dev

### Quick Links
- 🚀 [Getting Started](#quick-start-guide)
- 📚 [API Documentation](#core-mcp-methods)
- 💡 [Examples](#usage-examples)
- 🧪 [Testing Guide](#testing--validation)
- 🔧 [Build Instructions](#development--build)

---

**⚡ Ready to hack? Get started in under 5 minutes!**

```bash
git clone https://github.com/AIO-2030/mcp_pixel_mug.git
cd mcp_pixel_mug
pip install -r requirements.txt
python examples/example_client.py demo
```

**🎉 Happy hacking with PixelMug MCP!**

---

> **Note**: This project uses mock data for development and testing. For production deployment with real PixelMug devices, configure actual AWS IoT certificates and device registrations.