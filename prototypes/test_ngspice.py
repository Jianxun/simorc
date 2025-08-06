#!/usr/bin/env python3
"""
Test script to verify ngspice toolchain integration with wave_view
"""

import subprocess
import sys
from pathlib import Path
import wave_view

def run_ngspice_simulation(netlist_path):
    """Run ngspice simulation and return results."""
    try:
        # Run ngspice with the netlist
        result = subprocess.run(
            ['ngspice', '-b', str(netlist_path)],
            capture_output=True,
            text=True,
            cwd=netlist_path.parent
        )
        
        print("NGSPICE OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("NGSPICE ERRORS:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("Error: ngspice not found in PATH")
        return False
    except Exception as e:
        print(f"Error running ngspice: {e}")
        return False

def test_wave_view_parsing(raw_file_path):
    """Test parsing raw file with wave_view CLI tool."""
    try:
        if not raw_file_path.exists():
            print(f"Error: Raw file {raw_file_path} not found")
            return False
            
        # Use waveview CLI to inspect the raw file
        print(f"\nTesting waveview CLI parsing of {raw_file_path}")
        
        # Run waveview signals command
        result = subprocess.run(
            ['waveview', 'signals', str(raw_file_path)],
            capture_output=True,
            text=True,
            cwd=raw_file_path.parent
        )
        
        if result.returncode != 0:
            print(f"waveview signals failed: {result.stderr}")
            return False
            
        print("WAVEVIEW OUTPUT:")
        print(result.stdout)
        
        # Check if we found expected signals
        output = result.stdout
        expected_signals = ['time', 'v(in)', 'v(out)', 'i(v1)']
        
        for signal in expected_signals:
            if signal in output:
                print(f"✓ Found expected signal: {signal}")
            else:
                print(f"✗ Missing expected signal: {signal}")
                return False
        
        print("waveview parsing successful!")
        return True
        
    except Exception as e:
        print(f"Error parsing with waveview: {e}")
        return False

def main():
    """Main test function."""
    script_dir = Path(__file__).parent
    netlist_file = script_dir / "rc_circuit.cir"
    raw_file = script_dir / "rc_circuit.raw"
    
    print("Testing ngspice toolchain integration...")
    print(f"Netlist: {netlist_file}")
    
    # Test 1: Run ngspice simulation
    print("\n=== Test 1: Running ngspice simulation ===")
    if not run_ngspice_simulation(netlist_file):
        print("❌ ngspice simulation failed")
        return 1
    
    print("✅ ngspice simulation completed")
    
    # Test 2: Check if raw file was created
    print("\n=== Test 2: Checking raw file creation ===")
    if not raw_file.exists():
        print(f"❌ Raw file {raw_file} was not created")
        return 1
    
    print(f"✅ Raw file created: {raw_file}")
    
    # Test 3: Test wave_view parsing
    print("\n=== Test 3: Testing wave_view parsing ===")
    if not test_wave_view_parsing(raw_file):
        print("❌ wave_view parsing failed")
        return 1
    
    print("✅ wave_view parsing successful")
    
    print("\n🎉 All tests passed! ngspice toolchain is working.")
    return 0

if __name__ == "__main__":
    sys.exit(main())