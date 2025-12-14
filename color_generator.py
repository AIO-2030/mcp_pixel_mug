#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色生成器模块
用于生成鲜亮显眼的文本颜色和对比鲜明的背景颜色
"""

import random
import colorsys
from typing import Tuple


def rgb_to_decimal(r: int, g: int, b: int) -> int:
    """
    将RGB值转换为十进制颜色值
    
    Args:
        r: 红色分量 (0-255)
        g: 绿色分量 (0-255)
        b: 蓝色分量 (0-255)
    
    Returns:
        十进制颜色值，例如 0xff0000 = 16711680 (红色)
    """
    return (r << 16) | (g << 8) | b


def generate_vibrant_text_color() -> int:
    """
    生成鲜亮显眼的文本颜色
    
    策略：
    - 使用HSV色彩空间，确保高饱和度（鲜艳）
    - 高亮度值，确保颜色显眼
    - 避免过于暗淡的颜色
    
    Returns:
        十进制颜色值
    """
    # 生成随机色相 (0-360度)
    hue = random.uniform(0, 1)
    
    # 高饱和度 (0.7-1.0)，确保颜色鲜艳
    saturation = random.uniform(0.7, 1.0)
    
    # 高亮度 (0.6-1.0)，确保颜色显眼
    value = random.uniform(0.6, 1.0)
    
    # 转换为RGB
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # 转换为0-255范围
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    return rgb_to_decimal(r, g, b)


def generate_contrasting_bg_color(text_color_decimal: int) -> int:
    """
    根据文本颜色生成对比鲜明的背景颜色
    
    策略：
    - 计算文本颜色的HSV值
    - 使用互补色或对比色方案
    - 调整亮度和饱和度以形成对比，同时保持协调
    
    Args:
        text_color_decimal: 文本颜色的十进制值
    
    Returns:
        十进制背景颜色值
    """
    # 从十进制提取RGB
    r = (text_color_decimal >> 16) & 0xFF
    g = (text_color_decimal >> 8) & 0xFF
    b = text_color_decimal & 0xFF
    
    # 转换为HSV色彩空间
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    
    # 策略1: 使用互补色（色相+180度），但调整亮度和饱和度
    # 策略2: 使用对比色（色相+120度或-120度）
    # 策略3: 使用低饱和度的同色系或互补色
    
    # 随机选择策略，增加多样性
    strategy = random.choice(['complementary', 'triadic', 'low_saturation'])
    
    if strategy == 'complementary':
        # 互补色方案：色相+180度，降低亮度和饱和度
        bg_hue = (h + 0.5) % 1.0  # 互补色
        bg_saturation = random.uniform(0.3, 0.6)  # 中等饱和度
        bg_value = random.uniform(0.1, 0.4)  # 低亮度，形成对比
    elif strategy == 'triadic':
        # 三色方案：色相+120度或-120度
        offset = random.choice([1/3, -1/3])
        bg_hue = (h + offset) % 1.0
        bg_saturation = random.uniform(0.4, 0.7)
        bg_value = random.uniform(0.2, 0.5)
    else:  # low_saturation
        # 低饱和度方案：保持相近色相，但大幅降低饱和度和亮度
        bg_hue = (h + random.uniform(-0.1, 0.1)) % 1.0  # 相近色相
        bg_saturation = random.uniform(0.1, 0.3)  # 低饱和度
        bg_value = random.uniform(0.1, 0.3)  # 低亮度
    
    # 转换为RGB
    bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(bg_hue, bg_saturation, bg_value)
    
    # 转换为0-255范围
    bg_r = int(bg_r * 255)
    bg_g = int(bg_g * 255)
    bg_b = int(bg_b * 255)
    
    return rgb_to_decimal(bg_r, bg_g, bg_b)


def generate_color_pair() -> Tuple[int, int]:
    """
    生成一对协调且对比鲜明的颜色
    
    Returns:
        (文本颜色, 背景颜色) 的元组，都是十进制值
    """
    text_color = generate_vibrant_text_color()
    bg_color = generate_contrasting_bg_color(text_color)
    
    return (text_color, bg_color)

