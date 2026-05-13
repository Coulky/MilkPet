# -*- coding: utf-8 -*-
"""
游戏成功窗口 - 通用组件

用于显示游戏完成信息，包括：
- 游戏名称
- 难度
- 用时
- 获得的喵币分数
"""

import sys
import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont


class GameSuccessWindow(QWidget):
    """游戏成功窗口"""
    
    confirmed = pyqtSignal()
    
    def __init__(self, game_name: str, difficulty: str, time_seconds: int, score: int):
        super().__init__(None)
        
        self.game_name = game_name
        self.difficulty = difficulty
        self.time_seconds = time_seconds
        self.score = score
        
        self._setup_ui()
        self._center_on_screen()
    
    def _setup_ui(self):
        self.setWindowTitle("游戏完成")
        
        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 主容器
        container = QFrame(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background-color: rgba(43, 43, 54, 0.98);
                border-radius: 15px;
                border: 2px solid rgba(106, 106, 126, 0.9);
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)
        
        # 标题（居中）
        title_label = QLabel("🎉 恭喜完成！")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        # 信息面板（居中对齐）
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)
        info_layout.setAlignment(Qt.AlignCenter)
        
        # 游戏名称
        game_layout = QHBoxLayout()
        game_layout.setSpacing(10)
        
        game_label = QLabel("游戏：")
        game_label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        game_label.setFixedWidth(80)
        
        game_value = QLabel(self.game_name)
        game_value.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
        
        game_layout.addWidget(game_label)
        game_layout.addWidget(game_value)
        info_layout.addLayout(game_layout)
        
        # 难度
        diff_layout = QHBoxLayout()
        diff_layout.setSpacing(10)
        
        diff_label = QLabel("难度：")
        diff_label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        diff_label.setFixedWidth(80)
        
        diff_value = QLabel(self.difficulty)
        diff_value.setStyleSheet("color: #FFB6C1; font-size: 14px; font-weight: bold;")
        
        diff_layout.addWidget(diff_label)
        diff_layout.addWidget(diff_value)
        info_layout.addLayout(diff_layout)
        
        # 用时
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)
        
        time_label = QLabel("用时：")
        time_label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        time_label.setFixedWidth(80)
        
        time_str = self._format_time(self.time_seconds)
        time_value = QLabel(time_str)
        time_value.setStyleSheet("color: #98FB98; font-size: 14px; font-weight: bold;")
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(time_value)
        info_layout.addLayout(time_layout)
        
        # 分数（喵币）
        score_layout = QHBoxLayout()
        score_layout.setSpacing(10)
        
        score_label = QLabel("获得喵币：")
        score_label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        score_label.setFixedWidth(80)
        
        score_value = self._create_score_widget()
        
        score_layout.addWidget(score_label)
        score_layout.addWidget(score_value, 0, Qt.AlignLeft)
        info_layout.addLayout(score_layout)
        
        layout.addLayout(info_layout)
        
        # 完成按钮（居中）
        confirm_btn = QPushButton("确认")
        confirm_btn.setFixedSize(120, 40)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #5a7a9a;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a8aaa;
            }
            QPushButton:pressed {
                background-color: #4a6a8a;
            }
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(confirm_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        
        # 根据内容调整大小（不使用固定高度）
        container.adjustSize()
        self.adjustSize()
    
    def _create_score_widget(self):
        """创建带喵币图标的分数显示"""
        from basic_model.resource_manager import ResourceManager
        rm = ResourceManager()
        widget = rm.create_coin_label(text=str(self.score), icon_size=18, font_size=18, parent=self)
        widget.layout().setAlignment(Qt.AlignLeft)
        if hasattr(widget, '_text_label'):
            widget._text_label.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    font-size: 18px;
                    font-weight: bold;
                    background: transparent;
                }
            """)
        return widget
    
    def _format_time(self, seconds: int) -> str:
        """格式化时间显示"""
        minutes = seconds // 60
        secs = seconds % 60
        if minutes > 0:
            return f"{minutes}分{secs}秒"
        return f"{secs}秒"
    
    def _center_on_screen(self):
        """窗口居中"""
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _on_confirm(self):
        """确认按钮点击处理"""
        self.confirmed.emit()
        self.close()
    
    @staticmethod
    def calculate_score(base_score: int, time_seconds: int, difficulty_multiplier: float = 1.0) -> int:
        """
        计算分数（喵币）
        
        参数：
            base_score: 基础分数
            time_seconds: 用时（秒）
            difficulty_multiplier: 难度系数
        
        返回：
            最终分数
        """
        # 时间奖励：越快完成分数越高（10分钟内完成有奖励）
        max_time = 600  # 10分钟
        time_bonus = max(0, 1 - time_seconds / max_time)
        
        # 基础分数 + 时间奖励
        total_score = int(base_score * difficulty_multiplier * (1 + time_bonus))
        
        return max(total_score, 1)  # 至少1喵币
