extends Control

const GRID_SIZE = 8
var cell_size: int = 60

var grid_container: GridContainer
var score_label: Label
var moves_label: Label
var target_label: Label
var message_dialog: PanelContainer

var gem_buttons: Array = []
var gem_textures: Dictionary = {}
var selected_indicator: ColorRect

signal gem_selected(row, col)

func _ready():
	_load_gem_textures()
	_setup_nodes()
	_create_grid()

func _load_gem_textures():
	var colors = {
		0: Color.RED,
		1: Color.BLUE,
		2: Color.GREEN,
		3: Color.YELLOW,
		4: Color.PURPLE,
		5: Color.ORANGE
	}
	
	for i in range(6):
		var img = Image.create(50, 50, false, Image.FORMAT_RGBA8)
		img.fill(colors[i])
		
		var center_x = 25
		var center_y = 25
		var radius = 20
		
		for x in range(50):
			for y in range(50):
				if pow(x - center_x, 2) + pow(y - center_y, 2) <= pow(radius, 2):
					img.set_pixel(x, y, colors[i])
				else:
					img.set_pixel(x, y, Color.TRANSPARENT)
		
		gem_textures[i] = ImageTexture.create_from_image(img)

func _setup_nodes():
	grid_container = get_node_or_null("GridContainer")
	score_label = get_node_or_null("TopPanel/ScoreLabel")
	moves_label = get_node_or_null("TopPanel/MovesLabel")
	target_label = get_node_or_null("TopPanel/TargetLabel")
	message_dialog = get_node_or_null("MessageDialog")

func _create_grid():
	if not grid_container:
		return
	
	for child in grid_container.get_children():
		child.queue_free()
	gem_buttons.clear()
	grid_container.columns = GRID_SIZE
	
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			var btn = TextureButton.new()
			btn.name = "Gem_" + str(row) + "_" + str(col)
			btn.custom_minimum_size = Vector2(cell_size, cell_size)
			btn.size = Vector2(cell_size, cell_size)
			btn.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
			btn.pressed.connect(_on_gem_pressed.bind(row, col))
			
			grid_container.add_child(btn)
			gem_buttons.append(btn)
			
			selected_indicator = ColorRect.new()
			selected_indicator.name = "SelectedIndicator"
			selected_indicator.color = Color.WHITE
			selected_indicator.visible = false
			btn.add_child(selected_indicator)

func update_display(logic: Node):
	if not logic or gem_buttons.size() == 0:
		return
	
	var grid_data = logic.get_grid()
	
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			var idx = row * GRID_SIZE + col
			if idx < gem_buttons.size():
				var btn = gem_buttons[idx]
				var gem_type = logic.get_gem(row, col)
				
				if gem_type >= 0 and gem_textures.has(gem_type):
					btn.texture_normal = gem_textures[gem_type]
					btn.modulate = Color.WHITE
					btn.disabled = false
				else:
					btn.texture_normal = null
					btn.modulate = Color.TRANSPARENT

func update_selection(selected_pos: Vector2):
	for btn in gem_buttons:
		var indicator = btn.get_node_or_null("SelectedIndicator")
		if indicator:
			indicator.visible = false
	
	if selected_pos.x >= 0 and selected_pos.y >= 0:
		var idx = int(selected_pos.y) * GRID_SIZE + int(selected_pos.x)
		if idx < gem_buttons.size():
			var btn = gem_buttons[idx]
			var indicator = btn.get_node_or_null("SelectedIndicator")
			if indicator:
				indicator.visible = true

func update_score(score: int):
	if score_label:
		score_label.text = "分数: " + str(score)

func update_moves(moves: int):
	if moves_label:
		moves_label.text = "步数: " + str(moves)

func update_target(target: int):
	if target_label:
		target_label.text = "目标: " + str(target)

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
	for btn in gem_buttons:
		btn.disabled = not enabled

func _on_gem_pressed(row: int, col: int):
	gem_selected.emit(row, col)
