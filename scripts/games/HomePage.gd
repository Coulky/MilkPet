extends Control

const CircleSpriteScript = preload("res://scripts/games/CircleSprite.gd")
const ExitDialogScript = preload("res://scripts/common/ExitDialog.gd")

var player: CharacterBody2D
var player_sprite: ColorRect
var camera: Camera2D
var exit_dialog: Control
var game_layer: Node2D
var ui_layer: CanvasLayer
var ui_control: Control
var map_background: Sprite2D
var ground_line: Line2D

var buildings_node: Node2D
var buildings_data: Array[Dictionary] = []
var interaction_label: Label
var current_building: Dictionary = {}
var is_near_building: bool = false
var interaction_distance: float = 80.0

var move_speed: float = 250.0
var ground_y: float = 400.0
var map_width: int = 2000

var keys_pressed: Dictionary = {}
var esc_cooldown: float = 0.0
var boundary_dialog_cancelled: bool = false
var last_boundary_side: String = ""

@export var background_texture: Texture2D

func _ready():
	_ensure_background()
	_create_layers()
	_find_map_nodes()
	_move_buildings_to_game_layer()
	_create_ground()
	_create_player()
	_setup_camera()
	_create_exit_dialog()
	_collect_buildings()
	_create_interaction_label()

func _create_layers():
	game_layer = Node2D.new()
	game_layer.name = "GameLayer"
	add_child(game_layer)
	
	ui_layer = CanvasLayer.new()
	ui_layer.name = "UiLayer"
	ui_layer.layer = 100
	add_child(ui_layer)
	
	ui_control = Control.new()
	ui_control.name = "UiControl"
	ui_control.position = Vector2.ZERO
	ui_control.size = get_viewport().get_visible_rect().size
	ui_control.mouse_filter = MOUSE_FILTER_IGNORE
	ui_layer.add_child(ui_control)

func _ensure_background():
	var bg = get_node_or_null("Background")
	if not bg:
		bg = ColorRect.new()
		bg.name = "Background"
		bg.anchors_preset = Control.PRESET_FULL_RECT
		bg.color = Color(0.3, 0.25, 0.2, 1)
		add_child(bg)

func _find_map_nodes():
	buildings_node = $Buildings if has_node("Buildings") else null

func _move_buildings_to_game_layer():
	if buildings_node:
		remove_child(buildings_node)
		buildings_node.z_index = 3
		game_layer.add_child(buildings_node)
		
		for child in buildings_node.get_children():
			if child is Sprite2D and child.texture:
				var tex = child.texture
				if tex.get_width() > 100:
					child.scale = Vector2(150.0 / tex.get_width(), 150.0 / tex.get_height())
	
	if background_texture:
		map_background = Sprite2D.new()
		map_background.name = "MapBackground"
		map_background.texture = background_texture
		map_background.centered = false
		map_background.position = Vector2(0, 0)
		map_background.z_index = -10
		map_background.modulate = Color(1, 1, 1, 0.08)
		game_layer.add_child(map_background)

func _create_ground():
	ground_line = Line2D.new()
	ground_line.name = "GroundLine"
	ground_line.width = 4.0
	ground_line.default_color = Color(0.9, 0.85, 0.7, 1)
	ground_line.z_index = 1
	ground_line.add_point(Vector2(-100, ground_y))
	ground_line.add_point(Vector2(map_width + 100, ground_y))
	game_layer.add_child(ground_line)

func _collect_buildings():
	buildings_data.clear()
	if buildings_node:
		for child in buildings_node.get_children():
			var building_id = child.get_meta("_building_id", child.name.replace("Building_", ""))
			var building_info = {
				"node": child,
				"name": child.name,
				"id": building_id,
				"position": child.position
			}
			var marker = child.get_node_or_null("InteractionPoint")
			if marker:
				building_info.interaction_pos = child.position + marker.position
			else:
				building_info.interaction_pos = Vector2(child.position.x + 30, ground_y - 10)
			buildings_data.append(building_info)

func _create_interaction_label():
	interaction_label = Label.new()
	interaction_label.name = "InteractionLabel"
	interaction_label.text = "[E]"
	interaction_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	interaction_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	interaction_label.add_theme_font_size_override("font_size", 24)
	interaction_label.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	interaction_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	interaction_label.add_theme_constant_override("outline_size", 3)
	interaction_label.visible = false
	ui_control.add_child(interaction_label)

func _create_exit_dialog():
	exit_dialog = ExitDialogScript.new()
	exit_dialog.name = "ExitDialog"
	ui_control.add_child(exit_dialog)
	exit_dialog.connect("confirmed", _on_exit_to_home)
	exit_dialog.connect("cancelled", _on_exit_cancelled)

