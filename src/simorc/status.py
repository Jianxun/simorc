"""Status tracking utilities for simorc test execution."""
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import time


class CaseStatus(Enum):
    """Status of a simulation case."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def update_case_status(
    case_dir: Path,
    case_id: str,
    status: CaseStatus,
    error_message: Optional[str] = None,
    result_file: Optional[str] = None,
    simulation_duration: Optional[float] = None
) -> None:
    """Update status for a single case using run_status.json file.
    
    Args:
        case_dir: Directory containing the test case files
        case_id: Unique identifier for the test case
        status: New status for the case
        error_message: Error message if status is FAILED
        result_file: Path to result file if status is COMPLETED
        simulation_duration: Simulation time in seconds
    """
    status_file = case_dir / "run_status.json"
    
    status_data = {
        "case_id": case_id,
        "status": status.value,
        "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if error_message:
        status_data["error_message"] = error_message
    
    if result_file:
        status_data["result_file"] = result_file
    
    if simulation_duration is not None:
        status_data["simulation_duration"] = simulation_duration
    
    # Atomic write
    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to update status for case {case_id}: {e}")


def read_case_status(case_dir: Path) -> Optional[Dict[str, Any]]:
    """Read status from run_status.json file.
    
    Args:
        case_dir: Directory containing the test case files
        
    Returns:
        Status data dictionary or None if file doesn't exist
    """
    status_file = case_dir / "run_status.json"
    
    if not status_file.exists():
        return None
    
    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to read status file {status_file}: {e}")
        return None


def collect_case_statuses(results_dir: Path) -> List[Dict[str, Any]]:
    """Collect status from all case directories.
    
    Args:
        results_dir: Directory containing all case subdirectories
        
    Returns:
        List of status dictionaries for all cases
    """
    statuses = []
    
    # Find all case directories
    for case_dir in results_dir.glob("case_*"):
        if case_dir.is_dir():
            status = read_case_status(case_dir)
            if status:
                statuses.append(status)
    
    # Sort by case_id
    statuses.sort(key=lambda x: int(x.get("case_id", 0)))
    
    return statuses


def consolidate_run_status_csv(results_dir: Path) -> None:
    """Consolidate individual case statuses into run_status.csv.
    
    This implements the scatter-gather pattern for parallel execution:
    - Individual test functions write run_status.json files (scatter)
    - This function consolidates them into run_status.csv (gather)
    
    The run_status.csv includes parameter columns from metadata.csv for immediate visibility.
    
    Args:
        results_dir: Directory containing metadata.csv and case subdirectories
    """
    metadata_file = results_dir / "metadata.csv"
    run_status_file = results_dir / "run_status.csv"
    
    if not metadata_file.exists():
        print(f"Warning: metadata.csv not found at {metadata_file}")
        return
    
    # Read metadata to get all case IDs and parameters
    metadata_rows = []
    with open(metadata_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        metadata_rows = list(reader)
    
    # Extract parameter columns (exclude case_id, status, result_file)
    param_columns = [col for col in fieldnames 
                    if col not in ['case_id', 'status', 'result_file']]
    
    # Collect status updates from case directories
    case_statuses = {}
    for status in collect_case_statuses(results_dir):
        case_id = status.get("case_id")
        if case_id:
            case_statuses[case_id] = status
    
    # Create run_status.csv with parameter columns and status info
    run_status_rows = []
    for metadata_row in metadata_rows:
        case_id = metadata_row.get("case_id")
        
        # Start with parameters from metadata
        run_status_row = {"case_id": case_id}
        for param in param_columns:
            run_status_row[param] = metadata_row.get(param, "")
        
        # Add status information
        if case_id in case_statuses:
            status_data = case_statuses[case_id]
            run_status_row.update({
                "status": status_data.get("status", "pending"),
                "timestamp_iso": status_data.get("timestamp_iso", ""),
                "simulation_duration": status_data.get("simulation_duration", ""),
                "result_file": status_data.get("result_file", ""),
                "error_message": status_data.get("error_message", "")
            })
        else:
            # Default status for cases without updates
            run_status_row.update({
                "status": "pending",
                "timestamp_iso": "",
                "simulation_duration": "",
                "result_file": "",
                "error_message": ""
            })
        
        run_status_rows.append(run_status_row)
    
    # Write run_status.csv with parameter columns first, then status columns
    try:
        status_columns = ["status", "timestamp_iso", "simulation_duration", "result_file", "error_message"]
        fieldnames = ["case_id"] + param_columns + status_columns
        
        with open(run_status_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(run_status_rows)
        
        print(f"✅ Consolidated status updates into {run_status_file}")
        
    except Exception as e:
        print(f"Warning: Failed to create run_status.csv: {e}")


def initialize_run_status_csv(results_dir: Path) -> None:
    """Initialize run_status.csv with all cases in pending state.
    
    This should be called at the start of a sweep run to create the initial
    status file with all cases marked as pending.
    
    Args:
        results_dir: Directory containing metadata.csv
    """
    metadata_file = results_dir / "metadata.csv"
    run_status_file = results_dir / "run_status.csv"
    
    if not metadata_file.exists():
        print(f"Warning: metadata.csv not found at {metadata_file}")
        return
    
    # Read metadata to get all case IDs and parameters
    with open(metadata_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        metadata_rows = list(reader)
    
    # Extract parameter columns (exclude case_id, status, result_file)
    param_columns = [col for col in fieldnames 
                    if col not in ['case_id', 'status', 'result_file']]
    
    # Create initial run_status.csv with all cases pending
    run_status_rows = []
    for metadata_row in metadata_rows:
        case_id = metadata_row.get("case_id")
        
        # Start with parameters from metadata
        run_status_row = {"case_id": case_id}
        for param in param_columns:
            run_status_row[param] = metadata_row.get(param, "")
        
        # Add pending status
        run_status_row.update({
            "status": "pending",
            "timestamp_iso": "",
            "simulation_duration": "",
            "result_file": "",
            "error_message": ""
        })
        
        run_status_rows.append(run_status_row)
    
    # Write initial run_status.csv
    try:
        status_columns = ["status", "timestamp_iso", "simulation_duration", "result_file", "error_message"]
        fieldnames = ["case_id"] + param_columns + status_columns
        
        with open(run_status_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(run_status_rows)
        
        print(f"✅ Initialized {run_status_file} with {len(run_status_rows)} pending cases")
        
    except Exception as e:
        print(f"Warning: Failed to initialize run_status.csv: {e}")


def get_sweep_progress(results_dir: Path) -> Dict[str, int]:
    """Get progress summary for a sweep.
    
    Args:
        results_dir: Directory containing case subdirectories
        
    Returns:
        Dictionary with counts for each status
    """
    statuses = collect_case_statuses(results_dir)
    
    progress = {
        "total": len(statuses),
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0
    }
    
    for status in statuses:
        status_value = status.get("status", "pending")
        if status_value in progress:
            progress[status_value] += 1
    
    return progress