# PixelMug MCP Service 开发者提示词

## 系统概述

PixelMug MCP Service 是一个基于 stdio 模式的 JSON-RPC 2.0 服务，用于控制智能屏显水杯设备。服务使用子账号密钥直接调用腾讯云 IoT 服务，无需 STS 临时凭证。

## 核心特性

- **协议**: JSON-RPC 2.0 over stdio
- **认证**: 子账号密钥 (direct_subaccount)
- **设备支持**: 智能屏显水杯 (产品ID: H3PI4FBTV5)
- **主要功能**: 文本显示、像素图像显示、GIF动画显示

## 开发环境设置

### 1. 环境变量配置
```bash
# 必需的环境变量
export TC_SECRET_ID="your_subaccount_secret_id"
export TC_SECRET_KEY="your_subaccount_secret_key"
export DEFAULT_REGION="ap-guangzhou"

# 可选的环境变量
export TEST_PRODUCT_ID="H3PI4FBTV5"
export TEST_DEVICE_NAME="3CDC7580F950"
```

### 2. 服务启动
```bash
python stdio_server.py
```

## API 调用模式

### 标准调用流程
1. 构造 JSON-RPC 2.0 请求
2. 通过 stdin 发送到 stdio_server.py
3. 从 stdout 接收响应
4. 解析 JSON 响应

### 请求格式模板
```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": 1
}
```

### 响应格式模板
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "data": "..."
  },
  "id": 1
}
```

## 核心方法详解

### 1. 设备状态查询
**用途**: 检查设备在线状态和基本信息
**关键字段**: `online`, `device_type`, `product_name`
**调用场景**: 设备连接检查、状态监控

### 2. 文本显示
**用途**: 在设备屏幕上显示文本
**限制**: 最大200字符，支持空字符串
**调用场景**: 状态提示、消息通知

### 3. 像素图像显示
**用途**: 显示静态像素图像
**转换**: 自动转换为单帧GIF
**支持格式**: 2D数组、Base64图像、调色板格式
**调用场景**: 图标显示、简单图形

### 4. GIF动画显示
**用途**: 显示动态像素动画
**支持格式**: 帧数组、Base64 GIF、调色板格式
**参数**: 帧延迟、循环次数、尺寸
**调用场景**: 动画效果、动态提示

### 5. 图像转换
**用途**: 将Base64图像转换为像素矩阵
**缩放方法**: nearest/bilinear/bicubic
**调用场景**: 图像预处理、格式转换

## 像素数据格式规范

### 1. 2D数组格式 (推荐)
```json
[
  ["#FF0000", "#00FF00", "#0000FF"],
  ["#FFFF00", "#FF00FF", "#00FFFF"],
  ["#FFFFFF", "#000000", "#808080"]
]
```

### 2. 调色板格式 (节省空间)
```json
{
  "palette": ["#ffffff", "#ff0000", "#00ff00", "#0000ff"],
  "pixels": [
    [0, 1, 1, 0],
    [1, 2, 2, 1],
    [1, 3, 3, 1],
    [0, 1, 1, 0]
  ]
}
```

### 3. GIF帧格式 (动画)
```json
[
  {
    "frame_index": 0,
    "pixel_matrix": [["#FF0000", "#00FF00"]],
    "duration": 500
  }
]
```

## 错误处理策略

### 1. 常见错误类型
- **设备不存在**: `ResourceNotFound.DeviceNotExist`
- **设备离线**: `FailedOperation.ActionUnreachable`
- **参数错误**: `InvalidParameter.ActionInputParamsInvalid`
- **服务错误**: `-32603 Internal error`

### 2. 错误处理建议
- 实现重试机制
- 检查设备在线状态
- 验证参数格式
- 记录错误日志

### 3. 设备离线处理
设备离线时，API调用仍会成功，但 `call_status` 为 `FailedOperation.ActionUnreachable`。这是正常现象，表示请求已发送但设备无法接收。

## 开发最佳实践

### 1. 调用顺序建议
1. 先调用 `get_device_status` 检查设备状态
2. 根据设备状态决定是否发送控制命令
3. 使用 `convert_image_to_pixels` 预处理图像
4. 发送显示命令

### 2. 性能优化
- 使用调色板格式减少数据量
- 合理设置图像尺寸 (推荐16x16或更小)
- 避免频繁的状态查询

### 3. 调试技巧
- 使用 `help` 方法获取服务信息
- 检查响应中的 `credential_type` 确认认证方式
- 观察 `delivery_method` 了解传输方式

## 测试和验证

### 1. 单元测试
```bash
# 快速功能测试
python test_stdio_simple.py

# 完整功能测试
python test_stdio_mode.py
```

### 2. 手动测试
```bash
# 查询设备状态
echo '{"jsonrpc": "2.0", "method": "get_device_status", "params": {"product_id": "H3PI4FBTV5", "device_name": "3CDC7580F950"}, "id": 1}' | python stdio_server.py

# 发送文本
echo '{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "3CDC7580F950", "text": "Test"}, "id": 2}' | python stdio_server.py
```

### 3. 集成测试
- 验证所有方法调用
- 测试不同像素格式
- 验证错误处理
- 检查性能表现

## 部署注意事项

### 1. 环境要求
- Python 3.7+
- 腾讯云子账号密钥
- 网络访问腾讯云IoT服务

### 2. 安全考虑
- 保护子账号密钥安全
- 限制设备访问权限
- 监控API调用频率

### 3. 监控建议
- 监控设备在线状态
- 记录API调用日志
- 跟踪错误率
- 监控响应时间

## 常见问题解决

### Q1: 设备状态显示离线
**A**: 这是正常现象，设备可能暂时离线。API调用仍会成功，但设备无法接收命令。

### Q2: 像素图像显示异常
**A**: 检查像素数据格式，确保颜色值为有效的十六进制格式 (#RRGGBB)。

### Q3: GIF动画不播放
**A**: 检查帧数据格式，确保每帧都有正确的 `pixel_matrix` 和 `duration`。

### Q4: 服务启动失败
**A**: 检查环境变量是否正确设置，确保有腾讯云访问权限。

## 扩展开发

### 1. 添加新方法
- 在 `mug_service.py` 中添加方法
- 在 `mcp_server.py` 中添加处理逻辑
- 更新文档和测试

### 2. 支持新设备
- 修改设备ID和名称
- 适配新的物模型参数
- 测试兼容性

### 3. 性能优化
- 实现连接池
- 添加缓存机制
- 优化数据传输

## 技术支持

- 查看完整API文档: `API_DOCUMENTATION.md`
- 快速参考: `QUICK_REFERENCE.md`
- 运行测试脚本验证功能
- 检查日志获取详细错误信息
