# 腾讯云IoT STS临时凭证服务

本文档介绍如何使用腾讯云IoT Explorer STS临时凭证服务来控制PixelMug智能杯子。

## 概述

STS (Security Token Service) 是腾讯云提供的临时访问凭证服务，允许您为特定操作颁发具有有限权限的临时访问密钥，而无需暴露长期凭证。

## 环境配置

### 必需的环境变量

```bash
# 必填：CAM角色ARN
export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/IoTDeviceRole"

# 可选：腾讯云凭证（CVM/TKE环境下可省略）
export TC_SECRET_ID="AKID_PLACEHOLDER_SECRET_ID"
export TC_SECRET_KEY="PLACEHOLDER_SECRET_KEY"

# 可选：默认地域
export DEFAULT_REGION="ap-guangzhou"
```

### CAM角色配置

1. 在腾讯云控制台创建CAM角色
2. 配置信任策略，允许IoT服务承担该角色
3. 配置权限策略，限制只能访问特定设备

示例信任策略：
```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "principal": {
        "service": "iotcloud.tencentcloudapi.com"
      },
      "action": "sts:AssumeRole"
    }
  ]
}
```

示例权限策略：
```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "iotcloud:UpdateDeviceShadow",
        "iotcloud:PublishMessage"
      ],
      "resource": [
        "qcs::iotcloud:::productId/ABC123DEF/device/mug_001"
      ]
    }
  ]
}
```

## API使用

### 1. 颁发STS凭证

**请求**：
```json
{
  "jsonrpc": "2.0",
  "method": "issue_sts",
  "params": {
    "product_id": "ABC123DEF",
    "device_name": "mug_001"
  },
  "id": 1
}
```

**响应**：
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
  "id": 1
}
```

### 2. 使用STS凭证控制设备

获得STS凭证后，可以使用这些临时凭证调用腾讯云IoT Explorer API：

```python
from tencentcloud.iotexplorer.v20190423 import iotexplorer_client, models as iot_models
from tencentcloud.common import credential

# 使用STS凭证创建客户端
cred = credential.Credential(
    secret_id=sts_result["tmpSecretId"],
    secret_key=sts_result["tmpSecretKey"],
    token=sts_result["token"]
)

client = iotexplorer_client.IotexplorerClient(cred, "ap-guangzhou")

# 调用设备操作
req = iot_models.CallDeviceActionAsyncRequest()
params = {
    "ProductId": "ABC123DEF",
    "DeviceName": "mug_001",
    "ActionId": "display_pixel_image",
    "InputParams": json.dumps({
        "action": "display_pixel_image",
        "width": 16,
        "height": 16,
        "pixel_data": [
            ["#FF0000", "#00FF00"],
            ["#0000FF", "#FFFFFF"]
        ]
    })
}
req.from_json_string(json.dumps(params))
resp = client.CallDeviceActionAsync(req)
```

## 安全特性

### 1. 权限最小化

STS凭证只包含执行特定操作所需的最小权限：

- `iotcloud:UpdateDeviceShadow` - 更新设备影子
- `iotcloud:PublishMessage` - 发布消息到设备

### 2. 设备级访问控制

每个STS凭证只能访问指定的单个设备：

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "iotcloud:UpdateDeviceShadow",
        "iotcloud:PublishMessage"
      ],
      "resource": [
        "qcs::iotcloud:::productId/ABC123DEF/device/mug_001"
      ]
    }
  ]
}
```

### 3. 时间限制

STS凭证具有15分钟的有效期，过期后自动失效：

```json
{
  "tmpSecretId": "AKID_PLACEHOLDER_SECRET_ID",
  "tmpSecretKey": "PLACEHOLDER_SECRET_KEY",
  "token": "PLACEHOLDER_TOKEN",
  "expiration": "2024-01-01T12:00:00Z",  // 15分钟后过期
  "issued_at": "2024-01-01T11:45:00Z"
}
```

## 使用场景

### 1. Web应用集成

在Web应用中，前端可以请求STS凭证来控制用户的设备：

