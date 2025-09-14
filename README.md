# 🎨 PixelMug MCP Server

A Model Context Protocol (MCP) server for controlling PixelMug smart mugs via Tencent Cloud IoT Explorer. This service provides pixel art display, GIF animation, and image conversion capabilities for IoT-connected smart mugs.

## ✨ Features

- **🎨 Pixel Art Display**: Send custom pixel patterns to mug displays
- **🎬 GIF Animation**: Display animated GIFs with frame control
- **🖼️ Image Conversion**: Convert any image to pixel art format
- **☁️ Tencent Cloud IoT**: Secure device communication via IoT Explorer
- **🔐 STS Authentication**: Temporary credentials for secure access
- **📱 MCP Protocol**: Standardized JSON-RPC interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Tencent Cloud account with IoT Explorer access
- CAM role configured for device access

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AIO-2030/mcp_pixel_mug.git
cd mcp_pixel_mug
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/IoTDeviceRole"
export TC_SECRET_ID="AKID_PLACEHOLDER_SECRET_ID"  # Optional in CVM/TKE
export TC_SECRET_KEY="PLACEHOLDER_SECRET_KEY"     # Optional in CVM/TKE
export DEFAULT_REGION="ap-guangzhou"
```

4. Start the server:
```bash
python mcp_server.py
```

## 📖 API Reference

### Available Methods

The MCP server supports the following JSON-RPC methods:

#### 1. `help` - Get Service Information

**Purpose**: Retrieve service capabilities and method documentation

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
    "version": "2.0.0",
    "description": "PixelMug Smart Mug Tencent Cloud IoT Control Interface",
    "methods": [
      {
        "name": "help",
        "description": "Get service help information",
        "params": {}
      },
      {
        "name": "issue_sts",
        "description": "Issue Tencent Cloud IoT STS temporary access credentials",
        "params": {
          "product_id": "Product ID, e.g.: ABC123DEF",
          "device_name": "Device name, e.g.: mug_001"
        }
      },
      {
        "name": "send_pixel_image",
        "description": "Send pixel image to device via Tencent Cloud IoT",
        "params": {
          "product_id": "Product ID",
          "device_name": "Device name",
          "image_data": "Base64 encoded image or pixel matrix",
          "target_width": "Target width (optional, default: 16)",
          "target_height": "Target height (optional, default: 16)"
        }
      },
      {
        "name": "send_gif_animation",
        "description": "Send GIF pixel animation to device via Tencent Cloud IoT",
        "params": {
          "product_id": "Product ID",
          "device_name": "Device name",
          "gif_data": "Base64 encoded GIF or frame array",
          "frame_delay": "Delay between frames in ms (optional, default: 100)",
          "loop_count": "Number of loops (optional, default: 0 for infinite)"
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
      {
        "action": "send_pixel_image",
        "description": "Send pixel image via Tencent Cloud IoT",
        "params": {
          "image_data": "Pixel data or base64 image",
          "width": "Image width",
          "height": "Image height"
        }
      },
      {
        "action": "send_gif_animation",
        "description": "Send GIF animation via Tencent Cloud IoT",
        "params": {
          "gif_data": "GIF frame data",
          "frame_delay": "Frame delay (ms)",
          "loop_count": "Loop count"
        }
      }
    ],
    "pixel_art_formats": {
      "2d_array": "Array of arrays with hex colors: [[\"#FF0000\", \"#00FF00\"], [\"#0000FF\", \"#FFFFFF\"]]",
      "rgb_array": "Array of arrays with RGB tuples: [[[255,0,0], [0,255,0]], [[0,0,255], [255,255,255]]]",
      "base64": "Base64 encoded image data (PNG/JPEG)"
    }
  },
  "id": 1
}
```

### 2. `issue_sts` - Issue STS Credentials

**Purpose**: Issue Tencent Cloud IoT STS temporary access credentials for device control

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "issue_sts",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001"
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tmpSecretId": "AKID_PLACEHOLDER_SECRET_ID",
    "tmpSecretKey": "PLACEHOLDER_SECRET_KEY",
    "token": "PLACEHOLDER_TOKEN",
    "expiration": "2024-01-01T12:00:00Z",
    "region": "ap-guangzhou",
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "issued_at": "2024-01-01T11:45:00Z"
  },
  "id": 2
}
```

### 3. `send_pixel_image` - Send Pixel Image

**Purpose**: Send pixel image to device via Tencent Cloud IoT

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "send_pixel_image",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "target_width": 16,
    "target_height": 16
  },
  "id": 3
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "client_token": "PLACEHOLDER_CLIENT_TOKEN",
    "call_status": "SUCCESS",
    "request_id": "PLACEHOLDER_REQUEST_ID",
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "action_id": "display_pixel_image",
    "image_info": {
      "width": 16,
      "height": 16,
      "total_pixels": 256
    },
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "id": 3
}
```

### 4. `send_gif_animation` - Send GIF Animation

