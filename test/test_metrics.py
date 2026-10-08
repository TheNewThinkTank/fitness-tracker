import pytest

from src.common.metrics import (
    canonical_exercise,
    duration_seconds,
    estimate_one_rm,
    height_cm,
    parse_load,
    session_duration,
)
from src.utils.get_volume import get_total_volume


@pytest.mark.parametrize("name", ["bench_press", "bb_bench_press", "barbell_bench_press"])
def test_reviewed_bench_aliases(name):
    assert canonical_exercise(name) == "bench_press"
    assert canonical_exercise("close_grip_bench_press") != "bench_press"


def test_load_rules_do_not_guess_historical_bodyweight():
    assert parse_load("BODYWEIGHT - 20 kg").total_kg is None
    assert parse_load("BODYWEIGHT - 20 kg", 80).total_kg == 60
    assert parse_load("BODYWEIGHT + 10 kg", 80).total_kg == 90
    assert parse_load("BODYWEIGHT kg", 80).total_kg == 80
    assert parse_load("BODYWEIGHT - POWERBAND_PURPLE kg", 80).total_kg is None
    assert parse_load("Sidea_9012_Olympic_Hex_Bar + 20 kg").total_kg == 51
    assert parse_load("0 kg").total_kg == 0
    assert parse_load("unknown").total_kg is None
    assert parse_load("10 - 20 kg").total_kg is None


def test_total_volume_sums_actual_sets_and_same_day_sessions():
    records = [
        {"date": "2024-01-01", "exercises": {"bench_press": [
            {"reps": 10, "weight": "40 kg"}, {"reps": 5, "weight": "60 kg"},
        ]}},
        {"date": "2024-01-01", "exercises": {"row": [{"reps": 8, "weight": "10 kg"}]}},
        {"date": "2024-01-02", "exercises": {"pullup": [{"reps": 8, "weight": "BODYWEIGHT kg"}]}},
    ]
    assert get_total_volume(records) == [("2024-01-01", 780)]
    assert get_total_volume(records, {"2024-01-02": 80})[-1] == ("2024-01-02", 640)


def test_estimates_are_limited_to_eligible_low_rep_sets():
    assert estimate_one_rm(60, 5) == 70
    assert estimate_one_rm(60, 1) == 60
    assert estimate_one_rm(60, 11) is None
    assert estimate_one_rm(-20, 5) is None
    assert estimate_one_rm(float("inf"), 5) is None


def test_time_and_height_metrics():
    assert session_duration("23:50", "00:20") == 30
    assert session_duration(None, "10:00") is None
    assert session_duration("10:00", "09:00") is None
    assert duration_seconds("00:01:30") == 90
    assert duration_seconds("2 minutes") == 120
    assert duration_seconds("invalid") is None
    assert height_cm("0.4 m") == 40


def test_frequency_is_monday_aligned_and_includes_inactive_weeks():
    from src.combined_metrics.get_frequency_data import get_frequency_data

    result = get_frequency_data([{"date": "2026-01-05"}, {"date": "2026-01-19"}], "2026")
    assert result["workouts"].tolist() == [1, 0, 1]
    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-05", "2026-01-12", "2026-01-19"]
    assert get_frequency_data([], "2026").empty


def test_explicit_per_hand_volume_and_constant_load_comparisons():
    from datetime import date
    from src.analytics import TrainingAnalytics

    records = [(2026, 1, {"date": "2026-01-01", "exercises": {"db_press": [
        {"set_number": 1, "reps": 8, "weight": "10 kg", "load_multiplier": 2},
        {"set_number": 2, "reps": 5, "weight": "15 kg", "load_multiplier": 2},
    ]}})]
    service = TrainingAnalytics(records, programs=[])
    history = service.history("db_press", date(2026, 1, 1), date(2026, 1, 1), load_kg=20)
    assert len(history.sessions) == 1
    assert history.sessions[0].best_reps == 8
    assert history.sessions[0].volume_kg_reps == 160
    assert get_total_volume([records[0][2]]) == [("2026-01-01", 310)]


def test_program_split_spelling_and_alias_counts_preserve_sessions():
    from src.analytics import TrainingAnalytics
    from src.utils.training_metadata import split_id

    assert split_id("fullbody_a") == split_id("full_body_a")
    sets = [{"set_number": 1, "reps": 5, "weight": "60 kg"}]
    service = TrainingAnalytics([(2026, 1, {"date": "2026-01-01", "exercises": {"bench_press": sets, "bb_bench_press": sets}})], programs=[])
    assert service.exercises()[0].workouts == 1
    assert service.history("bench_press").sessions[0].sets == 2


def test_rep_range_cli_uses_shared_targets_and_merges_same_day_sets():
    from src.rep_range.rep_range import extract_actual_rep_ranges, extract_recommended_rep_ranges

    data = {"program_11": {"pull": {"bb_bench_press": "3 sets of 6-8 reps", "pullup": "3 sets of MAX reps"}}}
    assert extract_recommended_rep_ranges(data, "program_11") == {"bench_press": (6, 8)}
    sessions = [
        {"date": "2026-01-01", "split": "fullbody_a", "exercises": {"bb_bench_press": [{"reps": 6}]}},
        {"date": "2026-01-01", "split": "full_body_a", "exercises": {"bench_press": [{"reps": 8}]}},
    ]
    assert extract_actual_rep_ranges(sessions, ["full_body_a"]) == {"2026-01-01": {"bench_press": [6, 8]}}