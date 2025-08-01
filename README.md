# Chat Summarizer System

A comprehensive chat summarization system built with FastAPI, LangChain, OpenAI, Redis, and HuggingFace transformers. This system provides advanced chat analysis capabilities including sentiment analysis, topic classification, and AI-powered summarization.
<img width="1898" height="874" alt="Screenshot 2025-08-01 102040" src="https://github.com/user-attachments/assets/89f3c387-dbbe-4b9e-b98d-b6d603bdc8c8" />


## 🚀 Features

### Core Features
- **Chat Storage**: Store chat messages with session management using Redis
- **AI Summarization**: Generate comprehensive summaries using OpenAI via LangChain
- **Sentiment Analysis**: Analyze message sentiment using HuggingFace transformers
- **Topic Classification**: Classify messages into categories using zero-shot classification
- **Web Interface**: Modern, responsive web UI for chat interaction and analysis

### Extended Features
- **Real-time Analysis**: Automatic sentiment and topic analysis for each message
- **Session Management**: Create, view, and delete chat sessions
- **Statistics Dashboard**: View session statistics and analytics
- **Multiple Summary Types**: Brief, comprehensive, and structured summaries
- **Batch Processing**: Analyze multiple texts for sentiment and topic classification

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: HTML + Jinja2 + CSS + JavaScript
- **LLM**: OpenAI (via LangChain)
- **Storage**: Redis
- **NLP**: HuggingFace Transformers
- **Styling**: Modern CSS with responsive design

## 📋 Prerequisites

- Python 3.8+
- Redis server
- OpenAI API key
- Internet connection (for model downloads)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChatSummerizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Redis Configuration
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   
   # FastAPI Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True
   ```

5. **Start Redis server**
   ```bash
   # On Windows (if using WSL or Docker)
   # On Linux/Mac
   redis-server
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
chat_summarizer/
├── main.py                 # FastAPI application
├── models.py              # Pydantic models
├── redis_client.py        # Redis client for data storage
├── summarizer.py          # LangChain summarization
├── sentiment.py           # Sentiment analysis
├── classifier.py          # Topic classification
├── templates/
│   └── index.html        # Main web interface
├── static/
│   └── style.css         # Styling
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables template
└── README.md            # This file
```

## 🎯 Usage

### Web Interface

1. **Access the application**: Open `http://localhost:8000` in your browser
2. **Create a session**: Click "New Session" to start a new chat
3. **Send messages**: Type messages and select role (User/Assistant)
4. **View analysis**: Each message is automatically analyzed for sentiment and topic
5. **Generate summaries**: Use the analysis panel to generate summaries
6. **View statistics**: Get detailed session statistics

### API Endpoints

#### Chat Management
- `POST /chat/send` - Send a chat message
- `GET /chat/session/{session_id}` - Get session messages
- `GET /chat/sessions` - List all sessions
- `DELETE /chat/session/{session_id}` - Delete a session

#### Summarization
- `POST /summary/generate` - Generate comprehensive summary
- `GET /summary/brief/{session_id}` - Get brief summary
- `GET /summary/structured/{session_id}` - Get structured summary

#### Analysis
- `POST /sentiment/analyze` - Analyze text sentiment
- `POST /sentiment/batch` - Batch sentiment analysis
- `POST /topic/classify` - Classify text topic
- `POST /topic/batch` - Batch topic classification

#### Statistics
- `GET /stats/session/{session_id}` - Get session statistics
- `GET /stats/overview` - Get overview statistics
- `GET /health` - Health check

### Example API Usage

```python
import requests

# Send a message
response = requests.post('http://localhost:8000/chat/send', data={
    'session_id': 'session_123',
    'role': 'user',
    'content': 'Hello, how are you?'
})

# Generate summary
response = requests.post('http://localhost:8000/summary/generate', json={
    'session_id': 'session_123',
    'max_length': 500
})

# Analyze sentiment
response = requests.post('http://localhost:8000/sentiment/analyze', json={
    'text': 'I love this product!',
    'session_id': 'session_123'
})
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `REDIS_HOST` | Redis server host | localhost |
| `REDIS_PORT` | Redis server port | 6379 |
| `REDIS_DB` | Redis database number | 0 |
| `HOST` | FastAPI host | 0.0.0.0 |
| `PORT` | FastAPI port | 8000 |
| `DEBUG` | Debug mode | True |

### Model Configuration

The system uses the following pre-trained models:
- **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment`
- **Topic Classification**: `facebook/bart-large-mnli`
- **Summarization**: OpenAI GPT models via LangChain

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8000
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run**
   ```bash
   docker build -t chat-summarizer .
   docker run -p 8000:8000 chat-summarizer
   ```

### Production Deployment

1. **Use a production ASGI server**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set up reverse proxy (nginx)**
3. **Configure SSL certificates**
4. **Set up monitoring and logging**

## 🐳 Dockerized Deployment

### Quick Start (Linux/macOS/Windows with Docker Desktop)

1. **Set your OpenAI API key**
   - Create a `.env` file in the project root:
     ```env
     OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```
   This will start both the FastAPI app and Redis. The app will be available at [http://localhost:8000](http://localhost:8000).

3. **Live code reload**
   - By default, the app service mounts your code for live reload (`volumes: - .:/app`).
   - **Windows users:** If you have issues with file syncing or permissions, try changing the volume line in `docker-compose.yml` to:
     ```yaml
     # - .:/app:delegated
     ```
   - Or, comment out the volume for production builds.

### Using In-Memory Storage (No Redis)
- For local development or testing, you can use the in-memory storage by switching the import in `main.py` and `summarizer.py` to `MemoryClient` (already set up in this repo for fallback).
- If you want to run without Redis in Docker, comment out the `redis` service and related environment variables in `docker-compose.yml`.

### Customizing for Windows
- Docker Desktop for Windows uses Linux containers by default, so the provided Dockerfile and compose setup will work.
- If you want to use Windows containers, you may need to adapt the Dockerfile to use a Windows base image and install dependencies accordingly (not recommended for most users).

### Troubleshooting
- **Redis connection errors:** Ensure the Redis service is running (see `docker-compose logs redis`).
- **Volume mount issues on Windows:** Try using `:delegated` or restart Docker Desktop.
- **OpenAI API key errors:** Make sure your `.env` file is present and correct, or set the variable in your shell before running Docker Compose.

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running
   - Check Redis host and port configuration

2. **OpenAI API Error**
   - Verify API key is correct
   - Check API key has sufficient credits

3. **Model Loading Issues**
   - Ensure internet connection for model downloads
   - Check available disk space

4. **Memory Issues**
   - Reduce batch sizes for large datasets
   - Use smaller models for resource-constrained environments

### Performance Optimization

1. **Redis Optimization**
   - Configure Redis persistence
   - Set appropriate memory limits

2. **Model Optimization**
   - Use smaller models for faster inference
   - Implement model caching

3. **API Optimization**
   - Implement request rate limiting
   - Add response caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [LangChain](https://langchain.com/) for LLM integration
- [HuggingFace](https://huggingface.co/) for NLP models
- [OpenAI](https://openai.com/) for language models
- [Redis](https://redis.io/) for data storage

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health` 