```javascript
// 前端请求STS凭证
const response = await fetch('/api/sts/issue', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: 'ABC123DEF',
    device_name: 'mug_001',
    user_id: 'user123'
  })
});

const stsData = await response.json();

// 使用STS凭证调用腾讯云API
const iotClient = new TencentCloudIoTClient({
  secretId: stsData.tmpSecretId,
  secretKey: stsData.tmpSecretKey,
  token: stsData.token,
  region: stsData.region
});
```

### 2. 移动应用

移动应用可以安全地控制用户设备，无需在应用中存储长期凭证：

```swift
// iOS Swift示例
func requestSTSCredentials(productId: String, deviceName: String) async throws -> STSCredentials {
    let url = URL(string: "https://api.pixelmug.com/sts/issue")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body = [
        "product_id": productId,
        "device_name": deviceName,
        "user_id": getCurrentUserId()
    ]
    
    request.httpBody = try JSONSerialization.data(withJSONObject: body)
    
    let (data, _) = try await URLSession.shared.data(for: request)
    let response = try JSONDecoder().decode(STSResponse.self, from: data)
    
    return response.data
}
```

### 3. 服务器端代理

服务器可以作为代理，为客户端颁发STS凭证：

```python
from flask import Flask, request, jsonify
from mug_service import mug_service

app = Flask(__name__)

@app.route('/api/device/<product_id>/<device_name>/control', methods=['POST'])
def control_device(product_id, device_name):
    # 验证用户权限
    user_id = request.headers.get('X-User-ID')
    if not mug_service._authorize(user_id, product_id, device_name):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # 颁发STS凭证
    sts_result = mug_service.issue_sts(product_id, device_name)
    
    # 返回STS凭证给客户端
    return jsonify({
        'credentials': sts_result,
        'endpoint': 'https://iotexplorer.tencentcloudapi.com'
    })
```

## 错误处理

### 常见错误

1. **权限不足**
```json
{
  "error": {
    "code": "UnauthorizedOperation",
    "message": "You are not authorized to perform this operation"
  }
}
```

2. **角色不存在**
```json
{
  "error": {
    "code": "InvalidParameter",
    "message": "Role does not exist"
  }
}
```

3. **设备不存在**
```json
{
  "error": {
    "code": "ResourceNotFound",
    "message": "Device not found"
  }
}
```

### 错误处理示例

```python
def handle_sts_error(error):
    error_code = error.get('code', 'Unknown')
    error_message = error.get('message', 'Unknown error')
    
    if error_code == 'UnauthorizedOperation':
        print("权限不足，请检查CAM角色配置")
    elif error_code == 'InvalidParameter':
        print("参数错误，请检查产品ID和设备名称")
    elif error_code == 'ResourceNotFound':
        print("设备不存在，请检查设备是否已注册")
    else:
        print(f"未知错误: {error_code} - {error_message}")

# 使用示例
try:
    result = mug_service.issue_sts("ABC123DEF", "mug_001")
    print("STS凭证颁发成功")
except Exception as e:
    if hasattr(e, 'response'):
        error_data = e.response.json()
        handle_sts_error(error_data.get('error', {}))
    else:
        print(f"请求失败: {str(e)}")
```

## 最佳实践

### 1. 凭证缓存

STS凭证有效期为15分钟，建议实现缓存机制：

```python
import time
from functools import lru_cache

class STSCredentialManager:
    def __init__(self):
        self.cache = {}
    
    def get_credentials(self, product_id, device_name):
        cache_key = f"{product_id}:{device_name}"
        
        if cache_key in self.cache:
            creds, timestamp = self.cache[cache_key]
            # 检查是否还有5分钟有效期
            if time.time() - timestamp < 600:  # 10分钟
                return creds
        
        # 颁发新凭证
        creds = mug_service.issue_sts(product_id, device_name)
        self.cache[cache_key] = (creds, time.time())
        return creds
```

### 2. 权限验证

在颁发STS凭证前，验证用户是否有权限访问设备：

