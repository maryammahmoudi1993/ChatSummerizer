# Chat Summarizer

A FastAPI service that stores chat sessions, tags each message with sentiment and topic, and produces summaries (OpenAI when a key is configured, an offline extractive fallback otherwise).

<img width="1898" height="874" alt="Screenshot" src="https://github.com/user-attachments/assets/89f3c387-dbbe-4b9e-b98d-b6d603bdc8c8" />

## Features

- **Chat storage** with sessions: in-memory (default) or Redis
- **Sentiment analysis** and **topic classification** (rule-based, no ML downloads)
- **Summaries**: full, brief and structured; OpenAI via `OPENAI_API_KEY`, extractive fallback if unset or failing
- **Web UI** at `/` and interactive API docs at `/docs`
- Input validation (length limits, batch caps) and env-driven CORS

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py            # http://127.0.0.1:8000
```

Docker (app + Redis): `docker compose up --build`

## Configuration

See [.env.example](.env.example).

| Variable | Default | Purpose |
|----------|---------|---------|
| `STORAGE_BACKEND` | `memory` | `memory` or `redis` |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `localhost` / `6379` / `0` | Redis connection |
| `OPENAI_API_KEY` | unset | Enables LLM summaries |
| `CORS_ORIGINS` | `http://localhost:8000` | Comma-separated allowed origins |
| `HOST` / `PORT` / `DEBUG` | `127.0.0.1` / `8000` / `false` | Server (`DEBUG=true` enables reload) |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat/send` | Form: `session_id`, `role` (`user`/`assistant`), `content` |
| GET | `/chat/session/{id}` | Messages of a session |
| GET | `/chat/sessions` | List sessions |
| DELETE | `/chat/session/{id}` | Delete a session (404 if unknown) |
| POST | `/summary/generate` | JSON: `session_id`, `max_length` (20-2000 words) |
| GET | `/summary/brief/{id}`, `/summary/structured/{id}` | Other summary styles |
| POST | `/sentiment/analyze`, `/topic/classify` | JSON: `text` |
| POST | `/sentiment/batch`, `/topic/batch` | JSON array of up to 100 texts |
| GET | `/stats/session/{id}`, `/stats/overview` | Statistics |
| GET | `/health` | Component health |

## Project layout

```
chat_summarizer/   config, models, storage, sentiment, classifier, summarizer, api (app factory)
main.py            uvicorn entrypoint
templates/ static/ web UI
tests/             pytest suite
scripts/score.py   repo quality score
```

## Testing

```bash
pip install -r requirements-dev.txt
ruff check .
pytest --cov=chat_summarizer
python scripts/score.py      # rubric-based quality score, target >= 90
```

CI (GitHub Actions) runs lint and tests on Python 3.10-3.12. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
