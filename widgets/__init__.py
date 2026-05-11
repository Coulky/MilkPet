# -*- coding: utf-8 -*-
"""
窗口组件模块

包含通用的UI组件：
- game_success_window.py: 游戏成功窗口
- dialog.py: 统一弹框（完成/确认/警告/游戏失败）
"""

from .game_success_window import GameSuccessWindow
from .dialog import CompleteDialog, ConfirmDialog, WarningDialog, GameFailDialog

__all__ = [
    'GameSuccessWindow',
    'CompleteDialog',
    'ConfirmDialog',
    'WarningDialog',
    'GameFailDialog',
]