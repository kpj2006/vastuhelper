"""
AI Floor Plan Compliance Checker - FastAPI Backend

Main application entry point that configures the FastAPI app,
sets up CORS, includes routers, and defines the API structure.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routers for different API endpoints
from app.routers import analysis, upload

# Create FastAPI application instance
app = FastAPI(
    title="AI Floor Plan Compliance Checker API",
    description="Backend API for analyzing floor plans for building code compliance, Vastu Shastra rules, and sunlight optimization",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc documentation at /redoc
)

# Configure CORS (Cross-Origin Resource Sharing) for frontend integration
# This allows the React frontend to make requests to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://localhost:3001",  # Alternative port for React
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers with prefixes for organization
app.include_router(analysis.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

# Root endpoint for health check and basic info
@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information.
    Useful for health checks and API discovery.
    """
    return {
        "message": "AI Floor Plan Compliance Checker API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "analysis": "/api/analyze",
            "upload": "/api/upload"
        }
    }

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment.
    Returns the current status of the API.
    """
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }

# Global exception handler for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler to provide consistent error responses
    across the entire API.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# Run the application when this file is executed directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Accept connections from any IP
        port=8000,       # Default port for the API
        reload=True      # Auto-reload on code changes (development only)
    )
