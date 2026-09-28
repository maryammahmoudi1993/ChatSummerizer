FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 HOST=0.0.0.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY chat_summarizer ./chat_summarizer
COPY templates ./templates
COPY static ./static
COPY main.py ./

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