**Purpose**: Send GIF pixel animation to device via Tencent Cloud IoT

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "send_gif_animation",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
    "frame_delay": 100,
    "loop_count": 0,
    "target_width": 16,
    "target_height": 16
  },
  "id": 4
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "client_token": "PLACEHOLDER_CLIENT_TOKEN",
    "call_status": "SUCCESS",
    "request_id": "PLACEHOLDER_REQUEST_ID",
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "action_id": "display_gif_animation",
    "animation_info": {
      "frame_count": 1,
      "frame_delay": 100,
      "loop_count": 0,
      "width": 16,
      "height": 16,
      "total_pixels": 256
    },
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "id": 4
}
```

### 5. `convert_image_to_pixels` - Convert Image

**Purpose**: Convert base64 image to pixel matrix for display

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "convert_image_to_pixels",
  "params": {
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "target_width": 8,
    "target_height": 8,
    "resize_method": "nearest"
  },
  "id": 5
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "pixel_matrix": [
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff", "#0000ff"]
    ],
    "width": 8,
    "height": 8,
    "original_size": {
      "width": 1,
      "height": 1
    },
    "resize_method": "nearest",
    "total_pixels": 64,
    "format_info": {
      "original_mode": "RGB",
      "converted_mode": "RGB",
      "pixel_format": "hex_colors"
    }
  },
  "id": 5
}
```

## ⚙️ Pixel Art Formats

### 🎨 2D Array Format

Pixel patterns as arrays of hex color codes:

```json
[
  ["#FF0000", "#00FF00", "#0000FF"],
  ["#FFFF00", "#FF00FF", "#00FFFF"],
  ["#FFFFFF", "#000000", "#808080"]
]
```

### 🖼️ Base64 Image Format

Convert any image to pixel art:

```json
{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
  "target_width": 16,
  "target_height": 16
}
```

### 🎬 GIF Animation Format

Animated pixel art with frame control:

```json
{
  "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
  "frame_delay": 100,
  "loop_count": 0,
  "target_width": 16,
  "target_height": 16
}
```

## 🎯 Pixel Art Examples

### 😊 Smiley Face (8x8)
```json
[
  ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
  ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
  ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"],
  ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
  ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"],
  ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"],
  ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
  ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]
]
```

### ❤️ Heart Shape (8x8)
```json
[
  ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
  ["#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000"],
  ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
  ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
  ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
  ["#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000"],
  ["#000000", "#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000", "#000000"],
  ["#000000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#000000"]
]
```

## ☁️ Tencent Cloud IoT Integration

### Device Action Protocol

The service uses Tencent Cloud IoT Explorer for device communication:

- **Action**: `display_pixel_image` - Display static pixel image
- **Action**: `display_gif_animation` - Display animated GIF

### Message Format

Device actions follow this standardized format:

```json
{
  "action": "display_pixel_image",
  "width": 16,
  "height": 16,
  "pixel_data": [
    ["#FF0000", "#00FF00"],
    ["#0000FF", "#FFFFFF"]
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Security & Authentication

- **Protocol**: HTTPS API calls to Tencent Cloud IoT Explorer
- **Authentication**: STS temporary credentials with limited permissions
- **Authorization**: Device-specific access control via session policies
- **Encryption**: TLS 1.2+ with end-to-end encryption

### Environment Configuration

Required environment variables:

```bash
export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/IoTDeviceRole"
export TC_SECRET_ID="AKID_PLACEHOLDER_SECRET_ID"  # Optional in CVM/TKE
export TC_SECRET_KEY="PLACEHOLDER_SECRET_KEY"     # Optional in CVM/TKE
export DEFAULT_REGION="ap-guangzhou"
```

## 🧪 Testing & Validation

### Automated Test Suite

Run the complete test suite:

```bash
# Individual tests
./test_help.sh                    # Test help method
./test_issue_sts.sh              # Test STS credential issuing
./test_send_pixel_image.sh       # Test pixel image sending
./test_send_gif_animation.sh     # Test GIF animation sending
./test_convert_image.sh          # Test image conversion

# All tests via build script
python build.py test
```

### Manual Testing

```bash
# Start interactive server
python mcp_server.py

# Test with curl
curl -X POST http://localhost:8000/help
```

## 🏗️ Build & Deployment

### Build Executable

```bash
# Build standalone executable
python build.py build

# Build with PyInstaller
python build_exec.sh
```

### Docker Deployment

```bash
# Build Docker image
docker build -t pixelmug-mcp .

# Run container
docker run -p 8000:8000 \
  -e IOT_ROLE_ARN="your-role-arn" \
  -e TC_SECRET_ID="your-secret-id" \
  -e TC_SECRET_KEY="your-secret-key" \
  pixelmug-mcp
```

## 📚 Examples

Check the `examples/` directory for:

- `example_client.py` - Python client implementation
- `pixel_art_demo.py` - Pixel art creation examples
- `image_conversion_demo.py` - Image processing examples
- `bluetooth_bridge.py` - Bluetooth integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/AIO-2030/mcp_pixel_mug/issues)
- **Documentation**: [Wiki](https://github.com/AIO-2030/mcp_pixel_mug/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/AIO-2030/mcp_pixel_mug/discussions)

## 🔗 Related Projects

- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP specification
- [Tencent Cloud IoT Explorer](https://cloud.tencent.com/product/iotexplorer) - IoT platform
- [PixelMug Hardware](https://github.com/AIO-2030/pixelmug-hardware) - Hardware schematics
