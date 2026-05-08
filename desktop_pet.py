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

from PyQt5.QtWidgets import (QWidget, QLabel, QMenu, QAction,
                             QVBoxLayout, QHBoxLayout, QPushButton, 
                             QCheckBox, QMessageBox, QApplication, 
                             QScrollArea)
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
        
        # 玩家分数
        self.player_score = 0
        
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
        self.menu_widget = QWidget(self)
        self.menu_widget.setFixedWidth(220)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.scroll_area.setWidget(self.menu_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedWidth(250)
        self.scroll_area.setMinimumHeight(500)
        self.scroll_area.setMaximumHeight(800)
        self.scroll_area.hide()
        
        # 滚动区域样式（隐藏滚动条）
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(43, 43, 54, 0.95);
                border: 2px solid rgba(106, 106, 126, 0.95);
                border-radius: 10px;
            }
            QScrollBar:vertical {
                width: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(8)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_widget.setLayout(menu_layout)

        menu_style = """
            QPushButton {
                background-color: #fad8d1;
                color: #8a8070;
                border: none;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #FFE4E9;
            }
            QPushButton:pressed {
                background-color: #FFC0CB;
            }
            QWidget#menu_container {
                background-color: rgba(43, 43, 54, 0.95);
                border: 2px solid rgba(106, 106, 126, 0.95);
                border-radius: 10px;
            }
            QLabel#category_label {
                color: #8a8070;
                font-size: 15px;
                font-weight: bold;
                padding: 5px 0px 2px 5px;
                margin-top: 8px;
            }
            QCheckBox {
                color: white;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #888;
                background-color: #333;
            }
            QCheckBox::indicator:checked {
                background-color: #5a9a5a;
                border-color: #7aba7a;
            }
        """
        self.menu_widget.setStyleSheet(menu_style)
        self.menu_widget.setObjectName("menu_container")
        
        # 设置主布局间距
        menu_layout.setSpacing(4)  # 分类内按钮间距4px
        
        # ========== 娱乐区域 ==========
        # 第一行：标题 + 按钮水平对齐（高度相同）
        game_row = QHBoxLayout()
        game_row.setSpacing(5)
        game_row.setContentsMargins(0, 0, 0, 0)  # 无边距
        
        game_label = QLabel("娱乐")
        game_label.setObjectName("category_label")
        game_label.setFixedHeight(32)  # 与按钮高度一致
        game_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 垂直居中
        game_row.addWidget(game_label)

        huarong_btn = QPushButton("数字华容道")
        huarong_btn.setFixedWidth(150)  # 统一宽度
        huarong_btn.setFixedHeight(32)  # 统一高度
        huarong_btn.clicked.connect(self._on_huarong)
        game_row.addWidget(huarong_btn)
        
        menu_layout.addLayout(game_row)

        # 后续按钮（与第一行按钮左对齐）
        sudoku_btn = QPushButton("数独")
        sudoku_btn.setFixedWidth(150)  # 统一宽度
        sudoku_btn.setFixedHeight(32)  # 统一高度
        sudoku_btn.clicked.connect(self._on_sudoku)
        menu_layout.addWidget(sudoku_btn)
        
        # 粉色分隔线（娱乐与功能之间）
        line1 = QWidget()
        line1.setFixedHeight(2)
        line1.setStyleSheet("background-color: #FFB6C1; border-radius: 1px;")
        menu_layout.addWidget(line1)
        
        # ========== 功能区域 ==========
        # 第一行：标题 + 按钮水平对齐（高度相同）
        func_row = QHBoxLayout()
        func_row.setSpacing(5)
        func_row.setContentsMargins(0, 0, 0, 0)  # 无边距
        
        func_label = QLabel("功能")
        func_label.setObjectName("category_label")
        func_label.setFixedHeight(32)  # 与按钮高度一致
        func_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 垂直居中
        func_row.addWidget(func_label)

        backpack_btn = QPushButton("背包")
        backpack_btn.setFixedWidth(150)  # 统一宽度
        backpack_btn.setFixedHeight(32)  # 统一高度
        backpack_btn.clicked.connect(self._on_backpack)
        func_row.addWidget(backpack_btn)
        
        menu_layout.addLayout(func_row)

        # 后续按钮（与第一行按钮左对齐）
        shop_btn = QPushButton("商城")
        shop_btn.setFixedWidth(150)  # 统一宽度
        shop_btn.setFixedHeight(32)  # 统一高度
        shop_btn.clicked.connect(self._on_shop)
        menu_layout.addWidget(shop_btn)

        # 粉色分隔线（功能与系统之间）
        line2 = QWidget()
        line2.setFixedHeight(2)
        line2.setStyleSheet("background-color: #FFB6C1; border-radius: 1px;")
        menu_layout.addWidget(line2)
        
        # ========== 系统区域 ==========
        # 第一行：标题 + 按钮水平对齐（高度相同）
        sys_row = QHBoxLayout()
        sys_row.setSpacing(5)
        sys_row.setContentsMargins(0, 0, 0, 0)  # 无边距
        
        sys_label = QLabel("系统")
        sys_label.setObjectName("category_label")
        sys_label.setFixedHeight(32)  # 与按钮高度一致
        sys_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 垂直居中
        sys_row.addWidget(sys_label)

        self.top_btn = QPushButton("取消置顶" if self.is_on_top else "置顶")
        self.top_btn.setFixedWidth(150)  # 统一宽度
        self.top_btn.setFixedHeight(32)  # 统一高度
        self.top_btn.clicked.connect(self._toggle_top)
        sys_row.addWidget(self.top_btn)
        
        menu_layout.addLayout(sys_row)

        click_checkbox = QCheckBox("允许点击交互")
        click_checkbox.setChecked(True)
        click_checkbox.stateChanged.connect(self._on_click_toggle)
        menu_layout.addWidget(click_checkbox)
        
        quit_btn = QPushButton("退出")
        quit_btn.setFixedWidth(150)  # 统一宽度
        quit_btn.setFixedHeight(32)  # 统一高度
        quit_btn.clicked.connect(self._on_quit)
        quit_btn.setStyleSheet("""
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
        menu_layout.addWidget(quit_btn)
    
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
    
    def _show_menu(self, pos):
        """显示菜单 - 固定位置不跟随鼠标"""
        try:
            # 固定菜单位置：桌宠右下方
            pet_x = self.x()
            pet_y = self.y()
            pet_width = self.width()
            pet_height = self.height()

            # 菜单显示在桌宠右侧偏下
            x = pet_x + pet_width + 15
            y = pet_y + 20

            # 获取屏幕尺寸确保不超出
            screen = QApplication.instance().primaryScreen().availableGeometry()
            
            # 如果右侧空间不够，显示在左侧
            if x + 280 > screen.width():
                x = pet_x - 290
            
            # 如果底部空间不够，向上调整
            if y + 700 > screen.height():
                y = screen.height() - 720

            if y < 0:
                y = 10

            self.scroll_area.move(x, y)
            self.scroll_area.show()
            self.scroll_area.raise_()

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
                self.scroll_area.hide()
            
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
            self.top_btn.setText("取消置顶")
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
            self.top_btn.setText("置顶")
        
        # 恢复窗口位置和可见性
        self.move(pos)
        if visible:
            self.show()
        
        self.scroll_area.hide()
    
    def _on_click_toggle(self, state):
        "切换点击交互"
        self.allow_click = (state == Qt.Checked)
        
        if self.allow_click:
            current_flags = self.windowFlags()
            new_flags = current_flags & ~Qt.WindowTransparentForInput
            self.setWindowFlags(new_flags)
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        else:
            current_flags = self.windowFlags()
            new_flags = current_flags | Qt.WindowTransparentForInput
            self.setWindowFlags(new_flags)
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self.show()
    
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
        self.scroll_area.hide()

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
        self.scroll_area.hide()
        
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
                self.player_score += score
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
        self.scroll_area.hide()

        # 创建或显示背包窗口
        if not self.inventory_window or not self.inventory_window.isVisible():
            self._close_all_windows()
            self.inventory_window = InventoryWindow(parent=None)

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
            # 可以在这里保存背包数据
            pass
    
    def _on_shop(self):
        """打开商店"""
        print("Opening shop")
        self.scroll_area.hide()

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
        self.scroll_area.hide()
        
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
        self.scroll_area.hide()
        
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
        self.scroll_area.hide()
    
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
