# PixelMug MCP Service API 文档

## 概述

PixelMug MCP Service 是一个基于 stdio 模式的 JSON-RPC 2.0 服务，用于控制智能屏显水杯设备。服务默认使用子账号密钥调用腾讯云 IoT 服务，无需 STS 临时凭证。

## 服务信息

- **服务名称**: mcp_pixel_mug
- **版本**: 2.0.0
- **协议**: JSON-RPC 2.0 over stdio
- **认证方式**: 子账号密钥 (direct_subaccount)

## 环境要求

### 必需环境变量
```bash
export TC_SECRET_ID="your_subaccount_secret_id"
export TC_SECRET_KEY="your_subaccount_secret_key"
export DEFAULT_REGION="ap-guangzhou"
```

### 可选环境变量
```bash
export TEST_PRODUCT_ID="H3PI4FBTV5"
export TEST_DEVICE_NAME="3CDC7580F950"
```

## API 方法

### 1. help - 获取服务帮助信息

**调用场景**: 获取服务基本信息和支持的方法列表

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "help",
  "params": {},
  "id": 1
}
```

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "service": "mcp_pixel_mug",
    "version": "2.0.0",
    "description": "PixelMug Smart Mug Tencent Cloud IoT Control Interface (Alaya MCP)",
    "methods": [...],
    "supported_actions": [...],
    "pixel_art_examples": {...},
    "pixel_art_formats": {...}
  },
  "id": 1
}
```

### 2. get_device_status - 查询设备状态

**调用场景**: 查询设备的在线状态、基本信息等

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "get_device_status",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950"
  },
  "id": 2
}
```

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "device_status": {
      "online": false,
      "last_online_time": 1760982349,
      "last_offline_time": null,
      "client_ip": null,
      "device_cert": "",
      "device_secret": null,
      "enable_state": 1,
      "device_type": "设备",
      "product_name": "智能屏显水杯"
    },
    "timestamp": "2025-10-21T09:03:38.441762Z"
  },
  "id": 2
}
```

### 3. send_display_text - 发送文本到设备屏幕

**调用场景**: 在智能水杯屏幕上显示文本信息

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "send_display_text",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "text": "Hello World"
  },
  "id": 3
}
```

**参数说明**:
- `product_id` (string, 必需): 产品ID
- `device_name` (string, 必需): 设备名称
- `text` (string, 必需): 要显示的文本，最大200字符，允许空字符串

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "client_token": "",
    "call_status": "FailedOperation.ActionUnreachable",
    "request_id": "73fe5968-031f-4c19-9366-6e1122840bdf",
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "action_id": "run_display_text",
    "text_info": {
      "text": "Hello World",
      "length": 11,
      "max_length": 200
    },
    "credential_type": "direct_subaccount",
    "timestamp": "2025-10-21T09:03:43.525049Z"
  },
  "id": 3
}
```

### 4. send_pixel_image - 发送像素图像到设备

**调用场景**: 在设备屏幕上显示像素图像（会转换为单帧GIF）

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "send_pixel_image",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "image_data": [
      ["#FF0000", "#00FF00"],
      ["#0000FF", "#FFFF00"]
    ],
    "target_width": 2,
    "target_height": 2,
    "use_cos": false
  },
  "id": 4
}
```

**参数说明**:
- `product_id` (string, 必需): 产品ID
- `device_name` (string, 必需): 设备名称
- `image_data` (array/string, 必需): 像素数据，支持以下格式：
  - 2D数组: `[["#FF0000", "#00FF00"], ["#0000FF", "#FFFF00"]]`
  - Base64图像: `"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="`
  - 调色板格式: `{"palette": ["#ffffff", "#ff0000"], "pixels": [[0,1], [1,0]]}`
- `target_width` (int, 可选): 目标宽度，默认16
- `target_height` (int, 可选): 目标高度，默认16
- `use_cos` (bool, 可选): 是否使用COS上传，默认true
- `ttl_sec` (int, 可选): COS签名URL有效期，默认900秒

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "client_token": "",
    "call_status": "FailedOperation.ActionUnreachable",
    "request_id": "6d9d6f59-cffc-43cc-b545-374cf73019fc",
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "action_id": "run_display_gif",
    "image_info": {
      "width": 2,
      "height": 2,
      "total_pixels": 4,
      "converted_to_gif": true,
      "frame_count": 1
    },
    "delivery_method": "direct",
    "timestamp": "2025-10-21T09:03:50.316598Z"
  },
  "id": 4
}
```

