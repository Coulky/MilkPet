extends Control

const TileMapMapScript = preload("res://scripts/games/TileMapMap.gd")
const TileMapConfigScript = preload("res://scripts/games/TileMapConfig.gd")
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
var climb_speed: float = 150.0
var is_on_ground: bool = false
var is_on_ladder: bool = false

var coins_collected: int = 0
var total_coins: int = 0

var ladder_hint: Control
var ladder_hint_label: Label
var ladder_hint_visible: bool = false

var keys_pressed: Dictionary = {}

func _ready():
	_ensure_background()
	_setup_ui()
	_create_map()
	_create_player()
	_setup_camera()

func _ensure_background():
	var bg = get_node_or_null("Background")
	if not bg:
		bg = ColorRect.new()
		bg.name = "Background"
		bg.anchors_preset = Control.PRESET_FULL_RECT
		bg.color = Color.WHITE
		bg.add_theme_color_override("background_color", Color.WHITE)
		bg.add_theme_stylebox_override("panel", null)
		add_child(bg)
	bg.color = Color.WHITE
	bg.z_index = -1000
	move_child(bg, 0)
	self.add_theme_color_override("background_color", Color.WHITE)

func _setup_ui():
	_create_ladder_hint()

func _create_ladder_hint():
	ladder_hint = Control.new()
	ladder_hint.name = "LadderHint"
	ladder_hint.anchors_preset = Control.PRESET_CENTER
	ladder_hint.anchor_left = 0.5
	ladder_hint.anchor_top = 0.5
	ladder_hint.anchor_right = 0.5
	ladder_hint.anchor_bottom = 0.5
	ladder_hint.offset_left = -25.0
	ladder_hint.offset_top = -25.0
	ladder_hint.offset_right = 25.0
	ladder_hint.offset_bottom = 25.0
	ladder_hint.modulate = Color(1, 1, 1, 0)

	var hint_bg = ColorRect.new()
	hint_bg.name = "HintBg"
	hint_bg.anchors_preset = Control.PRESET_FULL_RECT
	hint_bg.color = Color(0, 0, 0, 0.7)
	ladder_hint.add_child(hint_bg)

	ladder_hint_label = Label.new()
	ladder_hint_label.name = "HintLabel"
	ladder_hint_label.anchors_preset = Control.PRESET_FULL_RECT
	ladder_hint_label.text = "W"
	ladder_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ladder_hint_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	ladder_hint_label.add_theme_font_size_override("font_size", 24)
	ladder_hint_label.add_theme_color_override("font_color", Color.WHITE)
	ladder_hint.add_child(ladder_hint_label)

	add_child(ladder_hint)

func _show_ladder_hint():
	if not ladder_hint_visible:
		ladder_hint_visible = true
		var tween = create_tween()
		tween.tween_property(ladder_hint, "modulate", Color(1, 1, 1, 0.8), 0.2)

func _hide_ladder_hint():
	if ladder_hint_visible:
		ladder_hint_visible = false
		var tween = create_tween()
		tween.tween_property(ladder_hint, "modulate", Color(1, 1, 1, 0), 0.2)

func _update_ladder_hint_position():
	var player_screen_pos = player.position + Vector2(0, -40)
	ladder_hint.position = player_screen_pos

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
	camera.make_current()

func _on_jump():
	keys_pressed["space"] = true

func _physics_process(delta):
	_check_near_ladder()
	_handle_input()
	_apply_gravity(delta)
	_apply_movement(delta)
	_check_collisions()
	_update_camera()
	_update_ladder_hint_position()
	keys_pressed.clear()

func _check_near_ladder():
	var tile_x = int(player.position.x / config.TILE_SIZE)
	var tile_y = int(player.position.y / config.TILE_SIZE)

	var near_ladder = false
	for dx in [-1, 0, 1]:
		for dy in [-1, 0, 1]:
			if config.is_ladder(tile_x + dx, tile_y + dy):
				near_ladder = true
				break

	if near_ladder and not is_on_ground:
		_show_ladder_hint()
	else:
		_hide_ladder_hint()

func _handle_input():
	var move_dir = 0.0
	var vertical_input = 0.0

	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP) or keys_pressed.get("w", false):
		vertical_input -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN) or keys_pressed.get("s", false):
		vertical_input += 1.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT) or keys_pressed.get("a", false):
		move_dir -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT) or keys_pressed.get("d", false):
		move_dir += 1.0

	player.velocity.x = move_dir * move_speed

	var near_ladder = _is_near_ladder()
	if is_on_ladder and not near_ladder:
		is_on_ladder = false
	if near_ladder and vertical_input != 0.0:
		is_on_ladder = true

	if is_on_ladder:
		player.velocity.y = vertical_input * climb_speed
		if Input.is_key_pressed(KEY_SPACE) or keys_pressed.get("space", false):
			is_on_ladder = false
		if vertical_input == 0.0:
			player.velocity.y = 0
	elif Input.is_key_pressed(KEY_SPACE) or keys_pressed.get("space", false):
		if is_on_ground:
			player.velocity.y = jump_force
			is_on_ground = false

func _is_near_ladder() -> bool:
	var center_tile_x = int(player.position.x / config.TILE_SIZE)
	var center_tile_y = int(player.position.y / config.TILE_SIZE)
	var left_tile_x = int((player.position.x - 8) / config.TILE_SIZE)
	var right_tile_x = int((player.position.x + 8) / config.TILE_SIZE)

	for check_x in [left_tile_x, center_tile_x, right_tile_x]:
		if check_x >= 0 and check_x < config.MAP_WIDTH:
			if config.is_ladder(check_x, center_tile_y) or config.is_ladder(check_x, center_tile_y - 1):
				return true
	return false

func _apply_gravity(delta):
	if not is_on_ladder:
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

func _check_collisions():
	var tile_x = int(player.position.x / config.TILE_SIZE)
	var tile_y_feet = int((player.position.y + 12) / config.TILE_SIZE)

	if tile_y_feet + 1 < config.MAP_HEIGHT and tile_y_feet >= -1:
		if config.is_solid(tile_x, tile_y_feet + 1):
			var tile_top = (tile_y_feet + 1) * config.TILE_SIZE
			var feet_y = player.position.y + 12
			var distance_to_tile = feet_y - tile_top
			
			if distance_to_tile > 0 and distance_to_tile < 40 and player.velocity.y >= 0:
				player.position.y = tile_top - 12
				player.velocity.y = 0
				is_on_ground = true

	if player.position.y > config.MAP_HEIGHT * config.TILE_SIZE:
		_reset_player_position()

func _update_camera():
	if camera:
		var target_pos = player.position
		target_pos.x = clamp(target_pos.x, camera.limit_left + 200, camera.limit_right - 200)
		target_pos.y = clamp(target_pos.y, camera.limit_top + 150, camera.limit_bottom - 150)
		camera.position = camera.position.lerp(target_pos, 0.1)

func _reset_player_position():
	player.position = player_start_pos
	player.velocity = Vector2(0, 0)