extends Node

const TILE_SIZE = 32
const MAP_WIDTH = 50
const MAP_HEIGHT = 15

const TILE_EMPTY = 0
const TILE_GROUND = 1
const TILE_PATH = 2
const TILE_HOUSE = 3
const TILE_SLOPE_UP_RIGHT = 4
const TILE_SLOPE_DOWN_LEFT = 5

var tile_colors: Dictionary = {}

var tile_names = {
	TILE_EMPTY: "empty",
	TILE_GROUND: "ground",
	TILE_PATH: "path",
	TILE_HOUSE: "house",
	TILE_SLOPE_UP_RIGHT: "slope_up_right",
	TILE_SLOPE_DOWN_LEFT: "slope_down_left"
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
		TILE_PATH: Color(0.6, 0.6, 0.6, 1.0),
		TILE_HOUSE: Color(0.55, 0.35, 0.15, 1.0),
		TILE_SLOPE_UP_RIGHT: Color(0.5, 0.5, 0.5, 1.0),
		TILE_SLOPE_DOWN_LEFT: Color(0.5, 0.5, 0.5, 1.0)
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
	return tile in [TILE_GROUND, TILE_HOUSE]

func is_ladder(_x: int, _y: int) -> bool:
	return false

func is_slope(x: int, y: int) -> bool:
	var tile = get_tile(x, y)
	return tile in [TILE_SLOPE_UP_RIGHT, TILE_SLOPE_DOWN_LEFT]

func is_path(x: int, y: int) -> bool:
	return get_tile(x, y) == TILE_PATH
