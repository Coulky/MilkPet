extends Node2D

const TileMapConfigScript = preload("res://scripts/games/TileMapConfig.gd")

var config: Node
var tile_size: int = 32
var ground_container: Node2D
var ladder_container: Node2D
var upper_container: Node2D
var ladder_texture: Texture2D

var view_width: int = 400
var view_height: int = 300

func _ready():
	config = TileMapConfigScript.new()
	add_child(config)

	ladder_texture = load("res://assets/images/ladder.png")

	var viewport_size = get_viewport().get_visible_rect().size
	view_width = int(viewport_size.x)
	view_height = int(viewport_size.y)

	_create_map_containers()
	_update_map()

func _create_map_containers():
	ground_container = Node2D.new()
	ground_container.name = "GroundContainer"
	ground_container.z_index = 0
	add_child(ground_container)

	ladder_container = Node2D.new()
	ladder_container.name = "LadderContainer"
	ladder_container.z_index = 1
	add_child(ladder_container)

	upper_container = Node2D.new()
	upper_container.name = "UpperContainer"
	upper_container.z_index = 2
	add_child(upper_container)

func _update_map():
	for child in ground_container.get_children():
		child.queue_free()
	for child in ladder_container.get_children():
		child.queue_free()
	for child in upper_container.get_children():
		child.queue_free()

	var map_data = config.current_map
	for y in range(map_data.size()):
		for x in range(map_data[y].size()):
			var tile_id = map_data[y][x]
			if tile_id != config.TILE_EMPTY:
				if tile_id == config.TILE_LADDER:
					_create_ladder_tile(x, y)
				elif tile_id in [config.TILE_PLATFORM, config.TILE_BRICK]:
					_create_upper_tile(x, y, tile_id)
				else:
					_create_ground_tile(x, y, tile_id)
				
				if tile_id in [config.TILE_PLATFORM, config.TILE_BRICK]:
					var below_tile = config.get_tile(x, y + 1)
					if below_tile == config.TILE_LADDER:
						_create_ladder_tile(x, y)

func _create_ground_tile(x: int, y: int, tile_id: int):
	var color = config.tile_colors.get(tile_id, Color(0.5, 0.5, 0.5, 1.0))
	
	var tile_node = StaticBody2D.new()
	tile_node.name = "Tile_%d_%d" % [x, y]
	tile_node.position = Vector2(x * tile_size, y * tile_size)
	
	var tile = ColorRect.new()
	tile.custom_minimum_size = Vector2(tile_size, tile_size)
	tile.color = color
	tile_node.add_child(tile)
	
	if config.is_solid(x, y):
		var collision = CollisionShape2D.new()
		var shape = RectangleShape2D.new()
		shape.size = Vector2(tile_size, tile_size)
		collision.shape = shape
		collision.position = Vector2(float(tile_size) / 2.0, float(tile_size) / 2.0)
		tile_node.add_child(collision)
	
	ground_container.add_child(tile_node)

func _create_ladder_tile(x: int, y: int):
	if ladder_texture:
		var ladder = TextureRect.new()
		ladder.name = "Ladder_%d_%d" % [x, y]
		ladder.texture = ladder_texture
		ladder.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ladder.custom_minimum_size = Vector2(tile_size, tile_size)
		ladder.position = Vector2(x * tile_size, y * tile_size)
		ladder_container.add_child(ladder)
	else:
		var ladder = Node2D.new()
		ladder.name = "Ladder_%d_%d" % [x, y]
		ladder.position = Vector2(x * tile_size, y * tile_size)
		ladder_container.add_child(ladder)

		var rails = ColorRect.new()
		rails.custom_minimum_size = Vector2(tile_size, tile_size)
		rails.color = Color(0.55, 0.35, 0.15, 1.0)
		ladder.add_child(rails)

		var rung1 = ColorRect.new()
		rung1.custom_minimum_size = Vector2(tile_size - 8, 4)
		rung1.color = Color(0.4, 0.25, 0.1, 1.0)
		rung1.position = Vector2(4, 8)
		ladder.add_child(rung1)

		var rung2 = ColorRect.new()
		rung2.custom_minimum_size = Vector2(tile_size - 8, 4)
		rung2.color = Color(0.4, 0.25, 0.1, 1.0)
		rung2.position = Vector2(4, 20)
		ladder.add_child(rung2)

		var left_rail = ColorRect.new()
		left_rail.custom_minimum_size = Vector2(4, tile_size)
		left_rail.color = Color(0.45, 0.28, 0.12, 1.0)
		left_rail.position = Vector2(0, 0)
		ladder.add_child(left_rail)

		var right_rail = ColorRect.new()
		right_rail.custom_minimum_size = Vector2(4, tile_size)
		right_rail.color = Color(0.45, 0.28, 0.12, 1.0)
		right_rail.position = Vector2(tile_size - 4, 0)
		ladder.add_child(right_rail)

func _create_upper_tile(x: int, y: int, tile_id: int):
	var color = config.tile_colors.get(tile_id, Color(0.5, 0.5, 0.5, 1.0))
	
	var tile_node = StaticBody2D.new()
	tile_node.name = "Tile_%d_%d" % [x, y]
	tile_node.position = Vector2(x * tile_size, y * tile_size)
	
	var tile = ColorRect.new()
	tile.custom_minimum_size = Vector2(tile_size, tile_size)
	tile.color = color
	tile_node.add_child(tile)
	
	if config.is_solid(x, y):
		var collision = CollisionShape2D.new()
		var shape = RectangleShape2D.new()
		shape.size = Vector2(tile_size, tile_size)
		collision.shape = shape
		collision.position = Vector2(float(tile_size) / 2.0, float(tile_size) / 2.0)
		tile_node.add_child(collision)
	
	upper_container.add_child(tile_node)

func get_tile_world_pos(x: int, y: int) -> Vector2:
	return Vector2(x * tile_size, y * tile_size)

func get_tile_from_world(x: float, y: float) -> Vector2i:
	return Vector2i(int(x / tile_size), int(y / tile_size))

func set_tile(x: int, y: int, tile_type: int):
	config.set_tile(x, y, tile_type)
	_update_map()

func collect_coin(x: int, y: int) -> bool:
	if config.is_collectible(x, y):
		config.set_tile(x, y, config.TILE_EMPTY)
		_update_map()
		return true
	return false

func load_map(map_data: Array):
	config.current_map = map_data
	_update_map()

func get_map_width() -> int:
	return config.MAP_WIDTH

func get_map_height() -> int:
	return config.MAP_HEIGHT