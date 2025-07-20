"""Simulation execution utilities for simorc test functions."""
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple


class SimulationError(Exception):
    """Exception raised when simulation execution fails."""
    pass


def run_ngspice_simulation(
    case_id: str,
    netlist_path: Path,
    case_dir: Path,
    parameters: Dict[str, Any],
    timeout: int = 60
) -> Tuple[Path, float]:
    """Execute ngspice simulation for a test case.
    
    Args:
        case_id: Unique identifier for the test case
        netlist_path: Path to the SPICE netlist file
        case_dir: Directory containing the test case files
        parameters: Dictionary of simulation parameters
        timeout: Simulation timeout in seconds
        
    Returns:
        Tuple of (raw_file_path, simulation_duration_seconds)
        
    Raises:
        SimulationError: If simulation fails or results are invalid
    """
    import time
    
    print(f"Running simulation for case {case_id} with parameters: {parameters}")
    
    # Validate inputs
    if not netlist_path.exists():
        raise SimulationError(f"Netlist not found: {netlist_path}")
    
    if netlist_path.stat().st_size == 0:
        raise SimulationError(f"Empty netlist: {netlist_path}")
    
    start_time = time.time()
    
    try:
        # Run ngspice with the netlist
        result = subprocess.run(
            ['ngspice', '-b', str(netlist_path)],
            capture_output=True,
            text=True,
            cwd=case_dir,
            timeout=timeout
        )
        
        simulation_duration = time.time() - start_time
        
        # Check for simulation success
        if result.returncode != 0:
            raise SimulationError(f"ngspice failed for case {case_id}: {result.stderr}")
        
        # Verify output .raw file exists
        raw_file = case_dir / f"case_{case_id}_results.raw"
        if not raw_file.exists():
            raise SimulationError(f"Raw file not created for case {case_id}: {raw_file}")
        
        # Verify raw file has content
        if raw_file.stat().st_size == 0:
            raise SimulationError(f"Empty raw file for case {case_id}: {raw_file}")
        
        print(f"✅ Simulation completed for case {case_id} in {simulation_duration:.3f}s")
        return raw_file, simulation_duration
        
    except subprocess.TimeoutExpired:
        raise SimulationError(f"Simulation timeout for case {case_id}")
    except FileNotFoundError:
        raise SimulationError("ngspice not found in PATH")
    except Exception as e:
        raise SimulationError(f"Simulation error for case {case_id}: {e}")


def validate_simulation_setup(netlist_path: Path, case_dir: Path) -> Tuple[bool, str]:
    """Validate that simulation setup is correct.
    
    Args:
        netlist_path: Path to the SPICE netlist file
        case_dir: Directory containing the test case files
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check netlist exists and has content
        if not netlist_path.exists():
            return False, f"Netlist not found: {netlist_path}"
        
        if netlist_path.stat().st_size == 0:
            return False, f"Empty netlist: {netlist_path}"
        
        # Check case directory exists
        if not case_dir.exists():
            return False, f"Case directory not found: {case_dir}"
        
        # Check ngspice is available
        try:
            subprocess.run(['ngspice', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False, "ngspice not found in PATH or not working"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {e}"