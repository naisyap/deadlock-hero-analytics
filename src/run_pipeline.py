
from api_client import fetch_hero_stats, save_hero_stats
from data_processing import process_hero_data
from add_hero_names import add_hero_names


def run_pipeline():
    """Run the complete Deadlock data processing pipeline."""

    print("\n=== STEP 1: FETCH HERO STATISTICS ===")
    hero_data = fetch_hero_stats()
    save_hero_stats(hero_data)

    print("\n=== STEP 2: PROCESS HERO STATISTICS ===")
    process_hero_data()

    print("\n=== STEP 3: ADD HERO NAMES ===")
    add_hero_names()

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_pipeline()
