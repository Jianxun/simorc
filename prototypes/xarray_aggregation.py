#!/usr/bin/env python3
"""
xarray Aggregation Prototype for simorc Phase 5

This script demonstrates aggregating simulation results from multiple parameter
cases into an xarray Dataset. It uses:
- metadata.csv for parameter coordinates (R, C values)
- config.yaml for signal mapping (canonical names to SPICE expressions)
- spicelib directly for raw file signal extraction
- xarray for multidimensional data organization
"""

import csv
from pathlib import Path
import yaml
import numpy as np
import xarray as xr


def parse_metadata_csv(metadata_path):
    """Parse metadata.csv to extract parameter coordinates and case info."""
    cases = []
    with open(metadata_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append({
                'case_id': int(row['case_id']),
                'R': row['R'],
                'C': row['C'],
                'result_file': row['result_file']
            })
    
    # Extract unique parameter values for coordinates
    R_values = sorted(list(set(case['R'] for case in cases)))
    C_values = sorted(list(set(case['C'] for case in cases)))
    
    print(f"Found {len(cases)} cases")
    print(f"R values: {R_values}")
    print(f"C values: {C_values}")
    
    return cases, R_values, C_values


def parse_config_yaml(config_path):
    """Parse testbench config.yaml to get signal mapping."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'postprocess' not in config or 'signals' not in config['postprocess']:
        raise ValueError("No postprocess.signals found in config.yaml")
    
    signals = config['postprocess']['signals']
    print(f"Signal mapping: {signals}")
    return signals


def extract_signals_direct(raw_file_path, signal_expressions):
    """Use spicelib directly to extract signal data from raw file."""
    from spicelib import RawRead
    
    try:
        # Load the raw file directly using spicelib
        raw_data = RawRead(str(raw_file_path))
    except FileNotFoundError:
        raise FileNotFoundError(f"SPICE raw file not found: {raw_file_path}")
    except Exception as e:
        raise Exception(f"Failed to read SPICE raw file '{raw_file_path}': {e}")
    
    # Get available signals (trace names)
    available_signals = raw_data.get_trace_names()
    print(f"Available signals in {raw_file_path}: {available_signals}")
    
    # Extract each signal using spicelib
    signal_data = {}
    
    
    for signal_name, spice_expr in signal_expressions.items():
        print(f"Extracting {signal_name}: {spice_expr}")
        
        # Find the signal (case-insensitive matching)
        original_name = None
        for signal in available_signals:
            if signal.lower() == spice_expr.lower():
                original_name = signal
                break
        
        if original_name is None:
            print(f"Warning: Failed to find signal {signal_name} ({spice_expr}) in available signals")
            continue
            
        try:
            # Get trace data and convert to numpy array
            trace = raw_data.get_trace(original_name)
            data = np.array(trace)
            signal_data[signal_name] = data
            print(f"  Extracted {len(data)} data points, shape: {data.shape}")
        except Exception as e:
            print(f"Warning: Failed to extract {signal_name} ({spice_expr}): {e}")
            continue
    
    # Also extract frequency as the independent variable
    freq_signal = None
    for signal in available_signals:
        if signal.lower() == 'frequency':
            freq_signal = signal
            break
    
    if freq_signal:
        try:
            freq_trace = raw_data.get_trace(freq_signal)
            freq_data = np.array(freq_trace)
            signal_data['frequency'] = freq_data
            print(f"  Extracted frequency with {len(freq_data)} points, shape: {freq_data.shape}")
        except Exception as e:
            print(f"Warning: Failed to extract frequency: {e}")
    else:
        print("Warning: No frequency signal found")
    
    return signal_data


def create_xarray_dataset(cases, R_values, C_values, all_signal_data):
    """Create xarray Dataset from extracted signal data."""
    
    # Prepare data arrays for each signal
    # Since frequency sweeps might have different lengths, we'll use object arrays
    signal_names = list(all_signal_data[0].keys()) if all_signal_data else []
    print(f"Creating dataset with signals: {signal_names}")
    
    # Create coordinate arrays
    coords = {
        'R': R_values,
        'C': C_values
    }
    
    # Initialize data variables with object dtype to handle variable-length arrays
    data_vars = {}
    
    for signal_name in signal_names:
        # Create empty object array with R,C dimensions
        signal_array = np.empty((len(R_values), len(C_values)), dtype=object)
        
        # Fill in the data for each case
        for i, case in enumerate(cases):
            R_idx = R_values.index(case['R'])
            C_idx = C_values.index(case['C'])
            
            if signal_name in all_signal_data[i]:
                signal_array[R_idx, C_idx] = all_signal_data[i][signal_name]
            else:
                signal_array[R_idx, C_idx] = np.array([])  # Empty array for missing data
        
        data_vars[signal_name] = (['R', 'C'], signal_array)
    
    # Create the xarray Dataset
    dataset = xr.Dataset(data_vars, coords=coords)
    
    # Add metadata
    dataset.attrs['description'] = 'RC low-pass filter simulation results'
    dataset.attrs['simulation_type'] = 'AC analysis'
    dataset.attrs['n_cases'] = len(cases)
    
    return dataset


def main():
    """Main aggregation workflow."""
    # Define paths relative to this script
    script_dir = Path(__file__).parent
    rc_results_dir = script_dir.parent / 'example' / 'rc' / 'results' / 'rc_values'
    config_path = script_dir.parent / 'example' / 'rc' / 'testbenches' / 'ac' / 'config.yaml'
    
    print("=== xarray Aggregation Prototype ===")
    print(f"Results directory: {rc_results_dir}")
    print(f"Config path: {config_path}")
    
    # Step 1: Parse metadata.csv
    metadata_path = rc_results_dir / 'metadata.csv'
    cases, R_values, C_values = parse_metadata_csv(metadata_path)
    
    # Step 2: Parse config.yaml for signal mapping
    signals = parse_config_yaml(config_path)
    
    # Step 3: Extract signals from each case
    all_signal_data = []
    for case in cases:
        raw_file_path = rc_results_dir / case['result_file']
        print(f"\n--- Processing Case {case['case_id']}: R={case['R']}, C={case['C']} ---")
        
        try:
            signal_data = extract_signals_direct(raw_file_path, signals)
            all_signal_data.append(signal_data)
        except Exception as e:
            print(f"Error processing case {case['case_id']}: {e}")
            all_signal_data.append({})  # Empty dict for failed cases
    
    # Step 4: Create xarray Dataset
    print(f"\n--- Creating xarray Dataset ---")
    dataset = create_xarray_dataset(cases, R_values, C_values, all_signal_data)
    
    # Step 5: Display dataset info
    print(f"\n--- Dataset Summary ---")
    print(dataset)
    print(f"\nDataset dimensions: {dict(dataset.dims)}")
    print(f"Dataset coordinates: {list(dataset.coords)}")
    print(f"Dataset variables: {list(dataset.data_vars)}")
    
    # Step 6: Test data access patterns
    print(f"\n--- Testing Data Access ---")
    try:
        # Test parameter slicing
        case_data = dataset.sel(R="1k", C="1n")
        print(f"Case R=1k, C=1n data variables: {list(case_data.data_vars)}")
        
        # Test signal access - need to extract the array from the object first
        if 'vin' in dataset.data_vars:
            vin_1k_1n = dataset.vin.sel(R="1k", C="1n").item()  # .item() extracts the array from object
            print(f"vin signal for R=1k, C=1n: {len(vin_1k_1n)} points, type: {type(vin_1k_1n)}")
            print(f"Sample vin values: {vin_1k_1n[:3]}")
            
        if 'frequency' in dataset.data_vars:
            freq_1k_1n = dataset.frequency.sel(R="1k", C="1n").item()
            print(f"frequency for R=1k, C=1n: {len(freq_1k_1n)} points, type: {type(freq_1k_1n)}")
            print(f"Sample frequency values: {freq_1k_1n[:3]}")
            
    except Exception as e:
        print(f"Error in data access test: {e}")
    
    # Step 7: Test alternative storage format - pickle for now since netCDF4 has issues with object arrays
    print(f"\n--- Testing Persistence ---")
    output_path = rc_results_dir / 'dataset.pkl'
    try:
        # Save using pickle since netCDF4 doesn't handle object arrays well
        import pickle
        with open(output_path, 'wb') as f:
            pickle.dump(dataset, f)
        print(f"Saved dataset to: {output_path}")
        
        # Test reload
        with open(output_path, 'rb') as f:
            reloaded = pickle.load(f)
        print(f"Successfully reloaded dataset using pickle")
        print(f"Reloaded dimensions: {dict(reloaded.sizes)}")
        print(f"Reloaded variables: {list(reloaded.data_vars)}")
        
        # Test accessing reloaded data
        vin_reloaded = reloaded.vin.sel(R="1k", C="1n").item()
        print(f"Reloaded vin signal: {len(vin_reloaded)} points")
        
    except Exception as e:
        print(f"Error in persistence test: {e}")
    
    # Step 8: Show how to work with the data for analysis
    print(f"\n--- Example Analysis Usage ---")
    try:
        print("Frequency response analysis example:")
        for R_val in R_values[:2]:  # Just show first 2 R values
            for C_val in C_values[:2]:  # Just show first 2 C values
                freq = dataset.frequency.sel(R=R_val, C=C_val).item()
                vin = dataset.vin.sel(R=R_val, C=C_val).item()
                vout = dataset.vout.sel(R=R_val, C=C_val).item()
                
                # Calculate magnitude response
                gain = np.abs(vout / vin)
                print(f"  R={R_val}, C={C_val}: DC gain={gain[0]:.3f}, gain at {freq[-1]:.0f}Hz = {gain[-1]:.3f}")
                
    except Exception as e:
        print(f"Error in analysis example: {e}")
    
    print(f"\n=== Prototype Complete ===")


if __name__ == '__main__':
    main()