@echo off
setlocal

cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
set ZIP_NAME=LeakedPassChecker.zip
set ZIP_PATH=dist\%ZIP_NAME%

"%PYTHON%" -m pip install -r requirements.txt

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q main.spec 2>nul

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --noconsole ^
  --clean ^
  --name "LeakedPassChecker" ^
  --onefile ^
  --icon "assets\icon.ico" ^
  --add-data "assets\*.*;." ^
  main.py

echo.
echo ==========================
echo   PyInstaller build done
echo   dist\LeakedPassChecker.exe
echo ==========================
echo.

if not exist "dist" (
    echo dist folder missing, nothing to zip
    pause
    exit /b 1
)

echo Creating ZIP package...

if exist "%ZIP_PATH%" del "%ZIP_PATH%"

7z a "%ZIP_PATH%" ^
    "build_pyinstaller.bat" ^
    "main.py" ^
    "requirements.txt" ^
    "requirements_dev.txt" ^
    "test_data_creator.py" ^
    "app" ^
    "assets" ^
    "dist\LeakedPassChecker.exe"

echo.
echo ==========================
echo ZIP Done: %ZIP_PATH%
echo ==========================
echo.

pause
