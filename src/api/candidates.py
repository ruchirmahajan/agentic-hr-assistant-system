"""
Candidate API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid
import logging

from ..core.database import get_db
from ..core.security import security_utils
from ..core.exceptions import unauthorized_exception, not_found_exception
from ..models.candidate import Candidate
from ..models.user import User
from ..services.file_service import file_service
from ..services.claude_service import claude_service
from ..services.gdpr_service import gdpr_service
from .auth.dependencies import get_current_user, require_permission

logger = logging.getLogger(__name__)

candidates_router = APIRouter()


@candidates_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_candidate(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    experience_years: Optional[int] = Form(None),
    current_position: Optional[str] = Form(None),
    current_company: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    resume_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate with resume upload"""
    try:
        # Check permissions
        if not current_user.has_permission("edit_candidates"):
            raise unauthorized_exception("Permission denied")
        
        # Create candidate record
        candidate = Candidate(
            full_name=full_name,
            email=email,
            phone=phone,
            experience_years=experience_years,
            current_position=current_position,
            current_company=current_company,
            source=source,
            created_by=current_user.id
        )
        
        db.add(candidate)
        await db.flush()  # Get the candidate ID
        
        # Process resume upload
        resume_data = await file_service.process_resume_upload(
            resume_file,
            str(candidate.id),
            str(current_user.id)
        )
        
        # Extract skills from resume
        skills = await claude_service.extract_skills_from_resume(
            resume_data['text_content']
        )
        
        candidate.skills = skills
        candidate.skills_extracted = skills
        
        await db.commit()
        
        # Record GDPR consent (default consents)
        await gdpr_service.record_consent(
            str(candidate.id),
            {
                "data_processing": True,
                "resume_analysis": True,
                "communication": True,
                "data_retention": True
            }
        )
        
        return {
            "id": str(candidate.id),
            "message": "Candidate created successfully",
            "resume_processed": True,
            "skills_extracted": len(skills)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create candidate: {str(e)}"
        )


@candidates_router.get("/")
async def list_candidates(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List candidates with optional search"""
    try:
        # Check permissions
        if not current_user.has_permission("view_candidates"):
            raise unauthorized_exception("Permission denied")
        
        # Build query
        query = select(Candidate)
        
        if search:
            # Search in non-PII fields only for privacy
            query = query.where(
                (Candidate.current_position.ilike(f"%{search}%")) |
                (Candidate.current_company.ilike(f"%{search}%")) |
                (Candidate.source.ilike(f"%{search}%"))
            )
        
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        # Return candidates without PII unless user has permission
        include_pii = current_user.has_permission("view_pii")
        
        return {
            "candidates": [
                candidate.to_dict(include_pii=include_pii) 
                for candidate in candidates
            ],
            "total": len(candidates),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve candidates"
        )


@candidates_router.get("/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate details"""
    try:
        # Check permissions
        if not current_user.has_permission("view_candidates"):
            raise unauthorized_exception("Permission denied")
        
        # Get candidate
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise not_found_exception("Candidate not found")
        
        # Return candidate data
        include_pii = current_user.has_permission("view_pii")
        return candidate.to_dict(include_pii=include_pii)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve candidate"
        )


@candidates_router.put("/{candidate_id}")
async def update_candidate(
    candidate_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update candidate information"""
    try:
        # Check permissions
        if not current_user.has_permission("edit_candidates"):
            raise unauthorized_exception("Permission denied")
        
        # Get candidate
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise not_found_exception("Candidate not found")
        
        # Update allowed fields
        updateable_fields = [
            'experience_years', 'current_position', 'current_company',
            'skills', 'education', 'source', 'notes'
        ]
        
        for field, value in update_data.items():
            if field in updateable_fields and hasattr(candidate, field):
                setattr(candidate, field, value)
        
        # Update PII fields with proper encryption
        if 'full_name' in update_data:
            candidate.full_name = update_data['full_name']
        if 'email' in update_data:
            candidate.email = update_data['email']
        if 'phone' in update_data:
            candidate.phone = update_data['phone']
        
        await db.commit()
        
        return {"message": "Candidate updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update candidate"
        )


@candidates_router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete candidate (GDPR compliant)"""
    try:
        # Check permissions
        if not current_user.has_permission("delete_candidates"):
            raise unauthorized_exception("Permission denied")
        
        # Use GDPR service for compliant deletion
        success = await gdpr_service.delete_candidate_data(
            candidate_id,
            str(current_user.id),
            "admin_deletion"
        )
        
        if success:
            return {"message": "Candidate deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete candidate"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete candidate"
        )


@candidates_router.post("/{candidate_id}/documents")
async def upload_document(
    candidate_id: str,
    document_type: str = Form(...),
    document_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload additional document for candidate"""
    try:
        # Check permissions and candidate exists
        if not current_user.has_permission("edit_candidates"):
            raise unauthorized_exception("Permission denied")
        
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise not_found_exception("Candidate not found")
        
        # Process document upload
        document_data = await file_service.process_document_upload(
            document_file,
            candidate_id,
            document_type,
            str(current_user.id)
        )
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document_data['file_id'],
            "document_type": document_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@candidates_router.get("/{candidate_id}/export")
async def export_candidate_data(
    candidate_id: str,
    include_files: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export candidate data for GDPR compliance"""
    try:
        # Check permissions
        if not current_user.has_permission("export_data"):
            raise unauthorized_exception("Permission denied")
        
        # Export data using GDPR service
        export_data = await gdpr_service.export_candidate_data(
            candidate_id,
            str(current_user.id),
            include_files
        )
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting candidate data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data"
        )