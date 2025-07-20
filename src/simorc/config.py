"""Configuration models for simorc YAML files."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DutConfig(BaseModel):
    """Device Under Test configuration."""
    netlist: Path = Field(..., description="Path to DUT netlist file")


class TestbenchConfigModel(BaseModel):
    """Individual testbench configuration."""
    schematic: Optional[Path] = Field(None, description="Path to schematic file")
    template: Path = Field(..., description="Path to SPICE template file")
    filename_raw: str = Field("results.raw", description="Output raw file name")
    filename_log: str = Field("sim.log", description="Output log file name")
    parameters: Dict[str, Union[str, int, float]] = Field(default_factory=dict, description="Testbench parameters")
    plot_specs: Optional[Dict[str, Path]] = Field(None, description="Plot specification files")

    @field_validator('template')
    @classmethod
    def template_must_be_jinja2(cls, v):
        """Ensure template file has .j2 extension."""
        if not str(v).endswith('.j2'):
            raise ValueError('Template file must have .j2 extension')
        return v


class SweepConfig(BaseModel):
    """Parameter sweep configuration."""
    testbench: str = Field(..., description="Target testbench name")
    parameters: Dict[str, List[Union[str, int, float]]] = Field(..., description="Parameters to sweep")

    @field_validator('parameters')
    @classmethod
    def parameters_must_have_values(cls, v):
        """Ensure all parameters have at least one value."""
        for param, values in v.items():
            if not values:
                raise ValueError(f'Parameter {param} must have at least one value')
        return v


class SimSetupConfig(BaseModel):
    """Main simulation setup configuration."""
    model_config = ConfigDict(validate_assignment=True)
    
    dut: DutConfig = Field(..., description="Device Under Test configuration")
    testbenches: Dict[str, Path] = Field(..., description="Available testbenches")
    sweeps: Dict[str, Path] = Field(..., description="Available parameter sweeps")


class PlotConfig(BaseModel):
    """Plot specification configuration."""
    title: str = Field(..., description="Plot title")
    xlabel: str = Field(..., description="X-axis label")
    ylabel: str = Field(..., description="Y-axis label")
    signals: List[str] = Field(..., description="Signals to plot")
    plot_type: str = Field("linear", description="Plot type (linear, semilogx, semilogy, loglog)")
    grid: bool = Field(True, description="Show grid")
    legend: bool = Field(True, description="Show legend")