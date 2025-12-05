from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, memory, emotion, persona

# Initialize FastAPI app
app = FastAPI(
    title="AI Companion API",
    description="Memory-enhanced personality AI companion backend",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # All Vercel deployments
    allow_origins=[
        "http://localhost:5173",  # Local development
        # Add your custom domain here when ready:
        # "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(memory.router, prefix="/api", tags=["Memory"])
app.include_router(emotion.router, prefix="/api", tags=["Emotion"])
app.include_router(persona.router, prefix="/api", tags=["Persona"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Companion API"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Companion API",
        "docs": "/docs",
        "health": "/health",
    }
