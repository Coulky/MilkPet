extends Control

const GRID_SIZE = 9
const CELL_SIZE = 60

var grid_container: GridContainer
var timer_label: Label
var lives_label: Label
var number_buttons: HBoxContainer
var new_game_button: Button
var back_button: Button
var note_mode_button: Button
var hint_button: Button
var auto_notes_button: Button
var message_dialog: Label

var cells: Array = []

signal cell_selected(row, col)
signal number_input(number)
signal new_game_requested
signal back_requested
signal note_mode_toggled(active)
signal hint_requested
signal auto_notes_requested

func _ready():
	_setup_nodes()
	_create_grid_cells()

func _setup_nodes():
	grid_container = get_node("GridContainer")
	timer_label = get_node("TimerLabel")
	lives_label = get_node("LivesLabel")
	number_buttons = get_node("NumberButtons")
	new_game_button = get_node("NewGameButton")
	back_button = get_node("BackButton")
	note_mode_button = get_node("ActionButtons/NoteModeButton")
	hint_button = get_node("ActionButtons/HintButton")
	auto_notes_button = get_node("ActionButtons/AutoNotesButton")
	message_dialog = get_node("MessageDialog")

	message_dialog.visible = false

	for i in range(9):
		number_buttons.get_child(i).pressed.connect(_on_number_pressed.bind(i + 1))

	new_game_button.pressed.connect(_on_new_game_pressed)
	back_button.pressed.connect(_on_back_pressed)
	note_mode_button.pressed.connect(_on_note_mode_pressed)
	hint_button.pressed.connect(_on_hint_pressed)
	auto_notes_button.pressed.connect(_on_auto_notes_pressed)

func _create_grid_cells():
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell = Button.new()
			cell.custom_minimum_size = Vector2(CELL_SIZE, CELL_SIZE)
			cell.add_theme_font_size_override("font_size", 24)
			cell.pressed.connect(_on_cell_pressed.bind(i, j))

			if i % 3 == 0:
				cell.add_theme_color_override("border_top_color", Color.BLACK)
				cell.add_theme_constant_override("border_top_width", 3)
			if j % 3 == 0:
				cell.add_theme_color_override("border_left_color", Color.BLACK)
				cell.add_theme_constant_override("border_left_width", 3)
			if i == 8:
				cell.add_theme_color_override("border_bottom_color", Color.BLACK)
				cell.add_theme_constant_override("border_bottom_width", 3)
			if j == 8:
				cell.add_theme_color_override("border_right_color", Color.BLACK)
				cell.add_theme_constant_override("border_right_width", 3)

			grid_container.add_child(cell)
			cells.append(cell)

func update_display(grid: Node, selected: Vector2, note_mode_active: bool):
	var hint_cell = grid.get_hint_cell()

	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell_index = i * GRID_SIZE + j
			var cell = cells[cell_index]
			var value = grid.get_number(i, j)
			var notes = grid.get_notes(i, j)

			cell.remove_theme_color_override("font_color")
			cell.remove_theme_color_override("custom_colors/font_color")
			cell.remove_theme_color_override("background_color")
			cell.remove_theme_color_override("custom_colors/background_color")

			if selected == Vector2(i, j):
				cell.add_theme_color_override("background_color", Color(0.3, 0.5, 0.8))

			if hint_cell and hint_cell.row == i and hint_cell.col == j:
				cell.add_theme_color_override("background_color", Color(1.0, 1.0, 0.5))

			if value == 0:
				if notes.size() > 0 and note_mode_active:
					cell.text = notes.map(func(n): return str(n)).join(", ")
					cell.add_theme_font_size_override("font_size", 12)
					cell.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
				else:
					cell.text = ""
					cell.add_theme_font_size_override("font_size", 24)
			else:
				cell.text = str(value)
				cell.add_theme_font_size_override("font_size", 24)
				if grid.is_original_cell(i, j):
					cell.add_theme_color_override("font_color", Color(0.1, 0.1, 0.1))
				else:
					cell.add_theme_color_override("font_color", Color(0.2, 0.5, 0.8))

func update_timer(seconds: int):
	var minutes = int(seconds / 60.0)
	var secs = seconds % 60
	timer_label.text = "时间: " + str(minutes).pad_zeros(2) + ":" + str(secs).pad_zeros(2)

func update_lives(count: int):
	lives_label.text = "生命: " + "x" + str(count)

func set_buttons_enabled(enabled: bool):
	for i in range(9):
		number_buttons.get_child(i).disabled = not enabled
	note_mode_button.disabled = not enabled
	hint_button.disabled = not enabled
	auto_notes_button.disabled = not enabled

func set_note_mode_active(active: bool):
	if active:
		note_mode_button.add_theme_color_override("background_color", Color(0.8, 0.6, 0.2))
	else:
		note_mode_button.remove_theme_color_override("background_color")

func show_message(message: String):
	message_dialog.text = message
	message_dialog.visible = true
	get_tree().create_timer(3.0).timeout.connect(_hide_message)

func _hide_message():
	message_dialog.visible = false

func _on_cell_pressed(row: int, col: int):
	cell_selected.emit(row, col)

func _on_number_pressed(number: int):
	number_input.emit(number)

func _on_new_game_pressed():
	new_game_requested.emit()

func _on_back_pressed():
	back_requested.emit()

func _on_note_mode_pressed():
	note_mode_toggled.emit(not note_mode_button.has_theme_color_override("background_color"))

func _on_hint_pressed():
	hint_requested.emit()

func _on_auto_notes_pressed():
	auto_notes_requested.emit()
