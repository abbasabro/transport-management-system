@echo off
REM Activate the virtual environment (adjust path if needed)
call venv\Scripts\activate.bat

REM Clean previous build
rmdir /s /q dist
rmdir /s /q build

REM Run PyInstaller with correct resource paths
pyinstaller ^
  --name "BBSUTSD-TMS" ^
  --windowed ^
  --icon="resources/images/logo.png" ^
  --add-data "transport_db.db;." ^
  --add-data "resources;resources" ^
  --add-data "reports;reports" ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import reportlab.lib.pagesizes ^
  --hidden-import reportlab.graphics ^
  --hidden-import bcrypt ^
  --clean ^
  main.py

echo Build completed.
pause