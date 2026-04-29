extends Control

func _ready():
	update_texts()

func update_texts():
	$TitleLabel.text = GlobalData.translate("game_collection")
	$GamesButton.text = GlobalData.translate("game_library")
	$ContinueButton.text = GlobalData.translate("continue_game")
	$AchievementsButton.text = GlobalData.translate("achievements")
	$SettingsButton.text = GlobalData.translate("settings")
	$QuitButton.text = GlobalData.translate("quit")

func _on_games_button_pressed():
	print("游戏库功能开发中")

func _on_continue_button_pressed():
	print("继续游戏功能开发中")

func _on_achievements_button_pressed():
	print("成就功能开发中")

func _on_settings_button_pressed():
	get_tree().change_scene_to_file("res://scenes/SettingsPage.tscn")

func _on_quit_button_pressed():
	get_tree().quit()
