import { Link, Navigate } from "react-router-dom";
import {
  FaBell,
  FaBookmark,
  FaBriefcase,
  FaBuilding,
  FaCheckCircle,
  FaClipboardList,
  FaDatabase,
  FaEnvelopeOpenText,
  FaFileAlt,
  FaMagic,
  FaPlay,
  FaQuestionCircle,
  FaSearch,
  FaShieldAlt,
  FaUserEdit
} from "react-icons/fa";
import {
  SiAirbnb,
  SiAnthropic,
  SiAtlassian,
  SiCisco,
  SiDoordash,
  SiDropbox,
  SiFigma,
  SiInstacart,
  SiLyft,
  SiNetflix,
  SiNotion,
  SiPerplexity,
  SiPinterest,
  SiReddit,
  SiSnapchat,
  SiSpacex,
  SiSpotify,
  SiStripe,
  SiTripadvisor,
  SiUdemy
} from "react-icons/si";

import { getAuthToken } from "../api/auth";

const features = [
  {
    title: "Curated job discovery",
    description:
      "Search saved jobs from your database, review fresh leads, and focus on roles with useful detail instead of noisy listings.",
    icon: <FaSearch />
  },
  {
    title: "Swipe-style review",
    description:
      "Ignore, save, report unavailable, or send a role to AI apply flow with quick keyboard and card actions.",
    icon: <FaBookmark />
  },
  {
    title: "Official apply links",
    description:
      "Prioritize jobs with external application URLs so users can open the company application page directly.",
    icon: <FaBriefcase />
  },
  {
    title: "AI cover letters",
    description:
      "Use Gemini with your resume and optional cover letter template to draft company-specific application material.",
    icon: <FaMagic />
  },
  {
    title: "Application tracker",
    description:
      "Move opportunities through saved, applying, submitted, interviewing, offer, rejected, or closed states.",
    icon: <FaClipboardList />
  },
  {
    title: "Profile and materials",
    description:
      "Store personal details, resume files, and reusable templates that power future application workflows.",
    icon: <FaUserEdit />
  }
];

const platformItems = ["Company roles", "Official apply pages", "Fresh openings", "Profile-matched leads"];

const companyRows = [
  [
    { name: "Spotify", icon: <SiSpotify /> },
    { name: "OpenAI", icon: <FaBuilding /> },
    { name: "Airbnb", icon: <SiAirbnb /> },
    { name: "Stripe", icon: <SiStripe /> },
    { name: "Reddit", icon: <SiReddit /> },
    { name: "Netflix", icon: <SiNetflix /> },
    { name: "Anthropic", icon: <SiAnthropic /> },
    { name: "Figma", icon: <SiFigma /> },
    { name: "Cisco", icon: <SiCisco /> },
    { name: "SpaceX", icon: <SiSpacex /> },
    { name: "Notion", icon: <SiNotion /> },
    { name: "Snap", icon: <SiSnapchat /> }
  ],
  [
    { name: "Pinterest", icon: <SiPinterest /> },
    { name: "Atlassian", icon: <SiAtlassian /> },
    { name: "DoorDash", icon: <SiDoordash /> },
    { name: "Perplexity", icon: <SiPerplexity /> },
    { name: "Dropbox", icon: <SiDropbox /> },
    { name: "Instacart", icon: <SiInstacart /> },
    { name: "Lyft", icon: <SiLyft /> },
    { name: "Plaid", icon: <FaBuilding /> },
    { name: "DocuSign", icon: <FaBuilding /> },
    { name: "TripAdvisor", icon: <SiTripadvisor /> },
    { name: "Udemy", icon: <SiUdemy /> },
    { name: "Mercury", icon: <FaBuilding /> }
  ]
];

const faqItems = [
  {
    question: "Does it apply to jobs automatically?",
    answer:
      "The current flow focuses on finding structured job leads, opening official apply links, preparing materials, and tracking decisions. Fully automated application submission can be added later with review controls."
  },
  {
    question: "Why use official apply links?",
    answer:
      "Official company application pages usually capture richer screening context than one-click platform applications, and they give users more control over what is submitted."
  },
  {
    question: "Can I review AI-generated material first?",
    answer:
      "Yes. The platform is designed around review-first workflows: generate drafts from your resume and template, then decide what to send."
  },
  {
    question: "Where does job data come from?",
    answer:
      "The user-facing site reads clean records from the database. A separate admin/crawler flow can collect and update roles from major job platforms."
  }
];

