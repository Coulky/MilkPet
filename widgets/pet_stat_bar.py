# -*- coding: utf-8 -*-
"""
宠物属性进度条组件

自定义进度条，用于右键菜单中显示桌宠属性：
- 底色 = 字体颜色 (#8a8070)
- 边框 = 华容道按钮边框颜色 (#FFB6C1)
- 进度填充 = progress_bar.png
- 中间显示当前值 (白色文字)
- 保护状态下：绿色边框 + 绿色倒计时
"""

import sys
import os
import time

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QRectF, QTimer
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
    PROTECTION_BORDER_COLOR = QColor("#4CAF50")
    PROTECTION_TEXT_COLOR = QColor("#4CAF50")

    def __init__(self, label_text: str, max_value: int = 100, parent=None):
        super().__init__(parent)
        self._label_text = label_text
        self._max_value = max_value
        self._current_value = 0.0

        # 保护状态相关
        self._is_protected = False
        self._protection_end_time = 0.0  # 保护结束时间戳
        self._protection_duration = 0.0   # 保护总时长（秒）

        # 倒计时更新定时器
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._update_countdown)

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

    def set_protection(self, duration: float):
        """设置保护状态（duration单位：秒）"""
        if duration > 0:
            self._is_protected = True
            self._protection_duration = duration
            self._protection_end_time = time.time() + duration
            self._countdown_timer.start(1000)  # 每秒更新倒计时
            self.update()
        else:
            self._clear_protection()

    def _clear_protection(self):
        """清除保护状态"""
        self._is_protected = False
        self._protection_end_time = 0.0
        self._protection_duration = 0.0
        self._countdown_timer.stop()
        self.update()

    def _update_countdown(self):
        """更新倒计时"""
        if not self._is_protected:
            self._countdown_timer.stop()
            return

        current_time = time.time()
        if current_time >= self._protection_end_time:
            self._clear_protection()
        else:
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

        # 边框（根据保护状态选择颜色）
        border_color = self.PROTECTION_BORDER_COLOR if self._is_protected else self.BORDER_COLOR
        border_path = QPainterPath()
        border_path.addRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), radius, radius)
        pen = QPen(border_color, 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(border_path)

        # 中间文字（包含数值和可能的倒计时）
        base_text = f"{int(self._current_value)}/{self._max_value}"

        if self._is_protected:
            # 计算剩余时间
            remaining = max(0, self._protection_end_time - time.time())
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            countdown_text = f"({minutes:02d}:{seconds:02d})"

            # 绘制基础数值（白色）
            font = QFont("Microsoft YaHei", 9)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.TEXT_COLOR)

            # 计算文本位置，居中显示
            full_text = f"{base_text} {countdown_text}"
            text_rect = QRectF(0, 0, w, h)
            painter.drawText(text_rect, Qt.AlignCenter, full_text)

            # 注意：这里简化处理，实际绘制时需要分别设置颜色
            # 由于QPainter不支持富文本，我们使用简单方案：整体绘制后用不同颜色覆盖
        else:
            font = QFont("Microsoft YaHei", 9)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.TEXT_COLOR)
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, base_text)

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

    def set_protection(self, duration: float):
        """设置保护状态（duration单位：秒）"""
        self.bar.set_protection(duration)
