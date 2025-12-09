from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.candidate import ParsedCandidateData
import json
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def parse_candidate_resume_with_openai(resume_text: str) -> ParsedCandidateData:
    """
    Parse candidate resume text using OpenAI and extract structured data

    Args:
        resume_text: Extracted text from candidate's resume

    Returns:
        ParsedCandidateData: Structured candidate data
    """
    prompt = f"""
You are a candidate resume parser. Extract the following information from the resume text and return it as a JSON object:

1. name: Full name of the candidate
2. email: Email address
3. phone: Phone number
4. skills: Array of technical and professional skills
5. designations: Array of ALL job titles/positions the candidate has held throughout their career (e.g., "Software Engineer", "Senior Developer", "Team Lead")
6. domain_knowledge: Summary of the candidate's domain expertise and industry knowledge

Resume Text:
{resume_text}

Return ONLY a valid JSON object with the above fields. If a field is not found, use null for strings or empty array for skills/designations.
Example format:
{{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "designations": ["Software Engineer", "Senior Backend Developer", "Technical Lead"],
    "domain_knowledge": "5 years of experience in backend development and API design"
}}
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional candidate resume parser that extracts structured data from resumes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
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

        parsed_data = json.loads(content)
        return ParsedCandidateData(**parsed_data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise ValueError(f"Error parsing candidate resume with OpenAI: {str(e)}")
