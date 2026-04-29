extends Node

var resolutions = [
	{ "width": 800, "height": 600 },
	{ "width": 1024, "height": 576 },
	{ "width": 1024, "height": 600 },
	{ "width": 1024, "height": 768 },
	{ "width": 1152, "height": 864 },
	{ "width": 1280, "height": 720 },
	{ "width": 1280, "height": 768 },
	{ "width": 1280, "height": 800 },
	{ "width": 1280, "height": 960 },
	{ "width": 1280, "height": 1024 },
	{ "width": 1360, "height": 768 },
	{ "width": 1366, "height": 768 },
	{ "width": 1440, "height": 900 },
	{ "width": 1536, "height": 864 },
	{ "width": 1600, "height": 900 },
	{ "width": 1600, "height": 1200 },
	{ "width": 1680, "height": 1050 },
	{ "width": 1920, "height": 1080 },
	{ "width": 1920, "height": 1200 },
	{ "width": 2048, "height": 1152 },
	{ "width": 2048, "height": 1536 },
	{ "width": 2560, "height": 1080 },
	{ "width": 2560, "height": 1440 },
	{ "width": 2560, "height": 1600 },
	{ "width": 3440, "height": 1440 },
	{ "width": 3840, "height": 2160 }
]

var window_modes = ["windowed", "fullscreen"]

func get_default() -> Dictionary:
	return {
		"language": "zh-CN",
		"resolution": { "width": 1280, "height": 720 },
		"window_mode": 0,
		"sound_volume": 1.0,
		"music_volume": 1.0,
		"theme_id": "default",
		"shortcuts": {
			"pause": "Escape",
			"confirm": "Enter",
			"back": "Backspace"
		}
	}
