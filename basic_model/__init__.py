# -*- coding: utf-8 -*-
"""
游戏模块包

包含：
- inventory.py: 背包系统
- items.py: 道具系统
- statistics.py: 数据统计系统
"""

from .inventory import InventoryWindow, InventorySlot
from .items import (ItemFactory, Item, ItemType, ItemRarity)
from .statistics import (StatisticsManager, Achievement, GameStats,
                        PlayerStats)
from common.common_enum import AchievementType

__all__ = [
    # 背包
    'InventoryWindow',
    'InventorySlot',
    
    # 道具
    'ItemFactory',
    'Item',
    'ItemType',
    'ItemRarity',
    
    # 统计
    'StatisticsManager',
    'Achievement',
    'GameStats',
    'PlayerStats',
]
