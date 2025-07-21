# Workflow Diagram & Boundaries

## Architecture Overview

```mermaid
graph TD
    subgraph "Stage 1: Generation (simorc build)"
        A["sim_setup.yaml<br/>sweep.yaml"] --> B[simorc build]
        B --> C1["metadata.csv"]
        B --> C2["tests/test_*.py"]
        B --> C3["case_X/netlist.spice"]
    end

    subgraph "Stage 2: Execution (simorc run)"
        D1["metadata.csv"] --> E[pytest]
        D2["tests/test_*.py"] --> E
        E --> F["ngspice simulation"]
        F --> G["case_X/results.raw"]
        E --> H["run_status.csv"]
    end

    subgraph "Stage 3: Analysis (simorc analyze)"
        I1["All results.raw"] --> J[simorc analyze]
        I2["run_status.csv"] --> J
        I3["metadata.csv"] --> J
        J --> K1["sweep_results.h5"]
        J --> K2["Metrics & Waveforms"]
    end

    subgraph "Downstream Tools"
        K1 --> L1[Visualization Tools]
        K1 --> L2[Report Generators] 
        K1 --> L3[Archive Systems]
    end

    subgraph "User Commands"
        U1[User] --> B
        U1 --> E
        U1 --> J
    end
    
    C1 --> D1
    C2 --> D2
    G --> I1
    H --> I2
    C1 --> I3

    style B fill:#90EE90
    style E fill:#90EE90
    style J fill:#FFB347
    style K1 fill:#87CEEB
```

## Stage Boundaries & Contracts

### Generation → Execution

- **`metadata.csv`**: Parameter combinations and case tracking
- **`tests/test_*.py`**: pytest-compatible test files
- **`case_X/netlist.spice`**: Parameterized simulation netlists

### Execution → Analysis

- **`case_X/results.raw`**: SPICE simulation output files
- **`run_status.csv`**: Execution status with timing and parameters
- **`metadata.csv`**: Updated with result file paths

### Analysis → Downstream

- **`sweep_results.h5`**: Structured HDF5 with all data and metadata
- **Standardized schema**: For tool-agnostic consumption

## Data Flow

The workflow ensures clean data flow between stages:

1. **Stage 1** creates all the configuration and test infrastructure
2. **Stage 2** executes simulations and tracks status
3. **Stage 3** processes results into structured, queryable format
4. **Downstream tools** consume the structured output for visualization and reporting