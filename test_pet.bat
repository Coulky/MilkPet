@echo off
chcp 65001 >nul 2>nul
title 🐱 桌面宠物 - 测试运行

echo.
echo ╔═══════════════════════════════╗
echo ║  🐱 桌面宠物 - 测试模式      ║
echo ╚═══════════════════════════════╝
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python!
    pause
    exit /b 1
)

python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 正在安装 PyQt5...
    pip install PyQt5 -q
)

echo ✅ 启动桌面宠物...
echo 💡 关闭窗口后程序会退出（托盘图标会消失）
echo.

python pet_app.py

pause