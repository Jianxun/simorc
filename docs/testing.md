# Testing Guide

This document explains how to run tests in the simorc project, covering both framework tests and project-specific simulation tests.

## Overview

The simorc project has two distinct types of tests:

1. **Framework Tests**: Core simorc functionality tests
2. **Project Tests**: Simulation tests for specific projects (e.g., RC circuits, OTA designs)

Each type requires a different execution strategy to avoid conflicts and ensure proper test isolation.

## Framework Tests

Framework tests verify the core simorc functionality including CLI commands, configuration validation, and internal modules.

### Running Framework Tests

```bash
# From the simorc project root directory
cd /path/to/simorc
python -m pytest tests/ -v
```

### Expected Results

- **Test Count**: ~66 tests
- **Test Categories**:
  - CLI command functionality (`tests/cli/`)
  - Configuration validation (`tests/test_config.py`)
  - Project initialization (`tests/test_init.py`)
  - Sweep building (`tests/test_build.py`)
  - Error handling (`tests/test_error_handling.py`)
  - Simulation execution (`tests/test_simulation.py`)
  - Status management (`tests/test_status.py`)

### Example Output

```
============================= test session starts ==============================
platform darwin -- Python 3.12.9, pytest-8.4.0, pluggy-1.6.0
collected 66 items

tests/cli/test_main.py::TestCLIBasics::test_cli_help PASSED              [  1%]
tests/cli/test_main.py::TestCLIBasics::test_cli_version PASSED           [  3%]
...
======================== 66 passed, 1 warning in 0.15s =========================
```

## Project Tests

Project tests are simulation-specific tests that verify the execution of actual SPICE simulations within simorc projects.

### Running Project Tests

Project tests must be run from the directory containing the `sim_setup.yaml` file:

```bash
# Navigate to the specific project directory
cd /path/to/project/with/sim_setup.yaml

# Run project-specific tests
python -m pytest -v
```

### Example: RC Circuit Project

```bash
# Navigate to RC example project
cd example/rc

# Run RC simulation tests
python -m pytest -v
```

**Expected Results**:
- **Test Count**: 9 tests (3×3 parameter combinations)
- **Test Type**: Parametrized simulation cases testing different R and C values

**Example Output**:
```
============================= test session starts ==============================
collected 9 items

results/rc_values/tests/test_rc_values.py::test_simulation_case[1-100-100p] PASSED [ 11%]
results/rc_values/tests/test_rc_values.py::test_simulation_case[2-100-1n] PASSED [ 22%]
...
============================== 9 passed in 0.13s =============================
```

## Test Execution Strategy

### ✅ Correct Approach

**Framework Tests** (from project root):
```bash
cd /Users/username/simorc
python -m pytest tests/
```

**Project Tests** (from project directory):
```bash
cd /Users/username/simorc/example/rc
python -m pytest
```

### ❌ Incorrect Approach

**DO NOT** run pytest from the project root without specifying `tests/`:
```bash
# This will pick up obsolete test files and cause failures
cd /Users/username/simorc
python -m pytest  # ❌ Wrong - discovers all test files
```

## Test Types and Locations

### Framework Test Structure

```
tests/
├── cli/
│   └── test_main.py           # CLI interface tests
├── test_build.py              # Sweep building tests
├── test_config.py             # Configuration validation tests
├── test_error_handling.py     # Error handling tests
├── test_init.py               # Project initialization tests
├── test_loader.py             # Configuration loading tests
├── test_rc_validation.py      # RC project validation tests
├── test_simulation.py         # Simulation execution tests
└── test_status.py             # Status management tests
```

### Project Test Structure

```
example/rc/
├── sim_setup.yaml             # Project configuration
├── results/
│   └── rc_values/
│       ├── metadata.csv       # Generated test metadata
│       └── tests/
│           └── test_rc_values.py  # Generated simulation tests
└── ...
```

## Continuous Integration

When setting up CI/CD pipelines, use the following test commands:

```yaml
# Example GitHub Actions workflow
- name: Test Framework
  run: python -m pytest tests/ -v

- name: Test RC Example
  run: |
    cd example/rc
    python -m pytest -v
```

## Troubleshooting

### Common Issues

1. **Tests from obsolete directories are discovered**
   - **Problem**: Running `pytest` from project root picks up old test files
   - **Solution**: Always specify `tests/` when running from project root

2. **Project tests fail with import errors**
   - **Problem**: Running project tests from wrong directory
   - **Solution**: Ensure you're in the directory containing `sim_setup.yaml`

3. **Simulation tests fail with "Read-only file system" errors**
   - **Problem**: Obsolete test files trying to write to protected directories
   - **Solution**: Use the correct test execution strategy above

### Debugging Test Failures

For detailed error output:
```bash
# Framework tests with detailed output
python -m pytest tests/ --tb=long -v

# Project tests with detailed output  
cd example/rc
python -m pytest --tb=long -v
```

## Test Development Guidelines

### Adding Framework Tests

1. Create test files in the `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures for common setup
4. Test both success and failure cases
5. Ensure tests are isolated and don't depend on external state

### Adding Project Tests

Project tests are typically auto-generated by the `simorc build` command:

```bash
# Build a sweep to generate project tests
simorc build sweep_name

# Generated tests will appear in:
# results/sweep_name/tests/test_sweep_name.py
```

For custom project tests:
1. Place in the project directory (same level as `sim_setup.yaml`)
2. Ensure tests can access project configuration
3. Use relative paths for project resources

## Integration with Development Workflow

### Test-Driven Development

1. **Write Framework Tests First**: When adding new simorc features
   ```bash
   # Create test for new feature
   # Run to see it fail
   python -m pytest tests/test_new_feature.py -v
   
   # Implement feature
   # Run to see it pass
   python -m pytest tests/test_new_feature.py -v
   ```

2. **Validate Projects**: Before and after changes
   ```bash
   # Test that existing projects still work
   cd example/rc
   python -m pytest -v
   ```

### Pre-commit Workflow

Before committing changes:
```bash
# 1. Run all framework tests
python -m pytest tests/ -v

# 2. Test example projects  
cd example/rc && python -m pytest -v

# 3. Run linting (if configured)
# python -m flake8 src/ tests/

# 4. Commit if all tests pass
git add . && git commit -m "Description of changes"
```