#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update CAM Role Trust Policy for Sub-account Access
根据腾讯云CAM文档更新角色信任策略，允许子账号扮演角色
"""

import json
import os
import logging
from typing import Dict, Any

# 腾讯云CAM相关依赖
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

class RoleTrustPolicyUpdater:
    """CAM角色信任策略更新器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def update_role_trust_policy(self, role_name: str, sub_account_uin: str, main_account_uin: str) -> Dict[str, Any]:
        """
        更新角色信任策略，允许子账号扮演角色
        
        Args:
            role_name: 角色名称
            sub_account_uin: 子账号UIN
            main_account_uin: 主账号UIN
            
        Returns:
            更新结果
        """
        try:
            if not CAM_AVAILABLE:
                raise ImportError("Tencent Cloud CAM SDK not installed, please install tencentcloud-sdk-python-cam")
            
            # 获取主账号凭证
            secret_id = os.getenv("TC_SECRET_ID")
            secret_key = os.getenv("TC_SECRET_KEY")
            
            if not secret_id or not secret_key:
                raise ValueError("Please set TC_SECRET_ID and TC_SECRET_KEY environment variables")
            
            # 创建凭证
            cred = credential.Credential(secret_id, secret_key)
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            
            # 创建CAM客户端
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cam.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cam_client.CamClient(cred, region, clientProfile)
            
            # 构建新的信任策略
            trust_policy = {
                "version": "2.0",
                "statement": [
                    {
                        "action": "name/sts:AssumeRole",
                        "effect": "allow",
                        "principal": {
                            "qcs": [f"qcs::cam::uin/{sub_account_uin}:root"]
                        }
                    }
                ]
            }
            
            # 创建更新角色请求
            req = cam_models.UpdateRoleDescriptionRequest()
            params = {
                "RoleName": role_name,
                "Description": f"Updated trust policy to allow sub-account {sub_account_uin} to assume role"
            }
            req.from_json_string(json.dumps(params))
            
            # 更新角色描述（可选）
            try:
                resp_desc = client.UpdateRoleDescription(req)
                self.logger.info(f"Updated role description for {role_name}")
            except Exception as e:
                self.logger.warning(f"Failed to update role description: {str(e)}")
            
            # 更新角色信任策略
            req_policy = cam_models.UpdateAssumeRolePolicyRequest()
            policy_params = {
                "RoleName": role_name,
                "PolicyDocument": json.dumps(trust_policy)
            }
            req_policy.from_json_string(json.dumps(policy_params))
            
            resp_policy = client.UpdateAssumeRolePolicy(req_policy)
            
            result = {
                "status": "success",
                "role_name": role_name,
                "sub_account_uin": sub_account_uin,
                "main_account_uin": main_account_uin,
                "trust_policy": trust_policy,
                "request_id": resp_policy.RequestId
            }
            
            self.logger.info(f"Successfully updated trust policy for role {role_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update role trust policy: {str(e)}")
            raise
    
    def get_role_info(self, role_name: str) -> Dict[str, Any]:
        """获取角色信息"""
        try:
            if not CAM_AVAILABLE:
                raise ImportError("Tencent Cloud CAM SDK not installed")
            
            # 获取主账号凭证
            secret_id = os.getenv("TC_SECRET_ID")
            secret_key = os.getenv("TC_SECRET_KEY")
            
            if not secret_id or not secret_key:
                raise ValueError("Please set TC_SECRET_ID and TC_SECRET_KEY environment variables")
            
            # 创建凭证
            cred = credential.Credential(secret_id, secret_key)
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            
            # 创建CAM客户端
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cam.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cam_client.CamClient(cred, region, clientProfile)
            
            # 获取角色信息
            req = cam_models.GetRoleRequest()
            params = {"RoleName": role_name}
            req.from_json_string(json.dumps(params))
            
            resp = client.GetRole(req)
            
            return {
                "role_name": resp.RoleInfo.RoleName,
                "role_id": resp.RoleInfo.RoleId,
                "description": resp.RoleInfo.Description,
                "role_arn": resp.RoleInfo.RoleArn
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get role info: {str(e)}")
            raise

def main():
    """主函数"""
    updater = RoleTrustPolicyUpdater()
    
    # 从环境变量获取配置
    role_name = os.getenv("IOT_ROLE_NAME", "alaya_mcp")
    sub_account_uin = "100044493744"  # 从之前的调试信息获取
    main_account_uin = "100043941809"  # 从角色ARN获取
    
    print(f"准备更新角色 {role_name} 的信任策略...")
    print(f"主账号UIN: {main_account_uin}")
    print(f"子账号UIN: {sub_account_uin}")
    
    try:
        # 先获取当前角色信息
        print("\n获取当前角色信息...")
        role_info = updater.get_role_info(role_name)
        print(f"当前角色信息: {json.dumps(role_info, indent=2, ensure_ascii=False)}")
        
        # 更新信任策略
        print(f"\n更新角色 {role_name} 的信任策略...")
        result = updater.update_role_trust_policy(role_name, sub_account_uin, main_account_uin)
        print(f"更新结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 验证更新后的角色信息
        print("\n验证更新后的角色信息...")
        updated_role_info = updater.get_role_info(role_name)
        print(f"更新后的角色信息: {json.dumps(updated_role_info, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
