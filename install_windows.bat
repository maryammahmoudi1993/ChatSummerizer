@echo off
echo ========================================
echo Chat Summarizer - Windows Installation
echo ========================================

echo.
echo Step 1: Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 2: Installing PyTorch (CPU version for Windows)...
pip install torch==2.2.0+cpu torchvision==0.17.0+cpu torchaudio==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu

echo.
echo Step 3: Installing core dependencies...
pip install fastapi==0.104.1 uvicorn==0.24.0 redis==5.0.1 python-dotenv==1.0.0 pydantic==2.5.0 jinja2==3.1.2 python-multipart==0.0.6

echo.
echo Step 4: Installing LangChain and OpenAI...
pip install langchain==0.0.350 langchain-openai==0.0.2 openai==1.3.7

echo.
echo Step 5: Installing ML libraries (Windows compatible versions)...
pip install numpy==1.26.4 pandas==2.1.4 scikit-learn==1.3.2 transformers==4.35.2

echo.
echo Step 6: Creating .env file...
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
echo 3. Run: python main.py
echo.
pause 