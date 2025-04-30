"""
FastAPI application entry point for the Property Investment Analysis Application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Investment Agent API",
    description="API for Property Investment Analysis Application",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API router
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("API starting up")
    # Any additional startup initialization can be added here

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("API shutting down")
    # Any cleanup code can be added here