"""CLI command implementations."""
from typing import Optional
from pathlib import Path
import yaml
import click

from ..loader import validate_project
from ..generator import build_sweep
from ..status import initialize_run_status_csv, consolidate_run_status_csv, get_sweep_progress
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


@handle_cli_errors
def run_command(sweep_run_id: str, parallel: int) -> None:
    """Execute a prepared sweep (Stage 2: Execution)."""
    import subprocess
    import time
    
    # Find sweep directory - try multiple locations
    search_paths = [
        Path(f"results/{sweep_run_id}"),  # results/sweep_name
        Path(sweep_run_id),               # direct path
        Path(f"results").glob(f"*{sweep_run_id}*")  # partial match in results
    ]
    
    sweep_dir = None
    for path in search_paths[:2]:  # Check first two directly
        if path.exists() and path.is_dir():
            sweep_dir = path
            break
    
    if not sweep_dir:  # Check glob results
        try:
            for path in search_paths[2]:
                if path.is_dir():
                    sweep_dir = path
                    break
        except:
            pass
    
    if not sweep_dir:
        click.echo(f"❌ Sweep directory not found: {sweep_run_id}")
        click.echo("Available sweeps:")
        if Path("results").exists():
            for path in Path("results").glob("*"):
                if path.is_dir():
                    click.echo(f"  - {path.name}")
        return
    
    click.echo(f"🚀 Running sweep: {sweep_dir}")
    click.echo(f"⚡ Using {parallel} parallel processes")
    
    # Validate sweep directory
    metadata_file = sweep_dir / "metadata.csv"
    test_file = sweep_dir / "tests" / f"test_{sweep_dir.name.split('_')[0]}_values.py"  # Simplified
    
    if not metadata_file.exists():
        click.echo(f"❌ metadata.csv not found in {sweep_dir}")
        return
    
    # Find test file - more robust search
    test_files = list((sweep_dir / "tests").glob("test_*.py")) if (sweep_dir / "tests").exists() else []
    if not test_files:
        click.echo(f"❌ No test files found in {sweep_dir}/tests/")
        return
    
    test_file = test_files[0]  # Use first test file found
    click.echo(f"📋 Test file: {test_file}")
    
    # Initialize run_status.csv
    initialize_run_status_csv(sweep_dir)
    
    # Build pytest command with relative path from sweep directory
    pytest_args = [
        "python", "-m", "pytest",
        str(test_file.relative_to(sweep_dir)),  # Relative path from sweep dir
        "-v", "-x"  # verbose, stop on first failure
    ]
    
    # Add parallel execution if requested
    if parallel > 1:
        pytest_args.extend(["-n", str(parallel)])
        click.echo(f"🔄 Parallel execution enabled with {parallel} workers")
    
    click.echo(f"⚙️  Command: {' '.join(pytest_args)}")
    
    # Execute pytest
    start_time = time.time()
    try:
        result = subprocess.run(
            pytest_args,
            cwd=sweep_dir,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        execution_time = time.time() - start_time
        
        # Consolidate status after execution
        click.echo("\n📊 Consolidating results...")
        consolidate_run_status_csv(sweep_dir)
        
        # Show summary
        progress = get_sweep_progress(sweep_dir)
        click.echo(f"\n✅ Execution completed in {execution_time:.1f}s")
        click.echo(f"📈 Results: {progress['completed']}/{progress['total']} completed")
        
        if progress['failed'] > 0:
            click.echo(f"❌ Failed: {progress['failed']} cases")
        
        if result.returncode == 0:
            success_message(f"Sweep '{sweep_run_id}' executed successfully!")
        else:
            click.echo(f"⚠️  Pytest exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        click.echo("\n⏹️  Execution interrupted by user")
        click.echo("📊 Consolidating partial results...")
        consolidate_run_status_csv(sweep_dir)
        
        progress = get_sweep_progress(sweep_dir)
        click.echo(f"📈 Partial results: {progress['completed']}/{progress['total']} completed")
        
    except Exception as e:
        click.echo(f"❌ Execution failed: {e}")
        return


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