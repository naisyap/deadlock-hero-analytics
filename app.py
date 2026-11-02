
from pathlib import Path
from datetime import datetime, timezone
import time
import requests
import numpy as np

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


REFRESH_SECONDS = 6 * 60 * 60
STATS_URL = "https://api.deadlock-api.com/v1/analytics/hero-stats"
HEROES_URL = "https://api.deadlock-api.com/v1/assets/heroes"
REQUIRED_COLUMNS = [
    "hero_id", "hero_name", "matches", "wins", "losses", "win_rate",
    "avg_kills", "avg_deaths", "avg_assists", "avg_player_damage",
]


def validate_dashboard_data(df):
    """Reject incomplete or inconsistent snapshots before displaying them."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty or df["hero_id"].duplicated().any():
        raise ValueError("Hero data is empty or contains duplicate IDs.")
    for column in REQUIRED_COLUMNS:
        if column not in ("hero_id", "hero_name"):
            df[column] = pd.to_numeric(df[column], errors="raise")
    if df[REQUIRED_COLUMNS].isna().any().any() or not np.isfinite(
        df[[c for c in REQUIRED_COLUMNS if c not in ("hero_id", "hero_name")]].to_numpy(dtype=float)
    ).all():
        raise ValueError("Hero data contains missing required values.")
    if (df["matches"] <= 0).any() or not (
        df["wins"] + df["losses"] == df["matches"]
    ).all():
        raise ValueError("Invalid hero match totals.")
    return df


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner="Fetching Deadlock statistics…")
def fetch_live_data():
    """Reproduce the existing pipeline calculations without writing partial files."""
    stats_response = requests.get(STATS_URL, timeout=30)
    stats_response.raise_for_status()
    stats = stats_response.json()
    if not isinstance(stats, list) or not stats:
        raise ValueError("Unexpected hero statistics response.")

    heroes_response = requests.get(HEROES_URL, timeout=30)
    heroes_response.raise_for_status()
    heroes = heroes_response.json()
    if not isinstance(heroes, list) or not heroes:
        raise ValueError("Unexpected hero names response.")

    df = pd.DataFrame(stats)
    # Hero images are nested under images.icon_hero_card in the Deadlock API.
    # Keep portraits optional so missing artwork never blocks the analytics.
    hero_rows = []
    for entry in heroes:
        if not isinstance(entry, dict):
            continue
        images = entry.get("images") or {}
        if not isinstance(images, dict):
            images = {}
        portrait = next(
            (images[key] for key in ("icon_hero_card", "icon_hero_card_webp", "top_bar_vertical_image", "icon_image_small")
             if isinstance(images.get(key), str)
             and images[key].startswith("https://")),
            None,
        )
        hero_rows.append({
            "hero_id": entry.get("id"),
            "hero_name": entry.get("name"),
            "hero_portrait": portrait,
        })
    hero_df = pd.DataFrame(hero_rows)
    if hero_df.empty or not {"hero_id", "hero_name"}.issubset(hero_df.columns):
        raise ValueError("Hero metadata does not contain valid identifiers and names.")
    if hero_df["hero_id"].duplicated().any():
        raise ValueError("Duplicate IDs in hero names response.")

    df["win_rate"] = (df["wins"] / df["matches"]) * 100
    df["avg_kills"] = df["total_kills"] / df["matches"]
    df["avg_deaths"] = df["total_deaths"] / df["matches"]
    df["avg_assists"] = df["total_assists"] / df["matches"]
    df["avg_player_damage"] = df["total_player_damage"] / df["matches"]
    df["appearance_share"] = df["matches"] / df["matches"].sum() * 100
    metrics = ["win_rate", "avg_kills", "avg_deaths", "avg_assists",
               "avg_player_damage", "appearance_share"]
    df[metrics] = df[metrics].round(2)
    df = df.merge(hero_df, on="hero_id", how="left", validate="many_to_one")
    df = validate_dashboard_data(df)
    fetched_at = datetime.now(timezone.utc).isoformat()
    return df, fetched_at


@st.cache_data(show_spinner=False)
def load_local_snapshot(path, modified_time):
    return validate_dashboard_data(pd.read_csv(path))


# The six-hour interval reruns the entire dashboard for an open browser session.
# Streamlit also refreshes cached API data on the next visit after the TTL expires.
if "dashboard_refresh_started" not in st.session_state:
    st.session_state.dashboard_refresh_started = time.monotonic()


@st.fragment(run_every="6h")
def schedule_dashboard_refresh():
    if time.monotonic() - st.session_state.dashboard_refresh_started >= REFRESH_SECONDS:
        st.session_state.dashboard_refresh_started = time.monotonic()
        st.rerun(scope="app")


schedule_dashboard_refresh()

try:
    data, fetched_at = fetch_live_data()
    data_source = "Live Deadlock API"
    last_updated = pd.Timestamp(fetched_at).strftime("%d %b %Y, %H:%M UTC")
except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as error:
    if not DATA_PATH.exists():
        st.error(f"API refresh failed and no saved CSV is available: {error}")
        st.stop()
    try:
        data = load_local_snapshot(str(DATA_PATH), DATA_PATH.stat().st_mtime)
    except (ValueError, OSError, pd.errors.ParserError) as csv_error:
        st.error(f"Neither the API nor saved CSV could be loaded: {csv_error}")
        st.stop()
    data_source = "Saved CSV (API unavailable)"
    last_updated = "Snapshot file modified: " + pd.Timestamp(
        DATA_PATH.stat().st_mtime, unit="s", tz="UTC"
    ).strftime("%d %b %Y, %H:%M UTC")
    st.warning("Live data is temporarily unavailable. Displaying the saved CSV snapshot.")


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
    st.caption(data_source)
    st.markdown("### Last Updated")
    st.caption(last_updated)
    st.caption("Live API results are cached for six hours. Open dashboards refresh every six hours.")


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
highest_hero = data.loc[data["win_rate"].idxmax(), "hero_name"]
lowest_hero = data.loc[data["win_rate"].idxmin(), "hero_name"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Heroes Analysed", f"{total_heroes:,}")

with col2:
    st.metric("Average Hero Win Rate", f"{average_win_rate:.2f}%")

with col3:
    st.metric("Highest Win Rate", f"{highest_win_rate:.2f}%", help=f"Hero: {highest_hero}")
    st.caption(f"Hero: **{highest_hero}**")

with col4:
    st.metric("Lowest Win Rate", f"{lowest_win_rate:.2f}%", help=f"Hero: {lowest_hero}")
    st.caption(f"Hero: **{lowest_hero}**")

st.caption(
    "Average hero win rate is the unweighted mean across heroes."
)

st.divider()


# ============================================================
# 7A. DYNAMIC KEY FINDINGS
# ============================================================

st.header("Key Findings")
st.caption("Automatically calculated from the currently displayed hero dataset.")

most_played = data.loc[data["matches"].idxmax()]
least_played = data.loc[data["matches"].idxmin()]

insight_col1, insight_col2, insight_col3 = st.columns(3)
with insight_col1:
    st.markdown("**Highest Win Rate**")
    st.write(f"{highest_hero} leads with a {highest_win_rate:.2f}% win rate.")
with insight_col2:
    st.markdown("**Most Recorded Hero Matches**")
    st.write(
        f"{most_played['hero_name']} has "
        f"{int(most_played['matches']):,} recorded hero matches."
    )
with insight_col3:
    st.markdown("**Win-Rate Spread**")
    st.write(
        f"The gap between the highest and lowest hero win rates is "
        f"{highest_win_rate - lowest_win_rate:.2f} percentage points."
    )

st.caption(
    "These are descriptive hero-level findings, not causal or skill-adjusted estimates. "
    "Hero match counts do not represent the number of unique game matches."
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

# Competition ranking: tied win rates share the same rank.
hero_rank = int(data["win_rate"].rank(method="min", ascending=False).loc[hero.name])
portrait_url = hero.get("hero_portrait")
portrait_available = isinstance(portrait_url, str) and portrait_url.startswith("https://")

if portrait_available:
    portrait_col, details_col = st.columns([1, 4], vertical_alignment="center")
    with portrait_col:
        st.image(portrait_url, width=175)
    with details_col:
        st.subheader(selected_hero)
        st.caption(f"Win-rate rank: #{hero_rank} of {total_heroes} heroes")
else:
    st.subheader(selected_hero)
    st.caption(f"Win-rate rank: #{hero_rank} of {total_heroes} heroes")

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

    # Interpret the selected hero-level Pearson correlation dynamically.
    strength = abs(correlation)
    if strength < 0.20:
        relationship = "very weak"
    elif strength < 0.40:
        relationship = "weak"
    elif strength < 0.60:
        relationship = "moderate"
    elif strength < 0.80:
        relationship = "strong"
    else:
        relationship = "very strong"

    if correlation > 0:
        direction = "positive"
        explanation = (
            "Heroes with higher values of this metric tend to have higher "
            "win rates in this snapshot."
        )
    elif correlation < 0:
        direction = "negative"
        explanation = (
            "Heroes with higher values of this metric tend to have lower "
            "win rates in this snapshot."
        )
    else:
        direction = "zero"
        explanation = "No linear association is observed in this snapshot."

    if strength < 0.20:
        explanation = (
            "There is little evidence of a linear relationship "
            "between these hero-level measures in this snapshot."
        )

    st.info(
        f"**Statistical interpretation:** A {relationship} {direction} "
        f"linear association between {selected_metric.lower()} and "
        f"hero win rate (Pearson r = {correlation:+.3f}; "
        f"n = {len(scatter_data)} heroes). {explanation}"
    )
    st.caption(
        "Strength labels use descriptive thresholds (0.20, 0.40, 0.60, 0.80), "
        "not significance tests. Correlation does not imply causation."
    )
else:
    st.info(
        "There is insufficient variation to calculate "
        "a Pearson correlation."
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
    "reflect the latest available validated snapshot."
)
