"""
InvoiceShield FastAPI Application
Main entry point for the invoice financing verification platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.core.config import settings
from app.db.database import init_db
from app.api import routes_documents, routes_invoices, routes_audit, routes_system
from app.schemas.documents import HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Assisted Invoice Financing Verification Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application start."""
    init_db()

# Include routers
app.include_router(routes_documents.router)
app.include_router(routes_invoices.router)
app.include_router(routes_audit.router)
app.include_router(routes_system.router)


@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to InvoiceShield API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns application status and version information.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )
