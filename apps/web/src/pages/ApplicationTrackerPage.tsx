import { useEffect, useMemo, useState } from "react";

import { JobLead, fetchJobs, updateJobsStatus } from "../api/jobAutomation";
import { PageHeader } from "../components/PageHeader";

const statuses = ["found", "saved", "ignored", "ai_applying", "draft", "reviewing", "submitted", "interviewing", "offer", "rejected", "closed"];

export function ApplicationTrackerPage() {
  const [jobs, setJobs] = useState<JobLead[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [status, setStatus] = useState("submitted");
  const [message, setMessage] = useState("");

  const counts = useMemo(() => statuses.map((item) => ({
    status: item,
    count: jobs.filter((job) => job.status === item).length
  })), [jobs]);

  async function loadJobs() {
    const data = await fetchJobs();
    setJobs(data);
    if (!selectedJobId && data[0]?.id) setSelectedJobId(data[0].id);
  }

  useEffect(() => {
    loadJobs().catch((error: Error) => setMessage(error.message));
  }, []);

  async function handleUpdate() {
    if (!selectedJobId) return;
    const result = await updateJobsStatus([selectedJobId], status);
    setMessage(`Updated ${result.updated} job.`);
    await loadJobs();
  }

  return (
    <>
      <PageHeader
        eyebrow="Pipeline"
        title="Application Tracker"
        description="Move roles from saved lead to reviewed, submitted, interviewing, offer, or closed."
      />

      <section className="stat-grid">
        {counts.map((item) => (
          <article className="stat-card" key={item.status}>
            <span>{item.status}</span>
            <strong>{item.count}</strong>
          </article>
        ))}
      </section>

      {message && <div className="alert alert-info mt-3">{message}</div>}

      <section className="panel mt-3">
        <h2>Update Status</h2>
        <div className="form-grid">
          <select className="form-select" value={selectedJobId ?? ""} onChange={(event) => setSelectedJobId(Number(event.target.value))}>
            {jobs.map((job) => <option key={job.id ?? job.title} value={job.id ?? ""}>{job.title} · {job.company || "Unknown"}</option>)}
          </select>
          <select className="form-select" value={status} onChange={(event) => setStatus(event.target.value)}>
            {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <button className="btn btn-primary" onClick={handleUpdate}>Update</button>
        </div>
      </section>
    </>
  );
}
