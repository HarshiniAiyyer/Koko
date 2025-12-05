# Backend FastAPI Application

This directory contains the FastAPI backend for the AI Companion system.

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API routes
│   ├── core/                # Core AI logic (moved from root)
│   ├── models/              # Pydantic request/response models
│   └── config.py
├── requirements.txt
└── .env
```

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for Swagger API documentation.
