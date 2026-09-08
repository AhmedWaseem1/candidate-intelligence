import re
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import os
import shutil
import shutil
from pathlib import Path
from database import Base, engine, get_db
from models import Candidate, Job as JobModel
from schemas import JobCreate


from pypdf import PdfReader
from docx import Document

# Extract a plain-text version of the uploaded resume so it can be displayed
# in the UI and checked against a job description for skill matching.
def extract_resume_text(file_path: Path) -> str:
    """
    Extract readable text from a PDF or DOCX resume.
    """
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(str(file_path))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if extension == ".docx":
        document = Document(str(file_path))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    raise ValueError("Unsupported resume format")

# This lightweight keyword matcher looks for common technical skills inside the
# extracted resume text or a job description. It is intentionally simple and
# deterministic for the early prototype, rather than using a full NLP model.
def extract_skills(text: str) -> set[str]:
    """
    Extract a small set of known technical skills from text.
    """
    known_skills = {
        "python",
        "javascript",
        "typescript",
        "react",
        "next.js",
        "node.js",
        "express",
        "fastapi",
        "django",
        "java",
        "spring",
        "c++",
        "c#",
        "html",
        "css",
        "tailwind",
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "git",
        "github",
        "rest",
        "graphql",
        "machine learning",
        "deep learning",
        "pandas",
        "numpy",
        "tensorflow",
        "pytorch",
        "figma",
        "agile",
        "scrum",
    }

    normalized_text = text.lower()
    detected_skills = set()

    for skill in known_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, normalized_text):
            detected_skills.add(skill)

    return detected_skills

app = FastAPI()  # The application object receives and routes HTTP requests.

# `uploads/` is the folder where resume files are saved on the server.
# `exist_ok=True` prevents an error if the folder already exists.
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create tables from the registered SQLAlchemy models on startup.
Base.metadata.create_all(bind=engine)

# Allow the local Vite frontend to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Return a small response used to confirm that the API is running."""

    # Simple endpoint for checking that the API process is reachable.
    return {"status": "ok"}


# Create a new job from the validated request body.
@app.post("/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Validate and save one job, then return the saved database object."""

    # `job` is the validated request data; `db` is injected by FastAPI.
    db_job = JobModel(
        title=job.title,
        description=job.description,
    )

    db.add(db_job)  # Stage the new object in the current transaction.
    db.commit()  # Persist the staged row in PostgreSQL.
    db.refresh(db_job)  # Read database-generated values such as id and created_at.

    return {
        "message": "Job created successfully",
        "job": db_job,
    }


# Return every job currently stored in the database.
@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    """Fetch every job from the jobs table."""

    # `.all()` executes the query and returns the matching rows as a list.
    jobs = db.query(JobModel).all()
    return jobs


# Delete one job, returning 404 when its ID does not exist.
@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete the job identified by the integer in the URL path."""

    # Find the requested row before attempting to delete it.
    job = db.query(JobModel).filter(JobModel.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)  # Mark the row for deletion in the current transaction.
    db.commit()  # Persist the deletion in PostgreSQL.

    return {"message": "Job deleted successfully"}


# Replace the title and description of an existing job.
@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job: JobCreate,
    db: Session = Depends(get_db),
):
    """Replace the title and description of one existing job."""

    # Look up the existing row so its values can be replaced.
    db_job = db.query(JobModel).filter(JobModel.id == job_id).first()

    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    db_job.title = job.title
    db_job.description = job.description

    db.commit()  # Save the changed fields.
    db.refresh(db_job)  # Reload the final database state for the response.

    return {
        "message": "Job updated successfully",
        "job": db_job,
    }

# Upload a candidate resume, save the file to disk, parse the text, and store
# both the metadata and extracted content in PostgreSQL for later viewing and matching.
@app.post("/candidates")
def upload_candidate(
    name: str = Form(...),
    email: str | None = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Only allow the file types our extraction function supports.
    allowed_extensions = {".pdf", ".docx"}

    extension = Path(resume.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resumes are supported",
        )

    # Create a safe local path for the uploaded file.
    file_path = UPLOAD_DIR / resume.filename

    # Save the uploaded file to disk.
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    try:
        # Read the saved file and extract its text.
        resume_text = extract_resume_text(file_path)
    except Exception as error:
        # Avoid saving an incomplete candidate record if extraction fails.
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=f"Could not extract resume text: {error}",
        )

    # Create the database record, including the extracted text.
    candidate = Candidate(
        name=name,
        email=email,
        resume_filename=resume.filename,
        resume_path=str(file_path),
        resume_text=resume_text,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "message": "Candidate uploaded successfully",
        "candidate": candidate,
    }

@app.get("/candidates")
def get_candidates(db: Session = Depends(get_db)):
    """Return all candidate rows saved in the database."""

    # `.query(Candidate).all()` executes a SELECT * FROM candidates query.
    candidates = db.query(Candidate).all()
    return candidates

# Return a single uploaded candidate so the frontend can render the complete
# resume metadata and extracted text in a detail panel.
@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Return one candidate and its extracted resume text for the detail view."""

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate
# Compare a job description against a candidate's extracted resume text to
# estimate how well the candidate matches the role. This is a simple prototype
# skill-overlap score, not a production-grade ATS or ML ranking system.
@app.get("/jobs/{job_id}/candidates/{candidate_id}/match")
def match_candidate_to_job(
    job_id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(JobModel)
        .filter(JobModel.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    job_skills = extract_skills(job.description)
    candidate_skills = extract_skills(candidate.resume_text or "")

    # Match the requested role against the candidate's extracted keywords and
    # return both the overlap and any missing skills in a format suitable for UI display.
    matched_skills = job_skills.intersection(candidate_skills)
    missing_skills = job_skills.difference(candidate_skills)

    if len(job_skills) == 0:
        match_score = 0
    else:
        match_score = round(
            (len(matched_skills) / len(job_skills)) * 100
        )

    return {
        "job_id": job.id,
        "candidate_id": candidate.id,
        "job_title": job.title,
        "candidate_name": candidate.name,
        "match_score": match_score,
        "job_skills": sorted(job_skills),
        "candidate_skills": sorted(candidate_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
    }