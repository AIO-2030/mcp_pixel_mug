#!/bin/bash
# PixelMug MCP Service Environment Variables Export
# 导出环境变量供可执行文件使用

# 必需的环境变量
export IOT_ROLE_ARN="qcs::cam::uin/123456789:role/iot-role"

# 可选的环境变量（有默认值）
export DEFAULT_REGION="ap-guangzhou"
export COS_BUCKET="pixelmug-assets"

# 腾讯云访问密钥（如果在非 CVM/TKE 环境运行需要设置）
export TC_SECRET_ID="your_secret_id"
export TC_SECRET_KEY="your_secret_key"

# 服务配置
export LOG_LEVEL="INFO"
export SERVICE_PORT="8000"

# Python 路径
export PYTHONPATH="/root/AIO-2030/mcp/mcp_pixel_mug"

echo "✅ 环境变量已导出"
echo "IOT_ROLE_ARN: $IOT_ROLE_ARN"
echo "DEFAULT_REGION: $DEFAULT_REGION"
echo "COS_BUCKET: $COS_BUCKET"
echo "LOG_LEVEL: $LOG_LEVEL"
echo "SERVICE_PORT: $SERVICE_PORT"
