extends Node2D

@onready var game_manager = get_node("/root/GameManager")

func _ready():
    game_manager.game_selected.connect(_on_game_selected)

func _on_game_selected(game_name: String):
    var game_scene = load("res://scenes/games/" + game_name + ".tscn")
    if game_scene:
        var game_instance = game_scene.instantiate()
        add_child(game_instance)
        game_manager.set_current_game(game_instance)
        
        if game_instance.has_signal("back_to_menu"):
            game_instance.back_to_menu.connect(_on_back_to_menu)
        if game_instance.has_signal("game_over"):
            game_instance.game_over.connect(_on_game_over)

func _on_back_to_menu():
    clear_current_game()
    get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _on_game_over(score: int):
    print("Game over! Score: ", score)

func clear_current_game():
    if game_manager.get_current_game():
        game_manager.get_current_game().queue_free()
        game_manager.set_current_game(null)