export function LandingPage() {
  if (getAuthToken()) {
    return <Navigate to="/app" replace />;
  }

  return (
    <main className="landing-page">
      <nav className="landing-nav">
        <Link className="landing-brand" to="/">
          <span className="brand-mark">JSA</span>
          <span>JobSeekingAgent</span>
        </Link>
        <div className="landing-nav-actions">
          <Link className="btn btn-link landing-login" to="/login">Log in</Link>
          <Link className="btn btn-primary" to="/register">Create account</Link>
        </div>
      </nav>

      <section className="landing-hero">
        <div className="landing-hero-content">
          <p className="landing-pill"><FaMagic /> AI job search workspace</p>
          <h1>Find the jobs that fit you best, then use AI to prepare stronger applications.</h1>
          <p>
            JobSeekingAgent helps you collect better job leads, review them quickly,
            generate tailored application material, and keep every opportunity moving.
          </p>
          <div className="landing-hero-actions">
            <Link className="btn btn-primary btn-lg" to="/register">Start for free</Link>
            <Link className="btn btn-light btn-lg" to="/login">Log in</Link>
          </div>
        </div>
      </section>

      <section className="company-proof-section" aria-label="Pre-vetted company roles">
        <div className="company-proof-copy">
          <p className="eyebrow">Company-sourced openings</p>
          <h2>Verified company roles, matched to your search.</h2>
          <p>
            We verify company signals before roles reach your feed, then use our own matching
            logic to surface openings that better fit your profile and goals.
          </p>
        </div>
        <div className="company-marquee" aria-hidden="true">
          {companyRows.map((row, rowIndex) => (
            <div className={`company-marquee-row row-${rowIndex + 1}`} key={rowIndex}>
              {[...row, ...row].map((company, index) => (
                <span className="company-logo-pill" key={`${company.name}-${index}`}>
                  {company.icon}
                  {company.name}
                </span>
              ))}
            </div>
          ))}
        </div>
      </section>

      <section className="landing-section landing-product-preview" aria-label="Product preview">
        <div className="preview-board">
          <div className="preview-browser-bar">
            <span />
            <span />
            <span />
          </div>
          <div className="preview-panel preview-search">
            <span><FaSearch /> Software Engineer</span>
            <span>Sydney</span>
            <button type="button">Search</button>
          </div>
          <div className="preview-job-card">
            <div className="preview-status">Review</div>
            <div>
              <p className="preview-source">LinkedIn · Official apply</p>
              <h2>Backend Software Engineer</h2>
              <p>Cloud platform team · Full-time · Hybrid</p>
              <div className="preview-tags">
                <span>Python</span>
                <span>FastAPI</span>
                <span>PostgreSQL</span>
              </div>
            </div>
          </div>
          <div className="preview-actions">
            <span>← Ignore</span>
            <span>↓ Save</span>
            <span>→ Apply with AI</span>
          </div>
          <div className="preview-side-stack">
            <div>
              <strong>Cover letter</strong>
              <span>Gemini draft ready</span>
            </div>
            <div>
              <strong>Tracker</strong>
              <span>Submitted · Interviewing · Offer</span>
            </div>
          </div>
        </div>
        <div className="landing-section-copy">
          <p className="eyebrow">Built around the search flow</p>
          <h2>From discovery to application, every module supports the next step.</h2>
          <p>
            The platform keeps job data structured, makes review fast, and connects your
            profile materials to AI drafting when you are ready to apply.
          </p>
        </div>
      </section>

      <section className="landing-section landing-automation">
        <div className="automation-copy">
          <p className="landing-pill subtle"><FaPlay /> Workflow preview</p>
          <h2>Review jobs like cards, then turn good matches into application tasks.</h2>
          <p>
            Move from discovery to action without losing context. Every saved role can carry its
            description, official apply URL, generated material, and application status forward.
          </p>
        </div>
        <div className="automation-timeline">
          <span><FaSearch /> Collect roles</span>
          <span><FaBookmark /> Save matches</span>
          <span><FaMagic /> Draft material</span>
          <span><FaEnvelopeOpenText /> Open official apply</span>
        </div>
      </section>

      <section className="landing-section">
        <div className="landing-section-heading">
          <p className="eyebrow">What is included</p>
          <h2>A complete toolkit for active job seekers.</h2>
        </div>
        <div className="landing-feature-grid">
          {features.map((feature) => (
            <article className="landing-feature-card" key={feature.title}>
              <span className="landing-feature-icon">{feature.icon}</span>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-band">
        <div>
          <p className="eyebrow">Smarter job matching</p>
          <h2>We collect roles from many companies, then surface the ones that fit you best.</h2>
          <p>
            JobSeekingAgent gathers openings from company sources, cleans the role details,
            and uses our own matching logic to prioritize jobs that better align with your
            profile, materials, and search goals.
          </p>
        </div>
        <div className="landing-platform-list">
          {platformItems.map((item) => <span key={item}><FaDatabase /> {item}</span>)}
        </div>
      </section>

      <section className="landing-section landing-flow">
        <div className="landing-section-heading">
          <p className="eyebrow">How it works</p>
          <h2>A calmer way to handle applications.</h2>
        </div>
        <div className="landing-steps">
          <span><FaSearch /> Search roles</span>
          <span><FaCheckCircle /> Review fit</span>
          <span><FaFileAlt /> Generate materials</span>
          <span><FaEnvelopeOpenText /> Apply externally</span>
          <span><FaBell /> Track status</span>
          <span><FaShieldAlt /> Keep control</span>
        </div>
      </section>

      <section className="landing-section landing-faq">
        <div className="landing-section-heading">
          <p className="eyebrow">FAQ</p>
          <h2>Clear answers before you create an account.</h2>
        </div>
        <div className="landing-faq-list">
          {faqItems.map((item) => (
            <article key={item.question}>
              <h3><FaQuestionCircle /> {item.question}</h3>
              <p>{item.answer}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-cta">
        <h2>Ready to build your application pipeline?</h2>
        <p>Create an account, verify your email, and start setting up your profile.</p>
        <Link className="btn btn-primary btn-lg" to="/register">Create account</Link>
      </section>

      <footer className="landing-footer">
        <div>
          <Link className="landing-brand" to="/">
            <span className="brand-mark">JSA</span>
            <span>JobSeekingAgent</span>
          </Link>
          <p>AI-assisted job discovery, materials, and application tracking.</p>
        </div>
        <div className="landing-footer-links">
          <Link to="/login">Log in</Link>
          <Link to="/register">Create account</Link>
        </div>
      </footer>
    </main>
  );
}
