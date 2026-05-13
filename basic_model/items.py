# -*- coding: utf-8 -*-
"""
道具系统模块

物品分类：
- 食物 (food)：提升饱食度 + 保护不降
- 饮品 (drink)：提升饥渴值 + 保护不降
- 玩具 (toy)：提升心情 + 保护不降
- 装饰 (decoration)：仅装饰，可设置有效期/永久，每槽位一个
"""

import sys
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from common.common_enum import ItemType, ItemRarity, DecorationPosition

from config.item_settings import items as item_settings


@dataclass
class Item:
    """道具数据类"""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    icon: str
    boost_value: int = 0                # 立即提升数值
    protection_duration: float = 0      # 保护不降持续时间（秒），0=无保护
    decoration_slot: str = ""
    position: DecorationPosition = None
    decoration_duration: float = 0
    required_level: int = 0             # 购买/使用所需等级，0=无限制
    stackable: bool = True
    max_stack: int = 99
    price: int = 0
    sell_price: int = 0

    def get_display_name(self) -> str:
        return f"{self.name} [{self.rarity.chinese_name}]"

    def get_tooltip(self) -> str:
        tooltip = f"【{self.get_display_name()}】\n"
        tooltip += f"{self.description}\n\n"

        if self.item_type == ItemType.FOOD:
            tooltip += f"效果：饱食度 +{self.boost_value}\n"
            if self.protection_duration > 0:
                mins = int(self.protection_duration / 60)
                tooltip += f"保护：{mins}分钟内饱食度不降\n"
        elif self.item_type == ItemType.DRINK:
            tooltip += f"效果：饥渴值 +{self.boost_value}\n"
            if self.protection_duration > 0:
                mins = int(self.protection_duration / 60)
                tooltip += f"保护：{mins}分钟内饥渴值不降\n"
        elif self.item_type == ItemType.TOY:
            tooltip += f"效果：心情 +{self.boost_value}\n"
            if self.protection_duration > 0:
                mins = int(self.protection_duration / 60)
                tooltip += f"保护：{mins}分钟内心情不降\n"
        elif self.item_type == ItemType.DECORATION:
            if self.decoration_duration > 0:
                mins = int(self.decoration_duration / 60)
                tooltip += f"有效期：{mins}分钟\n"
            else:
                tooltip += "有效期：永久\n"
            if self.required_level > 0:
                tooltip += f"需要等级：Lv.{self.required_level}\n"
        elif self.item_type == ItemType.GAME:
            tooltip += f"{self.description}\n"
            if self.required_level > 0:
                tooltip += f"需要等级：Lv.{self.required_level}\n"

        if self.price > 0:
            tooltip += f"\n💰 价格: {self.price} 喵币"

        return tooltip


class ItemFactory:
    """道具工厂"""

    _items: Dict[str, Item] = {}

    @classmethod
    def initialize(cls):
        """初始化道具工厂"""
        cls._create_items()

    @classmethod
    def _create_items(cls):
        for item_id, item in item_settings.items():
            cls._items[item_id] = Item(id=item_id, **item)

    @classmethod
    def get_item(cls, item_id: str) -> Optional[Item]:
        return cls._items.get(item_id)

    @classmethod
    def get_all_items(cls) -> Dict[str, Item]:
        return cls._items.copy()

    @classmethod
    def get_items_by_type(cls, item_type: ItemType) -> List[Item]:
        return [item for item in cls._items.values() if item.item_type == item_type]

    @classmethod
    def get_random_item(cls, rarity: ItemRarity = None) -> Optional[Item]:
        items = list(cls._items.values())
        if rarity:
            items = [item for item in items if item.rarity == rarity]
        if not items:
            return None
        import random
        return random.choice(items)

    @classmethod
    def get_loot_drop(cls) -> Optional[Item]:
        import random
        weights = {
            ItemRarity.COMMON: 50,
            ItemRarity.RARE: 30,
            ItemRarity.EPIC: 15,
            ItemRarity.LEGENDARY: 5,
        }
        rand = random.randint(1, 100)
        cumulative = 0
        selected_rarity = ItemRarity.COMMON
        for rarity, weight in weights.items():
            cumulative += weight
            if rand <= cumulative:
                selected_rarity = rarity
                break
        items = [item for item in cls._items.values() if item.rarity == selected_rarity]
        if items:
            return random.choice(items)
        return cls.get_random_item()


ItemFactory.initialize()