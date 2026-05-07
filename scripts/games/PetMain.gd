extends Node

var _dragging: bool = false
var _snapshot: Vector2
var _allow_click: bool = true
var _on_top: bool = true
var _menu: Control
var _btn_top: Button
var _chk_click: CheckBox
var _win_size: Vector2i
var _container: Control

func _ready():
	print("✅ PetMain ready!")
	
	var win = get_window()
	
	RenderingServer.set_default_clear_color(Color(0, 0, 0, 0))
	
	await get_tree().process_frame
	
	win.borderless = true
	win.transparent = true
	win.transparent_bg = true
	win.always_on_top = true
	win.unresizable = true
	
	get_viewport().transparent_bg = true
	get_viewport().set_transparent_background(true)
	
	var tex = load("res://assets/images/yongbing.png")
	if not tex:
		print("❌ Texture load failed!")
		return
	print("✅ Texture: ", tex.get_size())
	
	if tex is Texture2D:
		var img = tex.get_image()
		if img:
			DisplayServer.set_icon(img)
			print("🪟 Taskbar icon set")
	
	var ts = tex.get_size()
	var scale = 0.5
	var pad = 40
	var ss = Vector2(ts.x * scale, ts.y * scale)
	_win_size = Vector2i(int(ss.x) + pad * 2, int(ss.y) + pad * 2)
	win.size = _win_size
	
	_container = Control.new()
	_container.name = "PetContainer"
	_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	_container.offset_right = _win_size.x
	_container.offset_bottom = _win_size.y
	_container.gui_input.connect(_on_gui_input)
	add_child(_container)
	
	var texture_rect = TextureRect.new()
	texture_rect.name = "PetSprite"
	texture_rect.texture = tex
	texture_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	texture_rect.size = ss
	texture_rect.position = Vector2(pad, pad)
	texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_container.add_child(texture_rect)
	print("✅ TextureRect at ", texture_rect.position, " size=", texture_rect.size)
	
	_menu = Control.new()
	_menu.name = "PopupMenu"
	_menu.visible = false
	_menu.position = Vector2(20, 20)
	_menu.size = Vector2(160, 260)
	_menu.z_index = 100
	_menu.mouse_filter = Control.MOUSE_FILTER_STOP
	var ms = StyleBoxFlat.new()
	ms.bg_color = Color(0.15, 0.15, 0.18, 0.95)
	ms.set_corner_radius_all(10)
	ms.border_width_left = 2
	ms.border_width_right = 2
	ms.border_width_top = 2
	ms.border_width_bottom = 2
	ms.border_color = Color(0.4, 0.4, 0.5, 1.0)
	_menu.add_theme_stylebox_override("panel", ms)
	_container.add_child(_menu)
	
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

func _on_gui_input(event):
	if not _allow_click:
		return
		
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			_menu.visible = !_menu.visible
			print("🖱️ Right click! Menu visible: ", _menu.visible)
			get_viewport().set_input_as_handled()
			
		elif event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				_dragging = true
				_snapshot = Vector2(DisplayServer.mouse_get_position()) - Vector2(get_window().position)
				_menu.visible = false
				print("🖱️ Left down - start drag")
			else:
				_dragging = false
				print("🖱️ Left up - stop drag")

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