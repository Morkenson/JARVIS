@echo off
echo Building Jarvis Installer...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build executable with PyInstaller
echo Building executable...
pyinstaller jarvis.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

REM Verify PyInstaller output exists
if not exist "dist\Jarvis.exe" (
    if not exist "dist\Jarvis\Jarvis.exe" (
        echo.
        echo ERROR: PyInstaller executable not found!
        echo Expected: dist\Jarvis.exe or dist\Jarvis\Jarvis.exe
        pause
        exit /b 1
    )
)

echo.
echo Executable built successfully!
if exist "dist\Jarvis.exe" (
    echo Found: dist\Jarvis.exe
) else if exist "dist\Jarvis\Jarvis.exe" (
    echo Found: dist\Jarvis\Jarvis.exe
)
echo.

REM Check if Inno Setup is installed
where iscc >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Inno Setup Compiler (iscc.exe) not found in PATH.
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo.
    echo You can manually compile installer.iss using Inno Setup Compiler.
    echo.
    if exist "dist\Jarvis.exe" (
        echo The executable is available at: dist\Jarvis.exe
    ) else (
        echo The executable is available at: dist\Jarvis\Jarvis.exe
    )
    pause
    exit /b 0
)

REM Build installer with Inno Setup
echo Building installer...
iscc installer.iss

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installer built successfully!
echo Location: dist\JarvisSetup.exe
echo ========================================
echo.
pause

