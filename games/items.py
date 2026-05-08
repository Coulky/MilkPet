# -*- coding: utf-8 -*-
"""
道具系统模块

定义所有道具类型和属性：
- 食物类：恢复心情值、增加饱食度
- 功能道具：游戏辅助功能
- 装饰品：桌宠外观变化
- 特殊道具：解锁成就、获得奖励
"""

import sys
import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable


class ItemType(Enum):
    """道具类型枚举"""
    FOOD = "food"           # 食物
    CONSUMABLE = "consumable"  # 消耗品（功能道具）
    DECORATION = "decoration"  # 装饰品
    SPECIAL = "special"      # 特殊道具


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
class ItemEffect:
    """道具效果"""
    effect_type: str  # mood, hunger, game_hint, skip_level, appearance, achievement
    value: int = 0
    description: str = ""
    
    def apply(self, target=None) -> str:
        """应用效果并返回描述"""
        if self.effect_type == "mood":
            return f"心情值 +{self.value}"
        elif self.effect_type == "hunger":
            return f"饱食度 +{self.value}"
        elif self.effect_type == "game_hint":
            return "获得游戏提示"
        elif self.effect_type == "skip_level":
            return "跳过当前关卡"
        elif self.effect_type == "appearance":
            return f"外观变更：{self.description}"
        elif self.effect_type == "achievement":
            return f"解锁成就：{self.description}"
        return ""


@dataclass
class Item:
    """道具数据类"""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    icon: str  # 图标路径或emoji
    effects: List[ItemEffect]
    stackable: bool = True
    max_stack: int = 99
    price: int = 0  # 价格（用于商店）
    sell_price: int = 0  # 出售价格
    
    def get_display_name(self) -> str:
        """获取带稀有度的显示名称"""
        return f"{self.name} [{self.rarity.chinese_name}]"
    
    def get_tooltip(self) -> str:
        """获取道具提示信息"""
        tooltip = f"【{self.get_display_name()}】\n"
        tooltip += f"{self.description}\n\n"
        
        if self.effects:
            tooltip += "效果：\n"
            for effect in self.effects:
                tooltip += f"  • {effect.apply()}\n"
        
        if self.price > 0:
            tooltip += f"\n💰 价格: {self.price} 金币"
        
        return tooltip


