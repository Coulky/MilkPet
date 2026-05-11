import sys
import os
import random
import time

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QMessageBox, QLabel, QApplication,
                             QSizePolicy, QComboBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont

from config.styles import Colors
from widgets import GameSuccessWindow


class DHPuzzle(QWidget):
    """数字华容道游戏 - 独立窗口
    
    使用 Godot 项目中的 sliding_puzzle 资源图：
    - 图片位置: assets/images/sliding_puzzle/{1-25}.png
    - 对应 GD 文件: scripts/games/sliding_puzzle/SlidingPuzzle.gd
    """
    
    game_won = pyqtSignal(int, int)  # (score, time_seconds)
    
    GRID_PIXEL_SIZE = 450
    GRID_SPACING = 1
    
    def __init__(self):
        super().__init__(None)

        # 确保关闭此窗口不会退出整个应用
        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.grid_size = 3  # 默认3×3（简单难度）
        self.buttons = []
        self.empty_pos = (2, 2)  # 3×3的空格位置
        self.move_count = 0
        
        # 计时器相关
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.start_time = None
        self.elapsed_time = 0
        self.is_timer_running = False
        
        # 游戏结束标志（防止重复触发）
        self.game_finished = False
        self.success_window = None
        
        # 难度配置 (grid_size: (base_score, time_multiplier))
        self.difficulty_settings = {
            3: {"name": "简单", "base_score": 100, "time_bonus": 2.0},
            4: {"name": "普通", "base_score": 200, "time_bonus": 1.5},
            5: {"name": "困难", "base_score": 400, "time_bonus": 1.0}
        }
        
        # 使用预加载的图片
        from games.resource_manager import ResourceManager
        self.resource_manager = ResourceManager()
        self.number_images = self.resource_manager.dh_puzzle_images
        
        self._setup_ui()
        self._center_on_screen()
        self._new_game()
    
    def _center_on_screen(self):
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _calc_btn_size(self):
        total_spacing = self.GRID_SPACING * (self.grid_size - 1)
        return (self.GRID_PIXEL_SIZE - total_spacing) // self.grid_size
    
    def _setup_ui(self):
        self.setWindowTitle("数字华容道")
        self.setFixedSize(520, 680)

        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 启用透明背景

        container = QFrame(self)
        container.setObjectName("container")

        bg_path = self._get_bg_path()
        container.setStyleSheet(f"""
            QFrame#container {{
                background-image: url("{bg_path}");
                background-color: #2b2b36;
                border-radius: 15px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }}
            QFrame#grid_frame {{
                background-color: rgba(220, 215, 200, 0.95);
                border: 2px solid #8a8070;
                border-radius: 6px;
            }}
            QPushButton {{
                background-color: rgba(180, 175, 160, 0.9);
                color: #333333;
                border: none;
                border-radius: 0px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(200, 195, 180, 0.95);
            }}
            QPushButton:pressed {{
                background-color: rgba(160, 155, 140, 0.95);
            }}
            QPushButton:disabled {{
                background-color: transparent;
                border: none;
            }}
            QLabel#title {{
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }}
            QLabel#info {{
                color: #aaaaaa;
                font-size: 14px;
                padding: 5px;
                background: transparent;
            }}
            QPushButton#control_btn {{
                background-color: #5a7a9a;
                font-size: 14px;
                padding: 8px;
                margin-top: 10px;
                border-radius: 8px;
            }}
            QPushButton#control_btn:hover {{
                background-color: #6a8aaa;
            }}
            QPushButton#close_btn {{
                background-color: #8a4a4a;
                font-size: 14px;
                padding: 8px;
                margin-top: 10px;
                border-radius: 8px;
            }}
            QPushButton#close_btn:hover {{
                background-color: #aa5a5a;
            }}
            QComboBox {{
                background-color: #4a4a5e;
                color: white;
                border: 2px solid #6a6a7e;
                border-radius: 5px;
                padding: 5px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: #8a8a9e;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid white;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #3a3a4e;
                color: white;
                selection-background-color: #5a7a9a;
            }}
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("数字华容道")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # 按钮区域放在上面（新游戏、难度选择、关闭）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch(1)  # 左侧拉伸，让内容居中

        new_game_btn = self.resource_manager.create_styled_button(
            text="新游戏",
            callback=self._new_game,
            size=QSize(140, 100)  # 放大一倍
        )
        button_layout.addWidget(new_game_btn)

        # 难度选择区域（使用容器包裹，设置固定宽度，内容居中）
        from PyQt5.QtWidgets import QWidget
        difficulty_container = QWidget()
        difficulty_container.setStyleSheet("background: transparent;")
        difficulty_container.setFixedWidth(180)  # 设置固定宽度
        
        difficulty_h_layout = QHBoxLayout(difficulty_container)
        difficulty_h_layout.setContentsMargins(0, 0, 0, 0)  # 去掉容器边距
        difficulty_h_layout.setSpacing(2)  # 标签与下拉框间距
        
        difficulty_h_layout.addStretch(1)  # 左侧拉伸
        
        diff_label = QLabel("难度:")
        diff_label.setStyleSheet("color: #8a8070; font-size: 16px; font-weight: bold; background: transparent;")
        difficulty_h_layout.addWidget(diff_label)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("3x3", 3)
        self.difficulty_combo.addItem("4x4", 4)
        self.difficulty_combo.addItem("5x5", 5)
        self.difficulty_combo.setCurrentIndex(0)  # 默认3×3
        self.difficulty_combo.currentIndexChanged.connect(self._on_difficulty_changed)
        self.difficulty_combo.setFixedWidth(45)  # 固定宽度
        self.difficulty_combo.setFixedHeight(30)  # 固定高度
        # 浅粉色主题样式（使用通用样式配置）
        pink_text = Colors.PINK_TEXT
        self.difficulty_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #fad8d1;
                color: {pink_text};
                border: 1px solid #FFB6C1;
                border-radius: 4px;
                padding: 2px;
                font-weight: bold;
                font-size: 13px;
            }}
            QComboBox:hover {{
                background-color: #FFE8EC;
                border-color: #FFC0CB;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {pink_text};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFF5F7;
                color: {pink_text};
                selection-background-color: #fad8d1;
                selection-color: {pink_text};
                font-weight: bold;
            }}
        """)
        difficulty_h_layout.addWidget(self.difficulty_combo)
        
        difficulty_h_layout.addStretch(1)  # 右侧拉伸，让内容居中
        
        # 将容器添加到按钮布局
        button_layout.addWidget(difficulty_container)

        close_btn = self.resource_manager.create_styled_button(
            text="关闭",
            callback=self.close,
            size=QSize(100, 100)  # 放大一倍
        )
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch(1)  # 右侧拉伸，让左右边距相等

        main_layout.addLayout(button_layout)

        info_layout = QHBoxLayout()

        self.info_label = QLabel("时间: 00:00 | 步数: 0")
        self.info_label.setObjectName("info")
        self.info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label)

        main_layout.addLayout(info_layout)

        grid_frame = QFrame()
        grid_frame.setObjectName("grid_frame")
        
        self.grid_layout = QGridLayout(grid_frame)
        self.grid_layout.setSpacing(self.GRID_SPACING)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        
        btn_size = self._calc_btn_size()

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # 只创建空按钮，内容由 _new_game() 填充
                btn = QPushButton("")
                btn.setFixedSize(btn_size, btn_size)
                
                btn.clicked.connect(self._on_button_clicked(i, j))
                
                self.grid_layout.addWidget(btn, i, j)
                self.buttons.append(btn)

        main_layout.addWidget(grid_frame)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
    
    def _on_button_clicked(self, row, col):
        return lambda: self._move_tile(row, col)
    
    def _move_tile(self, row, col):
        empty_row, empty_col = self.empty_pos
        
        if (abs(row - empty_row) == 1 and col == empty_col) or \
           (abs(col - empty_col) == 1 and row == empty_row):
            
            empty_idx = empty_row * self.grid_size + empty_col
            click_idx = row * self.grid_size + col
            
            self.buttons[empty_idx].setText(self.buttons[click_idx].text())
            self.buttons[empty_idx].setIcon(self.buttons[click_idx].icon())
            self.buttons[empty_idx].setIconSize(self.buttons[click_idx].iconSize())
            self.buttons[empty_idx].setEnabled(True)
            self.buttons[empty_idx].setProperty("is_empty", False)
            # 同步 number 属性和样式
            num = self.buttons[click_idx].property("number")
            if num is not None:
                self.buttons[empty_idx].setProperty("number", int(num))
            self.buttons[empty_idx].setStyleSheet(self.buttons[click_idx].styleSheet())
            
            self.buttons[click_idx].setText("")
            self.buttons[click_idx].setIcon(QIcon())
            self.buttons[click_idx].setEnabled(False)
            self.buttons[click_idx].setProperty("is_empty", True)
            self.buttons[click_idx].setProperty("number", 0)
            self._set_empty_button_style(self.buttons[click_idx])
            
            self.empty_pos = (row, col)
            self.move_count += 1
            
            self.info_label.setText(f"步数: {self.move_count}")
            
            # 检查游戏是否完成（带状态保护）
            if not self.game_finished and self._check_win():
                self._show_win()
    
    def _reset_button_style(self, btn):
        btn.setStyleSheet("")
    
    def _set_empty_button_style(self, btn):
        btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
    
    def _check_win(self):
        """检查游戏是否胜利"""

        # 基本检查：确保游戏在进行中
        if not self.buttons or len(self.buttons) != self.grid_size * self.grid_size:
            print("[ERROR] 按钮列表无效")
            return False
        
        expected = 1
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if i == self.grid_size - 1 and j == self.grid_size - 1:
                    continue
                
                # 使用一维索引：idx = row * grid_size + col
                idx = i * self.grid_size + j
                btn = self.buttons[idx]
                
                # 检查按钮文本
                text = btn.text()
                if text != str(expected):
                    return False
                expected += 1
        
        # 检查最后一个按钮（空格）
        last_idx = (self.grid_size - 1) * self.grid_size + (self.grid_size - 1)
        last_btn = self.buttons[last_idx]
        is_win = last_btn.text() == ""
        
        if is_win:
            print(f"[INFO] ✅ 检测到游戏胜利！步数: {self.move_count}")
        
        return is_win
    
    def _show_win(self):
        """显示游戏胜利界面"""
        
        # ========== 前置检查 ==========
        
        # 检查游戏是否已结束（防止重复触发）
        if self.game_finished:
            print("[WARN] 游戏已完成，忽略重复触发")
            return
        
        # 标记游戏结束
        self.game_finished = True
        
        # 检查计时器是否在运行
        if not self.is_timer_running and self.elapsed_time == 0:
            print("[ERROR] 计时器未启动或用时无效")
            return
        
        # ========== 停止计时器 ==========
        self.timer.stop()
        self.is_timer_running = False
        
        print(f"[INFO] 🎉 游戏完成！用时: {self.elapsed_time}秒, 步数: {self.move_count}")
        
        # ========== 计算分数（喵币）==========
        difficulty_config = self.difficulty_settings.get(self.grid_size, {})
        base_score = difficulty_config.get("base_score", 100)
        time_bonus = difficulty_config.get("time_bonus", 1.0)
        difficulty_name = difficulty_config.get("name", "普通")
        
        # 时间奖励：越快完成分数越高（基于时间奖励系数）
        time_score = max(0, int(base_score * time_bonus * (1 - self.elapsed_time / 600)))  # 10分钟内完成有奖励
        
        # 步数奖励：步数越少分数越高
        optimal_moves = (self.grid_size * self.grid_size) * 2  # 预估最优步数
        move_efficiency = max(0.5, min(1.5, optimal_moves / max(self.move_count, 1)))
        
        total_score = int((base_score + time_score) * move_efficiency)
        
        # 分数合理性验证
        if total_score <= 0:
            print("[WARN] 分数计算异常，使用基础分")
            total_score = base_score
        
        print(f"[INFO] 💰 获得喵币: {total_score} (难度: {difficulty_name})")
        
        # ========== 显示成功窗口 ==========
        try:
            # 关闭之前的成功窗口（如果有）
            if self.success_window and hasattr(self.success_window, 'close'):
                self.success_window.close()
                self.success_window.deleteLater()
            
            # 创建新的游戏成功窗口
            self.success_window = GameSuccessWindow(
                game_name="数字华容道",
                difficulty=difficulty_name,
                time_seconds=self.elapsed_time,
                score=total_score
            )
            
            # 连接确认信号
            self.success_window.confirmed.connect(self._on_game_success_confirmed)
            
            # 显示窗口
            self.success_window.show()
            self.success_window.raise_()
            self.success_window.activateWindow()
            
            print("[OK] 游戏成功窗口已显示")
            
        except Exception as e:
            print(f"[ERROR] 显示游戏成功窗口失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 备用方案：直接关闭游戏并发送信号
            self._on_game_success_confirmed()
            return
        
        # ========== 发送游戏胜利信号 ==========
        try:
            self.game_won.emit(total_score, self.elapsed_time)
            print("[OK] 游戏胜利信号已发送")
        except Exception as e:
            print(f"[ERROR] 发送游戏胜利信号失败: {e}")
    
    def _on_game_success_confirmed(self):
        """游戏成功窗口确认处理"""
        
        print("[INFO] 用户点击了确认按钮，准备关闭游戏...")
        
        try:
            # 关闭成功窗口
            if self.success_window:
                self.success_window.close()
                self.success_window = None
            
            # 只关闭当前游戏窗口，不要关闭桌宠
            self.close()
            
            print("[OK] 游戏已正常结束")
            
        except Exception as e:
            print(f"[ERROR] 关闭游戏窗口时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 强制关闭
            try:
                self.close()
            except:
                pass
    
    def _show_hint(self):
        QMessageBox.information(
            self,
            "游戏提示",
            "目标：将数字按顺序排列 1-15\n"
            "规则：只能移动空格相邻的方块\n"
            "技巧：先完成前两行，再处理底部",
            QMessageBox.Ok
        )
    
    def _new_game(self):
        """开始新游戏"""
        
        print("[INFO] 开始新游戏...")
        
        # 停止计时器
        self.timer.stop()
        self.is_timer_running = False
        
        # 关闭之前的成功窗口（如果有）
        if self.success_window:
            try:
                self.success_window.close()
                self.success_window.deleteLater()
            except:
                pass
            self.success_window = None
        
        # 重置游戏状态
        self.game_finished = False
        
        btn_size = self._calc_btn_size()
        icon_size = btn_size - 4
        
        # 重置数据
        numbers = list(range(1, self.grid_size * self.grid_size))
        # numbers.insert(-1, 0)

        numbers.append(0)  # 0放在最后一位作为空格
        
        random.shuffle(numbers)
        
        idx = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                num = numbers[idx]
                btn = self.buttons[i * self.grid_size + j]
                
                if num != 0:
                    if num in self.number_images:
                        icon = QIcon(self.number_images[num])
                        btn.setIcon(icon)
                        btn.setIconSize(QSize(icon_size, icon_size))
                        btn.setText(str(num))
                        btn.setStyleSheet("""
                            QPushButton {
                                border: none;
                                background-color: transparent;
                                color: transparent;
                                font-size: 1px;
                                padding: 0px;
                                margin: 0px;
                            }
                            QPushButton:hover {
                                background-color: rgba(255, 255, 255, 0.1);
                            }
                            QPushButton:pressed {
                                background-color: rgba(0, 0, 0, 0.1);
                            }
                        """)
                    else:
                        btn.setText(str(num))
                        btn.setIcon(QIcon())
                        btn.setStyleSheet("""
                            QPushButton {
                                border: none;
                                background-color: transparent;
                                color: #333333;
                                font-size: 18px;
                                font-weight: bold;
                                padding: 0px;
                                margin: 0px;
                            }
                            QPushButton:hover {
                                background-color: rgba(255, 255, 255, 0.1);
                            }
                            QPushButton:pressed {
                                background-color: rgba(0, 0, 0, 0.1);
                            }
                        """)
                    btn.setEnabled(True)
                    btn.setProperty("is_empty", False)
                    btn.setProperty("number", num)
                else:
                    btn.setText("")
                    btn.setIcon(QIcon())
                    btn.setEnabled(False)
                    btn.setProperty("is_empty", True)
                    self._set_empty_button_style(btn)
                    self.empty_pos = (i, j)
                
                idx += 1
        
        self.move_count = 0
        self.elapsed_time = 0
        
        # 启动计时器
        self.start_time = time.time()
        self.timer.start(1000)  # 每秒更新一次
        self.is_timer_running = True
        
        # 更新显示
        self._update_info_display()
    
    def _update_timer(self):
        """更新计时器"""
        if self.is_timer_running:
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time)
            self._update_info_display()
    
    def _update_info_display(self):
        """更新信息栏显示"""
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        difficulty_name = self.difficulty_settings.get(self.grid_size, {}).get("name", "普通")
        self.info_label.setText(f"{time_str} | 步数: {self.move_count} | {difficulty_name}")
    
    def _on_difficulty_changed(self, index):
        """难度改变时重新开始游戏"""
        new_size = self.difficulty_combo.itemData(index)
        if new_size != self.grid_size:
            self.grid_size = new_size
            self._rebuild_grid()
            self._new_game()
    
    def _rebuild_grid(self):
        """重建网格"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.buttons.clear()
        
        btn_size = self._calc_btn_size()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                btn = QPushButton("")
                btn.setFixedSize(btn_size, btn_size)
                btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                num = i * self.grid_size + j + 1
                if num < self.grid_size * self.grid_size:
                    btn.setText(str(num))
                    btn.setProperty("is_empty", False)
                    btn.setEnabled(True)

                    if num in self.number_images:
                        icon = QIcon(self.number_images[num])
                        btn.setIcon(icon)
                        btn.setIconSize(QSize(btn_size - 4, btn_size - 4))
                        btn.setText("")
                else:
                    btn.setText("")
                    btn.setProperty("is_empty", True)
                    btn.setEnabled(False)
                    self._set_empty_button_style(btn)
                
                btn.clicked.connect(self._on_button_clicked(i, j))
                self.grid_layout.addWidget(btn, i, j)
                self.buttons.append(btn)
    
    def _get_bg_path(self):
        """获取背景图片路径"""
        return self.resource_manager.get_background_path()

    def closeEvent(self, event):
        """关闭事件 - 只关闭华容道窗口，不影响桌宠"""
        # 停止计时器
        self.timer.stop()
        self.is_timer_running = False
        event.accept()
