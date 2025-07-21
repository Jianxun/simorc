# Resumability and State Management

**Implementation Status**: ✅ **COMPLETE** 

Sweeps can be time-consuming, and failures are expected. The workflow is designed to be resumable at every stage.

## Generator Resumability (`simorc build`)

### Default Behavior
- **Refuses to overwrite** existing sweep directories by default
- **Validates existing state** before proceeding
- **Reports conflicts** with clear error messages

### Force Rebuild
- **`--force` flag** enables clean rebuilds
- **Removes all existing** case directories and generated files
- **Starts completely fresh** parameter expansion and generation

### Example Workflow
```bash
# First build
simorc build pvt_sweep
# Output: Created 100 cases in results/pvt_sweep_20250115_103045/

# Attempt to rebuild (fails by default)
simorc build pvt_sweep
# Error: Sweep directory already exists. Use --force to rebuild.

# Force rebuild
simorc build pvt_sweep --force  
# Output: Removed existing directory. Created 100 cases in results/pvt_sweep_20250115_110230/
```

## Executor Resumability (`simorc run`)

### State-Aware Execution
The executor is fully state-aware and can resume interrupted sweeps seamlessly.

#### State Discovery Process
1. **Locate sweep directory** by name or full path
2. **Read existing `run_status.csv`** if present
3. **Scan individual case status** files (`case_X/run_status.json`)
4. **Determine execution plan** based on current state

#### Execution Logic
```python
for case in all_cases:
    if case.status == "completed":
        skip_case(case)  # Already done
    elif case.status == "failed":
        retry_case(case)  # Retry failed cases
    else:  # pending or missing
        execute_case(case)  # Run new cases
```

### Example Resume Workflow
```bash
# Initial run (interrupted after 50/100 cases)
simorc run pvt_sweep -j 8
# Ctrl+C after some cases complete

# Resume execution (automatically skips completed cases)
simorc run pvt_sweep -j 8
# Output: Resuming execution. 50 cases completed, 50 pending.
# [Continues from where it left off]
```

## Status Tracking

### Multi-Level Status
Status is tracked at multiple levels for robustness:

#### 1. Individual Case Status (`case_X/run_status.json`)
```json
{
  "case_id": 1,
  "status": "completed",
  "timestamp_iso": "2025-01-15T10:30:45Z",
  "simulation_duration": 2.34,
  "result_file": "case_1_results.raw",
  "error_message": null
}
```

#### 2. Consolidated Status (`run_status.csv`)
```csv
case_id,status,timestamp_iso,simulation_duration,result_file,error_message
1,completed,2025-01-15T10:30:45Z,2.34,case_1/case_1_results.raw,
2,failed,2025-01-15T10:31:02Z,0.12,case_2/case_2_results.raw,Convergence error
3,pending,,,,
```

### Status Consolidation
After pytest execution completes:
1. **Scan all case directories** for individual status files
2. **Aggregate status information** into master CSV
3. **Update timestamps and metrics** 
4. **Report summary statistics**

## Error Handling and Recovery

### Graceful Degradation
- **Individual case failures** don't stop the entire sweep
- **Missing files** are handled with clear error messages
- **Corrupted status** files trigger re-execution of affected cases

### Recovery Strategies

#### Partial Execution Recovery
```bash
# If run_status.csv is corrupted but individual files exist
simorc run pvt_sweep --rebuild-status
# Reconstructs run_status.csv from individual case files
```

#### Case-Level Recovery
```bash
# Re-run only failed cases
simorc run pvt_sweep --retry-failed

# Re-run specific cases
simorc run pvt_sweep --cases 23,45,67
```

## State Persistence

### Directory Structure
```
results/pvt_sweep_20250115_103045/
├── metadata.csv          # Parameter combinations (immutable)
├── run_status.csv        # Consolidated execution status
├── case_1/
│   ├── netlist.spice     # Generated netlist
│   ├── case_1_results.raw # Simulation results
│   └── run_status.json   # Individual case status
├── case_2/
│   └── [similar structure]
└── tests/
    └── test_pvt_sweep.py # Generated pytest file
```

### Immutable vs Mutable State

#### Immutable (Set at generation time)
- **`metadata.csv`**: Parameter combinations and case definitions
- **`case_X/netlist.spice`**: Generated simulation netlists
- **`tests/test_*.py`**: Generated pytest test files

#### Mutable (Updated during execution)
- **`run_status.csv`**: Overall execution status and progress
- **`case_X/run_status.json`**: Individual case execution status
- **`case_X/case_X_results.raw`**: Simulation output files

This separation ensures that parameter definitions remain stable while execution state can be safely updated and recovered.