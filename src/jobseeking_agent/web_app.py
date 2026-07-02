from __future__ import annotations

from pathlib import Path

import streamlit as st

from jobseeking_agent import __version__
from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter
from jobseeking_agent.application.autofill import build_application_plan
from jobseeking_agent.config import get_settings
from jobseeking_agent.database.db import (
    get_job,
    init_db,
    job_status_counts,
    list_jobs,
    save_job,
    update_job_status,
)
from jobseeking_agent.database.models import Job
from jobseeking_agent.tracker.status_manager import VALID_STATUSES
from jobseeking_agent.utils.file_manager import ensure_local_directories

st.set_page_config(
    page_title="JobSeekingAgent",
    page_icon="JSA",
    layout="wide",
    initial_sidebar_state="expanded",
)


def bootstrap() -> None:
    ensure_local_directories()
    init_db()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --jsa-ink: #17202a;
            --jsa-muted: #68737d;
            --jsa-line: #dde3ea;
            --jsa-surface: #f7f9fb;
            --jsa-accent: #0f766e;
            --jsa-warm: #b45309;
        }
        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--jsa-ink);
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--jsa-line);
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stTabs"] button {
            min-height: 42px;
        }
        .jsa-band {
            border-top: 1px solid var(--jsa-line);
            border-bottom: 1px solid var(--jsa-line);
            background: var(--jsa-surface);
            padding: 14px 16px;
            margin: 8px 0 18px;
        }
        .jsa-status {
            color: var(--jsa-muted);
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def job_options() -> dict[str, int]:
    jobs = list_jobs(limit=200)
    return {
        f"#{job.id} {job.title} - {job.company}": int(job.id)
        for job in jobs
        if job.id is not None
    }


def jobs_table_data() -> list[dict[str, str | int | float | None]]:
    return [
        {
            "ID": job.id,
            "Title": job.title,
            "Company": job.company,
            "Location": job.location,
            "Platform": job.platform,
            "Status": job.status,
            "Score": job.match_score,
            "URL": job.job_url,
        }
        for job in list_jobs(limit=200)
    ]


def render_header() -> None:
    left, right = st.columns([0.72, 0.28], vertical_alignment="center")
    with left:
        st.title("JobSeekingAgent")
    with right:
        st.caption(f"v{__version__}")
        st.caption(str(init_db()))


def render_dashboard() -> None:
    counts = job_status_counts()
    jobs = list_jobs(limit=200)
    total = len(jobs)
    submitted = counts.get("submitted", 0)
    drafts = counts.get("draft", 0) + counts.get("found", 0)
    active = sum(counts.get(status, 0) for status in ("reviewing", "interviewing", "offer"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jobs", total)
    col2.metric("Drafts", drafts)
    col3.metric("Submitted", submitted)
    col4.metric("Active", active)

    st.markdown('<div class="jsa-band">Pipeline</div>', unsafe_allow_html=True)
    st.bar_chart(counts or {"found": 0})

    st.subheader("Recent Jobs")
    st.dataframe(jobs_table_data()[:10], use_container_width=True, hide_index=True)


def render_search() -> None:
    st.subheader("Job Search")
    source, manual = st.tabs(["Search Queue", "Manual Lead"])

    with source:
        col1, col2, col3 = st.columns([0.45, 0.35, 0.2])
        keywords = col1.text_input("Keywords", value="Software Engineer")
        location = col2.text_input("Location", value="Remote")
        platform = col3.selectbox("Platform", ["SEEK", "LinkedIn", "Indeed", "Company Site"])
        if st.button("Create Search", type="primary", use_container_width=True):
            st.session_state["last_search"] = {
                "keywords": keywords,
                "location": location,
                "platform": platform,
            }
            st.success(f"{platform}: {keywords} / {location}")

        st.dataframe(jobs_table_data(), use_container_width=True, hide_index=True)

    with manual:
        with st.form("manual_job_form", clear_on_submit=True):
            title = st.text_input("Title")
            company = st.text_input("Company")
            location = st.text_input("Location")
            platform = st.selectbox("Platform", ["manual", "seek", "linkedin", "indeed", "company"])
            url = st.text_input("URL")
            description = st.text_area("Description", height=180)
            submitted = st.form_submit_button("Save Job", type="primary", use_container_width=True)

        if submitted:
            if not title or not company:
                st.error("Title and company are required.")
            else:
                job_id = save_job(
                    Job(
                        title=title,
                        company=company,
                        location=location,
                        platform=platform,
                        job_url=url,
                        description=description,
                    )
                )
                st.success(f"Saved job #{job_id}")


def render_ai() -> None:
    st.subheader("AI Studio")
    options = job_options()
    if not options:
        st.info("Add a job first.")
        return

    selected = st.selectbox("Job", list(options.keys()))
    job = get_job(options[selected])
    if job is None:
        return

    col1, col2 = st.columns([0.45, 0.55])
    with col1:
        st.text_input("Resume", value=get_settings().resume_path)
        st.slider("Match Score", min_value=0, max_value=100, value=int(job.match_score or 0))
        if st.button("Generate Cover Letter", type="primary", use_container_width=True):
            path = generate_cover_letter(job)
            st.session_state["cover_letter_path"] = str(path)
            st.success(str(path))

    with col2:
        path_value = st.session_state.get("cover_letter_path")
        if path_value and Path(path_value).exists():
            st.text_area(
                "Cover Letter",
                value=Path(path_value).read_text(encoding="utf-8"),
                height=360,
            )
        else:
            st.text_area("Cover Letter", value="", height=360)


def render_application() -> None:
    st.subheader("Application")
    options = job_options()
    if not options:
        st.info("Add a job first.")
        return

    selected = st.selectbox("Job", list(options.keys()), key="application_job")
    job = get_job(options[selected])
    if job is None:
        return

    left, right = st.columns([0.42, 0.58])
    with left:
        st.text_input("Resume Path", value=get_settings().resume_path)
        st.text_input("Cover Letter Path", value="")
        st.checkbox("Manual Review", value=True, disabled=True)
        if st.button("Mark Reviewing", use_container_width=True):
            update_job_status(int(job.id), "reviewing")
            st.success("Status updated.")
        if st.button("Mark Submitted", type="primary", use_container_width=True):
            update_job_status(int(job.id), "submitted")
            st.success("Status updated.")

    with right:
        st.markdown('<div class="jsa-band">Browser Plan</div>', unsafe_allow_html=True)
        for index, step in enumerate(build_application_plan(job), start=1):
            st.checkbox(f"{index}. {step}", value=False)


def render_tracker() -> None:
    st.subheader("Tracker")
    data = jobs_table_data()
    st.dataframe(data, use_container_width=True, hide_index=True)

    options = job_options()
    if not options:
        return

    col1, col2, col3 = st.columns([0.45, 0.35, 0.2])
    selected = col1.selectbox("Job", list(options.keys()), key="tracker_job")
    status = col2.selectbox("Status", sorted(VALID_STATUSES))
    if col3.button("Update", type="primary", use_container_width=True):
        update_job_status(options[selected], status)
        st.success("Status updated.")


def render_settings() -> None:
    st.subheader("Settings")
    settings = get_settings()

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Environment", value=settings.app_env)
        st.text_input("Database URL", value=settings.database_url)
        st.text_input("Resume Path", value=settings.resume_path)
        st.text_input("Cover Letter Template", value=settings.cover_letter_template_path)
    with col2:
        st.toggle("Headless Browser", value=settings.browser_headless)
        st.number_input("Browser Slow Mo", value=settings.browser_slow_mo_ms, min_value=0)
        st.number_input("Crawl Delay", value=settings.crawl_delay_seconds, min_value=0)
        st.number_input("Max Jobs Per Source", value=settings.max_jobs_per_source, min_value=1)


def main() -> None:
    bootstrap()
    inject_styles()
    render_header()

    dashboard, search, ai, application, tracker, settings = st.tabs(
        ["Dashboard", "Search", "AI", "Application", "Tracker", "Settings"]
    )
    with dashboard:
        render_dashboard()
    with search:
        render_search()
    with ai:
        render_ai()
    with application:
        render_application()
    with tracker:
        render_tracker()
    with settings:
        render_settings()


if __name__ == "__main__":
    main()
