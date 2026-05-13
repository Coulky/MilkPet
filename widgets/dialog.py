# -*- coding: utf-8 -*-
"""
统一弹框组件

4种类型：
- CompleteDialog  完成弹框（单按钮：完成）
- ConfirmDialog   确认弹框（双按钮：取消/确认）
- WarningDialog   警告弹框（单按钮：我知道了）
- GameFailDialog  游戏失败弹框（双按钮：复活/放弃）
"""

import sys
import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer


DIALOG_STYLES = {
    "complete": {
        "title_color": "#FFD700",
        "title_icon": "\U0001f389",
        "title_text": "\u5b8c\u6210",
        "border": "#6a9a4a",
        "bg_tint": "rgba(74, 122, 74, 0.15)",
        "btn_bg": "#5a7a9a",
        "btn_bg_hover": "#6a8aaa",
    },
    "confirm": {
        "title_color": "#7ab8ff",
        "title_icon": "\u2753",
        "title_text": "\u786e\u8ba4\u64cd\u4f5c",
        "border": "#5a7a9a",
        "bg_tint": "rgba(90, 122, 154, 0.12)",
        "btn_bg": "#5a7a9a",
        "btn_bg_hover": "#6a8aaa",
    },
    "warning": {
        "title_color": "#FFB347",
        "title_icon": "\u26a0\ufe0f",
        "title_text": "\u8b66\u544a",
        "border": "#cc8833",
        "bg_tint": "rgba(204, 136, 51, 0.12)",
        "btn_bg": "#cc8833",
        "btn_bg_hover": "#dd9944",
    },
    "game_fail": {
        "title_color": "#ff6b6b",
        "title_icon": "\U0001f480",
        "title_text": "\u6e38\u620f\u5931\u8d25",
        "border": "#aa4444",
        "bg_tint": "rgba(170, 68, 68, 0.12)",
        "btn_primary": "#aa5555",
        "btn_primary_hover": "#bb6666",
        "btn_secondary": "#666666",
        "btn_secondary_hover": "#777777",
    },
}


class BaseDialog(QWidget):
    """弹框基类"""

    confirmed = pyqtSignal()
    cancelled = pyqtSignal()
    secondary = pyqtSignal()

    def __init__(self, title: str, message: str, dialog_type: str = "confirm", parent=None):
        super().__init__(parent)

        self.title_text = title
        self.message = message
        self.dialog_type = dialog_type
        self.style_cfg = DIALOG_STYLES.get(dialog_type, DIALOG_STYLES["confirm"])

        self._setup_ui()
        self._center_on_screen()

        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self.close)
        self._auto_close_timer.start(2500)

    def _get_bg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'images', 'background.png').replace('\\', '/')

    def _setup_ui(self):
        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        from basic_model.resource_manager import ResourceManager
        resource_manager = ResourceManager()
        self.setWindowIcon(resource_manager.logo_icon)

        container = QFrame(self)
        container.setObjectName("container")
        cfg = self.style_cfg

        border_color = cfg["border"]
        bg_tint = cfg["bg_tint"]

        container.setStyleSheet(f"""
            QFrame#container {{
                background-image: url("{self._get_bg_path()}");
                background-color: rgba(43, 43, 54, 0.98);
                border-radius: 16px;
                border: 2px solid {border_color};
            }}
            QLabel#dlg_title {{
                color: {cfg['title_color']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
            QLabel#dlg_message {{
                color: #dddddd;
                font-size: 14px;
                background: transparent;
                line-height: 1.5;
            }}
            QLabel#dlg_sub {{
                color: #999999;
                font-size: 12px;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(16)

        icon_title = f"{cfg['title_icon']} {self.title_text}"
        title_label = QLabel(icon_title)
        title_label.setObjectName("dlg_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        msg_label = QLabel(self.message)
        msg_label.setObjectName("dlg_message")
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._build_buttons(btn_layout, cfg)
        layout.addLayout(btn_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        container.adjustSize()
        self.adjustSize()

    def _build_buttons(self, btn_layout: QHBoxLayout, cfg: dict):
        pass

    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)


class CompleteDialog(BaseDialog):
    """完成弹框 - 单按钮（完成）"""

    def _build_buttons(self, btn_layout, cfg):
        btn = QPushButton("\u5b8c\u6210")
        btn.setFixedSize(120, 36)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cfg['btn_bg']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {cfg['btn_bg_hover']}; }}
            QPushButton:pressed {{ background-color: {cfg['btn_bg']}; }}
        """)
        btn.clicked.connect(lambda: [self.confirmed.emit(), self.close()])
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()


class ConfirmDialog(BaseDialog):
    """确认弹框 - 双按钮（取消/确认）"""

    def _build_buttons(self, btn_layout, cfg):
        cancel_btn = QPushButton("\u53d6\u6d88")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #555566;
                color: #cccccc;
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #666677; }
            QPushButton:pressed { background-color: #444455; }
        """)
        cancel_btn.clicked.connect(lambda: [self.cancelled.emit(), self.close()])
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("\u786e\u8ba4")
        confirm_btn.setFixedSize(100, 36)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cfg['btn_bg']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {cfg['btn_bg_hover']}; }}
            QPushButton:pressed {{ background-color: {cfg['btn_bg']}; }}
        """)
        confirm_btn.clicked.connect(lambda: [self.confirmed.emit(), self.close()])
        btn_layout.addWidget(confirm_btn)


class WarningDialog(BaseDialog):
    """警告弹框 - 单按钮（我知道了）"""

    def _build_buttons(self, btn_layout, cfg):
        btn = QPushButton("\u6211\u77e5\u9053\u4e86")
        btn.setFixedSize(120, 36)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cfg['btn_bg']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {cfg['btn_bg_hover']}; }}
            QPushButton:pressed {{ background-color: {cfg['btn_bg']}; }}
        """)
        btn.clicked.connect(lambda: [self.confirmed.emit(), self.close()])
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()


class GameFailDialog(BaseDialog):
    """游戏失败弹框 - 双按钮（复活/放弃）"""

    revive_clicked = pyqtSignal()
    abandon_clicked = pyqtSignal()

    def __init__(self, title: str, message: str, dialog_type: str = "game_fail",
                 parent=None, can_revive: bool = True):
        self.can_revive = can_revive
        super().__init__(title, message, dialog_type, parent)

    def _build_buttons(self, btn_layout, cfg):
        revive_btn = QPushButton("⭐ 复活")
        revive_btn.setFixedSize(110, 36)
        if not self.can_revive:
            revive_btn.setEnabled(False)
            revive_btn.setToolTip("复活币不足")
        revive_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cfg['btn_primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {cfg['btn_primary_hover']}; }}
            QPushButton:pressed {{ background-color: {cfg['btn_primary']}; }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
            }}
        """)
        revive_btn.clicked.connect(lambda: [self.revive_clicked.emit(), self.close()])
        btn_layout.addWidget(revive_btn)

        abandon_btn = QPushButton("放弃")
        abandon_btn.setFixedSize(100, 36)
        abandon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {cfg['btn_secondary']};
                color: #aaaaaa;
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {cfg['btn_secondary_hover']}; }}
            QPushButton:pressed {{ background-color: {cfg['btn_secondary']}; }}
        """)
        abandon_btn.clicked.connect(lambda: [self.abandon_clicked.emit(), self.close()])
        btn_layout.addWidget(abandon_btn)