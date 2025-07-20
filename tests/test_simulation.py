"""Tests for simulation utilities."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from simorc.simulation import (
    run_ngspice_simulation, 
    SimulationError,
    validate_simulation_setup
)


def test_run_ngspice_simulation_success(tmp_path):
    """Test successful ngspice simulation execution."""
    # Setup test files
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "netlist.spice"
    netlist_path.write_text("test netlist content")
    
    raw_file = case_dir / "case_1_results.raw"
    
    # Mock subprocess.run to simulate successful ngspice execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create the expected raw file
        raw_file.write_text("test raw data")
        
        # Test execution
        result = run_ngspice_simulation(
            case_id="1",
            netlist_path=netlist_path,
            case_dir=case_dir,
            parameters={"R": "100", "C": "1n"}
        )
        
        assert result == raw_file
        mock_run.assert_called_once()


def test_run_ngspice_simulation_missing_netlist(tmp_path):
    """Test simulation with missing netlist file."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "missing.spice"
    
    with pytest.raises(SimulationError, match="Netlist not found"):
        run_ngspice_simulation(
            case_id="1",
            netlist_path=netlist_path,
            case_dir=case_dir,
            parameters={}
        )


def test_run_ngspice_simulation_ngspice_failure(tmp_path):
    """Test simulation with ngspice execution failure."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "netlist.spice"
    netlist_path.write_text("test netlist content")
    
    # Mock subprocess.run to simulate ngspice failure
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Simulation error"
        mock_run.return_value = mock_result
        
        with pytest.raises(SimulationError, match="ngspice failed"):
            run_ngspice_simulation(
                case_id="1",
                netlist_path=netlist_path,
                case_dir=case_dir,
                parameters={}
            )


def test_run_ngspice_simulation_timeout(tmp_path):
    """Test simulation timeout handling."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "netlist.spice"
    netlist_path.write_text("test netlist content")
    
    # Mock subprocess.run to simulate timeout
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("ngspice", 60)
        
        with pytest.raises(SimulationError, match="timeout"):
            run_ngspice_simulation(
                case_id="1",
                netlist_path=netlist_path,
                case_dir=case_dir,
                parameters={},
                timeout=1
            )


def test_validate_simulation_setup_success(tmp_path):
    """Test successful simulation setup validation."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "netlist.spice"
    netlist_path.write_text("test netlist content")
    
    # Mock ngspice version check
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        is_valid, error_msg = validate_simulation_setup(netlist_path, case_dir)
        
        assert is_valid is True
        assert error_msg == ""


def test_validate_simulation_setup_missing_netlist(tmp_path):
    """Test validation with missing netlist."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    netlist_path = case_dir / "missing.spice"
    
    is_valid, error_msg = validate_simulation_setup(netlist_path, case_dir)
    
    assert is_valid is False
    assert "Netlist not found" in error_msg