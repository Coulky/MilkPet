# -*- coding: utf-8 -*-
"""
游戏模块包

包含：
- dh_puzzle.py: 数字华容道游戏
- sudoku.py: 数独游戏
"""

from .dh_puzzle import DHPuzzle
from .sudoku import SudokuGame

__all__ = [
    'DHPuzzle',
    'SudokuGame',
]