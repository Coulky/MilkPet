extends Control

const SudokuGridScript = preload("res://scripts/games/sudoku/SudokuGrid.gd")
const SudokuGeneratorScript = preload("res://scripts/games/sudoku/SudokuGenerator.gd")
const GameButtonFactoryScript = preload("res://scripts/common/GameButtonFactory.gd")

var sudoku_grid: Node
var sudoku_generator: Node

var selected_cell: Vector2 = Vector2(-1, -1)
var selected_number: int = 0
var note_mode: bool = false
var is_running: bool = false
var timer_seconds: int = 0
var current_level: String = "easy"
var current_puzzle_id: String = ""

func _ready():
	sudoku_grid = SudokuGridScript.new()
	sudoku_generator = SudokuGeneratorScript.new()
	add_child(sudoku_grid)
	add_child(sudoku_generator)

	_setup_buttons()

	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.cell_selected.connect(_on_cell_selected)
		sudoku_ui.number_input.connect(_on_number_input)
		sudoku_ui.new_game_requested.connect(_on_new_game)
		sudoku_ui.note_mode_toggled.connect(_on_note_mode_toggled)
		sudoku_ui.hint_requested.connect(_on_hint_requested)
		sudoku_ui.auto_notes_requested.connect(_on_auto_notes_requested)

	if SaveData.has_cached_game("sudoku"):
		load_cached_game()
	else:
		start_new_game()

func _setup_buttons():
	var window_height = get_window().size.y
	var btn_size = int(window_height * 0.15)
	
	var left_panel = get_node_or_null("SudokuUI/MainContainer/LeftPanel")
	var action_buttons = get_node_or_null("SudokuUI/MainContainer/LeftPanel/ActionButtons")
	
	if left_panel:
		GameButtonFactoryScript.create_simple_button(left_panel, "BackButton", "res://assets/images/back.png", _on_back)
		var back_btn = left_panel.get_node_or_null("BackButton")
		if back_btn:
			back_btn.custom_minimum_size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(left_panel, "RestartButton", "res://assets/images/restart.png", "重开", _on_restart)
		var restart_container = left_panel.get_node_or_null("RestartButtonContainer")
		if restart_container:
			restart_container.custom_minimum_size = Vector2(btn_size, btn_size)
	
	if action_buttons:
		GameButtonFactoryScript.create_button(action_buttons, "NoteModeButton", "res://assets/images/restart.png", "笔记", _on_note_mode_button)
		var note_mode_container = action_buttons.get_node_or_null("NoteModeButtonContainer")
		if note_mode_container:
			note_mode_container.custom_minimum_size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(action_buttons, "HintButton", "res://assets/images/restart.png", "提示", _on_hint_requested)
		var hint_container = action_buttons.get_node_or_null("HintButtonContainer")
		if hint_container:
			hint_container.custom_minimum_size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(action_buttons, "AutoNotesButton", "res://assets/images/restart.png", "自动笔记", _on_auto_notes_requested)
		var auto_notes_container = action_buttons.get_node_or_null("AutoNotesButtonContainer")
		if auto_notes_container:
			auto_notes_container.custom_minimum_size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(action_buttons, "NewGameButton", "res://assets/images/restart.png", "新游戏", _on_new_game)
		var new_game_container = action_buttons.get_node_or_null("NewGameButtonContainer")
		if new_game_container:
			new_game_container.custom_minimum_size = Vector2(btn_size, btn_size)

func start_new_game(level: String = "easy"):
	timer_seconds = 0
	selected_cell = Vector2(-1, -1)
	selected_number = 0
	note_mode = false
	is_running = true
	current_level = level

	var game_data = sudoku_generator.generate(level)
	sudoku_grid.init()
	sudoku_grid.load_game(game_data)

	current_puzzle_id = game_data.id

	SaveData.init_game_cache("sudoku", level, {
		"grid": game_data.grid.duplicate(true),
		"original": game_data.original.duplicate(true),
		"id": game_data.id
	})

	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
		sudoku_ui.update_timer(0)
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
		sudoku_ui.set_buttons_enabled(true)
		sudoku_ui.set_note_mode_active(note_mode)

	GameTimer.timer_init("Sudoku", 1.0, false)
	if GameTimer.timer_timeout.is_connected(_on_timer_tick):
		GameTimer.timer_timeout.disconnect(_on_timer_tick)
	GameTimer.timer_timeout.connect(_on_timer_tick)

func load_cached_game():
	SaveData.load_game_cache("sudoku")
	var cached_data = SaveData.get_cached_game_data()

	timer_seconds = cached_data.get("timer_seconds", 0)
	current_level = cached_data.get("difficulty", "easy")
	selected_cell = Vector2(-1, -1)
	selected_number = 0
	note_mode = false
	is_running = true

	var current_state = cached_data.get("current_state", {})
	var initial_data = cached_data.get("initial_data", {})

	sudoku_grid.init()

	if "grid" in current_state and "original" in current_state:
		sudoku_grid.load_game({
			"grid": current_state.grid,
			"original": current_state.original
		})
	elif "grid" in initial_data and "original" in initial_data:
		sudoku_grid.load_game({
			"grid": initial_data.grid,
			"original": initial_data.original
		})

	if "incorrect_count" in current_state:
		sudoku_grid.incorrect_count = current_state.incorrect_count

	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
		sudoku_ui.update_timer(timer_seconds)
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
		sudoku_ui.set_buttons_enabled(true)
		sudoku_ui.set_note_mode_active(note_mode)

	GameTimer.timer_init("Sudoku", 1.0, false)
	if GameTimer.timer_timeout.is_connected(_on_timer_tick):
		GameTimer.timer_timeout.disconnect(_on_timer_tick)
	GameTimer.timer_timeout.connect(_on_timer_tick)

