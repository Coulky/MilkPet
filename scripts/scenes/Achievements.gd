extends Control

var achievement_list: VBoxContainer
var back_button: Button
var title_label: Label

var achievement_definitions = {
	"sudoku_easy": {
		"name": "数独初级",
		"description": "完成简单难度棋盘",
		"thresholds": [1, 10, 50],
		"stars": [1, 2, 3]
	},
	"sudoku_medium": {
		"name": "数独中级",
		"description": "完成中等难度棋盘",
		"thresholds": [1, 10, 50],
		"stars": [1, 2, 3]
	},
	"sudoku_hard": {
		"name": "数独高级",
		"description": "完成困难难度棋盘",
		"thresholds": [1, 10, 50],
		"stars": [1, 2, 3]
	}
}

func _ready():
	_setup_nodes()
	_refresh_achievements()

func _setup_nodes():
	title_label = get_node("TitleLabel")
	back_button = get_node("BackButton")
	achievement_list = get_node("AchievementList")
	
	back_button.pressed.connect(_on_back_pressed)

func _refresh_achievements():
	for child in achievement_list.get_children():
		child.queue_free()
	
	for achievement_id in achievement_definitions.keys():
		var achievement_data = achievement_definitions[achievement_id]
		var progress = GlobalData.get_achievement_progress(achievement_id)
		var stars = GlobalData.get_achievement_stars(achievement_id)
		
		var achievement_panel = _create_achievement_panel(achievement_id, achievement_data, progress, stars)
		achievement_list.add_child(achievement_panel)

func _create_achievement_panel(achievement_id: String, data: Dictionary, progress: int, stars: int) -> Control:
	var panel = PanelContainer.new()
	panel.add_theme_stylebox_override("panel", _get_panel_stylebox())
	
	var hbox = HBoxContainer.new()
	hbox.custom_minimum_size = Vector2(0, 80)
	panel.add_child(hbox)
	
	var info_vbox = VBoxContainer.new()
	info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(info_vbox)
	
	var name_label = Label.new()
	name_label.text = data.name
	name_label.add_theme_font_size_override("font_size", 24)
	info_vbox.add_child(name_label)
	
	var desc_label = Label.new()
	desc_label.text = data.description
	desc_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	info_vbox.add_child(desc_label)
	
	var progress_label = Label.new()
	progress_label.text = "进度: " + str(progress) + "/" + str(data.thresholds[2])
	progress_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
	info_vbox.add_child(progress_label)
	
	var stars_hbox = HBoxContainer.new()
	stars_hbox.alignment = BoxContainer.ALIGNMENT_END
	hbox.add_child(stars_hbox)
	
	for i in range(3):
		var star_label = Label.new()
		if i < stars:
			star_label.text = "*"
			star_label.add_theme_color_override("font_color", Color(1, 0.8, 0))
		else:
			star_label.text = "*"
			star_label.add_theme_color_override("font_color", Color(0.3, 0.3, 0.3))
		star_label.add_theme_font_size_override("font_size", 32)
		stars_hbox.add_child(star_label)
	
	return panel

func _get_panel_stylebox() -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.15, 0.15, 0.2, 0.8)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(16)
	return style

func _on_back_pressed():
	get_tree().change_scene_to_file("res://scenes/GameIndex.tscn")
