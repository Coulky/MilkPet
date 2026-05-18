# -*- coding: utf-8 -*-
"""
宠物对话窗口组件

功能：
- 显示宠物对话内容
- 使用 talk.png 作为背景图
- 自动定位到桌宠上方
- 支持自动关闭和手动关闭
"""

import sys
import os

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont


class TalkWindow(QWidget):
    """
    对话窗口类
    
    属性：
    - text: 对话文本内容
    - duration: 显示时长（秒）
    - parent_pet: 父级桌宠窗口（用于定位）
    
    方法：
    - show_talk(text): 显示对话内容
    - close_talk(): 关闭对话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_pet = parent
        self.duration = 3

        self._setup_window()
        self._setup_ui()

        # 自动关闭定时器
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.close_talk)

    def _get_resource_path(self, filename):
        """获取资源文件路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            # 从 basic_model 目录向上两级到达项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        path = os.path.join(base_path, 'assets', filename)
        
        if os.path.exists(path):
            return path
        
        print(f"[WARN] TalkWindow: 未找到资源文件 {filename}")
        return None

    def _setup_window(self):
        """设置窗口属性"""
        flags = (Qt.Window | Qt.FramelessWindowHint | Qt.Tool | 
                Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_QuitOnClose, False)

    def _setup_ui(self):
        """设置UI界面"""
        # 使用绝对定位布局，让文字浮在背景图上方
        self.container = QWidget(self)
        
        # 背景图片（底层）
        self.bg_label = QLabel(self.container)
        bg_path = self._get_resource_path('talk.png')
        
        if bg_path:
            pixmap = QPixmap(bg_path)
            if not pixmap.isNull():
                self.bg_pixmap = pixmap
        
        # 文本标签（顶层，浮在背景上）
        self.text_label = QLabel(self.container)
        self.text_label.setObjectName("talk_text")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        
        font = QFont("Microsoft YaHei", 11)
        font.setBold(True)
        self.text_label.setFont(font)
        
        self.text_label.setStyleSheet("""
            QLabel#talk_text {
                color: #333333;
                background: transparent;
                border: none;
            }
        """)

    def show_talk(self, text: str, duration: int = 3, offset_y: int = -40):
        """
        显示对话内容
        
        参数：
            text: 对话文本
            duration: 显示时长（秒）
            offset_y: 相对于桌宠顶部的Y偏移量（负数表示在上方）
        """
        self.duration = duration

        # 设置文本
        self.text_label.setText(text)
        self.text_label.adjustSize()

        # 计算窗口大小（根据文本内容，留出内边距）
        padding = 20
        text_width = self.text_label.sizeHint().width() + padding * 2
        text_height = self.text_label.sizeHint().height() + padding * 1.5

        window_width = max(150, min(text_width, 300))
        window_height = max(50, int(text_height))

        # 设置容器和窗口大小
        self.container.setFixedSize(window_width, window_height)
        self.setFixedSize(window_width, window_height)

        # 设置背景图大小和位置（铺满整个窗口）
        if hasattr(self, 'bg_pixmap'):
            scaled_bg = self.bg_pixmap.scaled(
                window_width,
                window_height,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled_bg)
            self.bg_label.setGeometry(0, 0, window_width, window_height)

        # 设置文字位置（居中显示）
        text_x = (window_width - self.text_label.width()) // 2
        text_y = (window_height - self.text_label.height()) // 2
        self.text_label.setGeometry(text_x, text_y, 
                                   self.text_label.width(), 
                                   self.text_label.height())

        # 定位窗口（在父窗口上方）
        if self.parent_pet:
            pet_x = self.parent_pet.x()
            pet_y = self.parent_pet.y()
            pet_width = self.parent_pet.width()

            # 水平居中于桌宠
            x = pet_x + (pet_width - window_width) // 2
            
            # 在桌宠上方，加上偏移量
            y = pet_y + offset_y - window_height

            self.move(x, y)

        # 显示窗口
        self.show()
        self.raise_()

        # 启动自动关闭定时器
        self.auto_close_timer.start(duration * 1000)

    def close_talk(self):
        """关闭对话框"""
        self.auto_close_timer.stop()
        self.hide()

    def is_showing(self) -> bool:
        """检查对话框是否正在显示"""
        return self.isVisible()
