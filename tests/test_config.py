"""Tests for configuration models."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from simorc.config import (
    DutConfig,
    TestbenchConfigModel,
    SweepConfig,
    SimSetupConfig,
    PlotConfig
)


class TestDutConfig:
    """Test DUT configuration model."""

    def test_valid_dut_config(self):
        """Test valid DUT configuration."""
        config = DutConfig(netlist="./netlists/rc_lowpass.spice")
        assert config.netlist == Path("./netlists/rc_lowpass.spice")

    def test_dut_config_requires_netlist(self):
        """Test DUT configuration requires netlist."""
        with pytest.raises(ValidationError):
            DutConfig()


class TestTestbenchConfigModel:
    """Test testbench configuration model."""

    def test_valid_testbench_config(self):
        """Test valid testbench configuration."""
        config = TestbenchConfigModel(
            template="./tb_ac.spice.j2",
            parameters={"R": "1k", "C": "1n"}
        )
        assert config.template == Path("./tb_ac.spice.j2")
        assert config.parameters["R"] == "1k"
        assert config.filename_raw == "results.raw"  # default

    def test_testbench_config_custom_filenames(self):
        """Test testbench configuration with custom filenames."""
        config = TestbenchConfigModel(
            template="./tb.spice.j2",
            filename_raw="custom.raw",
            filename_log="custom.log"
        )
        assert config.filename_raw == "custom.raw"
        assert config.filename_log == "custom.log"

    def test_template_must_be_jinja2(self):
        """Test template file must have .j2 extension."""
        with pytest.raises(ValidationError, match="Template file must have .j2 extension"):
            TestbenchConfigModel(template="./template.spice")

    def test_testbench_config_requires_template(self):
        """Test testbench configuration requires template."""
        with pytest.raises(ValidationError):
            TestbenchConfigModel()


class TestSweepConfig:
    """Test sweep configuration model."""

    def test_valid_sweep_config(self):
        """Test valid sweep configuration."""
        config = SweepConfig(
            testbench="ac",
            parameters={"R": ["100", "1k", "10k"], "C": ["100p", "1n", "10n"]}
        )
        assert config.testbench == "ac"
        assert len(config.parameters["R"]) == 3
        assert len(config.parameters["C"]) == 3

    def test_sweep_config_requires_testbench(self):
        """Test sweep configuration requires testbench."""
        with pytest.raises(ValidationError):
            SweepConfig(parameters={"R": ["1k"]})

    def test_sweep_config_requires_parameters(self):
        """Test sweep configuration requires parameters."""
        with pytest.raises(ValidationError):
            SweepConfig(testbench="ac")

    def test_parameters_must_have_values(self):
        """Test parameters must have at least one value."""
        with pytest.raises(ValidationError, match="Parameter R must have at least one value"):
            SweepConfig(testbench="ac", parameters={"R": []})


class TestSimSetupConfig:
    """Test main simulation setup configuration model."""

    def test_valid_sim_setup_config(self):
        """Test valid simulation setup configuration."""
        config = SimSetupConfig(
            dut={"netlist": "./netlists/rc_lowpass.spice"},
            testbenches={"ac": "./testbenches/ac", "tran": "./testbenches/tran"},
            sweeps={"rc_values": "./sweeps/rc_sweep/sweep_rc_values.yaml"}
        )
        assert isinstance(config.dut, DutConfig)
        assert config.dut.netlist == Path("./netlists/rc_lowpass.spice")
        assert "ac" in config.testbenches
        assert "rc_values" in config.sweeps

    def test_sim_setup_config_requires_all_fields(self):
        """Test simulation setup configuration requires all fields."""
        with pytest.raises(ValidationError):
            SimSetupConfig()

        with pytest.raises(ValidationError):
            SimSetupConfig(dut={"netlist": "./test.spice"})


class TestPlotConfig:
    """Test plot configuration model."""

    def test_valid_plot_config(self):
        """Test valid plot configuration."""
        config = PlotConfig(
            title="Bode Plot",
            xlabel="Frequency (Hz)",
            ylabel="Magnitude (dB)",
            signals=["v(out)"]
        )
        assert config.title == "Bode Plot"
        assert config.plot_type == "linear"  # default
        assert config.grid is True  # default
        assert len(config.signals) == 1

    def test_plot_config_custom_settings(self):
        """Test plot configuration with custom settings."""
        config = PlotConfig(
            title="Custom Plot",
            xlabel="Time (s)",
            ylabel="Voltage (V)",
            signals=["v(in)", "v(out)"],
            plot_type="semilogx",
            grid=False,
            legend=False
        )
        assert config.plot_type == "semilogx"
        assert config.grid is False
        assert config.legend is False

    def test_plot_config_requires_all_fields(self):
        """Test plot configuration requires all required fields."""
        with pytest.raises(ValidationError):
            PlotConfig()

        with pytest.raises(ValidationError):
            PlotConfig(title="Test", xlabel="X", ylabel="Y")  # missing signals