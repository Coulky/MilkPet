extends Control

var games: Array = [
	{"id": "sudoku", "name_key": "sudoku", "scene_path": "res://scenes/games/sudoku/sudoku.tscn"},
	{"id": "tilemap", "name_key": "safe_zone", "scene_path": "res://scenes/games/tilemap.tscn"}
]

func _ready():
	update_ui()
	GlobalData.language_changed.connect(_on_language_changed)
	$BackButton.pressed.connect(_on_back_pressed)

func update_ui():
	var title_label = $TitleLabel
	title_label.text = I18n.translate("game_library")

	var back_button = $BackButton
	back_button.text = I18n.translate("back")

	var games_container = $GamesContainer
	while games_container.get_child_count() > 0:
		games_container.remove_child(games_container.get_child(0))

	for game in games:
		var game_card = create_game_card(game)
		games_container.add_child(game_card)

func create_game_card(game_data: Dictionary) -> Control:
	var card = Control.new()
	card.custom_minimum_size = Vector2(400, 150)
	card.add_theme_color_override("background_color", Color(0.2, 0.2, 0.3))
	card.add_theme_constant_override("border_width", 2)
	card.add_theme_color_override("border_color", Color(0.4, 0.4, 0.5))

	var vbox = VBoxContainer.new()
	vbox.alignment = 1
	card.add_child(vbox)

	var name_label = Label.new()
	name_label.text = I18n.translate(game_data.name_key)
	name_label.add_theme_font_size_override("font_size", 28)
	name_label.add_theme_color_override("font_color", Color(1, 1, 1))
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(name_label)

	var hbox = HBoxContainer.new()
	hbox.alignment = 1
	hbox.add_theme_constant_override("h_separation", 20)
	vbox.add_child(hbox)

	var has_cached = SaveData.has_cached_game(game_data.id)

	if has_cached:
		var continue_button = Button.new()
		continue_button.text = I18n.translate("continue")
		continue_button.custom_minimum_size = Vector2(120, 40)
		continue_button.add_theme_font_size_override("font_size", 18)
		continue_button.pressed.connect(_on_continue_game.bind(game_data))
		hbox.add_child(continue_button)

	var start_button = Button.new()
	start_button.text = I18n.translate("start_game")
	start_button.custom_minimum_size = Vector2(120, 40)
	start_button.add_theme_font_size_override("font_size", 18)
	start_button.pressed.connect(_on_start_game.bind(game_data))
	hbox.add_child(start_button)

	return card

func _on_start_game(game_data: Dictionary):
	SaveData.clear_game_cache()
	SaveData.clear_cached_game_on_disk(game_data.id)
	get_tree().change_scene_to_file(game_data.scene_path)

func _on_continue_game(game_data: Dictionary):
	if SaveData.load_game_cache(game_data.id):
		get_tree().change_scene_to_file(game_data.scene_path)

func _on_back_pressed():
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")

func _on_language_changed():
	update_ui()

func _exit_tree():
	GlobalData.language_changed.disconnect(_on_language_changed)
