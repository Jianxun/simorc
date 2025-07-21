# simorc Documentation

simorc is a simulation orchestration tool designed for robust, flexible, and maintainable analog circuit simulation workflows.

```{toctree}
:maxdepth: 2
:caption: Contents:

overview
architecture/index
configuration/index
cli/index
implementation/index
```

## Quick Start

1. Install simorc: `pip install simorc`
2. Initialize a project: `simorc init my_project`
3. Configure your simulation: Edit `sim_setup.yaml`
4. Build a sweep: `simorc build my_sweep`
5. Run simulations: `simorc run my_sweep`

## Key Features

- **Pytest-based orchestration** for mature test execution and parallel processing
- **Configuration-driven workflow** with explicit YAML configuration files
- **Three-stage architecture** separating generation, execution, and analysis
- **Self-contained design** with native SPICE file parsing and result aggregation