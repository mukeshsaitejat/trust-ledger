"""
Pydantic schemas for document API requests and responses.
These define the data contracts between frontend and backend.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class DocumentUploadResponse(BaseModel):
    """Response after successfully uploading a document."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    sha256_hash: str = Field(..., description="SHA-256 hash of file content")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True


class DocumentMetadata(BaseModel):
    """Document metadata for retrieval."""
    id: str
    filename: str
    document_type: str
    file_size: int
    sha256_hash: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    timestamp: datetime
