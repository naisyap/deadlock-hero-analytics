
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hero_performance.csv"

# Load processed data
df = pd.read_csv(DATA_PATH)

# Sort heroes by observed win rate
ranked = df.sort_values("win_rate", ascending=False)

print("\n=== TOP 10 HEROES BY WIN RATE ===")
print(
    ranked[["hero_name", "matches", "win_rate"]]
    .head(10)
    .to_string(index=False)
)

print("\n=== BOTTOM 10 HEROES BY WIN RATE ===")
print(
    ranked[["hero_name", "matches", "win_rate"]]
    .tail(10)
    .sort_values("win_rate")
    .to_string(index=False)
)

print("\n=== OVERALL WIN RATE STATISTICS ===")
print(f"Mean hero win rate: {df['win_rate'].mean():.2f}%")
print(f"Median hero win rate: {df['win_rate'].median():.2f}%")
print(f"Highest win rate: {df['win_rate'].max():.2f}%")
print(f"Lowest win rate: {df['win_rate'].min():.2f}%")
print(f"Standard deviation: {df['win_rate'].std():.2f}")
