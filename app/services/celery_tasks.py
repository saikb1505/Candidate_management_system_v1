from app.services.celery_app import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.candidate import Candidate, CandidateStatus
from app.utils.file_handler import extract_text_from_file, delete_file
from app.services.openai_service import parse_candidate_resume_with_openai
from datetime import datetime
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

# Create sync engine for Celery tasks
sync_engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


@celery_app.task(bind=True, max_retries=3)
def process_candidate_resume_task(self, file_path: str, filename: str, file_size: int, uploaded_by: int):
    """
    Background task to process candidate resume:
    1. Extract text from file
    2. Parse with OpenAI
    3. Check for duplicates (email/phone)
    4. Create new candidate profile or update existing one
    """
    db = SessionLocal()

    try:
        # Extract text from file
        logger.info(f"Extracting text from candidate resume file: {filename}")
        resume_text = extract_text_from_file(file_path)

        if not resume_text:
            raise ValueError("No text extracted from candidate resume")

        # Parse with OpenAI (run async function in sync context)
        logger.info(f"Parsing candidate resume {filename} with OpenAI")
        parsed_data = asyncio.run(parse_candidate_resume_with_openai(resume_text))

        # Check if a candidate with the same email or phone already exists
        existing_candidate = None
        if parsed_data.email or parsed_data.phone:
            query = db.query(Candidate).filter(Candidate.status == CandidateStatus.COMPLETED)

            if parsed_data.email and parsed_data.phone:
                # Check for either email or phone match
                existing_candidate = query.filter(
                    (Candidate.email == parsed_data.email) |
                    (Candidate.phone == parsed_data.phone)
                ).first()
            elif parsed_data.email:
                # Check only email
                existing_candidate = query.filter(
                    Candidate.email == parsed_data.email
                ).first()
            elif parsed_data.phone:
                # Check only phone
                existing_candidate = query.filter(
                    Candidate.phone == parsed_data.phone
                ).first()

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

            db.commit()

            # Delete old resume file after successful database update
            if old_file_path and old_file_path != file_path:
                try:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        logger.info(f"Deleted old candidate resume file: {old_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to delete old candidate resume file {old_file_path}: {cleanup_error}")

            logger.info(f"Successfully updated existing candidate {existing_candidate.id}")
            return {
                "status": "success",
                "candidate_id": existing_candidate.id,
                "candidate_name": parsed_data.name,
                "is_update": True,
            }
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
                domain_knowledge=parsed_data.domain_knowledge,
                raw_parsed_data=parsed_data.model_dump(),
                processed_at=datetime.utcnow(),
            )

            db.add(new_candidate)
            db.commit()
            db.refresh(new_candidate)

            logger.info(f"Successfully created new candidate {new_candidate.id}")
            return {
                "status": "success",
                "candidate_id": new_candidate.id,
                "candidate_name": parsed_data.name,
                "is_update": False,
            }

    except Exception as e:
        logger.error(f"Error processing candidate resume {filename}: {str(e)}")

        # Retry the task
        try:
            raise self.retry(exc=e, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for candidate resume {filename}")
            return {"status": "error", "message": str(e)}

    finally:
        db.close()
