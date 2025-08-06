# simorc Documentation

This directory contains the documentation for simorc, built using Sphinx.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

### Build HTML Documentation

```bash
cd docs/
python -m sphinx -M html . _build
```

The built documentation will be available in `_build/html/index.html`.

### Alternative Build Method

You can also use the Makefile:

```bash
cd docs/
make html
```

## Documentation Structure

The documentation is organized into the following sections:

- **Overview**: Core principles and three-stage architecture
- **Architecture**: Detailed workflow, data contracts, and analyzer design
- **Configuration**: YAML configuration system and validation
- **CLI**: Command-line interface reference and usage examples
- **Implementation**: Technical details on data artifacts, state management, and concurrency

## File Organization

```
docs/
├── index.md                    # Main documentation index
├── overview.md                 # Core principles and architecture overview
├── architecture/               # Architecture details
│   ├── index.md
│   ├── workflow.md            # Workflow diagram and stage boundaries
│   ├── data-contracts.md      # Data schemas and artifacts
│   └── analyzer.md            # Planned analyzer architecture
├── configuration/             # Configuration system
│   ├── index.md
│   ├── sim-setup.md          # sim_setup.yaml reference
│   ├── sweeps.md             # Sweep definition files
│   ├── testbenches.md        # Testbench configuration
│   └── validation.md         # Configuration validation
├── cli/                       # Command-line interface
│   ├── index.md
│   ├── commands.md           # Command reference
│   └── usage-examples.md     # Usage examples and workflows
├── implementation/            # Implementation details
│   ├── index.md
│   ├── data-artifacts.md     # Data schemas and file formats
│   ├── state-management.md   # Resumability and state tracking
│   └── concurrency.md        # Parallel execution and safety
├── conf.py                    # Sphinx configuration
├── Makefile                   # Build automation
└── README.md                  # This file
```

## Migration from Monolithic Architecture File

The original `docs/architecture.md` has been divided into multiple focused documents:

1. **Core principles** → `overview.md`
2. **Workflow diagrams** → `architecture/workflow.md`
3. **Data contracts** → `architecture/data-contracts.md`
4. **Analyzer design** → `architecture/analyzer.md`
5. **Configuration system** → `configuration/` directory
6. **CLI details** → `cli/` directory
7. **Implementation details** → `implementation/` directory

This structure provides better organization and easier maintenance of the documentation.

## Adding New Documentation

To add new documentation:

1. Create new `.md` files in the appropriate directory
2. Add the new file to the relevant `toctree` directive in the index files
3. Follow the existing structure and style
4. Build and test the documentation locally

## Sphinx Configuration

The documentation uses:

- **MyST Parser** for Markdown support
- **RTD Theme** for styling
- **Cross-references** between documents
- **Code highlighting** for examples
- **Table of contents** generation

See `conf.py` for the complete Sphinx configuration.