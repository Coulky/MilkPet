@echo off
chcp 65001 >nul 2>nul
title 🐱 桌面宠物 - 系统托盘版

echo.
echo ╔══════════════════════════════════════╗
echo ║     🐱 桌面宠物 系统托盘版 v1.0     ║
echo ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 Python!
    echo.
    echo 请先安装 Python: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 正在安装 PyQt5...
    pip install PyQt5 -q
    if %errorlevel% neq 0 (
        echo ❌ PyQt5 安装失败!
        pause
        exit /b 1
    )
)

echo.
echo ✅ 正在启动桌面宠物...
echo 💡 启动后:
echo    • 查看右下角系统托盘区域（可能有 ^ 隐藏图标）
echo    • 如果提示找不到程序，右键托盘图标选择 "📂 选择程序..."
echo    • 首次使用需要先在 Godot 中导出游戏
echo.

python tray_launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败！
    echo.
    echo 请按以下步骤操作：
    echo   1️⃣ 打开 Godot 编辑器
    echo   2️⃣ 点击菜单 Export → Export Project
    echo   3️⃣ 导出后会生成 milk.exe 文件
    echo   4️⃣ 再次运行此脚本，或右键托盘图标选择程序位置
    echo.
    pause
)