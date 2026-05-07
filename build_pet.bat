@echo off
chcp 65001 >nul 2>nul
title 🐱 打包桌面宠物 (PyQt5版)

echo.
echo ╔═════════════════════════════════════════╗
echo ║  🐱 桌面宠物 - PyQt5版 一键打包工具    ║
echo ╚═════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/4] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python!
    echo.
    echo 请安装 Python: https://www.python.org/downloads/
    echo 安装时务必勾选: Add Python to PATH
    pause
    exit /b 1
)
python --version
echo ✅ Python OK

echo.
echo [2/4] 检查/安装依赖...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 安装 PyInstaller...
    pip install pyinstaller -q
)
echo ✅ PyInstaller OK

python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 安装 PyQt5...
    pip install PyQt5 -q
)
echo ✅ PyQt5 OK

echo.
echo [3/4] 检查图片文件...
if not exist "assets\images\yongbing.png" (
    echo ⚠️ 警告: 未找到 yongbing.png
    echo   将使用占位符图标
) else (
    echo ✅ 图片文件存在
)

echo.
echo [4/4] 开始打包 EXE...
echo    这可能需要 2-3 分钟，请耐心等待...
echo.

python -m PyInstaller pet_build.spec --noconfirm --clean

if %errorlevel% equ 0 (
    echo.
    echo ╔══════════════════════════════════════╗
    echo ║       ✅ 打包成功！                   ║
    echo ╚══════════════════════════════════════╝
    echo.
    echo 📦 输出位置:
    echo    dist\桌面宠物\桌面宠物.exe
    echo.
    echo 💡 使用方法:
    echo    双击 dist\桌面宠物\桌面宠物.exe 即可启动！
    echo.
    
    if exist "dist\桌面宠物\桌面宠物.exe" (
        start explorer "dist\桌面宠物"
        echo 🎉 已打开输出文件夹
    )
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查上方错误信息
    pause
)

echo.
pause