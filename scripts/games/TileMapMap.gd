extends Node2D

const TileMapConfigScript = preload("res://scripts/games/TileMapConfig.gd")

var config: Node
var tile_size: int = 32
var ground_container: Node2D
var upper_container: Node2D

func _ready():
	config = TileMapConfigScript.new()
	add_child(config)

	_create_map_containers()
	_update_map()

func _create_map_containers():
	ground_container = Node2D.new()
	ground_container.name = "GroundContainer"
	ground_container.z_index = 0
	add_child(ground_container)

	upper_container = Node2D.new()
	upper_container.name = "UpperContainer"
	upper_container.z_index = 1
	add_child(upper_container)

func _update_map():
	for child in ground_container.get_children():
		child.queue_free()
	for child in upper_container.get_children():
		child.queue_free()

	var map_data = config.current_map
	for y in range(map_data.size()):
		for x in range(map_data[y].size()):
			var tile_id = map_data[y][x]
			if tile_id != config.TILE_EMPTY:
				if config.is_solid(x, y):
					_create_solid_tile(x, y, tile_id)
				elif config.is_slope(x, y):
					_create_slope_tile(x, y, tile_id)
				elif config.is_path(x, y) or tile_id == config.TILE_GROUND:
					_create_ground_tile(x, y, tile_id)

func _create_ground_tile(x: int, y: int, tile_id: int):
	var color = config.tile_colors.get(tile_id, Color(0.6, 0.6, 0.6, 1.0))
	
	var tile_node = Node2D.new()
	tile_node.name = "Tile_%d_%d" % [x, y]
	tile_node.position = Vector2(x * tile_size, y * tile_size)
	
	var tile = ColorRect.new()
	tile.custom_minimum_size = Vector2(tile_size, tile_size)
	tile.color = color
	tile_node.add_child(tile)
	
	ground_container.add_child(tile_node)

func _create_solid_tile(x: int, y: int, tile_id: int):
	var color = config.tile_colors.get(tile_id, Color(0.55, 0.35, 0.15, 1.0))
	
	var tile_node = StaticBody2D.new()
	tile_node.name = "Tile_%d_%d" % [x, y]
	tile_node.position = Vector2(x * tile_size, y * tile_size)
	
	var tile = ColorRect.new()
	tile.custom_minimum_size = Vector2(tile_size, tile_size)
	tile.color = color
	tile_node.add_child(tile)
	
	var collision = CollisionShape2D.new()
	var shape = RectangleShape2D.new()
	shape.size = Vector2(tile_size, tile_size)
	collision.shape = shape
	collision.position = Vector2(float(tile_size) / 2.0, float(tile_size) / 2.0)
	tile_node.add_child(collision)
	
	upper_container.add_child(tile_node)

func _create_slope_tile(x: int, y: int, slope_type: int):
	var color = config.tile_colors.get(slope_type, Color(0.5, 0.5, 0.5, 1.0))
	
	var tile_node = Node2D.new()
	tile_node.name = "Slope_%d_%d" % [x, y]
	tile_node.position = Vector2(x * tile_size, y * tile_size)
	
	var line = Line2D.new()
	line.width = 3.0
	line.default_color = color
	
	if slope_type == config.TILE_SLOPE_UP_RIGHT:
		line.add_point(Vector2(0, tile_size))
		line.add_point(Vector2(tile_size, 0))
	else:
		line.add_point(Vector2(0, 0))
		line.add_point(Vector2(tile_size, tile_size))
	
	tile_node.add_child(line)
	
	var fill = ColorRect.new()
	fill.custom_minimum_size = Vector2(tile_size, tile_size)
	fill.color = Color(color.r, color.g, color.b, 0.4)
	fill.position = Vector2(0, 0)
	tile_node.add_child(fill)
	
	ground_container.add_child(tile_node)

func get_tile_world_pos(x: int, y: int) -> Vector2:
	return Vector2(x * tile_size, y * tile_size)

func get_tile_from_world(x: float, y: float) -> Vector2i:
	return Vector2i(int(x / tile_size), int(y / tile_size))

func set_tile(x: int, y: int, tile_type: int):
	config.set_tile(x, y, tile_type)
	_update_map()

func load_map(map_data: Array):
	config.current_map = map_data
	_update_map()

func get_map_width() -> int:
	return config.MAP_WIDTH

func get_map_height() -> int:
	return config.MAP_HEIGHT
