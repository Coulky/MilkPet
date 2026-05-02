extends Control

const TileMapMapScript = preload("res://scripts/games/TileMapMap.gd")
const TileMapConfigScript = preload("res://scripts/games/TileMapConfig.gd")
const GameButtonFactoryScript = preload("res://scripts/common/GameButtonFactory.gd")
const CircleSpriteScript = preload("res://scripts/games/CircleSprite.gd")

var tile_map_node: Node2D
var player: CharacterBody2D
var player_sprite: Node2D
var camera: Camera2D

var config: Node

var player_start_pos: Vector2 = Vector2(200, 300)
var player_velocity: Vector2 = Vector2(0, 0)
var gravity: float = 600.0
var move_speed: float = 200.0
var jump_force: float = -350.0
var is_on_ground: bool = false

var coins_collected: int = 0
var total_coins: int = 0

var coin_label: Label
var top_panel: PanelContainer
var left_panel: PanelContainer
var action_buttons: VBoxContainer

var keys_pressed: Dictionary = {}

func _ready():
	_setup_ui()
	_create_map()
	_create_player()
	_setup_camera()
	_count_coins()

func _setup_ui():
	top_panel = PanelContainer.new()
	top_panel.name = "TopPanel"
	top_panel.anchors_preset = Control.PRESET_TOP_LEFT
	top_panel.anchor_left = 0.0
	top_panel.anchor_top = 0.0
	top_panel.anchor_right = 1.0
	top_panel.anchor_bottom = 0.0
	top_panel.offset_top = 0.0
	top_panel.offset_bottom = 60.0
	top_panel.size_flags_vertical = Control.SIZE_SHRINK_BEGIN

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0, 0, 0, 0.8)
	top_panel.add_theme_stylebox_override("panel", style)
	add_child(top_panel)

	var top_hbox = HBoxContainer.new()
	top_hbox.anchors_preset = Control.PRESET_FULL_RECT
	top_panel.add_child(top_hbox)

	coin_label = Label.new()
	coin_label.name = "CoinLabel"
	coin_label.text = "金币: 0 / 0"
	coin_label.add_theme_font_size_override("font_size", 18)
	coin_label.add_theme_color_override("font_color", Color.WHITE)
	top_hbox.add_child(coin_label)

	var spacer = Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND
	top_hbox.add_child(spacer)

	GameButtonFactoryScript.create_simple_button(top_hbox, "BackButton", "res://assets/images/back.png", _on_back)
	var back_btn = top_hbox.get_node_or_null("BackButton")
	if back_btn:
		back_btn.custom_minimum_size = Vector2(50, 50)

	left_panel = PanelContainer.new()
	left_panel.name = "LeftPanel"
	left_panel.anchors_preset = Control.PRESET_LEFT_WIDE
	left_panel.anchor_left = 0.0
	left_panel.anchor_top = 0.0
	left_panel.anchor_right = 0.0
	left_panel.anchor_bottom = 1.0
	left_panel.offset_left = 10.0
	left_panel.offset_top = 70.0
	left_panel.offset_right = 110.0
	left_panel.offset_bottom = -10.0
	left_panel.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN

	var left_style = StyleBoxFlat.new()
	left_style.bg_color = Color(0, 0, 0, 0.6)
	left_style.border_width_right = 2
	left_style.border_color = Color(0.5, 0.5, 0.5, 1)
	left_panel.add_theme_stylebox_override("panel", left_style)
	add_child(left_panel)

	action_buttons = VBoxContainer.new()
	action_buttons.name = "ActionButtons"
	action_buttons.anchors_preset = Control.PRESET_FULL_RECT
	action_buttons.add_theme_constant_override("separation", 15)
	left_panel.add_child(action_buttons)

	var btn_up = GameButtonFactoryScript.create_button(action_buttons, "MoveUpButton", "", "上", _on_move_up)
	var btn_left = GameButtonFactoryScript.create_button(action_buttons, "MoveLeftButton", "", "左", _on_move_left)
	var btn_right = GameButtonFactoryScript.create_button(action_buttons, "MoveRightButton", "", "右", _on_move_right)
	var btn_jump = GameButtonFactoryScript.create_button(action_buttons, "JumpButton", "", "跳", _on_jump)

	for container in [btn_up, btn_left, btn_right, btn_jump]:
		if container and container is Control:
			container.custom_minimum_size = Vector2(80, 50)

