# Overview

## Core Principles

The simulation workflow is built on three core principles to ensure it is robust, flexible, and maintainable.

- **Pytest as the Orchestrator**: We leverage the mature, battle-tested `pytest` framework for test execution, parameterization, parallel execution (`pytest-xdist`), and rich reporting. This eliminates the need for custom scheduling logic.
- **Configuration-Driven**: The entire workflow is driven by explicit YAML configuration files (`sim_setup.yaml`, sweep definitions, and testbench configs). This eliminates "magic" directory structures and makes the simulation suite transparent and version-controllable.
- **Separation of Concerns**: The workflow is divided into three distinct, independent stages: Generation, Execution, and Analysis. Each stage has a single responsibility and communicates through well-defined data artifacts.
- **Self-Contained Architecture**: simorc includes native SPICE raw file parsing and structured result aggregation, eliminating dependencies on external visualization tools for core functionality.

## The Three-Stage Architecture

The "orchestrator" is not a single script but a system of three specialized components.

### Stage 1: The Generator (`simorc build`)

**Implementation Status**: ✅ **COMPLETE** - Fully implemented and tested

The generator translates user-defined parameter sweeps into concrete, executable test plans.

- **Command**: `simorc build <sweep_name> [--force] [--directory]`
- **Inputs**: `sim_setup.yaml` and sweep definition YAML files
- **Process**:
  1. **Parameter Expansion**: Calculates the Cartesian product of all parameters specified in the sweep file
  2. **Directory Structure**: Creates organized `case_X/` directories for each parameter combination
  3. **Metadata Generation**: Creates `metadata.csv` with case tracking (case_id, parameters, result_file)
  4. **Netlist Generation**: Uses Jinja2 templates to render parameterized netlists for each case
  5. **Test Generation**: Creates parametrized `test_*.py` files that read from metadata.csv
- **Outputs**: 
  - `metadata.csv` (single source of truth)
  - `tests/test_*.py` (pytest-compatible test files)
  - `case_X/netlist.spice` (individual netlists)
  - Organized directory structure for execution

- **Key Features**:
  - **Template-based**: Jinja2 templating for netlist and test generation
  - **Resumable**: `--force` flag for clean rebuilds
  - **Organized**: Each case gets its own directory
  - **Validated**: Full Pydantic validation of configurations

### Stage 2: The Executor (`simorc run`)

**Implementation Status**: ✅ **COMPLETE** - Fully implemented and tested

The executor runs all simulation cases in a sweep using pytest orchestration.

- **Command**: `simorc run <sweep_run_id> [-j PARALLEL]`
- **Inputs**: Generated test files and metadata from Stage 1
- **Process**:
  1. **Sweep Discovery**: Intelligently locates sweep directories by name or path
  2. **Status Initialization**: Creates `run_status.csv` for execution tracking
  3. **Pytest Execution**: Invokes pytest with optional parallel execution (`-j` flag)
  4. **Simulation Execution**: Each test case runs ngspice and captures results
  5. **Status Consolidation**: Aggregates individual case status into summary CSV
- **Outputs**: 
  - `case_X/case_X_results.raw` (SPICE simulation results)
  - `run_status.csv` (execution status with timing and parameters)
  - `case_X/run_status.json` (individual case status)
  - Comprehensive error logging and debugging info

- **Key Features**:
  - **Parallel Execution**: pytest-xdist support for multi-process simulation
  - **Status Tracking**: Real-time progress monitoring with timestamps
  - **Error Handling**: Robust failure detection and debugging support
  - **Resumable**: Can restart failed or incomplete sweeps
  - **Live Progress**: Real-time console output during execution
  - **Timing Metrics**: Execution duration tracking per case

### Stage 3: The Analyzer (`simorc analyze`)

**Implementation Status**: 🚧 **PLANNED** - Architecture designed, implementation pending

The analyzer extracts metrics and aggregates results from completed sweep simulations.

- **Command**: `simorc analyze <sweep_run_id> [--output results.h5]`
- **Inputs**: SPICE raw files and metadata from completed sweep execution
- **Process**:
  1. **Raw File Parsing**: Native SPICE raw file parsing using `spicelib` or `ltspice`
  2. **Metrics Extraction**: User-defined Python scripts calculate scalar metrics (bandwidth, gain, etc.)
  3. **Waveform Processing**: Extract and process waveforms (FFT, filtering, derived signals)
  4. **Data Aggregation**: Combine all results into structured HDF5 format
  5. **Summary Generation**: Create aggregate statistics and pass/fail matrices
- **Outputs**:
  - `sweep_results.h5` (structured HDF5 with all data and metadata)
  - Scalar metrics per case (bandwidth, gain, phase margin)
  - Processed waveforms (frequency response, transients, noise)
  - Aggregated sweep statistics and parameter correlations

- **Key Features**:
  - **Self-Contained**: Native raw file parsing, no external tool dependencies
  - **User-Extensible**: Custom metrics via Python scripts
  - **Structured Output**: HDF5 format with hierarchical data organization
  - **Rich Metadata**: Full configuration and parameter tracking
  - **Tool Agnostic**: Clear contract for downstream visualization/reporting tools