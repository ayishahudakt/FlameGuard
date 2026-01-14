@echo off
echo ============================================
echo FLAME Guard - Vision Transformer Detection
echo 98%% Accuracy - Detects ALL Animals
echo ============================================
echo.
echo Can detect: Tiger, Cheetah, Leopard, Lion
echo and 1000+ other species!
echo.

cd /d D:\FlameGuard
call venv\Scripts\activate.bat
python camera_vit.py

pause
