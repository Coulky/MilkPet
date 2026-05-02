extends Node

const GRID_SIZE = 9

var current_sudoku: Array = []
var original_sudoku: Array = []
var notes: Dictionary = {}
var hint_cell: Dictionary = {}
var incorrect_count: int = 3

func init():
	current_sudoku = []
	original_sudoku = []
	notes = {}
	hint_cell = {}
	incorrect_count = 3

	for i in range(GRID_SIZE):
		current_sudoku.append([])
		original_sudoku.append([])
		for j in range(GRID_SIZE):
			current_sudoku[i].append(0)
			original_sudoku[i].append(0)

func load_game(game_data: Dictionary):
	current_sudoku = game_data.grid.duplicate(true)
	original_sudoku = game_data.original.duplicate(true)
	notes = {}

func set_number(row: int, col: int, num: int) -> bool:
	if original_sudoku[row][col] != 0:
		return false

	if num == original_sudoku[row][col]:
		current_sudoku[row][col] = num
		remove_related_notes(row, col, num)
		return true
	else:
		incorrect_count -= 1
		return false

func get_number(row: int, col: int) -> int:
	return current_sudoku[row][col]

func get_original_number(row: int, col: int) -> int:
	return original_sudoku[row][col]

func is_original_cell(row: int, col: int) -> bool:
	return original_sudoku[row][col] != 0

func remove_related_notes(row: int, col: int, num: int):
	# 移除同行同列同宫格中的该数字笔记
	for c in range(GRID_SIZE):
		var key = str(row) + "," + str(c)
		if notes.has(key) and notes[key].has(num):
			notes[key].erase(num)
			if notes[key].size() == 0:
				notes.erase(key)

	for r in range(GRID_SIZE):
		var key = str(r) + "," + str(col)
		if notes.has(key) and notes[key].has(num):
			notes[key].erase(num)
			if notes[key].size() == 0:
				notes.erase(key)

	var box_row = int(row / 3) * 3
	var box_col = int(col / 3) * 3
	for r in range(box_row, box_row + 3):
		for c in range(box_col, box_col + 3):
			var key = str(r) + "," + str(c)
			if notes.has(key) and notes[key].has(num):
				notes[key].erase(num)
				if notes[key].size() == 0:
					notes.erase(key)

func check_sudoku() -> Dictionary:
	# 检查是否完成
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if current_sudoku[row][col] == 0:
				return {"success": false, "message": "数独还未完成，请继续填写"}

	# 检查行
	for row in range(GRID_SIZE):
		var numbers = {}
		for col in range(GRID_SIZE):
			var num = current_sudoku[row][col]
			if numbers.has(num):
				return {"success": false, "message": "第" + str(row + 1) + "行有重复数字"}
			numbers[num] = true

	# 检查列
	for col in range(GRID_SIZE):
		var numbers = {}
		for row in range(GRID_SIZE):
			var num = current_sudoku[row][col]
			if numbers.has(num):
				return {"success": false, "message": "第" + str(col + 1) + "列有重复数字"}
			numbers[num] = true

	# 检查宫格
	for box_row in range(3):
		for box_col in range(3):
			var numbers = {}
			for row in range(box_row * 3, box_row * 3 + 3):
				for col in range(box_col * 3, box_col * 3 + 3):
					var num = current_sudoku[row][col]
					if numbers.has(num):
						return {"success": false, "message": "第" + str(box_row * 3 + box_col + 1) + "个宫格有重复数字"}
					numbers[num] = true

	return {"success": true, "message": "恭喜你，数独挑战成功！"}

func generate_auto_notes():
	notes = {}

	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if current_sudoku[row][col] == 0:
				var used_numbers = {}

				# 检查行
				for c in range(GRID_SIZE):
					if current_sudoku[row][c] != 0:
						used_numbers[current_sudoku[row][c]] = true

				# 检查列
				for r in range(GRID_SIZE):
					if current_sudoku[r][col] != 0:
						used_numbers[current_sudoku[r][col]] = true

				# 检查宫格
				var box_row = int(row / 3) * 3
				var box_col = int(col / 3) * 3
				for r in range(box_row, box_row + 3):
					for c in range(box_col, box_col + 3):
						if current_sudoku[r][c] != 0:
							used_numbers[current_sudoku[r][c]] = true

				# 获取可能的数字
				var possible_numbers = []
				for num in range(1, 10):
					if not used_numbers.has(num):
						possible_numbers.append(num)

				if possible_numbers.size() > 0:
					var key = str(row) + "," + str(col)
					notes[key] = possible_numbers

