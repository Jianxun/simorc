# Configuration Validation

To prevent common errors from typos or incorrect data types in the YAML configuration files, the system uses `pydantic` for comprehensive validation.

## Schema Enforcement

For each type of configuration file (`sim_setup.yaml`, sweep definitions, and `config.yaml`), a corresponding `pydantic` model is defined in the core library.

## Early Failure

Before any processing occurs, `simorc` loads the YAML files and parses them using these models. If there are any validation errors (e.g., a missing required field, a string where a number is expected), the tool will exit immediately with a clear, user-friendly error message indicating the exact location of the problem.

## Validation Command

Use `simorc validate` to check your configuration:

```bash
simorc validate
```

Example output for a valid configuration:
```
✓ sim_setup.yaml is valid
✓ sweep pvt_dc is valid  
✓ testbench dc is valid
✓ testbench ac is valid

Configuration validation passed!
```

Example output with errors:
```
✗ Error in sim_setup.yaml:
  - dut.netlist: File './netlists/missing.spice' does not exist
  
✗ Error in sweeps/pvt_dc.yaml:
  - parameters.vdda: Expected list, got string
  - testbench: 'invalid_tb' not found in sim_setup.yaml
  
✗ Error in testbenches/dc/config.yaml:
  - parameters.vdda: Expected number, got string 'invalid'

Configuration validation failed with 4 errors.
```

## Validation Rules

### `sim_setup.yaml`

- **Required fields**: `dut`, `testbenches`, `sweeps`
- **File existence**: All referenced files and directories must exist
- **Path validation**: Relative paths must be valid from sim_setup.yaml location

### Sweep Files

- **Required fields**: `testbench`, `parameters`
- **Testbench reference**: Must reference a testbench defined in sim_setup.yaml
- **Parameter types**: Parameter values must be lists or valid range specifications
- **Parameter existence**: All swept parameters must exist in base testbench config

### Testbench `config.yaml`

- **Required fields**: `schematic`, `template`, `parameters`
- **File existence**: Referenced schematic and template files must exist
- **Parameter types**: Default parameter values must have correct types
- **Template validation**: Jinja2 template syntax must be valid

## Custom Validation

You can extend validation by creating custom validators:

```python
# In your project
from simorc.config import BaseConfig
from pydantic import validator

class CustomTestbenchConfig(BaseConfig):
    """Extended testbench configuration with custom validation."""
    
    @validator('parameters')
    def validate_voltage_range(cls, v):
        if 'vdda' in v and not (0.5 <= v['vdda'] <= 5.0):
            raise ValueError('vdda must be between 0.5V and 5.0V')
        return v
```

## Benefits

This enforces configuration correctness and provides a better user experience by:

- **Catching errors early**: Before any time-consuming simulation work begins
- **Clear error messages**: Pinpoint exact location and nature of problems
- **Type safety**: Ensure numeric parameters are actually numbers
- **File validation**: Verify all referenced files exist before processing
- **Cross-reference validation**: Ensure sweep parameters exist in testbench configs