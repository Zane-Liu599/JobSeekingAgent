import { FormEvent, PointerEvent, useEffect, useMemo, useState } from "react";
import Markdown from "react-markdown";
import {
  FaBriefcase,
  FaBuilding,
  FaExternalLinkAlt,
  FaFlag,
  FaMapMarkerAlt,
  FaMoneyBillWave,
  FaSearch,
} from "react-icons/fa";

import {
  JobLead,
  applyUrlForJob,
  fetchJobs,
  searchJobs,
  updateJobsStatus
} from "../api/jobAutomation";

const swipeThreshold = 110;
const exitAnimationMs = 240;
type DecisionStatus = "ignored" | "saved" | "ai_applying" | "closed";
type ExitDirection = "left" | "right" | "down" | "up";

export function JobSearchPage() {
  const [jobs, setJobs] = useState<JobLead[]>([]);
  const [form, setForm] = useState({ keywords: "Software Engineer", location: "Sydney" });
  const [message, setMessage] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [exitDirection, setExitDirection] = useState<ExitDirection | null>(null);
  const [isDeciding, setIsDeciding] = useState(false);

  const activeJob = jobs[activeIndex];
  const details = useMemo(
    () => [
      activeJob?.company,
      activeJob?.location,
      activeJob?.employment_type,
      activeJob?.salary,
      activeJob?.platform
    ].filter(Boolean),
    [activeJob]
  );
  const description = activeJob?.description || "No detailed description saved yet.";

  async function loadJobs() {
    setJobs(await fetchJobs());
    setActiveIndex(0);
  }

  useEffect(() => {
    loadJobs().catch((error: Error) => setMessage(error.message));
  }, []);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    setIsSearching(true);
    setMessage("");
    try {
      const result = await searchJobs(form);
      setJobs(result.jobs);
      setActiveIndex(0);
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  async function handleDecision(status: DecisionStatus, direction: ExitDirection) {
    if (!activeJob || isDeciding) return;
    setIsDeciding(true);
    setExitDirection(direction);
    await new Promise((resolve) => window.setTimeout(resolve, exitAnimationMs));

    if (!activeJob.id) {
      setActiveIndex((current) => current + 1);
      setExitDirection(null);
      setIsDeciding(false);
      return;
    }

    const labels = {
      ignored: "Ignored",
      saved: "Saved",
      ai_applying: "Sent to AI apply queue",
      closed: "Reported unavailable"
    };

    try {
      await updateJobsStatus([activeJob.id], status);
      setJobs((current) =>
        current.map((job) => (job.id === activeJob.id ? { ...job, status } : job))
      );
      setMessage(`${labels[status]} ${activeJob.title}.`);
      setActiveIndex((current) => current + 1);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally {
      setDragOffset({ x: 0, y: 0 });
      setDragStart(null);
      setExitDirection(null);
      setIsDeciding(false);
    }
  }

  function handlePointerDown(event: PointerEvent<HTMLElement>) {
    if (isDeciding) return;
    setDragStart({ x: event.clientX, y: event.clientY });
  }

  function handlePointerMove(event: PointerEvent<HTMLElement>) {
    if (!dragStart || isDeciding) return;
    setDragOffset({
      x: event.clientX - dragStart.x,
      y: event.clientY - dragStart.y
    });
  }

  function handlePointerEnd() {
    if (isDeciding) return;
    if (dragOffset.x <= -swipeThreshold) {
      void handleDecision("ignored", "left");
    } else if (dragOffset.x >= swipeThreshold) {
      void handleDecision("ai_applying", "right");
    } else if (dragOffset.y >= swipeThreshold) {
      void handleDecision("saved", "down");
    } else {
      setDragOffset({ x: 0, y: 0 });
      setDragStart(null);
    }
  }

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (!activeJob || isDeciding) return;
      const target = event.target as HTMLElement | null;
      if (target?.matches("input, textarea, select")) return;

      if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") {
        event.preventDefault();
        void handleDecision("ignored", "left");
      }
      if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") {
        event.preventDefault();
        void handleDecision("ai_applying", "right");
      }
      if (event.key === "ArrowDown" || event.key.toLowerCase() === "s") {
        event.preventDefault();
        void handleDecision("saved", "down");
      }
      if (event.key.toLowerCase() === "r") {
        event.preventDefault();
        void handleDecision("closed", "up");
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeJob, isDeciding]);

  return (
    <>
      <form className="panel search-panel" onSubmit={handleSearch}>
        <input className="form-control search-input" value={form.keywords} onChange={(event) => setForm({ ...form, keywords: event.target.value })} placeholder="Job title, skill, or keyword" />
        <input className="form-control" value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} placeholder="Location" />
        <button className="btn btn-primary" disabled={isSearching} type="submit">
          <FaSearch /> {isSearching ? "Loading" : "Search"}
        </button>
      </form>

      {message && <div className="alert alert-info mt-3">{message}</div>}

      <section className="job-review-panel mt-3">
        {activeJob ? (
          <>
            <article
              className={`review-job-card ${exitDirection ? `swipe-exit-${exitDirection}` : ""}`}
              onDoubleClick={() =>
                applyUrlForJob(activeJob) &&
                window.open(applyUrlForJob(activeJob), "_blank", "noopener,noreferrer")
              }
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerEnd}
              onPointerCancel={handlePointerEnd}
              style={{
                transform: `translate(${dragOffset.x}px, ${dragOffset.y}px) rotate(${dragOffset.x / 28}deg)`
              }}
            >
              <div className="review-card-main">
                <div className="review-card-left">
                  <div className="review-title-row">
                    <div>
                      <div className="review-card-topline">
                        <span>{activeJob.platform || "source"}</span>
                        <span>{activeJob.status}</span>
                      </div>
                      <h2>{activeJob.title}</h2>
                      <p className="review-company">{activeJob.company || "Company pending"}</p>
                    </div>
                  </div>

                  <div className="review-meta">
                    {details.map((item) => <span key={item}>{item}</span>)}
                  </div>

                  <div className="review-description">
                    <h3>About this job</h3>
                    <Markdown>{description}</Markdown>
                  </div>
                </div>

                <aside className="review-card-side">
                  <h3>Application</h3>
                  <div className="side-info-list">
                    <span><FaBuilding /> {activeJob.company || "Company pending"}</span>
                    <span><FaMapMarkerAlt /> {activeJob.location || "Location pending"}</span>
                    <span><FaBriefcase /> {activeJob.employment_type || "Type pending"}</span>
                    <span><FaMoneyBillWave /> {activeJob.salary || "Salary not listed"}</span>
                  </div>
                  <a className="official-link" href={applyUrlForJob(activeJob)} target="_blank" rel="noreferrer">
                    Open official application <FaExternalLinkAlt />
                  </a>
                </aside>
              </div>
            </article>

            <div className="swipe-hints">
              <button className="swipe-action ignore" disabled={isDeciding} onClick={() => void handleDecision("ignored", "left")}>
                <span>← Ignore</span>
              </button>
              <button className="swipe-action save" disabled={isDeciding} onClick={() => void handleDecision("saved", "down")}>
                <span>↓ Save</span>
              </button>
              <button className="swipe-action apply" disabled={isDeciding} onClick={() => void handleDecision("ai_applying", "right")}>
                <span>→ Apply with AI</span>
              </button>
            </div>

            <button className="report-unavailable" disabled={isDeciding} onClick={() => void handleDecision("closed", "up")}>
              <FaFlag />
              <span>Press R to report this job is no longer available</span>
            </button>
          </>
        ) : (
          <div className="empty-review-state">
            <h2>No more jobs to review</h2>
            <p>Search again or add more official-apply jobs from the crawler backend.</p>
          </div>
        )}
      </section>
    </>
  );
}
