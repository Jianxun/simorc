# Data Artifacts & Schemas

## Overview

The simorc workflow communicates between stages through well-defined data artifacts. This ensures loose coupling between stages while maintaining data integrity.

## `metadata.csv` Schema

The `metadata.csv` file acts as the single source of truth for parameter combinations and case tracking:

- `case_id`: Unique integer identifier (1, 2, 3...)
- `result_file`: Relative path to the result file (e.g., `case_1/case_1_results.raw`)
- One column for each swept parameter (e.g., `R`, `C`, `vdda`, `temp`)

**Note**: Status tracking has been moved to `run_status.csv` for better separation of concerns.

### Example

```csv
case_id,result_file,R,C,vdda,temp
1,case_1/case_1_results.raw,1000,1e-12,3.3,25
2,case_2/case_2_results.raw,2000,1e-12,3.3,25
3,case_3/case_3_results.raw,1000,2e-12,3.3,25
```

## `run_status.csv` Schema

The `run_status.csv` file tracks execution status and timing:

- `case_id`: Links to metadata.csv
- Parameter columns (duplicated for convenience)
- `status`: Execution state (`pending`, `completed`, `failed`)
- `timestamp_iso`: ISO timestamp of completion
- `simulation_duration`: Execution time in seconds
- `result_file`: Path to result file
- `error_message`: Error details for failed cases

### Example

```csv
case_id,R,C,vdda,temp,status,timestamp_iso,simulation_duration,result_file,error_message
1,1000,1e-12,3.3,25,completed,2025-01-15T10:30:45Z,2.34,case_1/case_1_results.raw,
2,2000,1e-12,3.3,25,failed,2025-01-15T10:31:02Z,0.12,case_2/case_2_results.raw,Convergence error
3,1000,2e-12,3.3,25,pending,,,,
```

## Individual Case Status (`case_X/run_status.json`)

Each case directory contains an individual status file for parallel execution safety:

```json
{
  "case_id": 1,
  "status": "completed",
  "timestamp_iso": "2025-01-15T10:30:45Z",
  "simulation_duration": 2.34,
  "result_file": "case_1_results.raw",
  "error_message": null,
  "parameters": {
    "R": 1000,
    "C": 1e-12,
    "vdda": 3.3,
    "temp": 25
  }
}
```

## Resumability and State Management

**Implementation Status**: ✅ **COMPLETE** 

Sweeps can be time-consuming, and failures are expected. The workflow is designed to be resumable:

- **Generator (`simorc build`)**: Includes `--force` flag. By default, refuses to overwrite existing sweep directories. The `--force` flag enables clean rebuilds.
- **Executor (`simorc run`)**: Fully state-aware. Reads existing `run_status.csv` to skip completed cases and only execute pending or failed simulations. Provides seamless resumability with status consolidation after execution.

## Concurrency and Safe State Updates

**Implementation Status**: ✅ **COMPLETE**

Parallel execution with `pytest-xdist` is handled using a "scatter-gather" approach to avoid race conditions:

1. **Scatter (During Execution)**: Each `pytest` worker writes individual JSON status files to case directories (e.g., `case_X/run_status.json`). This action is atomic and avoids file contention.
2. **Gather (Post-Execution)**: After `pytest` completion, `simorc run` consolidates all individual status files into the master `run_status.csv` in a single atomic operation.

This approach successfully enables parallel execution while maintaining data integrity.