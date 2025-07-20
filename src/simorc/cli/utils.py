"""CLI utilities for common patterns and error handling."""
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import click


def handle_cli_errors(func: Callable) -> Callable:
    """Decorator to standardize CLI error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            click.echo(f"❌ File not found: {e}", err=True)
            raise click.Abort()
        except ValueError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"❌ {func.__name__} failed: {e}", err=True)
            raise click.Abort()
    return wrapper


def success_message(message: str) -> None:
    """Display a standardized success message."""
    click.echo(f"✅ {message}")


def info_message(message: str) -> None:
    """Display a standardized info message."""
    click.echo(f"📋 {message}")


def step_message(message: str) -> None:
    """Display a step/action message."""
    click.echo(f"🔧 {message}")


def results_summary(title: str, results: Dict[str, Any]) -> None:
    """Display a formatted results summary."""
    click.echo(f"\n📊 {title}:")
    for key, value in results.items():
        if isinstance(value, (list, tuple)):
            value = ', '.join(str(v) for v in value)
        click.echo(f"  {key}: {value}")


def validate_project_path(directory: str) -> Path:
    """Validate and resolve project directory path."""
    project_path = Path(directory).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {project_path}")
    return project_path


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation before proceeding."""
    return click.confirm(message, default=default)


def format_validation_results(results: Dict[str, Any]) -> None:
    """Format and display validation results."""
    info_message("Validation Results:")
    click.echo(f"  sim_setup.yaml: {results['sim_setup']}")
    
    if results['testbenches']:
        click.echo("  Testbenches:")
        for name, status in results['testbenches'].items():
            click.echo(f"    {name}: {status}")
    
    if results['sweeps']:
        click.echo("  Sweeps:")
        for name, status in results['sweeps'].items():
            click.echo(f"    {name}: {status}")
    
    if results['errors']:
        click.echo("\n❌ Validation Errors:")
        for error in results['errors']:
            click.echo(f"  • {error}")
        raise click.Abort()
    else:
        success_message("All configurations are valid!")


def format_build_results(sweep_name: str, results: Dict[str, Any]) -> None:
    """Format and display build results."""
    success_message(f"Sweep '{sweep_name}' built successfully!")
    click.echo(f"📁 Output directory: {results['output_dir']}")
    click.echo(f"📋 Generated {results['num_cases']} test cases")
    click.echo(f"🧪 Testbench: {results['testbench']}")
    click.echo(f"⚙️  Parameters: {', '.join(results['parameters'])}")
    click.echo(f"📄 Metadata: {results['metadata_path'].name}")
    click.echo(f"🧪 Test file: {results['test_file'].name}")
    
    click.echo(f"\nNext steps:")
    click.echo(f"  Run 'simorc run {sweep_name}' to execute the sweep")