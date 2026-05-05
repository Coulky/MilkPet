extends Area2D

# 测试版6：修复菜单位置

var _MainWindow: Window
var right_click_menu: Control
var dragging: bool = false
var snapshot: Vector2
var menu_opened: bool = false

func _ready():
	print("✅ Test6: Ready!")
	_MainWindow = get_window()

	var screen_size = DisplayServer.screen_get_size()
	_MainWindow.position = Vector2i(screen_size.x - 150, screen_size.y - 150)

	right_click_menu = get_node_or_null("RightClickMenu")
	connect("input_event", _on_pet_input_event)

	if right_click_menu:
		right_click_menu.position = Vector2(10, 10)
		for child in right_click_menu.get_children():
			if child is Button:
				child.connect("pressed", _on_menu_button_pressed.bind(child.name))

	print("Menu position set to: ", right_click_menu.position)

func _on_pet_input_event(viewport, event, shape_idx):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			print("Right click!")
			_show_menu()
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				dragging = true
				menu_opened = false
				snapshot = get_global_mouse_position() - Vector2(_MainWindow.position)
				if right_click_menu:
					right_click_menu.visible = false
			else:
				dragging = false

func _input(event):
	if dragging and event is InputEventMouseMotion:
		var new_pos = get_global_mouse_position() - snapshot
		new_pos.x = clamp(new_pos.x, 0, DisplayServer.screen_get_size().x - 100)
		new_pos.y = clamp(new_pos.y, 0, DisplayServer.screen_get_size().y - 100)
		_MainWindow.position = Vector2i(new_pos)

func _show_menu():
	if right_click_menu:
		menu_opened = !menu_opened
		right_click_menu.visible = menu_opened
		print("Menu: ", menu_opened)

func _on_menu_button_pressed(btn_name: String):
	print("🎉 Button: ", btn_name)
	menu_opened = false
	right_click_menu.visible = false