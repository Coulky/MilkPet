@echo off
chcp 65001 >nul 2>nul
title 🐱 打包桌面宠物 - 一键生成独立 EXE

echo.
echo ╔═══════════════════════════════════════════╗
echo ║   🐱 桌面宠物 - 打包为独立可执行文件    ║
echo ╚═══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 Python!
    pause
    exit /b 1
)
echo ✅ Python 已安装

echo.
echo [2/4] 检查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 正在安装 PyInstaller...
    pip install pyinstaller -q
    if %errorlevel% neq 0 (
        echo ❌ PyInstaller 安装失败!
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller 已就绪

echo.
echo [3/4] 检查 PyQt5...
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
echo ✅ PyQt5 已就绪

echo.
echo [4/4] 开始打包...
echo    这可能需要 1-2 分钟，请耐心等待...
echo.

python -m PyInstaller build_exe.spec --noconfirm --clean

if %errorlevel% equ 0 (
    echo.
    echo ╔══════════════════════════════════════╗
    echo ║       ✅ 打包成功！                  ║
    echo ╚══════════════════════════════════════╝
    echo.
    echo 📦 输出位置: dist\桌面宠物\桌面宠物.exe
    echo.
    echo 💡 使用方法:
    echo    1. 先导出 Godot 项目生成 milk.exe
    echo    2. 将 milk.exe 放到 dist\桌面宠物\ 目录下
    echo    3. 双击 "桌面宠物.exe" 即可启动
    echo.
    echo 或者直接复制整个 dist\桌面宠物\ 文件夹给别人使用！
    echo.
    
    if exist "dist\桌面宠物\桌面宠物.exe" (
        explorer "dist\桌面宠物"
    )
) else (
    echo.
    echo ❌ 打包失败！请检查上方错误信息
    pause
)