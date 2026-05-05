extends Node

const GEM_RED = 0
const GEM_BLUE = 1
const GEM_GREEN = 2
const GEM_YELLOW = 3
const GEM_PURPLE = 4
const GEM_ORANGE = 5
const GRID_SIZE = 8
var grid: Array = []
var selected_pos: Vector2 = Vector2(-1, -1)
var is_animating: bool = false
var score: int = 0
var moves: int = 0
var target_score: int = 1000

signal move_made(from_pos, to_pos)
signal match_found(matches)
signal score_changed(new_score)
signal moves_changed(new_moves)
signal game_won
signal game_over

func _ready():
	init()

func init():
	grid = []
	score = 0
	moves = 0
	selected_pos = Vector2(-1, -1)
	is_animating = false
	
	for row in range(GRID_SIZE):
		grid.append([])
		for col in range(GRID_SIZE):
			var gem_type
			while true:
				gem_type = randi() % 6
				if not _would_create_match(row, col, gem_type):
					break
			grid[row].append(gem_type)

func _would_create_match(row: int, col: int, gem_type: int) -> bool:
	if col >= 2 and grid[row][col-1] == gem_type and grid[row][col-2] == gem_type:
		return true
	if row >= 2 and grid[row-1][col] == gem_type and grid[row-2][col] == gem_type:
		return true
	return false

func get_gem(row: int, col: int) -> int:
	if row >= 0 and row < GRID_SIZE and col >= 0 and col < GRID_SIZE:
		return grid[row][col]
	return -1

func select_gem(row: int, col: int):
	if is_animating:
		return
	
	if selected_pos.x == -1:
		selected_pos = Vector2(row, col)
	elif selected_pos == Vector2(row, col):
		selected_pos = Vector2(-1, -1)
	else:
		if _is_adjacent(selected_pos, Vector2(row, col)):
			_try_swap(selected_pos.x, selected_pos.y, row, col)
			selected_pos = Vector2(-1, -1)
		else:
			selected_pos = Vector2(row, col)

func _is_adjacent(pos1: Vector2, pos2: Vector2) -> bool:
	var dx = abs(pos1.x - pos2.x)
	var dy = abs(pos1.y - pos2.y)
	return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

func _try_swap(row1: int, col1: int, row2: int, col2: int) -> bool:
	_swap_gems(row1, col1, row2, col2)
	
	var matches = _find_all_matches()
	if matches.size() > 0:
		moves += 1
		moves_changed.emit(moves)
		move_made.emit(Vector2(col1, row1), Vector2(col2, row2))
		_process_matches(matches)
		return true
	else:
		_swap_gems(row1, col1, row2, col2)
		return false

func _swap_gems(row1: int, col1: int, row2: int, col2: int):
	var temp = grid[row1][col1]
	grid[row1][col1] = grid[row2][col2]
	grid[row2][col2] = temp

func _find_all_matches() -> Array:
	var all_matches = []
	var checked = {}
	
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			var match_result = _check_match_at(row, col)
			if match_result.size() > 0:
				for pos in match_result:
					var key = str(pos.x) + "_" + str(pos.y)
					if not checked.has(key):
						checked[key] = true
						all_matches.append(pos)
	
	return all_matches

func _check_match_at(row: int, col: int) -> Array:
	var matches = []
	var gem_type = grid[row][col]
	
	if gem_type == -1 or gem_type == null:
		return matches
	
	var horizontal = [[row, col]]
	var c = col - 1
	while c >= 0 and grid[row][c] == gem_type:
		horizontal.prepend([row, c])
		c -= 1
	c = col + 1
	while c < GRID_SIZE and grid[row][c] == gem_type:
		horizontal.append([row, c])
		c += 1
	
	if horizontal.size() >= 3:
		for pos in horizontal:
			matches.append(Vector2(pos[1], pos[0]))
	
	var vertical = [[row, col]]
	var r = row - 1
	while r >= 0 and grid[r][col] == gem_type:
		vertical.prepend([r, col])
		r -= 1
	r = row + 1
	while r < GRID_SIZE and grid[r][col] == gem_type:
		vertical.append([r, col])
		r += 1
	
	if vertical.size() >= 3:
		for pos in vertical:
			if not matches.has(Vector2(pos[1], pos[0])):
				matches.append(Vector2(pos[1], pos[0]))
	
	return matches

func _process_matches(matches: Array):
	is_animating = true
	
	var points = matches.size() * 10
	score += points
	score_changed.emit(score)
	match_found.emit(matches)
	
	for pos in matches:
		grid[pos.y][pos.x] = -1
	
	call_deferred("_drop_gems")
	call_deferred("_fill_empty")
	
	await get_tree().create_timer(0.3).timeout
	
	var new_matches = _find_all_matches()
	if new_matches.size() > 0:
		_process_matches(new_matches)
	else:
		is_animating = false
		
		if score >= target_score:
			game_won.emit()
		elif moves >= 30:
			game_over.emit()

func _drop_gems():
	for col in range(GRID_SIZE):
		var empty_spots = 0
		for row in range(GRID_SIZE - 1, -1, -1):
			if grid[row][col] == -1:
				empty_spots += 1
			elif empty_spots > 0:
				grid[row + empty_spots][col] = grid[row][col]
				grid[row][col] = -1

func _fill_empty():
	for col in range(GRID_SIZE):
		for row in range(GRID_SIZE):
			if grid[row][col] == -1:
				grid[row][col] = randi() % 6

func get_grid() -> Array:
	return grid

func get_score() -> int:
	return score

func get_moves() -> int:
	return moves

func get_target_score() -> int:
	return target_score

func set_target_score(target: int):
	target_score = target

func is_game_over() -> bool:
	return score >= target_score or moves >= 30
