"""Tests for status tracking utilities."""
import pytest
import json
import csv
from pathlib import Path

from simorc.status import (
    update_case_status,
    read_case_status,
    collect_case_statuses,
    consolidate_run_status_csv,
    initialize_run_status_csv,
    get_sweep_progress,
    CaseStatus
)


def test_update_case_status(tmp_path):
    """Test updating case status with run_status.json."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    # Update status to running
    update_case_status(case_dir, "1", CaseStatus.RUNNING)
    
    status_file = case_dir / "run_status.json"
    assert status_file.exists()
    
    with open(status_file) as f:
        data = json.load(f)
    
    assert data["case_id"] == "1"
    assert data["status"] == "running"
    assert "timestamp_iso" in data
    # Note: removed unix timestamp, only ISO format now


def test_update_case_status_with_error(tmp_path):
    """Test updating case status with error message."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    update_case_status(
        case_dir, 
        "1", 
        CaseStatus.FAILED, 
        error_message="Simulation failed"
    )
    
    status_file = case_dir / "run_status.json"
    with open(status_file) as f:
        data = json.load(f)
    
    assert data["status"] == "failed"
    assert data["error_message"] == "Simulation failed"


def test_read_case_status(tmp_path):
    """Test reading case status from file."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    # Create status file
    status_data = {
        "case_id": "1",
        "status": "completed",
        "timestamp": 1234567890
    }
    
    status_file = case_dir / "run_status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f)
    
    # Read status
    result = read_case_status(case_dir)
    
    assert result == status_data


def test_read_case_status_missing_file(tmp_path):
    """Test reading status from non-existent file."""
    case_dir = tmp_path / "case_1"
    case_dir.mkdir()
    
    result = read_case_status(case_dir)
    assert result is None


def test_collect_case_statuses(tmp_path):
    """Test collecting statuses from multiple case directories."""
    # Create multiple case directories with status files
    for i in range(1, 4):
        case_dir = tmp_path / f"case_{i}"
        case_dir.mkdir()
        
        status_data = {
            "case_id": str(i),
            "status": "completed" if i % 2 else "failed"
        }
        
        status_file = case_dir / "run_status.json"
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    # Collect statuses
    statuses = collect_case_statuses(tmp_path)
    
    assert len(statuses) == 3
    assert statuses[0]["case_id"] == "1"
    assert statuses[1]["case_id"] == "2"
    assert statuses[2]["case_id"] == "3"


def test_consolidate_run_status_csv(tmp_path):
    """Test consolidating case statuses into run_status.csv."""
    # Create metadata.csv (read-only source of truth)
    metadata_file = tmp_path / "metadata.csv"
    with open(metadata_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "R", "C", "status", "result_file"])
        writer.writerow(["1", "100", "1n", "pending", "case_1.raw"])
        writer.writerow(["2", "1k", "10n", "pending", "case_2.raw"])
    
    # Create case directories with status files
    for i in range(1, 3):
        case_dir = tmp_path / f"case_{i}"
        case_dir.mkdir()
        
        status_data = {
            "case_id": str(i),
            "status": "completed",
            "result_file": f"case_{i}_results.raw"
        }
        
        status_file = case_dir / "run_status.json"
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    # Consolidate
    consolidate_run_status_csv(tmp_path)
    
    # Verify run_status.csv was created
    run_status_file = tmp_path / "run_status.csv"
    assert run_status_file.exists()
    
    with open(run_status_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]["case_id"] == "1"
    assert rows[0]["status"] == "completed"
    assert rows[1]["case_id"] == "2"
    assert rows[1]["status"] == "completed"
    
    # Verify metadata.csv was not modified
    with open(metadata_file) as f:
        reader = csv.DictReader(f)
        metadata_rows = list(reader)
    
    assert metadata_rows[0]["status"] == "pending"  # Unchanged
    assert metadata_rows[1]["status"] == "pending"  # Unchanged


def test_initialize_run_status_csv(tmp_path):
    """Test initializing run_status.csv from metadata.csv."""
    # Create metadata.csv
    metadata_file = tmp_path / "metadata.csv"
    with open(metadata_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "R", "C", "status", "result_file"])
        writer.writerow(["1", "100", "1n", "pending", "case_1.raw"])
        writer.writerow(["2", "1k", "10n", "pending", "case_2.raw"])
        writer.writerow(["3", "10k", "100p", "pending", "case_3.raw"])
    
    # Initialize
    initialize_run_status_csv(tmp_path)
    
    # Verify run_status.csv was created
    run_status_file = tmp_path / "run_status.csv"
    assert run_status_file.exists()
    
    with open(run_status_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 3
    for i, row in enumerate(rows, 1):
        assert row["case_id"] == str(i)
        assert row["status"] == "pending"
        assert row["error_message"] == ""


def test_get_sweep_progress(tmp_path):
    """Test getting sweep progress summary."""
    # Create case directories with different statuses
    statuses = ["completed", "failed", "running", "pending"]
    
    for i, status in enumerate(statuses, 1):
        case_dir = tmp_path / f"case_{i}"
        case_dir.mkdir()
        
        status_data = {
            "case_id": str(i),
            "status": status
        }
        
        status_file = case_dir / "run_status.json"
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    # Get progress
    progress = get_sweep_progress(tmp_path)
    
    assert progress["total"] == 4
    assert progress["completed"] == 1
    assert progress["failed"] == 1
    assert progress["running"] == 1
    assert progress["pending"] == 1