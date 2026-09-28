"""Entrypoint: `uvicorn main:app` or `python main.py`."""
import logging
import os

from chat_summarizer.api import create_app

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = create_app()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
