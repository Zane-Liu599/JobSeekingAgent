import typer
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.table import Table

from jobseeking_agent import __version__
from jobseeking_agent.config import get_settings
from jobseeking_agent.db import Job
from jobseeking_agent.search.keyword_search import build_search_query
from jobseeking_agent.search.safe_search import browser_storage_state_path, platform_search_url
from jobseeking_agent.services import get_job, init_db, list_jobs, save_job
from jobseeking_agent.services.cover_letter_service import generate_cover_letter_for_job
from jobseeking_agent.utils.file_manager import ensure_local_directories

app = typer.Typer(
    name="jobseek",
    help="Cross-platform job seeking automation agent.",
    no_args_is_help=True,
)
db_app = typer.Typer(help="Manage the local SQLite database.")
jobs_app = typer.Typer(help="Add and review jobs.")
ai_app = typer.Typer(help="Generate AI-assisted application materials.")
crawler_app = typer.Typer(help="Prepare logged-in crawler browser sessions.")
console = Console()

app.add_typer(db_app, name="db")
app.add_typer(jobs_app, name="jobs")
app.add_typer(ai_app, name="ai")
app.add_typer(crawler_app, name="crawler")


@app.command()
def doctor() -> None:
    """Show local configuration and environment readiness."""
    settings = get_settings()

    table = Table(title="JobSeekingAgent Doctor")
    table.add_column("Setting")
    table.add_column("Value")

    table.add_row("Version", __version__)
    table.add_row("Environment", settings.app_env)
    table.add_row("Database", settings.database_url)
    table.add_row("Headless Browser", str(settings.browser_headless))
    table.add_row("Browser Storage Dir", settings.browser_storage_dir)
    table.add_row("Max Jobs Per Source", str(settings.max_jobs_per_source))
    table.add_row("Resume Path", settings.resume_path)

    console.print(table)


@app.command()
def init() -> None:
    """Print next setup steps for a fresh local workspace."""
    ensure_local_directories()
    console.print("Create .env from .env.example, add your resume, then run:")
    console.print("[bold]jobseek db init[/bold]")
    console.print("[bold]jobseek doctor[/bold]")


@app.command()
def desktop() -> None:
    """Deprecated: the project now uses the React web frontend."""
    console.print("Desktop mode has been removed. Use Docker Compose and open http://localhost:8080.")


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8080, "--port"),
) -> None:
    """Deprecated: the web app is served by React + Nginx in Docker Compose."""
    console.print(
        "React web mode is served by Docker Compose. Run: "
        "docker compose --env-file .env -f infra/docker-compose.yml up -d --build"
    )
    console.print(f"Requested local address was {host}:{port}; default platform URL is http://localhost:8080.")


@crawler_app.command("login")
def save_browser_login(
    platform: str = typer.Argument(..., help="seek, linkedin, or indeed"),
    keywords: str = typer.Option("software engineer", "--keywords", "-k"),
    location: str = typer.Option("Sydney", "--location", "-l"),
    browser: str = typer.Option(
        "chrome",
        "--browser",
        "-b",
        help="Use chrome, msedge, or chromium for the login window.",
    ),
) -> None:
    """Open a real browser, let you log in, then save Playwright storage state."""
    settings = get_settings()
    query = build_search_query(keywords, location, platform)
    storage_path = browser_storage_state_path(query.platform, settings.browser_storage_dir)
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    url = platform_search_url(query)

    console.print(f"Opening {query.platform} in a real browser:")
    console.print(f"[bold]{url}[/bold]")
    console.print("Log in normally. Do not enter credentials into this terminal.")

    with sync_playwright() as playwright:
        launch_kwargs = {
            "headless": False,
            "slow_mo": settings.browser_slow_mo_ms,
        }
        if browser.lower() != "chromium":
            launch_kwargs["channel"] = browser.lower()
        try:
            browser_instance = playwright.chromium.launch(**launch_kwargs)
        except Exception as exc:
            if browser.lower() == "chromium":
                raise
            console.print(
                f"[yellow]Could not open {browser}; falling back to Playwright Chromium.[/yellow]"
            )
            console.print(f"[dim]{exc}[/dim]")
            browser_instance = playwright.chromium.launch(
                headless=False,
                slow_mo=settings.browser_slow_mo_ms,
            )
        context = browser_instance.new_context(user_agent=settings.user_agent)
        page = context.new_page()
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=settings.request_timeout_seconds * 1000,
        )
        console.input("Finish login in the browser window, then press Enter here...")
        context.storage_state(path=str(storage_path))
        browser_instance.close()

    console.print(f"Saved {query.platform} login state to [bold]{storage_path}[/bold]")


@db_app.command("init")
def init_database() -> None:
    """Create local SQLite tables."""
    ensure_local_directories()
    path = init_db()
    console.print(f"Initialized database at [bold]{path}[/bold]")


@jobs_app.command("add")
def add_job(
    title: str,
    company: str,
    location: str = typer.Option("", "--location", "-l"),
    employment_type: str = typer.Option("", "--type", "-t"),
    salary: str = typer.Option("", "--salary", "-s"),
    platform: str = typer.Option("manual", "--platform", "-p"),
    url: str = typer.Option("", "--url", "-u"),
    description: str = typer.Option("", "--description", "-d"),
) -> None:
    """Add or update a job lead."""
    init_db()
    job_id = save_job(
        Job(
            title=title,
            company=company,
            location=location,
            employment_type=employment_type,
            salary=salary,
            platform=platform,
            job_url=url,
            official_apply_url="",
            description=description,
        )
    )
    console.print(f"Saved job [bold]#{job_id}[/bold]: {title} at {company}")


@jobs_app.command("list")
def show_jobs(limit: int = typer.Option(20, "--limit", "-n", min=1, max=200)) -> None:
    """List saved job leads."""
    init_db()
    jobs = list_jobs(limit=limit)

    table = Table(title="Saved Jobs")
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Type")
    table.add_column("Salary")
    table.add_column("Platform")
    table.add_column("Status")

    for job in jobs:
        table.add_row(
            str(job.id or ""),
            job.title,
            job.company,
            job.location,
            job.employment_type,
            job.salary,
            job.platform,
            job.status,
        )

    console.print(table)


@ai_app.command("cover-letter")
def cover_letter(job_id: int) -> None:
    """Generate a local cover letter draft for a saved job."""
    init_db()
    job = get_job(job_id)
    if job is None:
        raise typer.BadParameter(f"No job found with id {job_id}")

    path = generate_cover_letter_for_job(job)
    console.print(f"Generated cover letter draft: [bold]{path}[/bold]")
