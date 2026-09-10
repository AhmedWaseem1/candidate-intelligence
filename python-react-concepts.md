# Python and React Concepts Used in This Project Only

This file explains only the Python and React parts that are actually used in this resume project.

---

# 1. Python concepts used in the backend

## 1.1 Import statements

Python files can import code from other files and libraries.

```python
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from pathlib import Path
```

Why it matters here:
- `FastAPI` creates the API
- `HTTPException` is used for errors like 404 or 400
- `File`, `UploadFile`, `Form` handle uploaded resumes and form data
- `Path` helps manage file paths
- `Session` gives database access

---

## 1.2 Functions and parameters

Python functions are used everywhere in the backend.

```python
def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    return "example text"
```

### Explanation
- `file_path` is a parameter
- `Path` tells Python the input is a file path object
- `-> str` means the function returns a string

Another example from the project:

```python
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return {"message": "Job created successfully"}
```

This function receives:
- `job` = validated job data
- `db` = database session injected by FastAPI

---

## 1.3 Decorators

The `@` symbol is a Python decorator. It adds behavior to a function.

```python
@app.get("/jobs")
def get_jobs():
    return []
```

### In this project
- `@app.get(...)` creates a GET route
- `@app.post(...)` creates a POST route
- `@app.put(...)` creates a PUT route
- `@app.delete(...)` creates a DELETE route

This is how the backend exposes API endpoints.

---

## 1.4 Return values

Functions can send data back to the caller.

```python
return {"status": "ok"}
```

This is used in:
- `/health`
- job create/update/delete routes
- candidate upload route

The frontend receives this JSON and uses it in React state.

---

## 1.5 Dictionaries and JSON

Python dictionaries are used to return JSON data.

```python
return {
    "message": "Job created successfully",
    "job": db_job,
}
```

### Why this matters
FastAPI automatically converts Python dictionaries into JSON for the browser.

---

## 1.6 Condition checks and validation

```python
if extension not in allowed_extensions:
    raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported")
```

### Explanation
- `if` checks a condition
- `raise HTTPException(...)` stops the request and returns an error to the frontend

This is used to validate uploaded resumes before processing them.

---

## 1.7 try / except error handling

```python
try:
    resume_text = extract_resume_text(file_path)
except Exception as error:
    if file_path.exists():
        file_path.unlink()
    raise HTTPException(status_code=400, detail=f"Could not extract resume text: {error}")
```

### Why it is used
If the resume is broken or not readable, the code catches the error and prevents bad data from being saved.

---

## 1.8 Path handling

```python
from pathlib import Path
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
```

### Meaning
- `Path("uploads")` creates a file path object
- `mkdir(exist_ok=True)` creates the folder if it does not already exist

This is used to save uploaded resumes to the server.

---

## 1.9 File upload logic

```python
with file_path.open("wb") as buffer:
    shutil.copyfileobj(resume.file, buffer)
```

### Meaning
- open the file for writing in binary mode
- copy uploaded file data into the server folder

This uploads the resume file to disk.

---

## 1.10 `Form` and `File` parameters

```python
def upload_candidate(
    name: str = Form(...),
    email: str | None = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
```

### Explanation
- `Form(...)` reads normal text fields from the form
- `File(...)` reads the uploaded file
- `UploadFile` stores the resume file object

This is needed because the frontend sends a `FormData` object.

---

## 1.11 SQLAlchemy database operations

These operations are used to save and fetch data.

```python
db.add(candidate)
db.commit()
db.refresh(candidate)
```

### Meaning
- `add()` stages the new object
- `commit()` saves it to the database
- `refresh()` loads the saved values such as ID or timestamps

### Query examples

```python
jobs = db.query(JobModel).all()
job = db.query(JobModel).filter(JobModel.id == job_id).first()
```

### Meaning
- `.all()` gets every result
- `.filter(...)` filters rows by a condition
- `.first()` gets the first matching row

This is the core database logic for jobs and candidates.

---

## 1.12 Sets and regex for skill matching

```python
import re

detected_skills = set()

for skill in known_skills:
    pattern = r"\b" + re.escape(skill) + r"\b"
    if re.search(pattern, normalized_text):
        detected_skills.add(skill)
```

### Meaning
- `set()` stores unique values
- `re.search(...)` checks whether a text pattern exists in a string
- this finds skills like `python`, `react`, `sql`, `docker`

This project uses a simple keyword matcher instead of a full ML model.

---

## 1.13 Pydantic model validation

```python
class JobCreate(BaseModel):
    title: str
    description: str
```

### Meaning
The incoming request must match the defined structure. If not, FastAPI rejects it before saving.

