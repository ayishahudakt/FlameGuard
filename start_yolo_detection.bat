@echo off
echo ============================================
echo FLAME Guard - YOLO Detection System
echo ============================================
echo.
echo Starting high-accuracy detection with YOLOv8...
echo Press Ctrl+C to stop
echo.

cd /d D:\FlameGuard
call venv\Scripts\activate.bat
python camera_yolo.py

pause
