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


class ItemType(Enum):
    """道具类型枚举"""
    FOOD = "food"
    DRINK = "drink"
    TOY = "toy"
    DECORATION = "decoration"


class ItemRarity(Enum):
    """道具稀有度"""
    COMMON = ("普通", "#FFFFFF")
    RARE = ("稀有", "#4A9EFF")
    EPIC = ("史诗", "#A855F7")
    LEGENDARY = ("传说", "#FFB800")

    def __init__(self, chinese_name: str, color: str):
        self.chinese_name = chinese_name
        self.color = color


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
    decoration_slot: str = ""           # 装饰品槽位 (head/face/body/accessory)
    decoration_duration: float = 0      # 装饰品有效期（秒），0=永久
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

        if self.price > 0:
            tooltip += f"\n💰 价格: {self.price} 喵币"

        return tooltip


class ItemFactory:
    """道具工厂"""

    _items: Dict[str, Item] = {}

    @classmethod
    def initialize(cls):
        cls._create_food_items()
        cls._create_drink_items()
        cls._create_toy_items()
        cls._create_decoration_items()

    @classmethod
    def _create_food_items(cls):
        items = [
            Item(
                id="fish",
                name="🐟 新鲜鱼干",
                description="桌宠最爱的零食",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.COMMON,
                icon="🐟",
                boost_value=20,
                protection_duration=300,
                price=10,
                sell_price=5,
            ),
            Item(
                id="cake",
                name="🎂 小蛋糕",
                description="甜美的蛋糕，让桌宠开心一整天",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.RARE,
                icon="🎂",
                boost_value=35,
                protection_duration=600,
                price=25,
                sell_price=12,
            ),
            Item(
                id="pizza",
                name="🍕 迷你披萨",
                description="美味的披萨切片，丰盛的一餐",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.RARE,
                icon="🍕",
                boost_value=50,
                protection_duration=900,
                price=30,
                sell_price=15,
            ),
            Item(
                id="star_candy",
                name="⭐ 星星糖果",
                description="神奇的糖果，大幅提升饱食度",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.EPIC,
                icon="⭐",
                boost_value=80,
                protection_duration=1800,
                price=80,
                sell_price=40,
            ),
        ]
        for item in items:
            cls._items[item.id] = item

    @classmethod
    def _create_drink_items(cls):
        items = [
            Item(
                id="milk",
                name="🥛 温热牛奶",
                description="温暖的牛奶，解渴又健康",
                item_type=ItemType.DRINK,
                rarity=ItemRarity.COMMON,
                icon="🥛",
                boost_value=20,
                protection_duration=300,
                price=8,
                sell_price=4,
            ),
            Item(
                id="juice",
                name="🧃 鲜榨果汁",
                description="新鲜水果榨汁，清爽解渴",
                item_type=ItemType.DRINK,
                rarity=ItemRarity.COMMON,
                icon="🧃",
                boost_value=25,
                protection_duration=360,
                price=12,
                sell_price=6,
            ),
            Item(
                id="bubble_tea",
                name="🧋 珍珠奶茶",
                description="甜甜的奶茶，幸福感满满",
                item_type=ItemType.DRINK,
                rarity=ItemRarity.RARE,
                icon="🧋",
                boost_value=40,
                protection_duration=720,
                price=22,
                sell_price=11,
            ),
            Item(
                id="magic_potion",
                name="🧪 魔法药水",
                description="神秘的药水，大幅提升饥渴值",
                item_type=ItemType.DRINK,
                rarity=ItemRarity.EPIC,
                icon="🧪",
                boost_value=70,
                protection_duration=1500,
                price=70,
                sell_price=35,
            ),
        ]
        for item in items:
            cls._items[item.id] = item

    @classmethod
    def _create_toy_items(cls):
        items = [
            Item(
                id="yarn_ball",
                name="� 毛线球",
                description="猫咪最爱的玩具，玩得不亦乐乎",
                item_type=ItemType.TOY,
                rarity=ItemRarity.COMMON,
                icon="�",
                boost_value=20,
                protection_duration=300,
                price=10,
                sell_price=5,
            ),
            Item(
                id="feather_wand",
                name="🪶 羽毛棒",
                description="逗猫神器，让桌宠兴奋不已",
                item_type=ItemType.TOY,
                rarity=ItemRarity.RARE,
                icon="🪶",
                boost_value=35,
                protection_duration=600,
                price=25,
                sell_price=12,
            ),
            Item(
                id="puzzle_toy",
                name="� 益智玩具",
                description="锻炼脑力的好玩具",
                item_type=ItemType.TOY,
                rarity=ItemRarity.RARE,
                icon="�",
                boost_value=30,
                protection_duration=480,
                price=20,
                sell_price=10,
            ),
            Item(
                id="golden_bell",
                name="🔔 金色铃铛",
                description="闪闪发光的铃铛，让桌宠无比快乐",
                item_type=ItemType.TOY,
                rarity=ItemRarity.EPIC,
                icon="🔔",
                boost_value=60,
                protection_duration=1200,
                price=60,
                sell_price=30,
            ),
        ]
        for item in items:
            cls._items[item.id] = item

    @classmethod
    def _create_decoration_items(cls):
        items = [
            Item(
                id="crown",
                name="� 皇冠",
                description="尊贵的皇冠",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.EPIC,
                icon="�",
                decoration_slot="head",
                decoration_duration=0,
                stackable=False,
                price=100,
                sell_price=50,
            ),
            Item(
                id="glasses",
                name="🤓 眼镜",
                description="时尚的眼镜",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.RARE,
                icon="🤓",
                decoration_slot="face",
                decoration_duration=86400,
                stackable=False,
                price=60,
                sell_price=30,
            ),
            Item(
                id="hat",
                name="🎩 礼帽",
                description="优雅的礼帽",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.RARE,
                icon="🎩",
                decoration_slot="head",
                decoration_duration=0,
                stackable=False,
                price=55,
                sell_price=27,
            ),
            Item(
                id="wings",
                name="👼 天使之翼",
                description="神圣的翅膀",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.LEGENDARY,
                icon="👼",
                decoration_slot="body",
                decoration_duration=0,
                stackable=False,
                price=200,
                sell_price=100,
            ),
            Item(
                id="bow_tie",
                name="🎀 蝴蝶结",
                description="可爱的蝴蝶结",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.COMMON,
                icon="🎀",
                decoration_slot="accessory",
                decoration_duration=3600,
                stackable=False,
                price=20,
                sell_price=10,
            ),
        ]
        for item in items:
            cls._items[item.id] = item

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