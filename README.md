# 🎨 PixelMug MCP Server

A Model Context Protocol (MCP) server for controlling PixelMug smart mugs via Tencent Cloud IoT Explorer. This service provides pixel art display, GIF animation, image conversion, and cloud storage capabilities for IoT-connected smart mugs with ALAYA network optimization.

## ✨ Features

- **🎨 Pixel Art Display**: Send custom pixel patterns to mug displays
- **🎬 GIF Animation**: Display animated GIFs with frame control
- **🖼️ Image Conversion**: Convert any image to pixel art format
- **🎨 Palette Format**: Support for efficient palette-based pixel art (up to 16 colors)
- **☁️ Tencent Cloud IoT**: Secure device communication via IoT Explorer
- **📦 COS Integration**: Cloud storage with pre-signed URLs for asset delivery
- **🔐 STS Authentication**: Temporary credentials for secure access
- **📱 MCP Protocol**: Standardized JSON-RPC interface
- **🌐 ALAYA Network**: Optimized for ALAYA network transmission

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
export COS_BUCKET="pixelmug-assets"               # COS bucket name
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
    "version": "2.1.0",
    "description": "PixelMug Smart Mug Tencent Cloud IoT Control Interface with COS Integration and ALAYA Network Support",
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
        "description": "Send pixel image to device via Tencent Cloud IoT with optional COS upload",
        "params": {
          "product_id": "Product ID",
          "device_name": "Device name",
          "image_data": "Base64 encoded image, pixel matrix, or palette format",
          "target_width": "Target width (optional, default: 16)",
          "target_height": "Target height (optional, default: 16)",
          "use_cos": "Enable COS upload (optional, default: True)",
          "ttl_sec": "COS signed URL TTL in seconds (optional, default: 900)"
        }
      },
      {
        "name": "send_gif_animation",
        "description": "Send GIF pixel animation to device via Tencent Cloud IoT with optional COS upload",
        "params": {
          "product_id": "Product ID",
          "device_name": "Device name",
          "gif_data": "Base64 encoded GIF, frame array, or palette format",
          "frame_delay": "Delay between frames in ms (optional, default: 100)",
          "loop_count": "Number of loops (optional, default: 0 for infinite)",
          "target_width": "Target width (optional, default: 16)",
          "target_height": "Target height (optional, default: 16)",
          "use_cos": "Enable COS upload (optional, default: True)",
          "ttl_sec": "COS signed URL TTL in seconds (optional, default: 900)"
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
      "base64": "Base64 encoded image data (PNG/JPEG)",
      "palette_based": "Palette-based format with color indices: {\"palette\": [\"#ffffff\", \"#ff0000\"], \"pixels\": [[0,1], [1,0]]}"
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

### 6. `get_device_status` - Query Device Status

**Purpose**: Query device online status and basic information

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "get_device_status",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001"
  },
  "id": 6
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "device_info": {
      "product_id": "ABC123DEF",
      "device_name": "mug_001",
      "is_online": true,
      "last_seen": 1704067200,
      "connection_status": "connected",
      "ip_address": "192.168.1.100",
      "signal_strength": -45,
      "battery_level": 85
    },
    "timestamp": 1704067200,
    "request_id": "status_1704067200"
  },
  "id": 6
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

### 🎨 Palette-Based Format (ALAYA Network Optimized)

Efficient format using color indices for network transmission:

```json
{
  "title": "sample_image",
  "description": "Converted from sample_image.jpg",
  "width": 32,
  "height": 32,
  "palette": [
    "#ffffff", "#ff0000", "#00ff00", "#0000ff",
    "#ffff00", "#ff00ff", "#00ffff", "#808080",
    "#000000", "#ffa500", "#800080", "#008000",
    "#ffc0cb", "#a52a2a", "#c0c0c0", "#808000"
  ],
  "pixels": [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ]
}
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

### 🎬 GIF Animation Formats

#### Traditional Frame Array
```json
[
  {
    "frame_index": 0,
    "pixel_matrix": [
      ["#FF0000", "#00FF00"],
      ["#0000FF", "#FFFFFF"]
    ],
    "duration": 100
  }
]
```

#### Palette-Based Animation
```json
{
  "title": "animated_heart",
  "width": 8,
  "height": 8,
  "palette": ["#000000", "#ff0000", "#ffffff"],
  "frame_delay": 200,
  "loop_count": 3,
  "frames": [
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0]
      ],
      "duration": 200
    }
  ]
}
```

## 📦 COS Integration

### Cloud Storage Features

- **Asset Upload**: Automatic upload of pixel art and GIF animations to COS
- **Pre-signed URLs**: Generate secure, time-limited download links
- **Metadata Storage**: Rich metadata for auditing and debugging
- **Cache Optimization**: Immutable objects with long-term caching
- **Fallback Support**: Automatic fallback to direct transmission if COS fails

### COS Key Pattern

```
pmug/{deviceName}/{YYYYMM}/{assetId}-{sha8}.{ext}
```

Examples:
- `pmug/mug_001/202412/asset_1740990123-a1b2c3d4.json`
- `pmug/mug_001/202412/asset_1740990124-e5f6g7h8.gif`

### Content Types

- **Pixel JSON**: `application/vnd.pmug.pixel+json`
- **GIF Animation**: `image/gif`

### Usage

```python
# Enable COS upload (default)
result = mug_service.send_pixel_image(
    product_id="ABC123DEF",
    device_name="mug_001",
    image_data=pixel_matrix,
    use_cos=True,
    ttl_sec=900  # 15 minutes
)

