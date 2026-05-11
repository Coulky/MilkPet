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
                             QMessageBox, QComboBox, QToolTip, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon

from .items import Item, ItemType, ItemRarity, ItemFactory


class InventorySlot(QFrame):
    """背包格子 - 参照商店 ShopItemSlot 样式"""

    item_used = pyqtSignal(str)

    def __init__(self, slot_id: int = 0, parent=None):
        super().__init__(parent)

        self.slot_id = slot_id
        self.item: Optional[Item] = None
        self.quantity: int = 0
        self._use_btn_visible = False

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(120, 150)
        self.setStyleSheet("""
            InventorySlot {
                background-color: rgba(58, 58, 78, 0.9);
                border: 2px solid #6a6a7e;
                border-radius: 10px;
            }
            InventorySlot:hover {
                border-color: #8a8abe;
            }
            QLabel#inv_icon {
                font-size: 32px;
            }
            QLabel#inv_name {
                color: #eeeeee;
                font-size: 11px;
                font-weight: bold;
            }
            QLabel#inv_rarity {
                font-size: 9px;
            }
            QLabel#inv_count {
                color: white;
                font-size: 11px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 150);
                padding: 1px 5px;
                border-radius: 8px;
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
        layout.addWidget(self.icon_label)

        self.name_label = QLabel()
        self.name_label.setObjectName("inv_name")
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        self.rarity_label = QLabel()
        self.rarity_label.setObjectName("inv_rarity")
        self.rarity_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.rarity_label)

        self.count_label = QLabel()
        self.count_label.setObjectName("inv_count")
        self.count_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.count_label.hide()

        count_layout = QVBoxLayout()
        count_layout.setContentsMargins(0, 0, 2, 2)
        count_layout.addWidget(self.count_label)

        self.use_btn = QPushButton("\u4f7f\u7528")
        self.use_btn.setObjectName("use_btn")
        self.use_btn.hide()
        self.use_btn.clicked.connect(self._on_use_clicked)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.use_btn)
        btn_layout.addStretch()

        layout.addLayout(count_layout)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def set_item(self, item: Item, quantity: int = 1):
        self.item = item
        self.quantity = quantity

        if item:
            self.icon_label.setText(item.icon if item.icon else "[?]")
            name_text = item.name[:8]
            if len(item.name) > 8:
                name_text += ".."
            self.name_label.setText(name_text)
            self.rarity_label.setText(f"[{item.rarity.chinese_name}]")

            rarity_color_map = {
                ItemRarity.COMMON: "#aaaaaa",
                ItemRarity.RARE: "#4a9eff",
                ItemRarity.EPIC: "#b04aff",
                ItemRarity.LEGENDARY: "#ffaa00",
            }
            rc = rarity_color_map.get(item.rarity, "#aaaaaa")
            self.rarity_label.setStyleSheet(f"color: {rc};")

            if quantity > 1:
                self.count_label.setText(f"x{quantity}")
                self.count_label.show()
            else:
                self.count_label.hide()

            self.setStyleSheet(f"""
                InventorySlot {{
                    background-color: rgba(58, 58, 78, 0.95);
                    border: 2px solid {rc};
                    border-radius: 10px;
                }}
                InventorySlot:hover {{
                    border-color: {rc};
                    background-color: rgba(68, 68, 88, 0.95);
                    box-shadow: 0 0 10px {rc}40;
                }}
            """)
            self._hide_use_btn()
        else:
            self.clear_slot()

    def clear_slot(self):
        self.item = None
        self.quantity = 0
        self.icon_label.setText("")
        self.name_label.setText("")
        self.rarity_label.setText("")
        self.count_label.hide()
        self._hide_use_btn()
        self.setStyleSheet("""
            InventorySlot {
                background-color: rgba(58, 58, 78, 0.9);
                border: 2px solid #6a6a7e;
                border-radius: 10px;
            }
            InventorySlot:hover {
                border-color: #8a8abe;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.item:
            if self._use_btn_visible:
                self._hide_use_btn()
            else:
                self._show_use_btn()

    def _show_use_btn(self):
        self._use_btn_visible = True
        self.use_btn.show()

    def _hide_use_btn(self):
        self._use_btn_visible = False
        self.use_btn.hide()

    def _on_use_clicked(self):
        if self.item:
            self._hide_use_btn()
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
        
        self._setup_ui()
        self._refresh_inventory()
    
    def _setup_ui(self):
        """设置UI"""
        from PyQt5.QtWidgets import QApplication
        
        self.setWindowTitle("背包")
        self.setFixedSize(720, 580)

        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 启用透明背景

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
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }}
            QLabel#info {{
                color: #aaaaaa;
                font-size: 14px;
                padding: 5px;
                background: transparent;
            }}
            QPushButton#control_btn {{
                background-color: #5a7a9a;
                color: white;
                font-size: 13px;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#control_btn:hover {{
                background-color: #6a8aaa;
            }}
            QPushButton#control_btn:checked {{
                background-color: #4a6a8a;
                border: 2px solid #8a8aba;
            }}
            QComboBox {{
                background-color: #3a3a46;
                color: white;
                border: 2px solid #5a5a6e;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid white;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #3a3a46;
                color: white;
                selection-background-color: #5a5a6e;
                outline: none;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget#grid_container {{
                background-color: rgba(43, 43, 54, 0.95);
                border: 2px solid #4a4a5e;
                border-radius: 12px;
            }}
        """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_bar = QHBoxLayout()
        
        title_label = QLabel("我的背包")
        title_label.setObjectName("title")
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        capacity_label = QLabel(f"容量: {len(self.inventory)}/{self.MAX_SLOTS}")
        capacity_label.setObjectName("info")
        title_bar.addWidget(capacity_label)
        self.capacity_label = capacity_label
        
        main_layout.addLayout(title_bar)
        
        filter_bar = QHBoxLayout()
        
        categories = [
            ("all", "全部"),
            ("food", "食物"),
            ("drink", "饮品"),
            ("toy", "\u73a9\u5177"),
            ("decoration", "\u88c5\u9970"),
            ("game", "\u6e38\u620f\u9053\u5177"),
        ]
        
        self.filter_buttons = {}
        for cat_id, cat_name in categories:
            btn = QPushButton(cat_name)
            btn.setObjectName("control_btn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, cid=cat_id: self._filter_items(cid))
            filter_bar.addWidget(btn)
            self.filter_buttons[cat_id] = btn
        
        self.filter_buttons["all"].setChecked(True)
        
        filter_bar.addStretch()
        
        sort_combo = QComboBox()
        sort_combo.addItem("按类型排序")
        sort_combo.addItem("按稀有度排序")
        sort_combo.addItem("按名称排序")
        sort_combo.addItem("按数量排序")
        sort_combo.currentIndexChanged.connect(self._sort_inventory)
        filter_bar.addWidget(sort_combo)
        
        main_layout.addLayout(filter_bar)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        grid_container = QWidget()
        grid_container.setObjectName("grid_container")
        
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        
        for i in range(self.MAX_SLOTS):
            row = i // 5
            col = i % 5
            
            slot = InventorySlot(slot_id=i)
            slot.item_used.connect(self._on_item_used)
            
            self.grid_layout.addWidget(slot, row, col)
            self.slots.append(slot)
        
        scroll_area.setWidget(grid_container)
        main_layout.addWidget(scroll_area)
        
        bottom_bar = QHBoxLayout()
        
        sort_btn = QPushButton("整理背包")
        sort_btn.setObjectName("control_btn")
        sort_btn.clicked.connect(self._sort_inventory)
        bottom_bar.addWidget(sort_btn)
        
        use_selected_btn = QPushButton("使用选中")
        use_selected_btn.setObjectName("control_btn")
        use_selected_btn.clicked.connect(self._use_selected_item)
        bottom_bar.addWidget(use_selected_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("control_btn")
        close_btn.setStyleSheet("""
            QPushButton#control_btn {
                background-color: #8a4a4a;
            }
            QPushButton#control_btn:hover {
                background-color: #aa5a5a;
            }
        """)
        close_btn.clicked.connect(self.close)
        bottom_bar.addWidget(close_btn)
        
        main_layout.addLayout(bottom_bar)
        
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
        
        self.selected_slot: Optional[InventorySlot] = None
    
    def _refresh_inventory(self):
        """刷新背包显示"""
        # 清空所有槽位
        for slot in self.slots:
            slot.clear_slot()
        
        # 根据筛选条件获取道具列表
        items_to_show = []
        
        for item_id, quantity in self.inventory.items():
            item = ItemFactory.get_item(item_id)
            if not item:
                continue
            
            # 应用筛选
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
        
        # 填充到槽位
        for idx, (item, quantity) in enumerate(items_to_show):
            if idx < len(self.slots):
                self.slots[idx].set_item(item, quantity)
        
        # 更新容量显示
        self.capacity_label.setText(f"容量: {len(self.inventory)}/{self.MAX_SLOTS}")
    
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
    
    def closeEvent(self, event):
        """关闭事件"""
        self.closed.emit()
        event.accept()
