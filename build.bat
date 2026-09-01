@echo off
title MaskFace - 构建打包
cd /d "%~dp0"

echo ========================================
echo   MaskFace - PyInstaller 打包构建 (onedir)
echo ========================================
echo.

:: Step 1: 检查模型文件
echo [1/4] 检查模型文件...
if not exist "models\deploy.prototxt" (
    echo   [错误] models\deploy.prototxt 未找到！
    pause
    exit /b 1
)
if not exist "models\res10_300x300_ssd_iter_140000_fp16.caffemodel" (
    echo   [错误] models\res10_300x300_ssd_iter_140000_fp16.caffemodel 未找到！
    pause
    exit /b 1
)
echo   [OK] 模型文件已就绪

:: Step 2: 确保依赖已安装
echo.
echo [2/4] 检查依赖...
uv sync
if %ERRORLEVEL% neq 0 (
    echo   [错误] 依赖安装失败！
    pause
    exit /b 1
)
echo   [OK] 依赖已就绪

:: Step 3: 执行 PyInstaller 打包
echo.
echo [3/4] 执行 PyInstaller 打包...
echo   这可能需要几分钟，请耐心等待...

uv run pyinstaller maskface.spec --clean --noconfirm

if %ERRORLEVEL% neq 0 (
    echo   [错误] 打包失败！
    pause
    exit /b 1
)

:: Step 4: 打包为 zip
echo.
echo [4/4] 打包为 zip...
if exist "dist\MaskFace" (
    powershell -Command "Compress-Archive -Path 'dist\MaskFace' -DestinationPath 'dist\MaskFace.zip' -Force"
    echo   [OK] dist\MaskFace.zip 已生成
)

echo.
echo ========================================
echo   构建完成！
echo   输出: dist\MaskFace\  (文件夹)
echo   压缩包: dist\MaskFace.zip
echo ========================================
echo.
pause