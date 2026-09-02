@echo off
setlocal enabledelayedexpansion
title MaskFace Build
cd /d "%~dp0"

echo ========================================
echo   MaskFace - PyInstaller Build
echo ========================================
echo/

echo [1/5] Checking models...
if not exist "models\deploy.prototxt" (
    echo   [ERROR] models\deploy.prototxt not found!
    pause
    exit /b 1
)
if not exist "models\res10_300x300_ssd_iter_140000_fp16.caffemodel" (
    echo   [ERROR] models\res10_300x300_ssd_iter_140000_fp16.caffemodel not found!
    pause
    exit /b 1
)
echo   [OK] Models ready

echo/
echo [2/5] Checking icon...
if not exist "maskface.ico" (
    echo   [WARN] maskface.ico not found, skipping...
    echo   Run: .venv\Scripts\python.exe -c "from PIL import Image; img=Image.open(r'mask.png'); img.save('maskface.ico',format='ICO',sizes=[(256,256),(48,48),(32,32),(16,16)])"
)
echo   [OK] Icon check done

echo/
echo [3/5] Cleaning old build...
taskkill /f /im MaskFace.exe >nul 2>&1
timeout /t 2 /nobreak >nul
if exist "dist\MaskFace\" rmdir /s /q "dist\MaskFace"
if exist "build\maskface\" rmdir /s /q "build\maskface"
echo   [OK] Clean done

echo/
echo [4/5] Installing dependencies...
uv sync
if !errorlevel! neq 0 (
    echo   [ERROR] Dependency install failed!
    pause
    exit /b 1
)
echo   [OK] Dependencies ready

echo/
echo [5/5] Running PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller maskface.spec --noconfirm
if !errorlevel! neq 0 (
    echo/
    echo   [ERROR] Build failed! Check output above.
    pause
    exit /b 1
)

echo/
echo ========================================
echo   SUCCESS! Output: dist\MaskFace\MaskFace.exe
echo ========================================
echo/
pause