# -*- coding: utf-8 -*-
"""
通用样式配置文件

存放所有窗口和组件的通用样式配置，便于统一管理和修改
"""

# ===== 颜色配置 =====
class Colors:
    """颜色配置"""
    
    # 主题色
    PRIMARY = "#5a7a9a"
    PRIMARY_HOVER = "#6a8aaa"
    
    # 警告色
    DANGER = "#8a4a4a"
    DANGER_HOVER = "#aa5a5a"
    
    # 成功色
    SUCCESS = "#4a7a4a"
    SUCCESS_HOVER = "#5a9a5a"
    
    # 背景色
    BACKGROUND = "#2b2b36"
    BACKGROUND_LIGHT = "#3a3a4e"
    BACKGROUND_DARK = "#1b1b26"
    
    # 文字颜色
    TEXT_WHITE = "#ffffff"
    TEXT_GRAY = "#aaaaaa"
    TEXT_DARK = "#8a8070"
    TEXT_BLACK = "#333333"
    
    # 边框颜色
    BORDER = "#5a5a6e"
    BORDER_LIGHT = "#8a8a9e"
    
    # 粉色系（按钮等）
    PINK_LIGHT = "#fad8d1"
    PINK_MEDIUM = "#FFE4E9"
    PINK_DARK = "#FFC0CB"
    PINK_TEXT = "#8a8070"
    
    # 其他
    GOLD = "#FFD700"

# ===== 字体配置 =====
class Fonts:
    """字体配置"""
    FAMILY = "\"Microsoft YaHei\", \"SimHei\", sans-serif"
    SIZE_SMALL = 12
    SIZE_NORMAL = 14
    SIZE_LARGE = 18
    SIZE_TITLE = 22

# ===== 圆角配置 =====
class Rounded:
    """圆角配置"""
    SMALL = 4
    NORMAL = 6
    LARGE = 8
    EXTRA_LARGE = 15

# ===== 按钮样式 =====
class ButtonStyles:
    """按钮样式配置"""
    
    # 粉色按钮（华容道等）
    PINK_BUTTON = {
        "background_color": Colors.PINK_LIGHT,
        "color": Colors.PINK_TEXT,
        "border_color": Colors.PINK_DARK,
        "hover_background": "#FFE8EC",
        "hover_border": Colors.PINK_DARK,
        "border_radius": Rounded.NORMAL,
        "padding": "8px 10px",
        "font_size": 13,
        "font_weight": "bold"
    }
    
    # 控制按钮
    CONTROL_BUTTON = {
        "background_color": Colors.PRIMARY,
        "color": Colors.TEXT_WHITE,
        "border_color": "none",
        "hover_background": Colors.PRIMARY_HOVER,
        "border_radius": Rounded.NORMAL,
        "padding": "10px",
        "font_size": 14
    }
    
    # 关闭按钮
    CLOSE_BUTTON = {
        "background_color": Colors.DANGER,
        "color": Colors.TEXT_WHITE,
        "border_color": "none",
        "hover_background": Colors.DANGER_HOVER,
        "border_radius": Rounded.NORMAL,
        "padding": "10px",
        "font_size": 14
    }
