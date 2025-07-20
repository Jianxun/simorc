"""Configuration loading and validation utilities."""

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import ValidationError

from .config import SimSetupConfig, TestbenchConfigModel, SweepConfig


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file and return parsed content."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax in {file_path}: {e}")


def load_sim_setup(project_path: Path) -> SimSetupConfig:
    """Load and validate main simulation setup configuration."""
    config_path = project_path / "sim_setup.yaml"
    data = load_yaml(config_path)
    
    try:
        return SimSetupConfig(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid sim_setup.yaml: {e}")


def load_testbench_config(testbench_path: Path) -> TestbenchConfigModel:
    """Load and validate testbench configuration."""
    config_path = testbench_path / "config.yaml"
    data = load_yaml(config_path)
    
    try:
        return TestbenchConfigModel(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid testbench config in {testbench_path}: {e}")


def load_sweep_config(sweep_path: Path) -> SweepConfig:
    """Load and validate sweep configuration."""
    data = load_yaml(sweep_path)
    
    try:
        return SweepConfig(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid sweep config in {sweep_path}: {e}")


def validate_project(project_path: Path) -> Dict[str, Any]:
    """Validate entire project configuration and return summary."""
    project_path = Path(project_path).resolve()
    
    # Load main configuration
    sim_setup = load_sim_setup(project_path)
    
    validation_results = {
        "project_path": str(project_path),
        "sim_setup": "✓ Valid",
        "testbenches": {},
        "sweeps": {},
        "errors": []
    }
    
    # Validate testbenches
    for tb_name, tb_rel_path in sim_setup.testbenches.items():
        tb_path = project_path / tb_rel_path
        try:
            load_testbench_config(tb_path)
            validation_results["testbenches"][tb_name] = "✓ Valid"
        except Exception as e:
            validation_results["testbenches"][tb_name] = f"✗ Error: {e}"
            validation_results["errors"].append(f"Testbench {tb_name}: {e}")
    
    # Validate sweeps
    for sweep_name, sweep_rel_path in sim_setup.sweeps.items():
        sweep_path = project_path / sweep_rel_path
        try:
            sweep_config = load_sweep_config(sweep_path)
            
            # Check if referenced testbench exists
            if sweep_config.testbench not in sim_setup.testbenches:
                raise ValueError(f"References non-existent testbench: {sweep_config.testbench}")
            
            validation_results["sweeps"][sweep_name] = "✓ Valid"
        except Exception as e:
            validation_results["sweeps"][sweep_name] = f"✗ Error: {e}"
            validation_results["errors"].append(f"Sweep {sweep_name}: {e}")
    
    return validation_results