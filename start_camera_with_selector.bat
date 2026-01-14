@echo off
echo ============================================
echo FLAME Guard - Station Selection Camera
echo ============================================
echo.
echo You will be able to choose which forest
echo station to monitor!
echo.

cd /d D:\FlameGuard
call venv\Scripts\activate.bat
python camera_with_station_selector.py

pause
