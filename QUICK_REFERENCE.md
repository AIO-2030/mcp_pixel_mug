# PixelMug MCP Service 快速参考

## 服务启动
```bash
python stdio_server.py
```

## 核心方法调用

### 1. 查询设备状态
```json
{
  "jsonrpc": "2.0",
  "method": "get_device_status",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950"
  },
  "id": 1
}
```

### 2. 发送文本
```json
{
  "jsonrpc": "2.0",
  "method": "send_display_text",
  "params": {
    "product_id": "H3PI4FBTV5",
    "device_name": "3CDC7580F950",
    "text": "Hello World"
  },
  "id": 2
}
```

### 3. 发送像素图像
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
  "id": 3
}
```

### 4. 发送GIF动画
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
      }
    ],
    "frame_delay": 500,
    "loop_count": 1,
    "target_width": 2,
    "target_height": 2,
    "use_cos": false
  },
  "id": 4
}
```

### 5. 转换图像为像素
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
  "id": 5
}
```

## 像素数据格式

### 2D数组格式
```json
[
  ["#FF0000", "#00FF00"],
  ["#0000FF", "#FFFF00"]
]
```

### 调色板格式
```json
{
  "palette": ["#ffffff", "#ff0000", "#00ff00"],
  "pixels": [
    [0, 1, 1, 0],
    [1, 2, 2, 1]
  ]
}
```

## 环境变量
```bash
export TC_SECRET_ID="your_secret_id"
export TC_SECRET_KEY="your_secret_key"
export DEFAULT_REGION="ap-guangzhou"
```

## 测试命令
```bash
# 快速测试
echo '{"jsonrpc": "2.0", "method": "get_device_status", "params": {"product_id": "H3PI4FBTV5", "device_name": "3CDC7580F950"}, "id": 1}' | python stdio_server.py

# 发送文本
echo '{"jsonrpc": "2.0", "method": "send_display_text", "params": {"product_id": "H3PI4FBTV5", "device_name": "3CDC7580F950", "text": "Hello"}, "id": 2}' | python stdio_server.py
```