func _create_map():
	tile_map_node = TileMapMapScript.new()
	tile_map_node.name = "TileMap"
	add_child(tile_map_node)
	config = tile_map_node.config

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

	player_sprite = CircleSpriteScript.new()
	player_sprite.name = "PlayerSprite"
	player_sprite.radius = 12
	player_sprite.color = Color(1.0, 0.2, 0.2, 1.0)
	player.add_child(player_sprite)

	add_child(player)

func _setup_camera():
	camera = Camera2D.new()
	camera.name = "GameCamera"
	camera.zoom = Vector2(1.5, 1.5)
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = config.MAP_WIDTH * config.TILE_SIZE
	camera.limit_bottom = config.MAP_HEIGHT * config.TILE_SIZE
	camera.position = player.position
	add_child(camera)

func _count_coins():
	total_coins = 0
	for y in range(config.MAP_HEIGHT):
		for x in range(config.MAP_WIDTH):
			if config.is_collectible(x, y):
				total_coins += 1
	update_coin_label()

func update_coin_label():
	if coin_label:
		coin_label.text = "金币: %d / %d" % [coins_collected, total_coins]

func _on_move_up():
	keys_pressed["w"] = true

func _on_move_left():
	keys_pressed["a"] = true

func _on_move_right():
	keys_pressed["d"] = true

func _on_jump():
	keys_pressed["space"] = true

func _physics_process(delta):
	_handle_input()
	_apply_gravity(delta)
	_apply_movement(delta)
	_check_collisions()
	_check_collectibles()
	_update_camera()
	keys_pressed.clear()

func _handle_input():
	var move_dir = 0.0

	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP) or keys_pressed.get("w", false):
		move_dir -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN) or keys_pressed.get("s", false):
		move_dir += 1.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT) or keys_pressed.get("a", false):
		move_dir -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT) or keys_pressed.get("d", false):
		move_dir += 1.0

	player.velocity.x = move_dir * move_speed

	if Input.is_key_pressed(KEY_SPACE) or keys_pressed.get("space", false):
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

	is_on_ground = false
	if collision:
		var normal = collision.get_normal()
		if normal.y < -0.5:
			is_on_ground = true
			player.velocity.y = 0

func _check_collisions():
	var tile_x = int(player.position.x / config.TILE_SIZE)
	var tile_y = int((player.position.y + 10) / config.TILE_SIZE)

	if tile_y >= 0 and tile_y < config.MAP_HEIGHT:
		if config.is_solid(tile_x, tile_y + 1) and player.velocity.y >= 0:
			var tile_top = tile_y * config.TILE_SIZE
			if player.position.y + 10 >= tile_top and player.position.y + 10 <= tile_top + 15:
				player.position.y = tile_top - 10
				player.velocity.y = 0
				is_on_ground = true

	if player.position.y > config.MAP_HEIGHT * config.TILE_SIZE:
		_reset_player_position()

func _check_collectibles():
	var tile_x = int(player.position.x / config.TILE_SIZE)
	var tile_y = int(player.position.y / config.TILE_SIZE)

	if config.is_collectible(tile_x, tile_y):
		if tile_map_node.collect_coin(tile_x, tile_y):
			coins_collected += 1
			update_coin_label()

func _update_camera():
	if camera:
		var target_pos = player.position
		target_pos.x = clamp(target_pos.x, camera.limit_left + 200, camera.limit_right - 200)
		target_pos.y = clamp(target_pos.y, camera.limit_top + 150, camera.limit_bottom - 150)
		camera.position = camera.position.lerp(target_pos, 0.1)

func _reset_player_position():
	player.position = player_start_pos
	player.velocity = Vector2(0, 0)

func _on_back():
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")