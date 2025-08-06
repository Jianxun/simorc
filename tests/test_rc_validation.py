"""Test configuration validation with example/rc project."""

import pytest
from pathlib import Path

from simorc.loader import validate_project


class TestRCProjectValidation:
    """Test validation of the example RC project."""

    def test_validate_rc_project(self):
        """Test that the example RC project validates correctly."""
        # Get the project root and example/rc path
        project_root = Path(__file__).parent.parent
        rc_project_path = project_root / "example" / "rc"
        
        if not rc_project_path.exists():
            pytest.skip("Example RC project not found")
        
        # Validate the RC project
        results = validate_project(rc_project_path)
        
        print(f"Validation results for {rc_project_path}:")
        print(f"  sim_setup: {results['sim_setup']}")
        print(f"  testbenches: {results['testbenches']}")
        print(f"  sweeps: {results['sweeps']}")
        
        if results['errors']:
            print("  Errors:")
            for error in results['errors']:
                print(f"    - {error}")
        
        # The RC project should validate successfully
        assert results['sim_setup'] == "✓ Valid"
        
        # Check testbenches
        for tb_name, status in results['testbenches'].items():
            if not status.startswith("✓"):
                print(f"Testbench {tb_name} validation failed: {status}")
        
        # Check sweeps  
        for sweep_name, status in results['sweeps'].items():
            if not status.startswith("✓"):
                print(f"Sweep {sweep_name} validation failed: {status}")
        
        # Print summary
        total_errors = len(results['errors'])
        if total_errors == 0:
            print("✓ All configurations are valid!")
        else:
            print(f"✗ Found {total_errors} validation errors")
            # Don't fail the test - let's see what the actual issues are
            pytest.fail(f"RC project validation failed with {total_errors} errors")