# -*- coding: utf-8 -*-
"""
桌宠属性系统

管理桌宠的属性值：
- 饱食度 (satiety)
- 饥渴值 (thirst)
- 心情 (mood)
- 经验值 (exp)

功能：
- 属性自然衰减
- 属性联动经验增减
- 喵币自动获取（防离线过量）
- 物品效果管理（保护不降）
"""

import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional

from config.settings import (
    COIN_AUTO_INTERVAL, COIN_AUTO_AMOUNT, COIN_MAX_OFFLINE_EARN,
    PET_INIT_SATIETY, PET_INIT_THIRST, PET_INIT_MOOD, PET_INIT_EXP,
    PET_DECAY_SATIETY, PET_DECAY_THIRST, PET_DECAY_MOOD,
    PET_ATTR_MIN, PET_ATTR_MAX,
    EXP_THRESHOLDS, EXP_MIN, EXP_MAX,
)


@dataclass
class PetStats:
    """桌宠属性数据"""

    satiety: float = PET_INIT_SATIETY
    thirst: float = PET_INIT_THIRST
    mood: float = PET_INIT_MOOD
    exp: float = PET_INIT_EXP

    # 时间追踪
    last_decay_time: float = 0.0
    last_coin_time: float = 0.0
    last_exp_check_time: float = 0.0
    last_login_time: float = 0.0

    # 物品保护效果（剩余秒数）
    satiety_protection: float = 0.0
    thirst_protection: float = 0.0
    mood_protection: float = 0.0

    # 装饰品装备状态 {slot: {"item_id": str, "expire_time": float (0=永久)}}
    equipped_decorations: Dict[str, dict] = field(default_factory=dict)

    # 活跃物品效果列表 [{"item_id": str, "type": str, "remaining": float}]
    active_effects: list = field(default_factory=list)

    def clamp(self, value: float) -> float:
        return max(PET_ATTR_MIN, min(PET_ATTR_MAX, value))

    def clamp_exp(self, value: float) -> float:
        return max(EXP_MIN, min(EXP_MAX, value))

    # ================================================================
    # 属性衰减
    # ================================================================
    def apply_decay(self, now: float) -> dict:
        """应用属性自然衰减，返回变化量"""
        if self.last_decay_time <= 0:
            self.last_decay_time = now
            return {"satiety": 0, "thirst": 0, "mood": 0}

        elapsed = now - self.last_decay_time
        self.last_decay_time = now

        changes = {"satiety": 0.0, "thirst": 0.0, "mood": 0.0}

        # 饱食度衰减（有保护则跳过）
        if self.satiety_protection > 0:
            self.satiety_protection = max(0, self.satiety_protection - elapsed)
        else:
            decay = PET_DECAY_SATIETY * elapsed
            self.satiety = self.clamp(self.satiety - decay)
            changes["satiety"] = -decay

        # 饥渴值衰减
        if self.thirst_protection > 0:
            self.thirst_protection = max(0, self.thirst_protection - elapsed)
        else:
            decay = PET_DECAY_THIRST * elapsed
            self.thirst = self.clamp(self.thirst - decay)
            changes["thirst"] = -decay

        # 心情衰减
        if self.mood_protection > 0:
            self.mood_protection = max(0, self.mood_protection - elapsed)
        else:
            decay = PET_DECAY_MOOD * elapsed
            self.mood = self.clamp(self.mood - decay)
            changes["mood"] = -decay

        # 更新活跃效果剩余时间
        self._update_active_effects(elapsed)

        return changes

    def _update_active_effects(self, elapsed: float):
        """更新活跃物品效果剩余时间"""
        remaining = []
        for effect in self.active_effects:
            effect["remaining"] -= elapsed
            if effect["remaining"] > 0:
                remaining.append(effect)
        self.active_effects = remaining

    # ================================================================
    # 经验值联动
    # ================================================================
    def check_exp_threshold(self, now: float) -> int:
        """检查属性阈值，返回经验变化量"""
        if self.last_exp_check_time <= 0:
            self.last_exp_check_time = now
            return 0

        # 取三个属性的最小值来判断档位
        min_attr = min(self.satiety, self.thirst, self.mood)

        # 找到匹配的阈值配置
        matched_threshold = None
        for threshold, interval, change in EXP_THRESHOLDS:
            if change > 0:
                # 正向：属性 >= 阈值
                if min_attr >= threshold:
                    matched_threshold = (threshold, interval, change)
                    break
            else:
                # 负向：属性 < 阈值（注意：这里的threshold是上一档的值）
                if min_attr < threshold:
                    matched_threshold = (threshold, interval, change)
                    break

        if matched_threshold is None:
            return 0

        threshold, interval, change = matched_threshold
        elapsed = now - self.last_exp_check_time

        if elapsed >= interval:
            cycles = int(elapsed / interval)
            self.last_exp_check_time += cycles * interval
            total_change = change * cycles
            self.exp = self.clamp_exp(self.exp + total_change)
            return total_change

        return 0

    # ================================================================
    # 喵币自动获取
    # ================================================================
    def check_coin_earn(self, now: float) -> int:
        """检查喵币自动获取，返回获取数量"""
        if self.last_coin_time <= 0:
            self.last_coin_time = now
            return 0

        elapsed = now - self.last_coin_time

        if elapsed >= COIN_AUTO_INTERVAL:
            cycles = int(elapsed / COIN_AUTO_INTERVAL)
            self.last_coin_time += cycles * COIN_AUTO_INTERVAL
            return COIN_AUTO_AMOUNT * cycles

        return 0

    def calc_offline_coins(self, offline_seconds: float) -> int:
        """计算离线期间应得的喵币（有上限）"""
        if offline_seconds <= 0:
            return 0
        cycles = int(offline_seconds / COIN_AUTO_INTERVAL)
        earned = cycles * COIN_AUTO_AMOUNT
        return min(earned, COIN_MAX_OFFLINE_EARN)

    # ================================================================
    # 物品效果
    # ================================================================
    def apply_item_boost(self, item_type: str, boost_value: int, protection_duration: float = 0):
        """应用物品立即提升效果"""
        if item_type == "food":
            self.satiety = self.clamp(self.satiety + boost_value)
            if protection_duration > 0:
                self.satiety_protection += protection_duration
        elif item_type == "drink":
            self.thirst = self.clamp(self.thirst + boost_value)
            if protection_duration > 0:
                self.thirst_protection += protection_duration
        elif item_type == "toy":
            self.mood = self.clamp(self.mood + boost_value)
            if protection_duration > 0:
                self.mood_protection += protection_duration

        # 记录活跃效果
        if protection_duration > 0:
            self.active_effects.append({
                "item_type": item_type,
                "remaining": protection_duration,
            })

    def equip_decoration(self, slot: str, item_id: str, duration: float = 0):
        """装备装饰品（duration=0表示永久）"""
        expire_time = 0 if duration == 0 else time.time() + duration
        self.equipped_decorations[slot] = {
            "item_id": item_id,
            "expire_time": expire_time,
        }

    def unequip_decoration(self, slot: str):
        """卸下装饰品"""
        self.equipped_decorations.pop(slot, None)

    def check_decoration_expiry(self, now: float) -> list:
        """检查装饰品是否过期，返回过期的slot列表"""
        expired = []
        for slot, info in list(self.equipped_decorations.items()):
            expire_time = info.get("expire_time", 0)
            if expire_time > 0 and now >= expire_time:
                expired.append(slot)
                del self.equipped_decorations[slot]
        return expired

    # ================================================================
    # 序列化
    # ================================================================
    def to_dict(self) -> dict:
        return {
            "satiety": self.satiety,
            "thirst": self.thirst,
            "mood": self.mood,
            "exp": self.exp,
            "last_decay_time": self.last_decay_time,
            "last_coin_time": self.last_coin_time,
            "last_exp_check_time": self.last_exp_check_time,
            "last_login_time": self.last_login_time,
            "satiety_protection": self.satiety_protection,
            "thirst_protection": self.thirst_protection,
            "mood_protection": self.mood_protection,
            "equipped_decorations": dict(self.equipped_decorations),
            "active_effects": list(self.active_effects),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PetStats":
        stats = cls()
        stats.satiety = data.get("satiety", PET_INIT_SATIETY)
        stats.thirst = data.get("thirst", PET_INIT_THIRST)
        stats.mood = data.get("mood", PET_INIT_MOOD)
        stats.exp = data.get("exp", PET_INIT_EXP)
        stats.last_decay_time = data.get("last_decay_time", 0)
        stats.last_coin_time = data.get("last_coin_time", 0)
        stats.last_exp_check_time = data.get("last_exp_check_time", 0)
        stats.last_login_time = data.get("last_login_time", 0)
        stats.satiety_protection = data.get("satiety_protection", 0)
        stats.thirst_protection = data.get("thirst_protection", 0)
        stats.mood_protection = data.get("mood_protection", 0)
        stats.equipped_decorations = data.get("equipped_decorations", {})
        stats.active_effects = data.get("active_effects", [])
        return stats