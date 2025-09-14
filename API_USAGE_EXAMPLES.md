# API Usage Examples

This document provides practical examples for using the PixelMug MCP Server API.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   ```bash
   export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/IoTDeviceRole"
   export TC_SECRET_ID="AKID_PLACEHOLDER_SECRET_ID"  # Optional for CVM/TKE
   export TC_SECRET_KEY="PLACEHOLDER_SECRET_KEY"    # Optional for CVM/TKE
   export DEFAULT_REGION="ap-guangzhou"
   ```
3. Start the service: `python start_server.py`

## API Endpoints

### 1. Help Endpoint

Get service information and available methods:

```bash
curl -X GET "http://localhost:8000/"
```

Response:
```json
{
  "service": "PixelMug IoT STS Service",
  "version": "2.0.0",
  "description": "Tencent Cloud IoT Device Control and STS Service",
  "features": [
    "STS temporary credential issuing",
    "Pixel image transmission to IoT devices",
    "GIF animation transmission to IoT devices",
    "Device authorization and validation"
  ]
}
```

### 2. STS Credentials Endpoint

Issue temporary credentials for device access:

```bash
curl -X GET "http://localhost:8000/sts/issue?pid=ABC123DEF&dn=mug_001&user_id=default_user"
```

Response:
```json
{
  "code": 0,
  "message": "STS credentials issued successfully",
  "data": {
    "tmpSecretId": "AKID_PLACEHOLDER_SECRET_ID",
    "tmpSecretKey": "PLACEHOLDER_SECRET_KEY",
    "token": "PLACEHOLDER_TOKEN",
    "expiration": "2023-12-25T10:15:30Z",
    "region": "ap-guangzhou",
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "issued_at": "2023-12-25T10:00:30Z"
  }
}
```

### 3. Send Pixel Image Endpoint

Send pixel image to device:

```bash
curl -X POST "http://localhost:8000/pixel/send" \
  -H "Content-Type: application/json" \
  -d '{
    "pid": "ABC123DEF",
    "dn": "mug_001",
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "width": 16,
    "height": 16,
    "user_id": "default_user"
  }'
```

Response:
```json
{
  "code": 0,
  "message": "Pixel image sent successfully",
  "data": {
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
    "timestamp": "2023-12-25T10:15:30Z"
  }
}
```

### 4. Send GIF Animation Endpoint

Send animated GIF to device:

```bash
curl -X POST "http://localhost:8000/gif/send" \
  -H "Content-Type: application/json" \
  -d '{
    "pid": "ABC123DEF",
    "dn": "mug_001",
    "gif_data": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
    "frame_delay": 100,
    "loop_count": 0,
    "width": 16,
    "height": 16,
    "user_id": "default_user"
  }'
```

## MCP JSON-RPC Examples

### 1. Help Request

```json
{
  "jsonrpc": "2.0",
  "method": "help",
  "params": {},
  "id": 1
}
```

### 2. Issue STS Credentials

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

### 3. Send Pixel Image

```json
{
  "jsonrpc": "2.0",
  "method": "send_pixel_image",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001",
    "image_data": [
      ["#FF0000", "#00FF00"],
      ["#0000FF", "#FFFFFF"]
    ],
    "target_width": 2,
    "target_height": 2
  },
  "id": 3
}
```

### 4. Send GIF Animation

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

### 5. Convert Image to Pixels

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

## Python Client Examples

### Basic Client

```python
import json
import requests

class PixelMugClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def call_method(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        response = requests.post(f"{self.base_url}/mcp", json=payload)
        return response.json()
    
    def get_help(self):
        return self.call_method("help", {})
    
    def issue_sts(self, product_id, device_name):
        return self.call_method("issue_sts", {
            "product_id": product_id,
            "device_name": device_name
        })
    
    def send_pixel_image(self, product_id, device_name, image_data, width=16, height=16):
        return self.call_method("send_pixel_image", {
            "product_id": product_id,
            "device_name": device_name,
            "image_data": image_data,
            "target_width": width,
            "target_height": height
        })

# Usage
client = PixelMugClient()

# Get help
help_info = client.get_help()
print(json.dumps(help_info, indent=2))

# Issue STS credentials
sts_result = client.issue_sts("ABC123DEF", "mug_001")
print(json.dumps(sts_result, indent=2))

# Send pixel image
pixel_data = [
    ["#FF0000", "#00FF00"],
    ["#0000FF", "#FFFFFF"]
]
result = client.send_pixel_image("ABC123DEF", "mug_001", pixel_data, 2, 2)
print(json.dumps(result, indent=2))
```

### Advanced Client with Error Handling

