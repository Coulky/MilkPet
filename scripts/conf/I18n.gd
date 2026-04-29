extends Node

var translations = {
	"zh-CN": {
		"lang_name": "简体中文",
		"game_collection": "休闲游戏合集",
		"game_library": "游戏库",
		"continue_game": "继续游戏",
		"achievements": "成就",
		"settings": "设置",
		"quit": "退出",
		"language": "语言",
		"resolution": "分辨率",
		"windowed": "窗口化",
		"fullscreen": "全屏",
		"sound_volume": "音量",
		"display": "窗口模式",
		"music_volume": "音乐音量",
		"shortcuts": "快捷键",
		"back": "返回",
		"confirm": "确认",
		"game": "游戏",
		"score": "分数",
		"pause": "暂停",
		"game_over": "游戏结束",
		"achievement_unlocked": "成就解锁",
		"apply": "应用",
		"reset": "恢复默认",
		"theme": "主题",
		"theme_default": "默认",
		"sudoku": "数独"
	},
	"zh-TW": {
		"lang_name": "繁體中文",
		"game_collection": "休閒遊戲合集",
		"game_library": "遊戲庫",
		"continue_game": "繼續遊戲",
		"achievements": "成就",
		"settings": "設置",
		"quit": "退出",
		"language": "語言",
		"resolution": "分辨率",
		"windowed": "窗口化",
		"fullscreen": "全屏",
		"sound_volume": "音量",
		"display": "窗口模式",
		"music_volume": "音樂音量",
		"shortcuts": "快捷鍵",
		"back": "返回",
		"confirm": "確認",
		"game": "遊戲",
		"score": "分數",
		"pause": "暫停",
		"game_over": "遊戲結束",
		"achievement_unlocked": "成就解鎖",
		"apply": "應用",
		"reset": "恢復默認",
		"theme": "主題",
		"theme_default": "默認",
		"sudoku": "數獨"
	},
	"en": {
		"lang_name": "English",
		"game_collection": "Casual Games Collection",
		"game_library": "Game Library",
		"continue_game": "Continue Game",
		"achievements": "Achievements",
		"settings": "Settings",
		"quit": "Quit",
		"language": "Language",
		"resolution": "Resolution",
		"windowed": "Windowed",
		"fullscreen": "Fullscreen",
		"sound_volume": "Sound Volume",
		"display": "Window Mode",
		"music_volume": "Music Volume",
		"shortcuts": "Shortcuts",
		"back": "Back",
		"confirm": "Confirm",
		"game": "Game",
		"score": "Score",
		"pause": "Pause",
		"game_over": "Game Over",
		"achievement_unlocked": "Achievement Unlocked",
		"apply": "Apply",
		"reset": "Reset",
		"theme": "Theme",
		"theme_default": "Default",
		"sudoku": "Sudoku"
	},
	"ja": {
		"lang_name": "日本語",
		"game_collection": "カジュアルゲームコレクション",
		"game_library": "ゲームライブラリ",
		"continue_game": "ゲームを続ける",
		"achievements": "アチーブメント",
		"settings": "設定",
		"quit": "終了",
		"language": "言語",
		"resolution": "解像度",
		"windowed": "ウィンドウ",
		"fullscreen": "フルスクリーン",
		"sound_volume": "サウンド音量",
		"display": "ウィンドウモード",
		"music_volume": "音楽音量",
		"shortcuts": "ショートカット",
		"back": "戻る",
		"confirm": "確認",
		"game": "ゲーム",
		"score": "スコア",
		"pause": "一時停止",
		"game_over": "ゲームオーバー",
		"achievement_unlocked": "アチーブメント解除",
		"apply": "適用",
		"reset": "リセット",
		"theme": "テーマ",
		"theme_default": "デフォルト",
		"sudoku": "数独"
	}
}

func translate(key, lang_code = ""):
	var lang = lang_code if lang_code != "" else GlobalData.current_language
	if lang in translations and key in translations[lang]:
		return translations[lang][key]
	return key

func get_display_name(lang_code: String) -> String:
	if lang_code in translations and "lang_name" in translations[lang_code]:
		return translations[lang_code]["lang_name"]
	return lang_code

func get_all_codes() -> Array:
	return translations.keys()
