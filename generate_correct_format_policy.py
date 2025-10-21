#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照正确的文档示例格式生成角色信任策略
使用principal字段，格式为 qcs::cam::uin/子账号UIN:root
"""

import json
import urllib.parse

def generate_correct_policy_format():
    """按照正确的文档示例格式生成策略"""
    
    # 我们的环境信息
    sub_account_uin = "100044493744"  # 子账号UIN
    
    print("=== 按照正确的文档示例格式生成策略 ===")
    print()
    
    # 1. 按照正确文档示例格式的策略
    print("1. 按照正确文档示例格式的策略:")
    correct_policy = {
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
    
    print("JSON格式:")
    print(json.dumps(correct_policy, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    policy_json = json.dumps(correct_policy)
    url_encoded = urllib.parse.quote(policy_json)
    print(url_encoded)
    print()
    
    # 2. 完整的API请求参数
    print("2. 完整的API请求参数:")
    api_request = {
        "RoleName": "alaya_mcp",
        "PolicyDocument": json.dumps(correct_policy)
    }
    
    print("JSON格式:")
    print(json.dumps(api_request, indent=2, ensure_ascii=False))
    print()
    
    print("URL编码格式:")
    api_request_json = json.dumps(api_request)
    api_url_encoded = urllib.parse.quote(api_request_json)
    print(api_url_encoded)
    print()
    
    # 3. 对比之前的错误格式
    print("3. 格式对比:")
    print("正确格式（使用子账号UIN:root）:")
    print(json.dumps(correct_policy, indent=2, ensure_ascii=False))
    print()
    
    # 之前错误的格式
    wrong_policy = {
        "version": "2.0",
        "statement": [
            {
                "action": "name/sts:AssumeRole",
                "effect": "allow",
                "principal": {
                    "qcs": ["qcs::cam::uin/100043941809:uin/100044493744"]
                }
            }
        ]
    }
    
    print("之前错误格式（使用主账号UIN:uin/子账号UIN）:")
    print(json.dumps(wrong_policy, indent=2, ensure_ascii=False))
    print()
    
    print("=== 说明 ===")
    print("• 正确格式: qcs::cam::uin/{子账号UIN}:root")
    print("• 错误格式: qcs::cam::uin/{主账号UIN}:uin/{子账号UIN}")
    print("• 文档示例使用子账号UIN:root格式")
    print("• 这解释了为什么之前的API调用失败")
    print()
    
    return correct_policy, api_request

def main():
    """主函数"""
    policy, request = generate_correct_policy_format()
    
    print("=== 最终推荐使用的策略（正确格式） ===")
    print("策略文档:")
    print(json.dumps(policy, indent=2, ensure_ascii=False))
    print()
    print("API请求参数:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    print("=== 环境信息 ===")
    print(f"子账号UIN: 100044493744")
    print(f"角色名称: alaya_mcp")
    print(f"角色ARN: qcs::cam::uin/100043941809:roleName/alaya_mcp")

if __name__ == "__main__":
    main()
