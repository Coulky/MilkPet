# -*- coding: utf-8 -*-
"""
道具配置文件

只保留核心道具：
- 食物 (food)：小鱼干、布丁蛋糕、三文鱼罐头
- 饮品 (drink)：鸡骨汤、鲜羊奶、金枪鱼汤
- 玩具 (toy)：逗猫棒、玩具小老鼠、激光笔
- 游戏道具 (game)：复活币
"""
from common.common_enum import ItemType, ItemRarity


items = {
    # ========== 食物 ==========
    "dried_fish": {
        "name": "\u5c0f\u9c7c\u5e72",
        "description": "\u684c\u5ba0\u6700\u7231\u7684\u96f6\u98df\uff0c\u63d0\u5347\u9971\u98df\u5ea6",
        "item_type": ItemType.FOOD,
        "rarity": ItemRarity.COMMON,
        "icon": "assets/items/dried_fish.png",
        "boost_value": 20,
        "protection_duration": 300,
        "price": 10,
        "sell_price": 5,
    },
    "pudding_cake": {
        "name": "\u5e03\u4e01\u86cb\u7cd5",
        "description": "\u751c\u7f8e\u7684\u86cb\u7cd5\uff0c\u8ba9\u684c\u5ba0\u5f00\u5fc3",
        "item_type": ItemType.FOOD,
        "rarity": ItemRarity.RARE,
        "icon": "assets/items/pudding_cake.png",
        "boost_value": 35,
        "protection_duration": 600,
        "price": 25,
        "sell_price": 12,
    },
    "salmon_can": {
        "name": "\u4e09\u6587\u9c7c\u7f50\u5934",
        "description": "\u65b0\u9c9c\u7684\u4e09\u6587\u9c7c\uff0c\u8425\u517b\u4e30\u5bcc",
        "item_type": ItemType.FOOD,
        "rarity": ItemRarity.EPIC,
        "icon": "assets/items/salmon_can.png",
        "boost_value": 50,
        "protection_duration": 900,
        "price": 40,
        "sell_price": 20,
    },

    # ========== 饮品 ==========
    "chicken_soup": {
        "name": "\u9e21\u9aa8\u6c64",
        "description": "\u6e29\u6696\u7684\u9e21\u6c64\uff0c\u89e3\u6e34\u53c8\u5065\u5eb7",
        "item_type": ItemType.DRINK,
        "rarity": ItemRarity.COMMON,
        "icon": "assets/items/chicken_soup.png",
        "boost_value": 20,
        "protection_duration": 300,
        "price": 10,
        "sell_price": 5,
    },
    "fresh_milk": {
        "name": "\u9c9c\u7f8a\u5976",
        "description": "\u65b0\u9c9c\u7684\u7f8a\u5976\uff0c\u8865\u5145\u8425\u517b",
        "item_type": ItemType.DRINK,
        "rarity": ItemRarity.RARE,
        "icon": "assets/items/fresh_milk.png",
        "boost_value": 30,
        "protection_duration": 600,
        "price": 22,
        "sell_price": 11,
    },
    "tuna_soup": {
        "name": "\u91d1\u67aa\u9c7c\u6c64",
        "description": "\u7f8e\u5473\u7684\u91d1\u67aa\u9c7c\u6c64\uff0c\u6062\u590d\u5143\u6c14",
        "item_type": ItemType.DRINK,
        "rarity": ItemRarity.EPIC,
        "icon": "assets/items/tuna_soup.png",
        "boost_value": 45,
        "protection_duration": 900,
        "price": 38,
        "sell_price": 19,
    },

    # ========== 玩具 ==========
    "cat_teaser": {
        "name": "\u902a\u732b\u68d2",
        "description": "\u732b\u54aa\u6700\u7231\u7684\u73a9\u5177\uff0c\u73a9\u5f97\u4e0d\u4ea6\u4e50\u4e4e",
        "item_type": ItemType.TOY,
        "rarity": ItemRarity.COMMON,
        "icon": "assets/items/cat_teaser.png",
        "boost_value": 20,
        "protection_duration": 300,
        "price": 10,
        "sell_price": 5,
    },
    "toy_mouse": {
        "name": "\u73a9\u5177\u5c0f\u8001\u9f20",
        "description": "\u53ef\u7231\u7684\u5c0f\u8001\u9f20\uff0c\u8ba9\u684c\u5ba0\u5174\u594b",
        "item_type": ItemType.TOY,
        "rarity": ItemRarity.RARE,
        "icon": "assets/items/toy_mouse.png",
        "boost_value": 35,
        "protection_duration": 600,
        "price": 25,
        "sell_price": 12,
    },
    "laser_pen": {
        "name": "\u6fc0\u5149\u7b14",
        "description": "\u795e\u5947\u7684\u6fc0\u5149\uff0c\u8ba9\u684c\u5ba0\u8ffd\u9012\u4e0d\u5df2",
        "item_type": ItemType.TOY,
        "rarity": ItemRarity.EPIC,
        "icon": "assets/items/laser_pen.png",
        "boost_value": 55,
        "protection_duration": 900,
        "price": 45,
        "sell_price": 22,
    },

    # ========== 游戏道具 ==========
    "revive_coin": {
        "name": "\u590d\u6d3b\u5e01",
        "description": "\u6570\u72ec\u6e38\u620f\u4e2d\u5931\u8d25\u65f6\u53ef\u4ee5\u590d\u6d3b\uff0c\u6062\u590d\u5230\u5931\u8d25\u524d\u7684\u72b6\u6001",
        "item_type": ItemType.GAME,
        "rarity": ItemRarity.RARE,
        "icon": "assets/items/revive_coin.png",
        "boost_value": 0,
        "protection_duration": 0,
        "stackable": True,
        "max_stack": 10,
        "required_level": 1,
        "price": 30,
        "sell_price": 15,
    },
}
