"""Tests for simorc init command."""

import tempfile
import pytest
from pathlib import Path
import yaml
from click.testing import CliRunner

from simorc.cli.main import cli


class TestInitCommand:
    """Test init command functionality."""

    def test_init_creates_directory_structure(self):
        """Test that init command creates proper directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            result = runner.invoke(cli, ['init', '-d', temp_dir])
            
            assert result.exit_code == 0
            assert "✓ Project initialized successfully!" in result.output
            
            temp_path = Path(temp_dir)
            
            # Check directories were created
            expected_dirs = ["netlists", "testbenches", "sweeps", "results"]
            for dir_name in expected_dirs:
                assert (temp_path / dir_name).exists()
                assert (temp_path / dir_name).is_dir()

    def test_init_creates_sim_setup_yaml(self):
        """Test that init command creates sim_setup.yaml."""
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            result = runner.invoke(cli, ['init', '-d', temp_dir])
            
            assert result.exit_code == 0
            
            sim_setup_path = Path(temp_dir) / "sim_setup.yaml"
            assert sim_setup_path.exists()
            
            # Validate YAML content
            with open(sim_setup_path) as f:
                config = yaml.safe_load(f)
            
            assert "dut" in config
            assert "testbenches" in config
            assert "sweeps" in config
            assert config["dut"]["netlist"] == "./netlists/dut.spice"

    def test_init_creates_example_testbench(self):
        """Test that init command creates example testbench."""
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            result = runner.invoke(cli, ['init', '-d', temp_dir])
            
            assert result.exit_code == 0
            
            tb_config_path = Path(temp_dir) / "testbenches" / "example" / "config.yaml"
            assert tb_config_path.exists()
            
            # Validate testbench config
            with open(tb_config_path) as f:
                config = yaml.safe_load(f)
            
            assert "template" in config
            assert "parameters" in config
            assert config["template"] == "./tb_example.spice.j2"

    def test_init_creates_example_sweep(self):
        """Test that init command creates example sweep."""
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            result = runner.invoke(cli, ['init', '-d', temp_dir])
            
            assert result.exit_code == 0
            
            sweep_path = Path(temp_dir) / "sweeps" / "example_sweep.yaml"
            assert sweep_path.exists()
            
            # Validate sweep config
            with open(sweep_path) as f:
                config = yaml.safe_load(f)
            
            assert "testbench" in config
            assert "parameters" in config
            assert config["testbench"] == "example"

    def test_init_skips_existing_files(self):
        """Test that init command skips existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create existing sim_setup.yaml
            existing_config = {"existing": "config"}
            sim_setup_path = temp_path / "sim_setup.yaml"
            with open(sim_setup_path, 'w') as f:
                yaml.dump(existing_config, f)
            
            runner = CliRunner()
            result = runner.invoke(cli, ['init', '-d', temp_dir])
            
            assert result.exit_code == 0
            assert "sim_setup.yaml already exists, skipping" in result.output
            
            # Verify existing file wasn't overwritten
            with open(sim_setup_path) as f:
                config = yaml.safe_load(f)
            assert config == existing_config

    def test_init_default_directory(self):
        """Test that init command works with default directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                runner = CliRunner()
                result = runner.invoke(cli, ['init'])
                
                assert result.exit_code == 0
                assert "✓ Project initialized successfully!" in result.output
                
                # Check files were created in current directory
                assert Path("sim_setup.yaml").exists()
                assert Path("netlists").exists()
                
            finally:
                os.chdir(original_cwd)