import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import PyPDF2
from docx import Document
import io


async def save_upload_file(upload_file: UploadFile) -> tuple[str, int]:
    """
    Save uploaded file and return file path and size

    Returns:
        tuple: (file_path, file_size)
    """
    # Validate file extension
    file_ext = upload_file.filename.split(".")[-1].lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}",
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # Save file
    file_size = 0
    async with aiofiles.open(file_path, "wb") as f:
        content = await upload_file.read()
        file_size = len(content)

        # Check file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes",
            )

        await f.write(content)

    return file_path, file_size


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from PDF: {str(e)}",
        )


def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from DOCX: {str(e)}",
        )


def extract_text_from_file(file_path: str) -> str:
    """Extract text from file based on extension"""
    file_ext = file_path.split(".")[-1].lower()

    if file_ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext in ["doc", "docx"]:
        return extract_text_from_docx(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}",
        )


async def delete_file(file_path: str) -> bool:
    """Delete a file from the filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
