#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照文档示例格式生成角色信任策略
使用resource字段而不是principal字段
"""

import json
import urllib.parse

def generate_policy_with_resource_format():
    """按照文档示例格式生成策略"""
    
    # 我们的环境信息
    main_account_uin = "100043941809"
    sub_account_uin = "100044493744"
    role_name = "alaya_mcp"
    
    print("=== 按照文档示例格式生成策略 ===")
    print()
    
    # 1. 按照文档示例格式的策略
    print("1. 按照文档示例格式的策略:")
    policy_with_resource = {
        "version": "2.0",
        "statement": [
            {
                "effect": "allow",
                "action": ["name/sts:AssumeRole"],
                "resource": [f"qcs::cam::uin/{main_account_uin}:roleName/{role_name}"]
            }
        ]
    }
    
    print("JSON格式:")
    print(json.dumps(policy_with_resource, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    policy_json = json.dumps(policy_with_resource)
    url_encoded = urllib.parse.quote(policy_json)
    print(url_encoded)
    print()
    
    # 2. 完整的API请求参数
    print("2. 完整的API请求参数:")
    api_request = {
        "RoleName": role_name,
        "PolicyDocument": json.dumps(policy_with_resource)
    }
    
    print("JSON格式:")
    print(json.dumps(api_request, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    api_request_json = json.dumps(api_request)
    api_url_encoded = urllib.parse.quote(api_request_json)
    print(api_url_encoded)
    print()
    
    # 3. 对比两种格式
    print("3. 格式对比:")
    print("文档示例格式（使用resource）:")
    print(json.dumps(policy_with_resource, indent=2, ensure_ascii=False))
    print()
    
    # 之前的格式（使用principal）
    policy_with_principal = {
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
    
    print("之前格式（使用principal）:")
    print(json.dumps(policy_with_principal, indent=2, ensure_ascii=False))
    print()
    
    print("=== 说明 ===")
    print("• 文档示例使用 'resource' 字段指定角色资源")
    print("• 之前格式使用 'principal' 字段指定授权对象")
    print("• 两种格式可能适用于不同的场景")
    print("• 建议先尝试文档示例格式")
    print()
    
    return policy_with_resource, api_request

def main():
    """主函数"""
    policy, request = generate_policy_with_resource_format()
    
    print("=== 最终推荐使用的策略（按文档格式） ===")
    print("策略文档:")
    print(json.dumps(policy, indent=2, ensure_ascii=False))
    print()
    print("API请求参数:")
    print(json.dumps(request, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
