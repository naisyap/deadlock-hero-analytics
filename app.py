
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Deadlock Hero Analytics",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# 2. LOAD DATA
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hero_performance.csv"
)


@st.cache_data
def load_data():
    """Load the processed Deadlock hero dataset."""
    return pd.read_csv(DATA_PATH)


df = load_data()


# ============================================================
# 3. REUSABLE TABLE FUNCTION
# ============================================================

def display_hero_table(data):
    """Display hero performance data with readable formatting."""

    columns = [
        "hero_name",
        "matches",
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
    ]

    formatted_data = data[columns].sort_values(
        "win_rate",
        ascending=False,
    )

    st.dataframe(
        formatted_data,
        column_config={
            "hero_name": st.column_config.TextColumn(
                "Hero"
            ),
            "matches": st.column_config.NumberColumn(
                "Recorded Matches",
                format="%d",
            ),
            "win_rate": st.column_config.NumberColumn(
                "Win Rate (%)",
                format="%.2f",
            ),
            "avg_kills": st.column_config.NumberColumn(
                "Avg. Kills",
                format="%.2f",
            ),
            "avg_deaths": st.column_config.NumberColumn(
                "Avg. Deaths",
                format="%.2f",
            ),
            "avg_assists": st.column_config.NumberColumn(
                "Avg. Assists",
                format="%.2f",
            ),
        },
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 4. DASHBOARD HEADER
# ============================================================

st.title("Deadlock Hero Performance Analytics")

st.write(
    "An interactive analysis of Deadlock hero performance, "
    "win rates, and recorded match statistics."
)

st.caption(
    "Data source: Deadlock API | "
    "Snapshot: 1 November 2026"
)

st.divider()


# ============================================================
# 5. SUMMARY STATISTICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Heroes Analysed",
        len(df),
    )

with col2:
    st.metric(
        "Mean Hero Win Rate",
        f"{df['win_rate'].mean():.2f}%",
    )

with col3:
    st.metric(
        "Highest Win Rate",
        f"{df['win_rate'].max():.2f}%",
    )

with col4:
    st.metric(
        "Lowest Win Rate",
        f"{df['win_rate'].min():.2f}%",
    )

st.caption(
    "Mean hero win rate is an unweighted average "
    "across heroes."
)

st.divider()


# ============================================================
# 6. HERO PERFORMANCE DATA
# ============================================================

st.subheader("Hero Performance Data")

st.write(
    "Explore the recorded performance statistics "
    "for all 44 Deadlock heroes."
)

display_hero_table(df)

st.divider()


# ============================================================
# 7. INDIVIDUAL HERO ANALYSIS
# ============================================================

st.subheader("Individual Hero Analysis")

selected_hero = st.selectbox(
    "Select a Deadlock hero:",
    sorted(df["hero_name"].unique()),
)

hero = df[
    df["hero_name"] == selected_hero
].iloc[0]

st.write(
    f"### {selected_hero} — Performance Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Win Rate",
        f"{hero['win_rate']:.2f}%",
    )

with col2:
    st.metric(
        "Average Kills",
        f"{hero['avg_kills']:.2f}",
    )

with col3:
    st.metric(
        "Average Deaths",
        f"{hero['avg_deaths']:.2f}",
    )

with col4:
    st.metric(
        "Average Assists",
        f"{hero['avg_assists']:.2f}",
    )

st.caption(
    f"Statistics based on "
    f"{int(hero['matches']):,} recorded hero matches."
)

st.divider()


# ============================================================
# 8. TOP 10 HEROES BY WIN RATE
# ============================================================

st.subheader("Top 10 Heroes by Win Rate")

top_heroes = df.nlargest(
    10,
    "win_rate",
).sort_values("win_rate")

fig = px.bar(
    top_heroes,
    x="win_rate",
    y="hero_name",
    orientation="h",
    hover_data=[
        "matches",
        "avg_kills",
        "avg_assists",
    ],
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
    template="plotly_dark",
    height=550,
    margin=dict(
        l=20,
        r=60,
        t=20,
        b=40,
    ),
    xaxis=dict(
        range=[0, 65],
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.divider()


# ============================================================
# 9. CORRELATION ANALYSIS
# ============================================================

st.subheader(
    "Hero Performance Correlation Analysis"
)

st.write(
    "Explore how different hero performance metrics "
    "relate to observed win rates."
)

metric_options = {
    "Recorded Matches": "matches",
    "Average Kills": "avg_kills",
    "Average Deaths": "avg_deaths",
    "Average Assists": "avg_assists",
    "Average Player Damage": "avg_player_damage",
}

selected_metric = st.selectbox(
    "Choose a metric to compare with win rate:",
    list(metric_options.keys()),
)

metric_column = metric_options[selected_metric]

correlation = df[metric_column].corr(
    df["win_rate"]
)

st.metric(
    "Pearson Correlation (r)",
    f"{correlation:+.3f}",
)

scatter_fig = px.scatter(
    df,
    x=metric_column,
    y="win_rate",
    hover_name="hero_name",
    hover_data=[
        "matches",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
    ],
    labels={
        metric_column: selected_metric,
        "win_rate": "Win Rate (%)",
    },
    title=f"{selected_metric} vs Win Rate",
)

scatter_fig.update_traces(
    marker=dict(
        size=11,
        opacity=0.8,
    )
)

scatter_fig.update_layout(
    template="plotly_dark",
    height=550,
)

st.plotly_chart(
    scatter_fig,
    use_container_width=True,
)

st.caption(
    "Correlation describes association, not causation. "
    "Results are based on aggregated hero statistics."
)

st.divider()


# ============================================================
# 10. HERO PERFORMANCE EXPLORER
# ============================================================

st.subheader("Hero Performance Explorer")

st.write(
    "Filter heroes by win rate and recorded match count "
    "to explore different performance groups."
)

min_win_rate = st.slider(
    "Minimum Win Rate (%)",
    min_value=40.0,
    max_value=60.0,
    value=45.0,
    step=0.5,
)

min_matches = st.number_input(
    "Minimum Recorded Hero Matches",
    min_value=0,
    max_value=int(df["matches"].max()),
    value=500000,
    step=100000,
)

filtered_df = df[
    (df["win_rate"] >= min_win_rate)
    & (df["matches"] >= min_matches)
].copy()

st.write(
    f"**Heroes matching your filters: "
    f"{len(filtered_df)}**"
)

display_hero_table(filtered_df)


# ============================================================
# 11. DOWNLOAD FILTERED DATA
# ============================================================

st.download_button(
    label="Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name="deadlock_filtered_heroes.csv",
    mime="text/csv",
)


# ============================================================
# 12. FOOTER
# ============================================================

st.divider()

st.caption(
    "Deadlock Hero Performance Analytics | "
    "Built with Python, Pandas, Plotly, and Streamlit."
)

st.caption(
    "This dashboard uses a historical API snapshot. "
    "Statistics may differ from current game performance."
)
