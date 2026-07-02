# JobSeekingAgent

JobSeekingAgent is a cross-platform job seeking automation project for macOS, Windows, and Linux. It is designed as a local desktop agent: a Qt desktop app provides the main experience, while a command-line tool handles scraping, matching, resume customization, application automation, and tracking.

This shape is intentional. Job search automation often needs local browser sessions, user-controlled credentials, resumes stored on disk, and careful review before submitting applications. A local desktop app keeps sensitive data on the user's machine while still feeling like normal software.

## Planned Features

- Scrape job listings from supported job boards and company career pages.
- Normalize job data into one local schema.
- Match roles against skills, location, visa status, salary, and preferences.
- Generate application tasks with human approval before submission.
- Automate browser-based resume submission with Playwright.
- Track application status, notes, timestamps, and follow-up reminders.
- Export reports to CSV, JSON, or a future dashboard.

## Tech Stack

- Python 3.11+
- PySide6 / Qt for the desktop application
- Typer for the CLI
- Playwright for browser automation
- HTTPX and BeautifulSoup for lightweight scraping
- Pydantic and python-dotenv for configuration
- Pytest and Ruff for CI quality checks

## Project Layout

```text
.
├── .github/workflows/ci.yml
├── src/jobseeking_agent/
│   ├── __init__.py
│   ├── ai/
│   ├── application/
│   ├── cli.py
│   ├── config.py
│   ├── database/
│   ├── desktop/
│   │   ├── main_window.py
│   │   ├── pages/
│   │   ├── styles.py
│   │   └── widgets.py
│   ├── desktop_app.py
│   ├── search/
│   ├── tracker/
│   └── utils/
├── data/
│   ├── cover_letters/
│   ├── exports/
│   └── resumes/
├── tests/
│   └── test_config.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/JobSeekingAgent.git
cd JobSeekingAgent
```

### 2. Create a virtual environment

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
playwright install chromium
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env` locally. Do not commit `.env`.

### 5. Run the desktop app

```bash
jobseek desktop
```

### 6. Run the CLI

```bash
python -m jobseeking_agent --help
python -m jobseeking_agent doctor
python -m jobseeking_agent db init
```

Or use the installed console command:

```bash
jobseek doctor
jobseek db init
jobseek desktop
```

## MVP Workflow

The first version is designed around this local workflow:

```text
Enter keywords and location
        ↓
Search or import jobs
        ↓
Parse job details
        ↓
Score fit and generate application material
        ↓
Review manually
        ↓
Autofill/upload in browser
        ↓
Track application status in SQLite
```

Current starter commands:

```bash
jobseek db init
jobseek jobs add "Backend Engineer" "Example Company" --location Remote --url https://example.com/job
jobseek jobs list
jobseek ai cover-letter 1
jobseek desktop
```

## Desktop App

Run the local desktop app:

```bash
jobseek desktop
```

The first desktop version includes visible entry points for the full product flow:

- Dashboard
- Jobs
- AI
- Application
- Tracker
- Settings / Candidate Profile

The Settings page stores local profile data in `data/profile.json`. Resume uploads are copied
to `data/resumes/`, and cover letter templates are copied to `data/cover_letters/`. These local
files are ignored by Git.

An optional Streamlit dashboard is still available for quick experiments:

```bash
jobseek web
```

## Development

Run tests:

```bash
pytest
```

Run lint checks:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```

## Automation Safety Rules

- Keep real credentials in `.env` or a password manager, never in code.
- Review each generated application before submitting.
- Respect each website's robots.txt, terms of service, and rate limits.
- Prefer official APIs when available.
- Add per-site throttling and clear user-agent strings before running large crawls.
- Store resumes and cover letters locally or in encrypted storage.

## CI

GitHub Actions runs on pushes and pull requests. The workflow checks:

- Python installation on Linux, macOS, and Windows.
- Dependency installation from `requirements.txt`.
- Ruff linting.
- Pytest test suite.

The CI file is at `.github/workflows/ci.yml`.

## Roadmap

- Add job source adapters under `src/jobseeking_agent/sources/`.
- Add local storage with SQLite.
- Add matching and ranking pipeline.
- Add browser automation flows under `src/jobseeking_agent/apply/`.
- Add a manual approval queue.
- Package desktop releases for macOS and Windows.

## License

Add a license before publishing the repository publicly.
