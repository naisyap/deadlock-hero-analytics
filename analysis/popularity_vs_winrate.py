
from pathlib import Path

import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hero_performance.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "figures"

# Load data
df = pd.read_csv(DATA_PATH)

# Calculate Pearson correlation
correlation = df["matches"].corr(df["win_rate"])

print("\n=== POPULARITY VS WIN RATE ===")
print(f"Pearson correlation: {correlation:.3f}")

# Create interactive scatter plot
fig = px.scatter(
    df,
    x="matches",
    y="win_rate",
    hover_name="hero_name",
    hover_data=["avg_kills", "avg_deaths", "avg_assists"],
    title="Deadlock Hero Popularity vs Win Rate",
    labels={
        "matches": "Recorded Hero Matches",
        "win_rate": "Win Rate (%)",
        "avg_kills": "Average Kills",
        "avg_deaths": "Average Deaths",
        "avg_assists": "Average Assists",
    },
)

fig.update_traces(
    marker=dict(size=11, opacity=0.8)
)

fig.update_layout(
    template="plotly_white",
    height=650,
)

# Save chart
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "popularity_vs_winrate.html"
fig.write_html(output_file)

print(f"Chart saved to: {output_file}")

# Display chart
fig.show()
