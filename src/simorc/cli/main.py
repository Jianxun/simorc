"""Main CLI interface for simorc."""
from typing import Optional

import click

from .commands import (
    init_command, build_command, validate_command, run_command,
    status_command, clean_command
)


@click.group(invoke_without_command=True)
@click.version_option(version="0.0.0", prog_name="simorc")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Simorc: A simulation orchestration tool.
    
    Simorc helps manage and automate electronic circuit simulation workflows
    using a three-stage architecture: Generate, Execute, and Analyze.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option('--directory', '-d', default='.', 
              help='Directory to initialize (default: current directory)')
def init(directory: str) -> None:
    """Initialize a new simorc project structure."""
    init_command(directory)


@cli.command()
@click.argument('sweep_name')
@click.option('--force', is_flag=True, 
              help='Overwrite existing sweep directory')
@click.option('--directory', '-d', default='.', 
              help='Project directory (default: current directory)')
def build(sweep_name: str, force: bool, directory: str) -> None:
    """Build/prepare a sweep for execution (Stage 1: Generation)."""
    build_command(sweep_name, force, directory)


@cli.command()
@click.argument('sweep_run_id')
@click.option('--parallel', '-j', type=int, default=1,
              help='Number of parallel processes (default: 1)')
def run(sweep_run_id: str, parallel: int) -> None:
    """Execute a prepared sweep (Stage 2: Execution)."""
    run_command(sweep_run_id, parallel)


@cli.command()
def status() -> None:
    """Show status of all sweeps."""
    status_command()


@cli.command()
@click.option('--directory', '-d', default='.', 
              help='Project directory to validate (default: current directory)')
def validate(directory: str) -> None:
    """Validate project configuration files."""
    validate_command(directory)


@cli.command()
@click.argument('sweep_run_id', required=False)
@click.option('--all', is_flag=True, help='Clean all completed sweeps')
def clean(sweep_run_id: Optional[str], all: bool) -> None:
    """Clean up sweep results to free space."""
    clean_command(sweep_run_id, all)


if __name__ == '__main__':
    cli()