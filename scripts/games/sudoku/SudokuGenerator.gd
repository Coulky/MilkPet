extends Node

const GRID_SIZE = 9
const SudokuPuzzlesScript = preload("res://scripts/games/sudoku/SudokuPuzzles.gd")

var rng: RandomNumberGenerator
var sudoku_puzzles: Node

# 星级通关列表 - 存储已完成的棋盘ID
var star1_completed: Array = []  # 简单难度完成
var star2_completed: Array = []  # 中等难度完成
var star3_completed: Array = []  # 困难难度完成

# 当前循环已完成列表
var current_cycle_completed: Array = []

func _init():
	rng = RandomNumberGenerator.new()
	sudoku_puzzles = SudokuPuzzlesScript.new()
	_load_progress()

func _load_progress():
	if "sudoku_star1_completed" in GlobalData.save_data:
		star1_completed = GlobalData.save_data.sudoku_star1_completed
	if "sudoku_star2_completed" in GlobalData.save_data:
		star2_completed = GlobalData.save_data.sudoku_star2_completed
	if "sudoku_star3_completed" in GlobalData.save_data:
		star3_completed = GlobalData.save_data.sudoku_star3_completed
	if "sudoku_cycle_completed" in GlobalData.save_data:
		current_cycle_completed = GlobalData.save_data.sudoku_cycle_completed

func _save_progress():
	GlobalData.save_data.sudoku_star1_completed = star1_completed
	GlobalData.save_data.sudoku_star2_completed = star2_completed
	GlobalData.save_data.sudoku_star3_completed = star3_completed
	GlobalData.save_data.sudoku_cycle_completed = current_cycle_completed
	GlobalData.save_save_data()

func get_star_level(level: String) -> int:
	match level:
		"easy": return 1
		"medium": return 2
		"hard": return 3
		_: return 1

func mark_completed(puzzle_id: String, level: String):
	var star_level = get_star_level(level)

	match star_level:
		1:
			if not star1_completed.has(puzzle_id):
				star1_completed.append(puzzle_id)
		2:
			if not star2_completed.has(puzzle_id):
				star2_completed.append(puzzle_id)
		3:
			if not star3_completed.has(puzzle_id):
				star3_completed.append(puzzle_id)

	if not current_cycle_completed.has(puzzle_id + "_" + str(star_level)):
		current_cycle_completed.append(puzzle_id + "_" + str(star_level))

	_save_progress()

	GlobalData.update_sudoku_achievement(level, get_completed_count_by_level(level))

func get_completed_count_by_level(level: String) -> int:
	match level:
		"easy": return star1_completed.size()
		"medium": return star2_completed.size()
		"hard": return star3_completed.size()
		_: return 0

func generate(level: String = "easy") -> Dictionary:
	var puzzle_ids = sudoku_puzzles.get_all_puzzle_ids()
	var star_level = get_star_level(level)

	# 获取当前难度已完成的列表
	var completed_list = []
	match star_level:
		1: completed_list = star1_completed
		2: completed_list = star2_completed
		3: completed_list = star3_completed

	# 过滤可用棋盘：不在当前难度已完成列表中，且不在本轮循环完成列表中
	var available_ids = puzzle_ids.filter(func(id):
		var ck = id + "_" + str(star_level)
		return not completed_list.has(id) and not current_cycle_completed.has(ck)
	)

	if available_ids.size() == 0:
		var all_difficulties_completed = true
		for id in puzzle_ids:
			var has_easy = current_cycle_completed.has(id + "_1")
			var has_medium = current_cycle_completed.has(id + "_2")
			var has_hard = current_cycle_completed.has(id + "_3")
			if not (has_easy or has_medium or has_hard):
				all_difficulties_completed = false
				break

		if all_difficulties_completed:
			current_cycle_completed = []
			_save_progress()
			available_ids = puzzle_ids.filter(func(id):
				var ck = id + "_" + str(star_level)
				return not completed_list.has(id) and not current_cycle_completed.has(ck)
			)
		else:
			available_ids = puzzle_ids

	# 按顺序选择第一个可用的棋盘
	var selected_id = available_ids[0]

	var one_d_grid = sudoku_puzzles.get_puzzle(selected_id)
	var complete_grid = sudoku_puzzles.convert_to_2d(one_d_grid)

	# 标记为本轮循环已使用
	var cycle_key = selected_id + "_" + str(star_level)
	if not current_cycle_completed.has(cycle_key):
		current_cycle_completed.append(cycle_key)
		_save_progress()

	var puzzle = remove_numbers(complete_grid.duplicate(true), level)

	return {
		"grid": puzzle,
		"original": complete_grid,
		"id": selected_id,
		"star_level": star_level
	}

func remove_numbers(grid: Array, level: String) -> Array:
	var remove_count = 40

	match level:
		"easy": remove_count = 40
		"medium": remove_count = 50
		"hard": remove_count = 60
		_: remove_count = 40

	var count = 0
	while count < remove_count:
		var row = rng.randi_range(0, 8)
		var col = rng.randi_range(0, 8)
		if grid[row][col] != 0:
			grid[row][col] = 0
			count += 1

	return grid

func create_empty_grid() -> Array:
	var grid = []
	for i in range(GRID_SIZE):
		grid.append([])
		for j in range(GRID_SIZE):
			grid[i].append(0)
	return grid

func is_valid(grid: Array, row: int, col: int, num: int) -> bool:
	for i in range(GRID_SIZE):
		if grid[row][i] == num:
			return false

	for i in range(GRID_SIZE):
		if grid[i][col] == num:
			return false

	var box_row = int(row / 3.0) * 3
	var box_col = int(col / 3.0) * 3
	for i in range(3):
		for j in range(3):
			if grid[box_row + i][box_col + j] == num:
				return false

	return true

func _solve_sudoku(grid: Array) -> bool:
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if grid[row][col] == 0:
				var numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
				numbers.shuffle()

				for num in numbers:
					if is_valid(grid, row, col, num):
						grid[row][col] = num

						if _solve_sudoku(grid):
							return true

						grid[row][col] = 0
				return false
	return true

func generate_complete_sudoku(grid: Array):
	_solve_sudoku(grid)

func get_completion_stats() -> Dictionary:
	var total_puzzles = sudoku_puzzles.get_all_puzzle_ids().size()
	return {
		"total": total_puzzles,
		"star1_count": star1_completed.size(),
		"star2_count": star2_completed.size(),
		"star3_count": star3_completed.size(),
		"cycle_progress": current_cycle_completed.size()
	}
