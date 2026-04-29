extends Node

const GRID_SIZE = 9
const SudokuPuzzlesScript = preload("res://scripts/games/sudoku/SudokuPuzzles.gd")

var rng: RandomNumberGenerator
var sudoku_puzzles: Node
var recent_puzzle_ids: Array = []

func _init():
	rng = RandomNumberGenerator.new()
	sudoku_puzzles = SudokuPuzzlesScript.new()

func generate(level: String = "easy") -> Dictionary:
	var puzzle_ids = sudoku_puzzles.get_all_puzzle_ids()

	var available_ids = puzzle_ids.filter(func(id):
		return not recent_puzzle_ids.has(id)
	)

	var ids_to_choose = available_ids if available_ids.size() > 0 else puzzle_ids

	var random_index = rng.randi_range(0, ids_to_choose.size() - 1)
	var selected_id = ids_to_choose[random_index]
	var one_d_grid = sudoku_puzzles.get_puzzle(selected_id)

	var complete_grid = sudoku_puzzles.convert_to_2d(one_d_grid)

	recent_puzzle_ids.insert(0, selected_id)
	if recent_puzzle_ids.size() > 10:
		recent_puzzle_ids.pop_back()

	var puzzle = remove_numbers(complete_grid.duplicate(true), level)

	return {
		"grid": puzzle,
		"original": complete_grid,
		"id": selected_id
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
