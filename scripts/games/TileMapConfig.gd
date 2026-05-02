extends Node

const TILE_SIZE = 32
const MAP_WIDTH = 50
const MAP_HEIGHT = 15

const TILE_EMPTY = 0
const TILE_GROUND = 1
const TILE_PLATFORM = 2
const TILE_BRICK = 3
const TILE_COIN = 4
const TILE_PIPE = 5
const TILE_TREE = 6
const TILE_FLOWER = 7
const TILE_GRASS = 8
const TILE_PATH = 9

var tile_colors = {
	TILE_EMPTY: Color.TRANSPARENT,
	TILE_GROUND: Color(0.35, 0.55, 0.25, 1.0),
	TILE_PLATFORM: Color(0.55, 0.35, 0.15, 1.0),
	TILE_BRICK: Color(0.65, 0.45, 0.25, 1.0),
	TILE_COIN: Color(1.0, 0.84, 0.0, 1.0),
	TILE_PIPE: Color(0.0, 0.6, 0.0, 1.0),
	TILE_TREE: Color(0.0, 0.5, 0.0, 1.0),
	TILE_FLOWER: Color(1.0, 0.3, 0.5, 1.0),
	TILE_GRASS: Color(0.45, 0.65, 0.3, 1.0),
	TILE_PATH: Color(0.7, 0.6, 0.4, 1.0)
}

var tile_names = {
	TILE_EMPTY: "empty",
	TILE_GROUND: "ground",
	TILE_PLATFORM: "platform",
	TILE_BRICK: "brick",
	TILE_COIN: "coin",
	TILE_PIPE: "pipe",
	TILE_TREE: "tree",
	TILE_FLOWER: "flower",
	TILE_GRASS: "grass",
	TILE_PATH: "path"
}

var current_map: Array = []

func _init():
	current_map = generate_safe_zone_map()

func generate_safe_zone_map() -> Array:
	var map = []
	for y in range(MAP_HEIGHT):
		map.append([])
		for x in range(MAP_WIDTH):
			if y >= MAP_HEIGHT - 3:
				map[y].append(TILE_GROUND)
			else:
				map[y].append(TILE_EMPTY)

	for x in range(5, 12):
		map[MAP_HEIGHT - 4][x] = TILE_PATH

	for x in range(15, 22):
		map[MAP_HEIGHT - 4][x] = TILE_PATH

	for x in range(25, 35):
		map[MAP_HEIGHT - 4][x] = TILE_PATH

	for x in range(5, 12):
		map[MAP_HEIGHT - 5][x] = TILE_BRICK

	for x in range(15, 22):
		map[MAP_HEIGHT - 5][x] = TILE_BRICK

	for x in range(25, 35):
		map[MAP_HEIGHT - 5][x] = TILE_BRICK

	for x in [8, 18, 30]:
		map[MAP_HEIGHT - 6][x] = TILE_COIN

	var decorations = [TILE_GRASS, TILE_FLOWER, TILE_TREE]
	var decor_x = [3, 6, 14, 23, 28, 40, 45]
	for x in decor_x:
		if x < MAP_WIDTH:
			map[MAP_HEIGHT - 4][x] = decorations[randi() % decorations.size()]

	return map

func generate_level_1() -> Array:
	var map = []
	for y in range(MAP_HEIGHT):
		map.append([])
		for x in range(MAP_WIDTH):
			if y >= MAP_HEIGHT - 3:
				map[y].append(TILE_GROUND)
			else:
				map[y].append(TILE_EMPTY)

	for x in range(10, 20):
		map[MAP_HEIGHT - 4][x] = TILE_PATH
		map[MAP_HEIGHT - 5][x] = TILE_BRICK

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

func is_collectible(x: int, y: int) -> bool:
	return get_tile(x, y) == TILE_COIN

func is_hazard(_x: int, _y: int) -> bool:
	return false