"""CLI command implementations."""
from typing import Optional
from pathlib import Path
import yaml
import click

from ..loader import validate_project
from ..generator import build_sweep
from .utils import (
    handle_cli_errors, success_message, info_message, step_message,
    validate_project_path, format_validation_results, format_build_results
)


@handle_cli_errors
def init_command(directory: str) -> None:
    """Initialize a new simorc project structure."""
    project_path = Path(directory).resolve()
    click.echo(f"Initializing simorc project in: {project_path}")
    
    # Create directory structure
    directories = ["netlists", "testbenches", "sweeps", "results"]
    
    for dir_name in directories:
        dir_path = project_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"Created directory: {dir_name}/")
    
    # Create sim_setup.yaml template
    sim_setup_content = {
        "dut": {"netlist": "./netlists/dut.spice"},
        "testbenches": {"example": "./testbenches/example"},
        "sweeps": {"example_sweep": "./sweeps/example_sweep.yaml"}
    }
    
    sim_setup_path = project_path / "sim_setup.yaml"
    if not sim_setup_path.exists():
        with open(sim_setup_path, 'w') as f:
            yaml.dump(sim_setup_content, f, default_flow_style=False, sort_keys=False)
        click.echo("Created sim_setup.yaml")
    else:
        click.echo("sim_setup.yaml already exists, skipping")
    
    # Create example testbench structure
    example_tb_path = project_path / "testbenches" / "example"
    example_tb_path.mkdir(parents=True, exist_ok=True)
    
    tb_config_content = {
        "template": "./tb_example.spice.j2",
        "filename_raw": "results.raw",
        "filename_log": "sim.log",
        "parameters": {"param1": "1k", "param2": "1n"}
    }
    
    tb_config_path = example_tb_path / "config.yaml"
    if not tb_config_path.exists():
        with open(tb_config_path, 'w') as f:
            yaml.dump(tb_config_content, f, default_flow_style=False, sort_keys=False)
        click.echo("Created testbenches/example/config.yaml")
    
    # Create example sweep file
    sweep_content = {
        "testbench": "example",
        "parameters": {
            "param1": ["100", "1k", "10k"],
            "param2": ["100p", "1n", "10n"]
        }
    }
    
    sweep_path = project_path / "sweeps" / "example_sweep.yaml"
    if not sweep_path.exists():
        with open(sweep_path, 'w') as f:
            yaml.dump(sweep_content, f, default_flow_style=False, sort_keys=False)
        click.echo("Created sweeps/example_sweep.yaml")
    
    success_message("Project initialized successfully!")
    click.echo("\nNext steps:")
    click.echo("1. Add your DUT netlist to netlists/")
    click.echo("2. Configure testbenches in testbenches/")
    click.echo("3. Define parameter sweeps in sweeps/")
    click.echo("4. Run 'simorc build <sweep_name>' to prepare simulations")


@handle_cli_errors
def build_command(sweep_name: str, force: bool, directory: str) -> None:
    """Build/prepare a sweep for execution (Stage 1: Generation)."""
    project_path = validate_project_path(directory)
    click.echo(f"Building sweep: {sweep_name}")
    if force:
        info_message("Force mode enabled - will overwrite existing files")
    
    results = build_sweep(project_path, sweep_name, force)
    format_build_results(sweep_name, results)


@handle_cli_errors
def validate_command(directory: str) -> None:
    """Validate project configuration files."""
    project_path = validate_project_path(directory)
    click.echo(f"Validating project in: {project_path}")
    
    results = validate_project(project_path)
    format_validation_results(results)


def run_command(sweep_run_id: str, parallel: int) -> None:
    """Execute a prepared sweep (Stage 2: Execution)."""
    click.echo(f"Running sweep: {sweep_run_id}")
    click.echo(f"Using {parallel} parallel processes")
    # TODO: Implement sweep execution


def status_command() -> None:
    """Show status of all sweeps."""
    click.echo("Sweep status:")
    # TODO: Implement status reporting


def clean_command(sweep_run_id: Optional[str], all: bool) -> None:
    """Clean up sweep results to free space."""
    if all:
        click.echo("Cleaning all completed sweeps")
    elif sweep_run_id:
        click.echo(f"Cleaning sweep: {sweep_run_id}")
    else:
        click.echo("Interactive cleanup mode")
    # TODO: Implement cleanup functionality