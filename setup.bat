@echo off
echo Setting up DiagnosAI...

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
pip install -r requirements.txt

echo Setup complete!
echo.
echo To run the application:
echo venv\Scripts\activate.bat
echo python app.py
pause