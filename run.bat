@echo off
echo Starting Pixel Abyss...
python pixaby.py
if errorlevel 1 (
    echo.
    echo Error running the game. Make sure Python is installed.
    pause
)