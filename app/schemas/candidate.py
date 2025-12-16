from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional, List
from datetime import datetime
from app.models.candidate import CandidateStatus


class CandidateBase(BaseModel):
    filename: str


class CandidateCreate(CandidateBase):
    file_path: str
    file_size: int


class CandidateUpdate(BaseModel):
    status: Optional[CandidateStatus] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    designations: Optional[List[str]] = None
    domain_knowledge: Optional[str] = None
    error_message: Optional[str] = None


class CandidateInDB(CandidateBase):
    id: int
    file_path: str
    file_size: int
    status: CandidateStatus
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    skills: Optional[List[str]]
    designations: Optional[List[str]]
    domain_knowledge: Optional[str]
    uploaded_by: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class Candidate(CandidateInDB):
    @computed_field
    @property
    def download_url(self) -> str:
        """Generate download URL for the resume"""
        return f"/candidates/{self.id}/download"


class ParsedCandidateData(BaseModel):
    """Schema for parsed candidate data from resume via OpenAI"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    designations: List[str] = []
    domain_knowledge: Optional[str] = None
