extends Control

var current_language_index = 0
var current_resolution_index = 0
var current_window_mode_index = 0

var languages = ["zh-CN", "zh-TW", "en", "ja"]

var pending_settings = {}

func _ready():
	load_current_settings()
	update_ui()

func load_current_settings():
	pending_settings = GlobalData.save_data.settings.duplicate(true)

	var saved_lang = pending_settings.language
	current_language_index = languages.find(saved_lang)
	if current_language_index == -1:
		current_language_index = 0

	var saved_res = pending_settings.resolution
	var resolutions = Config.resolutions
	for i in range(resolutions.size()):
		if resolutions[i].width == saved_res.width and resolutions[i].height == saved_res.height:
			current_resolution_index = i
			break

	current_window_mode_index = pending_settings.window_mode

func update_ui():
	var lang_name = GlobalData.get_lang_display_name(languages[current_language_index])
	$VBoxContainer/LanguageSection/LanguageValue.text = lang_name

	var res = Config.resolutions[current_resolution_index]
	$VBoxContainer/ResolutionSection/ResolutionValue.text = str(res.width) + "x" + str(res.height)

	var window_mode_name = GlobalData.translate(Config.window_modes[current_window_mode_index])
	$VBoxContainer/WindowModeSection/WindowModeValue.text = window_mode_name

	update_labels()

func update_labels():
	$VBoxContainer/LanguageSection/LanguageLabel.text = GlobalData.translate("language")
	$VBoxContainer/ResolutionSection/ResolutionLabel.text = GlobalData.translate("resolution")
	$VBoxContainer/WindowModeSection/WindowModeLabel.text = GlobalData.translate("display")
	update_button_texts()

func update_button_texts():
	$ButtonContainer/ResetButton.text = GlobalData.translate("reset")
	$ButtonContainer/BackButton.text = GlobalData.translate("back") + " (ESC)"
	$ButtonContainer/ApplyButton.text = GlobalData.translate("apply") + " (Space)"

func _on_language_prev_pressed():
	current_language_index -= 1
	if current_language_index < 0:
		current_language_index = languages.size() - 1
	pending_settings.language = languages[current_language_index]
	update_ui()

func _on_language_next_pressed():
	current_language_index += 1
	if current_language_index >= languages.size():
		current_language_index = 0
	pending_settings.language = languages[current_language_index]
	update_ui()

func _on_resolution_prev_pressed():
	var resolutions = Config.resolutions
	current_resolution_index -= 1
	if current_resolution_index < 0:
		current_resolution_index = resolutions.size() - 1
	pending_settings.resolution = resolutions[current_resolution_index]
	update_ui()

func _on_resolution_next_pressed():
	var resolutions = Config.resolutions
	current_resolution_index += 1
	if current_resolution_index >= resolutions.size():
		current_resolution_index = 0
	pending_settings.resolution = resolutions[current_resolution_index]
	update_ui()

func _on_window_mode_prev_pressed():
	current_window_mode_index -= 1
	if current_window_mode_index < 0:
		current_window_mode_index = Config.window_modes.size() - 1
	pending_settings.window_mode = current_window_mode_index
	update_ui()

func _on_window_mode_next_pressed():
	current_window_mode_index += 1
	if current_window_mode_index >= Config.window_modes.size():
		current_window_mode_index = 0
	pending_settings.window_mode = current_window_mode_index
	update_ui()

func _input(event):
	if event is InputEventKey and event.pressed:
		if event.as_text() == "Escape":
			on_back_pressed()
		elif event.as_text() == "Space":
			on_apply_pressed()

func on_back_pressed():
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")

func on_apply_pressed():
	apply_settings()
	get_tree().change_scene_to_file("res://scenes/HomePage.tscn")

func on_reset_pressed():
	pending_settings = Config.get_default().duplicate(true)

	current_language_index = 0
	current_resolution_index = 5
	current_window_mode_index = 0

	update_ui()

func apply_settings():
	GlobalData.save_data.settings = pending_settings.duplicate(true)
	GlobalData.save_save_data()

	GlobalData.set_language(pending_settings.language)

	if pending_settings.window_mode == 0:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		var res = pending_settings.resolution
		get_tree().root.content_scale_size = Vector2i(res.width, res.height)
		DisplayServer.window_set_size(Vector2i(res.width, res.height))
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
