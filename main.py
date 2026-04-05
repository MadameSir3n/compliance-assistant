"""
Compliance Assistant
Entry point: starts the FastAPI risk assessment API.

Usage:
    pip install -r requirements.txt
    cp .env.example .env  # add your OPENAI_API_KEY
    python main.py

    Or with Docker:
    docker-compose up
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
