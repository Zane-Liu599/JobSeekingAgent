import { useEffect, useMemo, useState } from "react";
import { FaDownload, FaTrash } from "react-icons/fa";

import { JobLead, applyUrlForJob, deleteJobs, exportJobsExcel, fetchJobs, updateJobsStatus } from "../api/jobAutomation";
import { PageHeader } from "../components/PageHeader";

const statuses = ["found", "saved", "ignored", "ai_applying", "draft", "reviewing", "submitted", "interviewing", "offer", "rejected", "closed"];

export function SavedJobsPage() {
  const [jobs, setJobs] = useState<JobLead[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [status, setStatus] = useState("reviewing");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const selectedJob = useMemo(() => jobs.find((job) => job.id === selectedJobId), [jobs, selectedJobId]);

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

  function toggleSelected(jobId: number) {
    setSelectedIds((current) => current.includes(jobId) ? current.filter((id) => id !== jobId) : [...current, jobId]);
  }

  async function runAction(action: () => Promise<string>) {
    setIsBusy(true);
    setMessage("");
    try {
      setMessage(await action());
      await loadJobs();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleStatusUpdate() {
    await runAction(async () => {
      const ids = selectedIds.length ? selectedIds : selectedJob?.id ? [selectedJob.id] : [];
      const result = await updateJobsStatus(ids, status);
      return `Updated ${result.updated} job(s).`;
    });
  }

  async function handleDelete() {
    await runAction(async () => {
      const result = await deleteJobs(selectedIds);
      setSelectedIds([]);
      return `Deleted ${result.deleted} job(s).`;
    });
  }

  async function handleExport() {
    await runAction(async () => {
      const blob = await exportJobsExcel();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "jobs.xlsx";
      link.click();
      URL.revokeObjectURL(url);
      return "Exported jobs.xlsx.";
    });
  }

  return (
    <>
      <PageHeader
        eyebrow="Job Library"
        title="Saved Jobs"
        description="Review roles with official apply links, select multiple jobs, export the list, and open the company application page when needed."
      />

      {message && <div className="alert alert-info">{message}</div>}

      <section className="panel">
        <div className="jobs-toolbar">
          <h2>{jobs.length} Jobs</h2>
          <div className="toolbar-actions">
            <select className="form-select form-select-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <button className="btn btn-sm btn-outline-secondary" disabled={isBusy || (!selectedIds.length && !selectedJob)} onClick={handleStatusUpdate}>Mark</button>
            <button className="btn btn-sm btn-outline-success" disabled={isBusy} onClick={handleExport}><FaDownload /> Export</button>
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
                <th>Apply</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id ?? `${job.title}-${job.company}`} className={selectedJobId === job.id ? "table-active" : ""} onClick={() => job.id && setSelectedJobId(job.id)} onDoubleClick={() => applyUrlForJob(job) && window.open(applyUrlForJob(job), "_blank", "noopener,noreferrer")}>
                  <td><input type="checkbox" checked={job.id ? selectedIds.includes(job.id) : false} onChange={() => job.id && toggleSelected(job.id)} /></td>
                  <td>{job.title}</td>
                  <td>{job.company || "Unknown"}</td>
                  <td>{job.location}</td>
                  <td>{job.employment_type}</td>
                  <td>{job.salary}</td>
                  <td><span className="badge text-bg-light">{job.status}</span></td>
                  <td><a href={applyUrlForJob(job)} target="_blank" rel="noreferrer">{job.platform}</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
