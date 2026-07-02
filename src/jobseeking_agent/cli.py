import typer
from rich.console import Console
from rich.table import Table

from jobseeking_agent import __version__
from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter
from jobseeking_agent.config import get_settings
from jobseeking_agent.database.db import get_job, init_db, list_jobs, save_job
from jobseeking_agent.database.models import Job
from jobseeking_agent.utils.file_manager import ensure_local_directories

app = typer.Typer(
    name="jobseek",
    help="Cross-platform job seeking automation agent.",
    no_args_is_help=True,
)
db_app = typer.Typer(help="Manage the local SQLite database.")
jobs_app = typer.Typer(help="Add and review jobs.")
ai_app = typer.Typer(help="Generate AI-assisted application materials.")
console = Console()

app.add_typer(db_app, name="db")
app.add_typer(jobs_app, name="jobs")
app.add_typer(ai_app, name="ai")


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
            platform=platform,
            job_url=url,
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
    table.add_column("Platform")
    table.add_column("Status")

    for job in jobs:
        table.add_row(
            str(job.id or ""),
            job.title,
            job.company,
            job.location,
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

    path = generate_cover_letter(job)
    console.print(f"Generated cover letter draft: [bold]{path}[/bold]")
