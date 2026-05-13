# -*- coding: utf-8 -*-
"""
游戏资源管理器 - 预加载和管理所有游戏素材
"""

import os
import sys

from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
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
        self.coin_icon = None
        
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
            self._preload_coin_icon()
            
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

    def _preload_coin_icon(self):
        """预加载喵币图标"""
        path = os.path.join(self._base_path, 'assets', 'images', 'coin_icon.png')
        if os.path.exists(path):
            self.coin_icon = QIcon(path)
            print("[ResourceManager] ✓ 喵币图标已加载")
    
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

    def get_coin_icon(self):
        """获取喵币图标"""
        return self.coin_icon

    def create_coin_label(self, text="", icon_size=14, font_size=12, parent=None):
        """创建带喵币图标的标签（图标+文字水平排列）
        
        参数:
            text: 显示的文字（如金额数字）
            icon_size: 图标大小(px)
            font_size: 文字字号
            parent: 父窗口
            
        返回:
            QWidget: 包含图标+文字的容器，可通过 container._text_label.setText() 更新文字
        """
        container = QWidget(parent)
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignCenter)

        if self.coin_icon and not self.coin_icon.isNull():
            icon_label = QLabel(container)
            pixmap = self.coin_icon.pixmap(icon_size, icon_size)
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(icon_size, icon_size)
            layout.addWidget(icon_label)

        text_label = QLabel(text, container)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: #FFD700;
                font-size: {font_size}px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        layout.addWidget(text_label)

        container._text_label = text_label
        return container
    
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

    MENU_CONTAINER_STYLE = """
        QPushButton#action_btn {
            background-color: #fad8d1;
            color: #8a8070;
            border: 1px solid #FFB6C1;
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 13px;
            font-weight: bold;
            text-align: center;
        }
        QPushButton#action_btn:hover {
            background-color: #FFE4E9;
            border-color: #FFC0CB;
        }
        QPushButton#action_btn:pressed {
            background-color: #FFC0CB;
            border-color: #FFB6C1;
        }
    """

    MENU_CATEGORY_LABEL_STYLE = """QLabel#category_label {{
                color: #8a8070;
                font-size: {font_size}px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                min-height: {min_height}px;
                background: transparent;
            }}"""

    MENU_FRAME_STYLE = """QFrame#menu_container {{
                background-image: url("{bg_path}");
                background-color: rgba(43, 43, 54, 0.95);
                border-radius: 15px;
                border: 2px solid rgba(106, 106, 126, 0.9);
            }}
            QWidget#category_container {{
                background: transparent;
            }}"""

    def get_menu_style(self, bg_path="", title_font_size=18, title_height=32):
        return self.MENU_CONTAINER_STYLE + "\n" + self.MENU_FRAME_STYLE.format(
            bg_path=bg_path
        ) + "\n" + self.MENU_CATEGORY_LABEL_STYLE.format(
            font_size=title_font_size,
            min_height=title_height
        )

    COMBOBOX_SIZE_MAP = {
        "large": (150, 40, 15),
        "medium": (120, 32, 13),
        "small": (90, 26, 11),
    }

    COMBOBOX_STYLE = """
        QComboBox {{
            background-color: #fad8d1;
            color: #8a8070;
            border: 1px solid #FFB6C1;
            border-radius: 4px;
            padding: 2px;
            padding-left: 5px;
            font-weight: bold;
            font-size: {font_size}px;
        }}
        QComboBox:hover {{
            background-color: #FFE8EC;
            border-color: #FFC0CB;
        }}
        QComboBox::drop-down {{
            border: none;
            width: {arrow_w}px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: {aw}px solid transparent;
            border-right: {aw}px solid transparent;
            border-top: {ah}px solid #8a8070;
            margin-right: {amr}px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #FFF5F7;
            color: #8a8070;
            selection-background-color: #fad8d1;
            selection-color: #8a8070;
            font-weight: bold;
        }}
    """

    def _build_combobox_style(self, size="small"):
        """根据尺寸构建下拉框样式"""
        w, h, fs = self.COMBOBOX_SIZE_MAP.get(size, self.COMBOBOX_SIZE_MAP["small"])
        aw = max(3, fs // 3)
        ah = max(4, fs // 2 + 2)
        amr = max(5, fs)
        return self.COMBOBOX_STYLE.format(font_size=fs, arrow_w=aw * 3 + 10,
                                          aw=aw, ah=ah, amr=amr)

    def create_styled_combobox(self, parent=None, size="small"):
        combo = QComboBox(parent)
        w, h, fs = self.COMBOBOX_SIZE_MAP.get(size, self.COMBOBOX_SIZE_MAP["small"])
        combo.setFixedWidth(w)
        combo.setFixedHeight(h)
        style = self._build_combobox_style(size)
        combo.setStyleSheet(style)
        return combo

    def apply_combobox_style(self, combo, size="small"):
        w, h, fs = self.COMBOBOX_SIZE_MAP.get(size, self.COMBOBOX_SIZE_MAP["small"])
        if not combo.minimumWidth():
            combo.setFixedWidth(w)
        if not combo.minimumHeight():
            combo.setFixedHeight(h)
        style = self._build_combobox_style(size)
        combo.setStyleSheet(style)

    ACTION_BTN_WARNING_STYLE = """
        QPushButton {
            background-color: #d4a5a5;
            color: #8a4a4a;
            border: none;
            padding: 8px 10px;
            font-weight: bold;
            font-size: 13px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #e4b5b5;
        }
    """

    BUTTON_SIZE_MAP = {
        "large": (160, 40, 15),
        "medium": (120, 32, 13),
        "small": (90, 26, 11),
    }

    def create_action_button(self, text="", callback=None, size="small",
                             special_style=None, selected=False, parent=None):
        """
        创建通用操作按钮（支持选中状态 + 三种尺寸）
        
        参数:
            text: 按钮文字
            callback: 点击回调
            size: 尺寸 "large"(大) / "medium"(中) / "small"(小)
            special_style: 特殊样式类型 ("warning"=红色警告样式)
            selected: 是否选中（True=高亮粉色背景+白字）
            parent: 父窗口
            
        返回:
            QPushButton: 操作按钮
        """
        btn_w, btn_h, font_size = self.BUTTON_SIZE_MAP.get(size, self.BUTTON_SIZE_MAP["medium"])
        
        btn = QPushButton(text, parent)
        btn.setObjectName("action_btn")
        btn.setFixedWidth(btn_w)
        btn.setFixedHeight(btn_h)
        
        if special_style == "warning":
            style = self.ACTION_BTN_WARNING_STYLE
        else:
            style = """
                QPushButton#action_btn {
                    background-color: #fad8d1;
                    color: #8a8070;
                    border: 1px solid #FFB6C1;
                    border-radius: 6px;
                    padding: 8px 10px;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton#action_btn:hover {
                    background-color: #FFE4E9;
                    border-color: #FFC0CB;
                }
                QPushButton#action_btn:pressed {
                    background-color: #FFC0CB;
                    border-color: #FFB6C1;
                }
            """
        
        if selected:
            btn.setCheckable(True)
            btn.setChecked(True)
            style += f"""
                QPushButton#action_btn {{
                    padding: {max(4, font_size // 3)}px {max(8, font_size)}px;
                    font-size: {font_size}px;
                }}
                QPushButton#action_btn:checked {{
                    background-color: #FFB6C1;
                    color: white;
                    border-color: #FFB6C1;
                }}
                QPushButton#action_btn:hover:!checked {{
                    background-color: #FFE4E9;
                    border-color: #FFC0CB;
                }}
            """
        else:
            style = style.replace("font-size: 13px;", f"font-size: {font_size}px;")
            style = style.replace("padding: 8px 10px;", f"padding: {max(4, font_size // 3)}px {max(8, font_size)}px;")
        
        btn.setStyleSheet(style)
        
        if callback:
            btn.clicked.connect(callback)
        
        return btn