# Disable COS (direct transmission)
result = mug_service.send_pixel_image(
    product_id="ABC123DEF",
    device_name="mug_001",
    image_data=pixel_matrix,
    use_cos=False
)
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

### 🎨 Palette-Based Smiley Face (4x4)
```json
{
  "title": "smiley_4x4",
  "width": 4,
  "height": 4,
  "palette": ["#000000", "#FFFF00", "#FFFFFF"],
  "pixels": [
    [0, 1, 1, 0],
    [1, 1, 1, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 0]
  ]
}
```

### 🎬 Palette-Based Animation
```json
{
  "title": "blinking_heart",
  "width": 6,
  "height": 6,
  "palette": ["#000000", "#ff0000", "#ffffff"],
  "frame_delay": 500,
  "loop_count": 3,
  "frames": [
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 0]
      ],
      "duration": 500
    },
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0],
        [0, 2, 2, 0, 2, 2],
        [2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2],
        [0, 2, 2, 2, 2, 0],
        [0, 0, 2, 2, 0, 0]
      ],
      "duration": 500
    }
  ]
}
```

## ☁️ Tencent Cloud IoT Integration

### Device Action Protocol

The service uses Tencent Cloud IoT Explorer for device communication:

- **Action**: `display_pixel_image` - Display static pixel image
- **Action**: `display_gif_animation` - Display animated GIF
- **Action**: `control.push_asset` - Push asset via COS with pre-signed URLs

### Message Formats

#### Direct Transmission
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

#### COS Asset Delivery
```json
{
  "method": "control.push_asset",
  "clientToken": "cmd_1740990123",
  "params": {
    "assetId": "asset_abc123",
    "type": "application/vnd.pmug.pixel+json",
    "url": "https://pixelmug-assets.cos.ap-guangzhou.myqcloud.com/pmug/mug_001/202412/asset_abc123-a1b2c3d4.json?sign=...",
    "bytes": 15360,
    "hash": "sha256:a1b2c3d4e5f6...",
    "width": 32,
    "height": 16,
    "loop": false,
    "expiresAt": 1740990423,
    "nonce": "d4b1..8f",
    "ts": 1740990123
  }
}
```

### Security & Authentication

- **Protocol**: HTTPS API calls to Tencent Cloud IoT Explorer
- **Authentication**: STS temporary credentials with limited permissions
- **Authorization**: Device-specific access control via session policies
- **Encryption**: TLS 1.2+ with end-to-end encryption
- **COS Security**: Pre-signed URLs with expiration and nonce validation

### Environment Configuration

Required environment variables:

```bash
export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/IoTDeviceRole"
export COS_BUCKET="pixelmug-assets"               # COS bucket name
export TC_SECRET_ID="AKID_PLACEHOLDER_SECRET_ID"  # Optional in CVM/TKE
export TC_SECRET_KEY="PLACEHOLDER_SECRET_KEY"     # Optional in CVM/TKE
export DEFAULT_REGION="ap-guangzhou"
```

### Dependencies

```bash
pip install tencentcloud-sdk-python-sts
pip install tencentcloud-sdk-python-iotexplorer
pip install tencentcloud-sdk-python-cos
pip install fastapi
pip install Pillow
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

# New feature tests
python test_cos_integration.py   # Test COS integration
python test_palette_format.py    # Test palette format support

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

### New Documentation

- `README_STS.md` - Complete STS and device protocol documentation
- `GIF_FORMATS.md` - Detailed GIF format support guide
- `INTEGRATION_SUMMARY.md` - COS integration implementation summary

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
