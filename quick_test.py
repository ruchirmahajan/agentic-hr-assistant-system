"""Quick test to see API response structure"""
import asyncio
from sqlalchemy import select, text
from src.core.database import engine, get_db, async_session_factory
from src.models.candidate import Candidate
from src.models.job import Job

async def test_get_candidate():
    async with async_session_factory() as db:
        result = await db.execute(select(Candidate).limit(1))
        candidate = result.scalar_one_or_none()
        
        if candidate:
            print("=== Candidate Found ===")
            print(f"ID: {candidate.id}")
            print(f"full_name property: {candidate.full_name}")
            print(f"email property: {candidate.email}")
            print(f"phone property: {candidate.phone}")
            print(f"experience_years: {candidate.experience_years}")
            print(f"current_position: {candidate.current_position}")
            print(f"current_company: {candidate.current_company}")
            # Check for status attribute
            print(f"Has status attr: {hasattr(candidate, 'status')}")
        else:
            print("No candidates found in database")

async def test_get_job():
    async with async_session_factory() as db:
        result = await db.execute(select(Job).limit(1))
        job = result.scalar_one_or_none()
        
        if job:
            print("\n=== Job Found ===")
            print(f"ID: {job.id}")
            print(f"title: {job.title}")
            print(f"department: {job.department}")
            print(f"location: {job.location}")
            print(f"employment_type: {job.employment_type}")
            print(f"experience_level: {job.experience_level}")
            print(f"description: {job.description[:50]}..." if job.description else "None")
            print(f"requirements: {job.requirements[:50]}..." if job.requirements else "None")
            # Check for status/job_type attributes
            print(f"Has status attr: {hasattr(job, 'status')}")
            print(f"Has job_type attr: {hasattr(job, 'job_type')}")
            print(f"is_active: {job.is_active}")
        else:
            print("\nNo jobs found in database")

if __name__ == "__main__":
    asyncio.run(test_get_candidate())
    asyncio.run(test_get_job())
