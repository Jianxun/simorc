# Command Reference

## Implemented Commands

### `simorc init [directory]` ✅

**Status**: Fully implemented and tested

Creates a new simulation environment with proper directory structure and template files.

```bash
simorc init my_project
cd my_project
```

**Features**:
- Creates directory structure
- Template configurations
- Example testbench and sweep
- Complete project skeleton ready for customization

**Output**:
```
Created simulation project in my_project/
├── sim_setup.yaml
├── testbenches/
│   └── dc/
├── sweeps/
│   └── example_sweep.yaml
└── netlists/
```

### `simorc validate [--directory]` ✅

**Status**: Fully implemented and tested

Validates all configuration files in the project for syntax and logical errors.

```bash
simorc validate
simorc validate --directory /path/to/project
```

**Features**:
- Comprehensive Pydantic validation
- Detailed error reporting with specific locations
- File existence checking
- Cross-reference validation

**Example Output**:
```
✓ sim_setup.yaml is valid
✓ sweep pvt_dc is valid  
✓ testbench dc is valid
Configuration validation passed!
```

### `simorc build <sweep_name> [--force] [--directory]` ✅

**Status**: Fully implemented and tested

Prepares a sweep for execution (Stage 1: Generation).

```bash
simorc build pvt_dc
simorc build pvt_dc --force  # Overwrite existing
simorc build pvt_dc --directory /path/to/project
```

**Features**:
- Parameter expansion using Cartesian product
- Jinja2 templating for netlist generation
- Organized case directories
- Pytest-compatible test generation
- Full Pydantic validation

**Outputs**:
- `metadata.csv` (single source of truth)
- `tests/test_*.py` (pytest-compatible test files)
- `case_X/netlist.spice` (individual netlists)
- Organized directory structure

### `simorc run <sweep_run_id> [-j PARALLEL]` ✅

**Status**: Fully implemented and tested

Executes a prepared sweep (Stage 2: Execution).

```bash
simorc run pvt_dc
simorc run pvt_dc -j 4  # Run with 4 parallel workers
simorc run results/pvt_dc_20250115_103045  # Full path
```

**Features**:
- Parallel execution via pytest-xdist
- Real-time status tracking
- Resumability (skips completed cases)
- Comprehensive error handling
- Live progress reporting
- Execution timing metrics

**Outputs**:
- `case_X/case_X_results.raw` (SPICE simulation results)
- `run_status.csv` (execution status with timing)
- `case_X/run_status.json` (individual case status)
- Detailed error logging

## Planned Commands

### `simorc analyze <sweep_run_id> [--output results.h5]` 🚧

**Status**: Architecture designed, implementation pending

Extracts metrics and aggregates results (Stage 3: Analysis).

```bash
simorc analyze pvt_dc
simorc analyze pvt_dc --output my_results.h5
```

**Planned Features**:
- Native SPICE raw file parsing
- User-defined metrics via Python scripts
- HDF5 output with structured data
- Waveform processing and aggregation

**Planned Outputs**:
- Structured HDF5 with scalars, waveforms, and metadata
- Aggregate statistics and pass/fail matrices

### `simorc status` 📋

**Status**: Placeholder implemented, needs enhancement

Overview of all sweep progress and status.

```bash
simorc status
simorc status --sweep pvt_dc
```

**Planned Features**:
- Multi-sweep dashboard
- Progress tracking across all sweeps
- Failure reporting and summaries
- Execution time estimates

### `simorc clean [sweep_run_id] [--all]` 📋

**Status**: Placeholder implemented, needs enhancement

Clean up sweep results to free disk space.

```bash
simorc clean pvt_dc
simorc clean --all  # Clean all results
simorc clean pvt_dc --keep-metadata  # Keep CSV files
```

**Planned Features**:
- Interactive cleanup with confirmation
- Selective deletion (results only, metadata only, etc.)
- Safety checks to prevent accidental deletion
- Disk space reporting

## Global Options

All commands support these global options:

- `--directory DIR`: Specify project directory (default: current directory)
- `--verbose`: Enable verbose output
- `--help`: Show command help

## Future Considerations

### `simorc plot <sweep_run_id>` (Optional)

**Status**: Under discussion - may be handled by external tools

Convenience wrapper for visualization that may delegate to external tools via the HDF5 contract.