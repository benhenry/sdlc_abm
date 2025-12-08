"""SDLC SimLab FastAPI Application

Main application entry point with CORS, error handling, and route registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .database import init_db
from .routes import scenarios, templates, simulations, comparisons
from . import websockets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup: Initialize database
    # NOTE: Using Alembic migrations instead of init_db()
    # Run: docker compose exec api alembic upgrade head
    # print("Initializing database...")
    # await init_db()
    # print("Database initialized successfully")

    yield

    # Shutdown: cleanup if needed
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="SDLC SimLab API",
    description="REST API for SDLC agent-based simulation engine",
    version=__version__,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        }
    )


# Include routers
app.include_router(scenarios.router)
app.include_router(templates.router)
app.include_router(simulations.router)
app.include_router(comparisons.router)
app.include_router(websockets.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": __version__,
        "service": "sdlc-simlab-api"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SDLC SimLab API",
        "version": __version__,
        "docs": "/api/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
