#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证正确的principal格式
"""

import json

def test_principal_formats():
    """测试不同的principal格式"""
    
    formats = [
        "qcs::cam::uin/100044493744:root",
        "qcs::cam::uin/100043941809:uin/100044493744", 
        "qcs::cam::uin/100044493744:uin/100044493744"
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
        
        print(f"   策略: {json.dumps(trust_policy, indent=2, ensure_ascii=False)}")
        print()

if __name__ == "__main__":
    test_principal_formats()
