# Deadlock Hero Performance Analytics Dashboard

A Python-powered analytics dashboard exploring hero performance, gameplay statistics, and game balance in Valve's *Deadlock*.

This project demonstrates an end-to-end data analytics workflow, from collecting API data and validating records to calculating performance metrics, conducting exploratory analysis, and developing an interactive dashboard.

## Project Overview

The Deadlock Hero Performance Analytics Dashboard is a portfolio project designed to investigate differences in hero performance using publicly accessible aggregated gameplay statistics.

The project combines data engineering, exploratory data analysis, automated testing, and interactive data visualisation to make hero-level statistics easier to explore and interpret.

### Research Questions

1. Which Deadlock heroes have the highest and lowest win rates?
2. Is there a relationship between hero popularity and win rate?
3. Do heroes with higher average kills also achieve higher win rates?
4. How do average deaths, assists, and player damage relate to performance?
5. How can an interactive dashboard support comparisons between heroes?

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| Pandas | Data cleaning, transformation, and analysis |
| Requests | Retrieving data from REST APIs |
| Plotly | Interactive data visualisations |
| Streamlit | Interactive web dashboard |
| pytest | Automated data validation tests |
| Git and GitHub | Version control and project documentation |
| VS Code | Development environment |

## Data Sources

Hero performance statistics are retrieved from the community-maintained Deadlock API.

**Hero statistics endpoint:**

`https://api.deadlock-api.com/v1/analytics/hero-stats`

**Hero metadata endpoint:**

`https://api.deadlock-api.com/v1/assets/heroes`

The statistics endpoint provides aggregated hero performance records, while the metadata endpoint supplies hero names and identifiers.

The analysed dataset contains 44 heroes, using a snapshot collected on 1 November 2026.

**Important:** The data represents aggregated API statistics rather than individual match records. Results may depend on the API's aggregation period, included matches, game modes, and patches.

## Data Pipeline

The project uses an automated three-stage data pipeline.

**Stage 1 — Data Extraction**

`src/api_client.py`

- Requests hero performance statistics from the API.
- Retrieves records in JSON format.
- Saves a timestamped raw data snapshot locally.

**Stage 2 — Data Processing**

`src/data_processing.py`

- Loads the most recent raw JSON snapshot.
- Validates the dataset.
- Calculates hero performance metrics.
- Exports a processed CSV dataset.

**Stage 3 — Hero Metadata Integration**

`src/add_hero_names.py`

- Retrieves hero metadata.
- Matches hero identifiers to hero names.
- Checks for missing or unmatched heroes.
- Updates the processed dataset.

The complete workflow is coordinated by `src/run_pipeline.py`.

### Calculated Metrics

| Metric | Calculation |
|---|---|
| Win rate (%) | Wins / Matches × 100 |
| Average kills | Total kills / Matches |
| Average deaths | Total deaths / Matches |
| Average assists | Total assists / Matches |
| Average player damage | Total player damage / Matches |
| Appearance share (%) | Hero matches / Sum of all hero matches × 100 |

Appearance share is a relative measure of the distribution of hero match counts within the dataset. It is **not equivalent to a true match-level pick rate**.

## Exploratory Data Analysis

The project uses descriptive statistics, rankings, interactive scatter plots, and Pearson correlation coefficients to examine hero-level performance.

### Highest Win Rates

Based on the 1 November 2026 snapshot:

| Rank | Hero | Win Rate |
|---|---|---|
| 1 | Graves | 57.29% |
| 2 | Rat King | 56.75% |
| 3 | Paige | 56.03% |
| 4 | Seven | 54.81% |
| 5 | Victor | 54.09% |

These rankings describe the analysed API snapshot and should not be interpreted as definitive rankings across all skill levels, patches, or competitive environments.

### Popularity and Win Rate

The correlation between recorded hero matches and win rate was approximately **+0.479**, indicating a moderate positive linear association in the analysed snapshot.

This does not establish that popularity causes higher win rates.

### Average Kills and Win Rate

The correlation between average kills and win rate was approximately **−0.064**, suggesting little linear association between these two hero-level measures.

Higher average kills alone do not necessarily correspond to higher hero win rates in this dataset.

