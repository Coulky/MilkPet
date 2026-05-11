from enum import Enum


class ItemType(Enum):
    """道具类型枚举"""
    FOOD = "food"
    DRINK = "drink"
    TOY = "toy"
    DECORATION = "decoration"
    GAME = "game"


class ItemRarity(Enum):
    """道具稀有度"""
    COMMON = ("普通", "#FFFFFF")
    RARE = ("稀有", "#4A9EFF")
    EPIC = ("史诗", "#A855F7")
    LEGENDARY = ("传说", "#FFB800")

    def __init__(self, chinese_name: str, color: str):
        self.chinese_name = chinese_name
        self.color = color


class AchievementType(Enum):
    """成就类型"""
    GAME_WINS = "game_wins"
    PLAY_TIME = "play_time"
    ITEMS_COLLECTED = "items"
    PERFECT_GAME = "perfect_game"
    SPEED_CLEAR = "speed_clear"
    SOCIAL = "social"
    EXPLORER = "explorer"