import sys
import os
import random
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGridLayout, QLabel, QFrame, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

from config.styles import Colors, ButtonStyles, Fonts, Rounded
from widgets.dialog import GameFailDialog


WHITE_THEME = {
    'primary': '#ffffff',
    'text': '#333333',
    'outer_border': '#313131',
    'inner_border': '#e0e0e0',
    'fill_text': '#2E59A2',
    'initial_text': '#333333',
    'same_num': '#92B2E3',
    'selected_area': '#D5ECFF',
    'selected_cell': '#B8D4F0',
    'error': '#F44336',
    'conflict': '#F6A2A2',
    'note_color': '#888888',
}

DIFFICULTY_SETTINGS = {
    'easy': {'name': '简单', 'remove_count': 35},
    'medium': {'name': '中等', 'remove_count': 45},
    'hard': {'name': '困难', 'remove_count': 55},
}

INITIAL_LIVES = 5


class SudokuGame(QWidget):
    """数独游戏 - 白色主题，参照JS项目配色，带生命值系统"""

    game_won = pyqtSignal(int, int, str)

    def __init__(self):
        print("[DEBUG] SudokuGame: Starting initialization...")
        try:
            super().__init__(None)
            self.setAttribute(Qt.WA_QuitOnClose, False)

            self.board = [[0]*9 for _ in range(9)]
            self.solution = [[0]*9 for _ in range(9)]
            self.inputs = [[None]*9 for _ in range(9)]
            self.initial = [[False]*9 for _ in range(9)]
            self.notes = [[set() for _ in range(9)] for _ in range(9)]
            self.note_mode = False
            self.current_difficulty = 'easy'
            self.selected_cell = None
            self.selected_number = None
            self.game_finished = False
            self.lives = INITIAL_LIVES
            self.game_over = False

            from basic_model.resource_manager import ResourceManager
            self.resource_manager = ResourceManager()

            print("[DEBUG] Setting up UI...")
            self._setup_ui()

            print("[DEBUG] Centering on screen...")
            self._center_on_screen()

            print("[DEBUG] Starting new game...")
            self._new_game()

            print("[DEBUG] Initialization complete!")
        except Exception as e:
            print(f"[ERROR] SudokuGame init failed: {e}")
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
        self.setFixedSize(540, 750)

        flags = Qt.Window | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        container = QFrame(self)
        container.setObjectName("container")
        bg_path = self._get_bg_path()
        T = WHITE_THEME
        container.setStyleSheet(f"""
            QFrame#container {{
                background-image: url("{bg_path}");
                background-color: #2b2b36;
                border-radius: 15px;
                font-family: {Fonts.FAMILY};
            }}
            QLabel#title {{
                color: #ffffff;
                font-size: {Fonts.SIZE_TITLE}px;
                font-weight: bold;
                padding: 6px;
                background: transparent;
            }}
            QLabel#info {{
                color: #aaaaaa;
                font-size: {Fonts.SIZE_SMALL}px;
                padding: 3px;
                background: transparent;
            }}
            QLabel#lives_label {{
                color: {T['error']};
                font-size: {Fonts.SIZE_NORMAL}px;
                font-weight: bold;
                background: transparent;
            }}
            QPushButton#cell_btn {{
                background-color: {T['primary']};
                color: {T['text']};
                border: 1px solid {T['inner_border']};
                border-radius: 0px;
                font-size: 20px;
                font-weight: bold;
                min-width: 50px;
                min-height: 50px;
            }}
            QPushButton#cell_btn:hover {{ background-color: #f5f5f5; }}
            QPushButton#cell_btn:disabled {{
                background-color: {T['primary']};
                color: {T['initial_text']};
                font-weight: bold;
            }}
            QPushButton#num_btn {{
                background-color: #f0f0f8;
                color: {T['fill_text']};
                border: 2px solid {T['inner_border']};
                border-radius: {Rounded.NORMAL}px;
                font-size: 18px;
                font-weight: bold;
                min-width: 48px;
                min-height: 42px;
            }}
            QPushButton#num_btn:hover {{ background-color: #e0e8f0; border-color: {T['fill_text']}; }}
            QPushButton#num_btn:checked {{
                background-color: {T['same_num']};
                color: white;
                border-color: {T['fill_text']};
            }}
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 12, 15, 12)

        title = QLabel("数独")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        new_game_btn = self.resource_manager.create_styled_button(
            text="新游戏",
            callback=self._new_game,
            size=QSize(100, 50)
        )
        top_bar.addWidget(new_game_btn)

        difficulty_container = QWidget()
        difficulty_container.setStyleSheet("background: transparent;")
        difficulty_container.setFixedWidth(160)

        diff_layout = QHBoxLayout(difficulty_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_layout.setSpacing(4)

        diff_label = QLabel("难度:")
        diff_label.setStyleSheet(f"color: {Colors.PINK_TEXT}; font-size: 14px; font-weight: bold; background: transparent;")
        diff_layout.addWidget(diff_label)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("简单", "easy")
        self.difficulty_combo.addItem("中等", "medium")
        self.difficulty_combo.addItem("困难", "hard")
        self.difficulty_combo.setCurrentIndex(0)
        self.difficulty_combo.currentIndexChanged.connect(self._on_difficulty_changed)
        self.difficulty_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.PINK_LIGHT};
                color: {Colors.PINK_TEXT};
                border: 1px solid {Colors.PINK_DARK};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QComboBox:hover {{
                background-color: "#FFE8EC";
                border-color: {Colors.PINK_DARK};
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid {Colors.PINK_TEXT};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #3a3a4e;
                color: white;
                selection-background-color: #5a7a9a;
            }}
        """)
        diff_layout.addWidget(self.difficulty_combo)
        top_bar.addWidget(difficulty_container)

        self.note_btn = self.resource_manager.create_styled_button(
            text="✏笔记",
            callback=self._toggle_note_mode,
            size=QSize(80, 50)
        )
        self.note_btn.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
            QLabel {{
                color: {Colors.PINK_TEXT};
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
            }}
        """)
        top_bar.addWidget(self.note_btn)

        close_btn = self.resource_manager.create_styled_button(
            text="关闭",
            callback=self.close,
            size=QSize(70, 50)
        )
        close_btn.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
            QLabel {{
                color: {Colors.PINK_TEXT};
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
            }}
        """)
        top_bar.addWidget(close_btn)

        main_layout.addLayout(top_bar)

        lives_layout = QHBoxLayout()
        lives_layout.addStretch(1)
        self.lives_label = QLabel(f"❤️ x{self.lives}")
        self.lives_label.setObjectName("lives_label")
        self.lives_label.setAlignment(Qt.AlignCenter)
        lives_layout.addWidget(self.lives_label)
        lives_layout.addStretch(1)
        main_layout.addLayout(lives_layout)

        info_layout = QHBoxLayout()
        self.info_label_widget = QLabel("点击格子，选择数字")
        self.info_label_widget.setObjectName("info")
        self.info_label_widget.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.info_label_widget)
        main_layout.addLayout(info_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(9):
            for j in range(9):
                btn = QPushButton("")
                btn.setObjectName("cell_btn")
                btn.setFixedSize(50, 50)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(self._on_cell_clicked(i, j))
                self.grid_layout.addWidget(btn, i, j)
                self.inputs[i][j] = btn

        main_layout.addWidget(self.grid_widget, alignment=Qt.AlignCenter)

        num_layout = QHBoxLayout()
        num_layout.setSpacing(4)

        self.num_buttons = []
        for num in range(1, 10):
            num_btn = QPushButton(str(num))
            num_btn.setObjectName("num_btn")
            num_btn.setFixedSize(48, 42)
            num_btn.setCursor(Qt.PointingHandCursor)
            num_btn.setCheckable(True)
            num_btn.clicked.connect(lambda checked, n=num: self._on_number_selected(n))
            num_layout.addWidget(num_btn)
            self.num_buttons.append(num_btn)

        clear_btn = QPushButton("X")
        clear_btn.setObjectName("num_btn")
        clear_btn.setFixedSize(48, 42)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._on_clear_selected)
        num_layout.addWidget(clear_btn)

        main_layout.addLayout(num_layout)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)

        self._apply_board_style()

    def _apply_board_style(self):
        T = WHITE_THEME
        for i in range(9):
            for j in range(9):
                btn = self.inputs[i][j]
                style_parts = []
                if i % 3 == 0:
                    style_parts.append(f"border-top: 2px solid {T['outer_border']};")
                else:
                    style_parts.append(f"border-top: 1px solid {T['inner_border']};")
                if i == 8:
                    style_parts.append(f"border-bottom: 2px solid {T['outer_border']};")
                if j % 3 == 0:
                    style_parts.append(f"border-left: 2px solid {T['outer_border']};")
                else:
                    style_parts.append(f"border-left: 1px solid {T['inner_border']};")
                if j == 8:
                    style_parts.append(f"border-right: 2px solid {T['outer_border']};")

                base_style = f"""
                    QPushButton#cell_btn {{
                        background-color: {T['primary']};
                        color: {T['text']};
                        {" ".join(style_parts)}
                    }}
                """
                btn.setStyleSheet(base_style)

    def _get_cell_base_style(self, row, col):
        T = WHITE_THEME
        style_parts = []
        if row % 3 == 0:
            style_parts.append(f"border-top: 2px solid {T['outer_border']};")
        else:
            style_parts.append(f"border-top: 1px solid {T['inner_border']};")
        if row == 8:
            style_parts.append(f"border-bottom: 2px solid {T['outer_border']};")
        if col % 3 == 0:
            style_parts.append(f"border-left: 2px solid {T['outer_border']};")
        else:
            style_parts.append(f"border-left: 1px solid {T['inner_border']};")
        if col == 8:
            style_parts.append(f"border-right: 2px solid {T['outer_border']};")
        return " ".join(style_parts)

    def _on_cell_clicked(self, row, col):
        return lambda: self._select_cell(row, col)

    def _select_cell(self, row, col):
        if self.game_finished or self.game_over:
            return
        self._clear_highlights()
        self.selected_cell = (row, col)
        self._update_highlights()

    def _on_number_selected(self, num):
        if not self.selected_cell or self.game_finished or self.game_over:
            return
        row, col = self.selected_cell
        if self.initial[row][col]:
            self.info_label_widget.setText("⚠️ 初始数字不可修改！")
            return

        old_value = self.board[row][col]
        if old_value == num:
            return

        self.board[row][col] = num
        self.notes[row][col].clear()
        self.inputs[row][col].setText(str(num))

        is_correct = (self.solution[row][col] == num)
        base_style = self._get_cell_base_style(row, col)

        if is_correct:
            self.inputs[row][col].setStyleSheet(
                f"QPushButton#cell_btn {{"
                f"  background-color: {WHITE_THEME['primary']};"
                f"  color: {WHITE_THEME['fill_text']};"
                f"  font-weight: bold;"
                f"  {base_style}"
                f"}}"
            )
        else:
            self.inputs[row][col].setStyleSheet(
                f"QPushButton#cell_btn {{"
                f"  background-color: {WHITE_THEME['primary']};"
                f"  color: {WHITE_THEME['error']} !important;"
                f"  font-weight: bold;"
                f"  {base_style}"
                f"}}"
            )
            self._lose_life()

        self._check_conflicts(row, col, num)
        self._check_win()
        self._update_highlights()

    def _lose_life(self):
        self.lives -= 1
        self.lives_label.setText(f"❤️ x{self.lives}")

        if self.lives <= 0:
            self._handle_game_over()
        else:
            self.info_label_widget.setText(f"答案错误！剩余生命值: {self.lives}")

    def _handle_game_over(self):
        self.game_over = True
        self.info_label_widget.setText("💔 游戏失败！")

        has_revive_coin = self._check_revive_coin()

        dialog = GameFailDialog(
            title="游戏失败",
            message=f"数独挑战失败！\n难度：{DIFFICULTY_SETTINGS[self.current_difficulty]['name']}\n\n是否使用复活币继续？",
            parent=self,
            can_revive=has_revive_coin
        )
        dialog.revive_clicked.connect(self._on_revive)
        dialog.abandon_clicked.connect(self._on_abandon)
        dialog.exec_()

    def _check_revive_coin(self):
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            inventory_data = storage.load_inventory()
            if inventory_data and 'revive_coin' in inventory_data:
                return inventory_data['revive_coin'] > 0
        except Exception as e:
            print(f"[ERROR] Failed to check revive coin: {e}")
        return False

    def _consume_revive_coin(self):
        try:
            from basic_model.secure_storage import SecureStorage
            storage = SecureStorage()
            inventory_data = storage.load_inventory()
            if inventory_data and 'revive_coin' in inventory_data and inventory_data['revive_coin'] > 0:
                inventory_data['revive_coin'] -= 1
                storage.save_inventory(inventory_data)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to consume revive coin: {e}")
        return False

    def _on_revive(self):
        if self._consume_revive_coin():
            self.lives = INITIAL_LIVES
            self.game_over = False
            self.lives_label.setText(f"❤️ x{self.lives}")
            self.info_label_widget.setText("✨ 复活成功！继续游戏吧！")
            self._clear_highlights()
        else:
            self.info_label_widget.setText("❌ 复活币不足！")

    def _on_abandon(self):
        self.close()

    def _check_conflicts(self, row, col, num):
        T = WHITE_THEME
        conflicts = []

        for c in range(9):
            if c != col and self.board[row][c] == num:
                conflicts.append((row, c))

        for r in range(9):
            if r != row and self.board[r][col] == num:
                conflicts.append((r, col))

        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and self.board[r][c] == num:
                    if (r, c) not in conflicts:
                        conflicts.append((r, c))

        for r, c in conflicts:
            is_correct = (self.solution[r][c] == self.board[r][c])
            base_style = self._get_cell_base_style(r, c)
            if not is_correct:
                self.inputs[r][c].setStyleSheet(
                    f"QPushButton#cell_btn {{"
                    f"  background-color: {WHITE_THEME['primary']};"
                    f"  color: {T['conflict']} !important;"
                    f"  font-weight: bold;"
                    f"  {base_style}"
                    f"}}"
                )

    def _on_clear_selected(self):
        if not self.selected_cell or self.game_finished or self.game_over:
            return
        row, col = self.selected_cell
        if self.initial[row][col]:
            self.info_label_widget.setText("⚠️ 初始数字不可清除！")
            return
        self.board[row][col] = 0
        self.notes[row][col].clear()
        self.inputs[row][col].setText("")
        base_style = self._get_cell_base_style(row, col)
        self.inputs[row][col].setStyleSheet(
            f"QPushButton#cell_btn {{"
            f"  background-color: {WHITE_THEME['primary']};"
            f"  color: {WHITE_THEME['text']};"
            f"  {base_style}"
            f"}}"
        )
        self._update_highlights()

    def _toggle_note(self, row, col, num):
        if num in self.notes[row][col]:
            self.notes[row][col].discard(num)
        else:
            self.notes[row][col].add(num)
        self.board[row][col] = 0
        self._render_notes(row, col)

    def _render_notes(self, row, col):
        btn = self.inputs[row][col]
        base_style = self._get_cell_base_style(row, col)
        if self.notes[row][col]:
            small_font = QFont()
            small_font.setPointSize(7)
            btn.setFont(small_font)
            notes_str = "".join(str(n) if n in self.notes[row][col] else " " for n in range(1, 10))
            lines = [notes_str[0:3], notes_str[3:6], notes_str[6:9]]
            btn.setText("\n".join(lines))
            btn.setStyleSheet(
                f"QPushButton#cell_btn {{"
                f"  background-color: {WHITE_THEME['primary']};"
                f"  color: {WHITE_THEME['note_color']};"
                f"  {base_style}"
                f"}}"
            )
        else:
            btn.setText("")
            btn.setToolTip("")
            normal_font = QFont()
            normal_font.setPointSize(11)
            btn.setFont(normal_font)
            btn.setStyleSheet(
                f"QPushButton#cell_btn {{"
                f"  background-color: {WHITE_THEME['primary']};"
                f"  color: {WHITE_THEME['text']};"
                f"  {base_style}"
                f"}}"
            )

    def _clear_highlights(self):
        T = WHITE_THEME
        for i in range(9):
            for j in range(9):
                btn = self.inputs[i][j]
                base_style = self._get_cell_base_style(i, j)
                if self.initial[i][j]:
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['primary']};"
                        f"  color: {T['initial_text']};"
                        f"  font-weight: bold;"
                        f"  {base_style}"
                        f"}}"
                    )
                elif self.board[i][j] != 0:
                    is_correct = (self.solution[i][j] == self.board[i][j])
                    if is_correct:
                        btn.setStyleSheet(
                            f"QPushButton#cell_btn {{"
                            f"  background-color: {T['primary']};"
                            f"  color: {T['fill_text']};"
                            f"  font-weight: bold;"
                            f"  {base_style}"
                            f"}}"
                        )
                    else:
                        btn.setStyleSheet(
                            f"QPushButton#cell_btn {{"
                            f"  background-color: {T['primary']};"
                            f"  color: {T['error']} !important;"
                            f"  font-weight: bold;"
                            f"  {base_style}"
                            f"}}"
                        )
                else:
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['primary']};"
                        f"  color: {T['text']};"
                        f"  {base_style}"
                        f"}}"
                    )
        for nb in self.num_buttons:
            nb.setChecked(False)
        self.selected_number = None

    def _update_highlights(self):
        if not self.selected_cell or self.game_finished or self.game_over:
            return
        T = WHITE_THEME
        sr, sc = self.selected_cell
        sel_val = self.board[sr][sc]

        for i in range(9):
            for j in range(9):
                btn = self.inputs[i][j]
                base_style = self._get_cell_base_style(i, j)
                is_sel = (i == sr and j == sc)
                same_row = (i == sr)
                same_col = (j == sc)
                same_box = (i // 3 == sr // 3 and j // 3 == sc // 3)
                same_num = (sel_val != 0 and self.board[i][j] == sel_val and not (i == sr and j == sc))

                if is_sel:
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['selected_cell']} !important;"
                        f"  color: {T['text']};"
                        f"  {base_style}"
                        f"}}"
                    )
                elif same_row or same_col or same_box:
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['selected_area']} !important;"
                        f"  color: {T['text']};"
                        f"  {base_style}"
                        f"}}"
                    )
                elif same_num:
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['same_num']} !important;"
                        f"  color: white;"
                        f"  {base_style}"
                        f"}}"
                    )

        if sel_val != 0:
            self.selected_number = sel_val
            idx = sel_val - 1
            if idx < len(self.num_buttons):
                self.num_buttons[idx].setChecked(True)

    def _toggle_note_mode(self):
        self.note_mode = not self.note_mode
        if self.note_mode:
            self.info_label_widget.setText("笔记模式：点击数字添加/取消笔记")
        else:
            self.info_label_widget.setText("点击格子，选择数字")

    def _on_difficulty_changed(self, index):
        data = self.difficulty_combo.itemData(index)
        if data:
            self.current_difficulty = data
            self._new_game()

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

        remove_count = DIFFICULTY_SETTINGS.get(self.current_difficulty, DIFFICULTY_SETTINGS['easy'])['remove_count']
        squares = side * side
        positions = list(range(squares))
        random.shuffle(positions)
        for p in positions[:remove_count]:
            self.solution[p // side][p % side] = 0

    def _new_game(self):
        self.board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.initial = [[False]*9 for _ in range(9)]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.selected_number = None
        self.game_finished = False
        self.game_over = False
        self.lives = INITIAL_LIVES

        self._generate_puzzle()
        self._apply_board_style()

        T = WHITE_THEME
        for i in range(9):
            for j in range(9):
                value = self.solution[i][j]
                self.board[i][j] = value
                btn = self.inputs[i][j]
                btn.setEnabled(True)
                btn.setFont(QFont())
                btn.setToolTip("")

                if value != 0:
                    self.initial[i][j] = True
                    btn.setText(str(value))
                    base_style = self._get_cell_base_style(i, j)
                    btn.setStyleSheet(
                        f"QPushButton#cell_btn {{"
                        f"  background-color: {T['primary']};"
                        f"  color: {T['initial_text']};"
                        f"  font-weight: bold;"
                        f"  {base_style}"
                        f"}}"
                    )
                else:
                    btn.setText("")
                    self.board[i][j] = 0

        self.lives_label.setText(f"❤️ x{self.lives}")
        diff_name = DIFFICULTY_SETTINGS[self.current_difficulty]['name']
        self.info_label_widget.setText(f"难度: {diff_name} | 点击格子，选择数字")

    def _check_win(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return False

        for i in range(9):
            if len(set(self.board[i])) != 9:
                return False
        for j in range(9):
            if len(set(self.board[i][j] for i in range(9))) != 9:
                return False
        for bi in range(3):
            for bj in range(3):
                box_nums = set()
                for i in range(bi*3, bi*3+3):
                    for j in range(bj*3, bj*3+3):
                        box_nums.add(self.board[i][j])
                if len(box_nums) != 9:
                    return False

        self.game_finished = True
        diff_name = DIFFICULTY_SETTINGS[self.current_difficulty]['name']
        self.info_label_widget.setText(f"🎉 恭喜！{diff_name}数独完成！")

        score_map = {'easy': 100, 'medium': 200, 'hard': 400}
        bonus = self.lives * 20
        score = score_map.get(self.current_difficulty, 100) + bonus
        self.game_won.emit(score, 0, diff_name)
        return True

    def _get_bg_path(self):
        from basic_model.resource_manager import ResourceManager
        return ResourceManager().get_background_path()

    def closeEvent(self, event):
        event.accept()
