# 腾讯云CAM角色信任策略更新指南

## 问题分析

根据我们的调试，STS角色假设失败的原因是：
- **角色存在**: `alaya_mcp` 角色确实存在
- **角色ARN正确**: `qcs::cam::uin/100043941809:roleName/alaya_mcp`
- **子账号UIN**: `100044493744`
- **主账号UIN**: `100043941809`

**问题**: 角色的信任策略不允许子账号 `100044493744` 扮演该角色。

## 解决方案

### 方法1: 通过腾讯云控制台手动更新（推荐）

1. **登录腾讯云控制台**
   - 访问: https://console.cloud.tencent.com/cam/role
   - 使用主账号登录

2. **找到目标角色**
   - 在角色列表中找到 `alaya_mcp` 角色
   - 点击角色名称进入详情页

3. **更新信任策略**
   - 点击 "信任策略" 标签页
   - 点击 "编辑" 按钮
   - 将信任策略更新为：

```json
{
  "version": "2.0",
  "statement": [
    {
      "action": "name/sts:AssumeRole",
      "effect": "allow",
      "principal": {
        "qcs": [
          "qcs::cam::uin/100043941809:uin/100044493744"
        ]
      }
    }
  ]
}
```

4. **保存策略**
   - 点击 "保存" 按钮
   - 确认更新

### 方法2: 通过API更新（如果控制台方法失败）

如果控制台方法失败，可能需要：

1. **检查子账号权限**
   - 确保子账号有 `sts:AssumeRole` 权限
   - 在CAM控制台为用户或用户组附加包含此权限的策略

2. **验证子账号UIN**
   - 确认子账号UIN `100044493744` 是正确的
   - 可以在CAM控制台的用户列表中查看

## 验证更新

更新信任策略后，可以运行以下命令验证：

```bash
cd /root/AIO-2030/mcp/mcp_pixel_mug
python3 -c "
from mug_service import mug_service
import logging
logging.basicConfig(level=logging.INFO)

try:
    result = mug_service.issue_sts('H3PI4FBTV5', 'mug_001')
    print('STS Success:', result)
except Exception as e:
    print('STS Error:', str(e))
"
```

## 常见问题

### Q: 为什么API更新失败？
A: 可能是principal格式问题或权限不足。建议使用控制台手动更新。

### Q: 如何确认子账号UIN？
A: 在CAM控制台的用户列表中查看，或使用我们添加的 `_get_caller_identity()` 方法。

### Q: 更新后仍然失败怎么办？
A: 检查子账号是否有 `sts:AssumeRole` 权限，以及角色是否有正确的权限策略。

## 相关文档

- [腾讯云CAM角色创建文档](https://cloud.tencent.com/document/product/598/19381#.E9.80.9A.E8.BF.87.E6.8E.A7.E5.88.B6.E5.8F.B0.E5.88.9B.E5.BB.BA)
- [腾讯云STS AssumeRole API文档](https://cloud.tencent.com/document/product/598/19419)
