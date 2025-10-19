# 环境变量配置指南

## 概述

PixelMug MCP Service 需要配置腾讯云相关的环境变量才能正常工作。为了安全起见，我们不在代码中硬编码真实的密钥信息。

## 快速开始

### 1. 复制环境变量模板

```bash
cp env.template export_env_local.sh
```

### 2. 编辑本地环境变量文件

```bash
nano export_env_local.sh
```

### 3. 填入您的真实配置

修改以下关键配置：

```bash
# IoT角色ARN
export IOT_ROLE_ARN="qcs::cam::uin/YOUR_UIN:roleName/YOUR_ROLE_NAME"

# 腾讯云访问凭证
export TC_SECRET_ID="YOUR_SECRET_ID"
export TC_SECRET_KEY="YOUR_SECRET_KEY"

# COS配置（如果使用COS功能）
export COS_OWNER_UIN="YOUR_UIN"
export COS_BUCKET_NAME="your-bucket-name"
```

### 4. 加载环境变量

```bash
# 方法1: 使用本地配置文件
source export_env_local.sh

# 方法2: 使用系统级配置（推荐）
sudo ./export_env.sh system
```

## 配置说明

### 必需的环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `IOT_ROLE_ARN` | IoT角色ARN | 腾讯云控制台 -> 访问管理 -> 角色 |
| `TC_SECRET_ID` | 腾讯云SecretId | 腾讯云控制台 -> 访问管理 -> API密钥管理 |
| `TC_SECRET_KEY` | 腾讯云SecretKey | 腾讯云控制台 -> 访问管理 -> API密钥管理 |

### 可选的环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEFAULT_REGION` | `ap-guangzhou` | 默认地域 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `COS_OWNER_UIN` | - | COS存储桶拥有者UIN |
| `COS_BUCKET_NAME` | - | COS存储桶名称 |
| `COS_REGION` | `ap-guangzhou` | COS地域 |

## 安全注意事项

1. **永远不要**将包含真实密钥的文件提交到Git仓库
2. 使用 `export_env_local.sh` 存储您的本地配置
3. 定期轮换您的API密钥
4. 使用子账号密钥而不是主账号密钥

## 验证配置

运行以下命令验证环境变量是否正确设置：

```bash
./export_env.sh --check
```

## 故障排除

### 问题：Environment variable IOT_ROLE_ARN is not set

**解决方案：**
1. 确保已正确加载环境变量：`source export_env_local.sh`
2. 检查环境变量是否设置：`echo $IOT_ROLE_ARN`
3. 使用系统级配置：`sudo ./export_env.sh system`

### 问题：GitHub推送被阻止

**原因：** GitHub检测到代码中包含敏感信息

**解决方案：**
1. 确保 `export_env.sh` 中使用占位符而不是真实密钥
2. 将真实配置放在 `export_env_local.sh` 中
3. 确保 `.gitignore` 包含 `*_local.sh` 和 `*.env`

## 管理命令

```bash
# 检查当前配置
./export_env.sh --check

# 查看配置状态
./export_env.sh --status

# 设置用户级配置
./export_env.sh user

# 设置系统级配置
sudo ./export_env.sh system

# 移除配置
./export_env.sh --remove user
sudo ./export_env.sh --remove system
```