class ItemFactory:
    """道具工厂 - 创建和管理所有道具"""
    
    _items: Dict[str, Item] = {}
    
    @classmethod
    def initialize(cls):
        """初始化所有道具"""
        cls._create_food_items()
        cls._create_consumable_items()
        cls._create_decoration_items()
        cls._create_special_items()
    
    @classmethod
    def _create_food_items(cls):
        """创建食物类道具"""
        food_items = [
            Item(
                id="fish",
                name="🐟 新鲜鱼干",
                description="桌宠最爱的零食，能显著提升心情",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.COMMON,
                icon="🐟",
                effects=[ItemEffect("mood", 20, "心情愉悦"), ItemEffect("hunger", 30, "填饱肚子")],
                price=10,
                sell_price=5
            ),
            Item(
                id="cake",
                name="🎂 小蛋糕",
                description="甜美的蛋糕，让桌宠开心一整天",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.RARE,
                icon="🎂",
                effects=[ItemEffect("mood", 35, "非常开心"), ItemEffect("hunger", 40, "大餐")],
                price=25,
                sell_price=12
            ),
            Item(
                id="milk",
                name="🥛 温热牛奶",
                description="温暖的牛奶，安抚情绪的好帮手",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.COMMON,
                icon="🥛",
                effects=[ItemEffect("mood", 15, "平静"), ItemEffect("hunger", 20, "小食")],
                price=8,
                sell_price=4
            ),
            Item(
                id="pizza",
                name="🍕 迷你披萨",
                description="美味的披萨切片，丰盛的一餐",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.RARE,
                icon="🍕",
                effects=[ItemEffect("mood", 25, "满足"), ItemEffect("hunger", 50, "饱餐")],
                price=30,
                sell_price=15
            ),
            Item(
                id="star_candy",
                name="⭐ 星星糖果",
                description="神奇的糖果，大幅提升各项数值",
                item_type=ItemType.FOOD,
                rarity=ItemRarity.EPIC,
                icon="⭐",
                effects=[ItemEffect("mood", 50, "超级开心"), ItemEffect("hunger", 60, "超级大餐")],
                price=80,
                sell_price=40
            ),
        ]
        
        for item in food_items:
            cls._items[item.id] = item
    
    @classmethod
    def _create_consumable_items(cls):
        """创建消耗品类道具"""
        consumable_items = [
            Item(
                id="hint_scroll",
                name="📜 提示卷轴",
                description="在游戏中获得一次智能提示",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.COMMON,
                icon="📜",
                effects=[ItemEffect("game_hint", 1, "游戏提示")],
                price=15,
                sell_price=7
            ),
            Item(
                id="skip_card",
                name="⏭️ 跳过关卡卡",
                description="直接通过当前游戏关卡",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.RARE,
                icon="⏭️",
                effects=[ItemEffect("skip_level", 1, "跳过")],
                price=50,
                sell_price=25
            ),
            Item(
                id="time_freeze",
                name="❄️ 时间冻结",
                description="冻结游戏计时器30秒",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.RARE,
                icon="❄️",
                effects=[ItemEffect("time_freeze", 30, "时间停止")],
                price=35,
                sell_price=17
            ),
            Item(
                id="double_score",
                name="✨ 双倍积分",
                description="下一局游戏积分翻倍",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.EPIC,
                icon="✨",
                effects=[ItemEffect("double_score", 1, "双倍积分")],
                price=60,
                sell_price=30
            ),
            Item(
                id="auto_solve",
                name="🤖 自动求解",
                description="自动完成当前数独或华容道",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.LEGENDARY,
                icon="🤖",
                effects=[ItemEffect("auto_solve", 1, "自动通关")],
                price=150,
                sell_price=75
            ),
        ]
        
        for item in consumable_items:
            cls._items[item.id] = item
    
    @classmethod
    def _create_decoration_items(cls):
        """创建装饰品类道具"""
        decoration_items = [
            Item(
                id="crown",
                name="👑 皇冠",
                description="让桌宠戴上皇冠，变得尊贵起来",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.EPIC,
                icon="👑",
                effects=[ItemEffect("appearance", 0, "戴上皇冠")],
                stackable=False,
                price=100,
                sell_price=50
            ),
            Item(
                id="glasses",
                name="🤓 眼镜",
                description="时尚的眼镜，让桌宠看起来更聪明",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.RARE,
                icon="🤓",
                effects=[ItemEffect("appearance", 0, "戴上眼镜")],
                stackable=False,
                price=60,
                sell_price=30
            ),
            Item(
                id="hat",
                name="🎩 礼帽",
                description="优雅的礼帽，绅士风度满满",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.RARE,
                icon="🎩",
                effects=[ItemEffect("appearance", 0, "戴上礼帽")],
                stackable=False,
                price=55,
                sell_price=27
            ),
            Item(
                id="wings",
                name="👼 天使之翼",
                description="神圣的翅膀，让桌宠如天使般美丽",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.LEGENDARY,
                icon="👼",
                effects=[ItemEffect("appearance", 0, "长出翅膀")],
                stackable=False,
                price=200,
                sell_price=100
            ),
            Item(
                id="bow_tie",
                name="🎀 蝴蝶结",
                description="可爱的蝴蝶结，增添可爱气息",
                item_type=ItemType.DECORATION,
                rarity=ItemRarity.COMMON,
                icon="🎀",
                effects=[ItemEffect("appearance", 0, "系上蝴蝶结")],
                stackable=False,
                price=20,
                sell_price=10
            ),
        ]
        
        for item in decoration_items:
            cls._items[item.id] = item
    
    @classmethod
    def _create_special_items(cls):
        """创建特殊道具"""
        special_items = [
            Item(
                id="lucky_coin",
                name="🪙 幸运金币",
                description="使用后随机获得一件稀有道具",
                item_type=ItemType.SPECIAL,
                rarity=ItemRarity.RARE,
                icon="🪙",
                effects=[ItemEffect("random_rare_item", 1, "随机稀有道具")],
                price=100,
                sell_price=0  # 不可出售
            ),
            Item(
                id="mystery_box",
                name="🎁 神秘礼盒",
                description="打开可能获得史诗或传说级道具！",
                item_type=ItemType.SPECIAL,
                rarity=ItemRarity.EPIC,
                icon="🎁",
                effects=[ItemEffect("random_epic_item", 1, "随机史诗道具")],
                price=200,
                sell_price=0
            ),
            Item(
                id="achievement_key",
                name="🔑 成就钥匙",
                description="立即解锁一个未完成的成就",
                item_type=ItemType.SPECIAL,
                rarity=ItemRarity.LEGENDARY,
                icon="🔑",
                effects=[ItemEffect("achievement", 1, "解锁成就")],
                price=300,
                sell_price=0
            ),
        ]
        
        for item in special_items:
            cls._items[item.id] = item
    
    @classmethod
    def get_item(cls, item_id: str) -> Optional[Item]:
        """根据ID获取道具"""
        return cls._items.get(item_id)
    
    @classmethod
    def get_all_items(cls) -> Dict[str, Item]:
        """获取所有道具"""
        return cls._items.copy()
    
    @classmethod
    def get_items_by_type(cls, item_type: ItemType) -> List[Item]:
        """根据类型获取道具列表"""
        return [item for item in cls._items.values() if item.item_type == item_type]
    
    @classmethod
    def get_random_item(cls, rarity: ItemRarity = None) -> Optional[Item]:
        """随机获取一个道具"""
        items = list(cls._items.values())
        
        if rarity:
            items = [item for item in items if item.rarity == rarity]
        
        if not items:
            return None
        
        import random
        return random.choice(items)
    
    @classmethod
    def get_loot_drop(cls) -> Item:
        """模拟战利品掉落（加权随机）"""
        import random
        
        weights = {
            ItemRarity.COMMON: 50,
            ItemRarity.RARE: 30,
            ItemRarity.EPIC: 15,
            ItemRarity.LEGENDARY: 5
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


# 初始化道具工厂
ItemFactory.initialize()
