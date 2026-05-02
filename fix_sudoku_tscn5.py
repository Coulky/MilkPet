#!/usr/bin/env python3
# -*- coding: utf-8 -*-

content = '''[gd_scene load_steps=14 format=3 uid="uid://b5v0q1lq0j6x"]

[ext_resource type="Script" path="res://scripts/games/sudoku/SudokuMain.gd" id="1"]
[ext_resource type="Script" path="res://scripts/games/sudoku/SudokuUI.gd" id="2"]
[ext_resource type="Texture2D" path="res://assets/images/back.png" id="3"]
[ext_resource type="Texture2D" path="res://assets/images/restart.png" id="4"]
[ext_resource type="Texture2D" path="res://assets/images/1.png" id="5"]
[ext_resource type="Texture2D" path="res://assets/images/2.png" id="6"]
[ext_resource type="Texture2D" path="res://assets/images/3.png" id="7"]
[ext_resource type="Texture2D" path="res://assets/images/4.png" id="8"]
[ext_resource type="Texture2D" path="res://assets/images/5.png" id="9"]
[ext_resource type="Texture2D" path="res://assets/images/6.png" id="10"]
[ext_resource type="Texture2D" path="res://assets/images/7.png" id="11"]
[ext_resource type="Texture2D" path="res://assets/images/8.png" id="12"]
[ext_resource type="Texture2D" path="res://assets/images/9.png" id="13"]

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
theme_override_colors/background_color = Color(1, 1, 1, 1)

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

[node name="BackButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("3")

[node name="RestartButtonContainer" type="Control" parent="SudokuUI/MainContainer/LeftPanel"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)

[node name="RestartButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel/RestartButtonContainer"]
layout_mode = 2
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("4")

[node name="RestartLabelBg" type="PanelContainer" parent="SudokuUI/MainContainer/LeftPanel/RestartButtonContainer"]
layout_mode = 2
anchors_preset = 0
anchor_left = 0.15
anchor_right = 0.85
anchor_top = 0.7
anchor_bottom = 0.9
custom_minimum_size = Vector2(0, 0)
size_flags_horizontal = 3
size_flags_vertical = 3

[node name="RestartLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel/RestartButtonContainer/RestartLabelBg"]
layout_mode = 1
text = "重开"
horizontal_alignment = 1
vertical_alignment = 1
custom_minimum_size = Vector2(0, 0)
theme_override_colors/font_color = Color(0, 0, 0, 1)

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

[node name="NoteModeButtonContainer" type="Control" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)

[node name="NoteModeButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer"]
layout_mode = 2
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("4")

[node name="NoteModeLabelBg" type="PanelContainer" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer"]
layout_mode = 2
anchors_preset = 0
anchor_left = 0.15
anchor_right = 0.85
anchor_top = 0.7
anchor_bottom = 0.9
custom_minimum_size = Vector2(0, 0)
size_flags_horizontal = 3
size_flags_vertical = 3

[node name="NoteModeLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer/NoteModeLabelBg"]
layout_mode = 1
text = "笔记"
horizontal_alignment = 1
vertical_alignment = 1
custom_minimum_size = Vector2(0, 0)
theme_override_colors/font_color = Color(0, 0, 0, 1)

[node name="HintButtonContainer" type="Control" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)

[node name="HintButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/HintButtonContainer"]
layout_mode = 2
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("4")

[node name="HintLabelBg" type="PanelContainer" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/HintButtonContainer"]
layout_mode = 2
anchors_preset = 0
anchor_left = 0.15
anchor_right = 0.85
anchor_top = 0.7
anchor_bottom = 0.9
custom_minimum_size = Vector2(0, 0)
size_flags_horizontal = 3
size_flags_vertical = 3

[node name="HintLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/HintButtonContainer/HintLabelBg"]
layout_mode = 1
text = "提示"
horizontal_alignment = 1
vertical_alignment = 1
custom_minimum_size = Vector2(0, 0)
theme_override_colors/font_color = Color(0, 0, 0, 1)

[node name="AutoNotesButtonContainer" type="Control" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)

[node name="AutoNotesButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/AutoNotesButtonContainer"]
layout_mode = 2
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("4")

[node name="AutoNotesLabelBg" type="PanelContainer" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/AutoNotesButtonContainer"]
layout_mode = 2
anchors_preset = 0
anchor_left = 0.15
anchor_right = 0.85
anchor_top = 0.7
anchor_bottom = 0.9
custom_minimum_size = Vector2(0, 0)
size_flags_horizontal = 3
size_flags_vertical = 3

[node name="AutoNotesLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/AutoNotesButtonContainer/AutoNotesLabelBg"]
layout_mode = 1
text = "自动笔记"
horizontal_alignment = 1
vertical_alignment = 1
custom_minimum_size = Vector2(0, 0)
theme_override_colors/font_color = Color(0, 0, 0, 1)

[node name="NewGameButtonContainer" type="Control" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons"]
layout_mode = 1
custom_minimum_size = Vector2(50, 50)

[node name="NewGameButton" type="Button" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NewGameButtonContainer"]
layout_mode = 2
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
custom_minimum_size = Vector2(50, 50)
flat = true
expand_icon = true
icon = ExtResource("4")

[node name="NewGameLabelBg" type="PanelContainer" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NewGameButtonContainer"]
layout_mode = 2
anchors_preset = 0
anchor_left = 0.15
anchor_right = 0.85
anchor_top = 0.7
anchor_bottom = 0.9
custom_minimum_size = Vector2(0, 0)
size_flags_horizontal = 3
size_flags_vertical = 3

[node name="NewGameLabel" type="Label" parent="SudokuUI/MainContainer/LeftPanel/ActionButtons/NewGameButtonContainer/NewGameLabelBg"]
layout_mode = 1
text = "新游戏"
horizontal_alignment = 1
vertical_alignment = 1
custom_minimum_size = Vector2(0, 0)
theme_override_colors/font_color = Color(0, 0, 0, 1)

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

[node name="Num1" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("5")

[node name="Num2" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("6")

[node name="Num3" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("7")

[node name="Num4" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("8")

[node name="Num5" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("9")

[node name="Num6" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("10")

[node name="Num7" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("11")

[node name="Num8" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("12")

[node name="Num9" type="Button" parent="SudokuUI/MainContainer/CenterArea/NumberButtons"]
layout_mode = 1
size_flags_horizontal = 8
size_flags_stretch_ratio = 1.0
custom_minimum_size = Vector2(50, 50)
expand_icon = true
icon = ExtResource("13")

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

[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/BackButton" to="." callable="_on_back"]
[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/RestartButtonContainer/RestartButton" to="." callable="_on_restart"]
[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/ActionButtons/NoteModeButtonContainer/NoteModeButton" to="." callable="_on_note_mode_button"]
[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/ActionButtons/HintButtonContainer/HintButton" to="." callable="_on_hint_requested"]
[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/ActionButtons/AutoNotesButtonContainer/AutoNotesButton" to="." callable="_on_auto_notes_requested"]
[connection signal="pressed" from="SudokuUI/MainContainer/LeftPanel/ActionButtons/NewGameButtonContainer/NewGameButton" to="." callable="_on_new_game"]
'''

with open('e:\\TraeProject\\CasualGames\\scenes\\games\\sudoku\\sudoku.tscn', 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully!")
