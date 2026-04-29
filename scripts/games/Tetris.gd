extends Node2D

@export var grid_width: int = 10
@export var grid_height: int = 20
@export var cell_size: int = 30

var grid: Array = []
var current_piece: Dictionary = {}
var current_position: Vector2 = Vector2.ZERO
var score: int = 0
var is_running: bool = false
var timer: Timer
var rng: RandomNumberGenerator

var shapes = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]]
}

var colors = {
    "I": Color(0, 1, 1),
    "O": Color(1, 1, 0),
    "T": Color(0.5, 0, 1),
    "S": Color(0, 1, 0),
    "Z": Color(1, 0, 0),
    "J": Color(0, 0, 1),
    "L": Color(1, 0.5, 0)
}

@onready var score_label = get_node("ScoreLabel")
@onready var back_button = get_node("BackButton")
@onready var start_button = get_node("StartButton")
@onready var game_area = get_node("GameArea")

func _ready():
    rng = RandomNumberGenerator.new()
    timer = Timer.new()
    timer.wait_time = 0.8
    timer.autostart = false
    add_child(timer)
    timer.timeout.connect(_on_timer_timeout)
    
    init_grid()

func init_grid():
    grid = []
    for y in range(grid_height):
        grid.append([])
        for x in range(grid_width):
            grid[y].append(0)

func reset_game():
    init_grid()
    score = 0
    score_label.text = "分数: 0"
    is_running = false
    timer.stop()
    spawn_piece()
    update_game_area()

func spawn_piece():
    var shape_keys = shapes.keys()
    var random_key = shape_keys[rng.rangei(0, shape_keys.size())]
    
    current_piece = {
        "shape": shapes[random_key],
        "color": colors[random_key],
        "type": random_key
    }
    
    current_position = Vector2(
        (grid_width - current_piece["shape"][0].size()) / 2,
        0
    )
    
    if not is_valid_position(current_position, current_piece["shape"]):
        game_over()

func is_valid_position(pos: Vector2, shape: Array) -> bool:
    for y in range(shape.size()):
        for x in range(shape[y].size()):
            if shape[y][x] == 1:
                var grid_x = pos.x + x
                var grid_y = pos.y + y
                
                if grid_x < 0 or grid_x >= grid_width or grid_y >= grid_height:
                    return false
                
                if grid_y >= 0 and grid[grid_y][grid_x] != 0:
                    return false
    
    return true

func rotate_piece():
    var shape = current_piece["shape"]
    var rotated = []
    
    for x in range(shape[0].size()):
        rotated.append([])
        for y in range(shape.size() - 1, -1, -1):
            rotated[x].append(shape[y][x])
    
    if is_valid_position(current_position, rotated):
        current_piece["shape"] = rotated
        update_game_area()

func move_piece(dx: int, dy: int):
    var new_pos = current_position + Vector2(dx, dy)
    
    if is_valid_position(new_pos, current_piece["shape"]):
        current_position = new_pos
        update_game_area()
    elif dy > 0:
        lock_piece()

func lock_piece():
    var shape = current_piece["shape"]
    var color = current_piece["color"]
    
    for y in range(shape.size()):
        for x in range(shape[y].size()):
            if shape[y][x] == 1:
                var grid_x = current_position.x + x
                var grid_y = current_position.y + y
                
                if grid_y >= 0:
                    grid[grid_y][grid_x] = color
    
    clear_lines()
    spawn_piece()
    update_game_area()

func clear_lines():
    var lines_cleared = 0
    
    for y in range(grid_height - 1, -1, -1):
        var is_full = true
        
        for x in range(grid_width):
            if grid[y][x] == 0:
                is_full = false
                break
        
        if is_full:
            grid.remove_at(y)
            var empty_line = []
            for i in range(grid_width):
                empty_line.append(0)
            grid.insert(0, empty_line)
            lines_cleared += 1
            y += 1
    
    if lines_cleared > 0:
        score += lines_cleared * 100
        score_label.text = "分数: " + str(score)
        
        timer.wait_time = max(0.2, 0.8 - score / 1000)

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
    
    if event.is_action_pressed("ui_right"):
        move_piece(1, 0)
    elif event.is_action_pressed("ui_left"):
        move_piece(-1, 0)
    elif event.is_action_pressed("ui_down"):
        move_piece(0, 1)
    elif event.is_action_pressed("ui_accept"):
        rotate_piece()

func _on_timer_timeout():
    if is_running:
        move_piece(0, 1)

func update_game_area():
    for child in game_area.get_children():
        child.queue_free()
    
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] != 0:
                var rect = ColorRect.new()
                rect.size = Vector2(cell_size - 1, cell_size - 1)
                rect.position = Vector2(x * cell_size, y * cell_size)
                rect.color = grid[y][x]
                game_area.add_child(rect)
    
    var shape = current_piece["shape"]
    var color = current_piece["color"]
    
    for y in range(shape.size()):
        for x in range(shape[y].size()):
            if shape[y][x] == 1:
                var rect = ColorRect.new()
                rect.size = Vector2(cell_size - 1, cell_size - 1)
                rect.position = Vector2(
                    (current_position.x + x) * cell_size,
                    (current_position.y + y) * cell_size
                )
                rect.color = color
                game_area.add_child(rect)

func game_over():
    is_running = false
    timer.stop()
    score_label.text = "游戏结束! 分数: " + str(score)