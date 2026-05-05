extends Area2D

# 桌面宠物控制器 - 完整版
# 功能：根据图片大小自动调整窗口尺寸

@export var pet_scale: float = 0.5
@export var window_padding: int = 40

var _MainWindow: Window
var pet_sprite: Sprite2D
var right_click_menu: Control
var check_box_allow_click: CheckBox
var btn_always_on_top: Button

var player_size: Vector2i = Vector2i(512, 512)
var dragging: bool = false
var snapshot: Vector2
var allow_click: bool = true
var always_on_top: bool = false

func _ready():
	print("✅ PetController ready!")
	
	_MainWindow = get_window()
	pet_sprite = get_node_or_null("PetSprite")
	right_click_menu = get_node_or_null("RightClickMenu")
	
	_resize_window_to_fit_image()
	
	if _MainWindow:
		_MainWindow.transparent = true
		_MainWindow.always_on_top = true
		print("🖼️ Window transparent: ", _MainWindow.transparent)
	
	check_box_allow_click = null
	btn_always_on_top = null
	
	if right_click_menu:
		check_box_allow_click = right_click_menu.get_node_or_null("CheckBoxAllowClick")
		btn_always_on_top = right_click_menu.get_node_or_null("BtnAlwaysOnTop")
		
		if check_box_allow_click:
			allow_click = check_box_allow_click.button_pressed
			check_box_allow_click.connect("toggled", _on_allow_click_toggled)
		
		if btn_always_on_top:
			btn_always_on_top.connect("pressed", _on_toggle_always_on_top)
	
	var screen_size = DisplayServer.screen_get_size()
	var target_pos = Vector2i(screen_size.x - player_size.x - 20, screen_size.y - player_size.y - 80)
	_MainWindow.position = target_pos
	
	connect("input_event", _on_pet_input_event)
	
	print("📍 Pet initialized at: ", _MainWindow.position)
	print("📋 Menu found: ", right_click_menu != null)

func _resize_window_to_fit_image():
	if not pet_sprite or not pet_sprite.texture:
		print("⚠️ No sprite or texture found, using default size")
		player_size = Vector2i(512, 512)
		if _MainWindow:
			_MainWindow.size = player_size
		return
	
	var texture_size = pet_sprite.texture.get_size()
	var scaled_size = Vector2(texture_size.x * pet_scale, texture_size.y * pet_scale)
	
	player_size = Vector2i(
		int(scaled_size.x) + window_padding * 2,
		int(scaled_size.y) + window_padding * 2
	)
	
	if pet_sprite:
		pet_sprite.scale = Vector2(pet_scale, pet_scale)
		pet_sprite.position = Vector2(player_size.x / 2, player_size.y / 2)
		pet_sprite.centered = true
	
	if _MainWindow:
		_MainWindow.size = player_size
	
	var collision_shape = get_node_or_null("CollisionShape2D")
	if collision_shape:
		var rect_shape = RectangleShape2D.new()
		rect_shape.size = Vector2(player_size.x, player_size.y)
		collision_shape.shape = rect_shape
	
	print("🖼️ Image size: ", texture_size)
	print("🖼️ Scaled size: ", scaled_size)
	print("🖼️ Window size: ", player_size)

func _on_pet_input_event(_viewport, event, _shape_idx):
	if not allow_click:
		return
	
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			print("🖱️ Right click detected")
			_show_right_click_menu()
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				dragging = true
				snapshot = get_global_mouse_position() - Vector2(_MainWindow.position)
				if right_click_menu:
					right_click_menu.visible = false
				print("👆 Start dragging")
			else:
				dragging = false
				print("✋ Stop dragging")

func _input(event):
	if dragging and event is InputEventMouseMotion:
		var new_pos = get_global_mouse_position() - snapshot
		new_pos.x = clamp(new_pos.x, 0, DisplayServer.screen_get_size().x - player_size.x)
		new_pos.y = clamp(new_pos.y, 0, DisplayServer.screen_get_size().y - player_size.y)
		_MainWindow.position = Vector2i(new_pos)
	
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		if right_click_menu and right_click_menu.visible:
			var menu_rect = right_click_menu.get_global_rect()
			if not menu_rect.has_point(get_global_mouse_position()):
				right_click_menu.visible = false
				print("📋 Menu closed (clicked outside)")

func _show_right_click_menu():
	if right_click_menu:
		right_click_menu.visible = !right_click_menu.visible
		print("📋 Menu visible: ", right_click_menu.visible)
	else:
		print("❌ Menu not found!")

func _hide_right_click_menu():
	if right_click_menu:
		right_click_menu.visible = false

func _on_allow_click_toggled(pressed: bool):
	allow_click = pressed
	print("🔘 Allow click: ", allow_click)
	if not allow_click:
		_hide_right_click_menu()

func _on_toggle_always_on_top():
	always_on_top = !always_on_top
	if _MainWindow:
		_MainWindow.always_on_top = always_on_top
	if btn_always_on_top:
		btn_always_on_top.text = "📌 取消置顶" if always_on_top else "📌 置顶"
	print("🔝 Always on top: ", always_on_top)

func _on_menu_button_pressed(btn_name: String):
	print("🖼️ Button pressed: ", btn_name)
	_hide_right_click_menu()
	
	match btn_name.to_lower():
		"btnbag":
			print("🎒 背包按钮被点击")
		"btnshop":
			print("🛒 商店按钮被点击")
		"btnsettings":
			print("⚙️ 设置按钮被点击")
		"btnabout":
			print("ℹ️ 关于按钮被点击")