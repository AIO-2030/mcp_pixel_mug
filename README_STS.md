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

## 相关文档

- [腾讯云STS文档](https://cloud.tencent.com/document/product/598)
- [腾讯云IoT Explorer文档](https://cloud.tencent.com/document/product/1081)
- [CAM角色管理](https://cloud.tencent.com/document/product/598/19422)
- [设备影子服务](https://cloud.tencent.com/document/product/1081/50280)
