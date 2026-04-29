extends Node

const GRID_SIZE = 9

var puzzle: Array = []
var solution: Array = []
var player_grid: Array = []
var mistakes: int = 0

func init():
	puzzle = []
	solution = []
	player_grid = []
	mistakes = 0

	for i in range(GRID_SIZE):
		puzzle.append([])
		solution.append([])
		player_grid.append([])
		for j in range(GRID_SIZE):
			puzzle[i].append(0)
			solution[i].append(0)
			player_grid[i].append(0)

func load_game(game_data: Dictionary):
	puzzle = game_data.puzzle
	solution = game_data.solution
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			player_grid[i][j] = puzzle[i][j]

func set_number(row: int, col: int, number: int) -> bool:
	if puzzle[row][col] != 0:
		return false

	if number == solution[row][col]:
		player_grid[row][col] = number
		return true
	else:
		mistakes += 1
		return false

func get_number(row: int, col: int) -> int:
	return player_grid[row][col]

func get_mistakes() -> int:
	return mistakes

func is_original_cell(row: int, col: int) -> bool:
	return puzzle[row][col] != 0

func is_complete() -> bool:
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			if player_grid[i][j] != solution[i][j]:
				return false
	return true

func get_solution_cell(row: int, col: int) -> int:
	return solution[row][col]
