"""
GDPR compliance service for data protection and privacy
"""
import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from ..core.database import get_db
from ..core.config import settings
from ..core.security import audit_logger, security_utils
from ..core.exceptions import GDPRComplianceError
from ..models.candidate import Candidate
from ..models.user import User
from ..services.file_service import file_service

logger = logging.getLogger(__name__)


@dataclass
class ConsentRecord:
    """GDPR consent record"""
    consent_type: str
    granted: bool
    timestamp: datetime
    version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class DataExportRequest:
    """Data export request for GDPR compliance"""
    candidate_id: str
    requested_by: str
    request_date: datetime
    status: str  # pending, processing, completed, failed
    export_data: Optional[Dict[str, Any]] = None


class GDPRService:
    """Service for GDPR compliance operations"""
    
    def __init__(self):
        self.retention_years = settings.DATA_RETENTION_YEARS
        self.consent_required = settings.CONSENT_REQUIRED
    
    async def record_consent(
        self, 
        candidate_id: str, 
        consent_data: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Record GDPR consent for a candidate"""
        try:
            async with get_db() as db:
                # Get candidate
                result = await db.execute(
                    select(Candidate).where(Candidate.id == candidate_id)
                )
                candidate = result.scalar_one_or_none()
                
                if not candidate:
                    raise GDPRComplianceError("Candidate not found")
                
                # Update consent status
                consent_record = {
                    "data_processing": consent_data.get("data_processing", False),
                    "resume_analysis": consent_data.get("resume_analysis", False),
                    "communication": consent_data.get("communication", False),
                    "data_retention": consent_data.get("data_retention", False),
                    "analytics": consent_data.get("analytics", False),
                    "consent_date": datetime.utcnow().isoformat(),
                    "consent_version": "1.0",
                    "ip_address": ip_address,
                    "user_agent": user_agent
                }
                
                candidate.consent_status = consent_record
                candidate.updated_at = datetime.utcnow()
                
                # Calculate retention date if consent granted
                if consent_record["data_processing"]:
                    candidate.data_retention_date = (
                        datetime.utcnow().date() + 
                        timedelta(days=self.retention_years * 365)
                    )
                
                await db.commit()
                
                # Log consent record
                audit_logger.log_data_operation(
                    user_id="system",
                    operation="consent_recorded",
                    details={
                        "candidate_id": candidate_id,
                        "consent_data": consent_record,
                        "ip_address": ip_address
                    }
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            raise GDPRComplianceError(f"Failed to record consent: {str(e)}")
    
    async def withdraw_consent(
        self, 
        candidate_id: str, 
        consent_types: List[str],
        requested_by: str
    ) -> bool:
        """Withdraw specific types of consent"""
        try:
            async with get_db() as db:
                # Get candidate
                result = await db.execute(
                    select(Candidate).where(Candidate.id == candidate_id)
                )
                candidate = result.scalar_one_or_none()
                
                if not candidate:
                    raise GDPRComplianceError("Candidate not found")
                
                # Update consent status
                consent_status = candidate.consent_status.copy()
                for consent_type in consent_types:
                    if consent_type in consent_status:
                        consent_status[consent_type] = False
                
                consent_status["withdrawal_date"] = datetime.utcnow().isoformat()
                consent_status["withdrawn_by"] = requested_by
                
                candidate.consent_status = consent_status
                candidate.updated_at = datetime.utcnow()
                
                await db.commit()
                
                # Log consent withdrawal
                audit_logger.log_data_operation(
                    user_id=requested_by,
                    operation="consent_withdrawn",
                    details={
                        "candidate_id": candidate_id,
                        "consent_types": consent_types
                    }
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error withdrawing consent: {e}")
            raise GDPRComplianceError(f"Failed to withdraw consent: {str(e)}")
    
    async def export_candidate_data(
        self, 
        candidate_id: str, 
        requested_by: str,
        include_files: bool = False
    ) -> Dict[str, Any]:
        """Export all candidate data for GDPR data portability"""
        try:
            async with get_db() as db:
                # Get candidate with all related data
                result = await db.execute(
                    select(Candidate)
                    .where(Candidate.id == candidate_id)
                    .options(selectinload(Candidate.applications))
                )
                candidate = result.scalar_one_or_none()
                
                if not candidate:
                    raise GDPRComplianceError("Candidate not found")
                
                # Build export data
                export_data = {
                    "export_info": {
                        "export_date": datetime.utcnow().isoformat(),
                        "requested_by": requested_by,
                        "data_subject_id": candidate_id,
                        "format_version": "1.0"
                    },
                    "personal_information": {
                        "full_name": candidate.full_name,
                        "email": candidate.email,
                        "phone": candidate.phone,
                        "address": candidate.address,
                    },
                    "profile_data": {
                        "experience_years": candidate.experience_years,
                        "current_position": candidate.current_position,
                        "current_company": candidate.current_company,
                        "skills": candidate.skills,
                        "education": candidate.education,
                        "source": candidate.source,
                        "notes": candidate.notes,
                    },
                    "ai_analysis": candidate.ai_analysis,
                    "consent_status": candidate.consent_status,
                    "timestamps": {
                        "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                        "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None,
                    },
                    "applications": [],
                    "documents": []
                }
                
                # Add application data
                if hasattr(candidate, 'applications'):
                    for application in candidate.applications:
                        export_data["applications"].append({
                            "application_id": str(application.id),
                            "job_title": application.job.title if application.job else None,
                            "status": application.status,
                            "ai_score": application.ai_score,
                            "manual_score": application.manual_score,
                            "notes": application.notes,
                            "applied_at": application.applied_at.isoformat() if application.applied_at else None,
                        })
                
                # Add document information (metadata only unless include_files=True)
                if hasattr(candidate, 'documents'):
                    for doc in candidate.documents:
                        doc_info = {
                            "document_id": str(doc.id),
                            "document_type": doc.document_type,
                            "filename": security_utils.decrypt_pii(doc.encrypted_filename),
                            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                        }
                        
                        # Include file content if requested
                        if include_files:
                            try:
                                file_content = await file_service.get_file_content(
                                    doc.minio_bucket, 
                                    doc.minio_object_key
                                )
                                doc_info["file_content_base64"] = file_content.hex()
                            except Exception as e:
                                logger.error(f"Error retrieving file content: {e}")
                                doc_info["file_content_error"] = str(e)
                        
                        export_data["documents"].append(doc_info)
                
                # Log data export
                audit_logger.log_data_operation(
                    user_id=requested_by,
                    operation="data_export",
                    details={
                        "candidate_id": candidate_id,
                        "include_files": include_files,
                        "export_size": len(json.dumps(export_data))
                    }
                )
                
                return export_data
                
        except Exception as e:
            logger.error(f"Error exporting candidate data: {e}")
            raise GDPRComplianceError(f"Failed to export data: {str(e)}")
    
    async def delete_candidate_data(
        self, 
        candidate_id: str, 
        requested_by: str,
        reason: str = "right_to_erasure"
    ) -> bool:
        """Delete candidate data (right to be forgotten)"""
        try:
            async with get_db() as db:
                # Get candidate with all related data
                result = await db.execute(
                    select(Candidate)
                    .where(Candidate.id == candidate_id)
                    .options(selectinload(Candidate.documents))
                )
                candidate = result.scalar_one_or_none()
                
                if not candidate:
                    raise GDPRComplianceError("Candidate not found")
                
                # Delete associated files from MinIO
                if hasattr(candidate, 'documents'):
                    for doc in candidate.documents:
                        await file_service.delete_file(
                            doc.minio_bucket, 
                            doc.minio_object_key
                        )
                
                # Log deletion before performing it
                audit_logger.log_data_operation(
                    user_id=requested_by,
                    operation="candidate_deletion",
                    details={
                        "candidate_id": candidate_id,
                        "reason": reason,
                        "full_name": candidate.full_name,
                        "email": candidate.email
                    }
                )
                
                # Delete candidate record (this will cascade to related records)
                await db.execute(
                    delete(Candidate).where(Candidate.id == candidate_id)
                )
                
                await db.commit()
                
                logger.info(f"Candidate data deleted: {candidate_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting candidate data: {e}")
            raise GDPRComplianceError(f"Failed to delete data: {str(e)}")
    
    async def anonymize_candidate_data(
        self, 
        candidate_id: str, 
        requested_by: str
    ) -> bool:
        """Anonymize candidate data instead of full deletion"""
        try:
            async with get_db() as db:
                # Get candidate
                result = await db.execute(
                    select(Candidate).where(Candidate.id == candidate_id)
                )
                candidate = result.scalar_one_or_none()
                
                if not candidate:
                    raise GDPRComplianceError("Candidate not found")
                
                # Anonymize the candidate
                candidate.anonymize_data()
                candidate.updated_at = datetime.utcnow()
                
                await db.commit()
                
                logger.info(f"Candidate data anonymized: {candidate_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error anonymizing candidate data: {e}")
            raise GDPRComplianceError(f"Failed to anonymize data: {str(e)}")
    
    async def process_data_retention(self) -> Dict[str, int]:
        """Process data retention - delete/anonymize expired data"""
        try:
            async with get_db() as db:
                # Find candidates past retention date
                today = date.today()
                result = await db.execute(
                    select(Candidate)
                    .where(Candidate.data_retention_date <= today)
                    .where(Candidate.gdpr_flags.op('->>')('anonymized') != 'true')
                )
                expired_candidates = result.scalars().all()
                
                deleted_count = 0
                anonymized_count = 0
                
                for candidate in expired_candidates:
                    # Check consent status to determine action
                    consent = candidate.consent_status or {}
                    
                    if consent.get('data_processing') == False:
                        # Full deletion if consent withdrawn
                        await self.delete_candidate_data(
                            str(candidate.id), 
                            "system", 
                            "retention_expired"
                        )
                        deleted_count += 1
                    else:
                        # Anonymization if consent still valid
                        await self.anonymize_candidate_data(
                            str(candidate.id), 
                            "system"
                        )
                        anonymized_count += 1
                
                # Log retention processing
                audit_logger.log_data_operation(
                    user_id="system",
                    operation="data_retention_processing",
                    details={
                        "deleted_count": deleted_count,
                        "anonymized_count": anonymized_count,
                        "process_date": today.isoformat()
                    }
                )
                
                return {
                    "deleted": deleted_count,
                    "anonymized": anonymized_count,
                    "total_processed": deleted_count + anonymized_count
                }
                
        except Exception as e:
            logger.error(f"Error processing data retention: {e}")
            raise GDPRComplianceError(f"Failed to process retention: {str(e)}")
    
    async def get_consent_status(self, candidate_id: str) -> Dict[str, Any]:
        """Get current consent status for candidate"""
        try:
            async with get_db() as db:
                result = await db.execute(
                    select(Candidate.consent_status)
                    .where(Candidate.id == candidate_id)
                )
                consent_status = result.scalar_one_or_none()
                
                return consent_status or {}
                
        except Exception as e:
            logger.error(f"Error getting consent status: {e}")
            raise GDPRComplianceError(f"Failed to get consent status: {str(e)}")
    
    async def validate_data_processing(
        self, 
        candidate_id: str, 
        operation: str
    ) -> bool:
        """Validate if data processing operation is allowed"""
        try:
            consent_status = await self.get_consent_status(candidate_id)
            
            # Map operations to required consents
            operation_requirements = {
                "resume_analysis": ["data_processing", "resume_analysis"],
                "communication": ["data_processing", "communication"],
                "data_export": ["data_processing"],
                "analytics": ["data_processing", "analytics"]
            }
            
            required_consents = operation_requirements.get(operation, ["data_processing"])
            
            for consent_type in required_consents:
                if not consent_status.get(consent_type, False):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating data processing: {e}")
            return False


# Global service instance
gdpr_service = GDPRService()