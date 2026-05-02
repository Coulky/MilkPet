extends Button

@export var button_name: String = ""
@export var icon_path: String = ""
@export var label_font_size: int = 5

var on_click_callback: Callable = null

func _ready():
	if icon_path != "":
		var texture = load(icon_path)
		if texture:
			icon = texture
	flat = true
	expand_icon = true
	setup_label()

func setup_label():
	var container = Control.new()
	container.name = "ButtonContainer"
	container.layout_mode = 2
	container.anchors_preset = 15
	container.anchor_right = 1.0
	container.anchor_bottom = 1.0
	add_child(container)
	
	var label_bg = PanelContainer.new()
	label_bg.name = "LabelBg"
	label_bg.layout_mode = 2
	label_bg.anchors_preset = 0
	label_bg.anchor_left = 0.15
	label_bg.anchor_right = 0.85
	label_bg.anchor_top = 0.7
	label_bg.anchor_bottom = 0.9
	label_bg.custom_minimum_size = Vector2(0, 0)
	label_bg.size_flags_horizontal = 3
	label_bg.size_flags_vertical = 3
	label_bg.add_theme_color_override("panel", Color(1, 1, 1, 1))
	label_bg.add_theme_color_override("border_color", Color(0, 0, 0, 1))
	container.add_child(label_bg)
	
	var label = Label.new()
	label.name = "ButtonLabel"
	label.layout_mode = 1
	label.text = button_name
	label.horizontal_alignment = 1
	label.vertical_alignment = 1
	label.font_size = label_font_size
	label.custom_minimum_size = Vector2(0, 0)
	label.add_theme_color_override("font_color", Color(0, 0, 0, 1))
	label_bg.add_child(label)

func _on_button_down():
	if on_click_callback != null:
		on_click_callback.call()

func set_callback(callback: Callable):
	on_click_callback = callback
