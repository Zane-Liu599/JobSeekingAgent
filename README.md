# JobSeekingAgent

JobSeekingAgent is a cross-platform job seeking automation project for macOS, Windows, and Linux. It is designed as a Python-first local agent: a command-line tool handles scraping, matching, resume customization, application automation, and tracking; a web dashboard can be added later on top of the same core modules.

This shape is intentional. Job search automation often needs local browser sessions, user-controlled credentials, resumes stored on disk, and careful review before submitting applications. A local CLI core is easier to test, safer with secrets, and portable across operating systems. A web UI can still be added later for review queues, analytics, and manual approvals.

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

### 5. Run the CLI

```bash
python -m jobseeking_agent --help
python -m jobseeking_agent doctor
python -m jobseeking_agent db init
```

Or use the installed console command:

```bash
jobseek doctor
jobseek db init
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
- Add optional Streamlit or FastAPI dashboard.

## License

Add a license before publishing the repository publicly.
