extends Node

signal game_selected(game_name: String)

var current_game: Node2D

func select_game(game_name: String):
    emit_signal("game_selected", game_name)

func set_current_game(game: Node2D):
    current_game = game

func get_current_game() -> Node2D:
    return current_game