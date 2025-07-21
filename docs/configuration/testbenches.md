# Testbench Configuration

Each directory referenced in the `testbenches` section of `sim_setup.yaml` acts as a self-contained testbench. At its core, a testbench consists of a schematic (`.sch` file) created in a tool like `xschem`, which defines the test setup.

## From Schematic to Template

A key feature of the workflow is the ability to embed Jinja2 placeholders (e.g., `{{ parameters.vdda }}`) directly within the schematic. The simulation netlist is generated from this schematic. This netlist, with the Jinja2 placeholders preserved, becomes the **template netlist** for the testbench. This process allows a single, readable schematic to serve as the source of truth for a configurable netlist.

## Testbench `config.yaml`

Each testbench directory must contain a `config.yaml` file that orchestrates its behavior. It contains:

- **`schematic`**: The path to the source schematic file.
- **`template`**: The path to the generated template netlist.
- **`parameters`**: Default values for all parameters used in the template (e.g., `vdda`, `corner`).
- Other metadata needed for post-processing, like plot specifications.

## Example: `testbenches/dc/config.yaml`

```yaml
# Points to the source schematic and the target template
schematic: ./tb_dc.sch
template: ./tb_dc.spice.j2

# Default parameters for a DC operating point simulation
parameters:
  vdda: 3.3
  vin_dc: 1.5
  i_bias: 5e-05
  corner: typical

plot_specs:
  dc_tf: ./plots/dc_tf.yaml
```

## Template Netlist Example

The template netlist (`tb_dc.spice.j2`) contains Jinja2 placeholders:

```spice
* DC Operating Point Testbench
.title DC Analysis of OTA

* Supply voltage
Vdd vdd 0 {{ parameters.vdda }}

* Input bias
Vin vin 0 DC {{ parameters.vin_dc }}

* Bias current source  
Ibias vdd nbias {{ parameters.i_bias }}

* Include DUT
.include {{ dut.netlist }}

* Include process models
.include models_{{ parameters.corner }}.spice

* Analysis
.op
.dc Vin 0 {{ parameters.vdda }} 0.1

.control
run
write {{ result_file }}
.endc

.end
```

## Directory Structure

A typical testbench directory structure:

```
testbenches/dc/
├── config.yaml          # Testbench configuration
├── tb_dc.sch            # Source schematic (xschem)
├── tb_dc.spice.j2       # Template netlist with Jinja2 placeholders
└── plots/
    └── dc_tf.yaml       # Plot specifications for results
```

## Plot Specifications

Plot specifications define how to visualize results:

```yaml
# plots/dc_tf.yaml
title: "DC Transfer Function"
x_axis:
  signal: "v(vin)"
  label: "Input Voltage (V)"
y_axis:
  signal: "v(vout)"
  label: "Output Voltage (V)"
grid: true
```

## Best Practices

1. **Use descriptive parameter names**: `vdda` instead of `v1`, `temp` instead of `t`
2. **Include units in comments**: `# Temperature in Celsius`
3. **Provide sensible defaults**: Choose typical operating conditions
4. **Validate parameter ranges**: Add comments about valid ranges
5. **Keep templates simple**: Complex logic should be in metrics scripts, not netlists