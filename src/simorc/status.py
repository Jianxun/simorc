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
    result_file: Optional[str] = None
) -> None:
    """Update status for a single case using run_status.json file.
    
    Args:
        case_dir: Directory containing the test case files
        case_id: Unique identifier for the test case
        status: New status for the case
        error_message: Error message if status is FAILED
        result_file: Path to result file if status is COMPLETED
    """
    status_file = case_dir / "run_status.json"
    
    status_data = {
        "case_id": case_id,
        "status": status.value,
        "timestamp": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if error_message:
        status_data["error_message"] = error_message
    
    if result_file:
        status_data["result_file"] = result_file
    
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


def consolidate_metadata_csv(results_dir: Path) -> None:
    """Consolidate individual case statuses into metadata.csv.
    
    This implements the scatter-gather pattern for parallel execution:
    - Individual test functions write run_status.json files (scatter)
    - This function consolidates them into metadata.csv (gather)
    
    Args:
        results_dir: Directory containing metadata.csv and case subdirectories
    """
    metadata_file = results_dir / "metadata.csv"
    
    if not metadata_file.exists():
        print(f"Warning: metadata.csv not found at {metadata_file}")
        return
    
    # Read current metadata
    rows = []
    with open(metadata_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Collect status updates from case directories
    case_statuses = {}
    for status in collect_case_statuses(results_dir):
        case_id = status.get("case_id")
        if case_id:
            case_statuses[case_id] = status
    
    # Update rows with collected statuses
    for row in rows:
        case_id = row.get("case_id")
        if case_id in case_statuses:
            status_data = case_statuses[case_id]
            row["status"] = status_data.get("status", "pending")
            
            # Update error message if present
            if "error_message" in status_data:
                if "error_message" not in fieldnames:
                    fieldnames = list(fieldnames) + ["error_message"]
                row["error_message"] = status_data["error_message"]
    
    # Write updated metadata
    try:
        with open(metadata_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Consolidated status updates into {metadata_file}")
        
    except Exception as e:
        print(f"Warning: Failed to update metadata.csv: {e}")


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