func _on_cell_selected(row: int, col: int):
	if not is_running:
		return

	selected_cell = Vector2(row, col)
	selected_number = sudoku_grid.get_number(row, col)

	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)

func _on_number_input(number: int):
	if not is_running or selected_cell == Vector2(-1, -1):
		return

	var row = int(selected_cell.x)
	var col = int(selected_cell.y)
	var sudoku_ui = get_node_or_null("SudokuUI")

	if sudoku_grid.is_original_cell(row, col):
		return

	if note_mode:
		sudoku_grid.set_note(row, col, number)
	else:
		if sudoku_grid.set_number(row, col, number):
			var result = sudoku_grid.check_sudoku()
			if result.success:
				_on_game_complete(result.message)
		else:
			if sudoku_ui:
				sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
			if sudoku_grid.get_incorrect_count() <= 0:
				_on_game_over()

	if sudoku_ui:
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
	save_game_state()

func _on_timer_tick():
	if is_running:
		timer_seconds += 1
		var sudoku_ui = get_node_or_null("SudokuUI")
		if sudoku_ui:
			sudoku_ui.update_timer(timer_seconds)

		var hint_cell = sudoku_grid.get_hint_cell()
		if hint_cell and Time.get_ticks_msec() - hint_cell.time > 1000:
			sudoku_grid.clear_hint_cell()
			if sudoku_ui:
				sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)

func _on_note_mode_toggled(active: bool):
	note_mode = active
	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.set_note_mode_active(note_mode)

func _on_note_mode_button():
	_on_note_mode_toggled(!note_mode)

func _on_hint_requested():
	if not is_running:
		return

	if sudoku_grid.give_hint():
		var sudoku_ui = get_node_or_null("SudokuUI")
		if sudoku_ui:
			sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
		save_game_state()

		var result = sudoku_grid.check_sudoku()
		if result.success:
			_on_game_complete(result.message)

func _on_auto_notes_requested():
	if not is_running:
		return

	sudoku_grid.generate_auto_notes()
	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)

func save_game_state():
	if not is_running:
		return

	SaveData.update_game_cache({
		"grid": sudoku_grid.current_sudoku.duplicate(true),
		"original": sudoku_grid.original_sudoku.duplicate(true),
		"incorrect_count": sudoku_grid.get_incorrect_count(),
		"timer_seconds": timer_seconds
	})
	SaveData.save_game_cache_to_disk()

func _on_new_game():
	SaveData.clear_game_cache()
	SaveData.clear_cached_game_on_disk("sudoku")
	GameTimer.timer_clear()
	start_new_game(current_level)

func _on_restart():
	_on_new_game()

func _on_back():
	save_game_state()
	GameTimer.timer_clear()
	get_tree().change_scene_to_file("res://scenes/GameIndex.tscn")

func _on_game_complete(message: String):
	is_running = false
	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()

	if current_puzzle_id != "":
		sudoku_generator.mark_completed(current_puzzle_id, current_level)

	SaveData.clear_cached_game_on_disk("sudoku")
	SaveData.clear_game_cache()
	print(message)
	if sudoku_ui:
		sudoku_ui.show_message(message)

func _on_game_over():
	is_running = false
	var sudoku_ui = get_node_or_null("SudokuUI")
	if sudoku_ui:
		sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()
	SaveData.clear_cached_game_on_disk("sudoku")
	SaveData.clear_game_cache()
	print("游戏结束！")
	if sudoku_ui:
		sudoku_ui.show_message("游戏结束！")

func _exit_tree():
	if is_running:
		save_game_state()
	GameTimer.timer_clear()

# 键盘输入支持
func _input(event: InputEvent):
	if not is_running:
		return
	
	if event is InputEventKey:
		if event.pressed:
			# 数字键 1-9
			for i in range(1, 10):
				if event.keycode == KEY_1 + i - 1:
					if selected_cell != Vector2(-1, -1):
						_on_number_input(i)
						return
			
			# 删除键
			if event.keycode == KEY_DELETE or event.keycode == KEY_BACKSPACE:
				if selected_cell != Vector2(-1, -1):
					var row = int(selected_cell.x)
					var col = int(selected_cell.y)
					if not sudoku_grid.is_original_cell(row, col):
						sudoku_grid.current_sudoku[row][col] = 0
						var sudoku_ui = get_node_or_null("SudokuUI")
						if sudoku_ui:
							sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
						save_game_state()
				return
			
			# 方向键
			if selected_cell != Vector2(-1, -1):
				var row = int(selected_cell.x)
				var col = int(selected_cell.y)
				
				match event.keycode:
					KEY_UP:
						if row > 0:
							row -= 1
					KEY_DOWN:
						if row < 8:
							row += 1
					KEY_LEFT:
						if col > 0:
							col -= 1
					KEY_RIGHT:
						if col < 8:
							col += 1
					_:
						return
				
				selected_cell = Vector2(row, col)
				selected_number = sudoku_grid.get_number(row, col)
				var sudoku_ui = get_node_or_null("SudokuUI")
				if sudoku_ui:
					sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
