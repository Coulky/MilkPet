extends Control

const GRID_SIZE = 9
const CELL_SIZE = 60

var grid_container: GridContainer
var timer_label: Label
var mistakes_label: Label
var number_buttons: HBoxContainer
var new_game_button: Button
var back_button: Button

var cells: Array = []

signal cell_selected(row, col)
signal number_input(number)
signal new_game_requested
signal back_requested

func _ready():
	_setup_nodes()
	_create_grid_cells()

func _setup_nodes():
	grid_container = get_node("GridContainer")
	timer_label = get_node("TimerLabel")
	mistakes_label = get_node("MistakesLabel")
	number_buttons = get_node("NumberButtons")
	new_game_button = get_node("NewGameButton")
	back_button = get_node("BackButton")

	number_buttons.get_child(0).pressed.connect(_on_number_pressed.bind(1))
	number_buttons.get_child(1).pressed.connect(_on_number_pressed.bind(2))
	number_buttons.get_child(2).pressed.connect(_on_number_pressed.bind(3))
	number_buttons.get_child(3).pressed.connect(_on_number_pressed.bind(4))
	number_buttons.get_child(4).pressed.connect(_on_number_pressed.bind(5))
	number_buttons.get_child(5).pressed.connect(_on_number_pressed.bind(6))
	number_buttons.get_child(6).pressed.connect(_on_number_pressed.bind(7))
	number_buttons.get_child(7).pressed.connect(_on_number_pressed.bind(8))
	number_buttons.get_child(8).pressed.connect(_on_number_pressed.bind(9))

	new_game_button.pressed.connect(_on_new_game_pressed)
	back_button.pressed.connect(_on_back_pressed)

func _create_grid_cells():
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell = Button.new()
			cell.custom_minimum_size = Vector2(CELL_SIZE, CELL_SIZE)
			cell.add_theme_font_size_override("font_size", 28)
			cell.pressed.connect(_on_cell_pressed.bind(i, j))
			grid_container.add_child(cell)
			cells.append(cell)

func update_display(grid: SudokuGrid, selected: Vector2):
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell_index = i * GRID_SIZE + j
			var cell = cells[cell_index]
			var value = grid.get_number(i, j)

			if value == 0:
				cell.text = ""
				cell.add_theme_color_override("font_color", Color.WHITE)
			else:
				cell.text = str(value)
				if grid.is_original_cell(i, j):
					cell.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
				else:
					cell.add_theme_color_override("font_color", Color(0.3, 0.7, 1.0))

			if selected == Vector2(i, j):
				cell.add_theme_color_override("font_color", Color.YELLOW)

func update_timer(seconds: int):
	var minutes = seconds / 60
	var secs = seconds % 60
	timer_label.text = "时间: " + str(minutes) + ":" + str(secs).pad_zeros(2)

func update_mistakes(count: int):
	mistakes_label.text = "错误: " + str(count)

func set_buttons_enabled(enabled: bool):
	number_buttons.get_child(0).disabled = not enabled
	number_buttons.get_child(1).disabled = not enabled
	number_buttons.get_child(2).disabled = not enabled
	number_buttons.get_child(3).disabled = not enabled
	number_buttons.get_child(4).disabled = not enabled
	number_buttons.get_child(5).disabled = not enabled
	number_buttons.get_child(6).disabled = not enabled
	number_buttons.get_child(7).disabled = not enabled
	number_buttons.get_child(8).disabled = not enabled

func _on_cell_pressed(row: int, col: int):
	cell_selected.emit(row, col)

func _on_number_pressed(number: int):
	number_input.emit(number)

func _on_new_game_pressed():
	new_game_requested.emit()

func _on_back_pressed():
	back_requested.emit()
