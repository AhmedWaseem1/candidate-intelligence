import { useState } from "react";
function App() {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const jobData = {
      title: jobTitle,
      description: jobDescription,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jobData),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        alert("Job created successfully!");
        setJobTitle("");
        setJobDescription("");
      } else {
        console.error("Failed to create job");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };
  return (
    <div>
      <h1>Candidate Intelligence</h1>

      <h2>Create Job</h2>

      <form
        onSubmit={handleSubmit}
      >
        <div>
          <label>Job Title</label>
          <input type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
          />
        </div>

        <div>
          <label>Job Description</label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows="8"
          />
        </div>

        <button type="submit">Create Job</button>
      </form>
    </div>
  );
}

export default App;