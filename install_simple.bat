@echo off
echo ========================================
echo Chat Summarizer - Simple Windows Installation
echo ========================================

echo.
echo Step 1: Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 2: Installing dependencies from simple_requirements.txt...
pip install -r simple_requirements.txt

echo.
echo Step 3: Creating .env file...
if not exist .env (
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo Created .env file
    echo Please edit .env file with your OpenAI API key
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Install Redis (or use Docker)
echo 3. Run: python main_simple.py
echo.
pause 