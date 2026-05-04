extends Control

var current_grid_size: int = 4
var cell_size: int = 100

var grid_container: GridContainer
var move_count_label: Label
var timer_label: Label
var message_dialog: Control

var tile_buttons: Array = []
var number_textures: Dictionary = {}
var scaled_textures: Dictionary = {}
var _is_initializing: bool = false
var _last_viewport_size: Vector2 = Vector2.ZERO
var _check_resize_timer: float = 0.0

signal tile_clicked(row, col)
signal grid_size_changed(grid_size)
signal message_dialog_clicked

func _ready():
	_load_number_textures()
	_setup_nodes()
	call_deferred("_update_layout")

func _process(delta):
	_check_resize_timer += delta
	if _check_resize_timer >= 0.5:
		_check_resize_timer = 0.0
		if is_inside_tree():
			var viewport = get_viewport()
			if viewport:
				var current_size = viewport.get_visible_rect().size
				if current_size != _last_viewport_size and current_size.x > 0 and current_size.y > 0:
					_last_viewport_size = current_size
					call_deferred("_update_layout")

func _notification(what):
	if what == NOTIFICATION_RESIZED:
		call_deferred("_update_layout")

func _load_number_textures():
	for i in range(1, 26):
		var path = "res://assets/images/sliding_puzzle/" + str(i) + ".png"
		var texture = load(path)
		if texture:
			number_textures[i] = texture

func _precache_scaled_textures():
	scaled_textures.clear()
	
	for value in number_textures.keys():
		var original_texture = number_textures[value]
		if original_texture:
			var img = original_texture.get_image()
			img.resize(cell_size, cell_size, Image.INTERPOLATE_NEAREST)
			scaled_textures[value] = ImageTexture.create_from_image(img)

func _setup_nodes():
	grid_container = get_node_or_null("GridContainer")
	move_count_label = get_node_or_null("TopPanel/MoveCountLabel")
	timer_label = get_node_or_null("TopPanel/TimerLabel")
	message_dialog = get_node_or_null("MessageDialog")
	
	if message_dialog:
		message_dialog.gui_input.connect(_on_message_dialog_input)

func _update_layout():
	if not is_inside_tree():
		return
	
	_is_initializing = true
	
	var viewport = get_viewport()
	if not viewport:
		_is_initializing = false
		return
	
	var viewport_size = viewport.get_visible_rect().size
	_last_viewport_size = viewport_size
	if viewport_size.x == 0 or viewport_size.y == 0:
		_is_initializing = false
		call_deferred("_update_layout")
		return
	
	var board_size = viewport_size.y * 0.5
	cell_size = int(board_size / current_grid_size) - 5
	
	if cell_size < 40:
		cell_size = 40
	elif cell_size > 100:
		cell_size = 100
	
	_create_grid_tiles()
	_precache_scaled_textures()
	
	await get_tree().process_frame
	_position_elements(viewport_size)
	
	_is_initializing = false

func _position_elements(viewport_size: Vector2):
	var top_panel = get_node_or_null("TopPanel")
	if top_panel:
		top_panel.position = Vector2((viewport_size.x - top_panel.size.x) / 2.0, 20)
	
	if grid_container and grid_container.get_child_count() > 0:
		var gap = 5
		var grid_width = current_grid_size * (cell_size + gap) - gap
		var grid_height = current_grid_size * (cell_size + gap) - gap
		grid_container.size = Vector2(grid_width, grid_height)
		grid_container.position = Vector2(
			(viewport_size.x - grid_width) / 2.0,
			80 + (viewport_size.y * 0.5 - grid_height) / 2.0
		)
	
	var left_panel = get_node_or_null("LeftPanel")
	if left_panel:
		left_panel.position = Vector2(20, (viewport_size.y - left_panel.size.y) / 2.0)
	
	if message_dialog:
		message_dialog.position = Vector2(
			(viewport_size.x - message_dialog.size.x) / 2.0,
			(viewport_size.y - message_dialog.size.y) / 2.0
		)

func _create_grid_tiles():
	if not grid_container:
		return
	
	for child in grid_container.get_children():
		child.queue_free()
	
	tile_buttons.clear()
	grid_container.columns = current_grid_size
	
	for row in range(current_grid_size):
		for col in range(current_grid_size):
			var btn = TextureButton.new()
			btn.name = "Tile_" + str(row) + "_" + str(col)
			btn.custom_minimum_size = Vector2(cell_size, cell_size)
			btn.size = Vector2(cell_size, cell_size)
			btn.stretch_mode = TextureButton.STRETCH_SCALE
			btn.pressed.connect(_on_tile_pressed.bind(row, col))
			
			grid_container.add_child(btn)
			tile_buttons.append(btn)

func set_grid_size(new_grid_size: int):
	current_grid_size = new_grid_size
	_update_layout()
	grid_size_changed.emit(new_grid_size)

func update_display(puzzle):
	if not puzzle:
		return
	
	if _is_initializing or tile_buttons.size() == 0:
		await get_tree().process_frame
		if tile_buttons.size() == 0:
			return
	
	for row in range(current_grid_size):
		for col in range(current_grid_size):
			var idx = row * current_grid_size + col
			if idx < tile_buttons.size():
				var btn = tile_buttons[idx]
				var value = puzzle.get_tile(row, col)
				
				if value == 0:
					btn.texture_normal = null
					btn.modulate = Color(1, 1, 1, 0)
					btn.disabled = true
				else:
					if scaled_textures.has(value):
						btn.texture_normal = scaled_textures[value]
					elif number_textures.has(value):
						btn.texture_normal = number_textures[value]
					else:
						var img = Image.create(cell_size, cell_size, false, Image.FORMAT_RGBA8)
						img.fill(Color(0.7, 0.85, 1))
						btn.texture_normal = ImageTexture.create_from_image(img)
					btn.modulate = Color(1, 1, 1, 1)
					btn.disabled = false

func update_move_count(count: int):
	if move_count_label:
		move_count_label.text = "步数: " + str(count)

func update_timer(seconds: int):
	if timer_label:
		var mins = int(seconds / 60.0)
		var secs = int(seconds) % 60
		timer_label.text = "时间: %02d:%02d" % [mins, secs]

func show_message(message: String):
	if message_dialog:
		message_dialog.visible = true
		var label = message_dialog.get_node_or_null("MessageLabel")
		if label:
			label.text = message

func hide_message():
	if message_dialog:
		message_dialog.visible = false

func set_buttons_enabled(enabled: bool):
	for btn in tile_buttons:
		if btn.texture_normal == null:
			btn.disabled = true
		else:
			btn.disabled = not enabled

func _on_tile_pressed(row: int, col: int):
	tile_clicked.emit(row, col)

func _on_message_dialog_input(event: InputEvent):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		message_dialog_clicked.emit()
