"""Main CLI interface for simorc."""
from typing import Optional
from pathlib import Path

import click
import yaml


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
    project_path = Path(directory).resolve()
    click.echo(f"Initializing simorc project in: {project_path}")
    
    try:
        # Create directory structure
        directories = [
            "netlists",
            "testbenches", 
            "sweeps",
            "results"
        ]
        
        for dir_name in directories:
            dir_path = project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            click.echo(f"Created directory: {dir_name}/")
        
        # Create sim_setup.yaml template
        sim_setup_content = {
            "dut": {
                "netlist": "./netlists/dut.spice"
            },
            "testbenches": {
                "example": "./testbenches/example"
            },
            "sweeps": {
                "example_sweep": "./sweeps/example_sweep.yaml"
            }
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
            "parameters": {
                "param1": "1k",
                "param2": "1n"
            }
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
        
        click.echo("✓ Project initialized successfully!")
        click.echo("\nNext steps:")
        click.echo("1. Add your DUT netlist to netlists/")
        click.echo("2. Configure testbenches in testbenches/")
        click.echo("3. Define parameter sweeps in sweeps/")
        click.echo("4. Run 'simorc build <sweep_name>' to prepare simulations")
        
    except Exception as e:
        click.echo(f"Error initializing project: {e}", err=True)
        raise click.Abort()


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