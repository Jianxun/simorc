"""Tests for configuration loading and validation."""

import tempfile
import pytest
from pathlib import Path
import yaml

from simorc.loader import (
    load_yaml,
    load_sim_setup,
    load_testbench_config,
    load_sweep_config,
    validate_project
)


class TestLoader:
    """Test configuration loading functions."""

    def test_load_yaml_valid_file(self):
        """Test loading valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"test": "data"}, f)
            temp_path = Path(f.name)
        
        try:
            data = load_yaml(temp_path)
            assert data == {"test": "data"}
        finally:
            temp_path.unlink()

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_yaml(Path("nonexistent.yaml"))

    def test_load_yaml_invalid_syntax(self):
        """Test loading YAML file with invalid syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: :")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML syntax"):
                load_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_load_sim_setup_valid(self):
        """Test loading valid sim_setup.yaml."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            config = {
                "dut": {"netlist": "./netlists/test.spice"},
                "testbenches": {"ac": "./testbenches/ac"},
                "sweeps": {"sweep1": "./sweeps/sweep1.yaml"}
            }
            
            with open(temp_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(config, f)
            
            sim_setup = load_sim_setup(temp_path)
            assert sim_setup.dut.netlist == Path("./netlists/test.spice")
            assert "ac" in sim_setup.testbenches

    def test_load_testbench_config_valid(self):
        """Test loading valid testbench config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tb_path = Path(temp_dir) / "testbench"
            tb_path.mkdir()
            
            config = {
                "template": "./tb.spice.j2",
                "parameters": {"R": "1k"}
            }
            
            with open(tb_path / "config.yaml", 'w') as f:
                yaml.dump(config, f)
            
            tb_config = load_testbench_config(tb_path)
            assert tb_config.template == Path("./tb.spice.j2")
            assert tb_config.parameters["R"] == "1k"

    def test_load_sweep_config_valid(self):
        """Test loading valid sweep config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                "testbench": "ac",
                "parameters": {"R": ["1k", "10k"], "C": ["1n", "10n"]}
            }
            yaml.dump(config, f)
            temp_path = Path(f.name)
        
        try:
            sweep_config = load_sweep_config(temp_path)
            assert sweep_config.testbench == "ac"
            assert len(sweep_config.parameters["R"]) == 2
        finally:
            temp_path.unlink()


class TestValidateProject:
    """Test project validation functionality."""

    def test_validate_project_success(self):
        """Test validating a complete valid project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sim_setup.yaml
            sim_setup = {
                "dut": {"netlist": "./netlists/test.spice"},
                "testbenches": {"ac": "./testbenches/ac"},
                "sweeps": {"sweep1": "./sweeps/sweep1.yaml"}
            }
            with open(project_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(sim_setup, f)
            
            # Create testbench
            tb_path = project_path / "testbenches" / "ac"
            tb_path.mkdir(parents=True)
            tb_config = {
                "template": "./tb.spice.j2",
                "parameters": {"R": "1k"}
            }
            with open(tb_path / "config.yaml", 'w') as f:
                yaml.dump(tb_config, f)
            
            # Create sweep
            sweeps_path = project_path / "sweeps"
            sweeps_path.mkdir()
            sweep_config = {
                "testbench": "ac",
                "parameters": {"R": ["1k", "10k"]}
            }
            with open(sweeps_path / "sweep1.yaml", 'w') as f:
                yaml.dump(sweep_config, f)
            
            # Validate project
            results = validate_project(project_path)
            
            assert results["sim_setup"] == "✓ Valid"
            assert results["testbenches"]["ac"] == "✓ Valid"
            assert results["sweeps"]["sweep1"] == "✓ Valid"
            assert len(results["errors"]) == 0

    def test_validate_project_with_errors(self):
        """Test validating project with configuration errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sim_setup.yaml
            sim_setup = {
                "dut": {"netlist": "./netlists/test.spice"},
                "testbenches": {"ac": "./testbenches/ac"},
                "sweeps": {"sweep1": "./sweeps/sweep1.yaml"}
            }
            with open(project_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(sim_setup, f)
            
            # Create invalid testbench (missing template)
            tb_path = project_path / "testbenches" / "ac"
            tb_path.mkdir(parents=True)
            tb_config = {"parameters": {"R": "1k"}}  # Missing required template
            with open(tb_path / "config.yaml", 'w') as f:
                yaml.dump(tb_config, f)
            
            # Create sweep with invalid testbench reference
            sweeps_path = project_path / "sweeps"
            sweeps_path.mkdir()
            sweep_config = {
                "testbench": "nonexistent",  # Invalid testbench reference
                "parameters": {"R": ["1k", "10k"]}
            }
            with open(sweeps_path / "sweep1.yaml", 'w') as f:
                yaml.dump(sweep_config, f)
            
            # Validate project
            results = validate_project(project_path)
            
            assert results["sim_setup"] == "✓ Valid"
            assert "✗ Error" in results["testbenches"]["ac"]
            assert "✗ Error" in results["sweeps"]["sweep1"]
            assert len(results["errors"]) >= 2