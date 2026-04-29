extends Node

signal timer_timeout

var timer_node: Timer
var timer_game_name: String = ""

func _ready():
	init_timer()

func init_timer():
	if timer_node:
		timer_node.queue_free()
	timer_node = Timer.new()
	add_child(timer_node)
	timer_node.timeout.connect(_on_timer_timeout)

func _on_timer_timeout():
	timer_timeout.emit()

func timer_init(game_name: String, wait_time: float, one_shot: bool = false):
	if timer_game_name != "" and timer_game_name != game_name:
		timer_clear()
	if not timer_node:
		init_timer()
	timer_game_name = game_name
	timer_node.wait_time = wait_time
	timer_node.one_shot = one_shot
	timer_node.start()

func timer_pause(game_name: String):
	if timer_game_name != game_name:
		return
	if timer_node:
		timer_node.stop()

func timer_resume(game_name: String):
	if timer_game_name != game_name:
		return
	if timer_node:
		timer_node.start()

func timer_clear():
	if timer_node:
		timer_node.stop()
		timer_node.queue_free()
		timer_node = null
	timer_game_name = ""
