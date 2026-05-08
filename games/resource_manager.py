# -*- coding: utf-8 -*-
"""
游戏资源管理器 - 预加载和管理所有游戏素材
"""

import os
import sys

from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QSize


class ResourceManager:
    """统一管理所有游戏的素材资源"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.huarong_images = {}
        self.sudoku_images = {}
        self.background_image = None
        self.pet_image = None
        self.logo_icon = None
        self.button_pixmap = None
        
        self._base_path = self._get_base_path()
    
    @staticmethod
    def _get_base_path():
        """获取基础路径"""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def preload_all(self):
        """预加载所有游戏素材"""
        print("[ResourceManager] 开始预加载所有素材...")
        
        try:
            self._preload_huarong_images()
            self._preload_background()
            self._preload_pet_image()
            self._preload_logo()
            self._preload_button()
            
            print("[ResourceManager] ✅ 所有素材预加载完成")
            
        except Exception as e:
            print(f"[ResourceManager] ❌ 预加载失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _preload_huarong_images(self):
        """预加载华容道数字图片 (1-25)"""
        print("[ResourceManager] 加载华容道图片...")
        
        images_dir = os.path.join(self._base_path, 'assets', 'images', 'sliding_puzzle')
        
        for i in range(1, 26):
            path = os.path.join(images_dir, f'{i}.png')
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.huarong_images[i] = pixmap
    
        print(f"[ResourceManager] ✓ 华容道图片已加载: {len(self.huarong_images)} 张")
    
    def _preload_background(self):
        """预加载背景图片"""
        path = os.path.join(self._base_path, 'assets', 'images', 'background.png')
        if os.path.exists(path):
            self.background_image = QPixmap(path)
            print("[ResourceManager] ✓ 背景图片已加载")
    
    def _preload_pet_image(self):
        """预加载桌宠图片"""
        path = os.path.join(self._base_path, 'assets', 'images', 'milk.png')
        if os.path.exists(path):
            self.pet_image = QPixmap(path)
            print("[ResourceManager] ✓ 桌宠图片已加载")
    
    def _preload_logo(self):
        """预加载 Logo 图标"""
        path = os.path.join(self._base_path, 'assets', 'images', 'logo.png')
        if os.path.exists(path):
            self.logo_icon = QIcon(path)
            print("[ResourceManager] ✓ Logo 图标已加载")
    
    def _preload_button(self):
        """预加载按钮背景图片"""
        path = os.path.join(self._base_path, 'assets', 'images', 'button.png')
        if os.path.exists(path):
            self.button_pixmap = QPixmap(path)
            print("[ResourceManager] ✓ 按钮图片已加载")
    
    def get_huarong_image(self, num):
        """获取华容道数字图片"""
        return self.huarong_images.get(num)
    
    def get_background_path(self):
        """获取背景图片路径"""
        return os.path.join(self._base_path, 'assets', 'images', 'background.png').replace('\\', '/')
    
    def get_pet_image(self):
        """获取桌宠图片"""
        return self.pet_image
    
    def get_logo_icon(self):
        """获取 Logo 图标"""
        return self.logo_icon
    
    def create_styled_button(self, text="", callback=None, size=None, parent=None):
        """
        创建统一样式的按钮（文字显示在图标中间）
        
        参数:
            text: 按钮显示的文字（居中覆盖在图标上）
            callback: 点击时调用的方法
            size: 按钮大小 QSize(width, height)，默认 (120, 100)
            parent: 父窗口
            
        返回:
            QWidget: 已设置好样式的按钮容器
        """
        # 创建容器
        btn_container = QWidget(parent)
        
        if size is None:
            size = QSize(120, 100)  # 默认大小（放大一倍）
        btn_container.setFixedSize(size)
        btn_container.setCursor(Qt.PointingHandCursor)
        
        # 背景图标标签（底层）
        icon_label = QLabel(btn_container)
        icon_label.setGeometry(0, 0, size.width(), size.height())
        icon_label.setAlignment(Qt.AlignCenter)
        
        if self.button_pixmap and not self.button_pixmap.isNull():
            scaled_pixmap = self.button_pixmap.scaled(
                size - QSize(8, 8),  # 图标稍小，留出边距
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            icon_label.setPixmap(scaled_pixmap)
        
        # 文字标签（上层，居中覆盖在图标上）
        text_label = QLabel(text, btn_container)
        
        # 根据按钮大小自动计算字号
        font_size = 16  # 固定16px，与"难度"标签一致
        
        text_label.setStyleSheet(f"""
            QLabel {{
                color: #8a8070;  /* 棋盘描边颜色 */
                font-size: {font_size}px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        
        # 强制设置字体为粗体（CSS可能不生效）
        from PyQt5.QtGui import QFont
        font = text_label.font()
        font.setBold(True)
        font.setPointSize(font_size)
        text_label.setFont(font)
        
        # 绝对定位：文字完全居中显示在图标上
        text_label.setGeometry(0, 0, size.width(), size.height())
        text_label.setAlignment(Qt.AlignCenter)  # 水平和垂直都居中
        text_label.raise_()  # 提升到最上层
        
        # 存储回调函数
        if callback:
            btn_container._callback = callback
        
        # 鼠标点击事件
        def mousePressEvent(event):
            if callback and event.button() == Qt.LeftButton:
                callback()
        
        btn_container.mousePressEvent = mousePressEvent
        
        # hover 效果
        def enterEvent(event):
            if self.button_pixmap and not self.button_pixmap.isNull():
                scaled_pixmap = self.button_pixmap.scaled(
                    size - QSize(4, 4),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                # 添加半透明白色效果
                painter_effect = QPainter(scaled_pixmap)
                painter_effect.fillRect(scaled_pixmap.rect(), QColor(255, 255, 255, 25))
                painter_effect.end()
                icon_label.setPixmap(scaled_pixmap)
        
        def leaveEvent(event):
            if self.button_pixmap and not self.button_pixmap.isNull():
                scaled_pixmap = self.button_pixmap.scaled(
                    size - QSize(4, 4),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                icon_label.setPixmap(scaled_pixmap)
        
        btn_container.enterEvent = enterEvent
        btn_container.leaveEvent = leaveEvent
        
        return btn_container