# Dockerfile for ChatSummerizer (FastAPI + optional Redis)
# Works for Linux and Windows (Docker Desktop uses Linux containers by default)

FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# For Windows users: if you use requirements_windows.txt, uncomment below
# COPY requirements_windows.txt ./
# RUN pip install --no-cache-dir -r requirements_windows.txt

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Set environment variables (can be overridden by docker-compose or .env)
ENV PYTHONUNBUFFERED=1

# Entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 