func get_notes(row: int, col: int) -> Array:
	var key = str(row) + "," + str(col)
	return notes.get(key, [])

func set_note(row: int, col: int, num: int):
	if original_sudoku[row][col] != 0:
		return

	var key = str(row) + "," + str(col)
	if not notes.has(key):
		notes[key] = []

	if notes[key].has(num):
		notes[key].erase(num)
		if notes[key].size() == 0:
			notes.erase(key)
	else:
		notes[key].append(num)
		notes[key].sort()

func get_remaining_cells() -> int:
	var remaining = 0
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if current_sudoku[row][col] == 0:
				remaining += 1
	return remaining

func give_hint() -> bool:
	var empty_cells = []
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if current_sudoku[row][col] == 0:
				empty_cells.append({"row": row, "col": col})

	if empty_cells.size() == 0:
		return false

	# 随机选择一个空格
	var random_index = randi() % empty_cells.size()
	var cell = empty_cells[random_index]

	var correct_number = original_sudoku[cell.row][cell.col]
	if correct_number == 0:
		return false

	# 填入正确数字
	current_sudoku[cell.row][cell.col] = correct_number

	# 记录提示位置
	hint_cell = {"row": cell.row, "col": cell.col, "time": Time.get_ticks_msec()}

	# 移除相关笔记
	var key = str(cell.row) + "," + str(cell.col)
	notes.erase(key)
	remove_related_notes(cell.row, cell.col, correct_number)

	return true

func get_hint_cell() -> Dictionary:
	return hint_cell

func clear_hint_cell():
	hint_cell = {}

func get_incorrect_count() -> int:
	return incorrect_count

# 检查某个位置是否可以填入特定数字（用于验证）
func can_place_number(row: int, col: int, num: int) -> bool:
	if current_sudoku[row][col] != 0:
		return false

	# 检查行
	for c in range(GRID_SIZE):
		if current_sudoku[row][c] == num:
			return false

	# 检查列
	for r in range(GRID_SIZE):
		if current_sudoku[r][col] == num:
			return false

	# 检查宫格
	var box_row = int(row / 3) * 3
	var box_col = int(col / 3) * 3
	for r in range(box_row, box_row + 3):
		for c in range(box_col, box_col + 3):
			if current_sudoku[r][c] == num:
				return false

	return true

# 获取某个格子的所有可能数字
func get_possible_numbers_for_cell(row: int, col: int) -> Array:
	if current_sudoku[row][col] != 0:
		return []

	var used = {}

	for c in range(GRID_SIZE):
		if current_sudoku[row][c] != 0:
			used[current_sudoku[row][c]] = true

	for r in range(GRID_SIZE):
		if current_sudoku[r][col] != 0:
			used[current_sudoku[r][col]] = true

	var box_row = int(row / 3) * 3
	var box_col = int(col / 3) * 3
	for r in range(box_row, box_row + 3):
		for c in range(box_col, box_col + 3):
			if current_sudoku[r][c] != 0:
				used[current_sudoku[r][c]] = true

	var possible = []
	for num in range(1, 10):
		if not used.has(num):
			possible.append(num)

	return possible

# 检查游戏是否结束（生命耗尽）
func is_game_over() -> bool:
	return incorrect_count <= 0

# 重置当前游戏
func reset_game():
	current_sudoku = original_sudoku.duplicate(true)
	notes = {}
	hint_cell = {}
	incorrect_count = 3

# 获取游戏进度（已填格子数）
func get_progress() -> float:
	var filled = 0
	var total = 0
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if original_sudoku[row][col] == 0:
				total += 1
				if current_sudoku[row][col] != 0:
					filled += 1
	if total == 0:
		return 1.0
	return filled / total