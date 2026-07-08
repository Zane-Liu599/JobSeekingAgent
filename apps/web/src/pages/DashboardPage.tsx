import { FaClipboardCheck, FaFileAlt, FaSearch, FaUserEdit, FaWarehouse } from "react-icons/fa";

import { PageHeader } from "../components/PageHeader";
import { ServiceCard } from "../components/ServiceCard";

export function DashboardPage() {
  return (
    <>
      <PageHeader
        eyebrow="Job Seeking Platform"
        title="JobSeekingAgent"
        description="A focused workspace for finding roles, saving job leads, preparing application material, and tracking every application from discovery to offer."
      />

      <section className="hero-panel">
        <div>
          <span className="eyebrow">One place for the whole search</span>
          <h2>Search jobs, generate material, and keep your application pipeline organized.</h2>
        </div>
      </section>

      <section className="service-grid">
        <ServiceCard
          title="Find Jobs"
          description="Search supported platforms with keywords, location, and source, then save useful roles to your library."
          action="Start searching"
          icon={<FaSearch />}
        />
        <ServiceCard
          title="Saved Jobs"
          description="Review saved roles, open source postings, select multiple rows, export Excel, or remove duplicates."
          action="Review leads"
          icon={<FaWarehouse />}
        />
        <ServiceCard
          title="Application Materials"
          description="Generate cover letter drafts and review a safe application plan before submitting anything."
          action="Prepare material"
          icon={<FaFileAlt />}
        />
        <ServiceCard
          title="Tracker"
          description="Move jobs through found, reviewing, submitted, interviewing, offer, rejected, or closed."
          action="Update pipeline"
          icon={<FaClipboardCheck />}
        />
        <ServiceCard
          title="Profile"
          description="Edit personal information and upload the resume or optional cover letter template used for applications."
          action="Edit profile"
          icon={<FaUserEdit />}
        />
      </section>
    </>
  );
}
