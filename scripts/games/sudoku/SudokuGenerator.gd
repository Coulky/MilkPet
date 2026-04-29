extends Node

const GRID_SIZE = 9

var rng: RandomNumberGenerator

func _init():
	rng = RandomNumberGenerator.new()

func generate() -> Dictionary:
	var solution = generate_solution()
	var puzzle = solution.duplicate(true)
	var cells_to_remove = 40

	var removed = 0
	while removed < cells_to_remove:
		var row = rng.randi_range(0, 8)
		var col = rng.randi_range(0, 8)
		if puzzle[row][col] != 0:
			puzzle[row][col] = 0
			removed += 1

	return {
		"puzzle": puzzle,
		"solution": solution
	}

func generate_solution() -> Array:
	var grid = []
	for i in range(GRID_SIZE):
		grid.append([])
		for j in range(GRID_SIZE):
			grid[i].append(0)

	fill_grid(grid, 0, 0)
	return grid

func fill_grid(grid: Array, row: int, col: int) -> bool:
	if row == GRID_SIZE:
		return true

	if col == GRID_SIZE:
		return fill_grid(grid, row + 1, 0)

	var numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	numbers.shuffle()

	for number in numbers:
		if is_valid(grid, row, col, number):
			grid[row][col] = number
			if fill_grid(grid, row, col + 1):
				return true
			grid[row][col] = 0

	return false

func is_valid(grid: Array, row: int, col: int, number: int) -> bool:
	for i in range(GRID_SIZE):
		if grid[row][i] == number:
			return false

	for i in range(GRID_SIZE):
		if grid[i][col] == number:
			return false

	var box_row = (row / 3) * 3
	var box_col = (col / 3) * 3
	for i in range(3):
		for j in range(3):
			if grid[box_row + i][box_col + j] == number:
				return false

	return true
