# -*- coding: utf-8 -*-
"""
设置窗口模块

功能：
- 设置宠物名字和对自己的称呼
- 自定义宠物对话（10句、增删改、只使用开关）
"""

import sys
import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QLineEdit, QApplication, QPushButton,
                             QStackedWidget, QScrollArea, QCheckBox,
                             QListWidget, QListWidgetItem, QDialog,
                             QDialogButtonBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from basic_model.resource_manager import ResourceManager


class SettingsWindow(QWidget):
    """设置窗口 - 容器1(左侧导航) + 容器2(右侧内容)"""
    
    settings_saved = pyqtSignal(dict)
    interaction_changed = pyqtSignal(str, bool)  # (setting_type, value)
    
    MAX_CUSTOM_DIALOGS = 10
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose, False)
        
        self.resource_manager = ResourceManager()
        self._load_settings()
        
        self.current_page = 0
        
        self._setup_ui()
    
    def _load_settings(self):
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            data = storage.load_encrypted_data()
            if data and 'settings' in data:
                self.settings = data['settings']
            else:
                self.settings = {
                    'pet_name': '小奶',
                    'user_title': '主人',
                    'is_on_top': True,
                    'allow_click': True,
                    'allow_talk': True,
                    'allow_move': False
                }
            
            # 确保交互设置存在（向后兼容）
            if 'is_on_top' not in self.settings:
                self.settings['is_on_top'] = True
            if 'allow_click' not in self.settings:
                self.settings['allow_click'] = True
            if 'allow_talk' not in self.settings:
                self.settings['allow_talk'] = True
            if 'allow_move' not in self.settings:
                self.settings['allow_move'] = False
            
            if data and 'custom_dialogs' in data:
                self.custom_dialogs = data['custom_dialogs']
                if not isinstance(self.custom_dialogs, list):
                    self.custom_dialogs = []
            else:
                self.custom_dialogs = []
            
            if data and 'use_custom_only' in data:
                self.use_custom_only = data['use_custom_only']
            else:
                self.use_custom_only = False
                
        except Exception as e:
            print(f"[WARN] 加载设置失败: {e}")
            self.settings = {
                'pet_name': '小奶',
                'user_title': '主人',
                'is_on_top': True,
                'allow_click': True,
                'allow_talk': True,
                'allow_move': False
            }
            self.custom_dialogs = []
            self.use_custom_only = False
    
    def _save_all(self):
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            
            data = storage.load_encrypted_data()
            if not data:
                data = {}
            
            data['settings'] = self.settings
            data['custom_dialogs'] = self.custom_dialogs
            data['use_custom_only'] = self.use_custom_only
            
            save_result = storage.save_encrypted_data(data)
            
            if not save_result:
                return False
            
            # 验证：立即读取刚保存的数据
            verify_data = storage.load_encrypted_data()
            
            if verify_data is None:
                return False
            
            try:
                from config.talk_settings import refresh_talk_cache
                refresh_talk_cache()
            except Exception as cache_err:
                print(f"[WARN] 刷新对话缓存失败: {cache_err}")
            
            self.settings_saved.emit(self.settings)
            return True
        except Exception as e:
            import traceback
            print(f"[ERROR] 保存设置失败: {e}")
            traceback.print_exc()
            return False
    
    def _setup_ui(self):
        self.setWindowTitle("设置")
        self.setFixedSize(600, 450)
        self.setWindowIcon(self.resource_manager.logo_icon)

        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        container = QFrame(self)
        container.setObjectName("container")
        
        bg_path = self._get_bg_path()
        container.setStyleSheet(f"""
            QFrame#container {{
                background-image: url("{bg_path}");
                background-color: #2b2b36;
                border-radius: 15px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }}
            QLabel#label {{
                color: #cccccc;
                font-size: 14px;
                padding: 4px;
                background: transparent;
            }}
            QLabel#hint {{
                color: #888888;
                font-size: 12px;
                padding: 2px;
                background: transparent;
            }}
            QLineEdit {{
                background-color: rgba(60, 60, 70, 0.95);
                color: #ffffff;
                border: 2px solid #8a8070;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }}
            QLineEdit:focus {{
                border-color: #FFD700;
            }}
            QTableWidget {{
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #8a8070;
                border-radius: 8px;
                gridline-color: #dddddd;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid #eeeeee;
            }}
            QTableWidget::item:selected {{
                background-color: #f0e6d6;
                color: #333333;
            }}
            QHeaderView::section {{
                background-color: #f5f0e8;
                color: #555555;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #8a8070;
                font-weight: bold;
                font-size: 13px;
            }}
            QCheckBox {{
                color: #cccccc;
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #8a8070;
                background-color: rgba(60, 60, 70, 0.95);
            }}
            QCheckBox::indicator:checked {{
                background-color: #8a8070;
                border-color: #FFD700;
            }}
            QCheckBox::indicator:disabled {{
                border-color: #555555;
                background-color: rgba(40, 40, 50, 0.8);
            }}
        """)
        
        main_layout = QHBoxLayout(container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        nav_panel = QWidget()
        nav_panel.setObjectName("container1")
        nav_panel.setFixedWidth(150)
        nav_panel.setStyleSheet("""
            QWidget#container1 {{
                background: rgba(40, 40, 50, 0.3);
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }}
        """)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(10, 20, 10, 10)
        nav_layout.setSpacing(8)
        
        title_label = QLabel("\u8bbe\u7f6e")
        title_label.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; padding: 6px;")
        title_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(title_label)
        nav_layout.addSpacing(16)
        
        self.nav_buttons = []
        nav_items = [
            ("\u79f0\u547c\u8bbe\u7f6e", 0),
            ("\u81ea\u5b9a\u4e49\u5bf9\u8bdd", 1),
            ("\u4ea4\u4e92\u8bbe\u7f6e", 2),
        ]
        
        for text, page_idx in nav_items:
            is_selected = (page_idx == 0)
            btn = self.resource_manager.create_action_button(
                text=text,
                callback=lambda checked, idx=page_idx: self._switch_page(idx),
                size="medium",
                selected=is_selected,
                parent=self
            )
            btn.setCursor(Qt.PointingHandCursor)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        nav_layout.addStretch()
        
        close_btn = self.resource_manager.create_action_button(
            text="\u5173\u95ed",
            callback=lambda: self.close(),
            size="medium",
            parent=self
        )
        close_btn.setCursor(Qt.PointingHandCursor)
        nav_layout.addWidget(close_btn)
        
        main_layout.addWidget(nav_panel)
        
        content_panel = QWidget()
        content_panel.setObjectName("container2")
        content_panel.setStyleSheet("""
            QWidget#container2 {
                background: transparent;
            }
        """)
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(0)
        
        content_stack = QStackedWidget()
        
        page1 = self._create_name_page()
        page2 = self._create_dialog_page()
        page3 = self._create_interaction_page()
        
        content_stack.addWidget(page1)
        content_stack.addWidget(page2)
        content_stack.addWidget(page3)
        
        self.content_stack = content_stack
        content_layout.addWidget(content_stack, stretch=1)
        
        main_layout.addWidget(content_panel, stretch=1)
        
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
        
        self._center_on_screen()
    
    def _create_name_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)
        layout.setContentsMargins(16, 24, 16, 16)
        
        pet_name_layout = QHBoxLayout()
        pet_name_layout.setSpacing(12)
        
        pet_name_label = QLabel("\u5ba0\u7269\u540d\u5b57\uff1a")
        pet_name_label.setObjectName("label")
        pet_name_label.setFixedWidth(100)
        pet_name_layout.addWidget(pet_name_label)
        
        self.pet_name_input = QLineEdit()
        self.pet_name_input.setText(self.settings.get('pet_name', '小奶'))
        self.pet_name_input.setPlaceholderText("\u8f93\u5165\u5ba0\u7269\u7684\u540d\u5b57...")
        pet_name_layout.addWidget(self.pet_name_input)
        
        layout.addLayout(pet_name_layout)
        
        pet_name_hint = QLabel("\u8fd9\u662f\u4f60\u7684\u5c0f\u5ba0\u7269\u7684\u540d\u5b57\uff0c\u4f1a\u5728\u5404\u4e2a\u5730\u65b9\u663e\u793a")
        pet_name_hint.setObjectName("hint")
        layout.addWidget(pet_name_hint)
        
        user_title_layout = QHBoxLayout()
        user_title_layout.setSpacing(12)
        
        user_title_label = QLabel("\u5bf9\u81ea\u5df1\u7684\u79f0\u547c\uff1a")
        user_title_label.setObjectName("label")
        user_title_label.setFixedWidth(100)
        user_title_layout.addWidget(user_title_label)
        
        self.user_title_input = QLineEdit()
        self.user_title_input.setText(self.settings.get('user_title', '主人'))
        self.user_title_input.setPlaceholderText("\u8f93\u5165\u5bf9\u81ea\u5df1\u7684\u79f0\u547c...")
        user_title_layout.addWidget(self.user_title_input)
        
        layout.addLayout(user_title_layout)
        
        user_title_hint = QLabel("\u5ba0\u7269\u4f1a\u7528\u8fd9\u4e2a\u79f0\u547c\u6765\u53eb\u4f60")
        user_title_hint.setObjectName("hint")
        layout.addWidget(user_title_hint)
        
        layout.addStretch()
        
        # 实时保存：输入框内容改变时自动保存
        self.pet_name_input.textChanged.connect(self._on_name_setting_changed)
        self.user_title_input.textChanged.connect(self._on_name_setting_changed)
        
        return page
    
    def _on_name_setting_changed(self):
        """称呼设置改变时自动保存"""
        pet_name = self.pet_name_input.text().strip() or '小奶'
        user_title = self.user_title_input.text().strip() or '主人'
        
        old_pet_name = self.settings.get('pet_name', '小奶')
        old_user_title = self.settings.get('user_title', '主人')
        
        if pet_name != old_pet_name or user_title != old_user_title:
            self.settings['pet_name'] = pet_name
            self.settings['user_title'] = user_title
            self._save_all()
    
    def _create_dialog_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 8)
        
        hint_label = QLabel("\u81ea\u5b9a\u4e5c\u5ba0\u7269\u5bf9\u8bdd\uff08\u6700\u591a" + str(self.MAX_CUSTOM_DIALOGS) + "\u53e5\uff09")
        hint_label.setStyleSheet("color: #aaaaaa; font-size: 13px; font-weight: bold;")
        layout.addWidget(hint_label)
        
        self.dialog_table = QTableWidget()
        self.dialog_table.setColumnCount(1)
        self.dialog_table.setHorizontalHeaderLabels(["\u5bf9\u8bdd\u5185\u5bb9"])
        self.dialog_table.setRowCount(self.MAX_CUSTOM_DIALOGS)
        self.dialog_table.verticalHeader().setVisible(False)
        self.dialog_table.horizontalHeader().setVisible(False)
        self.dialog_table.horizontalHeader().setStretchLastSection(True)
        self.dialog_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dialog_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dialog_table.setAlternatingRowColors(False)
        self.dialog_table.cellClicked.connect(self._on_cell_clicked)
        
        row_height = 32
        for i in range(self.MAX_CUSTOM_DIALOGS):
            self.dialog_table.setRowHeight(i, row_height)
            
            if i < len(self.custom_dialogs):
                container_widget = QWidget()
                container_layout = QHBoxLayout(container_widget)
                container_layout.setContentsMargins(8, 0, 4, 0)
                container_layout.setSpacing(0)
                
                text_label = QLabel(self.custom_dialogs[i])
                text_label.setStyleSheet("color: #333333; font-size: 13px; background: transparent;")
                text_label.setCursor(Qt.PointingHandCursor)
                container_layout.addWidget(text_label, stretch=1)
                
                delete_btn = QPushButton("×")
                delete_btn.setFixedSize(28, 28)
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #aa4a4a;
                        border: none;
                        border-radius: 14px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover { 
                        background-color: #ffeeee; 
                        color: #cc5a5a;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, idx=i: self._on_delete_dialog(idx))
                container_layout.addWidget(delete_btn)
                
                self.dialog_table.setCellWidget(i, 0, container_widget)
            else:
                empty_item = QTableWidgetItem("")
                empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
                empty_item.setBackground(Qt.lightGray)
                self.dialog_table.setItem(i, 0, empty_item)
        
        table_height = self.MAX_CUSTOM_DIALOGS * row_height + 4
        self.dialog_table.setFixedHeight(table_height)
        
        layout.addWidget(self.dialog_table, stretch=1)
        
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        
        self.only_custom_check = QCheckBox("\u53ea\u4f7f\u7528\u81ea\u5b9a\u4e49\u5bf9\u8bdd")
        self.only_custom_check.setChecked(self.use_custom_only)
        has_content = len(self.custom_dialogs) > 0
        self.only_custom_check.setEnabled(has_content)
        if not has_content:
            self.only_custom_check.setToolTip("\u81ea\u5b9a\u4e49\u5185\u5bb9\u4e3a\u7a7a\u65f6\u65e0\u6cd5\u5f00\u542f")
        self.only_custom_check.stateChanged.connect(self._on_only_custom_changed)
        bottom_row.addWidget(self.only_custom_check)
        
        bottom_row.addStretch()
        
        can_add = len(self.custom_dialogs) < self.MAX_CUSTOM_DIALOGS
        self.add_dialog_btn = QPushButton("+ \u6dfb\u52a0\u65b0\u5bf9\u8bdd")
        self.add_dialog_btn.setFixedSize(130, 32)
        self.add_dialog_btn.setEnabled(can_add)
        self.add_dialog_btn.setCursor(Qt.PointingHandCursor)
        self.add_dialog_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(138, 128, 112, 0.9);
                color: #ffffff;
                border: 2px dashed #8a8070;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: rgba(158, 148, 132, 0.95); }
            QPushButton:disabled {
                background-color: rgba(60, 60, 70, 0.5);
                border-color: #444444;
                color: #666666;
            }
        """)
        self.add_dialog_btn.clicked.connect(self._on_add_dialog)
        bottom_row.addWidget(self.add_dialog_btn)
        
        layout.addLayout(bottom_row)
        
        return page
    
    def _create_interaction_page(self):
        """创建交互设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 24, 16, 16)
        
        hint_label = QLabel("\u4ea4\u4e92\u8bbe\u7f6e")
        hint_label.setStyleSheet("color: #aaaaaa; font-size: 15px; font-weight: bold;")
        layout.addWidget(hint_label)
        
        top_check = QCheckBox("\u7f6e\u9876\u663e\u793a")
        top_check.setChecked(self.settings.get('is_on_top', True))
        top_check.stateChanged.connect(lambda state: self._on_interaction_changed('is_on_top', state == Qt.Checked))
        layout.addWidget(top_check)
        
        click_check = QCheckBox("\u5141\u8bb8\u70b9\u51fb\u4ea4\u4e92")
        click_check.setChecked(self.settings.get('allow_click', True))
        click_check.stateChanged.connect(lambda state: self._on_interaction_changed('allow_click', state == Qt.Checked))
        layout.addWidget(click_check)
        
        talk_check = QCheckBox("\u5141\u8bb8\u53d1\u8a00")
        talk_check.setChecked(self.settings.get('allow_talk', True))
        talk_check.stateChanged.connect(lambda state: self._on_interaction_changed('allow_talk', state == Qt.Checked))
        layout.addWidget(talk_check)
        
        move_check = QCheckBox("\u5141\u8bb1\u79fb\u52a8")
        move_check.setChecked(self.settings.get('allow_move', False))
        move_check.stateChanged.connect(lambda state: self._on_interaction_changed('allow_move', state == Qt.Checked))
        layout.addWidget(move_check)
        
        layout.addStretch()
        
        return page
    
    def _on_interaction_changed(self, setting_type: str, value: bool):
        """交互设置改变时保存并通知"""
        # 保存到 settings 字典
        self.settings[setting_type] = value
        
        # 保存到文件
        self._save_all()
        
        # 发射信号，携带设置类型和值
        self.interaction_changed.emit(setting_type, value)
    
    def _switch_page(self, page_idx: int):
        self.current_page = page_idx
        for i, btn in enumerate(self.nav_buttons):
            if i == page_idx:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
        
        # 切换页面时同步最新数据（防止外部修改导致不一致）
        self._sync_settings_from_file()
        
        self.content_stack.setCurrentIndex(page_idx)
    
    def showEvent(self, event):
        """窗口显示时同步最新数据"""
        super().showEvent(event)
        # 每次显示时都同步最新数据
        self._sync_settings_from_file()
    
    def _sync_settings_from_file(self):
        """从文件同步最新设置（解决多地方操作导致的数据不一致）"""
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            data = storage.load_encrypted_data()
            
            if data and 'settings' in data:
                file_settings = data['settings']
                
                # 同步交互设置（如果文件中有更新的值）
                for key in ['is_on_top', 'allow_click', 'allow_talk', 'allow_move']:
                    if key in file_settings and file_settings[key] != self.settings.get(key):
                        print(f"[INFO] 同步设置 {key}: {self.settings.get(key)} -> {file_settings[key]}")
                        self.settings[key] = file_settings[key]
                
                # 如果当前在交互设置页面，更新复选框状态
                if hasattr(self, 'current_page') and self.current_page == 2:  # 交互设置是第3页(索引2)
                    self._update_interaction_checkboxes()
                    
        except Exception as e:
            print(f"[WARN] 同步设置失败: {e}")
    
    def _update_interaction_checkboxes(self):
        """更新交互设置页面的复选框状态"""
        try:
            # 获取交互设置页面
            interaction_page = self.content_stack.widget(2)
            if not interaction_page:
                return
            
            layout = interaction_page.layout()
            if not layout:
                return
            
            # 遍历所有复选框并更新状态
            setting_map = {
                '置顶显示': 'is_on_top',
                '允许点击交互': 'allow_click',
                '允许发言': 'allow_talk',
                '允许移动': 'allow_move'
            }
            
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    text = widget.text()
                    if text in setting_map:
                        key = setting_map[text]
                        new_value = self.settings.get(key, True)
                        
                        # 断开信号以避免触发保存
                        widget.blockSignals(True)
                        widget.setChecked(new_value)
                        widget.blockSignals(False)
                        
        except Exception as e:
            print(f"[WARN] 更新复选框状态失败: {e}")
    
    def _on_only_custom_changed(self, state):
        self.use_custom_only = (state == Qt.Checked)
        self._save_all()
    
    def _validate_dialog_text(self, text: str) -> tuple:
        if not text or not text.strip():
            return False, "对话内容不能为空"
        
        text = text.strip()
        
        if '\\' in text:
            return False, "不允许使用转义符 (\\)"
        
        dangerous_patterns = [
            '${', '`', '$(', 'eval(', 'exec(',
            'import ', 'os.', 'subprocess',
            '__import__', 'system(',
            '\x00', '\x01', '\x02', '\x03', '\x04',
            '\x05', '\x06', '\x07', '\x08', '\x0b',
            '\x0c', '\x0e', '\x0f', '\x10', '\x11',
            '\x12', '\x13', '\x14', '\x15', '\x16',
            '\x17', '\x18', '\x19', '\x1a', '\x1b',
            '\x1c', '\x1d', '\x1e', '\x1f'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in text:
                return False, f"包含不允许的字符: {repr(pattern)}"
        
        control_chars = set()
        for char in text:
            if ord(char) < 32 and char != '\n' and char != '\t':
                control_chars.add(repr(char))
        
        if control_chars:
            return False, f"包含控制字符: {', '.join(control_chars)}"
        
        if len(text) > 100:
            return False, f"对话内容过长 ({len(text)}/100字符)"
        
        return True, ""
    
    def _show_validation_error(self, parent, error_msg: str):
        from widgets.dialog import BaseDialog
        dialog = BaseDialog(
            title="⚠️ 输入验证失败",
            message=error_msg,
            dialog_type="warning",
            parent=parent
        )
        dialog.show()
    
    def _refresh_dialog_table(self):
        current_idx = self.content_stack.currentIndex()
        old_widget = self.content_stack.widget(1)
        if old_widget:
            old_widget.setParent(None)
        page2 = self._create_dialog_page()
        self.content_stack.insertWidget(1, page2)
        self.content_stack.setCurrentIndex(current_idx)
    
    def _on_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("\u6dfb\u52a0\u5bf9\u8bdd")
        dialog.setFixedSize(420, 220)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: #2b2b36; }}
            QLabel {{ color: #cccccc; font-size: 14px; }}
            QLabel#warning {{ color: #ff6b6b; font-size: 12px; padding: 4px; }}
            QLineEdit {{
                background-color: rgba(60, 60, 70, 0.95);
                color: #ffffff;
                border: 2px solid #8a8070;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-family: "Microsoft YaHei";
            }}
            QLineEdit:focus {{ border-color: #FFD700; }}
            QPushButton {{
                background-color: #8a8070;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #9a9080; }}
            QPushButton:default {{ background-color: #6a9a4a; }}
            QPushButton:default:hover {{ background-color: #7aaa5a; }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 16)
        
        label = QLabel("\u8f93\u5165\u5ba0\u7269\u5bf9\u8bdd\u5185\u5bb9\uff1a")
        layout.addWidget(label)
        
        text_edit = QLineEdit()
        text_edit.setPlaceholderText("\u5728\u6b64\u8f93\u5165\u5bf9\u8bdd\u5185\u5bb9...")
        text_edit.setMaxLength(100)
        layout.addWidget(text_edit)
        
        hint = QLabel("\u6700\u591a " + str(self.MAX_CUSTOM_DIALOGS) + " \u53e5\uff0c\u5f53\u524d " + str(len(self.custom_dialogs)) + "\u53e5 / 100\u5b57\u7b26")
        hint.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint)
        
        warning_label = QLabel("")
        warning_label.setObjectName("warning")
        warning_label.setWordWrap(True)
        warning_label.hide()
        layout.addWidget(warning_label)
        
        def validate_and_accept():
            input_text = text_edit.text().strip()
            is_valid, error_msg = self._validate_dialog_text(input_text)
            
            if is_valid:
                dialog.accept()
            else:
                warning_label.setText(f"❌ {error_msg}")
                warning_label.show()
                text_edit.setFocus()
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(validate_and_accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            new_text = text_edit.text().strip()
            
            if not new_text:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "提示", "对话内容不能为空")
                return
            
            if len(self.custom_dialogs) >= self.MAX_CUSTOM_DIALOGS:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "提示", f"已达到最大数量限制（{self.MAX_CUSTOM_DIALOGS}条）")
                return
            
            is_valid, error_msg = self._validate_dialog_text(new_text)
            if not is_valid:
                self._show_validation_error(self, error_msg)
                return
            
            self.custom_dialogs.append(new_text)
            
            save_result = self._save_all()
            
            if save_result:
                self._refresh_dialog_table()
                
                if not self.only_custom_check.isEnabled():
                    self.only_custom_check.setEnabled(True)
                    self.only_custom_check.setToolTip("")
                
                from PyQt5.QtWidgets import QMessageBox
                import os
                
                # 获取存储路径用于显示
                try:
                    from basic_model.secure_storage import SecureStorage
                    temp_storage = SecureStorage()
                    storage_path = temp_storage.get_storage_path()
                    file_exists = os.path.exists(storage_path)
                    file_size = os.path.getsize(storage_path) if file_exists else 0
                    
                    msg = (
                        f"✅ 对话已添加并保存！\n\n"
                        f"📝 内容：{new_text}\n"
                        f"📊 当前共 {len(self.custom_dialogs)} 条自定义对话\n\n"
                        f"💾 存储信息：\n"
                        f"   文件路径：{storage_path}\n"
                        f"   文件存在：{'是' if file_exists else '否 ❌'}\n"
                        f"   文件大小：{file_size} 字节"
                    )
                except Exception as e:
                    msg = f"✅ 对话已添加并保存！\n\n内容：{new_text}\n当前共 {len(self.custom_dialogs)} 条\n\n⚠️ 无法获取存储信息: {e}"
                
                QMessageBox.information(
                    self,
                    "✅ 添加成功",
                    msg,
                    QMessageBox.Ok
                )
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    "❌ 保存失败",
                    "对话添加失败，请重试！\n\n可能原因：\n"
                    "• 存储文件被占用\n"
                    "• 磁盘空间不足\n"
                    "• 权限不足\n"
                    "• 加密/解密失败",
                    QMessageBox.Ok
                )
                self.custom_dialogs.pop()
    
    def _on_cell_clicked(self, row: int, column: int):
        if row < len(self.custom_dialogs):
            self._on_edit_dialog(row)
    
    def _on_edit_dialog(self, index: int):
        if index >= len(self.custom_dialogs):
            return
        
        old_text = self.custom_dialogs[index]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("\u7f16\u8f91\u5bf9\u8bdd")
        dialog.setFixedSize(420, 220)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: #2b2b36; }}
            QLabel {{ color: #cccccc; font-size: 14px; }}
            QLabel#warning {{ color: #ff6b6b; font-size: 12px; padding: 4px; }}
            QLineEdit {{
                background-color: rgba(60, 60, 70, 0.95);
                color: #ffffff;
                border: 2px solid #8a8070;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-family: "Microsoft YaHei";
            }}
            QLineEdit:focus {{ border-color: #FFD700; }}
            QPushButton {{
                background-color: #8a8070;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #9a9080; }}
            QPushButton:default {{ background-color: #6a9a4a; }}
            QPushButton:default:hover {{ background-color: #7aaa5a; }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 16)
        
        label = QLabel("\u4fee\u6539\u5bf9\u8bdd\u5185\u5bb9\uff1a")
        layout.addWidget(label)
        
        text_edit = QLineEdit()
        text_edit.setText(old_text)
        text_edit.setMaxLength(100)
        layout.addWidget(text_edit)
        
        hint = QLabel("100字符以内，不允许使用转义符")
        hint.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint)
        
        warning_label = QLabel("")
        warning_label.setObjectName("warning")
        warning_label.setWordWrap(True)
        warning_label.hide()
        layout.addWidget(warning_label)
        
        def validate_and_accept():
            input_text = text_edit.text().strip()
            is_valid, error_msg = self._validate_dialog_text(input_text)
            
            if is_valid:
                dialog.accept()
            else:
                warning_label.setText(f"❌ {error_msg}")
                warning_label.show()
                text_edit.setFocus()
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(validate_and_accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            new_text = text_edit.text().strip()
            if new_text:
                is_valid, error_msg = self._validate_dialog_text(new_text)
                if not is_valid:
                    self._show_validation_error(self, error_msg)
                    return
                
                self.custom_dialogs[index] = new_text
                self._save_all()
                self._refresh_dialog_table()
    
    def _on_delete_dialog(self, index: int):
        if index >= len(self.custom_dialogs):
            return
        
        del self.custom_dialogs[index]
        self._refresh_dialog_table()
        
        if len(self.custom_dialogs) == 0:
            self.only_custom_check.setChecked(False)
            self.only_custom_check.setEnabled(False)
            self.only_custom_check.setToolTip("\u81ea\u5b9a\u4e49\u5185\u5bb9\u4e3a\u7a7a\u65f6\u65e0\u6cd5\u5f00\u542f")
    
    def _on_save(self):
        pet_name = self.pet_name_input.text().strip()
        user_title = self.user_title_input.text().strip()
        
        if not pet_name:
            pet_name = '小奶'
        if not user_title:
            user_title = '主人'
        
        self.settings['pet_name'] = pet_name
        self.settings['user_title'] = user_title
        self.use_custom_only = self.only_custom_check.isChecked() and len(self.custom_dialogs) > 0
        
        if self._save_all():
            from widgets.dialog import CompleteDialog
            dialog = CompleteDialog(
                title="\u2728 \u8bbe\u7f6e\u5df2\u4fdd\u5b58",
                message=f"\u5ba0\u7269\u540d\u5b57\uff1a{pet_name}\n\u5bf9\u81ea\u5df1\u7684\u79f0\u547c\uff1a{user_title}\n\u81ea\u5b9a\u4e49\u5bf9\u8bdd\uff1a{len(self.custom_dialogs)}\u53e5",
                parent=self
            )
            dialog.show()
    
    def get_pet_name(self) -> str:
        return self.settings.get('pet_name', '小奶')
    
    def get_user_title(self) -> str:
        return self.settings.get('user_title', '\u4e3b\u4eba')
    
    def get_custom_dialogs(self) -> list:
        return self.custom_dialogs.copy()
    
    def get_use_custom_only(self) -> bool:
        return self.use_custom_only and len(self.custom_dialogs) > 0
    
    def _get_bg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'background.png').replace('\\', '/')
    
    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def closeEvent(self, event):
        event.accept()
