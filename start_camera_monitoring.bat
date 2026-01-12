@echo off
echo ============================================
echo FLAME Guard - Camera Monitoring System
echo ============================================
echo.
echo Starting real-time detection...
echo Press Ctrl+C to stop
echo.

cd /d D:\FlameGuard
call venv\Scripts\activate.bat
python camera_module\live_detection.py

pause
