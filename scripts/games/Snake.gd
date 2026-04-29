extends Node2D

@export var grid_size: int = 20
@export var cell_size: int = 25

var snake: Array = []
var direction: Vector2 = Vector2.RIGHT
var food: Vector2 = Vector2.ZERO
var score: int = 0
var is_running: bool = false
var timer: Timer
var rng: RandomNumberGenerator

@onready var score_label = get_node("ScoreLabel")
@onready var back_button = get_node("BackButton")
@onready var start_button = get_node("StartButton")
@onready var game_area = get_node("GameArea")

func _ready():
    rng = RandomNumberGenerator.new()
    timer = Timer.new()
    timer.wait_time = 0.15
    timer.autostart = false
    add_child(timer)
    timer.timeout.connect(_on_timer_timeout)
    
    reset_game()

func reset_game():
    snake = [Vector2(5, 5)]
    direction = Vector2.RIGHT
    score = 0
    score_label.text = "分数: 0"
    is_running = false
    timer.stop()
    spawn_food()
    update_game_area()

func spawn_food():
    var max_x = grid_size - 1
    var max_y = grid_size - 1
    
    while true:
        food = Vector2(rng.rangei(0, max_x + 1), rng.rangei(0, max_y + 1))
        if not snake.has(food):
            break

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
    
    if event.is_action_pressed("ui_right") and direction != Vector2.LEFT:
        direction = Vector2.RIGHT
    elif event.is_action_pressed("ui_left") and direction != Vector2.RIGHT:
        direction = Vector2.LEFT
    elif event.is_action_pressed("ui_up") and direction != Vector2.DOWN:
        direction = Vector2.UP
    elif event.is_action_pressed("ui_down") and direction != Vector2.UP:
        direction = Vector2.DOWN

func _on_timer_timeout():
    if not is_running:
        return
    
    var head = snake[0] + direction
    
    if head.x < 0 or head.x >= grid_size or head.y < 0 or head.y >= grid_size:
        game_over()
        return
    
    if snake.has(head):
        game_over()
        return
    
    snake.insert(0, head)
    
    if head == food:
        score += 10
        score_label.text = "分数: " + str(score)
        spawn_food()
    else:
        snake.pop_back()
    
    update_game_area()

func update_game_area():
    for child in game_area.get_children():
        child.queue_free()
    
    for segment in snake:
        var rect = ColorRect.new()
        rect.size = Vector2(cell_size - 2, cell_size - 2)
        rect.position = segment * cell_size + Vector2(1, 1)
        rect.color = Color(0, 1, 0)
        game_area.add_child(rect)
    
    var food_rect = ColorRect.new()
    food_rect.size = Vector2(cell_size - 2, cell_size - 2)
    food_rect.position = food * cell_size + Vector2(1, 1)
    food_rect.color = Color(1, 0, 0)
    game_area.add_child(food_rect)

func game_over():
    is_running = false
    timer.stop()
    score_label.text = "游戏结束! 分数: " + str(score)