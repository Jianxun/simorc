#!/usr/bin/env python3
"""
Simple script to inspect dataset.nc file dimensions and coordinates.
"""

import xarray as xr
from pathlib import Path


def inspect_dataset(dataset_path):
    """Inspect xarray dataset file and print key information."""
    try:
        print(f"=== Inspecting {dataset_path} ===")
        
        # Try to open the dataset
        dataset = xr.open_dataset(dataset_path)
        
        print(f"\n--- Dataset Overview ---")
        print(dataset)
        
        print(f"\n--- Dimensions ---")
        for dim_name, dim_size in dataset.sizes.items():
            print(f"  {dim_name}: {dim_size}")
        
        print(f"\n--- Coordinates ---")
        for coord_name, coord_data in dataset.coords.items():
            print(f"  {coord_name}: {coord_data.values}")
        
        print(f"\n--- Data Variables ---")
        for var_name, var_data in dataset.data_vars.items():
            print(f"  {var_name}: {var_data.dims} - {var_data.dtype} - shape {var_data.shape}")
        
        print(f"\n--- Attributes ---")
        for attr_name, attr_value in dataset.attrs.items():
            print(f"  {attr_name}: {attr_value}")
        
        # Try to access some sample data
        print(f"\n--- Sample Data Access ---")
        if 'R' in dataset.coords and 'C' in dataset.coords:
            R_vals = list(dataset.coords['R'].values)
            C_vals = list(dataset.coords['C'].values)
            print(f"Available R values: {R_vals}")
            print(f"Available C values: {C_vals}")
            
            # Try to access one data point
            if R_vals and C_vals:
                sample_data = dataset.sel(R=R_vals[0], C=C_vals[0])
                print(f"Sample case (R={R_vals[0]}, C={C_vals[0]}):")
                for var in sample_data.data_vars:
                    var_value = sample_data[var].values
                    print(f"  {var}: {type(var_value)} - {var_value}")
        
        # Check if dataset is empty (common issue with object arrays in netCDF)
        if not dataset.data_vars:
            print(f"\nWarning: Dataset appears empty - this is likely due to object array incompatibility with netCDF4 format.")
            dataset.close()
            
            # Try pickle alternative
            pkl_path = dataset_path.with_suffix('.pkl')
            if pkl_path.exists():
                print(f"\nTrying alternative pickle format: {pkl_path}")
                inspect_pickle_dataset(pkl_path)
            else:
                print(f"Alternative pickle file not found: {pkl_path}")
        else:
            dataset.close()
            print(f"\n=== Inspection Complete ===")
        
    except Exception as e:
        print(f"Error reading dataset: {e}")
        print(f"This might be due to object array incompatibility with netCDF4 format.")
        
        # Suggest alternative
        pkl_path = dataset_path.with_suffix('.pkl')
        if pkl_path.exists():
            print(f"\nTrying alternative pickle format: {pkl_path}")
            inspect_pickle_dataset(pkl_path)
        else:
            print(f"Alternative pickle file not found: {pkl_path}")


def inspect_pickle_dataset(pkl_path):
    """Inspect pickle-saved xarray dataset."""
    try:
        import pickle
        
        print(f"\n=== Inspecting {pkl_path} (pickle format) ===")
        
        with open(pkl_path, 'rb') as f:
            dataset = pickle.load(f)
        
        print(f"\n--- Dataset Overview ---")
        print(dataset)
        
        print(f"\n--- Dimensions ---")
        for dim_name, dim_size in dataset.sizes.items():
            print(f"  {dim_name}: {dim_size}")
        
        print(f"\n--- Coordinates ---")
        for coord_name, coord_data in dataset.coords.items():
            print(f"  {coord_name}: {coord_data.values}")
        
        print(f"\n--- Data Variables ---")
        for var_name, var_data in dataset.data_vars.items():
            print(f"  {var_name}: {var_data.dims} - {var_data.dtype} - shape {var_data.shape}")
        
        print(f"\n--- Sample Data from Object Arrays ---")
        if 'vin' in dataset.data_vars:
            # Extract one signal array from object storage
            R_vals = list(dataset.coords['R'].values)
            C_vals = list(dataset.coords['C'].values)
            if R_vals and C_vals:
                vin_array = dataset.vin.sel(R=R_vals[0], C=C_vals[0]).item()
                print(f"vin signal (R={R_vals[0]}, C={C_vals[0]}): {len(vin_array)} points")
                print(f"  Data type: {type(vin_array)}")
                print(f"  Shape: {vin_array.shape}")
                print(f"  First 3 values: {vin_array[:3]}")
        
        print(f"\n=== Pickle Inspection Complete ===")
        
    except Exception as e:
        print(f"Error reading pickle dataset: {e}")


def main():
    """Main inspection function."""
    # Define path to dataset
    script_dir = Path(__file__).parent
    dataset_path = script_dir.parent / 'example' / 'rc' / 'results' / 'rc_values' / 'dataset.nc'
    
    if not dataset_path.exists():
        print(f"Dataset file not found: {dataset_path}")
        return
    
    inspect_dataset(dataset_path)


if __name__ == '__main__':
    main()