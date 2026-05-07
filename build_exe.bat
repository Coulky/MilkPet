@echo off
chcp 65001 >nul 2>nul
title 🐱 打包桌面宠物

echo.
echo ╔═════════════════════════════════╗
echo ║   🐱 桌面宠物 - 打包为 EXE    ║
echo ╚═════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/3] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python!
    echo 请安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python OK

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
echo [2/3] 开始打包...
echo    (约需 1-2 分钟)
echo.

python -m PyInstaller build_exe.spec --noconfirm --clean

if %errorlevel% equ 0 (
    echo.
    echo [3/3] ✅ 打包完成！
    echo.
    echo 📦 输出位置: dist\桌面宠物\
    echo.
    
    if exist "dist\桌面宠物\桌面宠物.exe" (
        start explorer "dist\桌面宠物"
        echo 💡 下一步:
        echo    1. 将 Godot 导出的 milk.exe 复制到该文件夹
        echo    2. 双击 桌面宠物.exe 即可运行
        echo.
    )
) else (
    echo ❌ 打包失败！
    pause
)