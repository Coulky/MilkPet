# -*- coding: utf-8 -*-
"""
桌宠显示模块 - 负责桌宠窗口的显示、图片加载和基础UI

独立模块：避免其他功能修改影响核心显示逻辑
"""

import sys
import os

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap


class PetDisplay(QWidget):
    """
    桌宠显示核心类
    
    职责：
    - 桌宠窗口创建和属性设置
    - 图片加载和显示
    - 基础UI布局
    """
    
    def __init__(self):
        super().__init__()
        
        self.pet_image_path = None
        self.pet_label = None
        
        # 初始化显示
        self._load_pet_image()
        self._setup_window()
        self._setup_ui()
        self._move_to_bottom_right()
    
    def _find_resource_path(self, filename):
        """
        查找资源文件的路径
        
        参数:
            filename: 资源文件名（如 'milk.png', 'logo.png'）
            
        返回:
            str: 资源文件的完整路径，如果不存在则返回 None
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            # 获取项目根目录（向上两级：games/pet_display.py -> games/ -> 项目根）
            current_file = os.path.abspath(__file__)
            base_path = os.path.dirname(os.path.dirname(current_file))
        
        path = os.path.join(base_path, 'assets', 'images', filename)
        
        if os.path.exists(path):
            return path
        
        print(f"[WARN] 未找到资源文件: {filename}, 路径: {path}")
        return None
    
    def _load_pet_image(self):
        """加载桌宠图片"""
        self.pet_image_path = self._find_resource_path('milk.png')
        
        if self.pet_image_path:
            print(f"[OK] 找到桌宠图片: {self.pet_image_path}")
        else:
            print(f"[DEBUG] sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Milk Pet")
        
        flags = (Qt.FramelessWindowHint | 
                Qt.WindowStaysOnTopHint | 
                Qt.Tool)
        self.setWindowFlags(flags)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        
        screen = QApplication.instance().primaryScreen().availableGeometry()
        max_size = min(screen.width() * 0.3, screen.height() * 0.4, 350)
        self.setFixedSize(int(max_size), int(max_size * 1.2))
    
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.pet_label = QLabel()
        self.pet_label.setAlignment(Qt.AlignCenter)
        
        if self.pet_image_path and os.path.exists(self.pet_image_path):
            pixmap = QPixmap(self.pet_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pet_label.setPixmap(scaled_pixmap)
                print("[OK] 桌宠图片加载成功")
            else:
                self.pet_label.setText("Milk")
                self.pet_label.setStyleSheet("font-size: 150px;")
                print("[WARN] 图片加载失败，使用占位符")
        else:
            self.pet_label.setText("Milk")
            self.pet_label.setStyleSheet("font-size: 150px;")
        
        layout.addWidget(self.pet_label)
        self.setLayout(layout)
    
    def _move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 40
        self.move(x, y)
    
    def get_logo_path(self):
        """获取logo图标路径"""
        return self._find_resource_path('logo.png')
    
    def update_pet_image(self, image_path=None):
        """
        更新桌宠图片
        
        参数:
            image_path: 新的图片路径，如果为None则重新加载默认图片
        """
        if not image_path:
            self._load_pet_image()
        else:
            if os.path.exists(image_path):
                self.pet_image_path = image_path
            else:
                print(f"[ERROR] 图片不存在: {image_path}")
                return
        
        if self.pet_label and self.pet_image_path and os.path.exists(self.pet_image_path):
            pixmap = QPixmap(self.pet_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pet_label.setPixmap(scaled_pixmap)
                print("[OK] 桌宠图片已更新")