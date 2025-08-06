#!/usr/bin/env python3
"""
Serialization troubleshooting script for xarray datasets with object arrays.

Tests different file formats and data structures to find the best solution
for storing variable-length simulation data.
"""

import numpy as np
import xarray as xr
import pickle
import json
from pathlib import Path


def create_test_dataset():
    """Create a small test dataset similar to our simulation data."""
    # Create coordinates
    R_values = ['100', '1k', '10k']
    C_values = ['100p', '1n', '10n']
    
    # Create object arrays for variable-length data
    coords = {'R': R_values, 'C': C_values}
    
    # Simulate frequency data (each case has same length, but could vary)
    freq_data = np.empty((3, 3), dtype=object)
    vin_data = np.empty((3, 3), dtype=object)
    vout_data = np.empty((3, 3), dtype=object)
    
    for i, R in enumerate(R_values):
        for j, C in enumerate(C_values):
            # Create test data (in real case, these come from .raw files)
            n_points = 51  # Could be variable length
            freq_array = np.logspace(3, 8, n_points) + 0j  # Complex frequency
            vin_array = np.ones(n_points) + 0j              # Complex voltage
            vout_array = np.random.random(n_points) + 1j * np.random.random(n_points)
            
            freq_data[i, j] = freq_array
            vin_data[i, j] = vin_array
            vout_data[i, j] = vout_array
    
    # Create xarray Dataset
    data_vars = {
        'frequency': (['R', 'C'], freq_data),
        'vin': (['R', 'C'], vin_data),
        'vout': (['R', 'C'], vout_data)
    }
    
    dataset = xr.Dataset(data_vars, coords=coords)
    dataset.attrs['description'] = 'Test dataset for serialization'
    
    return dataset


def test_netcdf_serialization(dataset, output_dir):
    """Test netCDF4 serialization (expected to fail with object arrays)."""
    print("=== Testing netCDF4 (.nc) Serialization ===")
    output_path = output_dir / 'test_dataset.nc'
    
    try:
        dataset.to_netcdf(output_path)
        print(f"✅ Saved to: {output_path}")
        
        # Try to reload
        reloaded = xr.open_dataset(output_path)
        print(f"Reloaded dataset:")
        print(reloaded)
        print(f"Data variables: {list(reloaded.data_vars)}")
        reloaded.close()
        
        return True
        
    except Exception as e:
        print(f"❌ netCDF4 serialization failed: {e}")
        return False


def test_pickle_serialization(dataset, output_dir):
    """Test pickle serialization (should work)."""
    print("\n=== Testing Pickle (.pkl) Serialization ===")
    output_path = output_dir / 'test_dataset.pkl'
    
    try:
        with open(output_path, 'wb') as f:
            pickle.dump(dataset, f)
        print(f"✅ Saved to: {output_path}")
        
        # Try to reload
        with open(output_path, 'rb') as f:
            reloaded = pickle.load(f)
        print(f"Reloaded dataset:")
        print(reloaded)
        print(f"Data variables: {list(reloaded.data_vars)}")
        
        # Test data access
        sample_data = reloaded.vin.sel(R='1k', C='1n').item()
        print(f"Sample data shape: {sample_data.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pickle serialization failed: {e}")
        return False


def test_zarr_serialization(dataset, output_dir):
    """Test Zarr serialization (modern alternative to netCDF)."""
    print("\n=== Testing Zarr (.zarr) Serialization ===")
    output_path = output_dir / 'test_dataset.zarr'
    
    try:
        dataset.to_zarr(output_path)
        print(f"✅ Saved to: {output_path}")
        
        # Try to reload
        reloaded = xr.open_zarr(output_path)
        print(f"Reloaded dataset:")
        print(reloaded)
        print(f"Data variables: {list(reloaded.data_vars)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Zarr serialization failed: {e}")
        return False


