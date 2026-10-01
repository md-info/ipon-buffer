"""Reproducible paths, shared shocks, and conservation in actual simulation."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "simulation_run", Path(__file__).resolve().parents[2] / "simulation/run.py"
)
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)


def test_numeric_determinism_and_shared_paths():
    first = sim.simulate(2, "base", "ipon")
    assert first == sim.simulate(2, "base", "ipon")
    for strategy in sim.STRATEGIES:
        result = sim.simulate(2, "base", strategy)
        assert result["path_sha256"] == first["path_sha256"]
        assert result["shocks"] == first["shocks"]
        assert result["income_minor"] == first["income_minor"]
        assert result["conservation_error_minor"] == 0


def test_sensitivities_preserve_other_exogenous_demands():
    base = sim.path_for(0, "base")
    missing = sim.path_for(0, "missing_bill")
    assert base == missing  # Only the plan's knowledge changes.
    larger = sim.path_for(0, "larger_shocks")
    for original, changed in zip(base, larger, strict=True):
        assert changed["shock"] == original["shock"] * 2
        assert changed["income"] == original["income"]
