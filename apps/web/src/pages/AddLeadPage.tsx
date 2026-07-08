import { FormEvent, useState } from "react";

import { createJob } from "../api/jobAutomation";
import { PageHeader } from "../components/PageHeader";

const emptyLead = {
  title: "",
  company: "",
  location: "",
  employment_type: "",
  salary: "",
  platform: "manual",
  job_url: "",
  description: ""
};

export function AddLeadPage() {
  const [lead, setLead] = useState(emptyLead);
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const job = await createJob(lead);
    setLead(emptyLead);
    setMessage(`Saved ${job.title} at ${job.company}.`);
  }

  return (
    <>
      <PageHeader
        eyebrow="Manual Lead"
        title="Add Job Lead"
        description="Save jobs found outside supported platforms, including company career pages or recruiter messages."
      />

      <form className="panel" onSubmit={handleSubmit}>
        <div className="form-grid">
          <input className="form-control" required placeholder="Title" value={lead.title} onChange={(event) => setLead({ ...lead, title: event.target.value })} />
          <input className="form-control" required placeholder="Company" value={lead.company} onChange={(event) => setLead({ ...lead, company: event.target.value })} />
          <input className="form-control" placeholder="Location" value={lead.location} onChange={(event) => setLead({ ...lead, location: event.target.value })} />
          <input className="form-control" placeholder="Full-time, part-time, contract" value={lead.employment_type} onChange={(event) => setLead({ ...lead, employment_type: event.target.value })} />
          <input className="form-control" placeholder="Salary" value={lead.salary} onChange={(event) => setLead({ ...lead, salary: event.target.value })} />
          <input className="form-control" placeholder="Posting URL" value={lead.job_url} onChange={(event) => setLead({ ...lead, job_url: event.target.value })} />
        </div>
        <textarea className="form-control mt-3" rows={6} placeholder="Description or notes" value={lead.description} onChange={(event) => setLead({ ...lead, description: event.target.value })} />
        <button className="btn btn-primary mt-3" type="submit">Save Lead</button>
      </form>
      {message && <div className="alert alert-info mt-3">{message}</div>}
    </>
  );
}
