import { FormEvent, useState } from "react";
import { FaFileAlt, FaFolderOpen, FaSave, FaUserEdit } from "react-icons/fa";

import { PageHeader } from "../components/PageHeader";

const initialProfile = {
  fullName: "",
  email: "",
  phone: "",
  location: "",
  targetRole: "",
  workRights: "",
  linkedin: "",
  portfolio: "",
  summary: "",
  template: ""
};

export function ProfilePage() {
  const [profile, setProfile] = useState(initialProfile);
  const [resumeName, setResumeName] = useState("");
  const [coverTemplateName, setCoverTemplateName] = useState("");
  const [message, setMessage] = useState("");

  function handleSave(event: FormEvent) {
    event.preventDefault();
    setMessage("Profile saved locally for this session.");
  }

  return (
    <>
      <PageHeader
        eyebrow="Candidate Profile"
        title="Personal Information"
        description="Manage the details and files used when generating application material and preparing job submissions."
      />

      <form className="profile-layout" onSubmit={handleSave}>
        <section className="panel">
          <div className="section-title">
            <FaUserEdit />
            <h2>Basic Details</h2>
          </div>
          <div className="form-grid">
            <input className="form-control" placeholder="Full name" value={profile.fullName} onChange={(event) => setProfile({ ...profile, fullName: event.target.value })} />
            <input className="form-control" placeholder="Email" value={profile.email} onChange={(event) => setProfile({ ...profile, email: event.target.value })} />
            <input className="form-control" placeholder="Phone" value={profile.phone} onChange={(event) => setProfile({ ...profile, phone: event.target.value })} />
            <input className="form-control" placeholder="Location" value={profile.location} onChange={(event) => setProfile({ ...profile, location: event.target.value })} />
            <input className="form-control" placeholder="Target role" value={profile.targetRole} onChange={(event) => setProfile({ ...profile, targetRole: event.target.value })} />
            <input className="form-control" placeholder="Work rights / visa" value={profile.workRights} onChange={(event) => setProfile({ ...profile, workRights: event.target.value })} />
            <input className="form-control" placeholder="LinkedIn" value={profile.linkedin} onChange={(event) => setProfile({ ...profile, linkedin: event.target.value })} />
            <input className="form-control" placeholder="Portfolio / GitHub" value={profile.portfolio} onChange={(event) => setProfile({ ...profile, portfolio: event.target.value })} />
          </div>
          <textarea className="form-control mt-3" rows={5} placeholder="Short professional summary" value={profile.summary} onChange={(event) => setProfile({ ...profile, summary: event.target.value })} />
        </section>

        <section className="panel">
          <div className="section-title">
            <FaFolderOpen />
            <h2>Application Files</h2>
          </div>
          <label className="upload-box">
            <FaFileAlt />
            <span>{resumeName || "Upload resume PDF or DOCX"}</span>
            <input type="file" accept=".pdf,.doc,.docx" onChange={(event) => setResumeName(event.target.files?.[0]?.name ?? "")} />
          </label>
          <label className="upload-box">
            <FaFileAlt />
            <span>{coverTemplateName || "Optional cover letter template"}</span>
            <input type="file" accept=".txt,.md,.pdf,.doc,.docx" onChange={(event) => setCoverTemplateName(event.target.files?.[0]?.name ?? "")} />
          </label>
          <textarea
            className="form-control mt-3"
            rows={8}
            placeholder="Optional reusable cover letter tone, achievements, or paragraphs"
            value={profile.template}
            onChange={(event) => setProfile({ ...profile, template: event.target.value })}
          />
          <button className="btn btn-primary mt-3" type="submit">
            <FaSave /> Save Profile
          </button>
          {message && <div className="alert alert-info mt-3">{message}</div>}
        </section>
      </form>
    </>
  );
}
