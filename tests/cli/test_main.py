"""Tests for the main CLI interface."""
import pytest
from click.testing import CliRunner

from simorc.cli.main import cli


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def setup_method(self):
        """Setup test runner."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test that CLI shows help when --help is used."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'simorc' in result.output.lower()
        assert 'Usage:' in result.output
    
    def test_cli_version(self):
        """Test that CLI shows version when --version is used."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '0.0.0' in result.output  # Current version from pyproject.toml
    
    def test_cli_no_args(self):
        """Test that CLI shows help when no arguments provided."""
        result = self.runner.invoke(cli, [])
        assert result.exit_code == 0
        assert 'Usage:' in result.output
    
    def test_cli_invalid_command(self):
        """Test that CLI handles invalid commands gracefully."""
        result = self.runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        assert 'No such command' in result.output


class TestCLISubcommands:
    """Test that CLI recognizes expected subcommands."""
    
    def setup_method(self):
        """Setup test runner."""
        self.runner = CliRunner()
    
    def test_init_command_exists(self):
        """Test that init subcommand is recognized."""
        result = self.runner.invoke(cli, ['init', '--help'])
        assert result.exit_code == 0
        assert 'init' in result.output.lower()
    
    def test_build_command_exists(self):
        """Test that build subcommand is recognized."""
        result = self.runner.invoke(cli, ['build', '--help'])
        assert result.exit_code == 0
        assert 'build' in result.output.lower()
    
    def test_run_command_exists(self):
        """Test that run subcommand is recognized."""
        result = self.runner.invoke(cli, ['run', '--help'])
        assert result.exit_code == 0
        assert 'run' in result.output.lower()
    
    def test_status_command_exists(self):
        """Test that status subcommand is recognized."""
        result = self.runner.invoke(cli, ['status', '--help'])
        assert result.exit_code == 0
        assert 'status' in result.output.lower()
    
    def test_clean_command_exists(self):
        """Test that clean subcommand is recognized."""
        result = self.runner.invoke(cli, ['clean', '--help'])
        assert result.exit_code == 0
        assert 'clean' in result.output.lower()