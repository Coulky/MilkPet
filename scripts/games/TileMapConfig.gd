extends Node

const TILE_SIZE = 32
const MAP_WIDTH = 50
const MAP_HEIGHT = 15

const TILE_EMPTY = 0
const TILE_GROUND = 1
const TILE_PLATFORM = 2
const TILE_BRICK = 3
const TILE_LADDER = 4
const TILE_PIPE = 5
const TILE_TREE = 6
const TILE_FLOWER = 7
const TILE_GRASS = 8
const TILE_PATH = 9

var tile_colors: Dictionary = {}

var tile_names = {
	TILE_EMPTY: "empty",
	TILE_GROUND: "ground",
	TILE_PLATFORM: "platform",
	TILE_BRICK: "brick",
	TILE_LADDER: "ladder",
	TILE_PIPE: "pipe",
	TILE_TREE: "tree",
	TILE_FLOWER: "flower",
	TILE_GRASS: "grass",
	TILE_PATH: "path"
}

var current_map: Array = []

func _init():
	current_map = _load_map_from_json("res://assets/maps/safe_zone.json")

func _load_map_from_json(path: String) -> Array:
	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		_init_default_colors()
		return _generate_default_map()

	var content = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(content)
	if parse_result != OK:
		_init_default_colors()
		return _generate_default_map()

	var data = json.data
	if data == null or not data.has("map_data"):
		_init_default_colors()
		return _generate_default_map()

	if data.has("colors"):
		_load_colors_from_json(data["colors"])
	else:
		_init_default_colors()

	return data["map_data"]

func _load_colors_from_json(colors_data: Dictionary):
	tile_colors = {}
	for key in colors_data:
		var tile_id = int(key)
		var hex_color = colors_data[key]
		tile_colors[tile_id] = Color(hex_color)

func _init_default_colors():
	tile_colors = {
		TILE_EMPTY: Color.TRANSPARENT,
		TILE_GROUND: Color(0.35, 0.55, 0.25, 1.0),
		TILE_PLATFORM: Color(0.55, 0.35, 0.15, 1.0),
		TILE_BRICK: Color(0.65, 0.45, 0.25, 1.0),
		TILE_LADDER: Color(0.55, 0.35, 0.15, 1.0),
		TILE_PIPE: Color(0.0, 0.6, 0.0, 1.0),
		TILE_TREE: Color(0.0, 0.5, 0.0, 1.0),
		TILE_FLOWER: Color(1.0, 0.3, 0.5, 1.0),
		TILE_GRASS: Color(0.45, 0.65, 0.3, 1.0),
		TILE_PATH: Color(0.7, 0.6, 0.4, 1.0)
	}

func _generate_default_map() -> Array:
	var map = []
	for y in range(MAP_HEIGHT):
		map.append([])
		for x in range(MAP_WIDTH):
			if y >= MAP_HEIGHT - 1:
				map[y].append(TILE_GROUND)
			else:
				map[y].append(TILE_EMPTY)
	return map

func get_tile(x: int, y: int) -> int:
	if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
		return TILE_EMPTY
	return current_map[y][x]

func set_tile(x: int, y: int, tile_type: int):
	if x >= 0 and x < MAP_WIDTH and y >= 0 and y < MAP_HEIGHT:
		current_map[y][x] = tile_type

func is_solid(x: int, y: int) -> bool:
	var tile = get_tile(x, y)
	return tile in [TILE_GROUND, TILE_PLATFORM, TILE_BRICK, TILE_PIPE, TILE_TREE]

func is_ladder(x: int, y: int) -> bool:
	return get_tile(x, y) == TILE_LADDER

func is_collectible(_x: int, _y: int) -> bool:
	return false

func is_hazard(_x: int, _y: int) -> bool:
	return false