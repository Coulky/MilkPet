extends Control

const CircleSpriteScript = preload("res://scripts/games/CircleSprite.gd")
const ExitDialogScript = preload("res://scripts/common/ExitDialog.gd")

var game_layer: Node2D
var ui_layer: CanvasLayer
var ui_control: Control
var player: CharacterBody2D
var camera: Camera2D
var exit_dialog: Control

var map_config: Dictionary
var interactive_areas: Array = []
var current_area: Dictionary = {}

var player_start_pos: Vector2
var player_velocity: Vector2 = Vector2(0, 0)
var gravity: float = 600.0
var move_speed: float = 200.0
var jump_force: float = -350.0
var is_on_ground: bool = false
var e_just_pressed: bool = false

func _ready():
	_ensure_background()
	_load_map_config()
	_create_layers()
	_create_map_background()
	_create_interactive_areas()
	_create_player()
	_setup_camera()
	_create_exit_dialog()

func _load_map_config():
	var file = FileAccess.open("res://assets/maps/home_page.json", FileAccess.READ)
	if file:
		var json_text = file.get_as_text()
		file.close()
		var json = JSON.new()
		if json.parse(json_text) == OK:
			map_config = json.data
			interactive_areas = map_config.interactive_areas
			player_start_pos = Vector2(map_config.player_start.x, map_config.player_start.y)

func _create_layers():
	game_layer = Node2D.new()
	game_layer.name = "GameLayer"
	game_layer.z_index = 0
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
	
	var viewport = get_viewport()
	if viewport:
		viewport.size_changed.connect(_on_viewport_resized)

func _ensure_background():
	var bg = get_node_or_null("Background")
	if not bg:
		bg = ColorRect.new()
		bg.name = "Background"
		bg.anchors_preset = Control.PRESET_FULL_RECT
		bg.color = Color.WHITE
		bg.z_index = -1000
		add_child(bg)
		move_child(bg, 0)

func _create_map_background():
	var bg_texture = load(map_config.background_image)
	if bg_texture:
		var bg_sprite = Sprite2D.new()
		bg_sprite.name = "MapBackground"
		bg_sprite.texture = bg_texture
		bg_sprite.position = Vector2(map_config.map_size.width / 2, map_config.map_size.height / 2)
		game_layer.add_child(bg_sprite)

func _create_interactive_areas():
	for area in interactive_areas:
		var area_node = Area2D.new()
		area_node.name = "Area_" + area.id
		area_node.position = Vector2(area.position.x, area.position.y)
		
		var collision_shape = CollisionShape2D.new()
		var shape = RectangleShape2D.new()
		shape.size = Vector2(area.size.width, area.size.height)
		collision_shape.shape = shape
		area_node.add_child(collision_shape)
		
		area_node.connect("body_entered", _on_area_entered.bind(area))
		area_node.connect("body_exited", _on_area_exited.bind(area))
		
		game_layer.add_child(area_node)

func _create_player():
	player = CharacterBody2D.new()
	player.name = "Player"
	player.position = player_start_pos
	player.velocity = Vector2(0, 0)

	var collision = CollisionShape2D.new()
	var shape = CircleShape2D.new()
	shape.radius = 12
	collision.shape = shape
	player.add_child(collision)

	var player_sprite = CircleSpriteScript.new()
	player_sprite.name = "PlayerSprite"
	player_sprite.radius = 12
	player_sprite.color = Color(1.0, 0.2, 0.2, 1.0)
	player.add_child(player_sprite)

	game_layer.add_child(player)

func _setup_camera():
	camera = Camera2D.new()
	camera.name = "GameCamera"
	camera.zoom = Vector2(1.0, 1.0)
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = map_config.map_size.width
	camera.limit_bottom = map_config.map_size.height
	camera.position = player.position
	add_child(camera)
	camera.make_current()

func _create_exit_dialog():
	exit_dialog = ExitDialogScript.new()
	exit_dialog.name = "ExitDialog"
	ui_control.add_child(exit_dialog)
	exit_dialog.connect("confirmed", _on_exit_to_home)
	exit_dialog.connect("cancelled", _on_exit_cancelled)

func _on_area_entered(body: Node2D, area: Dictionary):
	current_area = area
	_show_interaction_hint(area)

func _on_area_exited(body: Node2D, area: Dictionary):
	if not current_area.is_empty() and current_area.id == area.id:
		current_area = {}
		_hide_interaction_hint()

func _show_interaction_hint(area: Dictionary):
	pass

func _hide_interaction_hint():
	pass

func _physics_process(delta):
	_handle_input(delta)
	_apply_gravity(delta)
	_apply_movement(delta)
	_check_ground()
	_check_interaction()
	_check_boundary()
	_update_camera()

func _handle_input(delta):
	var move_dir = 0.0
	
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		move_dir -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		move_dir += 1.0
	
	player.velocity.x = move_dir * move_speed
	
	if Input.is_key_pressed(KEY_SPACE):
		if is_on_ground:
			player.velocity.y = jump_force
			is_on_ground = false

func _apply_gravity(delta):
	player.velocity.y += gravity * delta
	if player.velocity.y > 500:
		player.velocity.y = 500

func _apply_movement(delta):
	var motion = player.velocity * delta
	var collision = player.move_and_collide(motion)
	
	if collision:
		var normal = collision.get_normal()
		if normal.y < -0.5:
			is_on_ground = true
			player.velocity.y = 0
		else:
			is_on_ground = false
	else:
		is_on_ground = false

func _check_ground():
	var ground_y = map_config.map_size.height - 100
	if player.position.y >= ground_y:
		player.position.y = ground_y
		player.velocity.y = 0
		is_on_ground = true

func _check_interaction():
	if e_just_pressed and not current_area.is_empty():
		_trigger_action(current_area.action)
	e_just_pressed = false

func _trigger_action(action: String):
	match action:
		"open_shop":
			print("打开商店")
		"enter_battle":
			print("进入战斗")
		"open_settings":
			print("打开设置")
		_:
			print("未知动作: ", action)

func _check_boundary():
	if player.position.x <= 0 or player.position.x >= map_config.map_size.width:
		if not exit_dialog.visible:
			exit_dialog.show_dialog("返回首页", "是否返回首页？", false)

func _update_camera():
	if camera:
		var target_pos = player.position
		target_pos.x = clamp(target_pos.x, camera.limit_left + 300, camera.limit_right - 300)
		target_pos.y = clamp(target_pos.y, camera.limit_top + 200, camera.limit_bottom - 200)
		camera.position = camera.position.lerp(target_pos, 0.1)

func _input(event):
	if event is InputEventKey and event.keycode == KEY_ESCAPE and event.pressed:
		if not exit_dialog.visible:
			exit_dialog.show_dialog("返回首页", "是否返回首页？", false)
	if event is InputEventKey and event.keycode == KEY_E and event.pressed:
		e_just_pressed = true

func _on_exit_to_home():
	get_tree().change_scene_to_file("res://scenes/GameIndex.tscn")

func _on_exit_cancelled():
	pass

func _on_viewport_resized():
	if ui_control:
		ui_control.size = get_viewport().get_visible_rect().size