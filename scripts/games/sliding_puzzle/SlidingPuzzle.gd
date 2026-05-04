extends Node

var grid_size: int = 4
var total_tiles: int

var grid: Array = []
var empty_pos: Vector2i
var move_count: int = 0
var is_solved: bool = false

signal tile_moved(from_pos, to_pos)
signal puzzle_solved(move_count)

func _ready():
	init(4)

func init(size: int = 4):
	grid_size = size
	total_tiles = grid_size * grid_size
	grid = []
	move_count = 0
	is_solved = false
	
	var num = 1
	for row in range(grid_size):
		grid.append([])
		for col in range(grid_size):
			if num < total_tiles:
				grid[row].append(num)
			else:
				grid[row].append(0)
			num += 1
	
	empty_pos = Vector2i(grid_size - 1, grid_size - 1)

func shuffle(moves: int = 100):
	var last_move = -1
	for i in range(moves):
		var valid_moves = get_valid_moves()
		valid_moves = valid_moves.filter(func(m): return m != last_move)
		if valid_moves.size() > 0:
			var random_move = valid_moves[randi() % valid_moves.size()]
			last_move = random_move
			match random_move:
				0:
					move_empty(0, -1)
				1:
					move_empty(0, 1)
				2:
					move_empty(-1, 0)
				3:
					move_empty(1, 0)
	move_count = 0
	is_solved = false

func get_valid_moves() -> Array:
	var moves = []
	if empty_pos.x > 0:
		moves.append(2)
	if empty_pos.x < grid_size - 1:
		moves.append(3)
	if empty_pos.y > 0:
		moves.append(0)
	if empty_pos.y < grid_size - 1:
		moves.append(1)
	return moves

func move_empty(dx: int, dy: int) -> bool:
	var new_x = empty_pos.x + dx
	var new_y = empty_pos.y + dy
	
	if new_x >= 0 and new_x < grid_size and new_y >= 0 and new_y < grid_size:
		var old_pos = Vector2i(empty_pos.x, empty_pos.y)
		
		grid[empty_pos.y][empty_pos.x] = grid[new_y][new_x]
		grid[new_y][new_x] = 0
		
		empty_pos = Vector2i(new_x, new_y)
		move_count += 1
		
		tile_moved.emit(Vector2i(new_x, new_y), old_pos)
		
		check_solved()
		return true
	return false

func move_tile(row: int, col: int) -> bool:
	if grid[row][col] == 0:
		return false
	
	var dx = abs(col - empty_pos.x)
	var dy = abs(row - empty_pos.y)
	
	if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
		var move_dx = col - empty_pos.x
		var move_dy = row - empty_pos.y
		return move_empty(move_dx, move_dy)
	
	return false

func get_tile(row: int, col: int) -> int:
	if row >= 0 and row < grid_size and col >= 0 and col < grid_size:
		return grid[row][col]
	return -1

func get_empty_position() -> Vector2i:
	return empty_pos

func get_grid_size() -> int:
	return grid_size

func get_move_count() -> int:
	return move_count

func check_solved():
	var num = 1
	for row in range(grid_size):
		for col in range(grid_size):
			var expected = num if num < total_tiles else 0
			if grid[row][col] != expected:
				is_solved = false
				return
			num += 1
	
	is_solved = true
	puzzle_solved.emit(move_count)

func is_puzzle_solved() -> bool:
	return is_solved

func reset():
	init(grid_size)

func get_grid() -> Array:
	return grid

func set_move_count(count: int):
	move_count = count

func load_state(saved_grid: Array, saved_empty_pos: Vector2i):
	grid = saved_grid
	empty_pos = saved_empty_pos
	is_solved = false