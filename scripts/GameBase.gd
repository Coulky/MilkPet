extends Node2D

signal game_over(score: int)
signal back_to_menu()

var score: int = 0
var is_running: bool = false

func start_game():
    is_running = true

func pause_game():
    is_running = false

func reset_game():
    score = 0
    is_running = false

func _on_back_button_pressed():
    emit_signal("back_to_menu")