```python
def issue_sts_with_authorization(user_id, product_id, device_name):
    # 验证用户权限
    if not mug_service._authorize(user_id, product_id, device_name):
        raise ValueError(f"User {user_id} has no permission to access device {product_id}/{device_name}")
    
    # 颁发STS凭证
    return mug_service.issue_sts(product_id, device_name)
```

### 3. 监控和日志

记录STS凭证的颁发和使用情况：

```python
import logging

logger = logging.getLogger(__name__)

def issue_sts_with_logging(product_id, device_name, user_id):
    logger.info(f"Issuing STS credentials for user {user_id}, device {product_id}/{device_name}")
    
    try:
        result = mug_service.issue_sts(product_id, device_name)
        logger.info(f"STS credentials issued successfully for {product_id}/{device_name}")
        return result
    except Exception as e:
        logger.error(f"Failed to issue STS credentials: {str(e)}")
        raise
```

## 故障排除

### 1. 凭证颁发失败

检查环境变量配置：
```bash
echo $IOT_ROLE_ARN
echo $TC_SECRET_ID
echo $TC_SECRET_KEY
echo $DEFAULT_REGION
```

### 2. 权限不足

检查CAM角色配置：
- 角色是否存在
- 信任策略是否正确
- 权限策略是否包含所需操作

### 3. 设备访问失败

检查设备状态：
- 设备是否已注册
- 产品ID是否正确
- 设备名称是否正确

### 4. 网络连接问题

检查网络连接：
```bash
curl -I https://sts.tencentcloudapi.com
curl -I https://iotexplorer.tencentcloudapi.com
```

## IoT COS Asset Delivery Protocol

This section describes the protocol for delivering assets (pixel images and GIF animations) to IoT devices via Tencent Cloud COS (Cloud Object Storage).

### Overview

The system uses a two-phase delivery approach:
1. **Asset Upload**: Assets are uploaded to COS with pre-signed URLs
2. **Device Notification**: IoT devices receive asset metadata via MQTT/Shadow

### Asset Storage Structure

#### COS Key Pattern
```
pmug/{deviceName}/{YYYYMM}/{assetId}-{sha8}.{ext}
```

**Examples:**
- `pmug/mug_001/202412/asset_1740990123-a1b2c3d4.json`
- `pmug/mug_001/202412/asset_1740990124-e5f6g7h8.gif`

#### Content Types
- **Pixel JSON**: `application/vnd.pmug.pixel+json`
- **GIF Animation**: `image/gif`

#### Object Metadata
```json
{
  "x-cos-meta-sha256": "a1b2c3d4e5f6...",
  "x-cos-meta-width": "32",
  "x-cos-meta-height": "16",
  "x-cos-meta-frames": "5",
  "x-cos-meta-asset-id": "asset_1740990123",
  "x-cos-meta-device-name": "mug_001",
  "x-cos-meta-product-id": "ABC123DEF"
}
```

#### Cache Headers
```
Cache-Control: public, max-age=31536000, immutable
Storage-Class: STANDARD
```

### IoT Device Payload Format

#### MQTT Topic
```
$shadow/operation/result/{productId}/{deviceName}
```

#### Payload Structure
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

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `method` | string | Always "control.push_asset" |
| `clientToken` | string | Unique command identifier |
| `assetId` | string | Unique asset identifier |
| `type` | string | MIME type of the asset |
| `url` | string | Pre-signed COS URL for download |
| `bytes` | integer | Size of the asset in bytes |
| `hash` | string | SHA256 hash with "sha256:" prefix |
| `width` | integer | Display width in pixels |
| `height` | integer | Display height in pixels |
| `loop` | boolean | Whether to loop (for animations) |
| `expiresAt` | integer | URL expiration timestamp (Unix) |
| `nonce` | string | Security nonce (8 hex chars) |
| `ts` | integer | Command timestamp (Unix) |

### Asset Data Formats

#### Pixel JSON Format
```json
{
  "kind": "pixel-json",
  "width": 32,
  "height": 16,
  "pixel_data": [
    ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF"],
    ["#FFFF00", "#FF00FF", "#00FFFF", "#000000"],
    ["#800000", "#008000", "#000080", "#808080"],
    ["#FFA500", "#800080", "#008080", "#C0C0C0"]
  ],
  "timestamp": "2024-12-20T10:30:00Z"
}
```

