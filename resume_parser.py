# resume_parser.py
from pathlib import Path
from typing import List
from pypdf import PdfReader
from docx import Document


def list_resumes(resumes_dir: Path) -> List[Path]:
    """List all resume files (.pdf, .docx) in resumes_dir."""
    if not resumes_dir.exists():
        raise FileNotFoundError(f"Resumes directory not found: {resumes_dir}")
    files = [
        p for p in resumes_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".pdf", ".docx"}
    ]
    return sorted(files)


def extract_resume_text(path: Path) -> str:
    """Extract text from a resume file (.pdf or .docx)."""
    if not path.exists():
        raise FileNotFoundError(f"Resume not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)

    if suffix == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported resume format: {suffix}")


def extract_candidate_metadata(resume_text: str, llm_client) -> dict:
    """
    Optional for later: use LLM to extract candidate metadata.
    For now, return empty fields.
    """
    return {
        "name": "",
        "email": "",
        "phone": "",
        "current_title": "",
        "years_experience": None,
    }
