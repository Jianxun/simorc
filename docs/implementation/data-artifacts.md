# Data Artifacts & Schemas

## Overview

The simorc workflow communicates between stages through well-defined data artifacts. This ensures loose coupling between stages while maintaining data integrity.

## File Formats

### CSV Files
- **Purpose**: Human-readable, version-controllable metadata
- **Usage**: Parameter tracking, status monitoring
- **Benefits**: Easy to inspect, edit, and process with standard tools

### JSON Files  
- **Purpose**: Structured data for individual cases
- **Usage**: Atomic status updates during parallel execution
- **Benefits**: Atomic writes, language-agnostic parsing

### Raw Files
- **Purpose**: Native SPICE simulation output
- **Usage**: Waveform data and operating point information  
- **Benefits**: Tool-standard format, direct simulator output

### HDF5 Files (Planned)
- **Purpose**: Structured, hierarchical data storage
- **Usage**: Aggregated results with metadata
- **Benefits**: Self-describing, high-performance, tool-agnostic

## Schema Evolution

The data schemas are designed to be forward-compatible:

### Version 1.0 (Current)
```csv
# metadata.csv
case_id,result_file,R,C,vdda,temp
1,case_1/case_1_results.raw,1000,1e-12,3.3,25
```

### Version 1.1 (Planned)
```csv  
# metadata.csv with schema version
schema_version,1.1
case_id,result_file,R,C,vdda,temp,created_at
1,case_1/case_1_results.raw,1000,1e-12,3.3,25,2025-01-15T10:30:45Z
```

## Data Validation

All data artifacts include validation:

### Metadata Validation
- **Case ID uniqueness**: No duplicate case IDs
- **Parameter types**: Numeric parameters validated as numbers
- **File references**: Result file paths validated for existence

### Status Validation
- **Valid states**: Only allowed status values (pending, completed, failed)
- **Timestamp format**: ISO 8601 timestamps
- **Duration consistency**: Non-negative simulation durations

### Cross-validation
- **Metadata-Status consistency**: Case IDs must match between files
- **Parameter consistency**: Parameters must match between files
- **File consistency**: Referenced files must exist

## Artifact Lifecycle

### Generation Phase
1. **metadata.csv** created with all parameter combinations
2. **test_*.py** files generated for pytest execution
3. **netlist.spice** files created for each case

### Execution Phase  
1. **run_status.csv** initialized from metadata.csv
2. **case_X/run_status.json** written atomically during execution
3. **case_X_results.raw** created by ngspice simulation
4. **run_status.csv** consolidated after execution

### Analysis Phase (Planned)
1. **sweep_results.h5** aggregates all raw files
2. **Metrics extracted** and stored in structured format
3. **Summary statistics** computed across all cases

## Data Integrity

### Atomic Operations
- Individual case status updates use atomic JSON writes
- CSV consolidation happens in single atomic operation
- File operations use temporary files with atomic rename

### Consistency Checks
- Cross-reference validation between metadata and status files
- File existence validation before processing
- Schema validation on all data loads

### Error Recovery
- Partial execution state can be recovered from individual JSON files
- Missing or corrupted files trigger clear error messages
- Validation errors include specific location information