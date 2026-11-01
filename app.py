
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Deadlock | Hero Performance Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. DESIGN SYSTEM
# ============================================================

BACKGROUND = "#171A1B"
PANEL = "#25292B"
ACCENT = "#D45543"
IVORY = "#F1E6D4"
MUTED = "#AAB0B2"
GRID = "#41474A"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND};
        color: {IVORY};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }}

    h1, h2, h3 {{
        color: {IVORY};
        letter-spacing: 0.2px;
    }}

    h1 {{
        font-weight: 800;
    }}

    div[data-testid="stMetric"] {{
        background: {PANEL};
        border: 1px solid {GRID};
        border-radius: 12px;
        padding: 18px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    div[data-testid="stMetricValue"] {{
        color: {IVORY};
    }}

    div[data-testid="stSidebar"] {{
        background-color: #202426;
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
    }}

    .dashboard-subtitle {{
        color: {MUTED};
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    .section-caption {{
        color: {MUTED};
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }}

    .accent-line {{
        height: 4px;
        width: 85px;
        background-color: {ACCENT};
        border-radius: 4px;
        margin-bottom: 1rem;
    }}

    hr {{
        border-color: {GRID};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. LOAD DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "hero_performance.csv"


@st.cache_data
def load_data(file_path: str, modified_time: float) -> pd.DataFrame:
    # modified_time makes Streamlit reload the CSV when it changes.
    df = pd.read_csv(file_path)

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
        "avg_player_damage",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required CSV columns: {', '.join(missing)}"
        )

    numeric_columns = [
        "matches",
        "wins",
        "losses",
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
        "avg_player_damage",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df["hero_name"] = df["hero_name"].fillna("Unknown Hero")
    df = df.dropna(subset=["matches", "win_rate"])

    return df


if not DATA_PATH.exists():
    st.error(
        "The processed hero dataset was not found. "
        "Run the data pipeline before launching the dashboard."
    )
    st.code("python src/run_pipeline.py")
    st.stop()

try:
    data = load_data(
        str(DATA_PATH),
        DATA_PATH.stat().st_mtime,
    )
except (ValueError, OSError, pd.errors.ParserError) as error:
    st.error(f"Unable to load hero statistics: {error}")
    st.stop()

if data.empty:
    st.warning("The processed dataset contains no usable hero records.")
    st.stop()


# ============================================================
# 4. SHARED CHART STYLE
# ============================================================

def style_chart(fig, height=440):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font=dict(
            family="Arial, sans-serif",
            color=IVORY,
            size=13,
        ),
        height=height,
        margin=dict(l=20, r=20, t=30, b=35),
        xaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID,
            title_font=dict(color=IVORY),
        ),
        yaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID,
            title_font=dict(color=IVORY),
        ),
        hoverlabel=dict(
            bgcolor=PANEL,
            font_color=IVORY,
        ),
    )
    return fig


def display_hero_table(df):
    preferred_columns = [
        "hero_name",
        "matches",
        "wins",
        "losses",
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
        "avg_player_damage",
    ]

    columns = [
        column
        for column in preferred_columns
        if column in df.columns
    ]

    table = df[columns].copy()

    return st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "hero_name": st.column_config.TextColumn("Hero"),
            "matches": st.column_config.NumberColumn(
                "Matches", format="%,d"
            ),
            "wins": st.column_config.NumberColumn(
                "Wins", format="%,d"
            ),
            "losses": st.column_config.NumberColumn(
                "Losses", format="%,d"
            ),
            "win_rate": st.column_config.NumberColumn(
                "Win Rate (%)", format="%.2f"
            ),
            "avg_kills": st.column_config.NumberColumn(
                "Avg Kills", format="%.2f"
            ),
            "avg_deaths": st.column_config.NumberColumn(
                "Avg Deaths", format="%.2f"
            ),
            "avg_assists": st.column_config.NumberColumn(
                "Avg Assists", format="%.2f"
            ),
            "avg_player_damage": st.column_config.NumberColumn(
                "Avg Damage", format="%,.2f"
            ),
        },
    )


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:
    st.title("DEADLOCK")
    st.caption("HERO INTELLIGENCE PLATFORM")

    st.divider()

    st.markdown("### Dashboard")
    st.write("Hero performance and comparative analytics")

    st.divider()

    st.markdown("### Data Source")
    st.caption("Deadlock API — aggregated hero statistics")

    st.markdown("### Data Snapshot")
    st.caption(
        "Local CSV modified: "
        + pd.Timestamp(
            DATA_PATH.stat().st_mtime,
            unit="s",
        ).strftime("%d %b %Y, %H:%M")
    )

    st.info(
        "Automatic six-hour API refresh is not enabled yet. "
        "The dashboard currently reads the processed CSV."
    )


# ============================================================
# 6. HEADER
# ============================================================

st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

st.title("Deadlock Hero Performance Analytics")

st.markdown(
    '<div class="dashboard-subtitle">'
    "Explore hero effectiveness, combat performance, "
    "popularity and statistical relationships."
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# 7. OVERVIEW METRICS
# ============================================================

st.header("Performance Overview")

total_heroes = len(data)
average_win_rate = data["win_rate"].mean()
highest_win_rate = data["win_rate"].max()
lowest_win_rate = data["win_rate"].min()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Heroes Analysed", f"{total_heroes:,}")

with col2:
    st.metric("Average Hero Win Rate", f"{average_win_rate:.2f}%")

with col3:
    st.metric("Highest Win Rate", f"{highest_win_rate:.2f}%")

with col4:
    st.metric("Lowest Win Rate", f"{lowest_win_rate:.2f}%")

st.caption(
    "Average hero win rate is the unweighted mean across heroes."
)

st.divider()


# ============================================================
# 8. HERO PERFORMANCE TABLE
# ============================================================

st.header("Hero Performance Rankings")

st.markdown(
    '<div class="section-caption">'
    "Compare hero win rates, match volume and combat statistics."
    "</div>",
    unsafe_allow_html=True,
)

ranked_data = data.sort_values(
    by="win_rate",
    ascending=False,
)

display_hero_table(ranked_data)

st.divider()


# ============================================================
# 9. INDIVIDUAL HERO ANALYSIS
# ============================================================

st.header("Individual Hero Analysis")

hero_names = sorted(data["hero_name"].unique())

selected_hero = st.selectbox(
    "Select a hero",
    options=hero_names,
)

hero = data.loc[
    data["hero_name"] == selected_hero
].iloc[0]

st.subheader(selected_hero)

hero_col1, hero_col2, hero_col3, hero_col4 = st.columns(4)

with hero_col1:
    st.metric("Win Rate", f"{hero['win_rate']:.2f}%")

with hero_col2:
    st.metric("Matches", f"{hero['matches']:,.0f}")

with hero_col3:
    st.metric("Average Kills", f"{hero['avg_kills']:.2f}")

with hero_col4:
    st.metric("Average Deaths", f"{hero['avg_deaths']:.2f}")

hero_col5, hero_col6 = st.columns(2)

with hero_col5:
    st.metric("Average Assists", f"{hero['avg_assists']:.2f}")

with hero_col6:
    st.metric(
        "Average Player Damage",
        f"{hero['avg_player_damage']:,.2f}",
    )

st.divider()


# ============================================================
# 10. TOP 10 HEROES BY WIN RATE
# ============================================================

st.header("Top 10 Heroes by Win Rate")

top_10 = data.nlargest(10, "win_rate").sort_values("win_rate")

bar_fig = px.bar(
    top_10,
    x="win_rate",
    y="hero_name",
    orientation="h",
    text="win_rate",
    color_discrete_sequence=[ACCENT],
    labels={
        "win_rate": "Win Rate (%)",
        "hero_name": "Hero",
    },
)

bar_fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False,
    marker_line_width=0,
)

style_chart(bar_fig, height=490)

bar_fig.update_layout(
    showlegend=False,
    xaxis_range=[
        0,
        min(100, max(65, float(top_10["win_rate"].max()) + 8)),
    ],
)

st.plotly_chart(
    bar_fig,
    use_container_width=True,
)

st.caption(
    "Rankings are based on aggregated hero win rates "
    "in the current dataset."
)

st.divider()


# ============================================================
# 11. CORRELATION ANALYSIS
# ============================================================

st.header("Hero Performance Correlation Analysis")

st.write(
    "Explore how hero win rate is associated with "
    "match volume and average combat statistics."
)

correlation_options = {
    "Match Count": "matches",
    "Average Kills": "avg_kills",
    "Average Deaths": "avg_deaths",
    "Average Assists": "avg_assists",
    "Average Player Damage": "avg_player_damage",
}

selected_metric = st.selectbox(
    "Choose a variable to compare against win rate",
    options=list(correlation_options.keys()),
)

x_column = correlation_options[selected_metric]

scatter_data = data.dropna(
    subset=[x_column, "win_rate"]
).copy()

scatter_fig = px.scatter(
    scatter_data,
    x=x_column,
    y="win_rate",
    hover_name="hero_name",
    color_discrete_sequence=[ACCENT],
    labels={
        x_column: selected_metric,
        "win_rate": "Win Rate (%)",
    },
    hover_data={
        x_column: ":,.2f",
        "win_rate": ":.2f",
    },
)

# Deadlock-inspired rust-red dots with ivory outlines
scatter_fig.update_traces(
    marker=dict(
        color=ACCENT,
        size=11,
        opacity=0.85,
        line=dict(
            color=IVORY,
            width=1,
        ),
    )
)

style_chart(scatter_fig, height=500)

st.plotly_chart(
    scatter_fig,
    use_container_width=True,
)

if (
    len(scatter_data) >= 2
    and scatter_data[x_column].nunique() > 1
    and scatter_data["win_rate"].nunique() > 1
):
    correlation = scatter_data[x_column].corr(
        scatter_data["win_rate"]
    )

    st.metric(
        "Pearson Correlation (r)",
        f"{correlation:+.3f}",
    )
else:
    st.info(
        "There is insufficient variation to calculate "
        "a Pearson correlation."
    )

st.caption(
    "Correlation describes a statistical association "
    "between aggregated hero-level variables. "
    "It does not establish causation."
)

st.divider()


# ============================================================
# 12. INTERACTIVE HERO PERFORMANCE EXPLORER
# ============================================================

st.header("Hero Performance Explorer")

st.write(
    "Filter heroes by minimum win rate and match volume."
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    minimum_win_rate = st.slider(
        "Minimum Win Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
    )

with filter_col2:
    minimum_matches = st.number_input(
        "Minimum Matches",
        min_value=0,
        max_value=int(data["matches"].max()),
        value=0,
        step=100,
    )

filtered_data = data[
    (data["win_rate"] >= minimum_win_rate)
    & (data["matches"] >= minimum_matches)
].sort_values(
    by="win_rate",
    ascending=False,
)

st.write(
    f"**{len(filtered_data)} of {len(data)} heroes** "
    "match your filters."
)

if filtered_data.empty:
    st.warning("No heroes match the selected filters.")
else:
    display_hero_table(filtered_data)

csv_data = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Hero Data (CSV)",
    data=csv_data,
    file_name="deadlock_filtered_hero_performance.csv",
    mime="text/csv",
    use_container_width=True,
)

st.divider()


# ============================================================
# 13. FOOTER
# ============================================================

st.caption(
    "Deadlock Hero Performance Analytics | "
    "Python • Pandas • Plotly • Streamlit"
)

st.caption(
    "Data source: Deadlock API. "
    "Statistics are aggregated at hero level and "
    "reflect the latest locally processed snapshot."
)