### 5. send_gif_animation - 发送GIF动画到设备

**调用场景**: 在设备屏幕上显示GIF动画

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "send_gif_animation",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "gif_data": [
      {
        "frame_index": 0,
        "pixel_matrix": [
          ["#FF0000", "#00FF00"],
          ["#0000FF", "#FFFF00"]
        ],
        "duration": 500
      },
      {
        "frame_index": 1,
        "pixel_matrix": [
          ["#00FF00", "#FF0000"],
          ["#FFFF00", "#0000FF"]
        ],
        "duration": 500
      }
    ],
    "frame_delay": 500,
    "loop_count": 1,
    "target_width": 2,
    "target_height": 2,
    "use_cos": false
  },
  "id": 5
}
```

**参数说明**:
- `product_id` (string, 必需): 产品ID
- `device_name` (string, 必需): 设备名称
- `gif_data` (array/string, 必需): GIF数据，支持以下格式：
  - 帧数组: `[{"frame_index": 0, "pixel_matrix": [...], "duration": 500}]`
  - Base64 GIF: `"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"`
  - 调色板格式: `{"palette": [...], "frames": [...]}`
- `frame_delay` (int, 可选): 帧间延迟(毫秒)，默认100
- `loop_count` (int, 可选): 循环次数，0表示无限循环，默认0
- `target_width` (int, 可选): 目标宽度，默认16
- `target_height` (int, 可选): 目标高度，默认16
- `use_cos` (bool, 可选): 是否使用COS上传，默认true
- `ttl_sec` (int, 可选): COS签名URL有效期，默认900秒
- `sta_port` (int, 可选): 设备通信端口，默认80

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "client_token": "",
    "call_status": "FailedOperation.ActionUnreachable",
    "request_id": "dc28a66d-cf52-4a88-94b2-a24c6ae3333d",
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "action_id": "run_display_gif",
    "animation_info": {
      "frame_count": 2,
      "frame_delay": 500,
      "loop_count": 1,
      "width": 2,
      "height": 2,
      "total_pixels": 4
    },
    "delivery_method": "direct",
    "timestamp": "2025-10-21T09:03:56.764074Z"
  },
  "id": 5
}
```

### 6. convert_image_to_pixels - 转换图像为像素矩阵

**调用场景**: 将Base64编码的图像转换为像素矩阵，用于后续显示

**请求格式**:
```json
{
  "jsonrpc": "2.0",
  "method": "convert_image_to_pixels",
  "params": {
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "target_width": 2,
    "target_height": 2,
    "resize_method": "nearest"
  },
  "id": 6
}
```

**参数说明**:
- `image_data` (string, 必需): Base64编码的图像数据
- `target_width` (int, 可选): 目标宽度，默认16
- `target_height` (int, 可选): 目标高度，默认16
- `resize_method` (string, 可选): 缩放方法，可选值：nearest/bilinear/bicubic，默认nearest

