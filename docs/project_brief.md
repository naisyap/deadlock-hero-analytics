# Deadlock Hero Performance Analytics

## Problem Statement

Hero-level performance statistics can help identify variation in recorded win rates and highlight patterns worth investigating in Deadlock. However, aggregated statistics require careful interpretation because they do not account for every factor influencing match outcomes.

## Project Objective

Develop a reproducible Python data pipeline and interactive Streamlit dashboard to analyse aggregated hero performance statistics from the community-maintained Deadlock API.

## Research Questions

1. Which heroes have the highest and lowest recorded win rates?
2. How is recorded hero match volume associated with win rate?
3. How do average kills, deaths, assists and player damage relate to win rate?
4. What limitations affect the interpretation of aggregated hero statistics?

## Target Audience

Game analysts, balance designers, data analysts and Deadlock players interested in exploring hero performance.

## Project Scope

- **Data source:** Community-maintained Deadlock API.
- **Data granularity:** Aggregated hero-level statistics.
- **Analysis:** Win rates, recorded match volume, combat averages, appearance share and Pearson correlations.
- **Data processing:** API extraction, validation, metric calculation and hero metadata enrichment.
- **Output:** Interactive Streamlit dashboard with rankings, filters and visualisations.
- **Automation:** Scheduled GitHub Actions data refresh and automated tests.

## Success Criteria

- Successfully retrieve hero statistics from the API.
- Validate hero identifiers, match counts and win/loss consistency.
- Calculate reproducible hero performance metrics.
- Provide at least three interactive visualisations.
- Implement automated tests for important calculations.
- Document data sources, methodology and limitations.
- Deploy an accessible dashboard.

## Limitations

- Data are aggregated by hero rather than individual player or match.
- Appearance share represents the relative distribution of recorded hero appearances, not a true match-level pick rate.
- The API's aggregation period and inclusion criteria may affect comparisons.
- Player skill, team composition, matchmaking and game updates can influence recorded performance.
- Correlations describe associations and do not establish causation.
- The time data were retrieved does not necessarily indicate when the underlying statistics were last updated.