---

# 2. React concepts used in the frontend

## 2.1 Component function

```jsx
function App() {
  return <h1>Candidate Intelligence</h1>;
}
```

### Meaning
A React component is a JavaScript function that returns UI.

This project uses a single main `App` component.

---

## 2.2 useState for form data

```jsx
const [jobTitle, setJobTitle] = useState("");
const [jobDescription, setJobDescription] = useState("");
```

### Meaning
- `jobTitle` stores the value of the input
- `setJobTitle` updates it
- React re-renders whenever the value changes

This is how the forms are controlled.

---

## 2.3 Controlled input syntax

```jsx
<input
  type="text"
  value={jobTitle}
  onChange={(e) => setJobTitle(e.target.value)}
  required
/>
```

### This is important because:
- `value` is the state value
- `onChange` updates the state on every keystroke

This is the standard React form pattern.

---

## 2.4 useEffect for loading data on page load

```jsx
useEffect(() => {
  fetchJobs();
  fetchCandidates();
}, []);
```

### Meaning
- `useEffect` runs after render
- empty dependency array `[]` means it runs once when the page loads

This loads job and candidate data automatically.

---

## 2.5 async fetch and await

```jsx
const fetchJobs = async () => {
  const response = await fetch("http://127.0.0.1:8000/jobs");
  const data = await response.json();
  setJobs(data);
};
```

### Meaning
- `async` allows the function to wait
- `await` waits until the server responds
- `response.json()` converts the JSON into JavaScript objects

This is how React communicates with the Python API.

---

## 2.6 POST requests with JSON

```jsx
const response = await fetch("http://127.0.0.1:8000/jobs", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: jobTitle,
    description: jobDescription,
  }),
});
```

### Meaning
- `method: "POST"` sends data to create a new job
- `JSON.stringify(...)` converts JavaScript object to JSON
- `headers` tells the server the format of the request

---

## 2.7 Form submission handling

```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  // send request to backend
};
```

### Meaning
- `e.preventDefault()` stops the browser from refreshing the page
- form submission is handled in JavaScript instead

---

## 2.8 File upload in React

```jsx
const [resume, setResume] = useState(null);

<input
  type="file"
  accept=".pdf,.doc,.docx"
  onChange={(e) => setResume(e.target.files[0])}
  required
/>
```

### Meaning
- the file is stored in React state as `resume`
- `e.target.files[0]` gets the selected file

---

## 2.9 FormData for file upload

```jsx
const formData = new FormData();
formData.append("name", candidateName);
formData.append("email", candidateEmail);
formData.append("resume", resume);
```

### Meaning
`FormData` sends text fields and a file together in one request.

Think of it like a package containing:
- the candidate name
- the email
- the actual uploaded resume file

This matches the Python backend route:

```python
name: str = Form(...)
email: str | None = Form(None)
resume: UploadFile = File(...)
```

This is why the backend can read the file and the text fields separately.

---

## 2.10 Rendering lists with map()

```jsx
{jobs.map((job) => (
  <div key={job.id}>
    <h3>{job.title}</h3>
    <p>{job.description}</p>
  </div>
))}
```

### Meaning
- `map()` loops through the array
- for each item it creates a new block of JSX
- `key={job.id}` gives React a unique identity for that item

Without `key`, React may get confused when the list changes.

This is used for:
- showing all jobs
- showing all uploaded candidates
- showing the selected candidate details

---

## 2.11 Conditional rendering

```jsx
{jobs.length === 0 ? (
  <p>No jobs found.</p>
) : (
  <div>
    {jobs.map(...)}
  </div>
)}
```

### Meaning
React checks a condition and chooses what to show.

In simple words:
- if the list is empty, show `No jobs found.`
- otherwise, display the job cards

This pattern is used a lot in the app to show loading, empty states, and details.

---

## 2.12 Event handlers and buttons

```jsx
<button type="button" onClick={() => fetchCandidate(candidate.id)}>
  View Resume
</button>
```

### Meaning
When the user clicks the button, React runs the function `fetchCandidate(...)`.

This is how the app reacts to user actions without reloading the page.

---

## 2.13 State for selected item detail view

```jsx
const [selectedCandidate, setSelectedCandidate] = useState(null);
const [isLoadingCandidate, setIsLoadingCandidate] = useState(false);
```

### Meaning
- `selectedCandidate` stores the candidate currently shown in the detail panel
- `isLoadingCandidate` tells the app whether the server is still fetching the candidate

When the button is clicked:
1. state changes to true
2. the app shows `Loading candidate...`
3. API response returns
4. `selectedCandidate` becomes the data received
5. the detail section displays the resume text

