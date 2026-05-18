@echo off
chcp 65001 >nul
echo ========================================
echo   Milk Pet 打包脚本
echo ========================================
echo.

cd /d "%~dp0.."

if not exist "assets\logo.ico" (
    echo [错误] 找不到图标文件: assets\logo.ico
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo [信息] 当前目录: %CD%
echo [信息] 图标文件: ✅ 已找到
echo.

set "SPEC_FILE=build\MilkPet.spec"

if not exist "%SPEC_FILE%" (
    echo [错误] 找不到配置文件: %SPEC_FILE%
    pause
    exit /b 1
)

echo [步骤 1/3] 清理旧的构建文件...
if exist "build\MilkPet" rmdir /s /q "build\MilkPet"
if exist "dist" rmdir /s /q "dist"
echo         ✅ 清理完成
echo.

echo [步骤 2/3] 开始 PyInstaller 打包...
pyinstaller "%SPEC_FILE%" --clean
if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！请检查上面的错误信息
    pause
    exit /b 1
)
echo         ✅ 打包完成
echo.

echo [步骤 3/3] 验证输出文件...
if exist "dist\MilkPet\MilkPet.exe" (
    echo         ✅ EXE 文件已生成: dist\MilkPet\MilkPet.exe
) else (
    echo         ⚠️ 未找到 EXE 文件，请检查 dist 目录
)

echo.
echo ========================================
echo   打包完成！
echo   输出位置: dist\MilkPet\
echo ========================================
echo.
pause