**响应格式**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "pixel_matrix": [
      ["#0000ff", "#0000ff"],
      ["#0000ff", "#0000ff"]
    ],
    "width": 2,
    "height": 2,
    "original_size": {
      "width": 1,
      "height": 1
    },
    "resize_method": "nearest",
    "total_pixels": 4,
    "format_info": {
      "original_mode": "RGB",
      "converted_mode": "RGB",
      "pixel_format": "hex_colors"
    }
  },
  "id": 6
}
```

## 像素艺术格式

### 1. 2D数组格式
```json
[
  ["#FF0000", "#00FF00", "#0000FF"],
  ["#FFFF00", "#FF00FF", "#00FFFF"],
  ["#FFFFFF", "#000000", "#808080"]
]
```

### 2. 调色板格式
```json
{
  "title": "sample_image",
  "description": "Converted from sample_image.jpg",
  "width": 4,
  "height": 4,
  "palette": ["#ffffff", "#ff0000", "#00ff00", "#0000ff"],
  "pixels": [
    [0, 1, 1, 0],
    [1, 2, 2, 1],
    [1, 3, 3, 1],
    [0, 1, 1, 0]
  ]
}
```

### 3. GIF帧格式
```json
[
  {
    "frame_index": 0,
    "pixel_matrix": [
      ["#FF0000", "#00FF00"],
      ["#0000FF", "#FFFF00"]
    ],
    "duration": 500
  },
  {
    "frame_index": 1,
    "pixel_matrix": [
      ["#00FF00", "#FF0000"],
      ["#FFFF00", "#0000FF"]
    ],
    "duration": 500
  }
]
```

## 错误处理

### 错误响应格式
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error: [TencentCloudSDKException] code:ResourceNotFound.DeviceNotExist message:设备未创建或是已删除"
  },
  "id": 1
}
```

### 常见错误码
- `-32600`: Invalid Request - 请求格式错误
- `-32601`: Method not found - 方法不存在
- `-32602`: Invalid params - 参数错误
- `-32603`: Internal error - 内部错误

### 设备相关错误
- `ResourceNotFound.DeviceNotExist`: 设备不存在
- `InvalidParameter.ActionInputParamsInvalid`: 动作参数不正确
- `FailedOperation.ActionUnreachable`: 设备离线，动作无法到达

## 调用示例

### Python 调用示例
```python
import json
import subprocess

def call_mcp_service(method, params, request_id=1):
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    
    # 通过stdio调用服务
    process = subprocess.Popen(
        ["python", "stdio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=json.dumps(request))
    
    if process.returncode == 0:
        return json.loads(stdout)
    else:
        raise Exception(f"Service error: {stderr}")

# 查询设备状态
result = call_mcp_service("get_device_status", {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950"
})
print(result)

# 发送文本
result = call_mcp_service("send_display_text", {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "text": "Hello World"
})
print(result)
```

### Node.js 调用示例
```javascript
const { spawn } = require('child_process');

function callMCPService(method, params, requestId = 1) {
    return new Promise((resolve, reject) => {
        const request = {
            jsonrpc: "2.0",
            method: method,
            params: params,
            id: requestId
        };
        
        const process = spawn('python', ['stdio_server.py'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let stdout = '';
        let stderr = '';
        
        process.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        process.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        process.on('close', (code) => {
            if (code === 0) {
                try {
                    resolve(JSON.parse(stdout));
                } catch (e) {
                    reject(new Error(`Parse error: ${e.message}`));
                }
            } else {
                reject(new Error(`Service error: ${stderr}`));
            }
        });
        
        process.stdin.write(JSON.stringify(request));
        process.stdin.end();
    });
}

// 使用示例
callMCPService("get_device_status", {
    product_id: "H3PI4FBTV5",
    device_name: "3CDC7580F950"
}).then(result => {
    console.log(result);
}).catch(error => {
    console.error(error);
});
```

## 注意事项

1. **设备状态**: 设备离线时，动作调用会返回 `FailedOperation.ActionUnreachable`，但API调用本身是成功的
2. **像素图像**: 像素图像会自动转换为单帧GIF通过 `run_display_gif` action发送
3. **端口设置**: COS URL为HTTPS时自动使用443端口，HTTP时使用80端口
4. **子账号密钥**: 服务默认使用子账号密钥，无需STS临时凭证
5. **错误处理**: 建议在调用方实现重试机制和错误处理逻辑

## 测试工具

项目提供了以下测试脚本：
- `test_stdio_simple.py`: 快速功能测试
- `test_stdio_mode.py`: 完整功能测试
- `demo_stdio_mode.py`: 功能演示脚本

运行测试：
```bash
# 快速测试
python test_stdio_simple.py

# 完整测试
python test_stdio_mode.py

# 功能演示
python demo_stdio_mode.py
```
