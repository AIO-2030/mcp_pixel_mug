#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIF Resizer Module
统一处理GIF缩放为标准规格(32x16)

缩放规则：
1. 等比例缩放，保持宽高比（如32x32会缩放为16x16）
2. 缩放后的空白区域，用原图四角像素的颜色填充
"""

import io
import logging
from typing import Optional, Tuple, List

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class GIFResizer:
    """GIF缩放器，将GIF统一缩放为32x16标准尺寸"""
    
    # 标准尺寸
    TARGET_WIDTH = 32
    TARGET_HEIGHT = 16
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def resize_gif_to_standard(self, gif_bytes: bytes) -> bytes:
        """
        将GIF缩放为标准尺寸(32x16)
        
        缩放规则：
        1. 等比例缩放，保持宽高比（如32x32会缩放为16x16）
        2. 缩放后的空白区域，用原图四角像素的颜色填充
        
        Args:
            gif_bytes: 原始GIF文件的字节数据
            
        Returns:
            缩放后的GIF文件字节数据
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available for GIF resizing")
        
        if not gif_bytes or len(gif_bytes) == 0:
            raise ValueError("Empty GIF data")
        
        try:
            # 打开GIF文件
            gif_image = Image.open(io.BytesIO(gif_bytes))
            
            # 获取原始尺寸
            original_width, original_height = gif_image.size
            self.logger.info(f"Original GIF size: {original_width}x{original_height}")
            
            # 计算等比例缩放尺寸
            # 使用较小的缩放比例以保持宽高比
            scale_w = self.TARGET_WIDTH / original_width
            scale_h = self.TARGET_HEIGHT / original_height
            scale = min(scale_w, scale_h)
            
            scaled_width = int(original_width * scale)
            scaled_height = int(original_height * scale)
            
            self.logger.info(f"Scaled size (maintaining aspect ratio): {scaled_width}x{scaled_height}")
            self.logger.info(f"Target size: {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}")
            
            # 处理所有帧
            resized_frames = []
            durations = []
            
            frame_index = 0
            try:
                while True:
                    # 获取当前帧
                    frame = gif_image.copy()
                    
                    # 转换为RGB模式以便处理
                    if frame.mode != 'RGB':
                        frame = frame.convert('RGB')
                    
                    # 提取当前帧的四角像素颜色
                    corner_colors = self._extract_corner_colors(frame)
                    fill_color = self._calculate_fill_color(corner_colors)
                    
                    if frame_index == 0:
                        self.logger.info(f"Fill color (from corner pixels): RGB{fill_color}")
                    
                    # 等比例缩放当前帧
                    resized_frame = frame.resize((scaled_width, scaled_height), Image.NEAREST)
                    
                    # 创建目标尺寸的画布，用四角像素颜色填充
                    canvas = Image.new('RGB', (self.TARGET_WIDTH, self.TARGET_HEIGHT), fill_color)
                    
                    # 计算居中位置
                    paste_x = (self.TARGET_WIDTH - scaled_width) // 2
                    paste_y = (self.TARGET_HEIGHT - scaled_height) // 2
                    
                    # 将缩放后的帧粘贴到画布中心
                    canvas.paste(resized_frame, (paste_x, paste_y))
                    
                    # 转换为调色板模式以优化GIF文件大小
                    canvas_palette = canvas.quantize()
                    
                    resized_frames.append(canvas_palette)
                    
                    # 获取帧延迟时间
                    duration = gif_image.info.get('duration', 100)
                    durations.append(duration)
                    
                    frame_index += 1
                    gif_image.seek(gif_image.tell() + 1)
                    
            except EOFError:
                # 已处理完所有帧
                pass
            
            self.logger.info(f"Processed {len(resized_frames)} frames")
            
            # 创建新的GIF
            output_buffer = io.BytesIO()
            
            if len(resized_frames) > 0:
                # 获取循环次数
                loop = gif_image.info.get('loop', 0)
                
                # 保存GIF
                save_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': resized_frames[1:] if len(resized_frames) > 1 else [],
                    'duration': durations,
                    'loop': loop,
                    'optimize': False
                }
                
                resized_frames[0].save(output_buffer, **save_kwargs)
                
                result_bytes = output_buffer.getvalue()
                output_buffer.close()
                
                self.logger.info(f"Resized GIF: {len(resized_frames)} frames, "
                               f"size: {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}, "
                               f"output size: {len(result_bytes)} bytes")
                
                return result_bytes
            else:
                raise ValueError("No frames found in GIF")
                
        except Exception as e:
            self.logger.error(f"Failed to resize GIF: {str(e)}")
            raise
    
    def _extract_corner_colors(self, image: Image.Image) -> List[Tuple[int, int, int]]:
        """
        提取图像四角像素颜色
        
        Args:
            image: PIL图像对象（RGB模式）
            
        Returns:
            四角像素的RGB颜色列表 [(r, g, b), ...]
            顺序：左上角、右上角、左下角、右下角
        """
        # 确保是RGB模式
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
        else:
            rgb_image = image
        
        width, height = rgb_image.size
        
        # 提取四角像素
        corners = [
            rgb_image.getpixel((0, 0)),  # 左上角
            rgb_image.getpixel((width - 1, 0)),  # 右上角
            rgb_image.getpixel((0, height - 1)),  # 左下角
            rgb_image.getpixel((width - 1, height - 1))  # 右下角
        ]
        
        return corners
    
    def _calculate_fill_color(self, corner_colors: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        """
        根据四角像素计算填充颜色
        
        规则：
        1. 如果四角像素颜色相同，直接使用该颜色
        2. 如果四角像素颜色不同，使用RGB平均值
        
        Args:
            corner_colors: 四角像素的RGB颜色列表
            
        Returns:
            RGB颜色元组 (r, g, b)
        """
        if not corner_colors or len(corner_colors) == 0:
            # 默认使用黑色
            return (0, 0, 0)
        
        # 检查四角像素是否颜色相同
        first_color = corner_colors[0]
        all_same = all(color == first_color for color in corner_colors)
        
        if all_same:
            # 四角颜色相同，直接使用
            self.logger.debug(f"All corner pixels have the same color: RGB{first_color}")
            return first_color
        
        # 四角颜色不同，计算RGB平均值
        total_r = sum(color[0] for color in corner_colors)
        total_g = sum(color[1] for color in corner_colors)
        total_b = sum(color[2] for color in corner_colors)
        
        count = len(corner_colors)
        avg_r = int(total_r / count)
        avg_g = int(total_g / count)
        avg_b = int(total_b / count)
        
        avg_color = (avg_r, avg_g, avg_b)
        self.logger.debug(f"Corner pixels have different colors, using average: RGB{avg_color}")
        
        return avg_color


# 全局实例
_gif_resizer = None


def get_gif_resizer() -> GIFResizer:
    """获取GIF缩放器单例"""
    global _gif_resizer
    if _gif_resizer is None:
        _gif_resizer = GIFResizer()
    return _gif_resizer


def resize_gif_to_standard(gif_bytes: bytes) -> bytes:
    """
    便捷函数：将GIF缩放为标准尺寸(32x16)
    
    Args:
        gif_bytes: 原始GIF文件的字节数据
        
    Returns:
        缩放后的GIF文件字节数据
    """
    resizer = get_gif_resizer()
    return resizer.resize_gif_to_standard(gif_bytes)

