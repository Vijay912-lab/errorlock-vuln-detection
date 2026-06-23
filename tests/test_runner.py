import json
from pathlib import Path

from errorlock.providers import MockProvider
from errorlock.runner import BenchmarkConfig, run_benchmark


def test_runner_writes_outputs(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    summary = run_benchmark(
        MockProvider(),
        BenchmarkConfig(
            dataset_path=root / "data" / "sample" / "sample_castle.json",
            out_dir=tmp_path / "out",
            db_path=tmp_path / "out" / "m.sqlite",
            train_size=0.34,
            seed=1,
        ),
    )
    assert summary["n_total"] == 3
    assert (tmp_path / "out" / "summary.json").exists()
    assert (tmp_path / "out" / "predictions.csv").exists()
    saved = json.loads((tmp_path / "out" / "summary.json").read_text())
    assert saved["model"] == "mock-rule-detector"
