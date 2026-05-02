extends Control

const GRID_SIZE = 9
var cell_size: int = 50

var grid_container: GridContainer
var timer_label: Label
var lives_label: Label
var number_buttons: HBoxContainer
var message_dialog: Label

var cells: Array = []
var _note_mode_active: bool = false
var _selected_number: int = -1

# 数字图片资源
var number_textures: Dictionary = {}

signal cell_selected(row, col)
signal number_input(number)
signal new_game_requested
signal note_mode_toggled(active)
signal hint_requested
signal auto_notes_requested

func _ready():
	_load_number_textures()
	_setup_nodes()
	_create_grid_cells()
	_update_grid_size()

func _notification(what):
	if what == NOTIFICATION_RESIZED:
		call_deferred("_update_grid_size")

func _load_number_textures():
	pass

func _setup_nodes():
	grid_container = get_node("MainContainer/CenterArea/GridContainer")
	timer_label = get_node("MainContainer/LeftPanel/TimerLabel")
	lives_label = get_node("MainContainer/LeftPanel/LivesLabel")
	number_buttons = get_node("MainContainer/CenterArea/NumberButtons")
	message_dialog = get_node("MessageDialog")

	message_dialog.visible = false

	if number_buttons and number_buttons.get_child_count() >= 9:
		for i in range(9):
			number_buttons.get_child(i).pressed.connect(_on_number_pressed.bind(i + 1))

func _update_grid_size():
	var window_height = get_window().size.y
	cell_size = int(window_height * 0.075)

	if cells.size() == 0:
		return

	for i in range(cells.size()):
		cells[i].custom_minimum_size = Vector2(cell_size, cell_size)

		var click_area = cells[i].get_node("ClickArea")
		var number_texture = click_area.get_node("NumberTexture")
		number_texture.custom_minimum_size = Vector2(cell_size - 10, cell_size - 10)

		var style = StyleBoxFlat.new()
		style.border_width_left = 1
		style.border_width_right = 1
		style.border_width_bottom = 1
		style.border_width_top = 1
		var row = int(i / float(GRID_SIZE))
		var col = i % GRID_SIZE
		if row % 3 == 0:
			style.border_width_top = max(2, int(cell_size * 0.05))
		if col % 3 == 0:
			style.border_width_left = max(2, int(cell_size * 0.05))
		if row == 8:
			style.border_width_bottom = max(2, int(cell_size * 0.05))
		if col == 8:
			style.border_width_right = max(2, int(cell_size * 0.05))
		style.border_color = Color.BLACK
		style.bg_color = Color.WHITE
		cells[i].add_theme_stylebox_override("panel", style)

	if number_buttons and number_buttons.get_child_count() >= 9:
		for i in range(9):
			var btn = number_buttons.get_child(i)
			btn.custom_minimum_size = Vector2(cell_size, cell_size)
			btn.expand_icon = true

