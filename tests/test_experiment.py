import csv
import json

from drone_hive.experiment import run_suite


def test_suite_exports_complete_evidence_bundle(tmp_path) -> None:
    output = tmp_path / "evidence"
    results = run_suite(output, seeds=(7,), steps=30, drones=8)
    assert len(results) == 5
    expected = {
        "step_metrics.csv",
        "run_summary.csv",
        "aggregate_summary.csv",
        "manifest.json",
        "policy_comparison.png",
        "exploration_trajectories.png",
    }
    assert expected <= {path.name for path in output.iterdir()}
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["study_type"] == "simulation"
    with (output / "run_summary.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 5
