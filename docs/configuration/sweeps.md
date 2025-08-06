# Sweep Definition Files

While `sim_setup.yaml` points to the *existence* of a sweep, the sweep definition file specifies *what* to sweep.

## Key Sections

### `testbench`
A mandatory string that specifies which testbench from `sim_setup.yaml` to use as the base for this sweep (e.g., `dc`).

### `parameters`
A dictionary where each key is a parameter to be swept and the value is a list of values for that parameter. The generator script will compute the Cartesian product of all these lists to create the individual simulation cases.

## Example

```yaml
# sweeps/pvt_dc.yaml
testbench: dc
parameters:
  vdda: [3.0, 3.3, 3.6]
  temp: [-40, 25, 125]
  model_corner: ["ff", "ss", "tt"]
```

This example creates 3 × 3 × 3 = 27 simulation cases, one for each combination of:
- Supply voltage (`vdda`)
- Temperature (`temp`)  
- Process corner (`model_corner`)

## Parameter Overriding

The parameters defined in the sweep file are treated as **overrides** to the default values found in the base testbench's `config.yaml`. 

- Any parameter not specified in the sweep file will retain its default value from the `config.yaml`
- Any parameter being swept must already exist in the base `config.yaml`

This separation of concerns—using one file to define the environment and another to define the experiment—is key to the system's flexibility.

## Advanced Parameter Definitions

### Range Specifications

```yaml
parameters:
  vdda: 
    type: range
    start: 3.0
    stop: 3.6
    num: 5  # Creates [3.0, 3.15, 3.3, 3.45, 3.6]
  
  temp: [-40, 25, 125]  # Explicit list
```

### Logarithmic Ranges

```yaml
parameters:
  frequency:
    type: logspace
    start: 1e3    # 1 kHz
    stop: 1e9     # 1 GHz  
    num: 50
```

## Sweep Naming Conventions

- Use descriptive names that indicate the sweep purpose: `pvt_dc`, `bandwidth_sweep`, `power_corners`
- Include the base testbench name for clarity: `ac_frequency_sweep`, `dc_bias_sweep`
- Store related sweeps in subdirectories: `sweeps/pvt/`, `sweeps/monte_carlo/`