# `sim_setup.yaml`: The Central Hub

The `sim_setup.yaml` file is the main entry point for a given Device Under Test (DUT). It acts as a "control panel," declaring pointers to all the necessary assets for that DUT's simulation environment.

## Key Sections

### `dut`
Specifies the path to the DUT's schematic or netlist. This is the component that will be tested.

### `testbenches`
A dictionary that declares all available single-run testbenches. The key is a short, user-friendly name (e.g., `dc`), and the value is the relative path to the directory containing that testbench's configuration (`config.yaml`) and template (`template.j2`).

### `sweeps`
A dictionary that declares all available parameter sweeps. The key is the name of the sweep (e.g., `pvt_dc`), and the value is the relative path to the YAML file that defines the sweep's parameters.

## Example

```yaml
# sim_setup.yaml
dut:
  schematic: /foss/designs/libs/core_analog/ota_5t/ota_5t.sch
  netlist: ./netlists/ota_5t_ac.spice

testbenches:
  dc: ./testbenches/dc
  ac: ./testbenches/ac

sweeps:
  pvt_dc: ./sweeps/pvt/sweep_pvt_dc.yaml
  vdda_sweep: ./sweeps/vdda_sweep.yaml
```

## Path Resolution

**Important**: All relative paths within this file are resolved relative to the directory containing `sim_setup.yaml` itself.

## Usage

The `sim_setup.yaml` file serves as the single entry point for:

- **Project validation**: `simorc validate` checks all referenced files exist
- **Sweep building**: `simorc build` uses testbench and sweep definitions
- **Discovery**: Tools can enumerate available testbenches and sweeps

This centralized approach ensures that all simulation assets are explicitly declared and version-controlled.