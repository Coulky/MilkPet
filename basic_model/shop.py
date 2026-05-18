# -*- coding: utf-8 -*-
"""
商店系统模块

功能：
- 商店UI界面（网格布局，参照背包样式）
- 物品购买（使用自定义确认弹框）
- 货币系统（喵币）
- 物品分类展示（食物/饮品/玩具/装饰/游戏道具）
"""

import sys
import os
from typing import Dict, List

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QLabel, QScrollArea, QFrame,
                             QSizePolicy, QApplication, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from .items import Item, ItemType, ItemRarity, ItemFactory
from common.common_enum import ItemType as ItemTypeEnum
from widgets.dialog import ConfirmDialog, WarningDialog, CompleteDialog
from basic_model.resource_manager import ResourceManager


CATEGORY_MAP = {
    "all": ("\u5168\u90e8", None),
    "food": ("\u98df\u7269", ItemType.FOOD),
    "drink": ("\u996e\u54c1", ItemType.DRINK),
    "toy": ("\u73a9\u5177", ItemType.TOY),
    "decoration": ("\u88c5\u9970", ItemType.DECORATION),
    "game": ("\u6e38\u620f\u9053\u5177", ItemType.GAME),
}

RARITY_COLORS = {
    ItemRarity.COMMON: "#aaaaaa",
    ItemRarity.RARE: "#4a9eff",
    ItemRarity.EPIC: "#b04aff",
    ItemRarity.LEGENDARY: "#ffaa00",
}


