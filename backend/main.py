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

@app.post("/candidates")
def upload_candidate(
    # `Form(...)` means the browser sends these as form fields instead of JSON.
    # This is important because a file upload request is not plain JSON.
    name: str = Form(...),
    email: str | None = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Save a resume file to disk and store the candidate record in PostgreSQL.

    The frontend sends a multipart form: text fields + binary file. FastAPI splits
    this into separate values and gives us them as function arguments.
    """

    # `resume.filename` is the original file name uploaded by the browser.
    # We place it inside the uploads folder so we keep the file on the server.
    file_path = UPLOAD_DIR / resume.filename

    # `copyfileobj` copies the binary file content from the request stream into the disk file.
    # `wb` means "write bytes" because resumes are binary files, not plain text.
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Create a Candidate model instance using the submitted form values.
    candidate = Candidate(
        name=name,
        email=email,
        resume_filename=resume.filename,
        resume_path=str(file_path),
    )

    db.add(candidate)  # Add the row to the current SQLAlchemy transaction.
    db.commit()  # Save the new row permanently in PostgreSQL.
    db.refresh(candidate)  # Read back the database-generated values like id and created_at.

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