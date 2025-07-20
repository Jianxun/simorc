"""Main CLI interface for simorc."""
from typing import Optional

import click


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
    click.echo(f"Initializing simorc project in: {directory}")
    # TODO: Implement project scaffolding


@cli.command()
@click.argument('sweep_name')
@click.option('--force', is_flag=True, 
              help='Overwrite existing sweep directory')
def build(sweep_name: str, force: bool) -> None:
    """Build/prepare a sweep for execution (Stage 1: Generation)."""
    click.echo(f"Building sweep: {sweep_name}")
    if force:
        click.echo("Force mode enabled - will overwrite existing files")
    # TODO: Implement sweep generation


@cli.command()
@click.argument('sweep_run_id')
@click.option('--parallel', '-j', type=int, default=1,
              help='Number of parallel processes (default: 1)')
def run(sweep_run_id: str, parallel: int) -> None:
    """Execute a prepared sweep (Stage 2: Execution)."""
    click.echo(f"Running sweep: {sweep_run_id}")
    click.echo(f"Using {parallel} parallel processes")
    # TODO: Implement sweep execution


@cli.command()
def status() -> None:
    """Show status of all sweeps."""
    click.echo("Sweep status:")
    # TODO: Implement status reporting


@cli.command()
@click.argument('sweep_run_id', required=False)
@click.option('--all', is_flag=True, help='Clean all completed sweeps')
def clean(sweep_run_id: Optional[str], all: bool) -> None:
    """Clean up sweep results to free space."""
    if all:
        click.echo("Cleaning all completed sweeps")
    elif sweep_run_id:
        click.echo(f"Cleaning sweep: {sweep_run_id}")
    else:
        click.echo("Interactive cleanup mode")
    # TODO: Implement cleanup functionality


if __name__ == '__main__':
    cli()