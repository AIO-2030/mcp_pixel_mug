#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different principal formats for CAM role trust policy
测试不同的principal格式
"""

import json
import os

# 测试不同的principal格式
def test_principal_formats():
    main_account_uin = "100043941809"
    sub_account_uin = "100044493744"
    
    formats = [
        # 格式1: 文档示例格式
        f"qcs::cam::uin/{sub_account_uin}:root",
        
        # 格式2: 主账号:子账号格式
        f"qcs::cam::uin/{main_account_uin}:uin/{sub_account_uin}",
        
        # 格式3: 简化的子账号格式
        f"qcs::cam::uin/{sub_account_uin}:uin/{sub_account_uin}",
        
        # 格式4: 角色格式
        f"qcs::cam::uin/{main_account_uin}:role/alaya_mcp",
    ]
    
    print("测试不同的principal格式:")
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt}")
        
        trust_policy = {
            "version": "2.0",
            "statement": [
                {
                    "action": "name/sts:AssumeRole",
                    "effect": "allow",
                    "principal": {
                        "qcs": [fmt]
                    }
                }
            ]
        }
        
        print(f"   信任策略: {json.dumps(trust_policy, indent=2, ensure_ascii=False)}")
        print()

if __name__ == "__main__":
    test_principal_formats()
