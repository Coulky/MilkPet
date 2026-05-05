extends Node

signal language_changed
signal achievement_updated(achievement_id, stars)

var current_language = "zh-CN"
var save_data = {}
var save_file_path = "user://save_data.json"

var sudoku_achievements_def = {
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
	load_save_data()
	apply_window_settings()

func translate(key: String) -> String:
	return I18n.translate(key)

func get_lang_display_name(lang_code: String) -> String:
	return I18n.get_display_name(lang_code)

func set_language(lang: String):
	if lang in I18n.get_all_codes():
		current_language = lang
		save_data.settings.language = lang
		save_save_data()
		language_changed.emit()

func load_save_data():
	if FileAccess.file_exists(save_file_path):
		var file = FileAccess.open(save_file_path, FileAccess.READ)
		if file:
			var json_text = file.get_as_text()
			file.close()
			var json = JSON.new()
			if json.parse(json_text) == OK:
				save_data = json.data
				if "settings" in save_data and "language" in save_data.settings:
					current_language = save_data.settings.language
				if not "games" in save_data:
					save_data.games = {}
				if not "achievements" in save_data:
					save_data.achievements = {}
				return
	init_default_data()
	save_save_data()

func save_save_data():
	var file = FileAccess.open(save_file_path, FileAccess.WRITE)
	if file:
		file.store_line(JSON.stringify(save_data))
		file.close()

func apply_window_settings():
	pass

func init_default_data():
	save_data = {
		"settings": Config.get_default(),
		"achievements": {},
		"games": {}
	}

func get_achievement_progress(achievement_id: String) -> int:
	if not "achievements" in save_data:
		save_data.achievements = {}
	if achievement_id in save_data.achievements:
		return save_data.achievements[achievement_id].get("progress", 0)
	return 0

func get_achievement_stars(achievement_id: String) -> int:
	if not "achievements" in save_data:
		save_data.achievements = {}
	if achievement_id in save_data.achievements:
		return save_data.achievements[achievement_id].get("stars", 0)
	return 0

func update_sudoku_achievement(difficulty: String, completed_count: int):
	var achievement_id = ""
	match difficulty:
		"easy": achievement_id = "sudoku_easy"
		"medium": achievement_id = "sudoku_medium"
		"hard": achievement_id = "sudoku_hard"
		_: return
	
	if not "achievements" in save_data:
		save_data.achievements = {}
	
	if not achievement_id in save_data.achievements:
		save_data.achievements[achievement_id] = {"progress": 0, "stars": 0}
	
	var current_progress = save_data.achievements[achievement_id].get("progress", 0)
	var current_stars = save_data.achievements[achievement_id].get("stars", 0)
	
	if completed_count > current_progress:
		save_data.achievements[achievement_id].progress = completed_count
		
		var thresholds = sudoku_achievements_def[achievement_id].thresholds
		var stars = sudoku_achievements_def[achievement_id].stars
		var new_stars = 0
		
		for i in range(thresholds.size()):
			if completed_count >= thresholds[i]:
				new_stars = stars[i]
		
		if new_stars > current_stars:
			save_data.achievements[achievement_id].stars = new_stars
			achievement_updated.emit(achievement_id, new_stars)
		
		save_save_data()

func get_all_achievements() -> Dictionary:
	return sudoku_achievements_def

func get_all_achievement_data() -> Dictionary:
	return save_data.achievements