---

# 3. The actual data flow in this project

## 3.1 Python backend flow

```text
Frontend form -> fetch request -> FastAPI route -> validate data -> save to database -> return JSON
```

Example:
1. React sends a POST request with a job title and description
2. Python route receives the request
3. `JobCreate` validates the data
4. database saves the row
5. FastAPI returns JSON like `{ message: "Job created successfully" }`

---

## 3.2 React frontend flow

```text
Component state -> user types -> onChange updates state -> button click -> fetch request -> response -> setState -> UI updates
```

Example:
1. user types in job title input
2. `onChange={(e) => setJobTitle(e.target.value)}` updates state
3. user clicks Create Job
4. `handleSubmit` sends the request
5. backend returns response
6. React updates the job list and the UI refreshes automatically

This is the heart of React.

---

## 3.3 Full project flow for candidate upload

```text
User selects file in React -> resume stored in state -> FormData created -> POST request to /candidates -> Python saves file -> PDF/DOCX parsed -> text extracted -> candidate row saved in DB -> JSON returned -> React shows uploaded candidate
```

This is the exact real-life flow used in your app.

---

# 4. Hard parts explained simply

## 4.1 What is a decorator?

A decorator is just a function that modifies another function.

Example:

```python
@app.get("/jobs")
def get_jobs():
    return []
```

This means:
- `get_jobs` is the original function
- `@app.get("/jobs")` adds a route rule to it
- now the function is accessible at `/jobs`

So decorators are not magic — they simply attach extra behavior.

---

## 4.2 What is `useState`?

`useState` is React's way to remember values.

```jsx
const [jobTitle, setJobTitle] = useState("");
```

Think of it like a variable that React watches.

When the value changes:
- React remembers the new value
- the component re-renders
- the screen updates

This is how input fields work in real apps.

---

## 4.3 What is `useEffect`?

`useEffect` is a place to run code after the component has rendered.

```jsx
useEffect(() => {
  fetchJobs();
}, []);
```

It is usually used for:
- loading data from the backend
- updating the page after mount
- reacting to state changes

The empty `[]` means: run once when the component first appears.

---

## 4.4 What is `fetch`?

`fetch` is the browser function used to talk to an API.

```jsx
const response = await fetch("http://127.0.0.1:8000/jobs");
```

This means:
- send a request to the backend URL
- wait for the response
- read the returned JSON
- update the UI

---

## 4.5 Why use `FormData` instead of JSON for file upload?

Because files are binary data, not normal text.

- JSON is good for strings, arrays, and objects
- `FormData` is good for files + text together

That is why the resume upload uses a form-like request instead of just JSON.

---

# 5. Most important syntax to remember

## Python syntax in this project

```python
@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobModel).all()
    return jobs
```

### What it means
- `@app.get("/jobs")` = create a GET route
- `def get_jobs(...)` = function that handles the request
- `db: Session = Depends(get_db)` = inject database session
- `return jobs` = sent back to the frontend as JSON

---

## React syntax in this project

```jsx
const [jobs, setJobs] = useState([]);

useEffect(() => {
  fetchJobs();
}, []);

{jobs.map((job) => (
  <div key={job.id}>{job.title}</div>
))}
```

### What it means
- `useState([])` = remember the jobs array
- `useEffect(...)` = run when the component loads
- `fetchJobs()` = get data from backend
- `jobs.map(...)` = display each job as a card

---

# 6. Final simple summary

In this project:
- Python handles the backend logic: routes, validation, file saving, database, resume parsing
- React handles the front-end logic: state, forms, user actions, loading data, rendering UI
- data moves between them using `fetch` and JSON
- the most important concepts are:
  - Python: `def`, decorators, return, `if`, `try/except`, `Path`, `Form`, `File`, database queries
  - React: `useState`, `useEffect`, `fetch`, `onChange`, `onClick`, `map()`, conditional rendering

If you remember only these ideas, you already understand the core of the project.

This project uses Python in the backend.

## 7.1 Example: FastAPI app

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

### Meaning
- `FastAPI()` creates the app
- `@app.get("/health")` creates a route
- The function returns JSON

## 7.2 Example: validation with Pydantic

```python
from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str
```

This validates incoming request data before saving it.

---

# 8. React Fundamentals

React is a JavaScript library for building user interfaces.

---

## 8.1 JSX syntax

JSX looks like HTML, but it is written inside JavaScript.

```jsx
function Welcome() {
  return <h1>Hello, React!</h1>;
}
```

### Use of JavaScript inside JSX

```jsx
const name = "Ali";

function Greeting() {
  return <h2>Hello {name}</h2>;
}
```

