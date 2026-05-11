from enum import Enum
class ItemType(Enum):
    """道具类型枚举"""
    FOOD = "food"  # 食物
    DRINK = "drink"  # 饮料
    TOY = "toy"  # 玩具
    DECORATION = "decoration"  # 装饰品

class ItemRarity(Enum):
    """道具稀有度"""
    COMMON = ("普通", "#FFFFFF")
    RARE = ("稀有", "#4A9EFF")
    EPIC = ("史诗", "#A855F7")
    LEGENDARY = ("传说", "#FFB800")

    def __init__(self, chinese_name: str, color: str):
        self.chinese_name = chinese_name
        self.color = color