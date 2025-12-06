"""
Document Storage Service
Handles secure file upload, storage, retrieval, and management
"""
import os
import hashlib
import uuid
import shutil
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class DocumentStorageService:
    """Secure document storage service with file integrity and access control"""
    
    # Allowed MIME types for security
    ALLOWED_MIME_TYPES = {
        # Documents
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/plain': '.txt',
        'application/rtf': '.rtf',
        
        # Images (for ID documents, photos)
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        
        # Spreadsheets (for salary slips, etc.)
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'text/csv': '.csv',
    }
    
    # Maximum file sizes by type (in bytes)
    MAX_FILE_SIZES = {
        'resume': 10 * 1024 * 1024,          # 10MB
        'cover_letter': 5 * 1024 * 1024,      # 5MB
        'identity_proof': 10 * 1024 * 1024,   # 10MB
        'address_proof': 10 * 1024 * 1024,    # 10MB
        'education_certificate': 15 * 1024 * 1024,  # 15MB
        'marksheet': 15 * 1024 * 1024,        # 15MB
        'degree_certificate': 15 * 1024 * 1024,  # 15MB
        'experience_letter': 10 * 1024 * 1024,  # 10MB
        'relieving_letter': 10 * 1024 * 1024,  # 10MB
        'salary_slip': 5 * 1024 * 1024,       # 5MB
        'offer_letter': 10 * 1024 * 1024,     # 10MB
        'portfolio': 50 * 1024 * 1024,        # 50MB
        'certification': 10 * 1024 * 1024,    # 10MB
        'reference_letter': 5 * 1024 * 1024,  # 5MB
        'background_check': 10 * 1024 * 1024, # 10MB
        'medical_certificate': 10 * 1024 * 1024,  # 10MB
        'other': 10 * 1024 * 1024,            # 10MB default
    }
    
    def __init__(self, base_storage_path: str = None):
        """Initialize the document storage service"""
        self.base_path = Path(base_storage_path or settings.STORAGE_PATH)
        self.upload_path = Path(settings.UPLOAD_PATH)
        
        # Create storage directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary storage directories"""
        directories = [
            self.base_path,
            self.base_path / "candidates",
            self.base_path / "temp",
            self.upload_path,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    def _get_candidate_folder(self, candidate_id: str) -> Path:
        """Get or create the storage folder for a candidate"""
        folder = self.base_path / "candidates" / candidate_id
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    def _generate_secure_filename(self, original_filename: str, document_type: str) -> str:
        """Generate a secure, unique filename"""
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        
        # Generate UUID-based filename
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        return f"{document_type}_{timestamp}_{unique_id}{ext}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum for file integrity"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _calculate_checksum_from_content(self, content: bytes) -> str:
        """Calculate SHA-256 checksum from file content"""
        return hashlib.sha256(content).hexdigest()
    
    def validate_file(
        self, 
        filename: str, 
        content: bytes, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Validate uploaded file for security and compliance
        Returns validation result with any errors
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "mime_type": None,
            "file_size": len(content),
            "extension": None
        }
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        result["mime_type"] = mime_type
        result["extension"] = Path(filename).suffix.lower()
        
        # Check MIME type
        if mime_type not in self.ALLOWED_MIME_TYPES:
            result["valid"] = False
            result["errors"].append(f"File type '{mime_type}' is not allowed. Allowed types: PDF, DOC, DOCX, TXT, JPG, PNG, XLS, XLSX")
        
        # Check file extension matches MIME type
        if mime_type and result["extension"] != self.ALLOWED_MIME_TYPES.get(mime_type, ""):
            # Allow .jpeg for image/jpeg
            if not (mime_type == "image/jpeg" and result["extension"] in [".jpg", ".jpeg"]):
                result["warnings"].append(f"File extension doesn't match content type")
        
        # Check file size
        max_size = self.MAX_FILE_SIZES.get(document_type, self.MAX_FILE_SIZES["other"])
        if len(content) > max_size:
            result["valid"] = False
            result["errors"].append(f"File size ({len(content) / (1024*1024):.1f}MB) exceeds maximum allowed ({max_size / (1024*1024):.1f}MB)")
        
        # Check for empty file
        if len(content) == 0:
            result["valid"] = False
            result["errors"].append("File is empty")
        
        # Basic content validation (check magic bytes for common types)
        if mime_type == "application/pdf" and not content.startswith(b"%PDF"):
            result["valid"] = False
            result["errors"].append("File content doesn't match PDF format")
        
        if mime_type == "image/jpeg" and not content.startswith(b"\xff\xd8\xff"):
            result["valid"] = False
            result["errors"].append("File content doesn't match JPEG format")
        
        if mime_type == "image/png" and not content.startswith(b"\x89PNG"):
            result["valid"] = False
            result["errors"].append("File content doesn't match PNG format")
        
        return result
    
    async def save_document(
        self,
        candidate_id: str,
        document_type: str,
        original_filename: str,
        content: bytes,
        uploaded_by: str = None
    ) -> Dict[str, Any]:
        """
        Save a document to storage
        Returns document metadata or raises exception
        """
        # Validate the file
        validation = self.validate_file(original_filename, content, document_type)
        if not validation["valid"]:
            raise ValueError(f"File validation failed: {', '.join(validation['errors'])}")
        
        # Get candidate folder
        candidate_folder = self._get_candidate_folder(candidate_id)
        
        # Generate secure filename
        secure_filename = self._generate_secure_filename(original_filename, document_type)
        
        # Full file path
        file_path = candidate_folder / secure_filename
        
        # Save the file
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Calculate checksum
            checksum = self._calculate_checksum_from_content(content)
            
            # Get relative path for storage
            relative_path = f"candidates/{candidate_id}/{secure_filename}"
            
            logger.info(f"Document saved: {relative_path} for candidate {candidate_id}")
            
            return {
                "stored_filename": secure_filename,
                "original_filename": original_filename,
                "file_path": relative_path,
                "file_size": len(content),
                "mime_type": validation["mime_type"],
                "file_extension": validation["extension"],
                "checksum": checksum,
                "warnings": validation["warnings"]
            }
            
        except Exception as e:
            logger.error(f"Failed to save document: {str(e)}")
            # Clean up if partial write
            if file_path.exists():
                file_path.unlink()
            raise
    
    async def get_document(
        self,
        file_path: str,
        verify_checksum: str = None
    ) -> bytes:
        """
        Retrieve a document from storage
        Optionally verify checksum for integrity
        """
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Security check - ensure path is within storage
        try:
            full_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise PermissionError("Invalid file path - access denied")
        
        with open(full_path, "rb") as f:
            content = f.read()
        
        # Verify checksum if provided
        if verify_checksum:
            actual_checksum = self._calculate_checksum_from_content(content)
            if actual_checksum != verify_checksum:
                logger.error(f"Checksum mismatch for {file_path}")
                raise ValueError("File integrity check failed - checksum mismatch")
        
        return content
    
    async def delete_document(self, file_path: str) -> bool:
        """
        Delete a document from storage
        Returns True if deleted, False if not found
        """
        full_path = self.base_path / file_path
        
        # Security check
        try:
            full_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise PermissionError("Invalid file path - access denied")
        
        if full_path.exists():
            full_path.unlink()
            logger.info(f"Document deleted: {file_path}")
            return True
        
        return False
    
    async def get_document_info(self, file_path: str) -> Dict[str, Any]:
        """Get document file information"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        stat = full_path.stat()
        
        return {
            "file_path": file_path,
            "file_size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "checksum": self._calculate_checksum(full_path)
        }
    
    async def copy_document(
        self,
        source_path: str,
        dest_candidate_id: str,
        new_document_type: str
    ) -> Dict[str, Any]:
        """Copy a document to another candidate or as a new version"""
        source_full = self.base_path / source_path
        
        if not source_full.exists():
            raise FileNotFoundError(f"Source document not found: {source_path}")
        
        # Read the source file
        with open(source_full, "rb") as f:
            content = f.read()
        
        # Save as new document
        original_filename = source_full.name
        return await self.save_document(
            candidate_id=dest_candidate_id,
            document_type=new_document_type,
            original_filename=original_filename,
            content=content
        )
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_size = 0
        file_count = 0
        candidate_count = 0
        
        candidates_path = self.base_path / "candidates"
        
        if candidates_path.exists():
            for candidate_folder in candidates_path.iterdir():
                if candidate_folder.is_dir():
                    candidate_count += 1
                    for file in candidate_folder.iterdir():
                        if file.is_file():
                            file_count += 1
                            total_size += file.stat().st_size
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": file_count,
            "total_candidates_with_documents": candidate_count
        }
    
    async def cleanup_orphaned_files(self, valid_file_paths: List[str]) -> int:
        """
        Clean up files that are not in the database
        Returns count of deleted files
        """
        deleted_count = 0
        candidates_path = self.base_path / "candidates"
        
        if not candidates_path.exists():
            return 0
        
        for candidate_folder in candidates_path.iterdir():
            if candidate_folder.is_dir():
                for file in candidate_folder.iterdir():
                    if file.is_file():
                        relative_path = f"candidates/{candidate_folder.name}/{file.name}"
                        if relative_path not in valid_file_paths:
                            file.unlink()
                            deleted_count += 1
                            logger.info(f"Cleaned up orphaned file: {relative_path}")
        
        return deleted_count


# Global instance
document_storage = DocumentStorageService()
