"""
Demo API endpoints without authentication for testing
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
import logging

from ..core.database import get_db
from ..models.candidate import Candidate
from ..models.job import Job
from ..models.application import Application
from ..models.user import User
from ..models.interview import InterviewPanel, InterviewSlot, Interview, InterviewFeedback

logger = logging.getLogger(__name__)

demo_router = APIRouter()


class JobCreate(BaseModel):
    title: str
    description: str
    department: str
    location: str
    employment_type: str
    experience_level: str = "mid"
    requirements: Optional[str] = None


@demo_router.post("/candidates", status_code=status.HTTP_201_CREATED)
async def create_demo_candidate(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    experience_years: Optional[int] = Form(None),
    current_position: Optional[str] = Form(None),
    current_company: Optional[str] = Form(None),
    source: Optional[str] = Form("Demo"),
    resume_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a demo candidate without authentication"""
    try:
        # Create candidate record
        candidate = Candidate(
            full_name=full_name,
            email=email,
            phone=phone,
            experience_years=experience_years,
            current_position=current_position,
            current_company=current_company,
            source=source,
            skills="Demo skills",  # Placeholder
            skills_extracted="Demo skills"  # Placeholder
        )
        
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        
        return {
            "id": str(candidate.id),
            "message": "Demo candidate created successfully",
            "full_name": candidate.full_name,
            "email": candidate.email
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating demo candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create candidate: {str(e)}"
        )


