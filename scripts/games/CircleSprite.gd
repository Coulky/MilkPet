extends Node2D

var radius: float = 12.0
var color: Color = Color(1.0, 0.2, 0.2, 1.0)

func _draw():
	draw_circle(Vector2.ZERO, radius, color)