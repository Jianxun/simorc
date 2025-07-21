# Usage Examples

## Basic Workflow

### 1. Create a New Project

```bash
# Initialize a new simulation project
simorc init my_amplifier
cd my_amplifier

# Validate the template configuration
simorc validate
```

### 2. Configure Your Design

Edit `sim_setup.yaml` to point to your DUT:

```yaml
dut:
  schematic: /path/to/my_amplifier.sch
  netlist: ./netlists/my_amplifier.spice

testbenches:
  dc: ./testbenches/dc
  ac: ./testbenches/ac

sweeps:
  pvt_analysis: ./sweeps/pvt_analysis.yaml
  bandwidth_sweep: ./sweeps/bandwidth_sweep.yaml
```

### 3. Define a Parameter Sweep

Create `sweeps/pvt_analysis.yaml`:

```yaml
testbench: dc
parameters:
  vdda: [2.7, 3.3, 3.6]
  temp: [-40, 25, 85, 125]
  corner: ["ss", "tt", "ff"]
```

### 4. Build and Run the Sweep

```bash
# Generate test cases (3×4×3 = 36 cases)
simorc build pvt_analysis

# Execute simulations in parallel
simorc run pvt_analysis -j 8

# Check status
simorc status
```

## Advanced Usage

### Resumable Simulations

If simulations fail or are interrupted:

```bash
# Check what failed
simorc status pvt_analysis

# Resume execution (skips completed cases)
simorc run pvt_analysis -j 4

# Force rebuild if needed
simorc build pvt_analysis --force
```

### Multiple Sweeps

```bash
# Run different sweeps in sequence
simorc build pvt_analysis
simorc run pvt_analysis -j 8

simorc build bandwidth_sweep  
simorc run bandwidth_sweep -j 4

# Or in parallel (different terminals)
simorc run pvt_analysis -j 4 &
simorc run bandwidth_sweep -j 4 &
```

### Project Organization

```bash
# Work with projects in different directories
simorc validate --directory /path/to/project1
simorc build sweep1 --directory /path/to/project1

# Run from any location
simorc run /path/to/project1/results/sweep1_20250115_103045
```

## Real-World Example: Amplifier Characterization

### Directory Structure

```
amplifier_project/
├── sim_setup.yaml
├── netlists/
│   └── ota_amplifier.spice
├── testbenches/
│   ├── dc/
│   │   ├── config.yaml
│   │   └── tb_dc.spice.j2
│   └── ac/
│       ├── config.yaml
│       └── tb_ac.spice.j2
└── sweeps/
    ├── pvt_dc.yaml
    ├── gain_bandwidth.yaml
    └── power_corners.yaml
```

### Sweep Definitions

**PVT Analysis** (`sweeps/pvt_dc.yaml`):
```yaml
testbench: dc
parameters:
  vdda: [2.7, 3.0, 3.3, 3.6]
  temp: [-40, 0, 25, 85, 125]
  corner: ["ss", "sf", "fs", "tt", "ff"]
```

**Gain-Bandwidth Analysis** (`sweeps/gain_bandwidth.yaml`):
```yaml
testbench: ac
parameters:
  load_cap: [1e-12, 2e-12, 5e-12, 10e-12]
  bias_current: [10e-6, 20e-6, 50e-6, 100e-6]
  vdda: [3.3]
  temp: [25]
  corner: ["tt"]
```

### Execution Workflow

```bash
# Validate everything first
simorc validate

# Run DC analysis across PVT corners (100 cases)
simorc build pvt_dc
simorc run pvt_dc -j 8

# Run AC analysis for gain-bandwidth trade-offs (16 cases)  
simorc build gain_bandwidth
simorc run gain_bandwidth -j 4

# Check results
simorc status
```

### Expected Output

```
PVT DC Analysis: 100/100 cases completed (2 failed)
├── Completed: 98 cases in 145.2s
├── Failed: 2 cases (convergence errors at extreme corners)
└── Results: results/pvt_dc_20250115_103045/

Gain-Bandwidth Analysis: 16/16 cases completed
├── Completed: 16 cases in 32.1s  
├── Failed: 0 cases
└── Results: results/gain_bandwidth_20250115_110230/
```

## Error Handling Examples

### Configuration Errors

```bash
simorc validate
```
```
✗ Error in sweeps/pvt_dc.yaml:
  - parameters.vdda: Expected list, got string "3.3"
  - testbench: 'dc_invalid' not found in sim_setup.yaml

✗ Error in testbenches/dc/config.yaml:
  - template: File './tb_dc_missing.spice.j2' does not exist

Configuration validation failed with 3 errors.
```

### Simulation Errors

```bash
simorc run pvt_analysis
```
```
Case 23/100: FAILED (case_23)
├── Parameters: vdda=2.7, temp=125, corner=ss
├── Error: ngspice convergence failure
├── Duration: 0.12s
└── Log: case_23/simulation.log

Case 24/100: COMPLETED (case_24)
├── Parameters: vdda=2.7, temp=125, corner=tt  
├── Duration: 2.34s
└── Results: case_24/case_24_results.raw
```

## Performance Tips

### Parallel Execution

```bash
# Use number of CPU cores for I/O bound simulations
simorc run sweep_name -j $(nproc)

# Use fewer workers for memory-intensive simulations
simorc run large_sweep -j 4

# For very large sweeps, consider chunking
simorc run sweep_name -j 8 --max-cases 100
```

### Resource Management

```bash
# Clean up old results to save space
simorc clean old_sweep_name

# Keep only metadata and summaries
simorc clean old_sweep_name --keep-metadata

# Monitor disk usage
du -sh results/
```