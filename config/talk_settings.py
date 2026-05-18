# -*- coding: utf-8 -*-
"""
宠物对话配置文件

功能说明：
1. 点击对话 - 用户左键点击桌宠时随机显示
2. 自动对话 - 每隔一段时间自动显示  
3. 自定义对话 - 用户在设置中添加的对话（可选）
4. 缓存机制 - 对话数据缓存到内存，支持动态更新
5. 称呼替换 - 支持从设置中读取称呼并替换到对话中
"""

import random


# ============================================================
# 默认对话列表（基础配置）
# ============================================================
DEFAULT_CLICK_TALKS = [
    "喵~ {user_title}你终于理我啦！",
    "呼噜呼噜~ 好舒服！",
    "喵呜~ 要抱抱！",
    "{user_title}{user_title}，陪我玩嘛~",
    "喵~ 今天心情超好！",
    "*蹭蹭* 喜欢{user_title}！",
    "喵？有什么好事吗？",
    "呼~ {user_title}的手好暖和",
    "喵喵喵！我在呢！",
    "{user_title}最棒了！",
    "*摇尾巴* 开心！",
    "喵~ 继续点我呀~",
    "嘿嘿，被摸到啦",
    "{user_title}今天也好可爱！",
    "喵呜~ 再点一下下嘛~",
]

DEFAULT_AUTO_TALKS = [
    "喵... 有点无聊呢...",
    "{user_title}，你在忙什么呀？",
    "呼噜... 好困...",
    "喵~ 窗外的鸟儿在唱歌",
    "{user_title}，记得休息哦~",
    "*打哈欠* 困了困了...",
    "喵呜... 想吃小鱼干...",
    "今天的阳光真好呢~",
    "{user_title}，我想你了...",
    "喵~ 发呆中...",
    "*伸懒腰* 舒服~",
    "嗯... 做梦梦见小鱼干了...",
    "喵？听到声音了！",
    "呼噜呼噜... 睡着了zzZ",
    "{user_title}，加油工作！",
]


# ============================================================
# 对话系统配置
# ============================================================

AUTO_TALK_INTERVAL = 600  # 自动对话间隔（秒）

TALK_DISPLAY_DURATION = 3  # 对话显示时长（秒）

TALK_OFFSET_Y = -10  # 对话偏移量（像素）

ALLOW_TALK_ENABLED = True  # 是否启用对话系统

DEFAULT_USER_TITLE = "主人"  # 默认称呼


# ============================================================
# 对话缓存管理器
# ============================================================

