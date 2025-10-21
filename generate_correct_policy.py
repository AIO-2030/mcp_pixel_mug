#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据腾讯云CAM文档生成正确的角色信任策略
区分服务角色和子账号角色的不同principal格式
"""

import json
import urllib.parse

def generate_role_trust_policy():
    """生成角色信任策略"""
    
    # 我们的环境信息
    main_account_uin = "100043941809"
    sub_account_uin = "100044493744"
    
    print("=== 腾讯云CAM角色信任策略生成 ===")
    print()
    
    # 1. 子账号扮演角色的信任策略（我们的场景）
    print("1. 子账号扮演角色的信任策略（我们的场景）:")
    sub_account_policy = {
        "version": "2.0",
        "statement": [
            {
                "action": "name/sts:AssumeRole",
                "effect": "allow",
                "principal": {
                    "qcs": [f"qcs::cam::uin/{main_account_uin}:uin/{sub_account_uin}"]
                }
            }
        ]
    }
    
    print("JSON格式:")
    print(json.dumps(sub_account_policy, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    policy_json = json.dumps(sub_account_policy)
    url_encoded = urllib.parse.quote(policy_json)
    print(url_encoded)
    print()
    
    # 2. 服务角色的信任策略（文档示例）
    print("2. 服务角色的信任策略（文档示例）:")
    service_policy = {
        "version": "2.0",
        "statement": [
            {
                "action": "name/sts:AssumeRole",
                "effect": "allow",
                "principal": {
                    "service": ["cloudaudit.cloud.tencent.com", "cls.cloud.tencent.com"]
                }
            }
        ]
    }
    
    print("JSON格式:")
    print(json.dumps(service_policy, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    service_policy_json = json.dumps(service_policy)
    service_url_encoded = urllib.parse.quote(service_policy_json)
    print(service_url_encoded)
    print()
    
    # 3. 完整的API请求参数
    print("3. 完整的API请求参数:")
    api_request = {
        "RoleName": "alaya_mcp",
        "PolicyDocument": json.dumps(sub_account_policy)
    }
    
    print("JSON格式:")
    print(json.dumps(api_request, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    api_request_json = json.dumps(api_request)
    api_url_encoded = urllib.parse.quote(api_request_json)
    print(api_url_encoded)
    print()
    
    # 4. 说明
    print("=== 说明 ===")
    print("• 我们的场景是子账号扮演角色，使用 'qcs' principal")
    print("• 文档示例是服务角色，使用 'service' principal")
    print("• principal格式:")
    print("  - 子账号: qcs::cam::uin/{主账号UIN}:uin/{子账号UIN}")
    print("  - 服务: service名称数组")
    print()
    
    return sub_account_policy, api_request

def main():
    """主函数"""
    policy, request = generate_role_trust_policy()
    
    print("=== 最终推荐使用的策略 ===")
    print("策略文档:")
    print(json.dumps(policy, indent=2, ensure_ascii=False))
    print()
    print("API请求参数:")
    print(json.dumps(request, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
