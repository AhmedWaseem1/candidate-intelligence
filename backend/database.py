import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()  # Loads values from backend/.env into the process environment.

# Read the database connection string from backend/.env.
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy uses this engine to manage connections to PostgreSQL.
engine = create_engine(DATABASE_URL)

# This factory creates independent sessions that can be used by API requests.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class used by all SQLAlchemy models.
Base = declarative_base()


def get_db():
    """Provide one database session to a FastAPI route."""

    # FastAPI runs this dependency before a route and receives the yielded session.
    db = SessionLocal()

    try:
        yield db
    finally:
        # Closing releases the connection even if the route raises an error.
        db.close()