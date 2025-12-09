from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.candidate import Candidate, CandidateStatus
from app.utils.file_handler import extract_text_from_file, delete_file
from app.services.openai_service import parse_candidate_resume_with_openai
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


async def process_candidate_resume(
    db: AsyncSession,
    file_path: str,
    filename: str,
    file_size: int,
    uploaded_by: int,
) -> Candidate:
    """
    Process candidate resume synchronously:
    1. Extract text from file
    2. Parse with OpenAI
    3. Check for duplicates (email/phone)
    4. Create new candidate profile or update existing one

    Args:
        db: Database session
        file_path: Path to the uploaded resume file
        filename: Original filename
        file_size: Size of the file in bytes
        uploaded_by: ID of the user who uploaded the resume

    Returns:
        Candidate: The created or updated candidate record

    Raises:
        ValueError: If text extraction or parsing fails
    """
    try:
        # Extract text from file
        logger.info(f"Extracting text from candidate resume file: {filename}")
        resume_text = extract_text_from_file(file_path)

        if not resume_text:
            raise ValueError("No text extracted from candidate resume")

        # Validate and parse with OpenAI (validation happens inside the function)
        logger.info(f"Validating and parsing candidate resume {filename} with OpenAI")
        parsed_data = await parse_candidate_resume_with_openai(resume_text)

        # Check if a candidate with the same email or phone already exists
        existing_candidate = None
        if parsed_data.email or parsed_data.phone:
            query = select(Candidate).where(Candidate.status == CandidateStatus.COMPLETED)

            if parsed_data.email and parsed_data.phone:
                # Check for either email or phone match
                result = await db.execute(
                    query.where(
                        (Candidate.email == parsed_data.email) |
                        (Candidate.phone == parsed_data.phone)
                    )
                )
            elif parsed_data.email:
                # Check only email
                result = await db.execute(
                    query.where(Candidate.email == parsed_data.email)
                )
            else:
                # Check only phone
                result = await db.execute(
                    query.where(Candidate.phone == parsed_data.phone)
                )

            existing_candidate = result.scalar_one_or_none()

        if existing_candidate:
            # Update the existing candidate record
            logger.info(f"Found existing candidate {existing_candidate.id} with matching email/phone. Updating existing record.")

            # Store old file path for cleanup
            old_file_path = existing_candidate.file_path

            # Update existing candidate with new parsed data
            existing_candidate.name = parsed_data.name
            existing_candidate.email = parsed_data.email
            existing_candidate.phone = parsed_data.phone
            existing_candidate.skills = parsed_data.skills
            existing_candidate.designations = parsed_data.designations
            existing_candidate.domain_knowledge = parsed_data.domain_knowledge
            existing_candidate.raw_parsed_data = parsed_data.model_dump()
            existing_candidate.status = CandidateStatus.COMPLETED
            existing_candidate.processed_at = datetime.utcnow()
            existing_candidate.error_message = None

            # Update file path and metadata to reflect latest upload
            existing_candidate.file_path = file_path
            existing_candidate.filename = filename
            existing_candidate.file_size = file_size
            existing_candidate.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(existing_candidate)

            # Delete old resume file after successful database update
            if old_file_path and old_file_path != file_path:
                try:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        logger.info(f"Deleted old candidate resume file: {old_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to delete old candidate resume file {old_file_path}: {cleanup_error}")

            logger.info(f"Successfully updated existing candidate {existing_candidate.id}")
            return existing_candidate
        else:
            # No duplicate found, create new candidate
            logger.info(f"No existing candidate found. Creating new record for {filename}")

            new_candidate = Candidate(
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                status=CandidateStatus.COMPLETED,
                uploaded_by=uploaded_by,
                name=parsed_data.name,
                email=parsed_data.email,
                phone=parsed_data.phone,
                skills=parsed_data.skills,
                designations=parsed_data.designations,
                domain_knowledge=parsed_data.domain_knowledge,
                raw_parsed_data=parsed_data.model_dump(),
                processed_at=datetime.utcnow(),
            )

            db.add(new_candidate)
            await db.commit()
            await db.refresh(new_candidate)

            logger.info(f"Successfully created new candidate {new_candidate.id}")
            return new_candidate

    except Exception as e:
        logger.error(f"Error processing candidate resume {filename}: {str(e)}")
        # Clean up the uploaded file on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up uploaded file after error: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to clean up file {file_path}: {cleanup_error}")
        raise
