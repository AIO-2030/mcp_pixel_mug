# GIF 像素格式支持说明

## 概述

`mug_service.py` 目前支持三种 GIF 像素格式：

1. **Base64 编码的 GIF 文件**
2. **传统帧数组格式**
3. **调色板格式 GIF 动画**

## 1. Base64 编码的 GIF 文件

### 输入格式
```python
gif_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
```

### 处理过程
- 自动解码 Base64 数据
- 使用 PIL 库解析 GIF 文件
- 提取每一帧并转换为像素矩阵
- 自动调整尺寸到目标大小

### 输出格式
```json
[
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
]
```

## 2. 传统帧数组格式

### 输入格式
```python
gif_data = [
  {
    "frame_index": 0,
    "pixel_matrix": [
      ["#FF0000", "#00FF00", "#0000FF"],
      ["#FFFF00", "#FF00FF", "#00FFFF"],
      ["#800000", "#008000", "#000080"]
    ],
    "duration": 200
  },
  {
    "frame_index": 1,
    "pixel_matrix": [
      ["#00FF00", "#FF0000", "#FFFF00"],
      ["#FF00FF", "#00FFFF", "#FF0000"],
      ["#008000", "#000080", "#800000"]
    ],
    "duration": 200
  }
]
```

### 字段说明
- `frame_index`: 帧索引（从 0 开始）
- `pixel_matrix`: 2D 像素矩阵，每个像素为十六进制颜色字符串
- `duration`: 帧持续时间（毫秒）

## 3. 调色板格式 GIF 动画

### 输入格式
```python
gif_data = {
  "title": "animated_heart",
  "description": "Animated heart with palette",
  "width": 8,
  "height": 8,
  "palette": [
    "#000000",  # 0 - 黑色
    "#ff0000",  # 1 - 红色
    "#ffffff"   # 2 - 白色
  ],
  "frame_delay": 200,
  "loop_count": 3,
  "frames": [
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0]
      ],
      "duration": 200
    },
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 2, 2, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 1, 2, 2, 1],
        [1, 2, 2, 1, 1, 2, 2, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0]
      ],
      "duration": 200
    }
  ]
}
```

### 字段说明

#### 顶层字段
- `title`: 动画标题
- `description`: 动画描述
- `width`: 动画宽度（像素）
- `height`: 动画高度（像素）
- `palette`: 调色板数组，最多 16 种颜色
- `frame_delay`: 默认帧延迟（毫秒）
- `loop_count`: 循环次数（0 表示无限循环）

#### 帧字段
- `pixels`: 2D 像素索引数组，每个数字对应调色板中的颜色索引
- `duration`: 该帧的持续时间（毫秒）

## 使用示例

### 1. 使用 Base64 GIF
```python
from mug_service import mug_service

# Base64 编码的 GIF 文件
base64_gif = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

result = mug_service.send_gif_animation(
    product_id="ABC123DEF",
    device_name="mug_001",
    gif_data=base64_gif,
    frame_delay=100,
    loop_count=0,
    target_width=16,
    target_height=16
)
```

### 2. 使用传统帧数组
```python
frames = [
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
]

result = mug_service.send_gif_animation(
    product_id="ABC123DEF",
    device_name="mug_001",
    gif_data=frames,
    frame_delay=100,
    loop_count=1
)
```

### 3. 使用调色板格式
```python
palette_gif = {
  "title": "blinking_heart",
  "width": 8,
  "height": 8,
  "palette": ["#000000", "#ff0000", "#ffffff"],
  "frame_delay": 300,
  "loop_count": 5,
  "frames": [
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0]
      ],
      "duration": 300
    },
    {
      "pixels": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 2, 0, 0, 2, 2, 0],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [0, 2, 2, 2, 2, 2, 2, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0]
      ],
      "duration": 300
    }
  ]
}

result = mug_service.send_gif_animation(
    product_id="ABC123DEF",
    device_name="mug_001",
    gif_data=palette_gif,
    frame_delay=300,
    loop_count=5
)
```

## 格式转换

所有格式最终都会转换为统一的帧数组格式：

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

## 验证规则

### 调色板格式验证
- 调色板最多 16 种颜色
- 颜色格式必须是 `#RRGGBB` 格式
- 像素索引必须在调色板范围内
- 每帧的像素数组尺寸必须匹配指定的宽高

### 传统格式验证
- 像素颜色必须是有效的十六进制格式
- 帧数组不能为空
- 每帧必须包含 `pixel_matrix` 和 `duration`

### Base64 格式验证
- 必须是有效的 Base64 编码
- 解码后必须是有效的 GIF 文件
- 必须包含至少一帧

## 性能考虑

1. **调色板格式**：最节省带宽，适合网络传输
2. **传统格式**：直观易用，适合编程生成
3. **Base64 格式**：适合从文件直接加载

## 错误处理

系统会自动处理以下错误情况：
- 无效的颜色格式
- 超出范围的像素索引
- 尺寸不匹配的像素数组
- 空的帧数组
- 无效的 Base64 数据
