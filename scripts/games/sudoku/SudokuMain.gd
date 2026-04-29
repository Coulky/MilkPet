extends Control

const SudokuGridScript = preload("res://scripts/games/sudoku/SudokuGrid.gd")
const SudokuGeneratorScript = preload("res://scripts/games/sudoku/SudokuGenerator.gd")

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

	var sudoku_ui = $SudokuUI
	sudoku_ui.cell_selected.connect(_on_cell_selected)
	sudoku_ui.number_input.connect(_on_number_input)
	sudoku_ui.new_game_requested.connect(_on_new_game)
	sudoku_ui.back_requested.connect(_on_back)
	sudoku_ui.note_mode_toggled.connect(_on_note_mode_toggled)
	sudoku_ui.hint_requested.connect(_on_hint_requested)
	sudoku_ui.auto_notes_requested.connect(_on_auto_notes_requested)

	if SaveData.has_cached_game("sudoku"):
		load_cached_game()
	else:
		start_new_game()

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

	var sudoku_ui = $SudokuUI
	sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
	sudoku_ui.update_timer(0)
	sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
	sudoku_ui.set_buttons_enabled(true)
	sudoku_ui.set_note_mode_active(note_mode)

	GameTimer.timer_init("Sudoku", 1.0, false)
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

	var sudoku_ui = $SudokuUI
	sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
	sudoku_ui.update_timer(timer_seconds)
	sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
	sudoku_ui.set_buttons_enabled(true)
	sudoku_ui.set_note_mode_active(note_mode)

	GameTimer.timer_init("Sudoku", 1.0, false)
	GameTimer.timer_timeout.connect(_on_timer_tick)

func _on_cell_selected(row: int, col: int):
	if not is_running:
		return

	selected_cell = Vector2(row, col)
	selected_number = sudoku_grid.get_number(row, col)

	var sudoku_ui = $SudokuUI
	sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)

func _on_number_input(number: int):
	if not is_running or selected_cell == Vector2(-1, -1):
		return

	var row = int(selected_cell.x)
	var col = int(selected_cell.y)
	var sudoku_ui = $SudokuUI

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
			sudoku_ui.update_lives(sudoku_grid.get_incorrect_count())
			if sudoku_grid.get_incorrect_count() <= 0:
				_on_game_over()

	sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
	save_game_state()

func _on_timer_tick():
	if is_running:
		timer_seconds += 1
		var sudoku_ui = $SudokuUI
		sudoku_ui.update_timer(timer_seconds)

		var hint_cell = sudoku_grid.get_hint_cell()
		if hint_cell and Time.get_ticks_msec() - hint_cell.time > 1000:
			sudoku_grid.clear_hint_cell()
			sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)

func _on_note_mode_toggled(active: bool):
	note_mode = active
	var sudoku_ui = $SudokuUI
	sudoku_ui.set_note_mode_active(note_mode)

func _on_hint_requested():
	if not is_running:
		return

	if sudoku_grid.give_hint():
		var sudoku_ui = $SudokuUI
		sudoku_ui.update_display(sudoku_grid, selected_cell, note_mode)
		save_game_state()

		var result = sudoku_grid.check_sudoku()
		if result.success:
			_on_game_complete(result.message)

func _on_auto_notes_requested():
	if not is_running:
		return

	sudoku_grid.generate_auto_notes()
	var sudoku_ui = $SudokuUI
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

func _on_back():
	save_game_state()
	GameTimer.timer_clear()
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")

func _on_game_complete(message: String):
	is_running = false
	var sudoku_ui = $SudokuUI
	sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()
	
	if current_puzzle_id != "":
		sudoku_generator.mark_completed(current_puzzle_id, current_level)
	
	SaveData.clear_cached_game_on_disk("sudoku")
	SaveData.clear_game_cache()
	print(message)
	sudoku_ui.show_message(message)

func _on_game_over():
	is_running = false
	var sudoku_ui = $SudokuUI
	sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()
	SaveData.clear_cached_game_on_disk("sudoku")
	SaveData.clear_game_cache()
	print("游戏结束！")
	sudoku_ui.show_message("游戏结束！")

func _exit_tree():
	if is_running:
		save_game_state()
	GameTimer.timer_clear()
