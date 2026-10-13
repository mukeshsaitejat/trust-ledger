"""
Document storage service.
Handles file uploads, hash calculation, and filesystem operations.
"""
import hashlib
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class DocumentStorageService:
    """Manages document storage and hash calculation."""
    
    def __init__(self):
        self.storage_dir = settings.upload_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_sha256(self, file_content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            file_content: File bytes
            
        Returns:
            Hex string of SHA-256 hash
        """
        return hashlib.sha256(file_content).hexdigest()
    
    def generate_unique_filename(self, original_filename: str) -> tuple[str, str]:
        """
        Generate a unique filename to prevent collisions.
        
        Args:
            original_filename: Original uploaded filename
            
        Returns:
            Tuple of (document_id, storage_filename)
        """
        # Generate UUID for document ID
        doc_id = str(uuid.uuid4())
        
        # Extract extension safely
        extension = Path(original_filename).suffix.lower()
        
        # Create storage filename: {uuid}{extension}
        storage_filename = f"{doc_id}{extension}"
        
        return doc_id, storage_filename
    
    def save_document(
        self,
        file_content: bytes,
        original_filename: str
    ) -> tuple[str, str, str]:
        """
        Save document to filesystem.
        
        Args:
            file_content: File bytes to save
            original_filename: Original filename from upload
            
        Returns:
            Tuple of (document_id, storage_path, sha256_hash)
        """
        # Generate unique ID and filename
        doc_id, storage_filename = self.generate_unique_filename(original_filename)
        
        # Calculate hash before saving
        sha256_hash = self.calculate_sha256(file_content)
        
        # Full path for storage
        file_path = self.storage_dir / storage_filename
        
        # Write file
        file_path.write_bytes(file_content)
        
        return doc_id, str(file_path), sha256_hash
    
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify a stored file hasn't been modified.
        
        Args:
            file_path: Path to stored file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches, False otherwise
        """
        path = Path(file_path)
        if not path.exists():
            return False
        
        current_hash = self.calculate_sha256(path.read_bytes())
        return current_hash == expected_hash


# Global service instance
document_storage = DocumentStorageService()