def test_flattened_netcdf(dataset, output_dir):
    """Test netCDF with flattened data structure."""
    print("\n=== Testing Flattened netCDF Structure ===")
    output_path = output_dir / 'test_dataset_flat.nc'
    
    try:
        # Flatten the object arrays into a different structure
        flat_data = {}
        
        # Create a case dimension instead of object arrays
        n_cases = len(dataset.coords['R']) * len(dataset.coords['C'])
        case_names = []
        
        # Extract all data into regular arrays
        max_length = 0
        all_signals = {}
        
        # First pass: find maximum length and collect all data
        for i, R in enumerate(dataset.coords['R'].values):
            for j, C in enumerate(dataset.coords['C'].values):
                case_name = f"R{R}_C{C}"
                case_names.append(case_name)
                
                for var_name in dataset.data_vars:
                    if var_name not in all_signals:
                        all_signals[var_name] = []
                    
                    signal_data = dataset[var_name].isel(R=i, C=j).item()
                    all_signals[var_name].append(signal_data)
                    max_length = max(max_length, len(signal_data))
        
        print(f"Max signal length: {max_length}")
        print(f"Number of cases: {len(case_names)}")
        
        # Second pass: create padded arrays
        coords_flat = {
            'case': case_names,
            'sample': np.arange(max_length)
        }
        
        data_vars_flat = {}
        for var_name, signal_list in all_signals.items():
            # Create 2D array: [case, sample]
            padded_array = np.full((len(case_names), max_length), np.nan, dtype=complex)
            
            for case_idx, signal_data in enumerate(signal_list):
                padded_array[case_idx, :len(signal_data)] = signal_data
            
            data_vars_flat[var_name] = (['case', 'sample'], padded_array)
        
        # Create flattened dataset
        flat_dataset = xr.Dataset(data_vars_flat, coords=coords_flat)
        flat_dataset.attrs = dataset.attrs.copy()
        flat_dataset.attrs['structure'] = 'flattened'
        
        print("Flattened dataset structure:")
        print(flat_dataset)
        
        # Save to netCDF - try splitting complex into real/imag
        try:
            # Split complex variables into real and imaginary parts
            real_data_vars = {}
            for var_name, var_data in data_vars_flat.items():
                real_array = padded_array.real
                imag_array = padded_array.imag
                real_data_vars[f"{var_name}_real"] = (['case', 'sample'], real_array)
                real_data_vars[f"{var_name}_imag"] = (['case', 'sample'], imag_array)
            
            real_dataset = xr.Dataset(real_data_vars, coords=coords_flat)
            real_dataset.attrs = dataset.attrs.copy()
            real_dataset.attrs['structure'] = 'flattened_real_imag'
            
            real_dataset.to_netcdf(output_path)
            print(f"✅ Saved to: {output_path}")
        except Exception as e:
            print(f"Complex splitting failed: {e}")
            # Fallback: convert to float by taking magnitude
            float_data_vars = {}
            for var_name, (dims, data) in data_vars_flat.items():
                float_data_vars[f"{var_name}_magnitude"] = (dims, np.abs(data).astype(float))
            
            float_dataset = xr.Dataset(float_data_vars, coords=coords_flat)
            float_dataset.attrs = dataset.attrs.copy()
            float_dataset.attrs['structure'] = 'flattened_magnitude'
            
            float_dataset.to_netcdf(output_path)
            print(f"✅ Saved magnitude data to: {output_path}")
        
        # Try to reload
        reloaded = xr.open_dataset(output_path)
        print(f"Reloaded flattened dataset:")
        print(reloaded)
        reloaded.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Flattened netCDF failed: {e}")
        return False


