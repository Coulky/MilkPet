extends Node

var sudoku_stats: Dictionary = {
	"easy_completed": [],
	"medium_completed": [],
	"hard_completed": [],
	"last_played_id": null
}

const STATS_FILE_PATH = "user://sudoku_stats.save"

func _ready():
	load_stats()

func load_stats():
	if FileAccess.file_exists(STATS_FILE_PATH):
		var file = FileAccess.open(STATS_FILE_PATH, FileAccess.READ)
		if file:
			var data = file.get_var()
			file.close()
			if data is Dictionary:
				sudoku_stats = data

func save_stats():
	var file = FileAccess.open(STATS_FILE_PATH, FileAccess.WRITE)
	if file:
		file.store_var(sudoku_stats)
		file.close()

func get_easy_completed() -> Array:
	return sudoku_stats.get("easy_completed", [])

func get_medium_completed() -> Array:
	return sudoku_stats.get("medium_completed", [])

func get_hard_completed() -> Array:
	return sudoku_stats.get("hard_completed", [])

func get_last_played_id():
	return sudoku_stats.get("last_played_id")

func set_last_played_id(puzzle_id: Variant):
	sudoku_stats["last_played_id"] = puzzle_id
	save_stats()

func add_to_completed(puzzle_id: String, difficulty: String):
	match difficulty:
		"easy":
			if not puzzle_id in sudoku_stats["easy_completed"]:
				sudoku_stats["easy_completed"].append(puzzle_id)
				sudoku_stats["easy_completed"].sort()
		"medium":
			if not puzzle_id in sudoku_stats["medium_completed"]:
				sudoku_stats["medium_completed"].append(puzzle_id)
				sudoku_stats["medium_completed"].sort()
		"hard":
			if not puzzle_id in sudoku_stats["hard_completed"]:
				sudoku_stats["hard_completed"].append(puzzle_id)
				sudoku_stats["hard_completed"].sort()
	save_stats()

func get_next_puzzle_id(all_ids: Array) -> String:
	all_ids.sort()
	
	var last_id = get_last_played_id()
	
	if last_id == null or all_ids.size() == 0:
		if all_ids.size() > 0:
			set_last_played_id(all_ids[0])
			return all_ids[0]
		else:
			return ""
	
	var last_index = all_ids.find(last_id)
	
	if last_index == -1:
		if all_ids.size() > 0:
			set_last_played_id(all_ids[0])
			return all_ids[0]
		else:
			return ""
	
	var next_index = (last_index + 1) % all_ids.size()
	var next_id = all_ids[next_index]
	
	var difficulty = get_difficulty_for_puzzle(next_id)
	if difficulty != "":
		set_last_played_id(next_id)
		return get_next_puzzle_id(all_ids)
	else:
		set_last_played_id(next_id)
		return next_id

func get_difficulty_for_puzzle(puzzle_id: String) -> String:
	if puzzle_id in sudoku_stats["easy_completed"]:
		return "easy"
	elif puzzle_id in sudoku_stats["medium_completed"]:
		return "medium"
	elif puzzle_id in sudoku_stats["hard_completed"]:
		return "hard"
	return ""

func record_new_game(puzzle_id: String):
	set_last_played_id(puzzle_id)

func record_game_complete(puzzle_id: String, difficulty: String):
	add_to_completed(puzzle_id, difficulty)

func clear_stats():
	sudoku_stats = {
		"easy_completed": [],
		"medium_completed": [],
		"hard_completed": [],
		"last_played_id": null
	}
	save_stats()
