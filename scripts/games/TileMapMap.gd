extends Node2D

const TileMapConfigScript = preload("res://scripts/games/TileMapConfig.gd")

var config: Node
var tile_size: int = 32
var tile_container: Node2D

var view_width: int = 400
var view_height: int = 300

func _ready():
	config = TileMapConfigScript.new()
	add_child(config)

	var viewport_size = get_viewport().get_visible_rect().size
	view_width = int(viewport_size.x)
	view_height = int(viewport_size.y)

	_create_map_container()
	_update_map()

func _create_map_container():
	tile_container = Node2D.new()
	tile_container.name = "TileContainer"
	add_child(tile_container)

func _update_map():
	if not tile_container:
		return

	for child in tile_container.get_children():
		child.queue_free()

	var map_data = config.current_map
	for y in range(map_data.size()):
		for x in range(map_data[y].size()):
			var tile_id = map_data[y][x]
			if tile_id != config.TILE_EMPTY:
				var color = config.tile_colors.get(tile_id, Color.TRANSPARENT)
				var tile = ColorRect.new()
				tile.custom_minimum_size = Vector2(tile_size, tile_size)
				tile.color = color
				tile.position = Vector2(x * tile_size, y * tile_size)
				tile_container.add_child(tile)

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