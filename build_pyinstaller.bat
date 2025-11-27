@echo off
setlocal

cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe

REM Проверка зависимостей
"%PYTHON%" -m pip install -r requirements.txt

REM Очистка прошлых сборок
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q main.spec 2>nul

REM Сборка через PyInstaller
"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --noconsole ^
  --clean ^
  --name "LeakChecker" ^
  --onedir ^
  --icon "assets\icon.ico" ^
  --add-data "assets\*.*;." ^
  main.py

echo.
echo ==========================
echo   PyInstaller build done
echo   dist\LogonChecker\
echo ==========================
echo.
pause
