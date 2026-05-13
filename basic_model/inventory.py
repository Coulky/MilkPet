# -*- coding: utf-8 -*-
"""
背包系统模块

功能：
- 背包UI界面（网格布局）
- 道具管理（添加、使用、丢弃、排序）
- 分类筛选
- 容量管理
- 拖拽交互
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QLabel, QScrollArea, QFrame,
                             QMessageBox, QComboBox, QToolTip, QSizePolicy,
                             QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon

from .items import Item, ItemType, ItemRarity, ItemFactory
from basic_model.resource_manager import ResourceManager


class InventorySlot(QFrame):
    """背包格子 - 与商店 ShopItemSlot 样式一致"""

    item_used = pyqtSignal(str)

    def __init__(self, slot_id: int = 0, parent=None):
        super().__init__(parent)

        self.slot_id = slot_id
        self.item: Optional[Item] = None
        self.quantity: int = 0

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(120, 150)
        self.setStyleSheet("""
            InventorySlot {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }
            QLabel#inv_icon {
                font-size: 32px;
                background: transparent;
            }
            QLabel#inv_name {
                color: #333333;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }
            QLabel#inv_count {
                color: #FFD700;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
            QPushButton#use_btn {
                background-color: #4a7a4a;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                padding: 3px 8px;
            }
            QPushButton#use_btn:hover { background-color: #5a9a5a; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("inv_icon")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(64, 64)
        layout.addWidget(self.icon_label)

        self.name_label = QLabel()
        self.name_label.setObjectName("inv_name")
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        self.count_label = QLabel()
        self.count_label.setObjectName("inv_count")
        self.count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.count_label)

        self.use_btn = QPushButton("\u4f7f\u7528")
        self.use_btn.setObjectName("use_btn")
        self.use_btn.clicked.connect(self._on_use_clicked)
        layout.addWidget(self.use_btn)

        self.setLayout(layout)

    def set_item(self, item: Item, quantity: int = 1):
        self.item = item
        self.quantity = quantity

        if item:
            if item.icon and (item.icon.endswith('.png') or item.icon.endswith('.jpg') or item.icon.endswith('.jpeg')):
                icon_path = item.icon
                if not os.path.isabs(icon_path):
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    icon_path = os.path.join(base_dir, icon_path)
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.icon_label.setPixmap(scaled_pixmap)
                else:
                    self.icon_label.setText("[?]")
            else:
                self.icon_label.setText(item.icon if item.icon else "[?]")

            name_text = item.name[:8]
            if len(item.name) > 8:
                name_text += ".."
            self.name_label.setText(name_text)

            self.count_label.setText(f"x{quantity}")

            rarity_color_map = {
                ItemRarity.COMMON: "#aaaaaa",
                ItemRarity.RARE: "#4a9eff",
                ItemRarity.EPIC: "#b04aff",
                ItemRarity.LEGENDARY: "#ffaa00",
            }
            rc = rarity_color_map.get(item.rarity, "#aaaaaa")

            self.setStyleSheet(f"""
                InventorySlot {{
                    background-color: #ffffff;
                    border: 2px solid {rc};
                    border-radius: 10px;
                }}
                QLabel {{
                    background: transparent;
                    color: #333333;
                }}
                QLabel#inv_count {{
                    color: #FFD700;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                }}
                QPushButton#use_btn {{
                    background-color: #4a7a4a;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                    padding: 3px 8px;
                }}
                QPushButton#use_btn:hover {{ background-color: #5a9a5a; }}
            """)
        else:
            self.clear_slot()

    def clear_slot(self):
        self.item = None
        self.quantity = 0
        self.icon_label.setText("")
        self.name_label.setText("")
        self.count_label.setText("")
        self.setStyleSheet("""
            InventorySlot {
                background-color: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }
        """)

    def _on_use_clicked(self):
        if self.item:
            self.item_used.emit(self.item.id)


