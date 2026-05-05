extends Area2D

# 桌面宠物主控制器
# 功能：右键菜单、拖拽、允许点击开关、系统托盘

@export var player_size: Vector2i = Vector2i(100, 100)

@onready var _MainWindow: Window = get_window()
var pet_sprite: Sprite2D
var right_click_menu: Control
var check_box_allow_click: CheckBox

var dragging: bool = false
var snapshot: Vector2
var allow_click: bool = true

func _ready():
	print("PetController ready!")
	
	pet_sprite = get_node_or_null("PetSprite")
	right_click_menu = get_node_or_null("RightClickMenu")
	check_box_allow_click = right_click_menu.get_node_or_null("CheckBoxAllowClick") if right_click_menu else null
	
	if check_box_allow_click:
		allow_click = check_box_allow_click.button_pressed
		check_box_allow_click.connect("toggled", _on_allow_click_toggled)
	
	var screen_size = DisplayServer.screen_get_size(DisplayServer.get_keyboard_focus_screen())
	var start_pos = DisplayServer.screen_get_position(DisplayServer.get_keyboard_focus_screen())
	
	var target_x = (screen_size.x - player_size.x) + start_pos.x
	var target_y = (screen_size.y - player_size.y) + start_pos.y
	
	_MainWindow.position = Vector2i(target_x, target_y)
	
	connect("input_event", _on_pet_input_event)
	
	if right_click_menu:
		var buttons = right_click_menu.get_children()
		for btn in buttons:
			if btn is Button and btn.has_method("pressed"):
				btn.connect("pressed", _on_menu_button_pressed.bind(btn.name))
	
	print("Pet initialized at position: ", _MainWindow.position)

func _on_pet_input_event(viewport, event, shape_idx):
	if not allow_click:
		return
	
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			_show_right_click_menu()
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				dragging = true
				snapshot = get_global_mouse_position() - Vector2(_MainWindow.position)
				if right_click_menu:
					right_click_menu.visible = false
			else:
				dragging = false

func _input(event):
	if dragging and event is InputEventMouseMotion:
		var new_pos = get_global_mouse_position() - snapshot
		new_pos.x = clamp(new_pos.x, 0, DisplayServer.screen_get_size().x - player_size.x)
		new_pos.y = clamp(new_pos.y, 0, DisplayServer.screen_get_size().y - player_size.y)
		_MainWindow.position = Vector2i(new_pos)

func _show_right_click_menu():
	if right_click_menu:
		right_click_menu.visible = !right_click_menu.visible
		print("Right click menu shown: ", right_click_menu.visible)

func _hide_right_click_menu():
	if right_click_menu:
		right_click_menu.visible = false

func _on_allow_click_toggled(pressed: bool):
	allow_click = pressed
	print("Allow click toggled: ", allow_click)
	if not allow_click:
		_hide_right_click_menu()

func _on_menu_button_pressed(btn_name: String):
	print("Menu button pressed: ", btn_name)
	match btn_name.to_lower():
		"btnbag":
			print("背包按钮被点击（暂未实现）")
		"btnshop":
			print("商店按钮被点击（暂未实现）")
		"btnsettings":
			print("设置按钮被点击（暂未实现）")
		"btnabout":
			print("关于按钮被点击（暂未实现）")