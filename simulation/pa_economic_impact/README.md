# Pennsylvania Higher Education Economic Impact Simulation

A comprehensive economic impact analysis of Pennsylvania's public higher education system, including PASSHE universities, state-related institutions (Penn State, Pitt, Temple, Lincoln), and community colleges.

## Project Structure

The simulation is organized into 18 independent phases, each in its own file. Every phase can be run standalone — no dependencies on other phase outputs.

| File | Phase | Description |
|------|-------|-------------|
| `config.py` | — | Shared constants, data dictionaries, helper functions, and imports |
| `phase1_institutional_data.py` | 1 | Institutional enrollment, research, and employment data |
| `phase2_employment_economic_multipliers.py` | 2 | Employment sectors, spending analysis, Monte Carlo sensitivity |
| `phase3_historical_trends.py` | 3 | Historical trends (2010–2026), brain drain, policy scenarios, ROI |
| `phase4_county_level.py` | 4 | County-level economic impact aggregation |
| `phase5_visualizations.py` | 5 | Charts 1–8 (visualizations for Phases 1–4) |
| `phase6_free_college.py` | 6 | Free college simulation with multiple horizons and federal matching |
| `phase7_counterfactual.py` | 7 | Counterfactual analysis (1980–2024) |
| `phase8_limitations.py` | 8 | Dynamic feedback, crowding-out, private institutions, correlated MC |
| `phase9_demographics.py` | 9 | Demographic-segmented analysis |
| `phase10_sector_split.py` | 10 | Community college vs. four-year sector split |
| `phase11_cost_of_attendance.py` | 11 | Full cost-of-attendance modeling |
| `phase12_tuition_cap.py` | 12 | Tuition cap scenario |
| `phase13_federal_matching.py` | 13 | Counter-cyclical federal matching |
| `phase14_exclude_flagships.py` | 14 | Rerun analysis excluding Penn State & Pitt |
| `phase15_mobility_bonus.py` | 15 | Mobility bonus premium |
| `phase16_equity_match.py` | 16 | Equity match by state wealth |
| `phase17_revenue_mechanisms.py` | 17 | Federal revenue mechanisms |
| `phase18_mobility_value_score.py` | 18 | Mobility Value Score & completion gap |
| `run_all.py` | — | Master runner for executing all or selected phases |

## Usage

### Run all phases
```bash
python run_all.py
```

### Run specific phases
```bash
python run_all.py 1 6 8
```

### Run a single phase independently
```bash
python phase3_historical_trends.py
```

### List all phases
```bash
python run_all.py --list
```

## Output

All outputs (CSV data files and PNG charts) are saved to the `pa_output/` directory.

- **17 figures** (fig1–fig17): Publication-ready charts at 150 DPI
- **14 CSV files**: Detailed data tables for each analysis component

## Requirements

- Python 3.8+
- numpy
- pandas
- matplotlib
- seaborn
- scipy

## Architecture

All shared data (institutional enrollment numbers, economic multipliers, policy parameters, etc.) lives in `config.py`. Each phase file imports everything from `config.py` and recomputes any intermediate data it needs, ensuring full independence. Phases that depend on Phase 6 (free college) results recompute those results internally.
