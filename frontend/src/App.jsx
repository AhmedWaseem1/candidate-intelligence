import { useEffect, useState } from "react";

function App() {
  // A component is a JavaScript function that returns the UI it should render.

  // Each state value is the single source of truth for the matching form field.
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [jobs, setJobs] = useState([]); // Jobs loaded from the backend.

  // These state values store the candidate form data for the resume upload form.
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");
  const [resume, setResume] = useState(null); // Holds the selected resume file object.

  // Store all uploaded candidates fetched from the backend.
  const [candidates, setCandidates] = useState([]);

  // `fetch` returns a promise, so this function waits for the HTTP response
  // and then converts the JSON response into data React can render.
  const fetchJobs = async () => {
    // `async` allows this function to pause at each `await` until the promise resolves.
    try {
      const response = await fetch("http://127.0.0.1:8000/jobs");

      // A response can exist even when the server returns an HTTP error.
      if (!response.ok) {
        throw new Error("Failed to fetch jobs");
      }

      const data = await response.json();
      setJobs(data); // Re-render the page with the latest jobs.
    } catch (error) {
      console.error("Error fetching jobs:", error);
    }
  };

  // Fetch all saved candidates so the page can display them after upload.
  const fetchCandidates = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/candidates");

      if (!response.ok) {
        throw new Error("Failed to fetch candidates");
      }

      const data = await response.json();
      setCandidates(data); // Store the API response in component state.
    } catch (error) {
      console.error("Error fetching candidates:", error);
    }
  };
  // An empty dependency array means this runs once after the first render.
  useEffect(() => {
    fetchJobs();
    fetchCandidates();
  }, []);

  // Stop the browser's normal form submission, which would reload the page.
  const handleSubmit = async (e) => {
    // `e` is the browser's submit event; its `target` is the submitted form.
    e.preventDefault();

    // Match the JSON shape expected by the JobCreate Pydantic schema.
    const jobData = {
      title: jobTitle,
      description: jobDescription,
    };

    try {
      // POST sends the form data to FastAPI as a JSON request body.
      const response = await fetch("http://127.0.0.1:8000/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jobData),
      });

      if (!response.ok) {
        throw new Error("Failed to create job");
      }

      const data = await response.json(); // Read the API response for debugging.

      console.log(data);

      setJobTitle(""); // Clear the controlled input after a successful save.
      setJobDescription("");

      fetchJobs(); // Reload so the newly created job appears in the list.
    } catch (error) {
      console.error("Error creating job:", error);
    }
  };

  // Handle the candidate upload form submission.
  const handleCandidateSubmit = async (e) => {
    // `e.preventDefault()` stops the browser from submitting the form normally,
    // which would refresh the page and lose the uploaded file state.
    e.preventDefault();

    // A file must be selected before we can send the request.
    if (!resume) {
      alert("Please select a resume");
      return;
    }

    // `FormData` is the browser API for sending multipart form requests.
    // It can include both string fields and binary file content in the same request.
    const formData = new FormData();

    // These keys must exactly match the parameter names in the FastAPI route.
    formData.append("name", candidateName);
    formData.append("email", candidateEmail);
    formData.append("resume", resume);

    try {
      // We do not set `Content-Type` manually because the browser creates the required
      // `multipart/form-data` boundary automatically for FormData requests.
      const response = await fetch("http://127.0.0.1:8000/candidates", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload candidate");
      }

      const data = await response.json(); // Read the JSON response from the backend.

      console.log(data);
      alert("Candidate uploaded successfully!");

      // Clear the controlled inputs after a successful upload.
      setCandidateName("");
      setCandidateEmail("");
      setResume(null);
      fetchCandidates();

      // Reset the file input so the browser clears the selected file visually.
      e.target.reset();
    } catch (error) {
      console.error("Error uploading candidate:", error);
    }
  };

  return (
    <div>
      <h1>Candidate Intelligence</h1>

      <h2>Create Job</h2>

      {/* React calls handleSubmit when the user submits this form. */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Job Title</label>
          <input
            type="text"
            value={jobTitle}
            /* Update React state on every keystroke. */
            onChange={(e) => setJobTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Job Description</label>
          <textarea
            value={jobDescription}
            /* The textarea follows the same controlled-input pattern. */
            onChange={(e) => setJobDescription(e.target.value)}
            rows="8"
            required
          />
        </div>

        <button type="submit">Create Job</button>
      </form>

      <hr />

      <h2>Existing Jobs</h2>

      {jobs.length === 0 ? (
        <p>No jobs found.</p>
      ) : (
        <div>
          {/* map() creates one job card for every object in the jobs array. */}
          {jobs.map((job) => (
            <div key={job.id}>
              <h3>{job.title}</h3>
              <p>{job.description}</p>
              <small>
                Created: {new Date(job.created_at).toLocaleString()}
              </small>
            </div>
          ))}
        </div>
      )}

      <hr />

      <h2>Upload Candidate</h2>

      {/* React calls handleCandidateSubmit when this form is submitted. */}
      <form onSubmit={handleCandidateSubmit}>
        <div>
          <label>Candidate Name</label>
          <input
            type="text"
            value={candidateName}
            /* Store the candidate name in React state on every keystroke. */
            onChange={(e) => setCandidateName(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Candidate Email</label>
          <input
            type="email"
            value={candidateEmail}
            /* Store the candidate email in React state. */
            onChange={(e) => setCandidateEmail(e.target.value)}
          />
        </div>

        <div>
          <label>Resume</label>
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            /*
             * File inputs are special because they expose the chosen file through
             * the browser's `files` array. We store the first selected file here.
             */
            onChange={(e) => setResume(e.target.files[0])}
            required
          />
        </div>

        <button type="submit">Upload Candidate</button>
      </form>
      <hr />

      <h2>Uploaded Candidates</h2>

      {candidates.length === 0 ? (
        <p>No candidates found.</p>
      ) : (
        <div>
          {/* map() creates one card per candidate received from the backend. */}
          {candidates.map((candidate) => (
            <div key={candidate.id}>
              <h3>{candidate.name}</h3>

              <p>
                Email: {candidate.email || "Not provided"}
              </p>

              <p>
                Resume: {candidate.resume_filename}
              </p>

              <small>
                Uploaded: {new Date(candidate.created_at).toLocaleString()}
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;