#!/usr/bin/env python3
# -*- coding: utf-8 -*-

content = '''[gd_scene load_steps=3 format=3 uid="uid://b5v0q1lq0j6x"]

[ext_resource type="Script" path="res://scripts/games/sudoku/SudokuMain.gd" id="1"]
[ext_resource type="Script" path="res://scripts/games/sudoku/SudokuUI.gd" id="2"]

[node name="Sudoku" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1")

[node name="SudokuUI" type="Control" parent="."]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("2")

[node name="MainContainer" type="HBoxContainer" parent="SudokuUI"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
theme_override_constants/h_separation = 30

[node name="LeftPanel" type="VBoxContainer" parent="SudokuUI/MainContainer"]
layout_mode = 1
size_flags_horizontal = 4
alignment = 0
theme_override_constants/v_separation = 10

[node name="TimerLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel"]
layout_mode = 1
text = "时间: 00:00"
horizontal_alignment = 1
font_size = 18
theme_override_colors/font_color = Color(0, 0, 0, 1)

[node name="LivesLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel"]
layout_mode = 1
text = "生命: x3"
horizontal_alignment = 1
font_size = 18
theme_override_colors/font_color = Color(0, 0, 0, 1)

[node name="ActionButtons" type="VBoxContainer" parent="SudokuUI/MainContainer/LeftPanel"]
layout_mode = 1
alignment = 0
theme_override_constants/v_separation = 2

[node name="Spacer" type="Control" parent="SudokuUI/MainContainer"]
layout_mode = 1
custom_minimum_size = Vector2(80, 0)
size_flags_horizontal = 1

[node name="CenterArea" type="VBoxContainer" parent="SudokuUI/MainContainer"]
layout_mode = 1
size_flags_horizontal = 8
alignment = 1
theme_override_constants/v_separation = 15

[node name="GridContainer" type="GridContainer" parent="SudokuUI/MainContainer/CenterArea"]
layout_mode = 1
columns = 9
theme_override_constants/h_separation = 0
theme_override_constants/v_separation = 0

[node name="NumberButtons" type="HBoxContainer" parent="SudokuUI/MainContainer/CenterArea"]
layout_mode = 1
alignment = 1
theme_override_constants/h_separation = 8

[node name="MessageDialog" type="Label" parent="SudokuUI"]
layout_mode = 3
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -150.0
offset_top = -50.0
offset_right = 150.0
offset_bottom = 50.0
text = ""
horizontal_alignment = 1
vertical_alignment = 1
font_size = 28
theme_override_colors/font_color = Color(1, 1, 0, 1)
theme_override_colors/background_color = Color(0, 0, 0, 0.8)
visible = false
'''

with open('e:\\TraeProject\\CasualGames\\scenes\\games\\sudoku\\sudoku.tscn', 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully!")
