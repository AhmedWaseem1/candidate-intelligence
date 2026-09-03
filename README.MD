# Candidate Intelligence

Candidate Intelligence is a small full-stack application for creating and reviewing job postings. The frontend is built with React and Vite, and the backend is a FastAPI service backed by PostgreSQL and SQLAlchemy.

## Current scope

The application currently supports:

- Creating a job with a title and description
- Listing all saved jobs
- Updating a job
- Deleting a job
- Checking backend availability through a health endpoint

Resume upload and candidate analysis are not implemented yet.

## Project structure

```text
candidate-intelligence/
├── backend/
│   ├── database.py    # Database connection and session dependency
│   ├── main.py        # FastAPI app and job endpoints
│   ├── models.py      # SQLAlchemy database models
│   └── schemas.py     # Pydantic request schemas
├── frontend/
│   ├── src/App.jsx    # React job-management interface
│   └── package.json   # Frontend scripts and dependencies
└── README.MD
```

## Quick start tomorrow

Use this checklist when returning to the project:

1. Start PostgreSQL and confirm that `backend/.env` still contains `DATABASE_URL`.
2. Open a terminal in the project root, then start the backend:

	```powershell
	cd backend
	.\venv\Scripts\Activate.ps1
	uvicorn main:app --reload
	```

3. Open a second terminal in the project root, then start the frontend:

	```powershell
	cd frontend
	npm run dev
	```

4. Open `http://localhost:5173` in the browser.
5. If the jobs do not load, visit `http://127.0.0.1:8000/health`. It should return:

	```json
	{"status":"ok"}
	```

The backend terminal must remain running while using the frontend. Stop either development server with `Ctrl+C`.

## Prerequisites

- Python 3.10 or newer
- Node.js and npm
- PostgreSQL running locally
- A PostgreSQL database and user with permission to create tables

## Configuration

Create `backend/.env` with a SQLAlchemy PostgreSQL connection string:

```env
DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/<database>
```

Do not commit `.env` or put real credentials in documentation. `backend/database.py` loads this value when the API starts. `backend/main.py` creates the database tables automatically; no migration tool is configured yet.

## Run locally

Open two terminals from the repository root.

### 1. Start the backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

If the virtual environment does not exist, create it and install the backend dependencies:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

The frontend calls the backend at `http://127.0.0.1:8000`. The backend CORS configuration currently allows requests from `http://localhost:5173`.

## How the application works

The application has three layers:

1. **React frontend:** `frontend/src/App.jsx` stores the form values and current job list in React state. When the page opens, it sends `GET /jobs`. When the form is submitted, it sends `POST /jobs`, clears the form, and fetches the updated list.
2. **FastAPI backend:** `backend/main.py` receives HTTP requests, validates request bodies with `JobCreate`, and uses a database session for each operation.
3. **PostgreSQL database:** `backend/models.py` maps the `Job` Python class to the `jobs` table. SQLAlchemy reads the connection string and creates the table when the API starts.

The normal create flow is:

```text
User fills form
	-> React sends POST /jobs
	-> FastAPI validates title and description
	-> SQLAlchemy inserts a Job row
	-> PostgreSQL assigns id and created_at
	-> React reloads GET /jobs and displays the new job
```

## Database model

The `jobs` table currently contains:

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | Integer | Auto-generated primary key |
| `title` | String | Required job title |
| `description` | Text | Required job description |
| `created_at` | Timestamp | Set by PostgreSQL when the row is created |

There is no migration system yet. During early development, adding a new column to `models.py` does not update an existing table automatically. For schema changes, use a migration tool such as Alembic or recreate the development table only when existing data can be discarded.

## API reference

All job request bodies use JSON with the following fields:

```json
{
	"title": "Backend Engineer",
	"description": "Build and maintain Python APIs."
}
```

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Returns `{ "status": "ok" }` when the API is running |
| `POST` | `/jobs` | Creates a job and returns the saved record |
| `GET` | `/jobs` | Returns all jobs |
| `PUT` | `/jobs/{job_id}` | Replaces a job's title and description |
| `DELETE` | `/jobs/{job_id}` | Deletes a job |

Example request:

```powershell
Invoke-RestMethod `
	-Uri http://127.0.0.1:8000/jobs `
	-Method Post `
	-ContentType "application/json" `
	-Body '{"title":"Backend Engineer","description":"Build Python APIs."}'
```

Updating or deleting a missing job returns HTTP `404` with `Job not found`.

The current React screen displays jobs and creates new ones. The update and delete endpoints exist in the backend but do not yet have controls in the frontend.

## Where to make changes

- Change database connection behavior in `backend/database.py`.
- Add or modify API routes in `backend/main.py`.
- Change database columns in `backend/models.py`.
- Change request validation in `backend/schemas.py`.
- Change the page, form, or API calls in `frontend/src/App.jsx`.
- Change visual styling in `frontend/src/App.css` and `frontend/src/index.css`.

When adding a new job field, update the model, schema, frontend request object, form state, and database schema or migration together. Otherwise the API and UI can disagree about the shape of a job.

## Frontend commands

Run these from `frontend/`:

```powershell
npm run dev      # Start the development server
npm run build    # Create a production build
npm run lint     # Run ESLint
npm run preview  # Preview the production build locally
```

## Troubleshooting

- **Database connection error:** confirm PostgreSQL is running and that `DATABASE_URL` points to an existing database.
- **CORS error:** use the frontend URL configured in `backend/main.py`, normally `http://localhost:5173`.
- **Frontend cannot load jobs:** verify the backend is running on port `8000` and check `http://127.0.0.1:8000/health`.
- **PowerShell blocks activation:** run `Set-ExecutionPolicy -Scope Process Bypass` in the current terminal, then activate the virtual environment again.
- **`uvicorn` is not recognized:** activate `backend/venv`, or install the backend packages inside that environment.
- **Port already in use:** stop the old server with `Ctrl+C`, or start the backend with another port and update the frontend URL in `frontend/src/App.jsx`.
- **Changes are not visible:** Vite should hot-reload frontend changes; restart the API after changing Python code if reload did not pick it up.

## Development notes

- The backend uses SQLAlchemy sessions per request and closes each session after the request completes.
- The `jobs` table is defined by `backend/models.py` with `id`, `title`, `description`, and `created_at` columns.
- There are currently no automated backend tests or database migrations in the repository.
- The frontend currently uses a hard-coded backend URL; a future deployment should move it to an environment variable.
