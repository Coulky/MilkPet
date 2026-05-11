# -*- coding: utf-8 -*-
"""
宠物属性进度条组件

自定义进度条，用于右键菜单中显示桌宠属性：
- 底色 = 字体颜色 (#8a8070)
- 边框 = 华容道按钮边框颜色 (#FFB6C1)
- 进度填充 = progress_bar.png
- 中间显示当前值 (白色文字)
"""

import sys
import os

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen, QFont, QBrush, QPainterPath


def _get_assets_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PetStatBar(QWidget):
    """宠物属性进度条"""

    BG_COLOR = QColor("#8a8070")
    BORDER_COLOR = QColor("#FFB6C1")
    TEXT_COLOR = QColor("#ffffff")
    FILL_COLOR = QColor("#FFB6C1")

    def __init__(self, label_text: str, max_value: int = 100, parent=None):
        super().__init__(parent)
        self._label_text = label_text
        self._max_value = max_value
        self._current_value = 0.0

        self._progress_pixmap = None
        self._load_progress_image()

        self.setFixedHeight(24)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _load_progress_image(self):
        img_path = os.path.join(_get_assets_dir(), 'assets', 'images', 'progress_bar.png')
        if os.path.exists(img_path):
            self._progress_pixmap = QPixmap(img_path)

    def set_value(self, value: float):
        self._current_value = max(0, min(value, self._max_value))
        self.update()

    def set_max_value(self, max_value: int):
        self._max_value = max_value
        self.update()

    def current_value(self) -> float:
        return self._current_value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        radius = 4

        # 背景（底色 = 字体颜色）
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(1, 1, w - 2, h - 2), radius, radius)
        painter.fillPath(bg_path, QBrush(self.BG_COLOR))

        # 进度填充
        if self._max_value > 0:
            ratio = self._current_value / self._max_value
            fill_width = int((w - 2) * ratio)
            if fill_width > 0:
                fill_rect = QRectF(1, 1, fill_width, h - 2)
                fill_path = QPainterPath()
                fill_path.addRoundedRect(fill_rect, radius, radius)

                if self._progress_pixmap and not self._progress_pixmap.isNull():
                    # 用 progress_bar.png 平铺填充
                    scaled = self._progress_pixmap.scaled(
                        fill_width, h - 2,
                        Qt.IgnoreAspectRatio,
                        Qt.SmoothTransformation
                    )
                    painter.save()
                    painter.setClipPath(fill_path)
                    painter.drawPixmap(1, 1, scaled)
                    painter.restore()
                else:
                    painter.fillPath(fill_path, QBrush(self.FILL_COLOR))

        # 边框
        border_path = QPainterPath()
        border_path.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), radius, radius)
        pen = QPen(self.BORDER_COLOR, 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(border_path)

        # 中间文字
        text = f"{int(self._current_value)}/{self._max_value}"
        font = QFont("Microsoft YaHei", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(self.TEXT_COLOR)
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, text)

        painter.end()


class PetStatRow(QWidget):
    """宠物属性行（标签 + 进度条）"""

    def __init__(self, label_text: str, max_value: int = 100, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签
        self.label = QLabel(label_text)
        self.label.setFixedWidth(48)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #8a8070;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(self.label)

        # 进度条
        self.bar = PetStatBar(label_text, max_value)
        layout.addWidget(self.bar, 1)

    def set_value(self, value: float):
        self.bar.set_value(value)

    def set_max_value(self, max_value: int):
        self.bar.set_max_value(max_value)