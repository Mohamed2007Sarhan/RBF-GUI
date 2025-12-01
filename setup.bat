@echo off
echo Installing required Python packages...
pip install -r requirements.txt || python -m pip install -r requirements.txt
echo.
echo Setup complete! You can now run the Bitcoin RBF GUI tool.
echo Double-click run_gui.bat to start the application.
pause