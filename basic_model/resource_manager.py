# -*- coding: utf-8 -*-
"""
游戏资源管理器 - 预加载和管理所有游戏素材
"""

import os
import sys

from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox
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
        
        self.dh_puzzle_images = {}
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
            self._preload_dh_puzzle_images()
            self._preload_background()
            self._preload_pet_image()
            self._preload_logo()
            self._preload_button()
            
            print("[ResourceManager] ✅ 所有素材预加载完成")
            
        except Exception as e:
            print(f"[ResourceManager] ❌ 预加载失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _preload_dh_puzzle_images(self):
        """预加载华容道数字图片 (1-25)"""
        print("[ResourceManager] 加载华容道图片...")
        
        images_dir = os.path.join(self._base_path, 'assets', 'images', 'sliding_puzzle')
        
        for i in range(1, 26):
            path = os.path.join(images_dir, f'{i}.png')
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.dh_puzzle_images[i] = pixmap
    
        print(f"[ResourceManager] ✓ 华容道图片已加载: {len(self.dh_puzzle_images)} 张")
    
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
    
    def get_dh_puzzle_image(self, num):
        """获取华容道数字图片"""
        return self.dh_puzzle_images.get(num)
    
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

    def create_icon_button(self, text="关闭", callback=None, size=None, parent=None):
        """
        创建带图标背景的按钮（图标+文字叠加）
        
        参数:
            text: 按钮文字
            callback: 点击回调
            size: QSize(width, height)，默认 (120, 100)
            parent: 父窗口
            
        返回:
            QWidget: 按钮容器
        """
        btn_container = QWidget(parent)
        if size is None:
            size = QSize(120, 100)
        btn_container.setFixedSize(size)
        btn_container.setCursor(Qt.PointingHandCursor)

        icon_label = QLabel(btn_container)
        icon_label.setGeometry(0, 0, size.width(), size.height())
        icon_label.setAlignment(Qt.AlignCenter)

        if self.button_pixmap and not self.button_pixmap.isNull():
            scaled = self.button_pixmap.scaled(
                size - QSize(8, 8), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(scaled)

        text_label = QLabel(text, btn_container)
        text_label.setGeometry(0, 0, size.width(), size.height())
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("""
            QLabel {
                color: #8a8070;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        font = text_label.font()
        font.setBold(True)
        font.setPointSize(16)
        text_label.setFont(font)
        text_label.raise_()

        def mousePressEvent(event):
            if callback and event.button() == Qt.LeftButton:
                callback()
        btn_container.mousePressEvent = mousePressEvent

        return btn_container

    MENU_BUTTON_STYLE = """
        QPushButton {
            background-color: #fad8d1;
            color: #8a8070;
            border: 1px solid #FFB6C1;
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 13px;
            font-weight: bold;
            text-align: center;
        }
        QPushButton:hover {
            background-color: #FFE4E9;
            border-color: #FFC0CB;
        }
        QPushButton:pressed {
            background-color: #FFC0CB;
            border-color: #FFB6C1;
        }
    """

    def create_menu_button(self, text="", callback=None, parent=None):
        """
        创建右键菜单风格的按钮
        
        参数:
            text: 按钮文字
            callback: 点击回调
            parent: 父窗口
            
        返回:
            QPushButton: 菜单按钮
        """
        btn = QPushButton(text, parent)
        btn.setStyleSheet(self.MENU_BUTTON_STYLE)
        if callback:
            btn.clicked.connect(callback)
        return btn

    COMBOBOX_STYLE = """
        QComboBox {
            background-color: #fad8d1;
            color: #8a8070;
            border: 1px solid #FFB6C1;
            border-radius: 4px;
            padding: 2px;
            font-weight: bold;
            font-size: 13px;
        }
        QComboBox:hover {
            background-color: #FFE8EC;
            border-color: #FFC0CB;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #8a8070;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #FFF5F7;
            color: #8a8070;
            selection-background-color: #fad8d1;
            selection-color: #8a8070;
            font-weight: bold;
        }
    """

    def create_styled_combobox(self, parent=None):
        """
        创建统一样式的下拉选择框
        
        参数:
            parent: 父窗口
            
        返回:
            QComboBox: 样式化下拉框
        """
        combo = QComboBox(parent)
        combo.setStyleSheet(self.COMBOBOX_STYLE)
        return combo

    def apply_combobox_style(self, combo):
        """为已有 QComboBox 应用统一样式"""
        combo.setStyleSheet(self.COMBOBOX_STYLE)

    CATEGORY_BTN_STYLE = """
        QPushButton {{
            background-color: #fad8d1;
            color: #8a8070;
            font-size: 12px;
            font-weight: bold;
            padding: 5px 12px;
            border-radius: 6px;
            border: 1px solid #FFB6C1;
        }}
        QPushButton:checked {{
            background-color: #FFB6C1;
            color: white;
            border-color: #FFB6C1;
        }}
        QPushButton:hover:!checked {{
            background-color: #FFE4E9;
            border-color: #FFC0CB;
        }}
    """

    def create_category_button(self, text="", selected=False, callback=None, parent=None):
        """
        创建分类/筛选按钮（支持选中状态）
        
        参数:
            text: 按钮文字
            selected: 是否选中（True=高亮样式，False=普通样式）
            callback: 点击回调
            parent: 父窗口
            
        返回:
            QPushButton: 可选中的分类按钮
        """
        btn = QPushButton(text, parent)
        btn.setObjectName("cat_btn")
        btn.setCheckable(True)
        btn.setChecked(selected)
        btn.setStyleSheet(self.CATEGORY_BTN_STYLE)
        if callback:
            btn.clicked.connect(callback)
        return btn

    def apply_category_style(self, btn):
        """为已有按钮应用分类按钮统一样式"""
        btn.setCheckable(True)
        btn.setStyleSheet(self.CATEGORY_BTN_STYLE)