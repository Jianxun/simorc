# Concurrency and Safe State Updates

**Implementation Status**: ✅ **COMPLETE**

Parallel execution with `pytest-xdist` requires careful handling to avoid race conditions while maintaining data integrity.

## Scatter-Gather Architecture

The parallel execution strategy uses a "scatter-gather" approach:

### 1. Scatter Phase (During Execution)
- **Each pytest worker** operates independently
- **Individual status files** written to case directories
- **Atomic JSON operations** prevent file contention
- **No shared state** between workers

### 2. Gather Phase (Post-Execution)  
- **Single consolidation process** after pytest completion
- **Atomic CSV generation** from all individual files
- **Master status file** updated in one operation

## Worker Isolation

### Independent Case Directories
Each case gets its own isolated directory:
```
case_1/
├── netlist.spice         # Read-only input
├── case_1_results.raw    # Written by ngspice
└── run_status.json       # Written by pytest worker
```

### No Shared Writes
- **Workers never write** to shared files during execution
- **No file locking** required between workers
- **No coordination** needed during simulation phase

## Atomic Operations

### Individual Case Updates
Each case status update is atomic:

```python
# Atomic JSON write
status_data = {
    "case_id": case_id,
    "status": "completed", 
    "timestamp_iso": datetime.now(timezone.utc).isoformat(),
    "simulation_duration": duration,
    "result_file": f"case_{case_id}_results.raw",
    "error_message": None
}

# Write to temporary file, then atomic rename
temp_file = f"case_{case_id}/run_status.json.tmp"
final_file = f"case_{case_id}/run_status.json"

with open(temp_file, 'w') as f:
    json.dump(status_data, f, indent=2)

os.rename(temp_file, final_file)  # Atomic on POSIX systems
```

### Status Consolidation
Master CSV update is also atomic:

```python
# Collect all individual status files
all_status = []
for case_dir in case_directories:
    status_file = os.path.join(case_dir, "run_status.json")
    if os.path.exists(status_file):
        with open(status_file) as f:
            all_status.append(json.load(f))

# Write consolidated CSV atomically
temp_csv = "run_status.csv.tmp"
final_csv = "run_status.csv"

with open(temp_csv, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
    writer.writeheader()
    writer.writerows(all_status)

os.rename(temp_csv, final_csv)  # Atomic update
```

## Race Condition Prevention

### File System Level
- **No concurrent writes** to the same file
- **Atomic renames** for file updates
- **Independent directories** for each worker

### Process Level
- **pytest-xdist handles** worker coordination
- **Workers assigned** non-overlapping case sets
- **No shared memory** or coordination primitives needed

### Data Level
- **Case IDs are unique** and pre-assigned
- **No shared counters** or mutable state
- **Status files are write-once** per execution

## Error Handling in Parallel Context

### Worker Failures
- **Individual worker crashes** don't affect other workers
- **Missing status files** indicate incomplete execution
- **Partial results preserved** for manual inspection

### Cleanup and Recovery
```python
# Handle missing or corrupted status files
def consolidate_status(case_directories):
    consolidated = []
    
    for case_dir in case_directories:
        status_file = os.path.join(case_dir, "run_status.json")
        
        if not os.path.exists(status_file):
            # Worker didn't complete - mark as pending
            case_id = extract_case_id(case_dir)
            consolidated.append({
                "case_id": case_id,
                "status": "pending",
                "error_message": "Execution incomplete"
            })
        else:
            try:
                with open(status_file) as f:
                    consolidated.append(json.load(f))
            except json.JSONDecodeError:
                # Corrupted file - mark as failed
                case_id = extract_case_id(case_dir)
                consolidated.append({
                    "case_id": case_id, 
                    "status": "failed",
                    "error_message": "Status file corrupted"
                })
    
    return consolidated
```

## Performance Considerations

### Optimal Worker Count
```bash
# CPU-bound simulations (typical)
simorc run sweep_name -j $(nproc)

# Memory-intensive simulations
simorc run sweep_name -j $(($(nproc) / 2))

# I/O intensive simulations  
simorc run sweep_name -j $(($(nproc) * 2))
```

### File System Overhead
- **Minimize file operations** during execution
- **Batch status updates** where possible
- **Use local storage** for temporary files when available

### Memory Management
- **Workers share nothing** - no memory coordination overhead
- **Each worker loads** only its assigned cases
- **pytest-xdist handles** worker lifecycle and memory cleanup

## Benefits of This Approach

### Simplicity
- **No complex locking** or synchronization primitives
- **Standard file operations** with atomic semantics
- **Leverages pytest-xdist** battle-tested parallelization

### Robustness
- **Individual failures isolated** to single cases
- **Partial execution recoverable** from filesystem state
- **No shared state corruption** possible

### Scalability  
- **Linear scaling** with number of workers
- **No coordination bottlenecks** during execution
- **Works across** different compute environments (local, cluster, cloud)