from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Job as JobModel
from schemas import JobCreate


app = FastAPI()  # The application object receives and routes HTTP requests.


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