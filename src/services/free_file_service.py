"""
Free Local File Service (replaces paid MinIO/S3)
Stores files locally on filesystem - completely free
"""
import os
import shutil
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class FreeFileService:
    """
    Free local file storage service
    Replaces expensive cloud storage with local filesystem
    """
    
    def __init__(self, base_path: str = "./storage"):
        """Initialize with local storage path"""
        self.base_path = Path(base_path)
        self.uploads_path = self.base_path / "uploads"
        self.resumes_path = self.base_path / "resumes" 
        self.documents_path = self.base_path / "documents"
        
        # Create directories
        for path in [self.uploads_path, self.resumes_path, self.documents_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized free local file storage at: {self.base_path}")
    
    async def save_resume(self, file_data: bytes, filename: str, candidate_id: str) -> Dict[str, Any]:
        """Save resume file locally"""
        try:
            # Generate unique filename
            file_ext = Path(filename).suffix
            unique_filename = f"{candidate_id}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = self.resumes_path / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Return file info
            return {
                "file_id": unique_filename,
                "original_filename": filename,
                "file_path": str(file_path),
                "file_size": len(file_data),
                "content_type": self._get_content_type(filename),
                "created_at": datetime.now().isoformat(),
                "storage_type": "local_free"
            }
            
        except Exception as e:
            logger.error(f"Failed to save resume: {e}")
            raise Exception(f"File save failed: {e}")
    
    async def save_document(self, file_data: bytes, filename: str, document_type: str = "general") -> Dict[str, Any]:
        """Save document file locally"""
        try:
            # Generate unique filename
            file_ext = Path(filename).suffix
            unique_filename = f"{document_type}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = self.documents_path / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            return {
                "file_id": unique_filename,
                "original_filename": filename,
                "file_path": str(file_path),
                "file_size": len(file_data),
                "document_type": document_type,
                "content_type": self._get_content_type(filename),
                "created_at": datetime.now().isoformat(),
                "storage_type": "local_free"
            }
            
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise Exception(f"Document save failed: {e}")
    
    async def get_file(self, file_id: str, file_type: str = "resume") -> Optional[bytes]:
        """Retrieve file from local storage"""
        try:
            if file_type == "resume":
                file_path = self.resumes_path / file_id
            else:
                file_path = self.documents_path / file_id
            
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
                
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {e}")
            return None
    
    async def delete_file(self, file_id: str, file_type: str = "resume") -> bool:
        """Delete file from local storage"""
        try:
            if file_type == "resume":
                file_path = self.resumes_path / file_id
            else:
                file_path = self.documents_path / file_id
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    async def list_files(self, file_type: str = "resume", limit: int = 100) -> List[Dict[str, Any]]:
        """List files in storage"""
        try:
            if file_type == "resume":
                search_path = self.resumes_path
            else:
                search_path = self.documents_path
            
            files = []
            for file_path in search_path.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "file_id": file_path.name,
                        "file_size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "file_type": file_type
                    })
            
            # Sort by creation time, newest first
            files.sort(key=lambda x: x["created_at"], reverse=True)
            return files[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            stats = {
                "total_files": 0,
                "total_size_bytes": 0,
                "resumes_count": 0,
                "documents_count": 0,
                "resumes_size": 0,
                "documents_size": 0,
                "storage_type": "local_free",
                "base_path": str(self.base_path)
            }
            
            # Count resumes
            for file_path in self.resumes_path.iterdir():
                if file_path.is_file():
                    stats["resumes_count"] += 1
                    stats["resumes_size"] += file_path.stat().st_size
            
            # Count documents  
            for file_path in self.documents_path.iterdir():
                if file_path.is_file():
                    stats["documents_count"] += 1
                    stats["documents_size"] += file_path.stat().st_size
            
            stats["total_files"] = stats["resumes_count"] + stats["documents_count"]
            stats["total_size_bytes"] = stats["resumes_size"] + stats["documents_size"]
            stats["total_size_mb"] = round(stats["total_size_bytes"] / 1024 / 1024, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword', 
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    async def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_files = []
            
            for path in [self.resumes_path, self.documents_path]:
                for file_path in path.iterdir():
                    if file_path.is_file() and file_path.stat().st_ctime < cutoff_time:
                        file_path.unlink()
                        deleted_files.append(str(file_path))
            
            return {
                "deleted_count": len(deleted_files),
                "deleted_files": deleted_files,
                "cutoff_days": days_old
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
            return {"error": str(e)}


# Global service instance
file_service = FreeFileService()