@demo_router.get("/candidates")
async def list_demo_candidates(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List demo candidates without authentication"""
    try:
        # Build query
        query = select(Candidate).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        return [
            {
                "id": str(candidate.id),
                "full_name": candidate.full_name,
                "email": candidate.email,
                "phone": candidate.phone,
                "current_position": candidate.current_position,
                "current_company": candidate.current_company,
                "experience_years": candidate.experience_years,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None
            }
            for candidate in candidates
        ]
        
    except Exception as e:
        logger.error(f"Error listing demo candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list candidates: {str(e)}"
        )


@demo_router.post("/test", status_code=status.HTTP_201_CREATED)
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint works!"}


@demo_router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_demo_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a demo job without authentication"""
    try:
        # Get or create a demo user for created_by field
        demo_user_result = await db.execute(
            select(User).where(User.email == "demo@example.com")
        )
        demo_user = demo_user_result.scalar_one_or_none()
        
        if not demo_user:
            # Create demo user if it doesn't exist
            demo_user = User(
                email="demo@example.com",
                username="demo_user",
                first_name="Demo",
                last_name="User",
                hashed_password="demo_hash",
                is_active=True
            )
            db.add(demo_user)
            await db.commit()
            await db.refresh(demo_user)
        
        # Create job record
        job = Job(
            title=job_data.title,
            description=job_data.description,
            requirements=job_data.requirements or "No specific requirements",
            department=job_data.department,
            location=job_data.location,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            created_by=str(demo_user.id),
            is_active=True
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        return {
            "id": str(job.id),
            "message": "Demo job created successfully",
            "title": job.title,
            "department": job.department
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating demo job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@demo_router.get("/jobs")
async def list_demo_jobs(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List demo jobs without authentication"""
    try:
        # Build query
        query = select(Job).where(Job.is_active == True).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return [
            {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "department": job.department,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Error listing demo jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@demo_router.get("/applications")
async def list_demo_applications(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List demo applications without authentication"""
    try:
        # Build query
        query = select(Application).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        applications = result.scalars().all()
        
        return [
            {
                "id": str(app.id),
                "status": app.status,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None
            }
            for app in applications
        ]
        
    except Exception as e:
        logger.error(f"Error listing demo applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list applications: {str(e)}"
        )


@demo_router.get("/candidates/{candidate_id}")
async def get_demo_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific demo candidate without authentication"""
    try:
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        return {
            "id": str(candidate.id),
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "current_position": candidate.current_position,
            "current_company": candidate.current_company,
            "experience_years": candidate.experience_years,
            "status": "Active",
            "created_at": candidate.created_at.isoformat() if candidate.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candidate: {str(e)}"
        )


@demo_router.get("/jobs/{job_id}")
async def get_demo_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific demo job without authentication"""
    try:
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "department": job.department,
            "location": job.location,
            "employment_type": job.employment_type,
            "job_type": job.employment_type,
            "experience_level": job.experience_level,
            "requirements": job.requirements,
            "status": "open" if job.is_active else "closed",
            "is_active": job.is_active,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job: {str(e)}"
        )


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    experience_years: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None


@demo_router.put("/candidates/{candidate_id}")
async def update_demo_candidate(
    candidate_id: str,
    candidate_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a demo candidate without authentication"""
    try:
        # Get existing candidate
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        # Update candidate fields
        update_data = candidate_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(candidate, field):
                setattr(candidate, field, value)
        
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        
        return {
            "id": str(candidate.id),
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "experience_years": candidate.experience_years,
            "current_position": candidate.current_position,
            "current_company": candidate.current_company,
            "status": "Active",
            "created_at": candidate.created_at.isoformat() if candidate.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating demo candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update candidate: {str(e)}"
        )


@demo_router.put("/jobs/{job_id}")
async def update_demo_job(
    job_id: str,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a demo job without authentication"""
    try:
        # Get existing job
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Update job fields
        update_data = job_data.model_dump(exclude_unset=True)
        
        # Map job_type to employment_type
        if 'job_type' in update_data:
            update_data['employment_type'] = update_data.pop('job_type')
        
        for field, value in update_data.items():
            if hasattr(job, field):
                setattr(job, field, value)
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        return {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "department": job.department,
            "location": job.location,
            "job_type": job.employment_type,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "status": "open" if job.is_active else "closed",
            "is_active": job.is_active,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating demo job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )


@demo_router.get("/stats")
async def get_demo_stats(db: AsyncSession = Depends(get_db)):
    """Get demo statistics without authentication"""
    try:
        candidates_count = await db.scalar(select(func.count(Candidate.id)))
        jobs_count = await db.scalar(select(func.count(Job.id)).where(Job.is_active == True))
        applications_count = await db.scalar(select(func.count(Application.id)))
        interviews_count = await db.scalar(select(func.count(Interview.id)))
        panels_count = await db.scalar(select(func.count(InterviewPanel.id)).where(InterviewPanel.is_active == True))
        
        return {
            "total_candidates": candidates_count or 0,
            "active_jobs": jobs_count or 0,
            "total_applications": applications_count or 0,
            "scheduled_interviews": interviews_count or 0,
            "active_panels": panels_count or 0
        }
        
    except Exception as e:
        logger.error(f"Error getting demo stats: {e}")
        return {
            "total_candidates": 0,
            "active_jobs": 0,
            "total_applications": 0,
            "scheduled_interviews": 0,
            "active_panels": 0
        }


# ==================== INTERVIEW PANEL ENDPOINTS ====================

class InterviewerData(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    is_lead: bool = False


class InterviewPanelCreate(BaseModel):
    name: str
    level: str  # screening, technical_1, technical_2, managerial, hr, final
    department: Optional[str] = None
    description: Optional[str] = None
    max_interviews_per_day: int = 5
    interview_duration_minutes: int = 60
    buffer_minutes: int = 15
    interviewers: List[InterviewerData] = []
    skills_evaluated: List[str] = []


class InterviewPanelUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    max_interviews_per_day: Optional[int] = None
    interview_duration_minutes: Optional[int] = None
    buffer_minutes: Optional[int] = None
    interviewers: Optional[List[InterviewerData]] = None
    skills_evaluated: Optional[List[str]] = None
    is_active: Optional[bool] = None


@demo_router.post("/panels", status_code=status.HTTP_201_CREATED)
async def create_interview_panel(
    panel_data: InterviewPanelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview panel"""
    try:
        # Convert interviewers to dict format with IDs
        interviewers_with_ids = [
            {
                "id": str(uuid.uuid4()),
                "name": i.name,
                "email": i.email,
                "role": i.role,
                "is_lead": i.is_lead
            }
            for i in panel_data.interviewers
        ]
        
        panel = InterviewPanel(
            name=panel_data.name,
            level=panel_data.level,
            department=panel_data.department,
            description=panel_data.description,
            max_interviews_per_day=panel_data.max_interviews_per_day,
            interview_duration_minutes=panel_data.interview_duration_minutes,
            buffer_minutes=panel_data.buffer_minutes,
            interviewers=interviewers_with_ids,
            skills_evaluated=panel_data.skills_evaluated
        )
        
        db.add(panel)
        await db.commit()
        await db.refresh(panel)
        
        return {
            "id": str(panel.id),
            "message": "Interview panel created successfully",
            "name": panel.name,
            "level": panel.level
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating interview panel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview panel: {str(e)}"
        )


@demo_router.get("/panels")
async def list_interview_panels(
    level: Optional[str] = None,
    department: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all interview panels"""
    try:
        query = select(InterviewPanel)
        
        if is_active is not None:
            query = query.where(InterviewPanel.is_active == is_active)
        if level:
            query = query.where(InterviewPanel.level == level)
        if department:
            query = query.where(InterviewPanel.department == department)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        panels = result.scalars().all()
        
        return [
            {
                "id": str(panel.id),
                "name": panel.name,
                "level": panel.level,
                "department": panel.department,
                "description": panel.description,
                "max_interviews_per_day": panel.max_interviews_per_day,
                "interview_duration_minutes": panel.interview_duration_minutes,
                "buffer_minutes": panel.buffer_minutes,
                "interviewers": panel.interviewers or [],
                "skills_evaluated": panel.skills_evaluated or [],
                "is_active": panel.is_active,
                "created_at": panel.created_at.isoformat() if panel.created_at else None
            }
            for panel in panels
        ]
        
    except Exception as e:
        logger.error(f"Error listing interview panels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list interview panels: {str(e)}"
        )


@demo_router.get("/panels/{panel_id}")
async def get_interview_panel(
    panel_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific interview panel"""
    try:
        result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == panel_id)
        )
        panel = result.scalar_one_or_none()
        
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview panel not found"
            )
        
        return {
            "id": str(panel.id),
            "name": panel.name,
            "level": panel.level,
            "department": panel.department,
            "description": panel.description,
            "max_interviews_per_day": panel.max_interviews_per_day,
            "interview_duration_minutes": panel.interview_duration_minutes,
            "buffer_minutes": panel.buffer_minutes,
            "interviewers": panel.interviewers or [],
            "skills_evaluated": panel.skills_evaluated or [],
            "evaluation_criteria": panel.evaluation_criteria or [],
            "is_active": panel.is_active,
            "created_at": panel.created_at.isoformat() if panel.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview panel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview panel: {str(e)}"
        )


@demo_router.put("/panels/{panel_id}")
async def update_interview_panel(
    panel_id: str,
    panel_data: InterviewPanelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an interview panel"""
    try:
        result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == panel_id)
        )
        panel = result.scalar_one_or_none()
        
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview panel not found"
            )
        
        update_data = panel_data.model_dump(exclude_unset=True)
        
        # Convert interviewers if provided
        if 'interviewers' in update_data and update_data['interviewers']:
            interviewers_with_ids = [
                {
                    "id": str(uuid.uuid4()),
                    "name": i.name if hasattr(i, 'name') else i.get('name'),
                    "email": i.email if hasattr(i, 'email') else i.get('email'),
                    "role": i.role if hasattr(i, 'role') else i.get('role'),
                    "is_lead": i.is_lead if hasattr(i, 'is_lead') else i.get('is_lead', False)
                }
                for i in update_data['interviewers']
            ]
            update_data['interviewers'] = interviewers_with_ids
        
        for field, value in update_data.items():
            if hasattr(panel, field):
                setattr(panel, field, value)
        
        db.add(panel)
        await db.commit()
        await db.refresh(panel)
        
        return {
            "id": str(panel.id),
            "name": panel.name,
            "level": panel.level,
            "department": panel.department,
            "interviewers": panel.interviewers or [],
            "is_active": panel.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview panel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interview panel: {str(e)}"
        )


@demo_router.delete("/panels/{panel_id}")
async def delete_interview_panel(
    panel_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete an interview panel (set inactive)"""
    try:
        result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == panel_id)
        )
        panel = result.scalar_one_or_none()
        
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview panel not found"
            )
        
        panel.is_active = False
        db.add(panel)
        await db.commit()
        
        return {"message": "Interview panel deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interview panel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interview panel: {str(e)}"
        )


# ==================== INTERVIEW SLOT ENDPOINTS ====================

class SlotCreate(BaseModel):
    panel_id: str
    date: str  # ISO format date
    start_time: str  # ISO format datetime
    end_time: str  # ISO format datetime
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, biweekly
    recurrence_end_date: Optional[str] = None
    notes: Optional[str] = None


class SlotBulkCreate(BaseModel):
    panel_id: str
    dates: List[str]  # List of ISO format dates
    start_hour: int  # 9 for 9:00 AM
    end_hour: int  # 17 for 5:00 PM
    slot_duration_minutes: int = 60
    break_minutes: int = 15


@demo_router.post("/slots", status_code=status.HTTP_201_CREATED)
async def create_interview_slot(
    slot_data: SlotCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview slot"""
    try:
        # Verify panel exists
        panel_result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == slot_data.panel_id)
        )
        panel = panel_result.scalar_one_or_none()
        
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview panel not found"
            )
        
        slot = InterviewSlot(
            panel_id=slot_data.panel_id,
            date=datetime.fromisoformat(slot_data.date.replace('Z', '+00:00')),
            start_time=datetime.fromisoformat(slot_data.start_time.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(slot_data.end_time.replace('Z', '+00:00')),
            is_recurring=slot_data.is_recurring,
            recurrence_pattern=slot_data.recurrence_pattern,
            recurrence_end_date=datetime.fromisoformat(slot_data.recurrence_end_date.replace('Z', '+00:00')) if slot_data.recurrence_end_date else None,
            notes=slot_data.notes,
            status="available"
        )
        
        db.add(slot)
        await db.commit()
        await db.refresh(slot)
        
        return {
            "id": str(slot.id),
            "message": "Interview slot created successfully",
            "panel_id": slot.panel_id,
            "date": slot.date.isoformat() if slot.date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating interview slot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview slot: {str(e)}"
        )


@demo_router.post("/slots/bulk", status_code=status.HTTP_201_CREATED)
async def create_bulk_interview_slots(
    slot_data: SlotBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple interview slots at once"""
    try:
        # Verify panel exists
        panel_result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == slot_data.panel_id)
        )
        panel = panel_result.scalar_one_or_none()
        
        if not panel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview panel not found"
            )
        
        created_slots = []
        
        for date_str in slot_data.dates:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            current_hour = slot_data.start_hour
            
            while current_hour < slot_data.end_hour:
                start_time = date.replace(hour=current_hour, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=slot_data.slot_duration_minutes)
                
                if end_time.hour > slot_data.end_hour or (end_time.hour == slot_data.end_hour and end_time.minute > 0):
                    break
                
                slot = InterviewSlot(
                    panel_id=slot_data.panel_id,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    status="available"
                )
                db.add(slot)
                created_slots.append(slot)
                
                current_hour = end_time.hour
                if end_time.minute > 0:
                    current_hour += 1
                current_hour += slot_data.break_minutes // 60
        
        await db.commit()
        
        return {
            "message": f"Created {len(created_slots)} interview slots successfully",
            "slots_created": len(created_slots)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating bulk interview slots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview slots: {str(e)}"
        )


@demo_router.get("/slots")
async def list_interview_slots(
    panel_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List interview slots with filters"""
    try:
        query = select(InterviewSlot)
        
        if panel_id:
            query = query.where(InterviewSlot.panel_id == panel_id)
        if status_filter:
            query = query.where(InterviewSlot.status == status_filter)
        if date_from:
            query = query.where(InterviewSlot.date >= datetime.fromisoformat(date_from.replace('Z', '+00:00')))
        if date_to:
            query = query.where(InterviewSlot.date <= datetime.fromisoformat(date_to.replace('Z', '+00:00')))
            
        query = query.order_by(InterviewSlot.date, InterviewSlot.start_time).offset(skip).limit(limit)
        result = await db.execute(query)
        slots = result.scalars().all()
        
        return [
            {
                "id": str(slot.id),
                "panel_id": slot.panel_id,
                "date": slot.date.isoformat() if slot.date else None,
                "start_time": slot.start_time.isoformat() if slot.start_time else None,
                "end_time": slot.end_time.isoformat() if slot.end_time else None,
                "status": slot.status,
                "interview_id": slot.interview_id,
                "is_recurring": slot.is_recurring,
                "notes": slot.notes
            }
            for slot in slots
        ]
        
    except Exception as e:
        logger.error(f"Error listing interview slots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list interview slots: {str(e)}"
        )


@demo_router.get("/slots/{slot_id}")
async def get_interview_slot(
    slot_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific interview slot"""
    try:
        result = await db.execute(
            select(InterviewSlot).where(InterviewSlot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview slot not found"
            )
        
        return {
            "id": str(slot.id),
            "panel_id": slot.panel_id,
            "date": slot.date.isoformat() if slot.date else None,
            "start_time": slot.start_time.isoformat() if slot.start_time else None,
            "end_time": slot.end_time.isoformat() if slot.end_time else None,
            "status": slot.status,
            "interview_id": slot.interview_id,
            "is_recurring": slot.is_recurring,
            "recurrence_pattern": slot.recurrence_pattern,
            "notes": slot.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview slot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview slot: {str(e)}"
        )


@demo_router.put("/slots/{slot_id}/status")
async def update_slot_status(
    slot_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update the status of an interview slot"""
    try:
        result = await db.execute(
            select(InterviewSlot).where(InterviewSlot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview slot not found"
            )
        
        valid_statuses = ["available", "booked", "blocked", "past"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        slot.status = new_status
        db.add(slot)
        await db.commit()
        
        return {"message": "Slot status updated successfully", "new_status": new_status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating slot status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update slot status: {str(e)}"
        )


@demo_router.delete("/slots/{slot_id}")
async def delete_interview_slot(
    slot_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an interview slot"""
    try:
        result = await db.execute(
            select(InterviewSlot).where(InterviewSlot.id == slot_id)
        )
        slot = result.scalar_one_or_none()
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview slot not found"
            )
        
        if slot.status == "booked":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a booked slot. Cancel the interview first."
            )
        
        await db.delete(slot)
        await db.commit()
        
        return {"message": "Interview slot deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interview slot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interview slot: {str(e)}"
        )


# ==================== INTERVIEW SCHEDULE ENDPOINTS ====================

class InterviewCreate(BaseModel):
    candidate_id: str
    job_id: str
    panel_id: str
    slot_id: Optional[str] = None  # If provided, uses existing slot
    level: str
    round_number: int = 1
    scheduled_date: str  # ISO format
    scheduled_start: str  # ISO format
    scheduled_end: str  # ISO format
    interview_mode: str = "video"  # video, phone, in_person
    meeting_link: Optional[str] = None
    location: Optional[str] = None


class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    interview_mode: Optional[str] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    interviewer_notes: Optional[str] = None
    hr_notes: Optional[str] = None


class InterviewFeedbackCreate(BaseModel):
    interviewer_id: str
    interviewer_name: str
    interviewer_role: Optional[str] = None
    scores: Dict[str, float] = {}
    overall_score: Optional[float] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    comments: Optional[str] = None
    recommendation: Optional[str] = None  # strong_yes, yes, maybe, no, strong_no


@demo_router.post("/interviews", status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    interview_data: InterviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """Schedule a new interview"""
    try:
        # Verify candidate exists
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == interview_data.candidate_id)
        )
        if not candidate_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Verify job exists
        job_result = await db.execute(
            select(Job).where(Job.id == interview_data.job_id)
        )
        if not job_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify panel exists
        panel_result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == interview_data.panel_id)
        )
        if not panel_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Interview panel not found")
        
        # If slot_id provided, verify and book the slot
        slot = None
        if interview_data.slot_id:
            slot_result = await db.execute(
                select(InterviewSlot).where(InterviewSlot.id == interview_data.slot_id)
            )
            slot = slot_result.scalar_one_or_none()
            
            if not slot:
                raise HTTPException(status_code=404, detail="Interview slot not found")
            
            if slot.status != "available":
                raise HTTPException(status_code=400, detail="Slot is not available")
        
        # Create interview
        interview = Interview(
            candidate_id=interview_data.candidate_id,
            job_id=interview_data.job_id,
            panel_id=interview_data.panel_id,
            level=interview_data.level,
            round_number=interview_data.round_number,
            scheduled_date=datetime.fromisoformat(interview_data.scheduled_date.replace('Z', '+00:00')),
            scheduled_start=datetime.fromisoformat(interview_data.scheduled_start.replace('Z', '+00:00')),
            scheduled_end=datetime.fromisoformat(interview_data.scheduled_end.replace('Z', '+00:00')),
            interview_mode=interview_data.interview_mode,
            meeting_link=interview_data.meeting_link,
            location=interview_data.location,
            status="scheduled"
        )
        
        db.add(interview)
        await db.flush()  # Get the interview ID
        
        # Book the slot if provided
        if slot:
            slot.status = "booked"
            slot.interview_id = interview.id
            db.add(slot)
        
        await db.commit()
        await db.refresh(interview)
        
        return {
            "id": str(interview.id),
            "message": "Interview scheduled successfully",
            "candidate_id": interview.candidate_id,
            "job_id": interview.job_id,
            "panel_id": interview.panel_id,
            "level": interview.level,
            "scheduled_date": interview.scheduled_date.isoformat() if interview.scheduled_date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error scheduling interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule interview: {str(e)}"
        )


@demo_router.get("/interviews")
async def list_interviews(
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    panel_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List interviews with filters"""
    try:
        query = select(Interview)
        
        if candidate_id:
            query = query.where(Interview.candidate_id == candidate_id)
        if job_id:
            query = query.where(Interview.job_id == job_id)
        if panel_id:
            query = query.where(Interview.panel_id == panel_id)
        if status_filter:
            query = query.where(Interview.status == status_filter)
        if level:
            query = query.where(Interview.level == level)
        if date_from:
            query = query.where(Interview.scheduled_date >= datetime.fromisoformat(date_from.replace('Z', '+00:00')))
        if date_to:
            query = query.where(Interview.scheduled_date <= datetime.fromisoformat(date_to.replace('Z', '+00:00')))
            
        query = query.order_by(Interview.scheduled_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        interviews = result.scalars().all()
        
        # Get candidate and job names for display
        interview_list = []
        for interview in interviews:
            # Get candidate name
            candidate_result = await db.execute(
                select(Candidate).where(Candidate.id == interview.candidate_id)
            )
            candidate = candidate_result.scalar_one_or_none()
            
            # Get job title
            job_result = await db.execute(
                select(Job).where(Job.id == interview.job_id)
            )
            job = job_result.scalar_one_or_none()
            
            # Get panel name
            panel_result = await db.execute(
                select(InterviewPanel).where(InterviewPanel.id == interview.panel_id)
            )
            panel = panel_result.scalar_one_or_none()
            
            interview_list.append({
                "id": str(interview.id),
                "candidate_id": interview.candidate_id,
                "candidate_name": candidate.full_name if candidate else "Unknown",
                "job_id": interview.job_id,
                "job_title": job.title if job else "Unknown",
                "panel_id": interview.panel_id,
                "panel_name": panel.name if panel else "Unknown",
                "level": interview.level,
                "round_number": interview.round_number,
                "scheduled_date": interview.scheduled_date.isoformat() if interview.scheduled_date else None,
                "scheduled_start": interview.scheduled_start.isoformat() if interview.scheduled_start else None,
                "scheduled_end": interview.scheduled_end.isoformat() if interview.scheduled_end else None,
                "interview_mode": interview.interview_mode,
                "meeting_link": interview.meeting_link,
                "status": interview.status,
                "overall_score": interview.overall_score,
                "recommendation": interview.recommendation
            })
        
        return interview_list
        
    except Exception as e:
        logger.error(f"Error listing interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list interviews: {str(e)}"
        )


@demo_router.get("/interviews/{interview_id}")
async def get_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific interview with full details"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Get related entities
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == interview.candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        
        job_result = await db.execute(
            select(Job).where(Job.id == interview.job_id)
        )
        job = job_result.scalar_one_or_none()
        
        panel_result = await db.execute(
            select(InterviewPanel).where(InterviewPanel.id == interview.panel_id)
        )
        panel = panel_result.scalar_one_or_none()
        
        # Get feedback
        feedback_result = await db.execute(
            select(InterviewFeedback).where(InterviewFeedback.interview_id == interview_id)
        )
        feedbacks = feedback_result.scalars().all()
        
        return {
            "id": str(interview.id),
            "candidate": {
                "id": interview.candidate_id,
                "name": candidate.full_name if candidate else "Unknown",
                "email": candidate.email if candidate else None
            },
            "job": {
                "id": interview.job_id,
                "title": job.title if job else "Unknown",
                "department": job.department if job else None
            },
            "panel": {
                "id": interview.panel_id,
                "name": panel.name if panel else "Unknown",
                "interviewers": panel.interviewers if panel else []
            },
            "level": interview.level,
            "round_number": interview.round_number,
            "scheduled_date": interview.scheduled_date.isoformat() if interview.scheduled_date else None,
            "scheduled_start": interview.scheduled_start.isoformat() if interview.scheduled_start else None,
            "scheduled_end": interview.scheduled_end.isoformat() if interview.scheduled_end else None,
            "actual_start": interview.actual_start.isoformat() if interview.actual_start else None,
            "actual_end": interview.actual_end.isoformat() if interview.actual_end else None,
            "interview_mode": interview.interview_mode,
            "meeting_link": interview.meeting_link,
            "location": interview.location,
            "status": interview.status,
            "feedback": interview.feedback or {},
            "overall_score": interview.overall_score,
            "recommendation": interview.recommendation,
            "interviewer_notes": interview.interviewer_notes,
            "hr_notes": interview.hr_notes,
            "feedbacks": [
                {
                    "id": str(f.id),
                    "interviewer_name": f.interviewer_name,
                    "interviewer_role": f.interviewer_role,
                    "scores": f.scores,
                    "overall_score": f.overall_score,
                    "strengths": f.strengths,
                    "weaknesses": f.weaknesses,
                    "comments": f.comments,
                    "recommendation": f.recommendation,
                    "submitted_at": f.submitted_at.isoformat() if f.submitted_at else None
                }
                for f in feedbacks
            ],
            "created_at": interview.created_at.isoformat() if interview.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview: {str(e)}"
        )


@demo_router.put("/interviews/{interview_id}")
async def update_interview(
    interview_id: str,
    interview_data: InterviewUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an interview"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        update_data = interview_data.model_dump(exclude_unset=True)
        
        # Convert datetime strings
        datetime_fields = ['scheduled_date', 'scheduled_start', 'scheduled_end']
        for field in datetime_fields:
            if field in update_data and update_data[field]:
                update_data[field] = datetime.fromisoformat(update_data[field].replace('Z', '+00:00'))
        
        for field, value in update_data.items():
            if hasattr(interview, field):
                setattr(interview, field, value)
        
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        
        return {
            "id": str(interview.id),
            "message": "Interview updated successfully",
            "status": interview.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interview: {str(e)}"
        )


@demo_router.post("/interviews/{interview_id}/feedback", status_code=status.HTTP_201_CREATED)
async def add_interview_feedback(
    interview_id: str,
    feedback_data: InterviewFeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add feedback from an interviewer"""
    try:
        # Verify interview exists
        interview_result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = interview_result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        feedback = InterviewFeedback(
            interview_id=interview_id,
            interviewer_id=feedback_data.interviewer_id,
            interviewer_name=feedback_data.interviewer_name,
            interviewer_role=feedback_data.interviewer_role,
            scores=feedback_data.scores,
            overall_score=feedback_data.overall_score,
            strengths=feedback_data.strengths,
            weaknesses=feedback_data.weaknesses,
            comments=feedback_data.comments,
            recommendation=feedback_data.recommendation
        )
        
        db.add(feedback)
        
        # Update interview's overall score if provided
        if feedback_data.overall_score:
            # Get all feedbacks for this interview
            all_feedbacks_result = await db.execute(
                select(InterviewFeedback).where(InterviewFeedback.interview_id == interview_id)
            )
            all_feedbacks = all_feedbacks_result.scalars().all()
            
            scores = [f.overall_score for f in all_feedbacks if f.overall_score] + [feedback_data.overall_score]
            if scores:
                interview.overall_score = sum(scores) / len(scores)
                db.add(interview)
        
        await db.commit()
        await db.refresh(feedback)
        
        return {
            "id": str(feedback.id),
            "message": "Feedback added successfully",
            "interview_id": interview_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding interview feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add feedback: {str(e)}"
        )


@demo_router.put("/interviews/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    recommendation: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Mark an interview as completed"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        interview.status = "completed"
        interview.actual_end = datetime.utcnow()
        
        if recommendation:
            valid_recommendations = ["proceed", "reject", "hold", "hire"]
            if recommendation not in valid_recommendations:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid recommendation. Must be one of: {valid_recommendations}"
                )
            interview.recommendation = recommendation
        
        # Free up the slot if one was booked
        slot_result = await db.execute(
            select(InterviewSlot).where(InterviewSlot.interview_id == interview_id)
        )
        slot = slot_result.scalar_one_or_none()
        if slot:
            slot.status = "past"
            db.add(slot)
        
        db.add(interview)
        await db.commit()
        
        return {
            "message": "Interview marked as completed",
            "recommendation": interview.recommendation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(e)}"
        )


@demo_router.put("/interviews/{interview_id}/cancel")
async def cancel_interview(
    interview_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a scheduled interview"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        interview.status = "cancelled"
        if reason:
            interview.hr_notes = f"Cancelled: {reason}"
        
        # Free up the slot if one was booked
        slot_result = await db.execute(
            select(InterviewSlot).where(InterviewSlot.interview_id == interview_id)
        )
        slot = slot_result.scalar_one_or_none()
        if slot:
            slot.status = "available"
            slot.interview_id = None
            db.add(slot)
        
        db.add(interview)
        await db.commit()
        
        return {"message": "Interview cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel interview: {str(e)}"
        )


# ==================== INTERVIEW WORKFLOW ENDPOINTS ====================

@demo_router.get("/candidates/{candidate_id}/interviews")
async def get_candidate_interviews(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all interviews for a specific candidate"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.candidate_id == candidate_id).order_by(Interview.scheduled_date.desc())
        )
        interviews = result.scalars().all()
        
        interview_list = []
        for interview in interviews:
            job_result = await db.execute(select(Job).where(Job.id == interview.job_id))
            job = job_result.scalar_one_or_none()
            
            panel_result = await db.execute(select(InterviewPanel).where(InterviewPanel.id == interview.panel_id))
            panel = panel_result.scalar_one_or_none()
            
            interview_list.append({
                "id": str(interview.id),
                "job_title": job.title if job else "Unknown",
                "panel_name": panel.name if panel else "Unknown",
                "level": interview.level,
                "round_number": interview.round_number,
                "scheduled_date": interview.scheduled_date.isoformat() if interview.scheduled_date else None,
                "status": interview.status,
                "overall_score": interview.overall_score,
                "recommendation": interview.recommendation
            })
        
        return interview_list
        
    except Exception as e:
        logger.error(f"Error getting candidate interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candidate interviews: {str(e)}"
        )


@demo_router.get("/jobs/{job_id}/interviews")
async def get_job_interviews(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all interviews for a specific job"""
    try:
        result = await db.execute(
            select(Interview).where(Interview.job_id == job_id).order_by(Interview.scheduled_date.desc())
        )
        interviews = result.scalars().all()
        
        interview_list = []
        for interview in interviews:
            candidate_result = await db.execute(select(Candidate).where(Candidate.id == interview.candidate_id))
            candidate = candidate_result.scalar_one_or_none()
            
            panel_result = await db.execute(select(InterviewPanel).where(InterviewPanel.id == interview.panel_id))
            panel = panel_result.scalar_one_or_none()
            
            interview_list.append({
                "id": str(interview.id),
                "candidate_name": candidate.full_name if candidate else "Unknown",
                "panel_name": panel.name if panel else "Unknown",
                "level": interview.level,
                "round_number": interview.round_number,
                "scheduled_date": interview.scheduled_date.isoformat() if interview.scheduled_date else None,
                "status": interview.status,
                "overall_score": interview.overall_score,
                "recommendation": interview.recommendation
            })
        
        return interview_list
        
    except Exception as e:
        logger.error(f"Error getting job interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job interviews: {str(e)}"
        )


# =============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# =============================================================================

from ..models.document import (
    CandidateDocument, 
    DocumentAccessLog, 
    DocumentType, 
    DocumentStatus, 
    DocumentAccessLevel
)
from ..services.document_service import document_storage
from fastapi.responses import StreamingResponse
import io


class DocumentCreate(BaseModel):
    """Schema for document metadata"""
    document_type: str
    document_subtype: Optional[str] = None
    title: str
    description: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    institution_name: Optional[str] = None
    year_of_passing: Optional[int] = None
    grade_percentage: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    period_from: Optional[datetime] = None
    period_to: Optional[datetime] = None
    access_level: str = "panel_view"
    tags: Optional[List[str]] = []


@demo_router.post("/candidates/{candidate_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_candidate_document(
    candidate_id: str,
    document_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    document_subtype: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    institution_name: Optional[str] = Form(None),
    year_of_passing: Optional[int] = Form(None),
    grade_percentage: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    period_from: Optional[str] = Form(None),
    period_to: Optional[str] = Form(None),
    access_level: str = Form("panel_view"),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for a candidate
    Supports: Resume, ID proofs, Marksheets, Experience letters, Certificates, etc.
    """
    try:
        # Verify candidate exists
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Read file content
        content = await file.read()
        
        # Save file to storage
        storage_result = await document_storage.save_document(
            candidate_id=candidate_id,
            document_type=document_type,
            original_filename=file.filename,
            content=content
        )
        
        # Parse dates
        parsed_issue_date = datetime.fromisoformat(issue_date) if issue_date else None
        parsed_expiry_date = datetime.fromisoformat(expiry_date) if expiry_date else None
        parsed_period_from = datetime.fromisoformat(period_from) if period_from else None
        parsed_period_to = datetime.fromisoformat(period_to) if period_to else None
        
        # Parse tags
        tags_list = tags.split(",") if tags else []
        
        # Create document record
        document = CandidateDocument(
            candidate_id=candidate_id,
            document_type=document_type,
            document_subtype=document_subtype,
            title=title,
            description=description,
            original_filename=file.filename,
            stored_filename=storage_result["stored_filename"],
            file_path=storage_result["file_path"],
            file_size=storage_result["file_size"],
            mime_type=storage_result["mime_type"],
            file_extension=storage_result["file_extension"],
            checksum=storage_result["checksum"],
            document_number=document_number,
            issue_date=parsed_issue_date,
            expiry_date=parsed_expiry_date,
            issuing_authority=issuing_authority,
            institution_name=institution_name,
            year_of_passing=year_of_passing,
            grade_percentage=grade_percentage,
            company_name=company_name,
            designation=designation,
            period_from=parsed_period_from,
            period_to=parsed_period_to,
            access_level=access_level,
            tags=tags_list,
            status=DocumentStatus.PENDING.value,
            uploaded_by="demo_user"
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        logger.info(f"Document uploaded: {document.id} for candidate {candidate_id}")
        
        return {
            "id": str(document.id),
            "message": "Document uploaded successfully",
            "document_type": document.document_type,
            "title": document.title,
            "file_size": document.file_size_formatted,
            "warnings": storage_result.get("warnings", [])
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@demo_router.get("/candidates/{candidate_id}/documents")
async def list_candidate_documents(
    candidate_id: str,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents for a candidate
    Filterable by document_type and status
    """
    try:
        # Verify candidate exists
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Build query
        query = select(CandidateDocument).where(
            CandidateDocument.candidate_id == candidate_id,
            CandidateDocument.is_active == True
        )
        
        if document_type:
            query = query.where(CandidateDocument.document_type == document_type)
        
        if status:
            query = query.where(CandidateDocument.status == status)
        
        query = query.order_by(CandidateDocument.created_at.desc())
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return [
            {
                "id": str(doc.id),
                "document_type": doc.document_type,
                "document_subtype": doc.document_subtype,
                "title": doc.title,
                "description": doc.description,
                "original_filename": doc.original_filename,
                "file_size": doc.file_size_formatted,
                "mime_type": doc.mime_type,
                "status": doc.status,
                "access_level": doc.access_level,
                "document_number": doc.document_number,
                "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
                "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
                "is_expired": doc.is_expired,
                "issuing_authority": doc.issuing_authority,
                "institution_name": doc.institution_name,
                "year_of_passing": doc.year_of_passing,
                "grade_percentage": doc.grade_percentage,
                "company_name": doc.company_name,
                "designation": doc.designation,
                "period_from": doc.period_from.isoformat() if doc.period_from else None,
                "period_to": doc.period_to.isoformat() if doc.period_to else None,
                "verification_notes": doc.verification_notes,
                "verified_by": doc.verified_by,
                "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
                "tags": doc.tags or [],
                "download_count": doc.download_count,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "version": doc.version
            }
            for doc in documents
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@demo_router.get("/documents/{document_id}")
async def get_document_details(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific document"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get candidate info
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == document.candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        
        return {
            "id": str(document.id),
            "candidate_id": str(document.candidate_id),
            "candidate_name": candidate.full_name if candidate else "Unknown",
            "document_type": document.document_type,
            "document_subtype": document.document_subtype,
            "title": document.title,
            "description": document.description,
            "original_filename": document.original_filename,
            "file_size": document.file_size_formatted,
            "file_size_bytes": document.file_size,
            "mime_type": document.mime_type,
            "file_extension": document.file_extension,
            "status": document.status,
            "access_level": document.access_level,
            "document_number": document.document_number,
            "issue_date": document.issue_date.isoformat() if document.issue_date else None,
            "expiry_date": document.expiry_date.isoformat() if document.expiry_date else None,
            "is_expired": document.is_expired,
            "issuing_authority": document.issuing_authority,
            "institution_name": document.institution_name,
            "year_of_passing": document.year_of_passing,
            "grade_percentage": document.grade_percentage,
            "company_name": document.company_name,
            "designation": document.designation,
            "period_from": document.period_from.isoformat() if document.period_from else None,
            "period_to": document.period_to.isoformat() if document.period_to else None,
            "verification_notes": document.verification_notes,
            "verified_by": document.verified_by,
            "verified_at": document.verified_at.isoformat() if document.verified_at else None,
            "rejection_reason": document.rejection_reason,
            "tags": document.tags or [],
            "download_count": document.download_count,
            "last_accessed_at": document.last_accessed_at.isoformat() if document.last_accessed_at else None,
            "version": document.version,
            "is_latest": document.is_latest,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@demo_router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download a document file"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file content
        content = await document_storage.get_document(
            document.file_path,
            verify_checksum=document.checksum
        )
        
        # Update download count and last accessed
        document.download_count += 1
        document.last_accessed_at = datetime.utcnow()
        document.last_accessed_by = "demo_user"
        await db.commit()
        
        # Log access
        access_log = DocumentAccessLog(
            document_id=document.id,
            user_id="demo_user",
            user_name="Demo User",
            user_role="demo",
            action="download",
            access_reason="demo_download"
        )
        db.add(access_log)
        await db.commit()
        
        # Return file
        return StreamingResponse(
            io.BytesIO(content),
            media_type=document.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{document.original_filename}"',
                "Content-Length": str(document.file_size)
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document file not found on storage")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download document: {str(e)}"
        )


@demo_router.get("/documents/{document_id}/view")
async def view_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """View a document inline (for PDF viewer, image display, etc.)"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file content
        content = await document_storage.get_document(
            document.file_path,
            verify_checksum=document.checksum
        )
        
        # Update last accessed (but not download count for viewing)
        document.last_accessed_at = datetime.utcnow()
        document.last_accessed_by = "demo_user"
        await db.commit()
        
        # Log access
        access_log = DocumentAccessLog(
            document_id=document.id,
            user_id="demo_user",
            user_name="Demo User",
            user_role="demo",
            action="view",
            access_reason="demo_view"
        )
        db.add(access_log)
        await db.commit()
        
        # Return file for inline viewing
        return StreamingResponse(
            io.BytesIO(content),
            media_type=document.mime_type,
            headers={
                "Content-Disposition": f'inline; filename="{document.original_filename}"',
                "Content-Length": str(document.file_size)
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document file not found on storage")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to view document: {str(e)}"
        )


@demo_router.put("/documents/{document_id}/verify")
async def verify_document(
    document_id: str,
    status: str = Form(...),  # verified, rejected
    notes: Optional[str] = Form(None),
    rejection_reason: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Verify or reject a document"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if status not in ["verified", "rejected", "under_review"]:
            raise HTTPException(status_code=400, detail="Invalid status. Use: verified, rejected, or under_review")
        
        document.status = status
        document.verification_notes = notes
        document.verified_by = "demo_user"
        document.verified_at = datetime.utcnow()
        
        if status == "rejected":
            document.rejection_reason = rejection_reason
        
        await db.commit()
        
        logger.info(f"Document {document_id} verification status updated to: {status}")
        
        return {
            "id": str(document.id),
            "status": document.status,
            "message": f"Document {status} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error verifying document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify document: {str(e)}"
        )


@demo_router.put("/documents/{document_id}/access")
async def update_document_access(
    document_id: str,
    access_level: str = Form(...),
    allowed_users: Optional[str] = Form(None),  # Comma-separated user IDs
    db: AsyncSession = Depends(get_db)
):
    """Update document access level"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        valid_levels = ["hr_only", "panel_view", "restricted", "all_interviewers"]
        if access_level not in valid_levels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid access level. Use: {', '.join(valid_levels)}"
            )
        
        document.access_level = access_level
        
        if allowed_users:
            document.allowed_users = [u.strip() for u in allowed_users.split(",")]
        
        await db.commit()
        
        return {
            "id": str(document.id),
            "access_level": document.access_level,
            "message": "Document access updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating document access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document access: {str(e)}"
        )


@demo_router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    permanent: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document (soft delete by default, permanent if specified)"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if permanent:
            # Delete from storage
            await document_storage.delete_document(document.file_path)
            # Delete from database
            await db.delete(document)
            message = "Document permanently deleted"
        else:
            # Soft delete
            document.is_active = False
            document.deleted_at = datetime.utcnow()
            document.deleted_by = "demo_user"
            message = "Document deleted (can be restored)"
        
        await db.commit()
        
        logger.info(f"Document {document_id} deleted (permanent={permanent})")
        
        return {
            "id": document_id,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@demo_router.get("/documents/{document_id}/access-logs")
async def get_document_access_logs(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get access logs for a document (GDPR compliance)"""
    try:
        result = await db.execute(
            select(CandidateDocument).where(CandidateDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logs_result = await db.execute(
            select(DocumentAccessLog)
            .where(DocumentAccessLog.document_id == document_id)
            .order_by(DocumentAccessLog.accessed_at.desc())
        )
        logs = logs_result.scalars().all()
        
        return [
            {
                "id": str(log.id),
                "user_id": log.user_id,
                "user_name": log.user_name,
                "user_role": log.user_role,
                "action": log.action,
                "accessed_at": log.accessed_at.isoformat() if log.accessed_at else None,
                "ip_address": log.ip_address,
                "access_reason": log.access_reason
            }
            for log in logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting access logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get access logs: {str(e)}"
        )


@demo_router.get("/interviews/{interview_id}/documents")
async def get_interview_documents(
    interview_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for a candidate in an interview
    This is used by interview panels to view candidate documents
    """
    try:
        # Get interview
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Get documents for the candidate
        docs_result = await db.execute(
            select(CandidateDocument).where(
                CandidateDocument.candidate_id == interview.candidate_id,
                CandidateDocument.is_active == True,
                CandidateDocument.access_level.in_(["panel_view", "all_interviewers"])
            ).order_by(CandidateDocument.document_type, CandidateDocument.created_at.desc())
        )
        documents = docs_result.scalars().all()
        
        # Get candidate info
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == interview.candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        
        return {
            "interview_id": str(interview.id),
            "candidate_id": str(interview.candidate_id),
            "candidate_name": candidate.full_name if candidate else "Unknown",
            "documents": [
                {
                    "id": str(doc.id),
                    "document_type": doc.document_type,
                    "document_subtype": doc.document_subtype,
                    "title": doc.title,
                    "original_filename": doc.original_filename,
                    "file_size": doc.file_size_formatted,
                    "mime_type": doc.mime_type,
                    "status": doc.status,
                    "is_expired": doc.is_expired
                }
                for doc in documents
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview documents: {str(e)}"
        )


@demo_router.get("/document-types")
async def get_document_types():
    """Get list of supported document types"""
    return {
        "document_types": [
            {"value": "resume", "label": "Resume/CV", "description": "Candidate's resume or curriculum vitae"},
            {"value": "cover_letter", "label": "Cover Letter", "description": "Application cover letter"},
            {"value": "identity_proof", "label": "Identity Proof", "description": "Passport, Aadhaar, Driver's License, etc."},
            {"value": "address_proof", "label": "Address Proof", "description": "Utility bill, bank statement, etc."},
            {"value": "education_certificate", "label": "Education Certificate", "description": "Degree, diploma certificates"},
            {"value": "marksheet", "label": "Marksheet", "description": "Academic transcripts and marksheets"},
            {"value": "degree_certificate", "label": "Degree Certificate", "description": "University degree certificate"},
            {"value": "experience_letter", "label": "Experience Letter", "description": "Previous employment experience letter"},
            {"value": "relieving_letter", "label": "Relieving Letter", "description": "Letter confirming end of employment"},
            {"value": "salary_slip", "label": "Salary Slip", "description": "Previous salary/pay stubs"},
            {"value": "offer_letter", "label": "Offer Letter", "description": "Previous job offer letters"},
            {"value": "portfolio", "label": "Portfolio", "description": "Work samples and portfolio"},
            {"value": "certification", "label": "Certification", "description": "Professional certifications"},
            {"value": "reference_letter", "label": "Reference Letter", "description": "Professional reference letters"},
            {"value": "background_check", "label": "Background Check", "description": "Background verification documents"},
            {"value": "medical_certificate", "label": "Medical Certificate", "description": "Health/medical certificates"},
            {"value": "other", "label": "Other", "description": "Other supporting documents"}
        ],
        "access_levels": [
            {"value": "hr_only", "label": "HR Only", "description": "Only HR team can access"},
            {"value": "panel_view", "label": "Panel View", "description": "Interview panels can view"},
            {"value": "restricted", "label": "Restricted", "description": "Only specific users can access"},
            {"value": "all_interviewers", "label": "All Interviewers", "description": "All interviewers can access"}
        ],
        "statuses": [
            {"value": "pending", "label": "Pending", "description": "Awaiting verification"},
            {"value": "verified", "label": "Verified", "description": "Document verified"},
            {"value": "rejected", "label": "Rejected", "description": "Document rejected"},
            {"value": "expired", "label": "Expired", "description": "Document has expired"},
            {"value": "under_review", "label": "Under Review", "description": "Currently being reviewed"}
        ]
    }


@demo_router.get("/documents/stats")
async def get_document_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get document statistics"""
    try:
        # Total documents
        total_result = await db.execute(
            select(func.count(CandidateDocument.id)).where(CandidateDocument.is_active == True)
        )
        total_documents = total_result.scalar() or 0
        
        # By type
        type_result = await db.execute(
            select(
                CandidateDocument.document_type,
                func.count(CandidateDocument.id)
            ).where(CandidateDocument.is_active == True)
            .group_by(CandidateDocument.document_type)
        )
        by_type = {row[0]: row[1] for row in type_result}
        
        # By status
        status_result = await db.execute(
            select(
                CandidateDocument.status,
                func.count(CandidateDocument.id)
            ).where(CandidateDocument.is_active == True)
            .group_by(CandidateDocument.status)
        )
        by_status = {row[0]: row[1] for row in status_result}
        
        # Storage stats
        storage_stats = document_storage.get_storage_stats()
        
        return {
            "total_documents": total_documents,
            "by_type": by_type,
            "by_status": by_status,
            "storage": storage_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document stats: {str(e)}"
        )