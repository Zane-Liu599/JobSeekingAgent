import typer
from rich.console import Console
from rich.table import Table

from jobseeking_agent import __version__
from jobseeking_agent.config import get_settings

app = typer.Typer(
    name="jobseek",
    help="Cross-platform job seeking automation agent.",
    no_args_is_help=True,
)
console = Console()


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
    console.print("Create .env from .env.example, add your resume, then run:")
    console.print("[bold]jobseek doctor[/bold]")
