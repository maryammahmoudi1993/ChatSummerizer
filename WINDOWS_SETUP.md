# Windows Setup Guide for Chat Summarizer

## Installation Issues and Solutions

### Problem: numpy compilation error
The error you encountered is common on Windows when trying to install numpy 1.24.3, which requires compilation. The solution is to use pre-compiled wheels.

## Solution Options

### Option 1: Simple Installation (Recommended)
Use the simplified version that avoids heavy ML libraries:

```bash
# Run the simple installation script
install_simple.bat
```

This will install only the essential packages with Windows-compatible versions.

### Option 2: Full Installation with Updated Versions
Use the updated installation script with compatible versions:

```bash
# Run the updated installation script
install_windows.bat
```

### Option 3: Manual Installation
If the scripts don't work, install manually:

```bash
# 1. Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# 2. Install core dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 redis==5.0.1 python-dotenv==1.0.0 pydantic==2.5.0 jinja2==3.1.2 python-multipart==0.0.6

# 3. Install AI libraries
pip install openai==1.3.7 langchain==0.0.350 langchain-openai==0.0.2

# 4. Install Windows-compatible data libraries
pip install numpy==1.26.4 pandas==2.1.4

# 5. Install ML libraries (optional)
pip install scikit-learn==1.3.2 transformers==4.35.2
```

## Key Changes Made

1. **Updated numpy**: Changed from 1.24.3 to 1.26.4 (has pre-compiled wheels for Windows)
2. **Updated pandas**: Changed from 2.0.3 to 2.1.4 (better Windows compatibility)
3. **Created simple_requirements.txt**: Minimal requirements without heavy ML libraries
4. **Updated installation scripts**: Use compatible versions and better error handling

## Running the Application

### Simple Version (Recommended for Windows)
```bash
python main_simple.py
```

### Full Version (if all dependencies install successfully)
```bash
python main.py
```

## Redis Setup

You'll need Redis running. Options:

1. **Docker** (Recommended):
   ```bash
   docker run -d -p 6379:6379 redis
   ```

2. **Windows Subsystem for Linux (WSL)**:
   ```bash
   sudo apt-get update
   sudo apt-get install redis-server
   sudo service redis-server start
   ```

3. **Windows Redis** (Download from https://github.com/microsoftarchive/redis/releases)

## Environment Setup

1. Create a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Get an OpenAI API key from https://platform.openai.com/

## Troubleshooting

### If you still get compilation errors:
1. Try installing Microsoft Visual C++ Build Tools
2. Use the simple installation option
3. Consider using WSL2 for development

### If Redis connection fails:
1. Make sure Redis is running on port 6379
2. Check if firewall is blocking the connection
3. Try using Docker for Redis

## Features Available

### Simple Version:
- ✅ Chat interface
- ✅ Message storage
- ✅ Basic summarization
- ✅ Web interface
- ✅ Session management

### Full Version (if ML libraries install):
- ✅ All simple features
- ✅ Sentiment analysis
- ✅ Topic classification
- ✅ Advanced ML-based features

## Next Steps

1. Run the simple installation: `install_simple.bat`
2. Set up your OpenAI API key in `.env`
3. Start Redis
4. Run: `python main_simple.py`
5. Open http://localhost:8000 in your browser

The application will work with the simple version even if the heavy ML libraries fail to install! 