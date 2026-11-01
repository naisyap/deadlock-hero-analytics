
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

files = sorted(RAW_DATA_DIR.glob("hero_stats_*.json"))

if not files:
    raise FileNotFoundError("No hero statistics JSON files found.")

latest_file = files[-1]
df = pd.read_json(latest_file)

print("Dataset:", latest_file.name)
print("Shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head().to_string(index=False))

print("\nMissing values:")
print(df.isnull().sum().to_string())


print("\n--- DATA VALIDATION ---")

# Check for duplicate hero IDs
duplicate_heroes = df["hero_id"].duplicated().sum()
print(f"Duplicate hero IDs: {duplicate_heroes}")

# Check whether wins and losses equal matches
match_errors = (
    df["wins"] + df["losses"] != df["matches"]
).sum()
print(f"Match count inconsistencies: {match_errors}")

# Check for negative values
numeric_columns = df.select_dtypes(include="number")
negative_values = (numeric_columns < 0).sum().sum()
print(f"Negative numeric values: {negative_values}")

# Check for heroes with zero matches
zero_matches = (df["matches"] == 0).sum()
print(f"Heroes with zero matches: {zero_matches}")

print("\nValidation complete.")
