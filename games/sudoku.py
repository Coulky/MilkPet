import sys
import os
import random
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QMessageBox, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QFont


class SudokuGame(QWidget):
    """数独游戏 - 独立窗口
    
    使用 Godot 项目中的 sudoku 资源图：
    - 图片位置: assets/images/sudoku/{1-9}.png
    - 对应 GD 文件: scripts/games/sudoku/SudokuUI.gd
    """
    
    game_won = pyqtSignal()
    
    def __init__(self):
        print("[DEBUG] SudokuGame: Starting initialization...")
        
        try:
            super().__init__(None)

            self.setAttribute(Qt.WA_QuitOnClose, False)
            
            self.board = [[0]*9 for _ in range(9)]
            self.solution = [[0]*9 for _ in range(9)]
            self.inputs = [[None]*9 for _ in range(9)]
            self.initial = [[False]*9 for _ in range(9)]
            
            from basic_model.resource_manager import ResourceManager
            self.resource_manager = ResourceManager()
            
            print("[DEBUG] SudokuGame: Setting up UI...")
            self._setup_ui()
            
            print("[DEBUG] SudokuGame: Centering on screen...")
            self._center_on_screen()
            
            print("[DEBUG] SudokuGame: Starting new game...")
            self._new_game()
            
            print("[DEBUG] SudokuGame: Initialization complete!")
            
        except Exception as e:
            print(f"[ERROR] SudokuGame initialization failed: {e}")
            traceback.print_exc()
            raise
    
    def _center_on_screen(self):
        from PyQt5.QtWidgets import QApplication
        
        screen = QApplication.instance().primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        self.setWindowTitle("数独")
        self.setFixedSize(520, 680)

        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_QuitOnClose, False)
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
            QLabel#title {{
                color: #ffffff;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }}
            QLabel#info {{
                color: #aaaaaa;
                font-size: 13px;
                padding: 5px;
                background: transparent;
            }}
            QPushButton#cell_btn {{
                background-color: #3a3a46;
                color: white;
                border: 2px solid #5a5a6e;
                border-radius: 6px;
                font-size: 20px;
                font-weight: bold;
                min-width: 45px;
                min-height: 45px;
            }}
            QPushButton#cell_btn:hover {{
                background-color: #4a4a56;
                border-color: #8a8aaa;
            }}
            QPushButton#num_btn {{
                background-color: #4a5a7a;
                color: white;
                border: 2px solid #6a7a9a;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                min-width: 45px;
                min-height: 45px;
            }}
            QPushButton#num_btn:hover {{
                background-color: #5a6a8a;
                border-color: #8a9aba;
            }}
            QPushButton#control_btn {{
                background-color: #5a7a9a;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#control_btn:hover {{
                background-color: #6a8aaa;
            }}
            QPushButton#close_btn {{
                background-color: #8a4a4a;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#close_btn:hover {{
                background-color: #aa5a5a;
            }}
            QPushButton#clear_btn {{
                background-color: #7a5a4a;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton#clear_btn:hover {{
                background-color: #9a6a5a;
            }}
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("数独")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        info_layout = QHBoxLayout()
        self.info_label = "点击格子，然后选择数字"
        self.info_label_widget = QLabel(self.info_label)
        self.info_label_widget.setObjectName("info")
        self.info_label_widget.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label_widget)
        main_layout.addLayout(info_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(2)

        for i in range(9):
            for j in range(9):
                btn = self.resource_manager.create_styled_button(
                    text="",
                    callback=self._on_cell_clicked(i, j),
                    size=QSize(48, 48)
                )
                
                if (i % 3 == 0 and i != 0) or (j % 3 == 0 and j != 0):
                    if i % 3 == 0:
                        btn.setStyleSheet(btn.styleSheet() + "QPushButton { border-top: 3px solid #8a8aaa; }")
                    if j % 3 == 0:
                        current = btn.styleSheet() or ""
                        btn.setStyleSheet(current + "QPushButton { border-left: 3px solid #8a8aaa; }")

                self.grid_layout.addWidget(btn, i, j)
                self.inputs[i][j] = btn

        main_layout.addWidget(self.grid_widget)

        num_layout = QHBoxLayout()
        num_layout.setSpacing(5)

        for num in range(1, 10):
            num_btn = self.resource_manager.create_styled_button(
                text=str(num),
                callback=lambda checked, n=num: self._on_number_selected(n),
                size=QSize(48, 48)
            )
            num_layout.addWidget(num_btn)

        clear_btn = self.resource_manager.create_styled_button(
            text="X",
            callback=self._on_clear_selected,
            size=QSize(48, 48)
        )
        num_layout.addWidget(clear_btn)

        main_layout.addLayout(num_layout)

        button_layout = QHBoxLayout()

        check_btn = self.resource_manager.create_styled_button(
            text="检查答案",
            callback=self._check_solution,
            size=QSize(100, 40)
        )
        button_layout.addWidget(check_btn)

        solve_btn = self.resource_manager.create_styled_button(
            text="显示答案",
            callback=self._show_solution,
            size=QSize(100, 40)
        )
        button_layout.addWidget(solve_btn)

        new_game_btn = self.resource_manager.create_styled_button(
            text="新游戏",
            callback=self._new_game,
            size=QSize(100, 40)
        )
        button_layout.addWidget(new_game_btn)

        close_btn = self.resource_manager.create_styled_button(
            text="关闭",
            callback=self.close,
            size=QSize(100, 40)
        )
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)

        self.selected_cell = None

    def _on_cell_clicked(self, row, col):
        return lambda: self._select_cell(row, col)
    
    def _select_cell(self, row, col):
        if self.initial[row][col]:
            return
        
        # 取消之前选中的格子
        if self.selected_cell:
            old_row, old_col = self.selected_cell
            self.inputs[old_row][old_col].setStyleSheet("")
        
        # 选中当前格子
        self.selected_cell = (row, col)
        self.inputs[row][col].setStyleSheet("QPushButton#cell_btn { background-color: #5a6a8a; border-color: #8a9aba; }")
    
    def _on_number_selected(self, num):
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        if not self.initial[row][col]:
            self.board[row][col] = num
            self.inputs[row][col].setText(str(num))
            self.inputs[row][col].setStyleSheet("")
    
    def _on_clear_selected(self):
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        if not self.initial[row][col]:
            self.board[row][col] = 0
            self.inputs[row][col].setText("")
            self.inputs[row][col].setStyleSheet("")
        
        self.selected_cell = None
    
    def _generate_puzzle(self):
        base = 3
        side = base * base
        
        def pattern(r, c): 
            return (base * (r % base) + r // base + c) % side
        
        def shuffle(s): 
            return random.sample(s, len(s))
        
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))
        
        self.solution = [[nums[pattern(r, c)] for c in cols] for r in rows]
        
        squares = side * side
        empties = squares * 3 // 4
        for p in random.sample(range(squares), empties):
            self.solution[p // side][p % side] = 0
    
    def _new_game(self):
        self.board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.initial = [[False]*9 for _ in range(9)]
        self.selected_cell = None
        
        self._generate_puzzle()
        
        for i in range(9):
            for j in range(9):
                value = self.solution[i][j]
                self.board[i][j] = value
                
                if value != 0:
                    self.initial[i][j] = True
                    self.inputs[i][j].setText(str(value))
                    self.inputs[i][j].setEnabled(False)
                    self.inputs[i][j].setStyleSheet("QPushButton#cell_btn { background-color: #2a2a36; color: #888899; }")
                else:
                    self.inputs[i][j].setText("")
                    self.inputs[i][j].setEnabled(True)
                    self.inputs[i][j].setStyleSheet("")
                    self.board[i][j] = 0
        
        self.info_label_widget.setText("点击格子，然后选择数字")
    
    def _check_solution(self):
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]
                if value < 1 or value > 9:
                    QMessageBox.warning(
                        self,
                        "检查结果",
                        f"位置 ({i+1}, {j+1}) 还未填写或数字无效！\n请填入 1-9",
                        QMessageBox.Ok
                    )
                    return
        
        is_correct = True
        errors = []
        
        for i in range(9):
            row_nums = [self.board[i][j] for j in range(9)]
            if len(set(row_nums)) != 9:
                is_correct = False
                errors.append(f"第 {i+1} 行有重复数字")
        
        for j in range(9):
            col_nums = [self.board[i][j] for i in range(9)]
            if len(set(col_nums)) != 9:
                is_correct = False
                errors.append(f"第 {j+1} 列有重复数字")
        
        for box_i in range(3):
            for box_j in range(3):
                box_nums = []
                for i in range(box_i * 3, box_i * 3 + 3):
                    for j in range(box_j * 3, box_j * 3 + 3):
                        box_nums.append(self.board[i][j])
                if len(set(box_nums)) != 9:
                    is_correct = False
                    errors.append(f"第 {box_i+1}-{box_j+1} 宫有重复数字")
        
        if is_correct:
            QMessageBox.information(
                self,
                "恭喜！",
                "答案正确！你完成了这个数独谜题！\n\n太棒了！",
                QMessageBox.Ok
            )
            self.game_won.emit()
        else:
            error_text = "\n".join(errors[:3])
            if len(errors) > 3:
                error_text += f"\n... 还有 {len(errors)-3} 个错误"
            
            QMessageBox.warning(
                self,
                "答案有误",
                f"发现以下问题：\n{error_text}\n\n请检查后重试",
                QMessageBox.Ok
            )
    
    def _show_solution(self):
        try:
            reply = QMessageBox.question(
                self,
                "显示答案",
                "确定要显示完整答案吗？\n这将结束当前游戏",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                for i in range(9):
                    for j in range(9):
                        value = self.solution[i][j]
                        self.inputs[i][j].setText(str(value))
                        self.inputs[i][j].setEnabled(False)
                        self.board[i][j] = value

                self.info_label_widget.setText("已显示完整答案")
                self.selected_cell = None
        except Exception as e:
            print(f"❌ Error showing solution: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_bg_path(self):
        """获取背景图片路径"""
        from basic_model.resource_manager import ResourceManager
        return ResourceManager().get_background_path()

    def closeEvent(self, event):
        event.accept()
