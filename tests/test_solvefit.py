import os
import tempfile
import toml
import pulp
import pytest
from click.testing import CliRunner

from solvefit.solvefit import load_toml, make_categories, solve, cli

# ---- Unit tests ----


def test_load_toml(tmp_path):
    # Prepare a temporary TOML file
    toml_content = """
[activities]
strength = { "arm strength" = 2, "core strength" = 3, max_sessions = 2 }
running = { "cardio" = 3 }

[weights]
"arm strength" = 10
"core strength" = 20
"cardio" = 30
"""
    toml_file = tmp_path / "activities.toml"
    toml_file.write_text(toml_content)

    activities, weights = load_toml(str(toml_file))
    assert "strength" in activities
    assert "running" in activities
    assert weights["cardio"] == 30


def test_make_categories():
    weights = {"arm strength": 10, "core strength": 25, "cardio": 50}
    cats = make_categories(weights)
    assert set(cats) == set(weights.keys())


# ---- Integration test ----


def test_solve_basic():
    activities = {
        "strength": {"arm strength": 2, "core strength": 3, "max_sessions": 2},
        "running": {"cardio": 3},
    }
    weights = {"arm strength": 10, "core strength": 25, "cardio": 50}

    prob, activity_sessions = solve(activities, weights, n_sessions=3)
    # Status should be Optimal
    assert pulp.LpStatus[prob.status] == "Optimal"

    # Sessions for strength should be at most 2
    assert activity_sessions["strength"].varValue <= 2

    # Total sessions no more than 3
    total_sessions = sum(v.varValue for v in activity_sessions.values())
    assert total_sessions <= 3

    # Objective value should be > 0
    assert pulp.value(prob.objective) > 0


# ---- CLI tests ----


def test_cli_runs_successfully(tmp_path):
    # Write a minimal TOML file
    toml_content = """
[activities]
strength = { "arm strength" = 2, "core strength" = 3 }
running = { "cardio" = 3 }

[weights]
"arm strength" = 10
"core strength" = 25
"cardio" = 50
"""
    toml_file = tmp_path / "activities.toml"
    toml_file.write_text(toml_content)

    runner = CliRunner()
    result = runner.invoke(cli, ["--toml-path", str(toml_file), "--n_sessions", "3"])

    assert result.exit_code == 0
    assert "Status: Optimal" in result.output
    assert "Recommended training schedule:" in result.output
    assert "strength" in result.output
    assert "running" in result.output
