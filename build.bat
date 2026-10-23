@echo off
chcp 65001 >nul
rem Сборка Заметок в exe (нужен Python 3.10+)
python -m pip install -r requirements.txt pyinstaller || goto :error
python -m PyInstaller --noconfirm --clean --windowed --name Notes --icon notes.ico --add-data "notes.ico;." notes.py || goto :error
echo.
echo Готово: dist\Notes\Notes.exe
pause
exit /b 0
:error
echo Сборка не удалась, подробности выше.
pause
exit /b 1
