from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
from datetime import datetime

from app.db.base import get_db
from app.schemas.candidate_note import CandidateNoteCreate, CandidateNote, CandidateNoteUpdate
from app.models.candidate_note import CandidateNote as CandidateNoteModel
from app.models.candidate import Candidate
from app.models.user import User
from app.core.deps import get_current_user, require_recruiter_or_above
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{candidate_id}/notes", status_code=status.HTTP_201_CREATED, response_model=CandidateNote)
async def create_candidate_note(
    candidate_id: int,
    note_data: CandidateNoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a note to a candidate.
    Any authenticated user can add notes.
    """
    # Verify candidate exists
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    # Create note
    note = CandidateNoteModel(
        candidate_id=candidate_id,
        user_id=current_user.id,
        note=note_data.note,
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    # Add created_by field (user's full name or username)
    note_dict = {
        "id": note.id,
        "candidate_id": note.candidate_id,
        "user_id": note.user_id,
        "note": note.note,
        "previous_status": note.previous_status,
        "new_status": note.new_status,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "created_by": current_user.full_name or current_user.username,
    }

    return note_dict


@router.get("/{candidate_id}/notes", response_model=List[CandidateNote])
async def get_candidate_notes(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all notes for a candidate.
    Returns notes in chronological order (oldest first).
    """
    # Verify candidate exists
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    # Get all notes for this candidate with user information
    result = await db.execute(
        select(CandidateNoteModel)
        .options(joinedload(CandidateNoteModel.user))
        .where(CandidateNoteModel.candidate_id == candidate_id)
        .order_by(CandidateNoteModel.created_at.asc())
    )
    notes = result.unique().scalars().all()

    # Transform to include created_by field
    notes_response = []
    for note in notes:
        note_dict = {
            "id": note.id,
            "candidate_id": note.candidate_id,
            "user_id": note.user_id,
            "note": note.note,
            "previous_status": note.previous_status,
            "new_status": note.new_status,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "created_by": note.user.full_name or note.user.username,
        }
        notes_response.append(note_dict)

    return notes_response


@router.get("/notes/{note_id}", response_model=CandidateNote)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific note by ID"""
    result = await db.execute(
        select(CandidateNoteModel)
        .options(joinedload(CandidateNoteModel.user))
        .where(CandidateNoteModel.id == note_id)
    )
    note = result.unique().scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Transform to include created_by field
    note_dict = {
        "id": note.id,
        "candidate_id": note.candidate_id,
        "user_id": note.user_id,
        "note": note.note,
        "previous_status": note.previous_status,
        "new_status": note.new_status,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "created_by": note.user.full_name or note.user.username,
    }

    return note_dict


@router.patch("/notes/{note_id}", response_model=CandidateNote)
async def update_note(
    note_id: int,
    note_update: CandidateNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a note.
    Users can only update their own notes, unless they are recruiter or above.
    """
    result = await db.execute(
        select(CandidateNoteModel)
        .options(joinedload(CandidateNoteModel.user))
        .where(CandidateNoteModel.id == note_id)
    )
    note = result.unique().scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Check permissions - users can only edit their own notes unless they're recruiter or above
    from app.models.user import UserRole
    if note.user_id != current_user.id and current_user.role not in [UserRole.RECRUITER, UserRole.HR_MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this note",
        )

    # Update note
    note.note = note_update.note
    note.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(note)

    # Transform to include created_by field
    note_dict = {
        "id": note.id,
        "candidate_id": note.candidate_id,
        "user_id": note.user_id,
        "note": note.note,
        "previous_status": note.previous_status,
        "new_status": note.new_status,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "created_by": note.user.full_name or note.user.username,
    }

    return note_dict


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(require_recruiter_or_above),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a note.
    Requires Recruiter role or higher.
    """
    result = await db.execute(
        select(CandidateNoteModel).where(CandidateNoteModel.id == note_id)
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    await db.delete(note)
    await db.commit()

    return None
