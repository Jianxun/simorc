# Project Memory

## Project Overview
`simorc` is a Python-based simulation orchestration tool designed to manage and automate electronic circuit simulation workflows. The name is a play on "simulation orchestrator". The tool is built on three core principles:
-   **Pytest as Orchestrator**: Leveraging `pytest` for robust test execution.
-   **Configuration-Driven**: Using YAML files for transparent and version-controllable setups.
-   **Separation of Concerns**: A three-stage architecture (Generate, Execute, Analyze).

## Current State
- The core architecture has been defined in `context/architecture.md`.
- A minimal Python package structure (`0.0.0`) has been created and published to PyPI to reserve the name.
- A local Git repository has been initialized and pushed to GitHub.
- A Python virtual environment (`venv`) is set up with `wave_view` installed.
- The `.gitignore` file is configured.
- The `context` directory is established for session continuity.
- **MVP Development Branch**: Created `mvp-implementation` branch for systematic development.
- **Development Guidelines**: Consolidated TDD workflow and cross-session continuity practices in `CLAUDE.md`.
- **Phase 1 Complete - Core CLI Foundation**:
  - ✅ pytest test structure established (`/tests/cli/`)
  - ✅ Click-based CLI framework implemented with all subcommands
  - ✅ Package structure with proper entry points (`simorc` command)
  - ✅ Dependencies configured (click, pydantic, pyyaml, pytest)
  - ✅ All 9 CLI tests passing
  - ✅ Working commands: `simorc --version`, `simorc --help`, all subcommand help
- **Phase 2 Complete - Configuration System**:
  - ✅ Pydantic models for YAML schemas (`src/simorc/config.py`)
    - DutConfig, TestbenchConfigModel, SweepConfig, SimSetupConfig, PlotConfig
    - Updated to Pydantic V2 syntax with field_validator
    - 15 configuration model tests passing
  - ✅ simorc init command functionality (`simorc init`)
    - Creates proper directory structure (netlists, testbenches, sweeps, results)
    - Generates template configurations (sim_setup.yaml, example testbench, sweep)
    - Handles existing files gracefully, 6 init command tests passing
  - ✅ Configuration loading and validation system (`src/simorc/loader.py`)
    - YAML loading utilities with error handling
    - Project validation with detailed error reporting
    - 8 loader functionality tests passing
  - ✅ simorc validate command (`simorc validate`)
    - CLI interface for project configuration validation
    - Successfully validates example/rc project (1 validation test passing)
  - ✅ Comprehensive error handling and user feedback
    - Graceful handling of missing files, invalid YAML, permission errors
    - Detailed error messages with clear user guidance
    - 7 error handling tests passing
  - **Total: 46 tests passing for complete Phase 2 implementation**
- **Prototype Validation Complete**: Created and tested ngspice toolchain integration in `prototypes/` directory:
  - Simple RC circuit simulation working (`rc_circuit.cir`)
  - ngspice execution verified (generates 10,008 data points)
  - `waveview` CLI integration confirmed (can inspect signals: time, v(in), v(out), i(v1))
  - Complete simulation workflow validated from netlist → ngspice → raw file → waveview parsing
- **Example Projects Created**:
  - `designs/libs/tb_analog/tb_ota/`: Working OTA testbench example with full 3-stage workflow
  - `example/rc/`: New RC low-pass filter example ready for simorc implementation
    - DUT: Simple RC low-pass filter netlist (`netlists/rc_lowpass.spice`)
    - AC testbench: Frequency response analysis with Bode plot specifications
    - Transient testbench: Step response analysis
    - Parameter sweep: R and C value variations (3×3=9 cases)
    - Complete simorc configuration structure established

## Key Decisions
- **Architecture**: Adopted a three-stage architecture: Generate, Execute, Analyze. This is managed by a central `simorc` CLI tool.
- **CLI Structure**: The CLI will be subcommand-based (`init`, `build`, `run`, `plot`, `status`, `clean`, `netlist`).
- **Configuration**: The workflow is driven by `sim_setup.yaml`, sweep-specific YAML files, and testbench `config.yaml` files. `pydantic` will be used for validation.
- **State Management**: A `metadata.csv` file will track the state of each simulation case within a sweep, enabling resumability.
- **Concurrency**: A "scatter-gather" approach using a `.status/` directory will be used to handle parallel execution with `pytest-xdist` and avoid race conditions.
- **Project Naming**: Chose the name `simorc` and secured it on PyPI and GitHub.
- **Packaging**: Using `pyproject.toml` with `hatchling`.
- **Development Environment**: Using macOS with local ngspice installation (version 44.2) instead of devcontainer setup.
- **Result Parsing**: Using `wave_view` Python module for raw result parsing and visualization. Author has direct access to enhance features if needed.
- **Context Management**: Following structured context management guidelines with `context/memory.md` and `context/todo.md` for session continuity.

## Open Questions
- What are the detailed schemas for the `pydantic` validation models?
- What is the precise format for the `tb_lib` functions that will be called by the `pytest` tests?
- What plotting libraries and report formats will be used in the analysis stage?
- What will be the initial target simulation software (e.g., ngspice)? 