from pydantic import BaseModel


# Pydantic validates incoming JSON before it reaches the route function.
# The same shape is used for both creating and fully updating a job.
class JobCreate(BaseModel):
    # A colon introduces a type annotation; both values must be strings.
    title: str
    description: str