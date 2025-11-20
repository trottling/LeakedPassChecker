@echo off
setlocal

cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

REM Проверка зависимостей
"%PYTHON%" -m pip install -r requirements.txt

REM Очистка прошлых сборок
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q main.spec 2>nul

REM Сборка через PyInstaller
"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name "LeakChecker" ^
  --onedir ^
  --icon "assets\icon.ico" ^
  --add-data "assets\excel.png;." ^
  --add-data "assets\file.png;." ^
  --add-data "assets\icon.png;." ^
  --add-data "assets\loading.png;." ^
  --add-data "assets\start.png;." ^
  --add-data "assets\main.ui;." ^
  main.py

echo.
echo ==========================
echo   PyInstaller build done
echo   dist\LogonChecker\
echo ==========================
echo.
pause
