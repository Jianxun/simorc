"""Tests for error handling and user feedback."""

import tempfile
import pytest
from pathlib import Path
import yaml
from click.testing import CliRunner

from simorc.cli.main import cli


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_validate_missing_project(self):
        """Test validation of non-existent project."""
        runner = CliRunner()
        result = runner.invoke(cli, ['validate', '-d', '/nonexistent/path'])
        
        assert result.exit_code != 0
        assert "File not found" in result.output

    def test_validate_invalid_yaml_syntax(self):
        """Test validation with invalid YAML syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create invalid YAML
            with open(project_path / "sim_setup.yaml", 'w') as f:
                f.write("invalid: yaml: syntax: :")
            
            runner = CliRunner()
            result = runner.invoke(cli, ['validate', '-d', temp_dir])
            
            assert result.exit_code != 0
            assert "Invalid YAML syntax" in result.output

    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sim_setup.yaml missing required fields
            config = {"dut": {"netlist": "./test.spice"}}  # Missing testbenches and sweeps
            with open(project_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(config, f)
            
            runner = CliRunner()
            result = runner.invoke(cli, ['validate', '-d', temp_dir])
            
            assert result.exit_code != 0
            assert "Invalid sim_setup.yaml" in result.output

    def test_validate_missing_testbench_config(self):
        """Test validation when testbench config is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sim_setup.yaml
            config = {
                "dut": {"netlist": "./netlists/test.spice"},
                "testbenches": {"ac": "./testbenches/ac"},
                "sweeps": {"sweep1": "./sweeps/sweep1.yaml"}
            }
            with open(project_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(config, f)
            
            # Don't create the testbench directory
            
            runner = CliRunner()
            result = runner.invoke(cli, ['validate', '-d', temp_dir])
            
            assert result.exit_code != 0
            assert "Validation Errors" in result.output

    def test_init_error_handling(self):
        """Test init command error handling."""
        # Try to init in a location without write permissions
        runner = CliRunner()
        result = runner.invoke(cli, ['init', '-d', '/root/no_permission'])
        
        # Should handle permission errors gracefully
        assert result.exit_code != 0

    def test_validate_detailed_error_messages(self):
        """Test that validation provides detailed error messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sim_setup.yaml
            config = {
                "dut": {"netlist": "./netlists/test.spice"},
                "testbenches": {"ac": "./testbenches/ac"},
                "sweeps": {"sweep1": "./sweeps/sweep1.yaml"}
            }
            with open(project_path / "sim_setup.yaml", 'w') as f:
                yaml.dump(config, f)
            
            # Create testbench with invalid config (missing template)
            tb_path = project_path / "testbenches" / "ac"
            tb_path.mkdir(parents=True)
            tb_config = {"parameters": {"R": "1k"}}  # Missing required template
            with open(tb_path / "config.yaml", 'w') as f:
                yaml.dump(tb_config, f)
            
            # Create sweep with invalid testbench reference
            sweeps_path = project_path / "sweeps"
            sweeps_path.mkdir()
            sweep_config = {
                "testbench": "nonexistent",
                "parameters": {"R": ["1k", "10k"]}
            }
            with open(sweeps_path / "sweep1.yaml", 'w') as f:
                yaml.dump(sweep_config, f)
            
            runner = CliRunner()
            result = runner.invoke(cli, ['validate', '-d', temp_dir])
            
            assert result.exit_code != 0
            assert "Validation Errors" in result.output
            # Should provide specific error details
            assert "template" in result.output.lower() or "field required" in result.output.lower()

    def test_help_messages(self):
        """Test that help messages are informative."""
        runner = CliRunner()
        
        # Test main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "simulation orchestration" in result.output.lower()
        
        # Test init help
        result = runner.invoke(cli, ['init', '--help'])
        assert result.exit_code == 0
        assert "Initialize" in result.output
        
        # Test validate help
        result = runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert "Validate" in result.output