### Analytical Limitations

- The dataset contains aggregated hero-level statistics rather than individual player or match observations.
- Correlations are descriptive and do not establish causation.
- Results may be affected by player skill, team composition, balance patches, and selection effects.
- Match counts are not equivalent to the number of unique matches in the game.
- Win-rate rankings can change as additional data becomes available.

## Interactive Dashboard

### Dashboard Preview

Explore the interactive Streamlit dashboard through the screenshots below.

#### 1. Dashboard Overview & Hero Statistics

Overview of 44 Deadlock heroes, including win rates, recorded matches, and average performance metrics.

![Dashboard Overview and Hero Statistics](assets/dashboard-overview.png)

#### 2. Individual Hero Analysis & Win Rate Rankings

Compare individual hero statistics and explore the top 10 heroes ranked by win rate.

![Individual Hero Analysis and Win Rate Rankings](assets/hero-analysis-winrate-rankings.png)

#### 3. Hero Performance Correlation Analysis

Explore relationships between hero performance metrics and win rates using interactive scatter plots and Pearson correlation coefficients.

![Hero Performance Correlation Analysis](assets/hero-correlation-analysis.png)

#### 4. Interactive Hero Performance Explorer

Filter heroes by minimum win rate and recorded match count, then export the filtered dataset as a CSV file.

![Interactive Hero Performance Explorer](assets/hero-performance-explorer.png)

The Streamlit dashboard provides:

- A summary of hero performance statistics.
- An interactive hero performance table.
- Individual hero selection and metric comparisons.
- A top-10 win-rate chart.
- Interactive scatter plots exploring relationships between performance metrics.
- Filters for minimum win rate and recorded match count.
- CSV export of filtered results.

The dashboard is implemented in `app.py` using Streamlit and Plotly.

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version.
- Git.
- Internet access when retrieving fresh API data.

### 1. Clone the Repository

```bash
git clone https://github.com/naisyap/deadlock-hero-analytics.git
cd deadlock-hero-analytics
```

*Note: The repository is currently private, so cloning requires authorised access.*

### 2. Create a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Data Pipeline

```bash
python src/run_pipeline.py
```

This retrieves current API data, processes hero performance metrics, and integrates hero names.

Running the pipeline updates the processed CSV and saves a new raw snapshot locally.

### 5. Launch the Dashboard

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL, typically:

`http://localhost:8501`

### 6. Run Automated Tests

```bash
python -m pytest tests/ -v
```

The project currently contains nine automated data validation tests, covering:

- Non-empty datasets.
- Required columns.
- Unique hero identifiers.
- Complete hero names.
- Positive match counts.
- Match totals consistent with wins and losses.
- Valid win-rate ranges.
- Correct win-rate calculations.
- Correct average-kills calculations.

All nine tests passed during local verification on 1 November 2026.

## Project Structure

```text
deadlock-hero-analytics/
├── analysis/
│   ├── hero_analysis.py
│   ├── win_rate_chart.py
│   ├── popularity_vs_winrate.py
│   └── kills_vs_winrate.py
├── data/
│   ├── processed/
│   │   └── hero_performance.csv
│   └── raw/                    # Local API snapshots
├── docs/
│   └── project_brief.md
├── outputs/
│   └── figures/                # Generated HTML charts
├── src/
│   ├── api_client.py
│   ├── inspect_data.py
│   ├── data_processing.py
│   ├── add_hero_names.py
│   └── run_pipeline.py
├── tests/
│   └── test_hero_data.py
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

Raw API snapshots and generated chart files are excluded from version control. The processed dataset is retained to support local dashboard use.

## Future Improvements

Potential enhancements include:

- Tracking hero performance across multiple dates and balance patches.
- Comparing trends between historical snapshots.
- Adding more detailed data-quality reporting.
- Implementing automated pipeline execution.
- Expanding tests to cover API failures and data transformation edge cases.
- Deploying the dashboard for public access.

## Disclaimer

This is an independent educational and portfolio project. It is not affiliated with, endorsed by, or sponsored by Valve.

*Deadlock* and associated game assets belong to their respective rights holders.