#### Palette-Based Format
```json
{
  "kind": "pixel-json",
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
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "timestamp": "2024-12-20T10:30:00Z"
}
```

#### GIF Animation Format
```json
{
  "kind": "gif",
  "frame_count": 5,
  "frames": [
    {
      "frame_index": 0,
      "pixel_matrix": [
        ["#FF0000", "#00FF00"],
        ["#0000FF", "#FFFFFF"]
      ],
      "duration": 100
    },
    {
      "frame_index": 1,
      "pixel_matrix": [
        ["#00FF00", "#FF0000"],
        ["#FFFFFF", "#0000FF"]
      ],
      "duration": 100
    }
  ],
  "frame_delay": 100,
  "loop_count": 0,
  "width": 16,
  "height": 16,
  "timestamp": "2024-12-20T10:30:00Z"
}
```

### Device Implementation Guide

#### 1. MQTT Message Handling

```c
// C/C++ example
typedef struct {
    char assetId[64];
    char type[64];
    char url[512];
    int bytes;
    char hash[128];
    int width;
    int height;
    bool loop;
    long expiresAt;
    char nonce[16];
    long ts;
} AssetPayload;

typedef struct {
    char title[64];
    int width;
    int height;
    char palette[16][8];  // Up to 16 colors, each 7 chars + null
    int palette_size;
    int pixels[32][32];   // Support up to 32x32
} PaletteAsset;

void handle_asset_message(const char* topic, const char* payload) {
    cJSON* json = cJSON_Parse(payload);
    cJSON* method = cJSON_GetObjectItem(json, "method");
    
    if (strcmp(method->valuestring, "control.push_asset") == 0) {
        cJSON* params = cJSON_GetObjectItem(json, "params");
        AssetPayload asset = parse_asset_payload(params);
        
        // Download and display asset
        download_and_display_asset(&asset);
    }
    
    cJSON_Delete(json);
}

// Parse palette-based asset data
void parse_palette_asset(cJSON* asset_data, PaletteAsset* palette_asset) {
    cJSON* title = cJSON_GetObjectItem(asset_data, "title");
    cJSON* width = cJSON_GetObjectItem(asset_data, "width");
    cJSON* height = cJSON_GetObjectItem(asset_data, "height");
    cJSON* palette = cJSON_GetObjectItem(asset_data, "palette");
    cJSON* pixels = cJSON_GetObjectItem(asset_data, "pixels");
    
    strcpy(palette_asset->title, title->valuestring);
    palette_asset->width = width->valueint;
    palette_asset->height = height->valueint;
    
    // Parse palette
    palette_asset->palette_size = cJSON_GetArraySize(palette);
    for (int i = 0; i < palette_asset->palette_size && i < 16; i++) {
        cJSON* color = cJSON_GetArrayItem(palette, i);
        strcpy(palette_asset->palette[i], color->valuestring);
    }
    
    // Parse pixels
    for (int y = 0; y < palette_asset->height; y++) {
        cJSON* row = cJSON_GetArrayItem(pixels, y);
        for (int x = 0; x < palette_asset->width; x++) {
            cJSON* pixel = cJSON_GetArrayItem(row, x);
            palette_asset->pixels[y][x] = pixel->valueint;
        }
    }
}
```

#### 2. Asset Download

```c
// Download asset from COS URL
int download_asset(const char* url, char* buffer, int max_size) {
    HTTPClient http;
    http.begin(url);
    
    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
        int len = http.getSize();
        if (len <= max_size) {
            http.getString().toCharArray(buffer, max_size);
            return len;
        }
    }
    
    http.end();
    return -1;
}
```

#### 3. Asset Validation

```c
// Validate asset integrity
bool validate_asset(const char* data, int len, const char* expected_hash) {
    char hash[65];
    sha256_hash(data, len, hash);
    
    // Compare with expected hash (skip "sha256:" prefix)
    return strcmp(hash, expected_hash + 7) == 0;
}
```

