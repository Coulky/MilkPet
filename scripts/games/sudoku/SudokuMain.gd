extends Control

var sudoku_grid: SudokuGrid
var sudoku_generator: SudokuGenerator
var sudoku_ui: SudokuUI

var selected_cell: Vector2 = Vector2(-1, -1)
var is_running: bool = false
var timer_seconds: int = 0

func _ready():
	sudoku_grid = SudokuGrid.new()
	sudoku_generator = SudokuGenerator.new()
	sudoku_grid.init()
	add_child(sudoku_grid)
	add_child(sudoku_generator)

	sudoku_ui = $SudokuUI
	sudoku_ui.cell_selected.connect(_on_cell_selected)
	sudoku_ui.number_input.connect(_on_number_input)
	sudoku_ui.new_game_requested.connect(_on_new_game)
	sudoku_ui.back_requested.connect(_on_back)

	start_new_game()

func start_new_game():
	timer_seconds = 0
	selected_cell = Vector2(-1, -1)
	is_running = true

	var game_data = sudoku_generator.generate()
	sudoku_grid.init()
	sudoku_grid.load_game(game_data)

	sudoku_ui.update_mistakes(0)
	sudoku_ui.update_timer(0)
	sudoku_ui.update_display(sudoku_grid, selected_cell)
	sudoku_ui.set_buttons_enabled(true)

	GameTimer.timer_init("Sudoku", 1.0, false)
	GameTimer.timer_timeout.connect(_on_timer_tick)

func _on_cell_selected(row: int, col: int):
	if not is_running:
		return
	if sudoku_grid.is_original_cell(row, col):
		return

	selected_cell = Vector2(row, col)
	sudoku_ui.update_display(sudoku_grid, selected_cell)

func _on_number_input(number: int):
	if not is_running or selected_cell == Vector2(-1, -1):
		return

	var row = int(selected_cell.x)
	var col = int(selected_cell.y)

	if sudoku_grid.set_number(row, col, number):
		if sudoku_grid.is_complete():
			_on_game_complete()
	else:
		sudoku_ui.update_mistakes(sudoku_grid.get_mistakes())
		if sudoku_grid.get_mistakes() >= 3:
			_on_game_over()

	sudoku_ui.update_display(sudoku_grid, selected_cell)

func _on_timer_tick():
	if is_running:
		timer_seconds += 1
		sudoku_ui.update_timer(timer_seconds)

func _on_new_game():
	GameTimer.timer_clear()
	start_new_game()

func _on_back():
	GameTimer.timer_clear()
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")

func _on_game_complete():
	is_running = false
	sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()
	print("Game Complete!")

func _on_game_over():
	is_running = false
	sudoku_ui.set_buttons_enabled(false)
	GameTimer.timer_clear()
	print("Game Over!")

func _exit_tree():
	GameTimer.timer_clear()
