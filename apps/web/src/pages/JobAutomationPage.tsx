import { FormEvent, useEffect, useMemo, useState } from "react";
import Markdown from "react-markdown";
import { FaDownload, FaMagic, FaSearch, FaTrash } from "react-icons/fa";

import {
  CoverLetterResponse,
  JobLead,
  applyUrlForJob,
  createJob,
  deleteJobs,
  fetchApplicationPlan,
  fetchJobs,
  generateCoverLetter,
  searchJobs,
  updateJobsStatus
} from "../api/jobAutomation";
import { PageHeader } from "../components/PageHeader";

const emptyManualJob = {
  title: "",
  company: "",
  location: "",
  employment_type: "",
  salary: "",
  platform: "manual",
  job_url: "",
  description: ""
};

const statuses = ["found", "saved", "ignored", "ai_applying", "draft", "reviewing", "submitted", "interviewing", "offer", "rejected", "closed"];

export function JobAutomationPage() {
  const [jobs, setJobs] = useState<JobLead[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchForm, setSearchForm] = useState({ keywords: "Software Engineer", location: "Sydney" });
  const [manualJob, setManualJob] = useState(emptyManualJob);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [status, setStatus] = useState("reviewing");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [coverLetter, setCoverLetter] = useState<CoverLetterResponse | null>(null);
  const [applicationPlan, setApplicationPlan] = useState<string[]>([]);

  const selectedJob = useMemo(
    () => jobs.find((job) => job.id === selectedJobId) ?? jobs[0],
    [jobs, selectedJobId]
  );

  async function loadJobs() {
    const data = await fetchJobs();
    setJobs(data);
    if (!selectedJobId && data[0]?.id) {
      setSelectedJobId(data[0].id);
    }
  }

  useEffect(() => {
    loadJobs().catch((error: Error) => setMessage(error.message));
  }, []);

  async function runWithMessage(action: () => Promise<string>) {
    setIsBusy(true);
    setMessage("");
    try {
      setMessage(await action());
      await loadJobs();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Request failed");
    } finally {
      setIsBusy(false);
    }
  }

  function toggleSelected(jobId: number) {
    setSelectedIds((current) =>
      current.includes(jobId) ? current.filter((id) => id !== jobId) : [...current, jobId]
    );
  }

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    await runWithMessage(async () => {
      const result = await searchJobs(searchForm);
      return `${result.message} Saved ${result.saved_count} result(s).`;
    });
  }

  async function handleManualJob(event: FormEvent) {
    event.preventDefault();
    await runWithMessage(async () => {
      const job = await createJob(manualJob);
      setManualJob(emptyManualJob);
      return `Saved ${job.title} at ${job.company}.`;
    });
  }

  async function handleDelete() {
    await runWithMessage(async () => {
      const result = await deleteJobs(selectedIds);
      setSelectedIds([]);
      return `Deleted ${result.deleted} job(s).`;
    });
  }

  async function handleStatusUpdate() {
    await runWithMessage(async () => {
      const ids = selectedIds.length ? selectedIds : selectedJob?.id ? [selectedJob.id] : [];
      const result = await updateJobsStatus(ids, status);
      return `Updated ${result.updated} job(s).`;
    });
  }

  async function handleCoverLetter() {
    if (!selectedJob?.id) return;
    setIsBusy(true);
    setMessage("");
    try {
      const result = await generateCoverLetter(selectedJob.id);
      setCoverLetter(result);
      setMessage(`Generated cover letter: ${result.path}`);
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
        eyebrow="Job Automation"
        title="Search, Generate, Apply, Track"
        description="Search job boards, save leads, generate tailored cover letters, export jobs, and manage the application pipeline."
      />

      <section className="automation-grid">
        <form className="panel" onSubmit={handleSearch}>
          <h2>Search Jobs</h2>
          <div className="form-grid">
            <input
              className="form-control"
              value={searchForm.keywords}
              onChange={(event) => setSearchForm({ ...searchForm, keywords: event.target.value })}
              placeholder="Search"
            />
            <input
              className="form-control"
              value={searchForm.location}
              onChange={(event) => setSearchForm({ ...searchForm, location: event.target.value })}
              placeholder="Location"
            />
          </div>
          <button className="btn btn-primary mt-3" disabled={isBusy} type="submit">
            <FaSearch /> Search and Save
          </button>
        </form>

        <form className="panel" onSubmit={handleManualJob}>
          <h2>Add Job Lead</h2>
          <div className="form-grid">
            <input className="form-control" required placeholder="Title" value={manualJob.title} onChange={(event) => setManualJob({ ...manualJob, title: event.target.value })} />
            <input className="form-control" required placeholder="Company" value={manualJob.company} onChange={(event) => setManualJob({ ...manualJob, company: event.target.value })} />
            <input className="form-control" placeholder="Location" value={manualJob.location} onChange={(event) => setManualJob({ ...manualJob, location: event.target.value })} />
            <input className="form-control" placeholder="Type" value={manualJob.employment_type} onChange={(event) => setManualJob({ ...manualJob, employment_type: event.target.value })} />
            <input className="form-control" placeholder="Salary" value={manualJob.salary} onChange={(event) => setManualJob({ ...manualJob, salary: event.target.value })} />
            <input className="form-control" placeholder="URL" value={manualJob.job_url} onChange={(event) => setManualJob({ ...manualJob, job_url: event.target.value })} />
          </div>
          <textarea className="form-control mt-3" placeholder="Description" value={manualJob.description} onChange={(event) => setManualJob({ ...manualJob, description: event.target.value })} />
          <button className="btn btn-outline-primary mt-3" disabled={isBusy} type="submit">Save Lead</button>
        </form>
      </section>

      {message && <div className="alert alert-info mt-3">{message}</div>}

      <section className="panel mt-3">
        <div className="jobs-toolbar">
          <h2>Jobs</h2>
          <div className="toolbar-actions">
            <select className="form-select form-select-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <button className="btn btn-sm btn-outline-secondary" disabled={isBusy || (!selectedIds.length && !selectedJob)} onClick={handleStatusUpdate}>Mark</button>
            <a className="btn btn-sm btn-outline-success" href="/api/ai/jobs/export"><FaDownload /> Export</a>
            <button className="btn btn-sm btn-outline-danger" disabled={isBusy || !selectedIds.length} onClick={handleDelete}><FaTrash /> Delete</button>
          </div>
        </div>
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th></th>
                <th>Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Type</th>
                <th>Salary</th>
                <th>Status</th>
                <th>Platform</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id ?? `${job.title}-${job.company}`} className={selectedJob?.id === job.id ? "table-active" : ""} onDoubleClick={() => applyUrlForJob(job) && window.open(applyUrlForJob(job), "_blank", "noopener,noreferrer")} onClick={() => job.id && setSelectedJobId(job.id)}>
                  <td>
                    <input type="checkbox" checked={job.id ? selectedIds.includes(job.id) : false} onChange={() => job.id && toggleSelected(job.id)} />
                  </td>
                  <td>{job.title}</td>
                  <td>{job.company}</td>
                  <td>{job.location}</td>
                  <td>{job.employment_type}</td>
                  <td>{job.salary}</td>
                  <td><span className="badge text-bg-light">{job.status}</span></td>
                  <td>{job.platform}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="automation-grid mt-3">
        <div className="panel">
          <h2>Generate Cover Letter</h2>
          <p className="muted-text">{selectedJob ? `${selectedJob.title} at ${selectedJob.company}` : "Select a job first."}</p>
          <div className="d-flex gap-2">
            <button className="btn btn-primary" disabled={isBusy || !selectedJob} onClick={handleCoverLetter}>
              <FaMagic /> Generate
            </button>
            <button className="btn btn-outline-secondary" disabled={!selectedJob} onClick={handlePlan}>Application Plan</button>
          </div>
          {coverLetter && (
            <div className="cover-letter-preview mt-3">
              <Markdown>{coverLetter.text}</Markdown>
            </div>
          )}
        </div>

        <div className="panel">
          <h2>Application Plan</h2>
          <ol>
            {applicationPlan.map((step) => <li key={step}>{step}</li>)}
          </ol>
        </div>
      </section>
    </>
  );
}