#### 4. Display Implementation

```c
// Display pixel matrix on LED screen
void display_pixel_matrix(int width, int height, char pixel_data[][8]) {
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            uint32_t color = hex_to_rgb(pixel_data[y][x]);
            set_pixel(x, y, color);
        }
    }
    refresh_display();
}

// Display palette-based pixel matrix
void display_palette_pixel_matrix(int width, int height, int pixel_indices[][32], char palette[][8], int palette_size) {
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int color_index = pixel_indices[y][x];
            if (color_index >= 0 && color_index < palette_size) {
                uint32_t color = hex_to_rgb(palette[color_index]);
                set_pixel(x, y, color);
            }
        }
    }
    refresh_display();
}

// Display GIF animation
void display_gif_animation(GifAnimation* gif) {
    for (int frame = 0; frame < gif->frame_count; frame++) {
        display_pixel_matrix(gif->width, gif->height, gif->frames[frame].pixel_matrix);
        delay(gif->frames[frame].duration);
        
        if (gif->loop_count > 0 && frame == gif->frame_count - 1) {
            frame = -1; // Reset to beginning
            gif->loop_count--;
        }
    }
}
```

### Security Considerations

#### 1. URL Validation
- Always validate the URL domain (should be `*.cos.*.myqcloud.com`)
- Check URL expiration time before downloading
- Verify nonce to prevent replay attacks

#### 2. Hash Verification
- Always verify SHA256 hash of downloaded content
- Reject assets with invalid hashes
- Implement timeout for download operations

#### 3. Memory Management
- Limit maximum asset size (e.g., 64KB)
- Implement proper memory cleanup
- Handle out-of-memory conditions gracefully

### Error Handling

#### Common Error Scenarios

1. **Download Timeout**
```c
#define DOWNLOAD_TIMEOUT_MS 10000
// Implement timeout handling in download function
```

2. **Invalid Hash**
```c
if (!validate_asset(data, len, expected_hash)) {
    log_error("Asset hash verification failed");
    return -1;
}
```

3. **URL Expired**
```c
if (current_timestamp() > asset->expiresAt) {
    log_error("Asset URL has expired");
    return -1;
}
```

4. **Memory Insufficient**
```c
if (asset_size > MAX_ASSET_SIZE) {
    log_error("Asset too large: %d bytes", asset_size);
    return -1;
}
```

### Performance Optimization

#### 1. Caching Strategy
- Cache frequently used assets locally
- Implement LRU cache for memory management
- Use asset hash as cache key

#### 2. Display Optimization
- Pre-process pixel data for faster rendering
- Use DMA for bulk pixel updates
- Implement double buffering for smooth animations

#### 3. Network Optimization
- Use HTTP/2 if supported
- Implement connection pooling
- Compress asset data when possible

### Testing and Debugging

#### 1. Unit Testing
```c
void test_asset_parsing() {
    const char* test_payload = "{\"method\":\"control.push_asset\",\"params\":{...}}";
    AssetPayload asset = parse_asset_payload(test_payload);
    
    assert(strcmp(asset.assetId, "asset_123") == 0);
    assert(asset.width == 16);
    assert(asset.height == 16);
}
```

#### 2. Integration Testing
- Test with various asset sizes
- Verify hash validation
- Test error conditions
- Validate display output

#### 3. Debug Logging
```c
#define DEBUG_LEVEL 1

#if DEBUG_LEVEL >= 1
    #define log_debug(fmt, ...) printf("[DEBUG] " fmt "\n", ##__VA_ARGS__)
#else
    #define log_debug(fmt, ...)
#endif
```

## 相关文档

- [腾讯云STS文档](https://cloud.tencent.com/document/product/598)
- [腾讯云IoT Explorer文档](https://cloud.tencent.com/document/product/1081)
- [CAM角色管理](https://cloud.tencent.com/document/product/598/19422)
- [设备影子服务](https://cloud.tencent.com/document/product/1081/50280)
