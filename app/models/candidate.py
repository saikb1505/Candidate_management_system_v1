from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class CandidateStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.UPLOADED, nullable=False)

    # Candidate information from resume parsing
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)  # List of skills
    domain_knowledge = Column(Text, nullable=True)
    raw_parsed_data = Column(JSON, nullable=True)  # Full OpenAI response

    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    uploaded_by_user = relationship("User", back_populates="candidates")
