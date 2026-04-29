extends Node

signal language_changed

var current_language = "zh-CN"
var save_data = {}
var save_file_path = "user://save_data.json"

func _ready():
	load_save_data()

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

func init_default_data():
	save_data = {
		"settings": Config.get_default(),
		"achievements": {},
		"games": {}
	}
