extends Node

static func create_button(parent: Node, button_name: String, icon_path: String, label: String, callback: Variant) -> Control:
	var container = Control.new()
	container.name = button_name + "Container"
	container.anchors_preset = Control.PRESET_FULL_RECT
	parent.add_child(container)

	var inner = Control.new()
	inner.name = button_name + "Inner"
	inner.anchors_preset = Control.PRESET_CENTER
	inner.custom_minimum_size = Vector2(105, 108)
	container.add_child(inner)

	var icon_btn = Button.new()
	icon_btn.name = button_name
	icon_btn.anchors_preset = Control.PRESET_FULL_RECT
	icon_btn.custom_minimum_size = Vector2(105, 105)
	icon_btn.flat = true
	icon_btn.expand_icon = true

	if icon_path != "":
		var texture = load(icon_path)
		if texture:
			icon_btn.icon = texture

	inner.add_child(icon_btn)

	var label_bg = PanelContainer.new()
	label_bg.name = button_name + "LabelBg"
	label_bg.anchors_preset = Control.PRESET_FULL_RECT

	var style = StyleBoxFlat.new()
	style.bg_color = Color(1, 1, 1, 1)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.border_color = Color(0, 0, 0, 1)
	style.set_content_margin_all(4)
	label_bg.add_theme_stylebox_override("panel", style)

	var label_node = Label.new()
	label_node.text = label
	label_node.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label_node.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label_node.add_theme_color_override("font_color", Color(0, 0, 0, 1))
	label_node.add_theme_font_size_override("font_size", 10)
	label_bg.add_child(label_node)

	inner.add_child(label_bg)

	var label_width = label_bg.size.x
	label_bg.position = Vector2((105 - label_width) / 2, 76)

	if callback != null:
		icon_btn.connect("pressed", callback)

	return container

static func create_simple_button(parent: Node, button_name: String, icon_path: String, callback: Variant) -> Button:
	var button = Button.new()
	button.name = button_name
	button.anchors_preset = Control.PRESET_CENTER
	button.flat = true

	if icon_path != "":
		var texture = load(icon_path)
		if texture:
			button.icon = texture

	parent.add_child(button)

	if callback != null:
		button.connect("pressed", callback)

	return button