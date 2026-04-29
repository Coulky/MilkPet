extends Node

var current_game_cache: Dictionary = {}

func get_game(game_id: String) -> Dictionary:
	if game_id in GlobalData.save_data.games:
		return GlobalData.save_data.games[game_id]
	return {}

func save_game(game_id: String, data: Dictionary):
	GlobalData.save_data.games[game_id] = data
	GlobalData.save_save_data()

func create_game(game_id: String):
	if has_game(game_id):
		return
	GlobalData.save_data.games[game_id] = {
		"high_score": 0,
		"play_count": 0,
		"last_played": Time.get_unix_time_from_system()
	}
	GlobalData.save_save_data()

func update_score(game_id: String, score: int):
	if not has_game(game_id):
		create_game(game_id)
	var game_data = GlobalData.save_data.games[game_id]
	if score > game_data.get("high_score", 0):
		game_data["high_score"] = score
	game_data["last_played"] = Time.get_unix_time_from_system()
	GlobalData.save_save_data()

func add_play(game_id: String):
	if not has_game(game_id):
		create_game(game_id)
	GlobalData.save_data.games[game_id]["play_count"] += 1
	GlobalData.save_data.games[game_id]["last_played"] = Time.get_unix_time_from_system()
	GlobalData.save_save_data()

func has_game(game_id: String) -> bool:
	return game_id in GlobalData.save_data.games

func get_high_score(game_id: String) -> int:
	if has_game(game_id):
		return GlobalData.save_data.games[game_id].get("high_score", 0)
	return 0

func get_play_count(game_id: String) -> int:
	if has_game(game_id):
		return GlobalData.save_data.games[game_id].get("play_count", 0)
	return 0

func get_all_ids() -> Array:
	return GlobalData.save_data.games.keys()

func get_summary() -> Array:
	var list = []
	for game_id in GlobalData.save_data.games:
		var data = GlobalData.save_data.games[game_id]
		list.append({
			"id": game_id,
			"high_score": data.get("high_score", 0),
			"play_count": data.get("play_count", 0),
			"last_played": data.get("last_played", 0)
		})
	return list

func init_game_cache(game_name: String, difficulty: String, initial_data: Dictionary):
	current_game_cache = {
		"game_name": game_name,
		"difficulty": difficulty,
		"initial_data": initial_data,
		"current_state": initial_data.duplicate(true),
		"start_time": Time.get_unix_time_from_system(),
		"last_save_time": Time.get_unix_time_from_system()
	}

func update_game_cache(state_data: Dictionary):
	if current_game_cache.is_empty():
		return
	current_game_cache["current_state"] = state_data.duplicate(true)
	current_game_cache["last_save_time"] = Time.get_unix_time_from_system()

func save_game_cache_to_disk():
	if current_game_cache.is_empty():
		return
	var game_name = current_game_cache.get("game_name", "")
	if game_name == "":
		return
	
	if not has_game(game_name):
		create_game(game_name)
	
	GlobalData.save_data.games[game_name]["cached_game"] = current_game_cache
	GlobalData.save_save_data()

func load_game_cache(game_name: String) -> bool:
	if not has_game(game_name):
		return false
	
	var game_data = GlobalData.save_data.games[game_name]
	if "cached_game" in game_data:
		current_game_cache = game_data["cached_game"].duplicate(true)
		return true
	return false

func has_cached_game(game_name: String) -> bool:
	if not has_game(game_name):
		return false
	var game_data = GlobalData.save_data.games[game_name]
	return "cached_game" in game_data and not game_data["cached_game"].is_empty()

func get_cached_game_data() -> Dictionary:
	return current_game_cache.duplicate(true)

func get_current_game_name() -> String:
	return current_game_cache.get("game_name", "")

func get_current_difficulty() -> String:
	return current_game_cache.get("difficulty", "")

func get_initial_data() -> Dictionary:
	return current_game_cache.get("initial_data", {}).duplicate(true)

func get_current_state() -> Dictionary:
	return current_game_cache.get("current_state", {}).duplicate(true)

func clear_game_cache():
	current_game_cache = {}

func clear_cached_game_on_disk(game_name: String):
	if has_game(game_name):
		var game_data = GlobalData.save_data.games[game_name]
		if "cached_game" in game_data:
			game_data.erase("cached_game")
			GlobalData.save_save_data()
