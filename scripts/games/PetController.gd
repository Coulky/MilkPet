extends Area2D

# 桌面宠物主控制器
# 参考 test 项目实现：无边框透明窗口、右下角显示、点击穿透、拖拽移动

@export var player_size: Vector2i = Vector2i(100, 100)

@onready var _MainWindow: Window = get_window()
var pet_sprite: Sprite2D
var ui_panel: Control

var dragging: bool = false
var snapshot: Vector2
var draggable: bool = false

func _ready():
	print("PetController ready!")
	
	# 设置透明背景
	get_tree().get_root().set_transparent_background(true)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_TRANSPARENT, true)
	
	# 获取节点引用
	pet_sprite = get_node_or_null("PetSprite")
	ui_panel = get_node_or_null("UIPanel")
	
	# 初始位置（屏幕右下角）
	var screen_size = DisplayServer.screen_get_size(DisplayServer.get_keyboard_focus_screen())
	var start_pos = DisplayServer.screen_get_position(DisplayServer.get_keyboard_focus_screen())
	
	var target_x = (screen_size.x - player_size.x) + start_pos.x
	var target_y = (screen_size.y - player_size.y) + start_pos.y
	
	_MainWindow.position = Vector2i(target_x, target_y)
	
	# 隐藏UI面板
	if ui_panel:
		ui_panel.visible = false
	
	# 连接信号
	connect("mouse_entered", _on_pet_hover)
	connect("mouse_exited", _on_pet_leave)
	connect("input_event", _on_pet_click)
	
	# 连接按钮
	if ui_panel:
		var buttons = ui_panel.get_children()
		for btn in buttons:
			if btn.has_method("pressed"):
				btn.connect("pressed", _on_game_button_pressed.bind(btn.name))
	
	draggable = true
	print("Pet initialized at position: ", _MainWindow.position)

func _process(delta):
	pass

func _on_pet_hover():
	print("Mouse entered pet")
	if ui_panel:
		ui_panel.visible = true

func _on_pet_leave():
	print("Mouse left pet")
	if ui_panel:
		ui_panel.visible = false

func _on_pet_click(viewport, event, shape_idx):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed and draggable:
				print("Start dragging")
				dragging = true
				snapshot = position
				if ui_panel:
					ui_panel.visible = false
			else:
				print("Stop dragging")
				dragging = false

func _input(event):
	if Input.is_action_just_pressed("click") and draggable and not dragging:
		dragging = true
		snapshot = position
		if ui_panel:
			ui_panel.visible = false
	
	if Input.is_action_pressed("click") and draggable and dragging:
		_MainWindow.position = Vector2i(get_global_mouse_position() - snapshot)
	
	if Input.is_action_just_released("click") and dragging:
		dragging = false

func _on_game_button_pressed(btn_name: String):
	print("Button pressed: ", btn_name)
	match btn_name.to_lower():
		"btn_sudoku":
			get_tree().change_scene_to_file("res://scenes/games/sudoku/sudoku.tscn")
		"btn_sliding_puzzle":
			get_tree().change_scene_to_file("res://scenes/games/sliding_puzzle/sliding_puzzle.tscn")
		"btn_match3":
			get_tree().change_scene_to_file("res://scenes/games/match3/match3.tscn")
		"btn_achievements":
			get_tree().change_scene_to_file("res://scenes/Achievements.tscn")
