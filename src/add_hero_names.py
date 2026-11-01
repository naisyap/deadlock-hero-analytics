
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "hero_performance.csv"

HERO_API = "https://api.deadlock-api.com/v1/assets/heroes"


def add_hero_names():
    """Merge Deadlock hero names with performance statistics."""

    # Load our processed performance data
    df = pd.read_csv(CSV_PATH)

    # Retrieve hero information
    response = requests.get(HERO_API, timeout=30)
    response.raise_for_status()

    heroes = response.json()

    # Keep only the fields we need
    hero_df = pd.DataFrame(heroes)[["id", "name"]]

    # Rename columns to make the merge easier
    hero_df = hero_df.rename(
        columns={"id": "hero_id", "name": "hero_name"}
    )

    # Check that each hero ID appears only once
    if hero_df["hero_id"].duplicated().any():
        raise ValueError("Duplicate hero IDs in hero information.")

    # Match performance records with hero names
    merged = df.merge(
        hero_df,
        on="hero_id",
        how="left",
        validate="many_to_one"
    )

    # Check for unmatched heroes
    missing_names = merged["hero_name"].isna().sum()
    print(f"Heroes without names: {missing_names}")

    if missing_names:
        print("Unmatched hero IDs:")
        print(merged.loc[merged["hero_name"].isna(), "hero_id"].tolist())
        raise ValueError("Some hero IDs could not be matched.")

    # Place hero_name beside hero_id
    columns = merged.columns.tolist()
    columns.remove("hero_name")
    columns.insert(1, "hero_name")
    merged = merged[columns]

    # Save updated dataset
    merged.to_csv(CSV_PATH, index=False)

    print(f"Successfully matched {len(merged)} heroes.")

    print("\nTop 5 heroes by win rate:")
    print(
        merged[["hero_name", "matches", "win_rate"]]
        .sort_values("win_rate", ascending=False)
        .head(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    add_hero_names()
