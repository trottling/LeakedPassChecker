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

REM Сборка через Nuitka
"%PYTHON%" -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=pyqt6 ^
  --output-dir=dist ^
  --windows-icon-from-ico="assets\icon.ico" ^
  --include-data-file="assets\excel.png=excel.png" ^
  --include-data-file="assets\file.png=file.png" ^
  --include-data-file="assets\icon.png=icon.png" ^
  --include-data-file="assets\loading.png=loading.png" ^
  --include-data-file="assets\start.png=start.png" ^
  --include-data-file="assets\main.ui=main.ui" ^
  main.py

echo.
echo ==========================
echo   Nuitka build done
echo   dist\main.exe
echo ==========================
echo.
pause