class InventoryWindow(QWidget):
    """背包窗口"""
    
    item_used = pyqtSignal(str)  # 道具被使用
    item_dropped = pyqtSignal(str, int)  # 道具被丢弃
    closed = pyqtSignal()  # 窗口关闭
    
    MAX_SLOTS = 24  # 最大容量
    
    def __init__(self, inventory_data: Dict[str, int] = None, parent=None):
        super().__init__(parent)

        # 确保关闭此窗口不会退出整个应用
        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.inventory: Dict[str, int] = defaultdict(int)
        if inventory_data:
            self.inventory.update(inventory_data)
        
        self.slots: List[InventorySlot] = []
        self.current_filter = "all"
        self.resource_manager = ResourceManager()
        
        self._setup_ui()
        self._refresh_inventory()
    
    def _setup_ui(self):
        """设置UI - 与商店窗口样式完全一致"""
        
        self.setWindowTitle("背包")
        self.setFixedSize(720, 600)

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
            QLabel#title {{
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                padding: 6px;
                background: transparent;
            }}
            QLabel#info {{
                color: #FFD700;
                font-size: 15px;
                font-weight: bold;
                padding: 4px;
                background: transparent;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget#grid_container {{
                background: transparent;
            }}
        """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(18, 18, 18, 14)
        
        title_bar = QHBoxLayout()
        
        title_label = QLabel("\u6211\u7684\u80cc\u5305")
        title_label.setObjectName("title")
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        main_layout.addLayout(title_bar)
        
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(5)
        
        categories = [
            ("all", "\u5168\u90e8"),
            ("food", "\u98df\u7269"),
            ("drink", "\u996e\u54c1"),
            ("toy", "\u73a9\u5177"),
            ("decoration", "\u88c5\u9970"),
            ("game", "\u6e38\u620f\u9053\u5177"),
        ]
        
        self.filter_buttons = {}
        for cat_id, cat_name in categories:
            is_selected = (cat_id == "all")
            btn = self.resource_manager.create_action_button(
                text=cat_name,
                size="small",
                selected=is_selected,
                callback=lambda checked, cid=cat_id: self._filter_items(cid),
                parent=self
            )
            filter_bar.addWidget(btn)
            self.filter_buttons[cat_id] = btn

        filter_bar.addStretch()
        
        sort_combo = QComboBox()
        sort_combo.addItem("\u7efc\u5408")
        sort_combo.addItem("\u6309\u7a00\u6709\u5ea6")
        sort_combo.addItem("\u6309\u540d\u79f0")
        sort_combo.addItem("\u6309\u6570\u91cf")
        sort_combo.currentIndexChanged.connect(self._sort_inventory)
        self.resource_manager.apply_combobox_style(sort_combo)
        filter_bar.addWidget(sort_combo)
        
        main_layout.addLayout(filter_bar)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        grid_container = QWidget()
        grid_container.setObjectName("grid_container")
        
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(12, 12, 12, 12)
        
        scroll_area.setWidget(grid_container)
        main_layout.addWidget(scroll_area, stretch=1)
        
        bottom_bar = QHBoxLayout()
        
        close_btn = self.resource_manager.create_icon_button(
            text="\u5173\u95ed",
            callback=lambda: self.close(),
            parent=self
        )
        
        bottom_bar.addStretch()
        bottom_bar.addWidget(close_btn)
        bottom_bar.addStretch()
        
        main_layout.addLayout(bottom_bar)
        
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
        
        self._center_on_screen()
        
        self.selected_slot: Optional[InventorySlot] = None
    
    def _refresh_inventory(self):
        """刷新背包显示 - 动态生成格子（商城样式）"""
        for slot in self.slots:
            slot.deleteLater()
        self.slots.clear()
        
        items_to_show = []
        
        for item_id, quantity in self.inventory.items():
            item = ItemFactory.get_item(item_id)
            if not item:
                continue
            
            if self.current_filter != "all":
                type_map = {
                    "food": ItemType.FOOD,
                    "drink": ItemType.DRINK,
                    "toy": ItemType.TOY,
                    "decoration": ItemType.DECORATION,
                    "game": ItemType.GAME,
                }
                
                if self.current_filter in type_map:
                    if item.item_type != type_map[self.current_filter]:
                        continue
            
            items_to_show.append((item, quantity))
        
        col = 0
        row = 0
        cols_per_row = 5
        
        for item, quantity in items_to_show:
            slot = InventorySlot()
            slot.set_item(item, quantity)
            slot.item_used.connect(self._on_item_used)
            
            self.grid_layout.addWidget(slot, row, col)
            self.slots.append(slot)
            
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1
    
    def _filter_items(self, category: str):
        """筛选道具"""
        self.current_filter = category
        
        # 更新按钮状态
        for cat_id, btn in self.filter_buttons.items():
            btn.setChecked(cat_id == category)
        
        self._refresh_inventory()
    
    def _sort_inventory(self, index=0):
        """排序背包"""
        # 将字典转换为列表进行排序
        items_list = []
        
        for item_id, quantity in self.inventory.items():
            item = ItemFactory.get_item(item_id)
            if item:
                items_list.append((item, quantity, item_id))
        
        # 根据不同方式排序
        if index == 1:  # 按稀有度
            rarity_order = {ItemRarity.COMMON: 0, ItemRarity.RARE: 1, 
                          ItemRarity.EPIC: 2, ItemRarity.LEGENDARY: 3}
            items_list.sort(key=lambda x: rarity_order.get(x[0].rarity, 0), reverse=True)
        elif index == 2:  # 按名称
            items_list.sort(key=lambda x: x[0].name)
        elif index == 3:  # 按数量
            items_list.sort(key=lambda x: x[1], reverse=True)
        else:  # 默认按类型，再按价格低到高
            type_order = {ItemType.FOOD: 0, ItemType.DRINK: 1,
                         ItemType.TOY: 2, ItemType.DECORATION: 3,
                         ItemType.GAME: 4}
            items_list.sort(key=lambda x: (type_order.get(x[0].item_type, 99), x[0].price))
        
        # 清空并重新填充
        self.inventory.clear()
        for item, quantity, item_id in items_list:
            self.inventory[item_id] = quantity
        
        self._refresh_inventory()
    
    def _on_item_used(self, item_id: str):
        """使用道具"""
        item = ItemFactory.get_item(item_id)
        if not item:
            return
        
        # 减少数量
        if self.inventory[item_id] > 1:
            self.inventory[item_id] -= 1
        else:
            del self.inventory[item_id]
        
        # 发送使用信号
        self.item_used.emit(item_id)
        
        # 刷新显示
        self._refresh_inventory()
        
        print(f"[OK] 使用了道具: {item.name}")
    
    def _on_item_clicked(self, item_id: str):
        """点击道具 - 显示详情"""
        try:
            item = ItemFactory.get_item(item_id)
            if not item:
                return

            quantity = self.inventory.get(item_id, 0)

            rarity_colors = {
                ItemRarity.COMMON: "#FFFFFF",
                ItemRarity.UNCOMMON: "#1EFF00",
                ItemRarity.RARE: "#0070DD",
                ItemRarity.EPIC: "#A335EE",
                ItemRarity.LEGENDARY: "#FF8000"
            }
            color = rarity_colors.get(item.rarity, "#FFFFFF")

            detail_text = f"""<div style='font-family: Microsoft YaHei; font-size: 13px;'>
