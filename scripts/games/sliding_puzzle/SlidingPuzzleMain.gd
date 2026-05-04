extends Control

const SlidingPuzzleScript = preload("res://scripts/games/sliding_puzzle/SlidingPuzzle.gd")
const GameButtonFactoryScript = preload("res://scripts/common/GameButtonFactory.gd")

var puzzle: Node
var is_running: bool = false
var timer_seconds: int = 0
var current_size: int = 4

func _ready():
	puzzle = SlidingPuzzleScript.new()
	add_child(puzzle)
	
	_setup_buttons()
	_connect_signals()
	start_new_game(4)

func _setup_buttons():
	var window_height = get_window().size.y
	var btn_size = int(window_height * 0.08)
	if btn_size < 60:
		btn_size = 60
	
	var left_panel = get_node_or_null("SlidingPuzzleUI/LeftPanel")
	
	if left_panel:
		GameButtonFactoryScript.create_simple_button(left_panel, "BackButton", "res://assets/images/back.png", _on_back)
		var back_btn = left_panel.get_node_or_null("BackButton")
		if back_btn:
			back_btn.custom_minimum_size = Vector2(btn_size, btn_size)
			back_btn.size = Vector2(btn_size, btn_size)
		
		GameButtonFactoryScript.create_button(left_panel, "RestartButton", "res://assets/images/restart.png", "重开", _on_restart)
		var restart_container = left_panel.get_node_or_null("RestartButtonContainer")
		if restart_container:
			restart_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)
			restart_container.size = Vector2(btn_size, btn_size * 0.8)
		
		GameButtonFactoryScript.create_button(left_panel, "NewGameButton", "res://assets/images/restart.png", "新游戏", _on_new_game)
		var new_game_container = left_panel.get_node_or_null("NewGameButtonContainer")
		if new_game_container:
			new_game_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)
			new_game_container.size = Vector2(btn_size, btn_size * 0.8)
		
		GameButtonFactoryScript.create_button(left_panel, "Size3Button", "res://assets/images/restart.png", "3×3", func(): _on_grid_size_changed(3))
		var size3_container = left_panel.get_node_or_null("Size3ButtonContainer")
		if size3_container:
			size3_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)
			size3_container.size = Vector2(btn_size, btn_size * 0.8)
		
		GameButtonFactoryScript.create_button(left_panel, "Size4Button", "res://assets/images/restart.png", "4×4", func(): _on_grid_size_changed(4))
		var size4_container = left_panel.get_node_or_null("Size4ButtonContainer")
		if size4_container:
			size4_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)
			size4_container.size = Vector2(btn_size, btn_size * 0.8)
		
		GameButtonFactoryScript.create_button(left_panel, "Size5Button", "res://assets/images/restart.png", "5×5", func(): _on_grid_size_changed(5))
		var size5_container = left_panel.get_node_or_null("Size5ButtonContainer")
		if size5_container:
			size5_container.custom_minimum_size = Vector2(btn_size, btn_size * 0.8)
			size5_container.size = Vector2(btn_size, btn_size * 0.8)

func _connect_signals():
	var ui = get_node_or_null("SlidingPuzzleUI")
	if ui:
		ui.tile_clicked.connect(_on_tile_clicked)
		ui.grid_size_changed.connect(_on_ui_grid_size_changed)
		ui.message_dialog_clicked.connect(_on_message_dialog_clicked)
	
	puzzle.puzzle_solved.connect(_on_puzzle_solved)

func start_new_game(new_grid_size: int = 4):
	current_size = new_grid_size
	timer_seconds = 0
	is_running = true
	
	puzzle.init(new_grid_size)
	puzzle.shuffle(150)
	
	var ui = get_node_or_null("SlidingPuzzleUI")
	if ui:
		ui.set_grid_size(new_grid_size)
		ui.set_buttons_enabled(true)
		ui.hide_message()
		call_deferred("_update_display")
	
	GameTimer.timer_init("SlidingPuzzle", 1.0, false)
	if GameTimer.timer_timeout.is_connected(_on_timer_tick):
		GameTimer.timer_timeout.disconnect(_on_timer_tick)
	GameTimer.timer_timeout.connect(_on_timer_tick)

func _update_display():
	var ui = get_node_or_null("SlidingPuzzleUI")
	if ui:
		ui.update_display(puzzle)
		ui.update_move_count(puzzle.get_move_count())
		ui.update_timer(timer_seconds)

