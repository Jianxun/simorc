# Planned Analyzer Architecture

**Implementation Status**: 🚧 **PLANNED** - Architecture designed, implementation pending

## HDF5 Data Schema

The analyzer will output results in a structured HDF5 format:

```
sweep_results.h5
├── /metadata/              # Sweep configuration and execution info
├── /cases/case_N/          # Individual case results
│   ├── /scalars/           # Extracted metrics (bandwidth, gain, etc.)
│   ├── /waveforms/         # Processed signals (freq response, etc.)
│   └── attributes          # Case parameters and status
└── /aggregated/            # Cross-case analysis and summaries
```

## Metrics Configuration

Metrics will be defined in testbench configuration files:

```yaml
# testbench/config.yaml
metrics:
  bandwidth_3db:
    script: "./metrics/bandwidth_3db.py"
    signals: ["frequency", "v(vout)"]
    target: 10e6
    tolerance: 0.1
  
  gain_dc:
    script: "./metrics/dc_gain.py"
    signals: ["v(vout)", "v(vin)"]
    target: 40.0
    tolerance: 2.0

  phase_margin:
    script: "./metrics/phase_margin.py"
    signals: ["frequency", "v(vout)"]
    target: 60.0
    tolerance: 10.0
```

## Metrics Scripts

Users will define custom metrics through Python scripts:

```python
# metrics/bandwidth_3db.py
import numpy as np
from scipy import signal

def calculate_metric(data, config):
    """
    Calculate 3dB bandwidth from frequency response data.
    
    Args:
        data: Dictionary with signal arrays
        config: Metric configuration from config.yaml
    
    Returns:
        float: 3dB bandwidth in Hz
    """
    freq = data['frequency']
    vout = data['v(vout)']
    
    # Convert to magnitude in dB
    mag_db = 20 * np.log10(np.abs(vout))
    
    # Find DC gain
    dc_gain = mag_db[0]
    
    # Find 3dB point
    target_db = dc_gain - 3.0
    
    # Find frequency where gain drops to 3dB below DC
    idx = np.where(mag_db <= target_db)[0]
    if len(idx) > 0:
        return freq[idx[0]]
    else:
        return np.nan
```

## Tool Integration Contract

The HDF5 output serves as a standardized interface for downstream tools:

- **Visualization**: Any tool can read HDF5 for plotting (waveview, matplotlib, etc.)
- **Reporting**: Automated report generation from structured data
- **Archival**: Single-file storage of complete sweep results with metadata

## Analysis Workflow

1. **Raw File Parsing**: Native SPICE raw file parsing using `spicelib` or `ltspice`
2. **Metrics Extraction**: Execute user-defined Python scripts for each case
3. **Waveform Processing**: Extract and process waveforms (FFT, filtering, derived signals)
4. **Data Aggregation**: Combine all results into structured HDF5 format
5. **Summary Generation**: Create aggregate statistics and pass/fail matrices

## Expected Outputs

- `sweep_results.h5` (structured HDF5 with all data and metadata)
- Scalar metrics per case (bandwidth, gain, phase margin)
- Processed waveforms (frequency response, transients, noise)
- Aggregated sweep statistics and parameter correlations

## Benefits

- **Self-Contained**: Native raw file parsing, no external tool dependencies
- **User-Extensible**: Custom metrics via Python scripts
- **Structured Output**: HDF5 format with hierarchical data organization
- **Rich Metadata**: Full configuration and parameter tracking
- **Tool Agnostic**: Clear contract for downstream visualization/reporting tools