func _create_player():
	player = CharacterBody2D.new()
	player.name = "Player"
	player.position = Vector2(150, ground_y - 12)
	player.z_index = 5

	var collision = CollisionShape2D.new()
	var shape = CircleShape2D.new()
	shape.radius = 12
	collision.shape = shape
	player.add_child(collision)

	player_sprite = ColorRect.new()
	player_sprite.name = "PlayerSprite"
	player_sprite.size = Vector2(24, 24)
	player_sprite.position = Vector2(-12, -12)
	player_sprite.color = Color(1.0, 0.2, 0.2, 1.0)
	player.add_child(player_sprite)

	game_layer.add_child(player)

func _setup_camera():
	camera = Camera2D.new()
	camera.name = "GameCamera"
	camera.limit_left = -200
	camera.limit_top = -500
	camera.limit_right = map_width + 200
	camera.limit_bottom = 800
	camera.zoom = Vector2(1.8, 1.8)
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 8.0
	game_layer.add_child(camera)
	camera.make_current()

func _physics_process(delta):
	if esc_cooldown > 0:
		esc_cooldown -= delta
	
	_handle_input()
	_apply_movement(delta)
	_update_camera_position()
	_check_building_interaction()
	_update_interaction_label()
	_check_boundary()
	keys_pressed.clear()

func _update_camera_position():
	if camera and player:
		camera.position.x = player.position.x
		camera.position.y = player.position.y

func _handle_input():
	player.velocity.x = 0
	
	var at_left_boundary = player.position.x <= 30
	var at_right_boundary = player.position.x >= map_width - 30
	
	if (Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT) or keys_pressed.get("a", false)) and not at_left_boundary:
		player.velocity.x = -move_speed
	if (Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT) or keys_pressed.get("d", false)) and not at_right_boundary:
		player.velocity.x = move_speed
	
	player.velocity.y = 0
	player.position.y = ground_y - 12
	
	if is_near_building and (Input.is_key_pressed(KEY_E) or keys_pressed.get("e", false)):
		_on_interact_with_building()

func _apply_movement(_delta):
	if player and is_inside_tree():
		player.move_and_slide()

func _check_building_interaction():
	is_near_building = false
	current_building = {}
	
	for building in buildings_data:
		var dist = abs(player.position.x - building.interaction_pos.x)
		if dist < interaction_distance:
			is_near_building = true
			current_building = building
			return

func _update_interaction_label():
	if is_near_building and not exit_dialog.visible and camera:
		var viewport = get_viewport()
		if viewport and viewport.get_visible_rect().size.x > 0:
			var viewport_size = viewport.get_visible_rect().size
			interaction_label.position = Vector2(
				viewport_size.x / 2.0 - 15,
				viewport_size.y / 2.0 - 60
			)
			interaction_label.visible = true
		else:
			interaction_label.visible = false
	else:
		interaction_label.visible = false

func _on_interact_with_building():
	var building_id = current_building.get("id", "未知")
	print("进入建筑: ", building_id, " - ", current_building.get("name", ""))
	
	var is_last_building = (building_id == buildings_data[buildings_data.size() - 1].get("id", "")) if buildings_data.size() > 0 else false
	
	if is_last_building:
		_show_achievements()
	elif building_id == "mini_game":
		get_tree().change_scene_to_file("res://scenes/games/sudoku/sudoku.tscn")
	elif building_id == "sliding_puzzle":
		get_tree().change_scene_to_file("res://scenes/games/sliding_puzzle/sliding_puzzle.tscn")

func _show_achievements():
	get_tree().change_scene_to_file("res://scenes/Achievements.tscn")

func _check_boundary():
	var at_left_boundary = player.position.x <= 30
	var at_right_boundary = player.position.x >= map_width - 30
	
	if at_left_boundary or at_right_boundary:
		if not exit_dialog.visible:
			if not boundary_dialog_cancelled:
				if at_left_boundary:
					last_boundary_side = "left"
				else:
					last_boundary_side = "right"
				exit_dialog.show_dialog("返回首页", "是否返回首页？", false)
			else:
				var should_trigger = false
				if last_boundary_side == "left" and (Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT)):
					should_trigger = true
				elif last_boundary_side == "right" and (Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)):
					should_trigger = true
				
				if should_trigger:
					boundary_dialog_cancelled = false
					exit_dialog.show_dialog("返回首页", "是否返回首页？", false)
	else:
		boundary_dialog_cancelled = false
		last_boundary_side = ""

func _unhandled_input(event: InputEvent):
	if event is InputEventKey and event.keycode == KEY_ESCAPE and event.is_pressed() and esc_cooldown <= 0:
		if not exit_dialog.visible:
			esc_cooldown = 0.5
			exit_dialog.show_dialog("返回首页", "是否返回首页？", false)

func _on_exit_to_home():
	get_tree().change_scene_to_file("res://scenes/GameIndex.tscn")

func _on_exit_cancelled():
	boundary_dialog_cancelled = true
