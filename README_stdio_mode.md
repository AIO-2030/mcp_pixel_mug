# stdio模式使用说明

## 概述

stdio模式已配置为默认使用子账号密钥调用腾讯云IoT服务，无需STS临时凭证，简化了调用流程。

## 主要修改

### 1. mug_service.py 修改
- `send_pixel_image()`: 默认 `use_direct_credentials=True`
- `send_gif_animation()`: 默认 `use_direct_credentials=True`
- `get_device_status()`: 默认 `use_direct_credentials=True`
- `send_display_text()`: 默认 `use_direct_credentials=True`

### 2. mcp_server.py 修改
- 所有IoT云调用方法都显式设置 `use_direct_credentials=True`
- 移除了STS凭证相关的参数传递

## 环境变量配置

### 必需的环境变量
```bash
export TC_SECRET_ID="your_subaccount_secret_id"
export TC_SECRET_KEY="your_subaccount_secret_key"
export DEFAULT_REGION="ap-guangzhou"
```

### 可选的环境变量
```bash
export TEST_PRODUCT_ID="H3PI4FBTV5"
export TEST_DEVICE_NAME="mug_001"
```

## 使用方法

### 1. 直接调用mug_service
```python
from mug_service import mug_service

# 查询设备状态（自动使用子账号密钥）
status = mug_service.get_device_status("H3PI4FBTV5", "mug_001")

# 发送文本（自动使用子账号密钥）
result = mug_service.send_display_text("H3PI4FBTV5", "mug_001", "Hello World")

# 发送像素图像（自动使用子账号密钥）
pixel_data = [
    ["#FF0000", "#00FF00"],
    ["#0000FF", "#FFFF00"]
]
result = mug_service.send_pixel_image("H3PI4FBTV5", "mug_001", pixel_data)
```

### 2. 通过stdio_server调用
```bash
# 启动stdio服务器
python stdio_server.py

# 发送JSON-RPC请求
echo '{"jsonrpc": "2.0", "method": "get_device_status", "params": {"product_id": "H3PI4FBTV5", "device_name": "mug_001"}, "id": 1}' | python stdio_server.py
```

## 测试脚本

### 1. 完整功能测试
```bash
python test_stdio_mode.py
```

### 2. 快速功能测试
```bash
python test_stdio_simple.py
```

## 支持的方法

### 设备控制方法
- `get_device_status`: 查询设备在线状态
- `send_display_text`: 发送文本到设备屏幕
- `send_pixel_image`: 发送像素图像到设备
- `send_gif_animation`: 发送GIF动画到设备

### 工具方法
- `convert_image_to_pixels`: 将base64图像转换为像素矩阵
- `help`: 获取服务帮助信息

## 注意事项

1. **子账号权限**: 确保子账号具有访问指定IoT产品的权限
2. **网络连接**: 确保能够访问腾讯云IoT Explorer API
3. **设备在线**: 测试时确保目标设备在线
4. **参数验证**: 所有方法都会进行参数验证，请提供正确的product_id和device_name

## 错误排查

### 常见错误
1. **权限不足**: 检查子账号是否有IoT产品访问权限
2. **设备不存在**: 确认product_id和device_name正确
3. **网络问题**: 检查网络连接和防火墙设置
4. **环境变量**: 确认TC_SECRET_ID和TC_SECRET_KEY设置正确

### 调试方法
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看详细日志
from mug_service import mug_service
result = mug_service.get_device_status("H3PI4FBTV5", "mug_001")
```

## 性能优势

使用子账号密钥的优势：
- **无需STS**: 避免了STS临时凭证的获取和刷新
- **响应更快**: 直接使用子账号密钥，减少API调用次数
- **配置简单**: 只需设置子账号密钥，无需配置STS角色
- **稳定性好**: 避免了STS凭证过期的问题
