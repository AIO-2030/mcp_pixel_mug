#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to update role trust policy
简单的角色信任策略更新测试
"""

import json
import os
import logging

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.cam.v20190116 import cam_client, models as cam_models
    CAM_AVAILABLE = True
except ImportError:
    CAM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_update_role_policy():
    """测试更新角色策略"""
    try:
        if not CAM_AVAILABLE:
            raise ImportError("CAM SDK not available")
        
        # 获取凭证
        secret_id = os.getenv("TC_SECRET_ID")
        secret_key = os.getenv("TC_SECRET_KEY")
        
        if not secret_id or not secret_key:
            raise ValueError("Please set TC_SECRET_ID and TC_SECRET_KEY")
        
        cred = credential.Credential(secret_id, secret_key)
        region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
        
        # 创建客户端
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cam.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cam_client.CamClient(cred, region, clientProfile)
        
        # 构建信任策略 - 使用正确的格式
        trust_policy = {
            "version": "2.0",
            "statement": [
                {
                    "action": "name/sts:AssumeRole",
                    "effect": "allow",
                    "principal": {
                        "qcs": ["qcs::cam::uin/100044493744:root"]
                    }
                }
            ]
        }
        
        print("准备更新的信任策略:")
        print(json.dumps(trust_policy, indent=2, ensure_ascii=False))
        
        # 更新角色信任策略
        req = cam_models.UpdateAssumeRolePolicyRequest()
        params = {
            "RoleName": "alaya_mcp",
            "PolicyDocument": json.dumps(trust_policy)
        }
        req.from_json_string(json.dumps(params))
        
        print("\n发送更新请求...")
        resp = client.UpdateAssumeRolePolicy(req)
        
        print(f"更新成功! RequestId: {resp.RequestId}")
        return True
        
    except Exception as e:
        print(f"更新失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_update_role_policy()
