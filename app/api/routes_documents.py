"""
Document upload and retrieval API routes.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.database import get_db
from app.db.models import Document
from app.schemas.documents import DocumentUploadResponse, DocumentMetadata
from app.services.document_storage import document_storage
from app.services.audit_service import audit_service
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload an invoice, purchase order, or delivery receipt PDF.
    
    Args:
        file: PDF file to upload
        document_type: One of 'invoice', 'purchase_order', 'delivery_receipt'
        
    Returns:
        Document metadata including ID and SHA-256 hash
    """
    # Validate document type
    valid_types = {"invoice", "purchase_order", "delivery_receipt"}
    if document_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF files are allowed."
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read uploaded file: {str(e)}"
        )
    
    # Validate file size
    file_size = len(file_content)
    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )
    
    # Save document and calculate hash
    try:
        doc_id, storage_path, sha256_hash = document_storage.save_document(
            file_content,
            file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document: {str(e)}"
        )
    
    # Create database record
    db_document = Document(
        id=doc_id,
        filename=file.filename,
        document_type=document_type,
        file_path=storage_path,
        file_size=file_size,
        sha256_hash=sha256_hash
    )
    
    try:
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Record audit event
        audit_service.record_event(
            event_type="document_uploaded",
            entity_id=db_document.id,
            entity_type="document",
            event_data={
                "filename": db_document.filename,
                "document_type": db_document.document_type,
                "file_size": db_document.file_size,
                "sha256_hash": db_document.sha256_hash
            },
            actor="user",
            db=db
        )
        
    except Exception as e:
        # Clean up file if database insert fails
        try:
            Path(storage_path).unlink(missing_ok=True)
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document metadata: {str(e)}"
        )
    
    return DocumentUploadResponse(
        document_id=db_document.id,
        filename=db_document.filename,
        document_type=db_document.document_type,
        file_size=db_document.file_size,
        sha256_hash=db_document.sha256_hash,
        uploaded_at=db_document.uploaded_at
    )


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve document metadata by ID.
    
    Args:
        document_id: Unique document identifier
        
    Returns:
        Document metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    return DocumentMetadata.model_validate(document)
