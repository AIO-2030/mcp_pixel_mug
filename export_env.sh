#!/bin/bash
# PixelMug MCP Service Environment Variables Export
# 导出环境变量供可执行文件使用

# =============================================================================
# 必需的环境变量 - 必须配置
# =============================================================================

# IoT角色ARN - 用于STS临时凭证申请
# 格式: qcs::cam::uin/{UIN}:roleName/{角色名称}
# 获取方式: 腾讯云控制台 -> 访问管理 -> 角色 -> 选择角色 -> 复制角色ARN
# 当前配置: alaya_mcp 角色 (alaya network authority)
export IOT_ROLE_ARN="qcs::cam::uin/123456789:roleName/alaya_mcp"

# =============================================================================
# 腾讯云访问凭证 - 必须配置
# =============================================================================

# 推荐使用子账号密钥，比主账号密钥更安全
# 获取方式: 腾讯云控制台 -> 访问管理 -> API密钥管理
export TC_SECRET_ID="your_secret_id"
export TC_SECRET_KEY="your_secret_key"

# 凭证优先级: 子账号密钥 > 主账号密钥

# =============================================================================
# COS对象存储配置 - 可选，如果使用COS功能需要配置
# =============================================================================

# COS存储桶拥有者UIN - 拥有COS存储桶的腾讯云账号UIN
# 获取方式: 腾讯云控制台 -> 账号信息 -> 主账号ID
export COS_OWNER_UIN="123456789"

# COS存储桶名称 - 用于存储像素图片和GIF动画
# 获取方式: 腾讯云控制台 -> 对象存储 -> 存储桶列表
export COS_BUCKET_NAME="your-bucket-name"

# COS地域 - 存储桶所在的地域
# 常用地域: ap-guangzhou, ap-beijing, ap-shanghai
export COS_REGION="ap-guangzhou"

# =============================================================================
# 服务配置 - 可选，有默认值
# =============================================================================

# 默认地域 - 腾讯云服务默认地域
export DEFAULT_REGION="ap-guangzhou"

# COS存储桶名称（兼容旧版本）
export COS_BUCKET="pixelmug-assets"

# 日志级别 - DEBUG, INFO, WARNING, ERROR
export LOG_LEVEL="INFO"

# 注意: ALAYA网络使用stdio模式，无需HTTP服务监听端口

# =============================================================================
# ALAYA协议配置 - ALAYA是协议标准，DApp直接组装stdio参数
# =============================================================================

# 注意: ALAYA是协议标准，不需要额外的验证配置
# DApp直接通过stdio接口组装参数调用服务

# =============================================================================
# 配置验证和显示
# =============================================================================

echo "✅ PixelMug MCP Service 环境变量已导出"
echo ""
echo "📋 核心配置:"
echo "  IOT_ROLE_ARN: $IOT_ROLE_ARN"
echo "  DEFAULT_REGION: $DEFAULT_REGION"
echo ""
echo "☁️  COS配置:"
echo "  COS_OWNER_UIN: $COS_OWNER_UIN"
echo "  COS_BUCKET_NAME: $COS_BUCKET_NAME"
echo "  COS_REGION: $COS_REGION"
echo ""
echo "⚙️  服务配置:"
echo "  LOG_LEVEL: $LOG_LEVEL"
echo "  运行模式: stdio模式 (ALAYA网络)"
echo ""
echo "🌐 ALAYA协议:"
echo "  ALAYA是协议标准，DApp直接组装stdio参数"
echo ""
echo "🔑 访问凭证:"
if [ -n "$TC_SECRET_ID" ] && [ "$TC_SECRET_ID" != "your_secret_id" ]; then
    echo "  TC_SECRET_ID: ${TC_SECRET_ID:0:8}***"
    echo "  TC_SECRET_KEY: ${TC_SECRET_KEY:0:8}***"
    # 简单检测账号类型
    if [[ "$TC_SECRET_ID" =~ ^AKID.* ]]; then
        echo "  账号类型: 子账号密钥（推荐）"
    else
        echo "  账号类型: 主账号密钥"
    fi
else
    echo "  请配置TC_SECRET_ID和TC_SECRET_KEY环境变量"
fi
echo "  角色ARN: $IOT_ROLE_ARN"
echo ""
echo "💡 提示: 请根据实际情况修改上述配置值"
