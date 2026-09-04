import { useEffect, useState } from "react";

function App() {
  // A component is a JavaScript function that returns the UI it should render.

  // Each state value is the single source of truth for the matching form field.
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [jobs, setJobs] = useState([]); // Jobs loaded from the backend.

  // These state values store the candidate form data.
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");
  const [resume, setResume] = useState(null); // The selected resume file.

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

  // An empty dependency array means this runs once after the first render.
  useEffect(() => {
    fetchJobs();
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

  // Handle submitting the candidate upload form.
  const handleCandidateSubmit = async (e) => {
    // Prevent the browser from refreshing the page after form submission.
    e.preventDefault();

    // A resume must be selected before we send the request.
    if (!resume) {
      alert("Please select a resume");
      return;
    }

    // FormData is used when sending files through an HTTP request.
    // It can contain both normal text fields and the actual file.
    const formData = new FormData();

    // These field names must match the parameters expected by FastAPI.
    formData.append("name", candidateName);
    formData.append("email", candidateEmail);
    formData.append("resume", resume);

    try {
      // Send the candidate data and resume to the backend.
      // We do not manually set Content-Type because the browser
      // automatically creates the correct multipart/form-data header.
      const response = await fetch("http://127.0.0.1:8000/candidates", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload candidate");
      }

      const data = await response.json(); // Read the API response.

      console.log(data);
      alert("Candidate uploaded successfully!");

      // Clear the React state after a successful upload.
      setCandidateName("");
      setCandidateEmail("");
      setResume(null);

      // Reset the form so the selected file is also cleared visually.
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
             * File inputs are slightly different from normal inputs.
             * The selected file is available through e.target.files.
             * We store the first selected file in React state.
             */
            onChange={(e) => setResume(e.target.files[0])}
            required
          />
        </div>

        <button type="submit">Upload Candidate</button>
      </form>
    </div>
  );
}

export default App;