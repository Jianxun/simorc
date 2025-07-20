"""Test the simorc build command functionality."""
import tempfile
import shutil
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from simorc.cli.main import cli


class TestBuildCommand:
    """Test the build command functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_project(self):
        """Create a minimal test project structure."""
        # Create directories
        (self.project_path / "netlists").mkdir()
        (self.project_path / "testbenches" / "ac").mkdir(parents=True)
        (self.project_path / "sweeps" / "test_sweep").mkdir(parents=True)
        (self.project_path / "results").mkdir()
        
        # Create DUT netlist
        netlist_content = """* RC Low-pass filter
.param R=1k C=1n
R1 in out {R}
C1 out gnd {C}
"""
        (self.project_path / "netlists" / "rc_lowpass.spice").write_text(netlist_content)
        
        # Create sim_setup.yaml
        sim_setup = {
            "dut": {"netlist": "./netlists/rc_lowpass.spice"},
            "testbenches": {"ac": "./testbenches/ac"},
            "sweeps": {"test_sweep": "./sweeps/test_sweep/sweep.yaml"}
        }
        with open(self.project_path / "sim_setup.yaml", 'w') as f:
            yaml.dump(sim_setup, f)
        
        # Create testbench config
        tb_config = {
            "template": "./tb_ac.spice.j2",
            "filename_raw": "ac_results.raw",
            "filename_log": "ac_sim.log",
            "parameters": {"R": "1k", "C": "1n"}
        }
        with open(self.project_path / "testbenches" / "ac" / "config.yaml", 'w') as f:
            yaml.dump(tb_config, f)
        
        # Create testbench template
        template_content = """* AC Analysis Testbench
.include {{ dut_netlist }}
Vin in gnd AC 1
.ac dec 10 1 1G
.control
ac dec 10 1 1G
wrdata {{ filename_raw }} frequency v(out)
.endc
.end
"""
        (self.project_path / "testbenches" / "ac" / "tb_ac.spice.j2").write_text(template_content)
        
        # Create sweep config
        sweep_config = {
            "testbench": "ac",
            "parameters": {
                "R": ["100", "1k", "10k"],
                "C": ["100p", "1n", "10n"]
            }
        }
        with open(self.project_path / "sweeps" / "test_sweep" / "sweep.yaml", 'w') as f:
            yaml.dump(sweep_config, f)
    
    def test_build_command_exists(self):
        """Test that build command is available."""
        result = self.runner.invoke(cli, ['build', '--help'])
        assert result.exit_code == 0
        assert "Build/prepare a sweep for execution" in result.output
    
    def test_build_requires_sweep_name(self):
        """Test that build command requires a sweep name."""
        result = self.runner.invoke(cli, ['build'])
        assert result.exit_code == 2
        assert "Missing argument" in result.output
    
    def test_build_invalid_sweep_name(self):
        """Test build with non-existent sweep name."""
        self.create_test_project()
        result = self.runner.invoke(cli, ['build', 'nonexistent', '-d', str(self.project_path)], 
                                   catch_exceptions=False)
        assert result.exit_code != 0
        assert "not found" in result.output or "Error" in result.output
    
    def test_build_valid_sweep(self):
        """Test build with a valid sweep configuration."""
        self.create_test_project()
        result = self.runner.invoke(cli, ['build', 'test_sweep', '-d', str(self.project_path)])
        assert result.exit_code == 0
        assert "Building sweep: test_sweep" in result.output
        
        # Check that metadata.csv was created
        metadata_path = self.project_path / "results" / "test_sweep" / "metadata.csv"
        assert metadata_path.exists()
        
        # Check that case directories were generated
        output_dir = self.project_path / "results" / "test_sweep"
        case_dirs = list(output_dir.glob("case_*"))
        assert len(case_dirs) == 9  # Should have 9 case directories (3x3 parameter combinations)
        
        # Check that single parametrized test file was generated
        test_dir = output_dir / "tests"
        assert test_dir.exists()
        test_files = list(test_dir.glob("test_*.py"))
        assert len(test_files) == 1  # Should have exactly one parametrized test file
        
        # Check that each case directory has a netlist
        for case_dir in case_dirs:
            netlist_path = case_dir / "netlist.spice"
            assert netlist_path.exists()
            assert netlist_path.stat().st_size > 0
    
    def test_build_creates_correct_metadata(self):
        """Test that build creates metadata.csv with correct structure."""
        self.create_test_project()
        result = self.runner.invoke(cli, ['build', 'test_sweep', '-d', str(self.project_path)], 
                                   catch_exceptions=False)
        assert result.exit_code == 0
        
        metadata_path = self.project_path / "results" / "test_sweep" / "metadata.csv"
        metadata_content = metadata_path.read_text()
        
        # Check header
        lines = metadata_content.strip().split('\n')
        header = lines[0]
        assert "case_id" in header
        assert "R" in header
        assert "C" in header
        assert "result_file" in header
        # Note: status column removed - now tracked in run_status.csv
        
        # Check data rows (9 cases)
        assert len(lines) == 10  # header + 9 data rows
        
        # Check that all cases have result_file paths
        for line in lines[1:]:
            columns = line.split(',')
            result_file = columns[3]  # result_file column
            assert "case_" in result_file
            assert "_results.raw" in result_file
    
    def test_build_force_flag(self):
        """Test build with --force flag overwrites existing files."""
        self.create_test_project()
        
        # First build
        result1 = self.runner.invoke(cli, ['build', 'test_sweep', '-d', str(self.project_path)])
        assert result1.exit_code == 0
        
        # Second build without force should fail/warn
        result2 = self.runner.invoke(cli, ['build', 'test_sweep', '-d', str(self.project_path)])
        assert result2.exit_code != 0
        assert "already exists" in result2.output
        
        # Third build with force should succeed
        result3 = self.runner.invoke(cli, ['build', 'test_sweep', '--force', '-d', str(self.project_path)])
        assert result3.exit_code == 0
        assert "Force mode enabled" in result3.output