# Chat Summarizer - Windows Installation Script
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Green
Write-Host "Chat Summarizer - Windows Installation" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Upgrading pip and setuptools..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "Step 2: Installing PyTorch (CPU version for Windows)..." -ForegroundColor Yellow
pip install torch==2.2.0+cpu torchvision==0.17.0+cpu torchaudio==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu

Write-Host ""
Write-Host "Step 3: Installing core dependencies..." -ForegroundColor Yellow
pip install fastapi==0.104.1 uvicorn==0.24.0 redis==5.0.1 python-dotenv==1.0.0 pydantic==2.5.0 jinja2==3.1.2 python-multipart==0.0.6

Write-Host ""
Write-Host "Step 4: Installing LangChain and OpenAI..." -ForegroundColor Yellow
pip install langchain==0.0.350 langchain-openai==0.0.2 openai==1.3.7

Write-Host ""
Write-Host "Step 5: Installing ML libraries (Windows compatible versions)..." -ForegroundColor Yellow
pip install numpy==1.26.4 pandas==2.1.4 scikit-learn==1.3.2 transformers==4.35.2

Write-Host ""
Write-Host "Step 6: Creating .env file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    "OPENAI_API_KEY=your_openai_api_key_here" | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Created .env file" -ForegroundColor Green
    Write-Host "Please edit .env file with your OpenAI API key" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your OpenAI API key" -ForegroundColor White
Write-Host "2. Install Redis (or use Docker)" -ForegroundColor White
Write-Host "3. Run: python main.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue" 