"""
Free File handling service with LOCAL storage - NO CLOUD COSTS
"""
import asyncio
import io
import logging
import hashlib
from typing import Optional, Dict, Any, List, BinaryIO
from pathlib import Path
from datetime import datetime
import uuid
import shutil
import os

import aiofiles
from fastapi import UploadFile, HTTPException, status

from ..core.config import settings
from ..core.security import security_utils
from ..core.exceptions import HRAssistantException

logger = logging.getLogger(__name__)


class FreeFileService:
    """Free local file storage service - NO CLOUD COSTS"""
    
    def __init__(self):
        # Use local storage paths
        self.base_path = Path("./storage")
        self.resumes_path = self.base_path / "resumes"
        self.documents_path = self.base_path / "documents"
        self.uploads_path = self.base_path / "uploads"
        
        # Create directories
        self._ensure_directories()
        logger.info("🆓 FREE File Service initialized - LOCAL STORAGE ONLY!")
    
    def _ensure_directories(self):
        """Ensure all storage directories exist"""
        for path in [self.base_path, self.resumes_path, self.documents_path, self.uploads_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def upload_resume(
        self,
        file: UploadFile,
        candidate_id: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Upload resume file to local storage"""
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type {file_ext} not allowed. Allowed: {allowed_extensions}"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{candidate_id}_{file_id}{file_ext}"
            file_path = self.resumes_path / filename
            
            # Read and save file
            content = await file.read()
            
            # Check file size (10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(content) > max_size:
                raise HTTPException(status_code=400, detail="File too large (max 10MB)")
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Extract text content
            text_content = await self._extract_text(file_path, file_ext)
            
            # Calculate file hash
            file_hash = hashlib.md5(content).hexdigest()
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type,
                "file_hash": file_hash,
                "text_content": text_content,
                "upload_time": datetime.utcnow(),
                "candidate_id": candidate_id
            }
            
        except Exception as e:
            logger.error(f"Resume upload error: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def get_file(self, file_id: str, candidate_id: str = None) -> Dict[str, Any]:
        """Get file information"""
        try:
            # Find file by searching in resumes directory
            for file_path in self.resumes_path.iterdir():
                if file_id in file_path.name:
                    if file_path.exists():
                        stat = file_path.stat()
                        return {
                            "file_id": file_id,
                            "filename": file_path.name,
                            "file_path": str(file_path),
                            "file_size": stat.st_size,
                            "modified_time": datetime.fromtimestamp(stat.st_mtime)
                        }
            
            raise HTTPException(status_code=404, detail="File not found")
            
        except Exception as e:
            logger.error(f"Get file error: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail="Failed to retrieve file")
    
    async def delete_file(self, file_id: str, candidate_id: str = None) -> bool:
        """Delete file from local storage"""
        try:
            # Find and delete file
            for file_path in self.resumes_path.iterdir():
                if file_id in file_path.name:
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"Deleted file: {file_path}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            return False
    
    async def _extract_text(self, file_path: Path, file_ext: str) -> str:
        """Extract text from file - simple extraction"""
        try:
            if file_ext == '.txt':
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return await f.read()
            
            elif file_ext == '.pdf':
                # Simple PDF text extraction
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\\n"
                        return text
                except ImportError:
                    logger.warning("PyPDF2 not available, returning filename as content")
                    return f"PDF file: {file_path.name}"
            
            elif file_ext in ['.doc', '.docx']:
                # Simple DOCX extraction
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\\n"
                    return text
                except ImportError:
                    logger.warning("python-docx not available, returning filename as content")
                    return f"Document file: {file_path.name}"
            
            else:
                return f"Unsupported file type: {file_ext}"
                
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return f"Text extraction failed for {file_path.name}"
    
    async def list_candidate_files(self, candidate_id: str) -> List[Dict[str, Any]]:
        """List all files for a candidate"""
        try:
            files = []
            
            for file_path in self.resumes_path.iterdir():
                if candidate_id in file_path.name:
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "file_size": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime),
                        "file_path": str(file_path)
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"List files error: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "storage_path": str(self.base_path),
                "free_storage": True
            }
            
        except Exception as e:
            logger.error(f"Storage stats error: {e}")
            return {"error": str(e)}


# Create service instance
file_service = FreeFileService()