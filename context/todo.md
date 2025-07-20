# Project Todo List

## Current Sprint - Phase 3: Stage 1 - Generator
- [ ] Implement simorc build <sweep_name> command
- [ ] Create metadata.csv generation logic  
- [ ] Implement test_*.py generation for pytest
- [ ] Test with example/rc sweep configuration

## Phase 4: Stage 2 - Executor (Next)
- [ ] Implement simorc run <sweep_run_id> command
- [ ] Add ngspice execution and process management
- [ ] Implement parallel execution with pytest-xdist
- [ ] Add result file management and status tracking

## Backlog
- [ ] Add support for different simulation engines.
- [ ] Implement result parsing and analysis.
- [ ] Create documentation for users and developers.
- [ ] Set up continuous integration (CI) on GitHub Actions.

## Completed Tasks
- [X] Decide on the project name: `simorc`.
- [X] Create a placeholder package (0.0.0).
- [X] Publish the placeholder to PyPI.
- [X] Create and publish the repository to GitHub.
- [X] Set up a Python virtual environment.
- [X] Configure `.gitignore`.
- [X] Validate ngspice toolchain integration with prototype RC circuit
- [X] Create OTA testbench example with working 3-stage workflow
- [X] Create RC low-pass filter example project structure:
  - [X] RC DUT netlist with parameterized R and C values
  - [X] AC testbench for frequency response (Bode plots)
  - [X] Transient testbench for step response
  - [X] Parameter sweep configuration (3×3 R×C combinations)
  - [X] Complete simorc-compatible YAML configuration structure
- [X] **Phase 1: Core CLI Foundation**
  - [X] Setup pytest test structure (/tests/)
  - [X] Implement basic CLI framework with Click
  - [X] Create core package structure (src/simorc/)
  - [X] Implement simorc --version and simorc --help
  - [X] Add entry point configuration in pyproject.toml
- [X] **Phase 2: Configuration System**
  - [X] Implement pydantic models for YAML schemas (15 tests)
  - [X] Create simorc init command (scaffold project structure) (6 tests)
  - [X] Test configuration validation with example/rc project (9 tests)
  - [X] Implement basic error handling and user feedback (7 tests)
  - [X] Add simorc validate command with detailed reporting
  - [X] **Total: 46 tests passing for complete Phase 2** 