class ShopItemSlot(QFrame):
    """商店物品槽位 - 参照背包 InventorySlot 样式"""

    item_buy = pyqtSignal(str)

    def __init__(self, item: Item, parent=None):
        super().__init__(parent)
        self.item = item
        from basic_model.resource_manager import ResourceManager
        self.resource_manager = ResourceManager()
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(120, 150)

        rarity_color = RARITY_COLORS.get(self.item.rarity, "#aaaaaa")
        self.setStyleSheet(f"""
            ShopItemSlot {{
                background-color: #ffffff;
                border: 2px solid {rarity_color};
                border-radius: 10px;
            }}
            QLabel#shop_icon {{
                font-size: 32px;
                background: transparent;
            }}
            QLabel#shop_name {{
                color: #8a8070;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }}
            QPushButton#buy_btn {{
                background-color: #4a7a4a;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                padding: 3px 8px;
            }}
            QPushButton#buy_btn:hover {{ background-color: #5a9a5a; }}
            QPushButton#buy_btn:disabled {{
                background-color: #333333;
                color: #666666;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setObjectName("shop_icon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(96, 96)

        if self.item.icon and (self.item.icon.endswith('.png') or self.item.icon.endswith('.jpg') or self.item.icon.endswith('.jpeg')):
            icon_path = self.item.icon
            if not os.path.isabs(icon_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                icon_path = os.path.join(base_dir, icon_path)
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                icon_label.setText("[?]")
        else:
            icon_label.setText(self.item.icon if self.item.icon else "[?]")
        layout.addWidget(icon_label)

        name_text = self.item.name[:8]
        if len(self.item.name) > 8:
            name_text += ".."
        name_label = QLabel(name_text)
        name_label.setObjectName("shop_name")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        price_label = self.resource_manager.create_coin_label(text=str(self.item.price), icon_size=12, font_size=11)
        price_label.setObjectName("shop_price")
        if hasattr(price_label, '_text_label'):
            price_label._text_label.setStyleSheet("color: #8a8070; font-size: 11px; font-weight: bold; background: transparent;")
        layout.addWidget(price_label)

        buy_btn = QPushButton("\u8d2d\u4e70")
        buy_btn.setObjectName("buy_btn")
        buy_btn.clicked.connect(lambda: self.item_buy.emit(self.item.id))
        self.buy_btn = buy_btn
        layout.addWidget(buy_btn)

        self.setLayout(layout)

    def set_purchasable(self, can_buy: bool):
        """设置是否可购买（只置灰购买按钮，不影响图标显示）"""
        self.buy_btn.setEnabled(can_buy)


class ShopWindow(QWidget):
    """商店窗口"""

    closed = pyqtSignal()
    item_purchased = pyqtSignal(str, int)

    def __init__(self, player_score: int = 0, player_level: int = 0, owned_items: Dict[str, int] = None, parent=None):
        super().__init__(parent)

        self.player_score = player_score
        self.player_level = player_level
        self.owned_items = owned_items or {}
        self.current_category = "all"
        self.shop_items: List[Item] = []
        self.slots: List[ShopItemSlot] = []
        self.resource_manager = ResourceManager()

        self._load_items()
        self._setup_ui()

    def _load_items(self):
        ItemFactory.initialize()
        all_items = ItemFactory.get_all_items()
        self.shop_items = sorted(
            all_items.values(),
            key=lambda x: (x.item_type.value, x.price)
        )

    def _get_filtered_items(self) -> List[Item]:
        if self.current_category == "all":
            return self.shop_items
        cat_type = CATEGORY_MAP.get(self.current_category, (None, None))[1]
        if cat_type is None:
            return self.shop_items
        return [item for item in self.shop_items if item.item_type == cat_type]

    def _setup_ui(self):
        self.setWindowTitle("\u5546\u5e97")
        self.setFixedSize(720, 600)
        self.setWindowIcon(self.resource_manager.logo_icon)

        self.setAttribute(Qt.WA_QuitOnClose, False)

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
            QLabel#score {{
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
        title = QLabel("\u5546\u5e97")
        title.setObjectName("title")
        title_bar.addWidget(title)

        score_label = self.resource_manager.create_coin_label(text=str(self.player_score), icon_size=15, font_size=14)
        score_label.setObjectName("score")
        self.score_label = score_label
        title_bar.addStretch()
        title_bar.addWidget(score_label)
        main_layout.addLayout(title_bar)

        category_bar = QHBoxLayout()
        category_bar.setSpacing(5)

        self.cat_buttons = {}
        for cat_id, (cat_name, _) in CATEGORY_MAP.items():
            is_selected = (cat_id == "all")
            btn = self.resource_manager.create_action_button(
                text=cat_name,
                size="small",
                selected=is_selected,
                callback=lambda checked, cid=cat_id: self._switch_category(cid),
                parent=self
            )
            category_bar.addWidget(btn)
            self.cat_buttons[cat_id] = btn
        category_bar.addStretch()

        sort_combo = self.resource_manager.create_styled_combo(
            options=[("综合", 0), ("按稀有度", 1), ("按等级", 2), ("仅按价格", 3)],
            callback=self._sort_items
        )
        category_bar.addWidget(sort_combo)

        main_layout.addLayout(category_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.grid_container = QWidget()
        self.grid_container.setObjectName("grid_container")

        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(12, 12, 12, 12)

        self._refresh_display()

        scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(scroll_area, stretch=1)

        bottom_bar = QHBoxLayout()
        
        close_btn = self.resource_manager.create_styled_button(
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

    def _switch_category(self, cat_id: str):
        self.current_category = cat_id
        for cid, btn in self.cat_buttons.items():
            btn.setChecked(cid == cat_id)
        self._refresh_display()

    def _sort_items(self, index: int):
        filtered = self._get_filtered_items()
        if index == 0:
            filtered.sort(key=lambda x: (x.item_type.value, x.price))
        elif index == 1:
            filtered.sort(key=lambda x: x.rarity.value)
        elif index == 2:
            filtered.sort(key=lambda x: x.required_level)
        elif index == 3:
            filtered.sort(key=lambda x: x.price)
        self._display_grid(filtered)

    def _refresh_display(self):
        filtered = self._get_filtered_items()
        self._display_grid(filtered)

    def _display_grid(self, items: List[Item]):
        for slot in self.slots:
            slot.deleteLater()
        self.slots.clear()

        col = 0
        row = 0
        cols_per_row = 5

        for item in items:
            slot = ShopItemSlot(item, self)
            slot.item_buy.connect(self._on_buy_item)

            if self.player_level < item.required_level:
                slot.set_purchasable(False)

            self.grid_layout.addWidget(slot, row, col)
            self.slots.append(slot)

            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1

    def _on_buy_item(self, item_id: str):
        item = ItemFactory.get_item(item_id)
        if not item:
            return

        if self.player_level < item.required_level:
            dlg = WarningDialog(
                "\u7b49\u7ea7\u4e0d\u8db3",
                f"需要 Lv.{item.required_level} \u624d\u80fd\u8d2d\u4e70\u300e{item.name}\u300f\n\u5f53\u524d\u7b49\u7ea7: Lv.{self.player_level}",
                "warning",
                self
            )
            dlg.confirmed.connect(dlg.close)
            dlg.show()
            return

        if self.player_score < item.price:
            dlg = WarningDialog(
                "\u55b5\u5e01\u4e0d\u8db3",
                f"\u8d2d\u4e70\u300e{item.name}\u300f\u9700\u8981 {item.price} \U0001f4b0\n\u5f53\u524d\u62e5\u6709: {self.player_score} \U0001f4b0",
                "warning",
                self
            )
            dlg.confirmed.connect(dlg.close)
            dlg.show()
            return

        if item.item_type == ItemType.DECORATION and item.id in self.owned_items:
            dlg = WarningDialog(
                "\u5df2\u62e5\u6709\u6b64\u9970\u54c1",
                f"\u60a8\u5df2\u7ecf\u62e5\u6709\u300e{item.name}\u300f\uff0c\n\u540c\u4e00\u65f6\u95f4\u53ea\u80fd\u88c5\u59071\u4e2a\u76f8\u540c\u9970\u54c1\u3002",
                "warning",
                self
            )
            dlg.confirmed.connect(dlg.close)
            dlg.show()
            return

        confirm_dlg = ConfirmDialog(
            "\u786e\u8ba4\u8d2d\u4e70",
            f"\u786e\u5b9a\u8981\u8d2d\u4e70\u300e{item.name}\u300f\u5417\uff1f\n\n"
            f"\u4ef7\u683c: {item.price} \U0001f4b0\n"
            f"\u5269\u4f59: {self.player_score - item.price} \U0001f4b0",
            "confirm",
            self
        )

        def on_confirm():
            self.player_score -= item.price
            self.score_label._text_label.setText(str(self.player_score))
            self.item_purchased.emit(item.id, item.price)

            complete_dlg = CompleteDialog(
                "\u8d2d\u4e70\u6210\u529f",
                f"\u6210\u529f\u8d2d\u4e70\u300e{item.name}\u300f\uff01\n\n"
                f"\u82b1\u8d39: {item.price} \U0001f4b0\n"
                f"\u5269\u4f59: {self.player_score} \U0001f4b0",
                "complete",
                self
            )
            complete_dlg.confirmed.connect(complete_dlg.close)
            complete_dlg.show()

        confirm_dlg.confirmed.connect(on_confirm)
        confirm_dlg.cancelled.connect(confirm_dlg.close)
        confirm_dlg.show()

    def update_score(self, new_score: int):
        self.player_score = new_score
        if hasattr(self, 'score_label'):
            self.score_label._text_label.setText(str(self.player_score))

    def update_level(self, new_level: int):
        self.player_level = new_level
        self._refresh_display()

    def update_owned_items(self, owned: Dict[str, int]):
        self.owned_items = owned or {}

    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _get_bg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'background.png').replace('\\', '/')

    def _get_btn_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets', 'button.png').replace('\\', '/')

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()