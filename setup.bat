@echo off
REM Setup script for the Question Answer Generator project (Windows)

echo ==========================================
echo Question Answer Generator - Setup
echo ==========================================
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo [OK] Python 3 found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Create .env from .env.example if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created
    echo.
    echo [IMPORTANT] Edit .env and add your OpenAI credentials:
    echo    - OPENAI_API_KEY
    echo    - ASSISTANT_ID
) else (
    echo [OK] .env file already exists
)
echo.

echo ==========================================
echo [OK] Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env and add your OpenAI API key and Assistant ID
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate
echo 3. Run the batch processor:
echo    python -m src.run_batch
echo.
pause
