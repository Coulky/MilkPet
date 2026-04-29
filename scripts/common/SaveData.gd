extends Node

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
