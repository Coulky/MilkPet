extends Control

const Match3LogicScript = preload("res://scripts/games/match3/Match3Logic.gd")
const GameButtonFactoryScript = preload("res://scripts/common/GameButtonFactory.gd")

var match3_logic: Node
var is_running: bool = false

func _ready():
	match3_logic = Match3LogicScript.new()
	add_child(match3_logic)
	
	_setup_buttons()
	_connect_signals()
	start_new_game()

func _setup_buttons():
	var window_height = get_window().size.y
	var btn_size = int(window_height * 0.08)
	if btn_size < 60:
		btn_size = 60
	
	var left_panel = get_node_or_null("Match3UI/LeftPanel")
	
	if left_panel:
		GameButtonFactoryScript.create_simple_button(left_panel, "BackButton", "res://assets/images/back.png", _on_back)
		var back_btn = left_panel.get_node_or_null("BackButton")
		if back_btn:
			back_btn.custom_minimum_size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(left_panel, "RestartButton", "res://assets/images/restart.png", "重开", _on_restart)
		var restart_container = left_panel.get_node_or_null("RestartButtonContainer")
		if restart_container:
			restart_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)

func _connect_signals():
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.gem_selected.connect(_on_gem_selected)
	
	match3_logic.score_changed.connect(_on_score_changed)
	match3_logic.moves_changed.connect(_on_moves_changed)
	match3_logic.game_won.connect(_on_game_won)
	match3_logic.game_over.connect(_on_game_over)

func start_new_game():
	is_running = true
	match3_logic.init()
	
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.update_display(match3_logic)
		ui.update_score(0)
		ui.update_moves(0)
		ui.update_target(match3_logic.get_target_score())
		ui.set_buttons_enabled(true)
		ui.hide_message()

func _update_display():
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.update_display(match3_logic)

func _on_gem_selected(row: int, col: int):
	if not is_running:
		return
	
	match3_logic.select_gem(row, col)
	
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.update_selection(match3_logic.selected_pos)
		call_deferred("_update_display")

func _on_score_changed(new_score: int):
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.update_score(new_score)

func _on_moves_changed(new_moves: int):
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.update_moves(new_moves)

func _on_game_won():
	is_running = false
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.set_buttons_enabled(false)
		ui.show_message("恭喜完成！\n分数: " + str(match3_logic.get_score()))

func _on_game_over():
	is_running = false
	var ui = get_node_or_null("Match3UI")
	if ui:
		ui.set_buttons_enabled(false)
		ui.show_message("游戏结束！\n分数: " + str(match3_logic.get_score()))

func _on_back():
	get_tree().change_scene_to_file("res://scenes/games/HomePage.tscn")

func _on_restart():
	start_new_game()
