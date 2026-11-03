
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def process_hero_data():
    """Calculate hero performance metrics from raw API data."""

    files = sorted(RAW_DIR.glob("hero_stats_*.json"))

    if not files:
        raise FileNotFoundError("No raw hero statistics found.")

    latest_file = files[-1]
    df = pd.read_json(latest_file)

    # Validate the data before calculating metrics
    if df["hero_id"].duplicated().any():
        raise ValueError("Duplicate hero IDs detected.")

    if (df["matches"] <= 0).any():
        raise ValueError("Matches must be greater than zero.")

    if not (df["wins"] + df["losses"] == df["matches"]).all():
        raise ValueError("Wins and losses do not match total matches.")

    # Rates use aggregated hero appearances as the denominator.
    df["win_rate"] = (df["wins"] / df["matches"]) * 100

    df["avg_kills"] = df["total_kills"] / df["matches"]
    df["avg_deaths"] = df["total_deaths"] / df["matches"]
    df["avg_assists"] = df["total_assists"] / df["matches"]

    df["avg_player_damage"] = (
        df["total_player_damage"] / df["matches"]
    )

    # Relative pick frequency across hero appearances
    df["appearance_share"] = (
        df["matches"] / df["matches"].sum()
    ) * 100

    # Round calculated metrics
    metric_columns = [
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
        "avg_player_damage",
        "appearance_share",
    ]

    df[metric_columns] = df[metric_columns].round(2)

    # Save the processed dataset
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "hero_performance.csv"
    df.to_csv(output_file, index=False)

    print(f"Processed {len(df)} hero records.")
    print(f"Saved to: {output_file}")

    print("\nTop 5 heroes by win rate:")
    print(
        df[["hero_id", "matches", "win_rate"]]
        .sort_values("win_rate", ascending=False)
        .head(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    process_hero_data()
