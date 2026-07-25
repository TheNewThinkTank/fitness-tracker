import pandas as pd

from src.combined_metrics import combined_metrics
from src.common.params import PlotParams


def test_plot_duration_volume_1rm_runs_without_error(monkeypatch, tmp_path):
    table = [
        {
            "date": "2026-01-01",
            "exercises": {"bb_bench_press": [{"reps": 5, "weight": 100}]},
        },
        {
            "date": "2026-01-02",
            "exercises": {"bb_bench_press": [{"reps": 6, "weight": 110}]},
        },
    ]

    monkeypatch.setattr(combined_metrics, "settings", {"IMG_PATH": f"{tmp_path}/"})
    monkeypatch.setattr(combined_metrics, "get_all_durations", lambda year: {"2026-01-01": 30, "2026-01-02": 45})
    monkeypatch.setattr(combined_metrics, "get_total_volume", lambda table: [("2026-01-01", 200), ("2026-01-02", 250)])
    monkeypatch.setattr(
        combined_metrics,
        "get_df",
        lambda table, splits=None, exercise=None: pd.DataFrame({"reps": [5, 6], "weight": [100, 110]}),
    )
    monkeypatch.setattr(
        combined_metrics,
        "one_rep_max_estimator",
        lambda df: pd.DataFrame({"1RM": [120.0, 130.0]}, index=["2026-01-01", "2026-01-02"]),
    )
    monkeypatch.setattr(combined_metrics, "save_plot", lambda fig, path: None)

    params = PlotParams(table=table, year="2026")

    combined_metrics.plot_duration_volume_1rm(params)
