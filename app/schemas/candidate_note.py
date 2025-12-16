from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CandidateNoteBase(BaseModel):
    note: str


class CandidateNoteCreate(CandidateNoteBase):
    """Schema for creating a new note"""
    pass


class CandidateNoteWithStatus(CandidateNoteBase):
    """Schema for creating a note when changing status"""
    previous_status: Optional[str] = None
    new_status: Optional[str] = None


class CandidateNote(CandidateNoteBase):
    """Schema for note response"""
    id: int
    candidate_id: int
    user_id: int
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateNoteUpdate(BaseModel):
    """Schema for updating a note"""
    note: str
