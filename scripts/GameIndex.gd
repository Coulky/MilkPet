extends Control

func _ready():
	update_texts()
	GlobalData.language_changed.connect(_on_language_changed)
	update_continue_button()

func update_texts():
	$TitleLabel.text = GlobalData.translate("game_collection")
	$NewGameButton.text = GlobalData.translate("new_game")
	$ContinueButton.text = GlobalData.translate("continue_game")
	$AchievementsButton.text = GlobalData.translate("achievements")
	$SettingsButton.text = GlobalData.translate("settings")
	$QuitButton.text = GlobalData.translate("quit")

func update_continue_button():
	var has_cached = has_any_cached_game()
	$ContinueButton.disabled = not has_cached

func has_any_cached_game() -> bool:
	var game_ids = SaveData.get_all_ids()
	for game_id in game_ids:
		if SaveData.has_cached_game(game_id):
			return true
	return false

func get_last_cached_game() -> Dictionary:
	var last_game = null
	var last_time = 0
	var game_ids = SaveData.get_all_ids()

	for game_id in game_ids:
		if SaveData.has_cached_game(game_id):
			var game_data = SaveData.get_game(game_id)
			var cache_time = game_data.cached_game.last_save_time if "cached_game" in game_data else 0
			if cache_time > last_time:
				last_time = cache_time
				last_game = game_data.cached_game

	return last_game if last_game else {}

func _on_new_game_button_pressed():
	get_tree().change_scene_to_file("res://scenes/games/HomePage.tscn")

func _on_continue_button_pressed():
	var last_game = get_last_cached_game()
	if last_game and last_game.game_name:
		SaveData.load_game_cache(last_game.game_name)
		if last_game.game_name == "sudoku":
			get_tree().change_scene_to_file("res://scenes/games/sudoku/sudoku.tscn")
		elif last_game.game_name == "homepage":
			get_tree().change_scene_to_file("res://scenes/games/HomePage.tscn")

func _on_achievements_button_pressed():
	get_tree().change_scene_to_file("res://scenes/Achievements.tscn")

func _on_settings_button_pressed():
	get_tree().change_scene_to_file("res://scenes/SettingsPage.tscn")

func _on_quit_button_pressed():
	get_tree().quit()

func _on_language_changed():
	update_texts()

func _exit_tree():
	GlobalData.language_changed.disconnect(_on_language_changed)