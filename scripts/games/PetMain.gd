extends Node

var _dragging: bool = false
var _snapshot: Vector2
var _allow_click: bool = true
var _on_top: bool = true
var _menu: Control
var _btn_top: Button
var _chk_click: CheckBox
var _win_size: Vector2i

func _ready():
	print("✅ PetMain ready!")
	
	var win = get_window()
	
	RenderingServer.set_default_clear_color(Color(0, 0, 0, 0))
	get_viewport().transparent_bg = true
	
	await get_tree().process_frame
	
	win.borderless = true
	win.transparent = true
	win.transparent_bg = true
	win.unresizable = true
	win.always_on_top = true
	
	var img = Image.load_from_file("res://assets/images/yongbing.png")
	if img:
		DisplayServer.set_icon(img)
		print("🪪 Taskbar icon set")
	
	var tex = load("res://assets/images/yongbing.png")
	if not tex:
		print("❌ Texture load failed!")
		return
	print("✅ Texture: ", tex.get_size())
	
	var ts = tex.get_size()
	var scale = 0.5
	var pad = 40
	var ss = Vector2(ts.x * scale, ts.y * scale)
	_win_size = Vector2i(int(ss.x) + pad * 2, int(ss.y) + pad * 2)
	win.size = _win_size
	
	var area = Area2D.new()
	area.connect("input_event", _on_area_input)
	add_child(area)
	
	var sprite = Sprite2D.new()
	sprite.texture = tex
	sprite.scale = Vector2(scale, scale)
	sprite.position = Vector2(_win_size.x / 2.0, _win_size.y / 2.0)
	sprite.centered = true
	sprite.z_index = 10
	area.add_child(sprite)
	print("✅ Sprite at ", sprite.position, " scale=", sprite.scale)
	
	var col = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(_win_size.x, _win_size.y)
	col.shape = rect
	area.add_child(col)
	
	_menu = Control.new()
	_menu.visible = false
	_menu.position = Vector2(20, 20)
	_menu.size = Vector2(160, 260)
	_menu.z_index = 100
	var ms = StyleBoxFlat.new()
	ms.bg_color = Color(0.15, 0.15, 0.18, 0.95)
	ms.set_corner_radius_all(10)
	ms.border_width_left = 2
	ms.border_width_right = 2
	ms.border_width_top = 2
	ms.border_width_bottom = 2
	ms.border_color = Color(0.4, 0.4, 0.5, 1.0)
	_menu.add_theme_stylebox_override("panel", ms)
	area.add_child(_menu)
	
	_add_btn("BtnBag", "🎒 背包", 0.02, 0.14, "bag")
	_add_btn("BtnShop", "🛒 商店", 0.17, 0.29, "shop")
	_add_btn("BtnSettings", "⚙️ 设置", 0.32, 0.44, "settings")
	_add_btn("BtnAbout", "ℹ️ 关于", 0.47, 0.59, "about")
	
	_btn_top = _add_btn("BtnTop", "📌 取消置顶", 0.62, 0.74, "top")
	_btn_top.pressed.connect(_on_top_toggle)
	
	_chk_click = CheckBox.new()
	_chk_click.name = "ChkAllowClick"
	_chk_click.text = "允许点击交互"
	_chk_click.button_pressed = true
	_chk_click.custom_minimum_size = Vector2(0, 30)
	_chk_click.add_theme_color_override("font_color", Color(0.85, 0.85, 0.85, 1.0))
	_chk_click.add_theme_font_size_override("font_size", 12)
	_chk_click.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_chk_click.anchor_left = 0.05
	_chk_click.anchor_right = 0.95
	_chk_click.anchor_top = 0.78
	_chk_click.anchor_bottom = 0.94
	_chk_click.connect("toggled", _on_click_toggled)
	_menu.add_child(_chk_click)
	
	var scr = DisplayServer.screen_get_size()
	win.position = Vector2i(scr.x - _win_size.x - 20, scr.y - _win_size.y - 80)
	
	print("🪟 borderless=", win.borderless, " transparent=", win.transparent, " transparent_bg=", win.transparent_bg, " always_on_top=", win.always_on_top)
	print("🖼️ tex=", ts, " scaled=", ss, " win=", _win_size)
	print("📍 pos=", win.position)

func _add_btn(p_name: String, p_text: String, p_top: float, p_bot: float, p_tag: String) -> Button:
	var btn = Button.new()
	btn.name = p_name
	btn.text = p_text
	btn.custom_minimum_size = Vector2(0, 30)
	btn.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9, 1.0))
	btn.add_theme_font_size_override("font_size", 14)
	btn.set_anchors_preset(Control.PRESET_TOP_WIDE)
	btn.anchor_left = 0.05
	btn.anchor_right = 0.95
	btn.anchor_top = p_top
	btn.anchor_bottom = p_bot
	var bs = StyleBoxFlat.new()
	bs.bg_color = Color(0.25, 0.25, 0.3, 0.9)
	bs.set_corner_radius_all(6)
	btn.add_theme_stylebox_override("normal", bs)
	btn.pressed.connect(_on_menu_btn.bind(p_tag))
	_menu.add_child(btn)
	return btn

func _on_area_input(_vp, event, _idx):
	if not _allow_click:
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			_menu.visible = !_menu.visible
			print("📋 menu=", _menu.visible)
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				_dragging = true
				_snapshot = Vector2(DisplayServer.mouse_get_position()) - Vector2(get_window().position)
				_menu.visible = false
			else:
				_dragging = false

func _input(event):
	if _dragging and event is InputEventMouseMotion:
		var mp = DisplayServer.mouse_get_position()
		var np = Vector2(mp) - _snapshot
		get_window().position = Vector2i(np)
	
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		if _menu and _menu.visible:
			var mp = DisplayServer.mouse_get_position()
			var mr = Rect2(_menu.global_position, _menu.size)
			if not mr.has_point(mp):
				_menu.visible = false

func _on_click_toggled(pressed: bool):
	_allow_click = pressed
	if not _allow_click:
		_menu.visible = false

func _on_menu_btn(tag: String):
	print("🔘 ", tag)
	_menu.visible = false

func _on_top_toggle():
	_on_top = !_on_top
	get_window().always_on_top = _on_top
	_btn_top.text = "📌 取消置顶" if _on_top else "📌 置顶"
	print("📌 always_on_top=", _on_top)