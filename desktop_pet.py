# -*- coding: utf-8 -*-
"""
桌宠主控制器 - 协调所有功能模块

模块说明：
- games/pet_display.py: 桌宠显示核心（窗口、图片、UI）
- games/pet_tray.py: 系统托盘管理（图标、菜单、通知）
- games/huarongdao.py: 数字华容道游戏
- games/sudoku.py: 数独游戏
- games/inventory.py: 背包系统
- games/shop.py: 商店系统
"""

import sys
import os

from PyQt5.QtWidgets import (QWidget, QLabel, QMenu, QAction,
                             QVBoxLayout, QHBoxLayout, QPushButton, 
                             QMessageBox, QApplication, 
                             QScrollArea, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QPoint, QTimer

from games.pet_display import PetDisplay
from games.pet_tray import PetTrayManager
from games.huarongdao import HuaRongDao
from games.sudoku import SudokuGame
from games.inventory import InventoryWindow
from games.shop import ShopWindow
from games.items import ItemFactory, ItemRarity
from games.statistics import StatisticsManager


class DesktopPet(PetDisplay):
    """
    桌面宠物主控制器
    
    继承自 PetDisplay（显示逻辑）
    使用 PetTrayManager（托盘管理）
    
    新增功能：
    - 右键菜单和交互
    - 游戏窗口管理
    - 背包系统集成
    - 数据统计和成就系统
    """
    
    def __init__(self):
        # 先调用父类初始化显示部分
        super().__init__()
        
        self.dragging = False
        self.drag_position = QPoint()
        self.allow_click = True
        self.is_on_top = True
        self.huarong_window = None
        self.sudoku_window = None
        
        # 背包和统计系统
        self.inventory_window: InventoryWindow = None
        self.shop_window: ShopWindow = None
        self.stats_manager = StatisticsManager()
        
        # 玩家分数（从统计管理器获取）
        self.player_score = self.stats_manager.get_player_score()
        
        # 定时器：用于统计在线时间
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._update_session_time)
        self.session_timer.start(60000)
        
        # 初始化玩家会话
        self.stats_manager.player_stats.record_session_start()
        
        # 预加载所有游戏素材
        print("[DesktopPet] 预加载游戏素材...")
        from games.resource_manager import ResourceManager
        self.resource_manager = ResourceManager()
        self.resource_manager.preload_all()
        
        # 初始化托盘管理器
        self.tray_manager = PetTrayManager(self)
        
        # 设置右键菜单
        self._setup_menu()
        
        # 赠送新手礼包
        self._give_starter_pack()
    
    def _setup_menu(self):
        """设置右键菜单"""
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(190)
        self.menu_widget.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.menu_widget.setAttribute(Qt.WA_TranslucentBackground, True)  # 启用透明背景
        self.menu_widget.hide()
        
        # 使用 QFrame 作为背景容器（与其他窗口一致）
        self.menu_container = QFrame(self.menu_widget)
        self.menu_container.setObjectName("menu_container")
        
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(8)
        menu_layout.setContentsMargins(10, 4, 10, 10)
        self.menu_container.setLayout(menu_layout)
        
        main_layout = QVBoxLayout(self.menu_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.menu_container)

        # 布局常量（改为实例属性）
        self._title_container_width = 50  # 标题容器宽度
        self._title_container_height = 32  # 标题容器高度
        self._title_spacing = 0  # 标题容器内部间距
        self._title_font_size = 18  # 标题字号
        self._button_container_width = 100  # 按钮容器宽度
        self._category_top_margin = 4  # 分类容器上边界间距
        self._category_left_margin = 0  # 分类容器左边界间距

        # 获取背景图路径
        bg_path = self._get_bg_path()
        
        menu_style = """
            QPushButton {{
                background-color: #fad8d1;
                color: #8a8070;
                border: 1px solid #FFB6C1;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #FFE4E9;
                border-color: #FFC0CB;
            }}
            QPushButton:pressed {{
                background-color: #FFC0CB;
                border-color: #FFB6C1;
            }}
            QFrame#menu_container {{
                background-image: url("{2}");
                background-color: rgba(43, 43, 54, 0.95);
                border-radius: 15px;
                border: 2px solid rgba(106, 106, 126, 0.9);
            }}
            QLabel#category_label {{
                color: #8a8070;
                font-size: {0}px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                min-height: {1}px;
                background: transparent;
            }}
            QWidget#category_container {{
                background: transparent;
            }}
        """.format(self._title_font_size, self._title_container_height, bg_path)
        self.menu_widget.setStyleSheet(menu_style)
        self.menu_widget.setObjectName("menu_container")
        
        # ========== 分类数据 ==========
        # 按钮项格式: {"name": "按钮名称", "callback": 触发方法, "special_style": 特殊样式(可选), "ref": 按钮引用名(可选)}
        
        categories = [
            {
                "label": "娱乐",
                "items": [
                    {"name": "数字华容道", "callback": self._on_huarong},
                    {"name": "数独", "callback": self._on_sudoku},
                ]
            },
            {
                "label": "功能",
                "items": [
                    {"name": "背包", "callback": self._on_backpack},
                    {"name": "商城", "callback": self._on_shop},
                ]
            },
            {
                "label": "系统",
                "items": [
                    {"name": "取消置顶" if self.is_on_top else "置顶", "callback": self._toggle_top, "ref": "top_btn"},
                    {"name": "禁止点击交互" if self.allow_click else "允许点击交互", "callback": self._on_click_toggle, "ref": "click_btn"},
                    {"name": "退出", "callback": self._on_quit, "special_style": "warning"},
                ]
            },
        ]
        
        # ========== 渲染分类 ==========
        for i, category in enumerate(categories):
            category_widget = self._create_category(category["label"], category["items"])
            menu_layout.addWidget(category_widget)
            
            # 添加分隔线（最后一个分类不加）
            if i < len(categories) - 1:
                line = self._create_divider()
                menu_layout.addWidget(line)
        
        # 设置菜单最小宽度，避免右侧出现深色背景
        self.menu_widget.adjustSize()
        self.menu_widget.setMinimumWidth(self.menu_widget.sizeHint().width())
    
    def _create_category(self, label, items):
        """创建分类组件"""
        # 分类容器（标题容器 + 按钮容器，左右排列）
        category = QWidget()
        category.setObjectName("category_container")
        # 设置动态高度：内容决定高度，不扩展
        category.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        category_layout = QHBoxLayout(category)
        category_layout.setSpacing(3)
        category_layout.setContentsMargins(self._category_left_margin, self._category_top_margin, 10, 0)
        
        # 标题容器（左侧）- 设置固定高度等于按钮高度，避免空白
        title_container = QWidget()
        title_container.setFixedWidth(self._title_container_width)
        title_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(self._title_spacing)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("category_label")
        # 设置标题高度等于按钮高度，保持一致
        label_widget.setFixedHeight(32)
        label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(label_widget)
        
        category_layout.addWidget(title_container, alignment=Qt.AlignTop)
        
        # 按钮容器（右侧，垂直排列）
        btn_container = QWidget()
        btn_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(4)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # 渲染按钮
        for item in items:
            # 创建按钮
            btn = QPushButton(item["name"])
            btn.setFixedWidth(self._button_container_width)
            btn.setFixedHeight(32)
            btn.clicked.connect(item["callback"])
            
            # 特殊样式
            if item.get("special_style") == "warning":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d4a5a5;
                        color: #8a4a4a;
                        border: none;
                        padding: 8px 10px;
                        font-weight: bold;
                        font-size: 13px;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: #e4b5b5;
                    }
                """)
            
            # 保存按钮引用（用于更新文字）
            ref = item.get("ref")
            if ref:
                setattr(self, ref, btn)
            
            # 添加到布局
            btn_layout.addWidget(btn)
        
        category_layout.addWidget(btn_container, alignment=Qt.AlignTop)
        
        return category
    
    def _create_divider(self):
        """创建粉色分隔线"""
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #FFB6C1; border-radius: 1px;")
        return line
    
    def _give_starter_pack(self):
        """赠送新手礼包"""
        starter_items = [
            ("fish", 5),
            ("milk", 3),
            ("hint_scroll", 3),
            ("bow_tie", 1),
        ]
        
        for item_id, quantity in starter_items:
            item = ItemFactory.get_item(item_id)
            if item:
                print(f"[GIFT] 新手礼包: {item.name} x{quantity}")
                # 这里只是打印，实际添加在背包打开时处理

    def _update_session_time(self):
        """更新会话时间（每分钟调用）"""
        self.stats_manager.update_play_time(60)
    
    def _get_bg_path(self):
        """获取背景图路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'assets', 'images', 'background.png').replace('\\', '/')
    
    def _show_menu(self, pos):
        """显示右键菜单 - 固定位置不跟随鼠标"""
        try:
            # 固定菜单位置：桌宠右侧
            pet_x = self.x()
            pet_y = self.y()
            pet_width = self.width()
            pet_height = self.height()

            # 设置菜单高度与桌宠一致
            self.menu_widget.setFixedHeight(pet_height)
            
            # 菜单显示在桌宠右侧，距离更近（5px）
            x = pet_x + pet_width + 5
            y = pet_y

            # 获取屏幕尺寸确保不超出
            screen = QApplication.instance().primaryScreen().availableGeometry()
            menu_width = self.menu_widget.width()
            menu_height = self.menu_widget.height()
            
            # 如果右侧空间不够，显示在左侧
            if x + menu_width > screen.width():
                x = pet_x - menu_width - 5
            
            # 如果底部空间不够，向上调整
            if y + menu_height > screen.height():
                y = screen.height() - menu_height

            if y < 0:
                y = 10

            self.menu_widget.move(x, y)
            self.menu_widget.show()
            self.menu_widget.raise_()

            # 记录菜单打开次数
            self.stats_manager.record_interaction("menu")
        except Exception as e:
            print(f"[ERROR] Error showing menu: {e}")
            import traceback
            traceback.print_exc()
    
    def mousePressEvent(self, event):
        if not self.allow_click:
            event.ignore()
            return
        
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
            if self.menu_widget.isVisible():
                self.menu_widget.hide()
            
            # 记录互动"
            self.stats_manager.record_interaction("pet")
        
        elif event.button() == Qt.RightButton:
            global_pos = event.globalPos()
            local_pos = self.mapFromGlobal(global_pos)
            self._show_menu(local_pos)
            event.accept()
    
    def mouseMoveEvent(self, event):
        if not self.allow_click:
            event.ignore()
            return
        
        if self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            
            screen = QApplication.instance().primaryScreen().geometry()
            max_x = screen.width() - self.width()
            max_y = screen.height() - self.height()
            
            new_pos.setX(max(-self.width(), min(new_pos.x(), max_x)))
            new_pos.setY(max(-self.height(), min(new_pos.y(), max_y)))
            
            self.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def _toggle_top(self):
        """切换置顶状态"""
        self.is_on_top = not self.is_on_top
        
        # 保存当前窗口位置
        pos = self.pos()
        visible = self.isVisible()
        
        if self.is_on_top:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            if hasattr(self, 'top_btn'):
                self.top_btn.setText("取消置顶")
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
            if hasattr(self, 'top_btn'):
                self.top_btn.setText("置顶")
        
        # 恢复窗口位置和可见性
        self.move(pos)
        if visible:
            self.show()
        
        # 更新托盘菜单状态
        if hasattr(self, 'tray_manager'):
            self.tray_manager.update_tray_menu()
        
        self.menu_widget.hide()
    
    def _on_click_toggle(self):
        """切换点击交互"""
        self.allow_click = not self.allow_click
        
        # 使用属性控制鼠标事件穿透（更可靠的方式）
        if self.allow_click:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setWindowOpacity(1.0)  # 恢复完全不透明
            # 更新按钮文字
            if hasattr(self, 'click_btn'):
                self.click_btn.setText("禁止点击交互")
            print("[INFO] 点击交互已启用")
        else:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            # 更新按钮文字
            if hasattr(self, 'click_btn'):
                self.click_btn.setText("允许点击交互")
            print("[INFO] 点击交互已禁用")
        
        # 更新托盘菜单状态
        if hasattr(self, 'tray_manager'):
            self.tray_manager.update_tray_menu()
        
        self.menu_widget.hide()
    
    def _close_all_windows(self):
        """关闭所有已打开的功能窗口"""
        print("[DEBUG] Closing all windows...")
        
        windows_to_close = []
        
        if self.huarong_window:
            windows_to_close.append(('huarong', self.huarong_window))
        if self.sudoku_window:
            windows_to_close.append(('sudoku', self.sudoku_window))
        if self.inventory_window:
            windows_to_close.append(('inventory', self.inventory_window))
        if self.shop_window:
            windows_to_close.append(('shop', self.shop_window))
        
        for name, window in windows_to_close:
            try:
                print(f"[DEBUG] Closing {name} window...")
                
                # 断开所有信号连接
                try:
                    window.blockSignals(True)
                except:
                    pass
                
                # 隐藏窗口
                try:
                    if window.isVisible():
                        window.hide()
                except Exception as hide_err:
                    print(f"[WARN] Error hiding {name}: {hide_err}")
                
                # 关闭窗口
                try:
                    window.close()
                except Exception as close_err:
                    print(f"[WARN] Error closing {name}: {close_err}")
                    
                print(f"[DEBUG] {name} window closed successfully")
                
            except Exception as e:
                print(f"[WARN] Error processing {name} window: {e}")
        
        # 清理引用
        self.huarong_window = None
        self.sudoku_window = None
        self.inventory_window = None
        self.shop_window = None
        
        print("[DEBUG] All windows closed, references cleared")
    
    def _on_huarong(self):
        """打开华容道游戏"""
        print("HuaRong Dao clicked")
        self.menu_widget.hide()

        try:
            self._close_all_windows()
            self.huarong_window = HuaRongDao()

            # 连接游戏结束信号用于统计和得分
            self.huarong_window.game_won.connect(
                lambda score, time_sec: self._on_game_finished('huarongdao', won=True, score=score, time_seconds=time_sec)
            )

            self.huarong_window.show()
            print("[OK] HuaRong window opened (independent)")
        except Exception as e:
            print(f"[ERROR] Error opening HuaRong Dao: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "错误",
                f"无法打开华容道游戏\n\n错误信息: {str(e)}",
                QMessageBox.Ok
            )
    
    def _on_sudoku(self):
        """打开数独游戏"""
        print("Sudoku clicked")
        self.menu_widget.hide()
        
        try:
            self._close_all_windows()
            
            print("[DEBUG] Creating SudokuGame window...")
            self.sudoku_window = SudokuGame()
            
            # 连接游戏结束信号用于统计
            self.sudoku_window.game_won.connect(
                lambda: self._on_game_finished('sudoku', won=True)
            )
            
            self.sudoku_window.show()
            print("[OK] Sudoku window opened (independent)")
        except Exception as e:
            print(f"[ERROR] Error opening Sudoku: {e}")
            import traceback
            traceback.print_exc()
            self.sudoku_window = None
    
    def _on_game_finished(self, game_id: str, won: bool, **kwargs):
        """游戏结束时调用"""
        print(f"📊 Game finished: {game_id}, won={won}")
        
        # 记录游戏结果
        self.stats_manager.record_game_result(game_id, won, **kwargs)
        
        # 奖励道具和分数
        if won:
            score = kwargs.get('score', 0)
            time_seconds = kwargs.get('time_seconds', 0)
            
            # 增加玩家分数
            if score > 0:
                self.player_score = self.stats_manager.add_player_score(score)
                print(f"💰 获得分数: {score} 分, 总分: {self.player_score} 分")
            
                QMessageBox.information(
                    None,
                    "游戏胜利",
                    f"恭喜完成游戏！\n\n获得分数: {score} 分\n当前总分: {self.player_score} 分\n用时: {time_seconds} 秒",
                    QMessageBox.Ok
                )
            
            # 奖励道具
            reward_item = ItemFactory.get_loot_drop()
            if reward_item:
                QMessageBox.information(
                    None,
                    "道具奖励",
                    f"额外获得道具:\n{reward_item.icon} {reward_item.name}",
                    QMessageBox.Ok
                )

                # 如果背包窗口存在，添加道具
                if self.inventory_window:
                    self.inventory_window.add_item(reward_item.id)

    def _on_backpack(self):
        """打开背包"""
        print("Opening inventory")
        self.menu_widget.hide()

        # 创建或显示背包窗口
        if not self.inventory_window or not self.inventory_window.isVisible():
            self._close_all_windows()
            self.inventory_window = InventoryWindow(parent=None)

            # 加载背包数据
            saved_inventory = self.stats_manager.get_inventory_data()
            if saved_inventory:
                self.inventory_window.load_inventory_data(saved_inventory)

            # 连接信号
            self.inventory_window.item_used.connect(self._on_item_used)
            self.inventory_window.closed.connect(self._on_inventory_closed)

            # 添加新手礼包（首次）
            if self.stats_manager.player_stats.sessions_count <= 1:
                starter_items = [
                    ("fish", 5),
                    ("milk", 3),
                    ("hint_scroll", 3),
                    ("bow_tie", 1),
                ]
                for item_id, qty in starter_items:
                    self.inventory_window.add_item(item_id, qty)
            
            self.inventory_window.show()
        else:
            self.inventory_window.raise_()
            self.inventory_window.activateWindow()
    
    def _on_item_used(self, item_id: str):
        "道具被使用时调用"
        item = ItemFactory.get_item(item_id)
        if not item:
            return

        print(f"💊 Used item: {item.name}")
        
        # 应用效果
        effect_messages = []
        for effect in item.effects:
            msg = effect.apply()
            if msg:
                effect_messages.append(msg)
        
        # 显示效果提示
        if effect_messages:
            QMessageBox.information(
                self.inventory_window or self,
                f"使用了 {item.name}",
                "\n".join(effect_messages),
                QMessageBox.Ok
            )
        
        # 记录✅ 使用了"
        self.stats_manager.record_item_action("use", item_id)
    
    def _on_inventory_closed(self):
        """背包关闭时保存数据"""
        if self.inventory_window:
            # 保存背包数据
            inventory_data = self.inventory_window.get_inventory_data()
            self.stats_manager.set_inventory_data(inventory_data)
    
    def _on_shop(self):
        """打开商店"""
        print("Opening shop")
        self.menu_widget.hide()

        try:
            # 创建或显示商店窗口
            if not self.shop_window or not self.shop_window.isVisible():
                self._close_all_windows()
                self.shop_window = ShopWindow(player_score=self.player_score, parent=None)

                # 连接购买信号
                self.shop_window.item_purchased.connect(self._on_item_purchased)
                self.shop_window.closed.connect(self._on_shop_closed)

                self.shop_window.show()
            else:
                self.shop_window.raise_()
                self.shop_window.activateWindow()
        except Exception as e:
            print(f"[ERROR] Error opening shop: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "错误",
                f"无法打开商店\n\n错误信息: {str(e)}",
                QMessageBox.Ok
            )
    
    def _on_item_purchased(self, item_id: str, price: int):
        """物品购买成功"""
        print(f"🛒 购买物品: {item_id}, 价格: {price}")
        
        # 扣除分数（负数表示扣除）
        self.player_score = self.stats_manager.add_player_score(-price)
        
        # 记录消费
        self.stats_manager.player_stats.gold_spent += price
        
        # 添加到背包
        if self.inventory_window:
            self.inventory_window.add_item(item_id, 1)
        
        # 更新商店分数显示
        if self.shop_window:
            self.shop_window.update_score(self.player_score)
    
    def _on_shop_closed(self):
        """商店关闭"""
        print("🛒 Shop closed")
    
    def _on_statistics(self):
        """显示统计数据"""
        print("📊 Showing statistics")
        self.menu_widget.hide()
        
        # 获取统计数据
        player_summary = self.stats_manager.get_player_summary()
        huarong_summary = self.stats_manager.get_game_summary('huarongdao')
        sudoku_summary = self.stats_manager.get_game_summary('sudoku')
        
        # 构建显示文本
        stats_text = f"数据统计报告\n"
        stats_text += f"{'='*40}\n"
        stats_text += f"\n玩家信息\n"
        stats_text += f"   启动次数: {player_summary['sessions']}\n"
        stats_text += f"   总游玩时间: {player_summary['total_play_time']}\n"
        stats_text += f"   桌宠互动: {player_summary['interactions']}\n"
        stats_text += f"   菜单打开: {player_summary['menu_opens']}\n"
        stats_text += f"   使用了道具: {player_summary['items_used']}\n"
        stats_text += f"   收集道具: {player_summary['items_collected']}\n"
        stats_text += f"成就进度: {player_summary['achievements']}\n"
        stats_text += f"\n首次登录: {player_summary['first_login']}\n"
        stats_text += f"最近登录: {player_summary['last_login']}\n"

        stats_text += f"\n{'='*40}"
        stats_text += f"\n数字华容道统计\n"

        if huarong_summary:
            stats_text += f"\n   总场次: {huarong_summary['total_games']}\n"
            stats_text += f"   胜利: {huarong_summary['wins']}\n"
            stats_text += f"   失败: {huarong_summary['losses']}\n"
            stats_text += f"   胜率: {huarong_summary['win_rate']}\n"
            stats_text += f"   最佳成绩: {huarong_summary['best_score']}\n"
            stats_text += f"   最快通关: {huarong_summary['best_time']}\n"
            stats_text += f"   完美通关: {huarong_summary['perfect_games']}\n"
            stats_text += f"   当前连胜: {huarong_summary['current_streak']}\n"
            stats_text += f"   最佳连胜: {huarong_summary['best_streak']}\n"
            stats_text += f"   平均步数: {huarong_summary['average_moves']}\n"
            stats_text += f"   总游玩时间: {huarong_summary['total_play_time']}\n"
        else:
            stats_text += "\n   暂无游戏记录\n"

        stats_text += f"\n{'='*40}"
        stats_text += f"\n数独统计\n"

        if sudoku_summary:
            stats_text += f"\n   总场次: {sudoku_summary['total_games']}\n"
            stats_text += f"   胜利: {sudoku_summary['wins']}\n"
            stats_text += f"   失败: {sudoku_summary['losses']}\n"
            stats_text += f"   胜率: {sudoku_summary['win_rate']}\n"
            stats_text += f"   最佳成绩: {sudoku_summary['best_score']}\n"
            stats_text += f"   最快通关: {sudoku_summary['best_time']}\n"
            stats_text += f"   完美通关: {sudoku_summary['perfect_games']}\n"
            stats_text += f"   当前连胜: {sudoku_summary['current_streak']}\n"
            stats_text += f"   最佳连胜: {sudoku_summary['best_streak']}\n"
            stats_text += f"   平均步数: {sudoku_summary['average_moves']}\n"
            stats_text += f"   总游玩时间: {sudoku_summary['total_play_time']}\n"
        else:
            stats_text += "\n   暂无游戏记录\n"

        # 显示成就列表
        unlocked_count = sum(1 for a in self.stats_manager.achievements.values() if a.unlocked)
        total_achievements = len(self.stats_manager.achievements)

        stats_text += f"\n{'='*40}"
        stats_text += f"\n🏅 成就列表 ({unlocked_count}/{total_achievements})\n"

        for ach in sorted(self.stats_manager.achievements.values(), key=lambda x: x.id):
            status = "✅" if ach.unlocked else "⏳"
            progress = ach.get_progress_percent()
            stats_text += f"\n{status} {ach.icon} {ach.name}"
            stats_text += f"\n   进度: {progress:.0f}% ({ach.current_progress}/{ach.target_value})"
            if ach.unlocked:
                stats_text += f"\n   解锁时间: {ach.unlock_time}"

        stats_text += "\n\n" + "="*40

        # 创建统计窗口
        from PyQt5.QtWidgets import QTextEdit

        stats_dialog = QMessageBox(self)
        stats_dialog.setWindowTitle("数据统计")
        stats_dialog.setIcon(QMessageBox.Information)
        stats_text_edit = QTextEdit()
        stats_text_edit.setPlainText(stats_text)
        stats_text_edit.setReadOnly(True)
        stats_text_edit.setFont(QFont("Consolas", 10))
        stats_text_edit.setFixedSize(550, 700)
        
        layout = stats_dialog.layout()
        layout.addWidget(stats_text_edit, 0, 0, 1, layout.columnCount())
        
        stats_dialog.exec_()
    
    def _on_settings(self):
        """设置页面"""
        print("[INFO] Settings clicked")
        self.menu_widget.hide()
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider
        
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ 设置")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b36;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3a3a46;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                margin: -5px 0;
                background: #5a7a9a;
                border-radius: 9px;
            }
            QPushButton {
                background-color: #5a7a9a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6a8aaa;
            }
        """)
        
        layout = QVBoxLayout(dialog)

        title = QLabel("⚙️ 设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 音量设置（示例）
        vol_layout = QHBoxLayout()
        vol_label = QLabel("🔊 音量:")
        vol_slider = QSlider(Qt.Horizontal)
        vol_slider.setRange(0, 100)
        vol_slider.setValue(70)
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(vol_slider)
        layout.addLayout(vol_layout)
        
        # 自动保存设置
        save_layout = QHBoxLayout()
        save_label = QLabel("💾 自动保存:")
        save_slider = QSlider(Qt.Horizontal)
        save_slider.setRange(1, 30)
        save_slider.setValue(5)
        save_layout.addWidget(save_label)
        save_layout.addWidget(save_slider)
        layout.addLayout(save_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()

        reset_data_btn = QPushButton("🗑️ 重置所有数据")
        reset_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #8a4a4a;
            }
            QPushButton:hover {
                background-color: #aa5a5a;
            }
        """)
        reset_data_btn.clicked.connect(lambda: self._reset_data_confirm(dialog))
        btn_layout.addWidget(reset_data_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def _reset_data_confirm(self, parent):
        """确认重置数据"""
        reply = QMessageBox.question(
            parent,
            "⚠️ 确认重置",
            "确定要重置所有数据吗？\n\n包括：\n• 所有游戏记录\n• 成就进度\n• 背包道具\n• 统计数据\n\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stats_manager.reset_all_data()
            QMessageBox.information(
                parent,
                "✅ 重置完成",
                "所有数据已成功重置！",
                QMessageBox.Ok
            )

    def _on_about(self):
        """关于对话框"""
        player_info = self.stats_manager.get_player_summary()
        
        achievements_unlocked = sum(1 for a in self.stats_manager.achievements.values() if a.unlocked)
        total_achievements = len(self.stats_manager.achievements)

        about_text = f"Milk Pet v2.0\n\n"
        about_text += f"一个可爱的桌面伴侣！\n"
        about_text += f"核心功能：\n"
        about_text += f"  • 可拖动位置\n"
        about_text += f"  • 右键快捷菜单\n"
        about_text += f"  • 系统托盘集成\n"
        about_text += f"  • 内置小游戏（华容道、数独）\n"
        about_text += f"  • 背包与道具系统\n"
        about_text += f"  • 数据统计与成就\n"
        about_text += f"\n你的数据：\n"
        about_text += f"  • 启动次数: {player_info['sessions']}\n"
        about_text += f"  • 游戏时长: {player_info['total_play_time']}\n"
        about_text += f"  • 互动次数: {player_info['interactions']}\n"
        about_text += f"  • 解锁成就: {achievements_unlocked}/{total_achievements}\n"
        about_text += f"\n开发者：AI Assistant"
        about_text += f"\n版本 2.0 (Python/PyQt5)"
        about_text += f"\n感谢你的使用！"

        QMessageBox.information(
            self,
            "关于 Milk Pet",
            about_text,
            QMessageBox.Ok
        )
        self.menu_widget.hide()
    
    def _on_quit(self):
        "退出应用"
        print("[INFO] Quitting...")

        # 停止定时器
        self.session_timer.stop()

        # 关闭子窗口
        if self.huarong_window:
            self.huarong_window.close()
        if self.sudoku_window:
            self.sudoku_window.close()
        if self.inventory_window:
            self.inventory_window.close()
        if self.shop_window:
            self.shop_window.close()

        # 清理托盘资源
        if hasattr(self, 'tray_manager'):
            self.tray_manager.cleanup()

        # 保存数据
        self.stats_manager.save_data()

        QApplication.instance().quit()
    
    def closeEvent(self, event):
        "关闭事件"
        # 保存数据
        self.stats_manager.save_data()
        
        event.ignore()
        self.hide()