def test_hdf5_serialization(dataset, output_dir):
    """Test HDF5 serialization using h5py."""
    print("\n=== Testing HDF5 (.h5) Serialization ===")
    output_path = output_dir / 'test_dataset.h5'
    
    try:
        import h5py
        
        with h5py.File(output_path, 'w') as f:
            # Save coordinates
            coord_group = f.create_group('coordinates')
            for coord_name, coord_data in dataset.coords.items():
                coord_group.create_dataset(coord_name, data=coord_data.values.astype('S'))
            
            # Save data variables
            data_group = f.create_group('data_variables')
            for var_name, var_data in dataset.data_vars.items():
                var_group = data_group.create_group(var_name)
                
                # Save each signal separately with case indices
                for i, R in enumerate(dataset.coords['R'].values):
                    for j, C in enumerate(dataset.coords['C'].values):
                        case_name = f"R{i}_C{j}"
                        signal_data = var_data.isel(R=i, C=j).item()
                        var_group.create_dataset(case_name, data=signal_data)
            
            # Save attributes
            for attr_name, attr_value in dataset.attrs.items():
                f.attrs[attr_name] = attr_value
        
        print(f"✅ Saved to: {output_path}")
        
        # Try to reload and inspect
        with h5py.File(output_path, 'r') as f:
            print("HDF5 file structure:")
            def print_structure(name, obj):
                print(f"  {name}: {type(obj).__name__}")
            f.visititems(print_structure)
        
        return True
        
    except ImportError:
        print("❌ h5py not available")
        return False
    except Exception as e:
        print(f"❌ HDF5 serialization failed: {e}")
        return False


def test_json_serialization(dataset, output_dir):
    """Test JSON serialization (convert to nested dict)."""
    print("\n=== Testing JSON (.json) Serialization ===")
    output_path = output_dir / 'test_dataset.json'
    
    try:
        # Convert dataset to nested dictionary
        data_dict = {
            'coordinates': {name: coord.values.tolist() for name, coord in dataset.coords.items()},
            'data_variables': {},
            'attributes': dict(dataset.attrs)
        }
        
        # Convert data variables
        for var_name, var_data in dataset.data_vars.items():
            data_dict['data_variables'][var_name] = {}
            
            for i, R in enumerate(dataset.coords['R'].values):
                for j, C in enumerate(dataset.coords['C'].values):
                    case_key = f"R{R}_C{C}"
                    signal_data = var_data.isel(R=i, C=j).item()
                    
                    # Convert complex arrays to [real, imag] pairs
                    if np.iscomplexobj(signal_data):
                        data_dict['data_variables'][var_name][case_key] = {
                            'real': signal_data.real.tolist(),
                            'imag': signal_data.imag.tolist()
                        }
                    else:
                        data_dict['data_variables'][var_name][case_key] = signal_data.tolist()
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        print(f"✅ Saved to: {output_path}")
        
        # Check file size
        file_size = output_path.stat().st_size
        print(f"File size: {file_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False


def main():
    """Run all serialization tests."""
    print("🧪 xarray Dataset Serialization Test Suite")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("prototypes/serialization_tests")
    output_dir.mkdir(exist_ok=True)
    
    # Create test dataset
    print("Creating test dataset...")
    dataset = create_test_dataset()
    print(f"Test dataset:")
    print(dataset)
    print(f"Sample data type: {type(dataset.vin.isel(R=0, C=0).item())}")
    print(f"Sample data shape: {dataset.vin.isel(R=0, C=0).item().shape}")
    
    # Test different serialization methods
    results = {}
    results['netcdf'] = test_netcdf_serialization(dataset, output_dir)
    results['pickle'] = test_pickle_serialization(dataset, output_dir)
    results['zarr'] = test_zarr_serialization(dataset, output_dir)
    results['flattened_netcdf'] = test_flattened_netcdf(dataset, output_dir)
    results['hdf5'] = test_hdf5_serialization(dataset, output_dir)
    results['json'] = test_json_serialization(dataset, output_dir)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SERIALIZATION TEST RESULTS")
    print("=" * 50)
    for method, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{method:20s}: {status}")
    
    print(f"\n📁 Test files saved to: {output_dir}")
    print("\n💡 RECOMMENDATIONS:")
    if results['zarr']:
        print("1. 🥇 Zarr: Best modern alternative to netCDF for complex data")
    if results['flattened_netcdf']:
        print("2. 🥈 Flattened netCDF: Compatible with existing netCDF tools")
    if results['pickle']:
        print("3. 🥉 Pickle: Python-specific but preserves exact structure")


if __name__ == '__main__':
    main()