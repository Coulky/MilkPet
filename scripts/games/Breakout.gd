extends Node2D

@export var paddle_width: int = 120
@export var paddle_height: int = 15
@export var ball_radius: int = 10
@export var brick_rows: int = 5
@export var brick_cols: int = 10
@export var brick_width: int = 60
@export var brick_height: int = 25
@export var brick_padding: int = 5
@export var brick_offset_top: int = 60
@export var brick_offset_left: int = 35

var paddle_position: Vector2 = Vector2.ZERO
var ball_position: Vector2 = Vector2.ZERO
var ball_velocity: Vector2 = Vector2.ZERO
var bricks: Array = []
var score: int = 0
var lives: int = 3
var is_running: bool = false
var timer: Timer
var rng: RandomNumberGenerator

var brick_colors = [
    Color(1, 0, 0),
    Color(1, 0.5, 0),
    Color(1, 1, 0),
    Color(0, 1, 0),
    Color(0, 0, 1)
]

@onready var score_label = get_node("ScoreLabel")
@onready var lives_label = get_node("LivesLabel")
@onready var back_button = get_node("BackButton")
@onready var start_button = get_node("StartButton")
@onready var game_area = get_node("GameArea")

func _ready():
    rng = RandomNumberGenerator.new()
    timer = Timer.new()
    timer.wait_time = 0.016
    timer.autostart = false
    add_child(timer)
    timer.timeout.connect(_on_timer_timeout)
    
    init_bricks()
    reset_game()

func init_bricks():
    bricks = []
    
    for row in range(brick_rows):
        bricks.append([])
        for col in range(brick_cols):
            bricks[row].append({
                "x": brick_offset_left + col * (brick_width + brick_padding),
                "y": brick_offset_top + row * (brick_height + brick_padding),
                "width": brick_width,
                "height": brick_height,
                "color": brick_colors[row],
                "visible": true
            })

func reset_game():
    paddle_position = Vector2(
        (600 - paddle_width) / 2,
        550
    )
    
    ball_position = Vector2(
        300,
        530
    )
    
    ball_velocity = Vector2(4, -4).rotated(rng.range(-0.3, 0.3))
    
    score = 0
    lives = 3
    score_label.text = "分数: 0"
    lives_label.text = "生命: 3"
    
    is_running = false
    timer.stop()
    
    init_bricks()
    update_game_area()

func _on_start_button_pressed():
    if not is_running:
        reset_game()
        is_running = true
        timer.start()

func _on_back_button_pressed():
    timer.stop()
    get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _input(event: InputEvent):
    if not is_running:
        return
    
    if event is InputEventMouseMotion:
        var mouse_x = get_global_mouse_position().x
        paddle_position.x = clamp(mouse_x - paddle_width / 2, 0, 600 - paddle_width)

func _on_timer_timeout():
    if not is_running:
        return
    
    ball_position += ball_velocity
    
    if ball_position.x - ball_radius <= 0 or ball_position.x + ball_radius >= 600:
        ball_velocity.x = -ball_velocity.x
    
    if ball_position.y - ball_radius <= 0:
        ball_velocity.y = -ball_velocity.y
    
    if ball_position.y + ball_radius >= 600:
        lives -= 1
        lives_label.text = "生命: " + str(lives)
        
        if lives <= 0:
            game_over()
        else:
            ball_position = Vector2(300, 530)
            ball_velocity = Vector2(4, -4).rotated(rng.range(-0.3, 0.3))
    
    check_paddle_collision()
    check_brick_collision()
    update_game_area()

func check_paddle_collision():
    var paddle_rect = Rect2(
        paddle_position.x,
        paddle_position.y,
        paddle_width,
        paddle_height
    )
    
    var ball_rect = Rect2(
        ball_position.x - ball_radius,
        ball_position.y - ball_radius,
        ball_radius * 2,
        ball_radius * 2
    )
    
    if paddle_rect.intersects(ball_rect):
        var hit_pos = (ball_position.x - paddle_position.x) / paddle_width
        var angle = (hit_pos - 0.5) * PI * 0.6
        ball_velocity = Vector2(4, -4).rotated(angle).normalized() * 4
        ball_position.y = paddle_position.y - ball_radius

func check_brick_collision():
    for row in bricks:
        for brick in row:
            if brick["visible"]:
                var brick_rect = Rect2(
                    brick["x"],
                    brick["y"],
                    brick["width"],
                    brick["height"]
                )
                
                var ball_rect = Rect2(
                    ball_position.x - ball_radius,
                    ball_position.y - ball_radius,
                    ball_radius * 2,
                    ball_radius * 2
                )
                
                if brick_rect.intersects(ball_rect):
                    brick["visible"] = false
                    score += 10
                    score_label.text = "分数: " + str(score)
                    
                    var overlap = ball_rect.intersection(brick_rect)
                    
                    if overlap.width < overlap.height:
                        ball_velocity.x = -ball_velocity.x
                    else:
                        ball_velocity.y = -ball_velocity.y
                    
                    check_win()
                    return

func check_win():
    for row in bricks:
        for brick in row:
            if brick["visible"]:
                return
    
    score += 500
    score_label.text = "胜利! 分数: " + str(score)
    is_running = false
    timer.stop()

func update_game_area():
    for child in game_area.get_children():
        child.queue_free()
    
    for row in bricks:
        for brick in row:
            if brick["visible"]:
                var rect = ColorRect.new()
                rect.size = Vector2(brick["width"] - 2, brick["height"] - 2)
                rect.position = Vector2(brick["x"] + 1, brick["y"] + 1)
                rect.color = brick["color"]
                game_area.add_child(rect)
    
    var paddle_rect = ColorRect.new()
    paddle_rect.size = Vector2(paddle_width - 2, paddle_height - 2)
    paddle_rect.position = paddle_position + Vector2(1, 1)
    paddle_rect.color = Color(0.5, 0.5, 0.5)
    game_area.add_child(paddle_rect)
    
    var ball_circle = ColorRect.new()
    ball_circle.size = Vector2(ball_radius * 2, ball_radius * 2)
    ball_circle.position = ball_position - Vector2(ball_radius, ball_radius)
    ball_circle.color = Color(1, 1, 1)
    game_area.add_child(ball_circle)

func game_over():
    is_running = false
    timer.stop()
    score_label.text = "游戏结束! 分数: " + str(score)