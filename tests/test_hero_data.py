
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hero_performance.csv"


@pytest.fixture
def hero_data():
    """Load the processed hero dataset for testing."""
    return pd.read_csv(DATA_PATH)


def test_dataset_not_empty(hero_data):
    assert not hero_data.empty


def test_required_columns_exist(hero_data):
    required_columns = [
        "hero_id",
        "hero_name",
        "matches",
        "wins",
        "losses",
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
    ]

    assert set(required_columns).issubset(hero_data.columns)


def test_no_duplicate_hero_ids(hero_data):
    assert not hero_data["hero_id"].duplicated().any()


def test_no_missing_hero_names(hero_data):
    assert hero_data["hero_name"].notna().all()
    assert hero_data["hero_name"].str.strip().ne("").all()


def test_matches_are_positive(hero_data):
    assert (hero_data["matches"] > 0).all()


def test_wins_and_losses_match_total(hero_data):
    assert (
        hero_data["wins"] + hero_data["losses"]
        == hero_data["matches"]
    ).all()


def test_win_rates_are_valid(hero_data):
    assert hero_data["win_rate"].between(0, 100).all()


def test_win_rate_calculation(hero_data):
    expected = (
        hero_data["wins"] / hero_data["matches"] * 100
    ).round(2)

    assert (
        (hero_data["win_rate"] - expected).abs() < 0.011
    ).all()


def test_average_kills_calculation(hero_data):
    expected = (
        hero_data["total_kills"] / hero_data["matches"]
    ).round(2)

    assert (
        (hero_data["avg_kills"] - expected).abs() < 0.011
    ).all()
