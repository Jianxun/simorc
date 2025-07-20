"""Sweep generation functionality (Stage 1: Generate)."""
import csv
import itertools
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml
from jinja2 import Template

from .loader import load_sim_setup, load_sweep_config, load_testbench_config


def generate_parameter_combinations(parameters: Dict[str, List[Any]]) -> List[Dict[str, str]]:
    """Generate all combinations of parameter values.
    
    Args:
        parameters: Dictionary with parameter names as keys and lists of values
        
    Returns:
        List of dictionaries, each containing one parameter combination (all values as strings)
    """
    param_names = list(parameters.keys())
    param_values = list(parameters.values())
    
    combinations = []
    for values in itertools.product(*param_values):
        # Convert all values to strings
        combination = dict(zip(param_names, [str(v) for v in values]))
        combinations.append(combination)
    
    return combinations


def create_case_id(index: int) -> str:
    """Create a unique case ID from index.
    
    Args:
        index: Zero-based index of the parameter combination
        
    Returns:
        String case ID like "1", "2", "3", etc.
    """
    return str(index + 1)  # Start from 1 instead of 0


def generate_metadata_csv(sweep_name: str, combinations: List[Dict[str, str]], 
                         output_dir: Path) -> Path:
    """Generate metadata.csv file for tracking simulation cases.
    
    Args:
        sweep_name: Name of the sweep
        combinations: List of parameter combinations
        output_dir: Directory to write metadata.csv
        
    Returns:
        Path to the created metadata.csv file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "metadata.csv"
    
    if not combinations:
        raise ValueError("No parameter combinations provided")
    
    # Get parameter names from first combination
    param_names = list(combinations[0].keys())
    
    # CSV header: case_id, param1, param2, ..., status, result_file
    fieldnames = ["case_id"] + param_names + ["status", "result_file"]
    
    with open(metadata_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for index, combination in enumerate(combinations):
            case_id = create_case_id(index)
            row = {
                "case_id": case_id,
                "status": "pending",
                "result_file": f"case_{case_id}/case_{case_id}_results.raw"
            }
            # Add parameter values
            row.update(combination)
            writer.writerow(row)
    
    return metadata_path


def generate_case_directory(case_id: str, combination: Dict[str, str],
                           testbench_config: Dict[str, Any],
                           testbench_path: Path,
                           project_path: Path,
                           output_dir: Path) -> Path:
    """Generate a case directory with netlist for a single simulation case.
    
    Args:
        case_id: Unique identifier for this test case
        combination: Parameter values for this case
        testbench_config: Testbench configuration dictionary
        testbench_path: Path to testbench directory
        project_path: Path to project root
        output_dir: Directory to create case folder in
        
    Returns:
        Path to the created case directory
    """
    case_dir = output_dir / f"case_{case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and render Jinja2 template
    template_file = testbench_path / testbench_config['template']
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Create configuration context for template rendering
    config = {}
    
    # Add testbench parameters as base configuration
    config.update(testbench_config.get('parameters', {}))
    
    # Override with sweep parameter values
    config.update(combination)
    
    # Add special context variables
    config['root'] = str(project_path) + "/"  # Root path for includes
    config['case_id'] = case_id
    
    # Set output filename specific to this case
    base_filename = testbench_config.get('filename_raw', 'results.raw')
    config['filename_raw'] = f"case_{case_id}_{base_filename}"
    
    # Render the template
    try:
        netlist_content = template.render(config=config)
    except Exception as e:
        raise ValueError(f"Template rendering failed for case {case_id}: {e}")
    
    # Write rendered netlist to case directory
    netlist_path = case_dir / "netlist.spice"
    with open(netlist_path, 'w') as f:
        f.write(netlist_content)
    
    return case_dir


def generate_parametrized_test_file(sweep_name: str, combinations: List[Dict[str, str]],
                                   output_dir: Path) -> Path:
    """Generate a single parametrized pytest test file that reads from metadata.csv.
    
    Args:
        sweep_name: Name of the sweep
        combinations: List of parameter combinations (used only to determine param names)
        output_dir: Directory to write test file
        
    Returns:
        Path to the created test file
    """
    test_dir = output_dir / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_file_path = test_dir / f"test_{sweep_name}.py"
    
    # Extract parameter names from combinations
    param_names = list(combinations[0].keys()) if combinations else []
    
    # Load and render template
    template_path = Path(__file__).parent / "templates" / "parametrized_test.py.j2"
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Render the template with just parameter names - data comes from CSV
    test_content = template.render(
        sweep_name=sweep_name,
        param_names=param_names
    )
    
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    return test_file_path


def build_sweep(project_path: Path, sweep_name: str, force: bool = False) -> Dict[str, Any]:
    """Build/prepare a sweep for execution.
    
    Args:
        project_path: Path to the project directory
        sweep_name: Name of the sweep to build
        force: Whether to overwrite existing files
        
    Returns:
        Dictionary with build results and statistics
        
    Raises:
        FileNotFoundError: If required files are missing
        ValueError: If configuration is invalid
    """
    # Load project configuration
    sim_setup = load_sim_setup(project_path)
    
    # Verify sweep exists in configuration
    if sweep_name not in sim_setup.sweeps:
        available_sweeps = list(sim_setup.sweeps.keys())
        raise ValueError(f"Sweep '{sweep_name}' not found. Available sweeps: {available_sweeps}")
    
    # Load sweep configuration
    sweep_config_path = project_path / sim_setup.sweeps[sweep_name]
    sweep_config = load_sweep_config(sweep_config_path)
    
    # Load testbench configuration
    testbench_name = sweep_config.testbench
    if testbench_name not in sim_setup.testbenches:
        available_testbenches = list(sim_setup.testbenches.keys())
        raise ValueError(f"Testbench '{testbench_name}' not found. Available testbenches: {available_testbenches}")
    
    testbench_path = project_path / sim_setup.testbenches[testbench_name]
    testbench_config = load_testbench_config(testbench_path)
    
    # Create output directory
    output_dir = project_path / "results" / sweep_name
    if output_dir.exists() and not force:
        raise ValueError(f"Sweep output directory already exists: {output_dir}. Use --force to overwrite.")
    
    # Generate parameter combinations
    combinations = generate_parameter_combinations(sweep_config.parameters)
    
    if not combinations:
        raise ValueError("No parameter combinations generated. Check sweep configuration.")
    
    # Generate metadata.csv
    metadata_path = generate_metadata_csv(sweep_name, combinations, output_dir)
    
    # Generate case directories with netlists
    case_dirs = []
    
    for index, combination in enumerate(combinations):
        case_id = create_case_id(index)
        case_dir = generate_case_directory(
            case_id, combination, testbench_config.model_dump(),
            testbench_path, project_path, output_dir
        )
        case_dirs.append(case_dir)
    
    # Generate single parametrized test file
    test_file_path = generate_parametrized_test_file(sweep_name, combinations, output_dir)
    
    # Return build results
    return {
        "sweep_name": sweep_name,
        "output_dir": output_dir,
        "metadata_path": metadata_path,
        "test_file": test_file_path,
        "case_dirs": case_dirs,
        "num_cases": len(combinations),
        "testbench": testbench_name,
        "parameters": list(sweep_config.parameters.keys())
    }