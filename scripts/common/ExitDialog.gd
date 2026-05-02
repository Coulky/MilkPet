extends Control

signal confirmed
signal cancelled
signal go_home

var title_label: Label
var message_label: Label
var confirm_button: Button
var cancel_button: Button
var home_button: Button

func _ready():
	_initialize_dialog()

func _initialize_dialog():
	visible = false
	anchors_preset = PRESET_FULL_RECT
	
	var modal_bg = ColorRect.new()
	modal_bg.name = "ModalBg"
	modal_bg.anchors_preset = PRESET_FULL_RECT
	modal_bg.color = Color(0, 0, 0, 0.6)
	add_child(modal_bg)
	
	var dialog_panel = PanelContainer.new()
	dialog_panel.name = "DialogPanel"
	dialog_panel.anchors_preset = PRESET_CENTER
	dialog_panel.offset_left = -180
	dialog_panel.offset_top = -120
	dialog_panel.offset_right = 180
	dialog_panel.offset_bottom = 120
	
	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = Color(0.95, 0.95, 0.95, 1)
	panel_style.corner_radius_top_left = 12
	panel_style.corner_radius_top_right = 12
	panel_style.corner_radius_bottom_left = 12
	panel_style.corner_radius_bottom_right = 12
	panel_style.set_border_width(0, 2)
	panel_style.set_border_width(1, 2)
	panel_style.set_border_width(2, 2)
	panel_style.set_border_width(3, 2)
	panel_style.border_color = Color(0.3, 0.3, 0.3, 1)
	dialog_panel.add_theme_stylebox_override("panel", panel_style)
	add_child(dialog_panel)
	
	var vbox = VBoxContainer.new()
	vbox.name = "VBox"
	vbox.anchors_preset = PRESET_FULL_RECT
	vbox.add_theme_constant_override("separation", 20)
	vbox.add_theme_constant_override("margin_top", 25)
	vbox.add_theme_constant_override("margin_left", 20)
	vbox.add_theme_constant_override("margin_right", 20)
	vbox.add_theme_constant_override("margin_bottom", 20)
	dialog_panel.add_child(vbox)
	
	title_label = Label.new()
	title_label.name = "TitleLabel"
	title_label.text = "退出确认"
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.add_theme_font_size_override("font_size", 24)
	title_label.add_theme_color_override("font_color", Color(0, 0, 0, 1))
	vbox.add_child(title_label)
	
	message_label = Label.new()
	message_label.name = "MessageLabel"
	message_label.text = "确定要退出游戏吗？"
	message_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message_label.add_theme_font_size_override("font_size", 16)
	message_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.4, 1))
	vbox.add_child(message_label)
	
	var hbox = HBoxContainer.new()
	hbox.name = "ButtonHBox"
	hbox.add_theme_constant_override("separation", 15)
	vbox.add_child(hbox)
	
	var spacer = Control.new()
	spacer.size_flags_horizontal = SIZE_EXPAND
	hbox.add_child(spacer)
	
	home_button = Button.new()
	home_button.name = "HomeButton"
	home_button.text = "返回家园"
	home_button.custom_minimum_size = Vector2(100, 40)
	home_button.connect("pressed", _on_go_home)
	
	var home_style = StyleBoxFlat.new()
	home_style.bg_color = Color(0.2, 0.6, 0.85, 1)
	home_style.corner_radius_top_left = 6
	home_style.corner_radius_top_right = 6
	home_style.corner_radius_bottom_left = 6
	home_style.corner_radius_bottom_right = 6
	home_button.add_theme_stylebox_override("panel", home_style)
	home_button.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	home_button.add_theme_font_size_override("font_size", 18)
	hbox.add_child(home_button)
	
	confirm_button = Button.new()
	confirm_button.name = "ConfirmButton"
	confirm_button.text = "返回首页"
	confirm_button.custom_minimum_size = Vector2(100, 40)
	confirm_button.connect("pressed", _on_confirm)
	
	var confirm_style = StyleBoxFlat.new()
	confirm_style.bg_color = Color(0.85, 0.2, 0.2, 1)
	confirm_style.corner_radius_top_left = 6
	confirm_style.corner_radius_top_right = 6
	confirm_style.corner_radius_bottom_left = 6
	confirm_style.corner_radius_bottom_right = 6
	confirm_button.add_theme_stylebox_override("panel", confirm_style)
	confirm_button.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	confirm_button.add_theme_font_size_override("font_size", 18)
	hbox.add_child(confirm_button)
	
	cancel_button = Button.new()
	cancel_button.name = "CancelButton"
	cancel_button.text = "取消"
	cancel_button.custom_minimum_size = Vector2(100, 40)
	cancel_button.connect("pressed", _on_cancel)
	
	var cancel_style = StyleBoxFlat.new()
	cancel_style.bg_color = Color(0.7, 0.7, 0.7, 1)
	cancel_style.corner_radius_top_left = 6
	cancel_style.corner_radius_top_right = 6
	cancel_style.corner_radius_bottom_left = 6
	cancel_style.corner_radius_bottom_right = 6
	cancel_button.add_theme_stylebox_override("panel", cancel_style)
	cancel_button.add_theme_color_override("font_color", Color(0, 0, 0, 1))
	cancel_button.add_theme_font_size_override("font_size", 18)
	hbox.add_child(cancel_button)
	
	var spacer2 = Control.new()
	spacer2.size_flags_horizontal = SIZE_EXPAND
	hbox.add_child(spacer2)

func show_dialog(title: String = "退出确认", message: String = "确定要退出游戏吗？", show_home_button: bool = true):
	title_label.text = title
	message_label.text = message
	home_button.visible = show_home_button
	visible = true
	grab_focus()

func hide_dialog():
	visible = false

func _on_confirm():
	hide_dialog()
	emit_signal("confirmed")

func _on_cancel():
	hide_dialog()
	emit_signal("cancelled")

func _on_go_home():
	hide_dialog()
	emit_signal("go_home")

func _input(event: InputEvent):
	if event is InputEventKey and event.keycode == KEY_ESCAPE:
		if visible:
			_on_cancel()
