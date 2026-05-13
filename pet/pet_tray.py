# -*- coding: utf-8 -*-
"""
系统托盘管理模块 - 负责托盘图标、菜单和交互

独立模块：避免其他功能修改影响托盘逻辑
"""

import os

from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QPen, QFont


class PetTrayManager:
    """
    系统托盘管理器
    
    职责：
    - 托盘图标创建和显示
    - 托盘菜单管理
    - 托盘事件处理（双击显示/隐藏）
    """
    
    def __init__(self, parent_widget):
        """
        初始化托盘管理器
        
        参数:
            parent_widget: 桌宠主窗口（用于信号连接和回调）
        """
        self.parent = parent_widget
        self.tray_icon = None
        
        self._setup_tray()
    
    def _setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self.parent)

        # 优先使用 logo.ico 作为托盘图标
        logo_path = self.parent.get_logo_path()
        
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                tray_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(tray_pixmap)
                self.tray_icon.setIcon(icon)
                print(f"[OK] 托盘图标已设置: {logo_path}")
            else:
                self._set_default_tray_icon()
        else:
            self._set_default_tray_icon()
        
        # 显示托盘图标
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip("Milk Pet")

        # 创建托盘菜单
        tray_menu = self._create_tray_menu()
        self.tray_icon.setContextMenu(tray_menu)
        
        # 连接双击事件
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        print("[OK] 系统托盘已启动")
    
    def _create_tray_menu(self):
        """创建托盘右键菜单"""
        tray_menu = QMenu()

        show_action = QAction("显示桌宠", self.parent)
        show_action.triggered.connect(self.parent.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("隐藏桌宠", self.parent)
        hide_action.triggered.connect(self.parent.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()

        game_menu = tray_menu.addMenu("娱乐")

        dh_puzzle_action = QAction("数字华容道", self.parent)
        dh_puzzle_action.triggered.connect(lambda: self._trigger_callback('_on_dh_puzzle'))
        game_menu.addAction(dh_puzzle_action)

        sudoku_action = QAction("数独", self.parent)
        sudoku_action.triggered.connect(lambda: self._trigger_callback('_on_sudoku'))
        game_menu.addAction(sudoku_action)
        
        tray_menu.addSeparator()

        func_menu = tray_menu.addMenu("功能")

        backpack_action = QAction("背包", self.parent)
        backpack_action.triggered.connect(lambda: self._trigger_callback('_on_backpack'))
        func_menu.addAction(backpack_action)

        shop_action = QAction("商店", self.parent)
        shop_action.triggered.connect(lambda: self._trigger_callback('_on_shop'))
        func_menu.addAction(shop_action)

        stats_action = QAction("统计数据", self.parent)
        stats_action.triggered.connect(lambda: self._trigger_callback('_on_statistics'))
        func_menu.addAction(stats_action)

        tray_menu.addSeparator()

        sys_menu = tray_menu.addMenu("系统")

        # 置顶按钮（带状态显示）
        self.toggle_top_action = QAction("取消置顶" if self.parent.is_on_top else "置顶", self.parent)
        self.toggle_top_action.triggered.connect(lambda: self._trigger_callback('_toggle_top'))
        sys_menu.addAction(self.toggle_top_action)

        # 允许点击交互按钮（带状态显示）
        self.on_click_toggle_action = QAction("禁止点击交互" if self.parent.allow_click else "允许点击交互", self.parent)
        self.on_click_toggle_action.triggered.connect(lambda: self._trigger_callback('_on_click_toggle'))
        sys_menu.addAction(self.on_click_toggle_action)

        # 允许发言按钮（带状态显示）
        self.allow_talk_action = QAction("禁止发言" if self.parent.allow_talk else "允许发言", self.parent)
        self.allow_talk_action.triggered.connect(lambda: self._trigger_callback('_on_talk_toggle'))
        sys_menu.addAction(self.allow_talk_action)

        # 允许移动按钮（带状态显示）
        self.allow_move_action = QAction("禁止移动" if self.parent.allow_move else "允许移动", self.parent)
        self.allow_move_action.triggered.connect(lambda: self._trigger_callback('_on_move_toggle'))
        sys_menu.addAction(self.allow_move_action)
        
        tray_menu.addSeparator()

        quit_action = QAction("退出", self.parent)
        quit_action.triggered.connect(lambda: self._trigger_callback('_on_quit'))
        tray_menu.addAction(quit_action)
        
        return tray_menu
    
    def update_tray_menu(self):
        """更新托盘菜单状态"""
        if hasattr(self, 'toggle_top_action'):
            self.toggle_top_action.setText("取消置顶" if self.parent.is_on_top else "置顶")
        
        if hasattr(self, 'on_click_toggle_action'):
            self.on_click_toggle_action.setText("禁止点击交互" if self.parent.allow_click else "允许点击交互")
        
        if hasattr(self, 'allow_talk_action'):
            self.allow_talk_action.setText("禁止发言" if self.parent.allow_talk else "允许发言")
        
        if hasattr(self, 'allow_move_action'):
            self.allow_move_action.setText("禁止移动" if self.parent.allow_move else "允许移动")
    
    def _trigger_callback(self, callback_name):
        """
        触发父窗口的回调方法
        
        参数:
            callback_name: 回调方法名（如 '_on_dh_puzzle'）
        """
        if hasattr(self.parent, callback_name) and callable(getattr(self.parent, callback_name)):
            getattr(self.parent, callback_name)()
    
    def _set_default_tray_icon(self):
        "设置默认托盘图标（当图片加载失败时）"
        icon = QIcon()
        
        # 创建一个简单的文字图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.white, 2))
        font = QFont()
        font.setPixelSize(48)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "cat")
        painter.end()
        
        icon.addPixmap(pixmap)
        self.tray_icon.setIcon(icon)
        print("[WARN] 使用了默认托盘图标")
    
    def _on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.parent.isVisible():
                self.parent.hide()
            else:
                self.parent.show()
                self.parent.activateWindow()
    
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, duration=3000):
        """
        显示托盘通知消息
        
        参数:
            title: 标题
            message: 消息内容
            icon: 图标类型
            duration: 显示时长（毫秒）
        """
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon, duration)
    
    def cleanup(self):
        """清理托盘资源"""
        if self.tray_icon:
            self.tray_icon.hide()
            print("[OK] 托盘资源已清理")