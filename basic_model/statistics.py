# -*- coding: utf-8 -*-
"""
数据统计模块

功能：
- 游戏数据统计（华容道/数独）
- 玩家行为统计
- 成就系统
- 数据持久化（JSON存储）
- 数据可视化
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from basic_model.secure_storage import SecureStorage
from pet.pet_stats import PetStats
from common.common_enum import AchievementType

# 导入 PyQt5 用于消息框
try:
    from PyQt5.QtWidgets import QMessageBox
except ImportError:
    QMessageBox = None


@dataclass
class Achievement:
    """成就数据类"""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    icon: str  # emoji或图标路径
    target_value: int = 1  # 达成目标值
    reward_item: Optional[str] = None  # 奖励道具ID
    reward_quantity: int = 1
    unlocked: bool = False
    unlock_time: Optional[str] = None
    current_progress: int = 0
    
    def get_progress_percent(self) -> float:
        """获取进度百分比"""
        if self.target_value == 0:
            return 100.0
        return min(100.0, (self.current_progress / self.target_value) * 100)
    
    def check_unlocked(self) -> bool:
        """检查是否达成"""
        return self.current_progress >= self.target_value
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        # 枚举转换为字符串
        if 'achievement_type' in data and data['achievement_type']:
            data['achievement_type'] = data['achievement_type'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Achievement':
        """从字典创建"""
        # 字符串转换回枚举
        if 'achievement_type' in data and data['achievement_type']:
            data['achievement_type'] = AchievementType(data['achievement_type'])
        return cls(**data)


@dataclass
class GameStats:
    """单个游戏的统计数据"""
    game_id: str
    game_name: str
    total_games: int = 0        # 总游戏次数
    wins: int = 0               # 胜利次数
    losses: int = 0             # 失败次数
    best_score: int = 0         # 最佳分数
    best_time: int = 0          # 最快时间（秒）
    total_play_time: int = 0    # 总游玩时间（秒）
    perfect_games: int = 0      # 完美游戏数
    current_streak: int = 0     # 当前连胜
    best_streak: int = 0        # 最佳连胜
    average_moves: float = 0.0  # 平均步数/操作数
    
    @property
    def win_rate(self) -> float:
        """胜率"""
        if self.total_games == 0:
            return 0.0
        return (self.wins / self.total_games) * 100
    
    def record_game(self, won: bool, score: int = 0, time_spent: int = 0, 
                    moves: int = 0, is_perfect: bool = False):
        """记录一局游戏"""
        self.total_games += 1
        self.total_play_time += time_spent
        
        if won:
            self.wins += 1
            self.current_streak += 1
            
            if score > self.best_score:
                self.best_score = score
            
            if time_spent > 0 and (self.best_time == 0 or time_spent < self.best_time):
                self.best_time = time_spent
            
            if is_perfect:
                self.perfect_games += 1
            
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
            
            # 更新平均步数
            total_moves = self.average_moves * (self.wins - 1) + moves
            self.average_moves = total_moves / self.wins
        else:
            self.losses += 1
            self.current_streak = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameStats':
        """从字典创建"""
        return cls(**data)


@dataclass
class PlayerStats:
    """玩家统计数据"""
    total_session_time: int = 0          # 总在线时间（秒）
    sessions_count: int = 0              # 启动次数
    pet_interactions: int = 0            # 桌宠互动次数
    menu_opens: int = 0                  # 打开菜单次数
    items_used: int = 0                  # 使用道具次数
    items_collected: int = 0             # 收集道具数量
    unique_items: int = 0                # 唯一道具种类
    gold_earned: int = 0                 # 获得金币
    gold_spent: int = 0                  # 消费金币
    achievements_unlocked: int = 0       # 解锁成就数
    first_login_date: Optional[str] = None  # 首次登录日期
    last_login_date: Optional[str] = None   # 最后登录日期
    
    def record_session_start(self):
        """记录会话开始"""
        self.sessions_count += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not self.first_login_date:
            self.first_login_date = now
        
        self.last_login_date = now
    
    def add_play_time(self, seconds: int):
        """增加游戏时间"""
        self.total_session_time += seconds
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerStats':
        """从字典创建"""
        return cls(**data)


class StatisticsManager:
    """统计数据管理器（包含背包和分数）"""
    
    SAVE_FILE = "player_data.dat"
    
    def __init__(self):
        self.game_stats: Dict[str, GameStats] = {}
        self.player_stats = PlayerStats()
        self.achievements: Dict[str, Achievement] = {}
        self.storage = SecureStorage(app_name="MilkPet", data_file=self.SAVE_FILE)
        
        # 背包和分数数据
        self.inventory_data: Dict[str, int] = {}
        self.player_score: int = 0
        
        # 宠物属性
        self.pet_stats = PetStats()
        
        self._initialize_default_stats()
        self._initialize_achievements()
        self.load_data()
    
    def _initialize_default_stats(self):
        """初始化默认游戏统计"""
        self.game_stats['dh_puzzle'] = GameStats(
            game_id='dh_puzzle',
            game_name='数字华容道'
        )
        
        self.game_stats['sudoku'] = GameStats(
            game_id='sudoku',
            game_name='数独'
        )
    
    def _initialize_achievements(self):
        """初始化所有成就"""
        achievements_list = [
            # 华容道成就
            Achievement(
                id="hr_first_win",
                name="🎮 初次胜利",
                description="完成第一局数字华容道",
                achievement_type=AchievementType.GAME_WINS,
                icon="🎮",
                target_value=1,
                reward_item="dried_fish",
                reward_quantity=3
            ),
            Achievement(
                id="hr_win_10",
                name="🏆 熟练玩家",
                description="完成10局数字华容道",
                achievement_type=AchievementType.GAME_WINS,
                icon="🏆",
                target_value=10,
                reward_item="pudding_cake",
                reward_quantity=2
            ),
            Achievement(
                id="hr_perfect",
                name="⭐ 完美通关",
                description="在50步内完成华容道",
                achievement_type=AchievementType.PERFECT_GAME,
                icon="⭐",
                target_value=1,
                reward_item="salmon_can"
            ),

            # 数独成就
            Achievement(
                id="sdk_first_win",
                name="🔢 数独新手",
                description="完成第一局数独",
                achievement_type=AchievementType.GAME_WINS,
                icon="🔢",
                target_value=1,
                reward_item="chicken_soup",
                reward_quantity=3
            ),
            Achievement(
                id="sdk_win_10",
                name="🧠 数独大师",
                description="完成10局数独",
                achievement_type=AchievementType.GAME_WINS,
                icon="🧠",
                target_value=10,
                reward_item="fresh_milk",
                reward_quantity=2
            ),
            Achievement(
                id="sdk_speed",
                name="⚡ 闪电速解",
                description="在3分钟内完成数独",
                achievement_type=AchievementType.SPEED_CLEAR,
                icon="⚡",
                target_value=1,
                reward_item="cat_teaser",
                reward_quantity=5
            ),

            # 玩家成就
            Achievement(
                id="play_1h",
                name="⏰ 坚持不懈",
                description="累计游戏1小时",
                achievement_type=AchievementType.PLAY_TIME,
                icon="⏰",
                target_value=3600,  # 1小时 = 3600秒
                reward_item="toy_mouse"
            ),
            Achievement(
                id="items_20",
                name="🎒 收藏家",
                description="收集20个不同道具",
                achievement_type=AchievementType.ITEMS_COLLECTED,
                icon="🎒",
                target_value=20,
                reward_item="laser_pen"
            ),
            Achievement(
                id="interact_100",
                name="❤️ 好朋友",
                description="与桌宠互动100次",
                achievement_type=AchievementType.SOCIAL,
                icon="❤️",
                target_value=100,
                reward_item="revive_coin"
            ),
            Achievement(
                id="achievements_5",
                name="🌟 成就猎人",
                description="解锁5个成就",
                achievement_type=AchievementType.EXPLORER,
                icon="🌟",
                target_value=5,
                reward_item="tuna_soup"
            ),
        ]
        
        for ach in achievements_list:
            self.achievements[ach.id] = ach
    
    def record_game_result(self, game_id: str, won: bool, **kwargs):
        """记录游戏结果"""
        if game_id not in self.game_stats:
            self.game_stats[game_id] = GameStats(
                game_id=game_id,
                game_name=game_id
            )
        
        stats = self.game_stats[game_id]
        stats.record_game(won, **kwargs)
        
        # 检查相关成就
        self._check_game_achievements(game_id, won, **kwargs)
        
        # 自动保存
        self.save_data()
    
    def _check_game_achievements(self, game_id: str, won: bool, **kwargs):
        """检查游戏相关成就"""
        stats = self.game_stats[game_id]
        
        if game_id == 'dh_puzzle' and won:
            # 首次胜利
            self._update_achievement("hr_first_win", stats.wins)
            
            # 10次胜利
            self._update_achievement("hr_win_10", stats.wins)
            
            # 完美通关（50步以内）
            moves = kwargs.get('moves', 0)
            if moves > 0 and moves <= 50:
                self._update_achievement("hr_perfect", 1)
        
        elif game_id == 'sudoku' and won:
            # 首次胜利
            self._update_achievement("sdk_first_win", stats.wins)
            
            # 10次胜利
            self._update_achievement("sdk_win_10", stats.wins)
            
            # 速通（3分钟内）
            time_spent = kwargs.get('time_spent', 0)
            if time_spent > 0 and time_spent <= 180:
                self._update_achievement("sdk_speed", 1)
    
    def _update_achievement(self, achievement_id: str, progress_increment: int = 1):
        """更新成就进度"""
        if achievement_id not in self.achievements:
            return
        
        ach = self.achievements[achievement_id]
        
        if ach.unlocked:
            return
        
        ach.current_progress += progress_increment
        
        if ach.check_unlocked():
            ach.unlocked = True
            ach.unlock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.player_stats.achievements_unlocked += 1
            
            print(f"🎉 解锁成就: {ach.name}!")
            
            # 返回奖励信息
            if ach.reward_item:
                return {
                    'item': ach.reward_item,
                    'quantity': ach.reward_quantity,
                    'message': f'获得奖励: {ach.reward_item} x{ach.reward_quantity}'
                }
        
        return None
    
    def record_interaction(self, interaction_type: str = "pet"):
        """记录互动"""
        if interaction_type == "pet":
            self.player_stats.pet_interactions += 1
            
            # 检查互动成就
            reward = self._update_achievement("interact_100", 1)
            if reward:
                return reward
        
        elif interaction_type == "menu":
            self.player_stats.menu_opens += 1
        
        return None
    
    def record_item_action(self, action: str, item_id: str = None, quantity: int = 1):
        """记录道具行为"""
        if action == "use":
            self.player_stats.items_used += quantity
        elif action == "collect":
            self.player_stats.items_collected += quantity
            # 更新唯一道具统计（需要外部传入当前总数）
        
        # 检查收集成就
        reward = self._update_achievement("items_20", quantity)
        if reward:
            return reward
        
        return None
    
    def update_play_time(self, seconds: int):
        """更新游戏时间"""
        self.player_stats.add_play_time(seconds)
        
        # 检查时间成就
        reward = self._update_achievement("play_1h", seconds)
        if reward:
            return reward
        
        # 检查成就猎人成就（基于已解锁成就数量）
        unlocked_count = sum(1 for a in self.achievements.values() if a.unlocked)
        self._update_achievement("achievements_5", unlocked_count)
        
        return None
    
    def get_game_summary(self, game_id: str) -> Optional[Dict]:
        """获取游戏摘要"""
        if game_id not in self.game_stats:
            return None
        
        stats = self.game_stats[game_id]
        
        return {
            'game_name': stats.game_name,
            'total_games': stats.total_games,
            'wins': stats.wins,
            'losses': stats.losses,
            'win_rate': f"{stats.win_rate:.1f}%",
            'best_score': stats.best_score,
            'best_time': f"{stats.best_time // 60}:{stats.best_time % 60:02d}" if stats.best_time else "--:--",
            'perfect_games': stats.perfect_games,
            'current_streak': stats.current_streak,
            'best_streak': stats.best_streak,
            'average_moves': f"{stats.average_moves:.1f}",
            'total_play_time': f"{stats.total_play_time // 3600}h{(stats.total_play_time % 3600) // 60}m"
        }
    
    def get_player_summary(self) -> Dict:
        """获取玩家摘要"""
        total_hours = self.player_stats.total_session_time // 3600
        total_mins = (self.player_stats.total_session_time % 3600) // 60
        
        unlocked_achievements = sum(1 for a in self.achievements.values() if a.unlocked)
        total_achievements = len(self.achievements)
        
        return {
            'sessions': self.player_stats.sessions_count,
            'total_play_time': f"{total_hours}小时{total_mins}分钟",
            'interactions': self.player_stats.pet_interactions,
            'menu_opens': self.player_stats.menu_opens,
            'items_used': self.player_stats.items_used,
            'items_collected': self.player_stats.items_collected,
            'gold_earned': self.player_stats.gold_earned,
            'gold_spent': self.player_stats.gold_spent,
            'achievements': f"{unlocked_achievements}/{total_achievements}",
            'first_login': self.player_stats.first_login_date or "未知",
            'last_login': self.player_stats.last_login_date or "未知"
        }
    
    def save_data(self):
        """保存数据到文件（加密）"""
        try:
            data = {
                'version': '1.0',
                'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'game_stats': {k: v.to_dict() for k, v in self.game_stats.items()},
                'player_stats': self.player_stats.to_dict(),
                'achievements': {k: v.to_dict() for k, v in self.achievements.items()},
                'inventory': dict(self.inventory_data),
                'player_score': self.player_score,
                'pet_stats': self.pet_stats.to_dict(),
            }
            
            self.storage.save_encrypted_data(data)
            
        except Exception as e:
            print(f"[ERROR] 保存数据失败: {e}")
    
    def load_data(self):
        """从文件加载数据（解密）"""
        try:
            data = self.storage.load_encrypted_data()
            
            if data is None:
                print("[INFO] 使用默认数据")
                return
            
            # 加载游戏统计
            if 'game_stats' in data:
                for game_id, stats_data in data['game_stats'].items():
                    self.game_stats[game_id] = GameStats.from_dict(stats_data)
            
            # 加载玩家统计
            if 'player_stats' in data:
                self.player_stats = PlayerStats.from_dict(data['player_stats'])
            
            # 加载成就
            if 'achievements' in data:
                for ach_id, ach_data in data['achievements'].items():
                    if ach_id in self.achievements:
                        self.achievements[ach_id] = Achievement.from_dict(ach_data)
            
            # 加载背包数据
            if 'inventory' in data:
                self.inventory_data = data['inventory']
                print(f"[OK] 背包数据已加载: {len(self.inventory_data)} 种道具")
            
            # 加载分数数据
            if 'player_score' in data:
                self.player_score = data['player_score']
                print(f"[OK] 分数已加载: {self.player_score} 分")
            
            # 加载宠物属性
            if 'pet_stats' in data:
                self.pet_stats = PetStats.from_dict(data['pet_stats'])
                print(f"[OK] 宠物属性已加载")
            
        except Exception as e:
            print(f"[ERROR] 加载数据失败: {e}")
    
    def get_inventory_data(self) -> Dict[str, int]:
        """获取背包数据"""
        return dict(self.inventory_data)
    
    def set_inventory_data(self, data: Dict[str, int]):
        """设置背包数据"""
        self.inventory_data = dict(data)
        self.save_data()
    
    def get_player_score(self) -> int:
        """获取玩家分数"""
        return self.player_score
    
    def set_player_score(self, score: int):
        """设置玩家分数"""
        self.player_score = score
        self.save_data()
    
    def add_player_score(self, amount: int) -> int:
        """增加玩家分数"""
        self.player_score += amount
        self.save_data()
        return self.player_score
    
    def process_login_pet_stats(self) -> dict:
        """登录时处理宠物属性（离线衰减、离线喵币、装饰过期检查）"""
        import time
        now = time.time()
        result = {"offline_coins": 0, "expired_decorations": []}
        
        decay_changes = self.pet_stats.apply_decay(now)
        if any(v != 0 for v in decay_changes.values()):
            print(f"[INFO] 离线属性衰减: 饱食度{decay_changes['satiety']:+.1f}, 饥渴值{decay_changes['thirst']:+.1f}, 心情{decay_changes['mood']:+.1f}")
        
        if self.pet_stats.last_login_time > 0:
            offline_seconds = now - self.pet_stats.last_login_time
            result["offline_coins"] = self.pet_stats.calc_offline_coins(offline_seconds)
            if result["offline_coins"] > 0:
                self.player_score += result["offline_coins"]
                print(f"[INFO] 离线喵币: +{result['offline_coins']}")
        
        self.pet_stats.last_login_time = now
        
        result["expired_decorations"] = self.pet_stats.check_decoration_expiry(now)
        if result["expired_decorations"]:
            print(f"[INFO] 过期装饰品: {result['expired_decorations']}")
        
        if self.pet_stats.last_coin_time <= 0:
            self.pet_stats.last_coin_time = now
        if self.pet_stats.last_exp_check_time <= 0:
            self.pet_stats.last_exp_check_time = now
        
        self.save_data()
        return result
    
    def reset_all_data(self):
        """重置所有数据"""
        reply = QMessageBox.question(
            None,
            "确认重置",
            "确定要重置所有统计数据吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.game_stats.clear()
            self.player_stats = PlayerStats()
            
            for ach in self.achievements.values():
                ach.unlocked = False
                ach.unlock_time = None
                ach.current_progress = 0
            
            self._initialize_default_stats()
            self.save_data()
            
            print("[INFO] 所有数据已重置")
            return True
        
        return False
