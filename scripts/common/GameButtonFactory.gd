extends Node

static func create_button(parent: Node, button_name: String, icon_path: String, label: String, callback: Variant) -> Button:
	var container = Control.new()
	container.name = button_name + "Container"
	container.layout_mode = 1
	container.custom_minimum_size = Vector2(50, 50)
	parent.add_child(container)
	
	var button = Button.new()
	button.name = button_name
	button.layout_mode = 2
	button.anchors_preset = 15
	button.anchor_right = 1.0
	button.anchor_bottom = 1.0
	button.custom_minimum_size = Vector2(50, 50)
	button.flat = true
	button.expand_icon = true
	
	if icon_path != "":
		var texture = load(icon_path)
		if texture:
			button.icon = texture
	
	container.add_child(button)
	
	var label_bg = ColorRect.new()
	label_bg.name = button_name + "LabelBg"
	label_bg.layout_mode = 2
	label_bg.anchors_preset = 0
	label_bg.anchor_left = 0.15
	label_bg.anchor_right = 0.85
	label_bg.anchor_top = 0.7
	label_bg.anchor_bottom = 0.9
	label_bg.custom_minimum_size = Vector2(0, 0)
	label_bg.size_flags_horizontal = 3
	label_bg.size_flags_vertical = 3
	label_bg.color = Color(1, 1, 1, 1)
	container.add_child(label_bg)
	
	var label_node = Label.new()
	label_node.name = button_name + "Label"
	label_node.layout_mode = 1
	label_node.text = label
	label_node.horizontal_alignment = 1
	label_node.vertical_alignment = 1
	label_node.custom_minimum_size = Vector2(0, 0)
	label_node.add_theme_color_override("font_color", Color(0, 0, 0, 1))
	label_node.add_theme_font_size_override("font_size", 5)
	label_bg.add_child(label_node)
	
	if callback != null:
		button.connect("pressed", callback)
	
	return button

static func create_simple_button(parent: Node, button_name: String, icon_path: String, callback: Variant) -> Button:
	var button = Button.new()
	button.name = button_name
	button.layout_mode = 1
	button.custom_minimum_size = Vector2(50, 50)
	button.flat = true
	button.expand_icon = true
	
	if icon_path != "":
		var texture = load(icon_path)
		if texture:
			button.icon = texture
	
	parent.add_child(button)
	
	if callback != null:
		button.connect("pressed", callback)
	
	return button