class TalkCacheManager:
    """
    对话缓存管理器
    
    功能：
    - 管理点击对话和自动对话的缓存
    - 支持动态刷新（当设置改变时）
    - 自动处理自定义对话和称呼替换
    """
    
    def __init__(self):
        self._click_talks_cache = None
        self._auto_talks_cache = None
        self._last_settings_hash = None
    
    def _get_settings_hash(self):
        """生成当前设置的哈希值，用于检测变化"""
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            data = storage.load_encrypted_data()
            
            custom_dialogs = data.get('custom_dialogs', []) if data else []
            use_custom_only = data.get('use_custom_only', False) if data else False
            settings = data.get('settings', {}) if data else {}
            user_title = settings.get('user_title', DEFAULT_USER_TITLE)
            
            return (tuple(custom_dialogs), use_custom_only, user_title)
        except Exception:
            return ((), False, DEFAULT_USER_TITLE)
    
    def _replace_user_title(self, text: str, user_title: str) -> str:
        """替换对话中的称呼占位符"""
        if not text:
            return text
        
        title = user_title if user_title else DEFAULT_USER_TITLE
        return text.replace("{user_title}", title)
    
    def _build_click_talks(self) -> list:
        """构建点击对话缓存"""
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            data = storage.load_encrypted_data()
            
            if not data:
                data = {}
            
            settings = data.get('settings', {})
            user_title = settings.get('user_title', DEFAULT_USER_TITLE)
            use_custom_only = data.get('use_custom_only', False)
            custom_dialogs = data.get('custom_dialogs', [])
            
            if not isinstance(custom_dialogs, list):
                custom_dialogs = []
            
            if use_custom_only and len(custom_dialogs) > 0:
                talks = [self._replace_user_title(dialog, user_title) for dialog in custom_dialogs]
            else:
                base_talks = [self._replace_user_title(talk, user_title) for talk in DEFAULT_CLICK_TALKS]
                
                if len(custom_dialogs) > 0:
                    custom_talks = [self._replace_user_title(dialog, user_title) for dialog in custom_dialogs]
                    talks = base_talks + custom_talks
                else:
                    talks = base_talks
            
            print(f"[TalkCache] 构建点击对话缓存: {len(talks)}条 (自定义: {len(custom_dialogs)}, 仅自定义: {use_custom_only})")
            return talks
            
        except Exception as e:
            print(f"[ERROR] 构建点击对话失败: {e}")
            return [self._replace_user_title(talk, DEFAULT_USER_TITLE) for talk in DEFAULT_CLICK_TALKS]
    
    def _build_auto_talks(self) -> list:
        """构建自动对话缓存"""
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            data = storage.load_encrypted_data()
            
            if not data:
                data = {}
            
            settings = data.get('settings', {})
            user_title = settings.get('user_title', DEFAULT_USER_TITLE)
            use_custom_only = data.get('use_custom_only', False)
            custom_dialogs = data.get('custom_dialogs', [])
            
            if not isinstance(custom_dialogs, list):
                custom_dialogs = []
            
            if use_custom_only and len(custom_dialogs) > 0:
                talks = [self._replace_user_title(dialog, user_title) for dialog in custom_dialogs]
            else:
                base_talks = [self._replace_user_title(talk, user_title) for talk in DEFAULT_AUTO_TALKS]
                
                if len(custom_dialogs) > 0:
                    custom_talks = [self._replace_user_title(dialog, user_title) for dialog in custom_dialogs]
                    talks = base_talks + custom_talks
                else:
                    talks = base_talks
            
            print(f"[TalkCache] 构建自动对话缓存: {len(talks)}条 (自定义: {len(custom_dialogs)}, 仅自定义: {use_custom_only})")
            return talks
            
        except Exception as e:
            print(f"[ERROR] 构建自动对话失败: {e}")
            return [self._replace_user_title(talk, DEFAULT_USER_TITLE) for talk in DEFAULT_AUTO_TALKS]
    
    def _need_refresh(self) -> bool:
        """检查是否需要刷新缓存"""
        current_hash = self._get_settings_hash()
        need_update = (current_hash != self._last_settings_hash)
        
        if need_update:
            print(f"[TalkCache] 检测到设置变化，需要刷新缓存")
            self._last_settings_hash = current_hash
        
        return need_update
    
    def get_click_talks(self) -> list:
        """获取点击对话列表（带缓存）"""
        if self._click_talks_cache is None or self._need_refresh():
            self._click_talks_cache = self._build_click_talks()
        
        return self._click_talks_cache
    
    def get_auto_talks(self) -> list:
        """获取自动对话列表（带缓存）"""
        if self._auto_talks_cache is None or self._need_refresh():
            self._auto_talks_cache = self._build_auto_talks()
        
        return self._auto_talks_cache
    
    def clear_cache(self):
        """清除缓存（强制下次重新加载）"""
        print("[TalkCache] 清除对话缓存")
        self._click_talks_cache = None
        self._auto_talks_cache = None
        self._last_settings_hash = None
    
    def force_refresh(self):
        """强制刷新缓存"""
        self.clear_cache()
        self.get_click_talks()
        self.get_auto_talks()


# 全局缓存管理器实例
_talk_cache_manager = TalkCacheManager()


# ============================================================
# 公共接口函数（保持向后兼容）
# ============================================================

def _get_custom_dialogs():
    """获取用户自定义对话（兼容旧接口）"""
    try:
        from basic_model.secure_storage import SecureStorage
        storage = SecureStorage()
        data = storage.load_encrypted_data()
        if data and 'custom_dialogs' in data:
            custom = data['custom_dialogs']
            if isinstance(custom, list) and len(custom) > 0:
                return custom
    except Exception as e:
        print(f"[WARN] 加载自定义对话失败: {e}")
    return None


def _get_use_custom_only():
    """获取是否只使用自定义对话（兼容旧接口）"""
    try:
        from basic_model.secure_storage import SecureStorage
        storage = SecureStorage()
        data = storage.load_encrypted_data()
        if data and 'use_custom_only' in data:
            return bool(data['use_custom_only'])
    except Exception:
        pass
    return False


def get_random_click_talk() -> str:
    """
    获取随机点击对话（使用缓存机制）
    
    优先级：
    1. 如果"只使用自定义对话"开启且有自定义内容 → 只返回自定义对话
    2. 否则 → 返回默认对话 + 自定义对话的合并列表
    3. 如果没有自定义对话 → 只返回默认对话
    """
    talks = _talk_cache_manager.get_click_talks()
    
    if not talks:
        talks = ["喵~"]
    
    selected = random.choice(talks)
    print(f"[TALK] 点击对话: {selected}")
    return selected


def get_random_auto_talk() -> str:
    """
    获取随机自动对话（使用缓存机制）
    
    优先级同 get_random_click_talk
    """
    talks = _talk_cache_manager.get_auto_talks()
    
    if not talks:
        talks = ["喵..."]
    
    selected = random.choice(talks)
    print(f"[TALK] 自动对话: {selected}")
    return selected


def refresh_talk_cache():
    """刷新对话缓存（供外部调用）"""
    _talk_cache_manager.force_refresh()


def clear_talk_cache():
    """清除对话缓存（供外部调用）"""
    _talk_cache_manager.clear_cache()