func _on_tile_clicked(row: int, col: int):
	if not is_running:
		is_running = true
	
	if puzzle.move_tile(row, col):
		_update_display()

func _on_timer_tick():
	if is_running:
		timer_seconds += 1
		_update_display()

func _on_puzzle_solved(move_count: int):
	is_running = false
	GameTimer.timer_clear()
	
	var ui = get_node_or_null("SlidingPuzzleUI")
	if ui:
		ui.set_buttons_enabled(false)
		var mins = int(timer_seconds / 60.0)
		var secs = timer_seconds % 60
		ui.show_message("恭喜完成！\n用时: %02d:%02d\n步数: %d\n网格: %d×%d" % [mins, secs, move_count, current_size, current_size])

func _on_new_game():
	GameTimer.timer_clear()
	start_new_game(current_size)

func _on_restart():
	_on_new_game()

func _on_back():
	_save_progress()
	GameTimer.timer_clear()
	get_tree().change_scene_to_file("res://scenes/games/HomePage.tscn")

func _on_grid_size_changed(new_grid_size: int):
	if new_grid_size != current_size:
		GameTimer.timer_clear()
		start_new_game(new_grid_size)

func _on_ui_grid_size_changed(_grid_size_param: int):
	pass

func _on_message_dialog_clicked():
	var ui = get_node_or_null("SlidingPuzzleUI")
	if ui:
		ui.hide_message()
	_clear_saved_game()
	GameTimer.timer_clear()
	get_tree().change_scene_to_file("res://scenes/games/HomePage.tscn")

func _clear_saved_game():
	SaveData.clear_cached_game_on_disk("sliding_puzzle")
	SaveData.clear_game_cache()

func _save_progress():
	if is_running and not puzzle.is_puzzle_solved():
		var save_data = {
			"game_name": "sliding_puzzle",
			"grid_size": current_size,
			"timer": timer_seconds,
			"move_count": puzzle.get_move_count(),
			"grid": puzzle.get_grid(),
			"empty_pos": [puzzle.get_empty_position().x, puzzle.get_empty_position().y],
			"last_save_time": Time.get_unix_time_from_system()
		}
		
		SaveData.init_game_cache("sliding_puzzle", str(current_size) + "x" + str(current_size), {
			"grid_size": current_size,
			"timer": timer_seconds,
			"move_count": puzzle.get_move_count(),
			"grid": puzzle.get_grid(),
			"empty_pos": [puzzle.get_empty_position().x, puzzle.get_empty_position().y]
		})
		
		SaveData.update_game_cache({
			"grid_size": current_size,
			"timer": timer_seconds,
			"move_count": puzzle.get_move_count(),
			"grid": puzzle.get_grid(),
			"empty_pos": [puzzle.get_empty_position().x, puzzle.get_empty_position().y]
		})
		
		SaveData.save_game_cache_to_disk()

func load_saved_game() -> bool:
	if not SaveData.has_cached_game("sliding_puzzle"):
		return false
	
	SaveData.load_game_cache("sliding_puzzle")
	var cached_data = SaveData.get_cached_game_data()
	
	if cached_data and "current_state" in cached_data:
		var state = cached_data["current_state"]
		current_size = state.get("grid_size", 4)
		timer_seconds = state.get("timer", 0)
		
		puzzle.init(current_size)
		puzzle.load_state(state.get("grid", []), Vector2i(state.get("empty_pos", [3, 3])[0], state.get("empty_pos", [3, 3])[1]))
		puzzle.set_move_count(state.get("move_count", 0))
		
		is_running = true
		
		var ui = get_node_or_null("SlidingPuzzleUI")
		if ui:
			ui.set_grid_size(current_size)
			ui.set_buttons_enabled(true)
			ui.hide_message()
			call_deferred("_update_display")
		
		GameTimer.timer_init("SlidingPuzzle", 1.0, false)
		if GameTimer.timer_timeout.is_connected(_on_timer_tick):
			GameTimer.timer_timeout.disconnect(_on_timer_tick)
		GameTimer.timer_timeout.connect(_on_timer_tick)
		
		return true
	
	return false

func has_saved_game() -> bool:
	return SaveData.has_cached_game("sliding_puzzle")

func _exit_tree():
	if is_running:
		_save_progress()
