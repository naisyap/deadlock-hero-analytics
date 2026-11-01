
from pathlib import Path

import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hero_performance.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "figures"

# Load the processed dataset
df = pd.read_csv(DATA_PATH)

# Select the 10 heroes with the highest win rates
top_heroes = df.nlargest(10, "win_rate")
top_heroes = top_heroes.sort_values("win_rate")

# Create an interactive horizontal bar chart
fig = px.bar(
    top_heroes,
    x="win_rate",
    y="hero_name",
    orientation="h",
    hover_data=["matches", "avg_kills", "avg_assists"],
    title="Top 10 Deadlock Heroes by Observed Win Rate",
    labels={
        "win_rate": "Win Rate (%)",
        "hero_name": "Hero",
        "matches": "Recorded Matches",
        "avg_kills": "Average Kills",
        "avg_assists": "Average Assists",
    },
    text="win_rate",
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
)

fig.update_layout(
    template="plotly_white",
    height=600,
    margin=dict(l=110, r=80, t=80, b=60),
    xaxis=dict(range=[0, 65]),
)

# Save the chart
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "top_10_win_rates.html"
fig.write_html(output_file)

print(f"Chart saved to: {output_file}")

# Open the interactive chart in your browser
fig.show()