The `{}` allows JavaScript expressions inside JSX.

---

## 8.2 React components

A component is a reusable function that returns UI.

```jsx
function Button() {
  return <button>Click Me</button>;
}
```

Use it inside another component:

```jsx
function App() {
  return (
    <div>
      <Button />
    </div>
  );
}
```

---

## 8.3 Props

Props are values passed from parent to child.

```jsx
function WelcomeCard({ name }) {
  return <h2>Welcome {name}</h2>;
}

function App() {
  return <WelcomeCard name="Ahmed" />;
}
```

### Key idea
- Parent provides data
- Child receives it as a parameter

---

## 8.4 State with useState

State stores data that can change.

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increase</button>
    </div>
  );
}
```

### Meaning
- `count` = current value
- `setCount` = update function
- React re-renders the component when state changes

---

## 8.5 Events in React

```jsx
function SearchButton() {
  const handleClick = () => {
    alert("Button clicked");
  };

  return <button onClick={handleClick}>Search</button>;
}
```

Common events:
- `onClick`
- `onChange`
- `onSubmit`

---

## 8.6 Form handling

```jsx
function LoginForm() {
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" placeholder="Username" />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Why preventDefault?
It stops the browser from reloading the page after form submission.

---

## 8.7 Controlled inputs

```jsx
import { useState } from "react";

function FormExample() {
  const [name, setName] = useState("");

  return (
    <input
      type="text"
      value={name}
      onChange={(e) => setName(e.target.value)}
    />
  );
}
```

This pattern is used in forms for job title and description.

---

## 8.8 Conditional rendering

```jsx
function UserStatus({ isLoggedIn }) {
  return <p>{isLoggedIn ? "Online" : "Offline"}</p>;
}
```

Another example:

```jsx
function WelcomeMessage({ isLoggedIn }) {
  if (isLoggedIn) {
    return <h1>Welcome back</h1>;
  }

  return <h1>Please log in</h1>;
}
```

---

## 8.9 Rendering lists

```jsx
const fruits = ["Apple", "Banana", "Mango"];

function FruitList() {
  return (
    <ul>
      {fruits.map((fruit) => (
        <li key={fruit}>{fruit}</li>
      ))}
    </ul>
  );
}
```

### Key rule
Each list item should have a unique `key`.

---

## 8.10 useEffect

`useEffect` runs after the component renders.

```jsx
import { useEffect } from "react";

function Example() {
  useEffect(() => {
    console.log("Component loaded");
  }, []);

  return <h1>Hello</h1>;
}
```

### Dependency array

```jsx
useEffect(() => {
  console.log("Runs when count changes");
}, [count]);
```

This is used for API calls on page load.

---

## 8.11 Fetching data from backend

```jsx
useEffect(() => {
  fetch("http://127.0.0.1:8000/jobs")
    .then((response) => response.json())
    .then((data) => console.log(data));
}, []);
```

Modern async version:

```jsx
const fetchJobs = async () => {
  const response = await fetch("http://127.0.0.1:8000/jobs");
  const data = await response.json();
  console.log(data);
};
```

This project uses this pattern to call the Python backend.

---

## 8.12 Sending data to backend

```jsx
const response = await fetch("http://127.0.0.1:8000/jobs", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Python Developer",
    description: "Need Python and FastAPI"
  })
});
```

This sends JSON to the API.

---

# 9. Python vs React Summary

## Python
- Runs on the server
- Good for logic, APIs, database work, file processing
- Uses indentation and functions heavily

## React
- Runs in the browser
- Good for UI and interactions
- Uses components, state, props, JSX, and events

---

# 10. Syntax Cheat Sheet

## Python syntax

```python
def greet(name):
    if name:
        return f"Hello {name}"
    return "No name"
```

### Common rules
- Use `:` after `if`, `for`, `while`, `def`, `class`
- Indentation matters
- `=` assigns values
- `==` compares values

## React syntax

```jsx
function App() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### Common rules
- JSX uses HTML-like tags
- JavaScript expressions go inside `{}`
- Event handlers use camelCase like `onClick`
- Components return UI

---

# 11. Most Important Concepts to Remember

## Python to know well
- variables
- functions
- parameters and return values
- lists and dictionaries
- loops and conditions
- classes
- modules
- error handling

## React to know well
- component
- JSX
- props
- useState
- useEffect
- events
- forms
- rendering lists
- fetch API

---

# 12. Final tip

The easiest way to understand both is to practice small examples:

- Python: create a function that adds two numbers, then a function with default arguments
- React: build a counter, then a simple form that updates state

Once those building blocks are clear, the rest becomes much easier.
