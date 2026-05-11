# -*- coding: utf-8 -*-
"""
游戏模块包

包含：
- dh_puzzle.py: 数字华容道游戏
- sudoku.py: 数独游戏
- inventory.py: 背包系统
- items.py: 道具系统
- statistics.py: 数据统计系统
"""

from .dh_puzzle import DHPuzzle
from .sudoku import SudokuGame
from .inventory import InventoryWindow, InventorySlot
from .items import (ItemFactory, Item, ItemType, ItemRarity)
from .statistics import (StatisticsManager, Achievement, GameStats, 
                        PlayerStats, AchievementType)

__all__ = [
    # 游戏
    'DHPuzzle',
    'SudokuGame',
    
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