func _create_grid_cells():
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell = PanelContainer.new()
			cell.custom_minimum_size = Vector2(cell_size, cell_size)
			cell.mouse_filter = Control.MOUSE_FILTER_STOP
			
			var style = StyleBoxFlat.new()
			style.border_width_left = 1
			style.border_width_right = 1
			style.border_width_bottom = 1
			style.border_width_top = 1
			if i % 3 == 0:
				style.border_width_top = 3
			if j % 3 == 0:
				style.border_width_left = 3
			if i == 8:
				style.border_width_bottom = 3
			if j == 8:
				style.border_width_right = 3
			style.border_color = Color.BLACK
			style.bg_color = Color.WHITE
			cell.add_theme_stylebox_override("panel", style)
			
			var area = Control.new()
			area.name = "ClickArea"
			area.mouse_filter = Control.MOUSE_FILTER_STOP
			area.layout_mode = 1
			area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			area.size_flags_vertical = Control.SIZE_EXPAND_FILL
			area.gui_input.connect(_on_cell_gui_input.bind(i, j))
			cell.add_child(area)
			
			var texture_rect = TextureRect.new()
			texture_rect.name = "NumberTexture"
			texture_rect.layout_mode = 1
			texture_rect.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			texture_rect.size_flags_vertical = Control.SIZE_EXPAND_FILL
			texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			texture_rect.custom_minimum_size = Vector2(cell_size - 10, cell_size - 10)
			texture_rect.visible = false

			var note_grid = GridContainer.new()
			note_grid.name = "NoteGrid"
			note_grid.layout_mode = 1
			note_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			note_grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
			note_grid.columns = 3
			note_grid.custom_minimum_size = Vector2(cell_size - 6, cell_size - 6)
			note_grid.visible = false
			for n in range(1, 10):
				var note_texture = TextureRect.new()
				note_texture.name = "Note" + str(n)
				note_texture.layout_mode = 1
				note_texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				note_texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				note_texture.custom_minimum_size = Vector2(20, 20)
				note_texture.texture = number_textures.get(n)
				if note_texture.texture:
					note_texture.modulate = Color(0.5, 0.5, 0.5)
				note_grid.add_child(note_texture)

			var color_rect = ColorRect.new()
			color_rect.name = "ColorRect"
			color_rect.layout_mode = 1
			color_rect.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			color_rect.size_flags_vertical = Control.SIZE_EXPAND_FILL
			color_rect.color = Color.TRANSPARENT

			area.add_child(color_rect)
			area.add_child(texture_rect)
			area.add_child(note_grid)
			
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
			
			var number_texture = cell.get_node("ClickArea/NumberTexture")
			var note_grid = cell.get_node("ClickArea/NoteGrid")
			var color_rect = cell.get_node("ClickArea/ColorRect")

			color_rect.color = Color.TRANSPARENT

			if selected == Vector2(i, j):
				color_rect.color = Color(0.3, 0.5, 0.8, 0.3)

			if hint_cell and hint_cell.row == i and hint_cell.col == j:
				color_rect.color = Color(1.0, 1.0, 0.5, 0.5)

			if _selected_number != -1 and value == _selected_number:
				color_rect.color = Color(0.8, 0.8, 0.3, 0.4)

			if value == 0:
				number_texture.visible = false
				if notes.size() > 0 and note_mode_active:
					note_grid.visible = true
					for n in range(1, 10):
						var note_texture = note_grid.get_node("Note" + str(n))
						note_texture.visible = notes.has(n)
				else:
					note_grid.visible = false
			else:
				note_grid.visible = false
				if value in number_textures:
					number_texture.texture = number_textures[value]
					number_texture.visible = true
					if grid.is_original_cell(i, j):
						number_texture.modulate = Color.WHITE
					else:
						number_texture.modulate = Color(0.2, 0.5, 0.8)
				else:
					number_texture.visible = false

func update_display_with_number_highlight():
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			var cell_index = i * GRID_SIZE + j
			var cell = cells[cell_index]
			var color_rect = cell.get_node("ClickArea/ColorRect")
			
			if _selected_number != -1:
				color_rect.color = Color(0.8, 0.8, 0.3, 0.4)
			else:
				color_rect.color = Color.TRANSPARENT

func update_timer(seconds: int):
	var minutes = int(seconds / 60.0)
	var secs = seconds % 60
	timer_label.text = "时间: " + str(minutes).pad_zeros(2) + ":" + str(secs).pad_zeros(2)

func update_lives(count: int):
	lives_label.text = "生命: " + "x" + str(count)

func set_buttons_enabled(enabled: bool):
	if number_buttons and number_buttons.get_child_count() >= 9:
		for i in range(9):
			number_buttons.get_child(i).disabled = not enabled
	
	var note_btn = get_node_or_null("MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer/NoteModeButton")
	var hint_btn = get_node_or_null("MainContainer/LeftPanel/ActionButtons/HintButtonContainer/HintButton")
	var auto_notes_btn = get_node_or_null("MainContainer/LeftPanel/ActionButtons/AutoNotesButtonContainer/AutoNotesButton")
	if note_btn: note_btn.disabled = not enabled
	if hint_btn: hint_btn.disabled = not enabled
	if auto_notes_btn: auto_notes_btn.disabled = not enabled

func set_note_mode_active(active: bool):
	_note_mode_active = active
	var note_btn = get_node_or_null("MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer/NoteModeButton")
	if note_btn:
		if active:
			note_btn.add_theme_color_override("background_color", Color(0.8, 0.6, 0.2))
		else:
			note_btn.remove_theme_color_override("background_color")

func show_message(message: String):
	message_dialog.text = message
	message_dialog.visible = true
	get_tree().create_timer(3.0).timeout.connect(_hide_message)

func _hide_message():
	message_dialog.visible = false

func _on_cell_gui_input(event: InputEvent, row: int, col: int):
	if event is InputEventMouseButton and event.pressed:
		_selected_number = -1
		cell_selected.emit(row, col)

func _on_number_pressed(number: int):
	_selected_number = number
	number_input.emit(number)
	update_display_with_number_highlight()

func _on_new_game_pressed():
	new_game_requested.emit()

func _on_note_mode_pressed():
	_note_mode_active = not _note_mode_active
	note_mode_toggled.emit(_note_mode_active)

func _on_hint_pressed():
	hint_requested.emit()

func _on_auto_notes_requested():
	auto_notes_requested.emit()
