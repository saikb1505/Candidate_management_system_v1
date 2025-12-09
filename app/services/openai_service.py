from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.candidate import ParsedCandidateData
import json
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def parse_candidate_resume_with_openai(resume_text: str) -> ParsedCandidateData:
    """
    Validate and parse candidate resume text using OpenAI.
    First validates that the document is a resume, then extracts structured data.

    Args:
        resume_text: Extracted text from candidate's resume

    Returns:
        ParsedCandidateData: Structured candidate data

    Raises:
        ValueError: If document is not a resume or parsing fails
    """
    prompt = f"""
You are a professional resume parser. Your task has TWO steps:

STEP 1: VALIDATE the document is a RESUME/CV
- A resume contains: personal info, work experience, education, skills
- NOT a resume: job descriptions, invoices, marketing materials, articles

STEP 2: If it IS a resume, EXTRACT the following information:
1. name: Full name of the candidate
2. email: Email address
3. phone: Phone number
4. skills: Array of technical and professional skills
5. designations: Array of ALL job titles/positions the candidate has held throughout their career
6. domain_knowledge: Summary of the candidate's domain expertise and industry knowledge

Document Text:
{resume_text}

Return a JSON object with this EXACT format:
{{
    "is_resume": true or false,
    "document_type": "resume" or "job_description" or "invoice" or "other",
    "error_reason": "explanation if not a resume, otherwise null",
    "name": "candidate name or null",
    "email": "email or null",
    "phone": "phone or null",
    "skills": ["skill1", "skill2"] or [],
    "designations": ["title1", "title2"] or [],
    "domain_knowledge": "summary or null"
}}

If is_resume is false, only fill is_resume, document_type, and error_reason. Other fields should be null/empty.
If is_resume is true, fill all fields with extracted data.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume validator and parser that first checks if a document is a resume, then extracts structured data from valid resumes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1200,
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)

        # Check if document is a valid resume
        is_resume = result.get("is_resume", False)
        if not is_resume:
            document_type = result.get("document_type", "unknown")
            error_reason = result.get("error_reason", "Document does not appear to be a resume")
            raise ValueError(f"Document is not a valid resume")

        # Extract candidate data
        candidate_data = {
            "name": result.get("name"),
            "email": result.get("email"),
            "phone": result.get("phone"),
            "skills": result.get("skills", []),
            "designations": result.get("designations", []),
            "domain_knowledge": result.get("domain_knowledge"),
        }

        return ParsedCandidateData(**candidate_data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
    except ValueError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise ValueError(f"Error parsing candidate resume with OpenAI: {str(e)}")
