from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, cast, String
from typing import List, Optional
from datetime import datetime
from app.db.base import get_db
from app.schemas.candidate import Candidate as CandidateSchema, ParsedCandidateData
from app.models.candidate import Candidate, CandidateStatus
from app.models.user import User
from app.core.deps import get_current_user, require_recruiter_or_above
from app.utils.file_handler import save_upload_file, extract_text_from_file, delete_file
from app.services.celery_tasks import process_candidate_resume_task
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_candidate_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_recruiter_or_above),
):
    """
    Upload a candidate's resume file. File will be processed asynchronously.
    Candidate profile will be created or updated after parsing completes.
    Requires Recruiter role or higher.
    """
    try:
        # Save file
        file_path, file_size = await save_upload_file(file)

        # Trigger background processing (candidate will be created/updated in the task)
        process_candidate_resume_task.delay(file_path, file.filename, file_size, current_user.id)

        return {
            "message": "Candidate resume uploaded successfully and is being processed",
            "filename": file.filename,
            "status": "processing"
        }

    except Exception as e:
        logger.error(f"Error uploading candidate resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading candidate resume: {str(e)}",
        )


@router.get("/", response_model=List[CandidateSchema])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[CandidateStatus] = None,
    skills: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all candidates with optional filters.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status_filter: Filter by candidate status
        skills: Comma-separated list of skills to search for (e.g., "Python,Django,FastAPI")
    """
    # Start with base query
    query = select(Candidate)

    # Apply filters FIRST
    if status_filter:
        query = query.where(Candidate.status == status_filter)

    if skills:
        # Split skills by comma and strip whitespace
        skill_list = [skill.strip() for skill in skills.split(",") if skill.strip()]

        # Build OR conditions for each skill
        if skill_list:
            skill_conditions = []
            for skill in skill_list:
                # Cast JSON to text and use LIKE for case-insensitive partial matching
                # This checks if the skill appears anywhere in the skills JSON array
                # Removed quotes requirement to allow partial matching (e.g., "Ruby" matches "Ruby on Rails")
                skill_conditions.append(
                    func.lower(func.cast(Candidate.skills, String)).like(f'%{skill.lower()}%')
                )
            query = query.where(or_(*skill_conditions))

    # Apply ordering, then pagination LAST
    query = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    candidates = result.scalars().all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateSchema)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get candidate details by ID"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(require_recruiter_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Delete a candidate profile. Requires Recruiter role or higher."""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    # Delete file from filesystem
    await delete_file(candidate.file_path)

    # Delete from database
    await db.delete(candidate)

    return None


@router.get("/search/by-skill", response_model=List[CandidateSchema])
async def search_candidates_by_skill(
    skill: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search candidates by skill using case-insensitive partial matching"""
    result = await db.execute(
        select(Candidate)
        .where(Candidate.status == CandidateStatus.COMPLETED)
        .where(func.lower(func.cast(Candidate.skills, String)).like(f'%{skill.lower()}%'))
        .order_by(Candidate.created_at.desc())
    )
    candidates = result.scalars().all()
    return candidates


@router.get("/search/by-email", response_model=CandidateSchema)
async def search_candidate_by_email(
    email: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search candidate by email"""
    result = await db.execute(
        select(Candidate)
        .where(Candidate.email == email)
        .order_by(Candidate.created_at.desc())
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this email",
        )

    return candidate
