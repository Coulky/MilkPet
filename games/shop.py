# -*- coding: utf-8 -*-
"""
商店系统模块

功能：
- 商店UI界面
- 物品购买
- 货币系统（游戏分数）
- 物品分类展示
"""

import sys
import os
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QLabel, QScrollArea, QFrame,
                             QMessageBox, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont

from .items import Item, ItemType, ItemRarity, ItemFactory


class ShopItemSlot(QFrame):
    """商店物品槽位"""

    item_buy = pyqtSignal(str)  # 购买物品信号

    def __init__(self, item: Item, price: int, parent=None):
        super().__init__(parent)

        self.item = item
        self.price = price

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(140, 180)
        self.setStyleSheet("""
            ShopItemSlot {
                background-color: rgba(58, 58, 78, 0.9);
                border: 2px solid #6a6a7e;
                border-radius: 10px;
            }
            ShopItemSlot:hover {
                border-color: #8a8abe;
                background-color: rgba(68, 68, 88, 0.9);
            }
            QLabel#shop_item_name {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QLabel#shop_item_price {
                color: #FFD700;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#shop_item_desc {
                color: #aaaaaa;
                font-size: 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)

        if self.item.icon:
            icon_label.setText(self.item.icon)
            icon_label.setStyleSheet("font-size: 36px;")
        else:
            icon_label.setText("[?]")
            icon_label.setStyleSheet("font-size: 36px;")

        layout.addWidget(icon_label)

        name_label = QLabel(self.item.name[:8])
        name_label.setObjectName("shop_item_name")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        desc_label = QLabel(self.item.description[:20] + "..." if len(self.item.description) > 20 else self.item.description)
        desc_label.setObjectName("shop_item_desc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        price_label = QLabel(f"{self.price} 分")
        price_label.setObjectName("shop_item_price")
        price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(price_label)

        buy_btn = QPushButton("购买")
        buy_btn.setObjectName("buy_btn")
        buy_btn.clicked.connect(lambda: self.item_buy.emit(self.item.id))
        layout.addWidget(buy_btn)

        self.setLayout(layout)


class ShopWindow(QWidget):
    """商店窗口"""

    closed = pyqtSignal()
    item_purchased = pyqtSignal(str, int)  # (item_id, price)

    def __init__(self, player_score: int = 0, parent=None):
        super().__init__(parent)

        self.player_score = player_score
        self.shop_items: List[Dict] = []

        self._setup_shop_items()
        self._setup_ui()

    def _setup_shop_items(self):
        """初始化商店物品"""
        shop_data = [
            ("food_apple", 10, "恢复少量体力"),
            ("food_bread", 20, "恢复中等体力"),
            ("food_cake", 50, "大量体力恢复"),
            ("potion_health", 30, "治疗药水"),
            ("potion_mana", 40, "魔法药水"),
            ("deco_hat", 100, "装饰帽子"),
            ("deco_glasses", 80, "装饰眼镜"),
            ("special_star", 200, "幸运星"),
        ]

        for item_id, price, desc in shop_data:
            item = ItemFactory.get_item(item_id)
            if item:
                self.shop_items.append({
                    'item': item,
                    'price': price,
                    'description': desc
                })

    def _setup_ui(self):
        self.setWindowTitle("商店")
        self.setFixedSize(650, 550)

        self.setAttribute(Qt.WA_QuitOnClose, False)

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
            QLabel#score {{
                color: #FFD700;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
                background: transparent;
            }}
            QPushButton#control_btn {{
                background-color: rgba(90, 122, 154, 0.9);
                color: white;
                font-size: 13px;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#control_btn:hover {{
                background-color: #6a8aaa;
            }}
            QPushButton#close_btn {{
                background-color: #8a4a4a;
                color: white;
                font-size: 13px;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#close_btn:hover {{
                background-color: #aa5a5a;
            }}
            QPushButton#buy_btn {{
                background-color: #4a7a4a;
                color: white;
                font-size: 11px;
                padding: 5px 10px;
                border-radius: 5px;
                border: none;
            }}
            QPushButton#buy_btn:hover {{
                background-color: #5a9a5a;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_layout = QHBoxLayout()

        title = QLabel("商店")
        title.setObjectName("title")
        title_layout.addWidget(title)

        score_label = QLabel(f"当前分数: {self.player_score}")
        score_label.setObjectName("score")
        self.score_label = score_label
        title_layout.addStretch()
        title_layout.addWidget(score_label)

        main_layout.addLayout(title_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(380)

        scroll_widget = QWidget()
        items_layout = QGridLayout(scroll_widget)
        items_layout.setSpacing(15)

        col = 0
        row = 0
        for idx, shop_item in enumerate(self.shop_items):
            slot = ShopItemSlot(shop_item['item'], shop_item['price'], self)
            slot.item_buy.connect(self._on_buy_item)
            items_layout.addWidget(slot, row, col)

            col += 1
            if col >= 4:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()

        close_btn = QPushButton("关闭商店")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)

        self._center_on_screen()

    def _on_buy_item(self, item_id: str):
        """购买物品"""
        shop_item = next((s for s in self.shop_items if s['item'].id == item_id), None)
        
        if not shop_item:
            return
        
        price = shop_item['price']
        
        if self.player_score < price:
            QMessageBox.warning(
                self,
                "分数不足",
                f"购买此物品需要 {price} 分\n当前分数: {self.player_score} 分",
                QMessageBox.Ok
            )
            return

        reply = QMessageBox.question(
            self,
            "确认购买",
            f"确定要购买 {shop_item['item'].name} 吗？\n\n价格: {price} 分\n剩余: {self.player_score - price} 分",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.player_score -= price
            self.score_label.setText(f"当前分数: {self.player_score}")
            self.item_purchased.emit(item_id, price)
            
            QMessageBox.information(
                self,
                "购买成功",
                f"成功购买 {shop_item['item'].name}！\n\n花费: {price} 分\n剩余: {self.player_score} 分",
                QMessageBox.Ok
            )

    def update_score(self, new_score: int):
        """更新玩家分数"""
        self.player_score = new_score
        if hasattr(self, 'score_label'):
            self.score_label.setText(f"当前分数: {self.player_score}")

    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _get_bg_path(self):
        """获取背景图片路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'images', 'beiijng.png').replace('\\', '/')

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
