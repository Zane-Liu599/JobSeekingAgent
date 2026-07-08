import { useEffect, useMemo, useState } from "react";
import Markdown from "react-markdown";
import { FaClipboardList, FaMagic } from "react-icons/fa";

import { CoverLetterResponse, JobLead, fetchApplicationPlan, fetchJobs, generateCoverLetter } from "../api/jobAutomation";
import { PageHeader } from "../components/PageHeader";

export function MaterialsPage() {
  const [jobs, setJobs] = useState<JobLead[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [coverLetter, setCoverLetter] = useState<CoverLetterResponse | null>(null);
  const [applicationPlan, setApplicationPlan] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const selectedJob = useMemo(() => jobs.find((job) => job.id === selectedJobId) ?? jobs[0], [jobs, selectedJobId]);

  useEffect(() => {
    fetchJobs()
      .then((data) => {
        setJobs(data);
        if (data[0]?.id) setSelectedJobId(data[0].id);
      })
      .catch((error: Error) => setMessage(error.message));
  }, []);

  async function handleCoverLetter() {
    if (!selectedJob?.id) return;
    setIsBusy(true);
    setMessage("");
    try {
      const result = await generateCoverLetter(selectedJob.id);
      setCoverLetter(result);
      setMessage(result.error ? "Generated with local fallback. Add a Gemini key for tailored output." : "Cover letter generated.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to generate cover letter");
    } finally {
      setIsBusy(false);
    }
  }

  async function handlePlan() {
    if (!selectedJob?.id) return;
    const result = await fetchApplicationPlan(selectedJob.id);
    setApplicationPlan(result.steps);
  }

  return (
    <>
      <PageHeader
        eyebrow="Application Material"
        title="Generate Cover Letter"
        description="Create job-specific material from the selected role, then review every step before submitting."
      />

      {message && <div className="alert alert-info">{message}</div>}

      <section className="automation-grid">
        <div className="panel">
          <h2>Select Job</h2>
          <select className="form-select" value={selectedJob?.id ?? ""} onChange={(event) => setSelectedJobId(Number(event.target.value))}>
            {jobs.map((job) => <option key={job.id ?? job.title} value={job.id ?? ""}>{job.title} · {job.company || "Unknown"}</option>)}
          </select>
          <p className="muted-text mt-3">{selectedJob ? `${selectedJob.location || "Location pending"} · ${selectedJob.employment_type || "Type pending"} · ${selectedJob.salary || "Salary pending"}` : "Save a job first."}</p>
          <div className="d-flex gap-2">
            <button className="btn btn-primary" disabled={isBusy || !selectedJob} onClick={handleCoverLetter}><FaMagic /> Generate</button>
            <button className="btn btn-outline-secondary" disabled={!selectedJob} onClick={handlePlan}><FaClipboardList /> Plan</button>
          </div>
        </div>

        <div className="panel">
          <h2>Application Plan</h2>
          <ol className="step-list">
            {applicationPlan.map((step) => <li key={step}>{step}</li>)}
          </ol>
        </div>
      </section>

      {coverLetter && (
        <section className="panel mt-3">
          <h2>Draft Preview</h2>
          <div className="cover-letter-preview">
            <Markdown>{coverLetter.text}</Markdown>
          </div>
        </section>
      )}
    </>
  );
}
