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
    title: "Structured job discovery",
    description:
      "Search organized job records, compare useful role details, and spend less time sorting through duplicate or incomplete listings.",
    icon: <FaSearch />
  },
  {
    title: "Fast role review",
    description:
      "Ignore, save, report unavailable roles, or move a promising job into your application workflow with simple card actions.",
    icon: <FaBookmark />
  },
  {
    title: "Official apply links",
    description:
      "Prioritize roles that include external application URLs, so you can continue on the company or employer application page.",
    icon: <FaBriefcase />
  },
  {
    title: "AI-assisted materials",
    description:
      "Use Gemini with your resume and optional templates to draft role-specific cover letters and application content for review.",
    icon: <FaMagic />
  },
  {
    title: "Application tracker",
    description:
      "Keep each opportunity in a clear status, from saved and applying through submitted, interviewing, offer, rejected, or closed.",
    icon: <FaClipboardList />
  },
  {
    title: "Profile and materials",
    description:
      "Manage your profile details, resume files, and reusable templates in one place before you start applying.",
    icon: <FaUserEdit />
  }
];

const platformItems = ["Public job records", "Company apply pages", "Clean role details", "Profile-aware matching"];

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
      "The current product focuses on finding structured job leads, preparing materials, opening apply links, and tracking your progress. You stay in control before anything is submitted."
  },
  {
    question: "Why use official apply links?",
    answer:
      "Company or employer application pages often include the most complete instructions and screening questions. Opening those pages directly helps you review exactly what will be submitted."
  },
  {
    question: "Can I review AI-generated material first?",
    answer:
      "Yes. AI output is treated as a draft. You can review, edit, and decide whether it is appropriate for the role before using it."
  },
  {
    question: "Where does job data come from?",
    answer:
      "The user-facing site reads structured records from the database. A separate admin workflow can collect, clean, and update public role information before it appears in search."
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
          <p className="landing-pill"><FaMagic /> AI-assisted job search</p>
          <h1>Find relevant jobs faster and prepare stronger applications with AI support.</h1>
          <p>
            JobSeekingAgent brings job discovery, resume context, cover letter drafting,
            and application tracking into one workflow, so you can focus on the roles
            that are actually worth your time.
          </p>
          <div className="landing-hero-actions">
            <Link className="btn btn-primary btn-lg" to="/register">Start for free</Link>
            <Link className="btn btn-light btn-lg" to="/login">Log in</Link>
          </div>
        </div>
      </section>

      <section className="company-proof-section" aria-label="Company role discovery">
        <div className="company-proof-copy">
          <p className="eyebrow">Company role discovery</p>
          <h2>Track public openings from companies people actively search for.</h2>
          <p>
            JobSeekingAgent is designed to organize publicly available role information,
            enrich it with cleaner details, and rank opportunities against your profile
            and search goals.
          </p>
          <p>
            Company names shown here are examples of roles users may search for; no
            partnership or endorsement is implied.
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
              <p className="preview-source">Public listing · Apply link available</p>
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
              <span>AI draft ready to review</span>
            </div>
            <div>
              <strong>Tracker</strong>
              <span>Submitted · Interviewing · Offer</span>
            </div>
          </div>
        </div>
        <div className="landing-section-copy">
          <p className="eyebrow">Built around the application flow</p>
          <h2>Move from job search to application prep without losing context.</h2>
          <p>
            Each saved role can keep its description, company information, apply link,
            notes, generated drafts, and application status connected in one place.
          </p>
        </div>
      </section>

      <section className="landing-section landing-automation">
        <div className="automation-copy">
          <p className="landing-pill subtle"><FaPlay /> Workflow preview</p>
          <h2>Review jobs quickly, then turn the right matches into application tasks.</h2>
          <p>
            Use card actions to decide what to ignore, save, or prepare next. When a role
            looks promising, keep its details available for AI drafting and follow-up tracking.
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
          <h2>Practical tools for a more organized job search.</h2>
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
          <p className="eyebrow">Cleaner matching</p>
          <h2>Organize public job information, then prioritize roles that better match your profile.</h2>
          <p>
            The platform is built to turn scattered job records into a cleaner feed with
            searchable details, apply links when available, and ranking signals based on
            your experience, preferences, and materials.
          </p>
        </div>
        <div className="landing-platform-list">
          {platformItems.map((item) => <span key={item}><FaDatabase /> {item}</span>)}
        </div>
      </section>

      <section className="landing-section landing-flow">
        <div className="landing-section-heading">
          <p className="eyebrow">How it works</p>
          <h2>A more controlled way to manage applications.</h2>
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
          <h2>What to know before creating an account.</h2>
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
        <h2>Start with a cleaner job search workspace.</h2>
        <p>Create an account, verify your email, and set up your profile when you are ready.</p>
        <Link className="btn btn-primary btn-lg" to="/register">Create account</Link>
      </section>

      <footer className="landing-footer">
        <div>
          <Link className="landing-brand" to="/">
            <span className="brand-mark">JSA</span>
            <span>JobSeekingAgent</span>
          </Link>
          <p>Job discovery, application materials, and progress tracking with AI-assisted drafting.</p>
        </div>
        <div className="landing-footer-links">
          <Link to="/login">Log in</Link>
          <Link to="/register">Create account</Link>
        </div>
      </footer>
    </main>
  );
}