<h2 style='color: {color}; margin: 5px 0;'>{item.icon} {item.name}</h2>
<p style='margin: 3px 0;'><b>类型:</b> {item.item_type.value}</p>
<p style='margin: 3px 0;'><b>稀有度:</b> <span style='color: {color}'>{item.rarity.value}</span></p>
<p style='margin: 3px 0;'><b>数量:</b> {quantity}</p>
<p style='margin: 3px 0;'><b>描述:</b> {item.description}</p>
</div>"""

            msg = QMessageBox(self)
            msg.setWindowTitle("📦 物品详情")
            msg.setIcon(QMessageBox.Information)
            msg.setTextFormat(Qt.RichText)
            msg.setText(detail_text)
            
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b36;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                    font-size: 13px;
                    min-width: 350px;
                }
                QPushButton {
                    background-color: #5a7a9a;
                    color: white;
                    padding: 6px 20px;
                    border-radius: 4px;
                    border: none;
                    min-width: 80px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #6a8aaa;
                }
            """)

            buttons = []
            
            if item.item_type in (ItemType.FOOD, ItemType.DRINK, ItemType.TOY) and quantity > 0:
                use_btn = msg.addButton("✓ 使用", QMessageBox.ActionRole)
                buttons.append(('use', use_btn))
            
            if quantity > 1:
                split_btn = msg.addButton("📦 拆分", QMessageBox.ActionRole)
                buttons.append(('split', split_btn))

            close_btn = msg.addButton("关闭", QMessageBox.RejectRole)
            msg.setDefaultButton(close_btn)
            
            msg.raise_()
            msg.activateWindow()
            
            result = msg.exec_()

            if result == QMessageBox.Acceptable:
                clicked_btn = msg.clickedButton()
                
                for btn_type, btn in buttons:
                    if clicked_btn == btn:
                        if btn_type == 'use':
                            self._on_item_used(item_id)
                        elif btn_type == 'split':
                            self._split_item(item_id, quantity)
                        break

        except Exception as e:
            print(f"❌ 显示物品详情失败: {e}")
            import traceback
            traceback.print_exc()

    def _split_item(self, item_id: str, current_quantity: int):
        """拆分物品"""
        try:
            input_dialog = QMessageBox(self)
            input_dialog.setWindowTitle("拆分物品")
            
            from PyQt5.QtWidgets import QInputDialog, QLineEdit
            
            quantity, ok = QInputDialog.getInt(
                self,
                "拆分物品",
                f"当前数量: {current_quantity}\n请输入要拆分的数量 (1-{current_quantity - 1}):",
                1,
                1,
                current_quantity - 1,
                1
            )

            if ok and 1 <= quantity < current_quantity:
                self.inventory[item_id] -= quantity
                self._refresh_inventory()

                print(f"[OK] 拆分了 {quantity} 个 {item_id}")

        except Exception as e:
            print(f"❌ 拆分物品失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _use_selected_item(self):
        """使用选中的道具"""
        if self.selected_slot and self.selected_slot.item:
            self._on_item_used(self.selected_slot.item.id)
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加道具到背包"""
        # 检查容量
        if item_id not in self.inventory and len(self.inventory) >= self.MAX_SLOTS:
            QMessageBox.warning(
                self,
                "背包已满",
                f"背包容量已达上限 ({self.MAX_SLOTS} 格)\n请先清理一些空间",
                QMessageBox.Ok
            )
            return False
        
        item = ItemFactory.get_item(item_id)
        if not item:
            print(f"[WARN] 未找到道具: {item_id}")
            return False
        
        # 检查是否可堆叠
        if item.stackable:
            max_qty = min(item.max_stack, quantity + self.inventory.get(item_id, 0))
            self.inventory[item_id] = max_qty
        else:
            if item_id not in self.inventory:
                self.inventory[item_id] = 1
            else:
                print(f"[WARN] 该道具不可堆叠: {item.name}")
                return False
        
        self._refresh_inventory()
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """从背包移除道具"""
        if item_id not in self.inventory:
            return False
        
        if self.inventory[item_id] <= quantity:
            del self.inventory[item_id]
        else:
            self.inventory[item_id] -= quantity
        
        self.item_dropped.emit(item_id, quantity)
        self._refresh_inventory()
        return True
    
    def get_inventory_data(self) -> Dict[str, int]:
        """获取背包数据（用于保存）"""
        return dict(self.inventory)
    
    def load_inventory_data(self, data: Dict[str, int]):
        """加载背包数据"""
        self.inventory = defaultdict(int)
        self.inventory.update(data)
        self._refresh_inventory()
    
    def _get_bg_path(self):
        """获取背景图片路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'images', 'background.png').replace('\\', '/')

    def _get_btn_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'images', 'button.png').replace('\\', '/')

    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event):
        """关闭事件"""
        self.closed.emit()
        event.accept()
