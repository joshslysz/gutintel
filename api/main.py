"""
Main FastAPI application for GutIntel API.

This module sets up the FastAPI application with proper middleware, routing,
error handling, and lifecycle management.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from config import get_settings
from database import init_db, close_db, health_check
from models.responses import (
    BaseResponse, 
    HealthResponse, 
    ErrorDetail,
    InternalServerErrorResponse,
    ValidationErrorResponse
)
from routers import ingredients


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for proper resource management.
    """
    # Startup
    logger.info("Starting GutIntel API...")
    
    try:
        await init_db()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GutIntel API...")
    
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://gutintel.com/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {"url": "/", "description": "Current server"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    error_detail = ErrorDetail(
        code=f"HTTP_{exc.status_code}",
        message=exc.detail
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse.error_response([error_detail]).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with consistent error format."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred"
    )
    
    return JSONResponse(
        status_code=500,
        content=BaseResponse.error_response([error_detail]).dict()
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API and database health status",
    tags=["health"]
)
async def health_check_endpoint():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the current health status of the API and database connection.
    """
    try:
        # Check database health
        db_health = await health_check()
        
        # Determine overall health status
        is_healthy = db_health.get("database") == "connected"
        
        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            database=db_health.get("database", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database="error"
        )


# API version 1 routes
@app.get("/", summary="Root endpoint", tags=["root"])
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Welcome to GutIntel API",
        "version": settings.api_version,
        "docs_url": "/docs",
        "health_url": "/health"
    }


# Include routers
app.include_router(
    ingredients.router,
    prefix="/api/v1"
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests for monitoring."""
    # Log request
    logger.info(f"{request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.info(f"Response status: {response.status_code}")
    
    return response


# Add request size limitation
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request size to prevent abuse."""
    content_length = request.headers.get("content-length")
    
    if content_length:
        content_length = int(content_length)
        if content_length > settings.max_request_size:
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "errors": [
                        {
                            "code": "REQUEST_TOO_LARGE",
                            "message": f"Request size {content_length} exceeds maximum {settings.max_request_size} bytes"
                        }
                    ]
                }
            )
    
    return await call_next(request)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