```python
import json
import requests
import time
from typing import Dict, Any, Optional

class AdvancedPixelMugClient:
    def __init__(self, base_url="http://localhost:8000", timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": int(time.time() * 1000)  # Use timestamp as ID
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Network error: {str(e)}"
                },
                "id": payload["id"]
            }
    
    def get_help(self) -> Dict[str, Any]:
        """Get service help information"""
        return self._make_request("help", {})
    
    def issue_sts(self, product_id: str, device_name: str) -> Dict[str, Any]:
        """Issue STS credentials for device access"""
        return self._make_request("issue_sts", {
            "product_id": product_id,
            "device_name": device_name
        })
    
    def send_pixel_image(self, product_id: str, device_name: str, 
                        image_data: Any, width: int = 16, height: int = 16) -> Dict[str, Any]:
        """Send pixel image to device"""
        return self._make_request("send_pixel_image", {
            "product_id": product_id,
            "device_name": device_name,
            "image_data": image_data,
            "target_width": width,
            "target_height": height
        })
    
    def send_gif_animation(self, product_id: str, device_name: str, 
                          gif_data: Any, frame_delay: int = 100, 
                          loop_count: int = 0, width: int = 16, height: int = 16) -> Dict[str, Any]:
        """Send GIF animation to device"""
        return self._make_request("send_gif_animation", {
            "product_id": product_id,
            "device_name": device_name,
            "gif_data": gif_data,
            "frame_delay": frame_delay,
            "loop_count": loop_count,
            "target_width": width,
            "target_height": height
        })
    
    def convert_image_to_pixels(self, image_data: str, width: int = 16, 
                               height: int = 16, resize_method: str = "nearest") -> Dict[str, Any]:
        """Convert base64 image to pixel matrix"""
        return self._make_request("convert_image_to_pixels", {
            "image_data": image_data,
            "target_width": width,
            "target_height": height,
            "resize_method": resize_method
        })

# Usage example
if __name__ == "__main__":
    client = AdvancedPixelMugClient()
    
    # Test connection
    help_result = client.get_help()
    if "error" in help_result:
        print(f"Error: {help_result['error']['message']}")
    else:
        print("Service is running!")
        print(f"Version: {help_result['result']['version']}")
    
    # Issue STS credentials
    sts_result = client.issue_sts("ABC123DEF", "mug_001")
    if "error" not in sts_result:
        print("STS credentials issued successfully")
    else:
        print(f"STS error: {sts_result['error']['message']}")
    
    # Send pixel art
    smiley_face = [
        ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
        ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
        ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"],
        ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
        ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"],
        ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"],
        ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
        ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]
    ]
    
    result = client.send_pixel_image("ABC123DEF", "mug_001", smiley_face, 8, 8)
    if "error" not in result:
        print("Pixel image sent successfully!")
    else:
        print(f"Send error: {result['error']['message']}")
```

## Error Handling

### Common Error Codes

- `-32600`: Invalid Request
- `-32601`: Method Not Found
- `-32602`: Invalid Params
- `-32603`: Internal Error
- `-32700`: Parse Error

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params: Missing required parameter: product_id"
  },
  "id": 1
}
```

### Handling Errors in Python

```python
def handle_response(response):
    if "error" in response:
        error_code = response["error"]["code"]
        error_message = response["error"]["message"]
        
        if error_code == -32601:
            print(f"Method not found: {error_message}")
        elif error_code == -32602:
            print(f"Invalid parameters: {error_message}")
        elif error_code == -32603:
            print(f"Internal server error: {error_message}")
        else:
            print(f"Unknown error ({error_code}): {error_message}")
        
        return False
    else:
        print("Success!")
        return True

# Usage
result = client.get_help()
if handle_response(result):
    print(json.dumps(result["result"], indent=2))
```

## Testing

### Unit Tests

```python
import unittest
from pixelmug_client import AdvancedPixelMugClient

class TestPixelMugClient(unittest.TestCase):
    def setUp(self):
        self.client = AdvancedPixelMugClient()
    
    def test_help(self):
        result = self.client.get_help()
        self.assertNotIn("error", result)
        self.assertEqual(result["result"]["service"], "mcp_pixel_mug")
    
    def test_convert_image(self):
        # Test with 1x1 pixel PNG
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        result = self.client.convert_image_to_pixels(image_data, 8, 8)
        self.assertNotIn("error", result)
        self.assertEqual(len(result["result"]["pixel_matrix"]), 8)

if __name__ == "__main__":
    unittest.main()
```

### Integration Tests

```bash
#!/bin/bash
# test_integration.sh

echo "Testing PixelMug MCP Server Integration..."

# Test help endpoint
echo "1. Testing help endpoint..."
curl -s http://localhost:8000/ | jq '.service'

# Test MCP help method
echo "2. Testing MCP help method..."
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"help","params":{},"id":1}' | jq '.result.service'

# Test image conversion
echo "3. Testing image conversion..."
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"convert_image_to_pixels",
    "params":{
      "image_data":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
      "target_width":4,
      "target_height":4
    },
    "id":2
  }' | jq '.result.pixel_matrix | length'

echo "Integration tests completed!"
```

## Performance Tips

1. **Connection Pooling**: Use a session object for multiple requests
2. **Timeout Settings**: Set appropriate timeouts for your use case
3. **Error Retry**: Implement exponential backoff for transient errors
4. **Batch Operations**: Group multiple operations when possible
5. **Image Optimization**: Resize images before sending to reduce payload size

## Security Best Practices

1. **Environment Variables**: Store credentials in environment variables
2. **HTTPS**: Always use HTTPS in production
3. **Input Validation**: Validate all input parameters
4. **Rate Limiting**: Implement rate limiting for API calls
5. **Logging**: Log all API calls for audit purposes
