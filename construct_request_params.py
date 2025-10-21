#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构造CAM角色信任策略更新请求参数
根据我们的环境信息构造符合要求的JSON参数
"""

import json

def construct_update_role_policy_request():
    """构造更新角色信任策略的请求参数"""
    
    # 我们的环境信息
    role_name = "alaya_mcp"  # 角色名称
    main_account_uin = "100043941809"  # 主账号UIN
    sub_account_uin = "100044493744"  # 子账号UIN
    
    # 构造信任策略
    trust_policy = {
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
    
    # 构造请求参数
    request_params = {
        "RoleName": role_name,
        "PolicyDocument": json.dumps(trust_policy)
    }
    
    return request_params

def main():
    """主函数"""
    print("=== CAM角色信任策略更新请求参数 ===")
    print()
    
    # 构造请求参数
    request_params = construct_update_role_policy_request()
    
    print("请求参数JSON:")
    print(json.dumps(request_params, indent=2, ensure_ascii=False))
    print()
    
    print("信任策略详情:")
    trust_policy = json.loads(request_params["PolicyDocument"])
    print(json.dumps(trust_policy, indent=2, ensure_ascii=False))
    print()
    
    print("环境信息:")
    print(f"角色名称: {request_params['RoleName']}")
    print(f"主账号UIN: 100043941809")
    print(f"子账号UIN: 100044493744")
    print(f"角色ARN: qcs::cam::uin/100043941809:roleName/alaya_mcp")
    print()
    
    print("=== 使用说明 ===")
    print("1. 复制上面的请求参数JSON")
    print("2. 在腾讯云CAM控制台或API中使用")
    print("3. 或者使用我们提供的Python脚本自动更新")
    
    return request_params

if __name__ == "__main__":
    main()
