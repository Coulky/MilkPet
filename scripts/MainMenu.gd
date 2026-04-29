extends Control

func _on_snake_button_pressed():
    get_tree().change_scene_to_file("res://scenes/games/snake.tscn")

func _on_tetris_button_pressed():
    get_tree().change_scene_to_file("res://scenes/games/tetris.tscn")

func _on_breakout_button_pressed():
    get_tree().change_scene_to_file("res://scenes/games/breakout.tscn")

func _on_back_button_pressed():
    get_tree().change_scene_to_file("res://scenes/HomePage.tscn")