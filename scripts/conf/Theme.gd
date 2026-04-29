extends Node

var themes = {
	"default": {
		"name_key": "theme_default",
		"colors": {
			"background": Color(0.1, 0.1, 0.2, 1),
			"primary": Color(0.2, 0.4, 0.8, 1),
			"secondary": Color(0.3, 0.3, 0.4, 1),
			"accent": Color(0.8, 0.6, 0.2, 1),
			"text": Color(1, 1, 1, 1),
			"text_disabled": Color(0.5, 0.5, 0.5, 1)
		}
	}
}

func get_theme(theme_id: String) -> Dictionary:
	if theme_id in themes:
		return themes[theme_id]
	return themes["default"]

func get_theme_ids() -> Array:
	return themes.keys()

func get_color(theme_id: String, color_name: String) -> Color:
	var theme = get_theme(theme_id)
	if color_name in theme.colors:
		return theme.colors[color_name]
	return Color.WHITE
