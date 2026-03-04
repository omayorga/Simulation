"""Phase 3: Historical Trends with Real Wage Growth
Pennsylvania Higher Education Economic Impact Analysis

Sources:
- SHEEO SHEF FY2024 Report (shef.sheeo.org)
- BLS/EPI Pennsylvania wage data (bls.gov, epi.org)
- JEC Brain Drain Report 2019
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# PHASE 3: HISTORICAL TRENDS WITH REAL WAGE GROWTH
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 3: HISTORICAL ANALYSIS WITH REAL WAGE GROWTH")
print("=" * 80)

# Validate historical data
assert validate_data_lengths(historical_data, 17), "Historical data length mismatch!"

df_historical = pd.DataFrame(historical_data)

# Inflation-adjusted appropriations
df_historical['state_appropriation_real'] = (
    df_historical['state_appropriation_nominal'] / df_historical['cpi_adjustment']
)

# Per-FTE funding
df_historical['total_enrollment'] = (
    df_historical['passhe_enrollment'] + df_historical['state_related_enrollment']
)
df_historical['appropriation_per_fte'] = (
    df_historical['state_appropriation_real'] * 1e6 / df_historical['total_enrollment']
)

# Real wage-adjusted calculations
df_historical['cumulative_wage_factor'] = (1 + df_historical['real_wage_growth']).cumprod()
df_historical['appropriation_wage_adjusted'] = (
    df_historical['state_appropriation_real'] / df_historical['cumulative_wage_factor']
)
df_historical['per_fte_wage_adjusted'] = (
    df_historical['appropriation_wage_adjusted'] * 1e6 / df_historical['total_enrollment']
)

# Real tuition adjusted
df_historical['tuition_real'] = (
    df_historical['tuition_avg_public'] / df_historical['cpi_adjustment']
)

print("\nHistorical State Appropriations (Real 2024 $):")
print(f"  2010: ${df_historical.loc[0, 'state_appropriation_real']:.0f}M")
print(f"  2024: ${df_historical.loc[14, 'state_appropriation_real']:.0f}M")
print(f"  Change: {((df_historical.loc[14, 'state_appropriation_real'] / df_historical.loc[0, 'state_appropriation_real']) - 1) * 100:.1f}%")

print("\nWage-Adjusted Appropriations (accounts for real wage growth):")
print(f"  2010: ${df_historical.loc[0, 'appropriation_wage_adjusted']:.0f}M")
print(f"  2024: ${df_historical.loc[14, 'appropriation_wage_adjusted']:.0f}M")
print(f"  Change: {((df_historical.loc[14, 'appropriation_wage_adjusted'] / df_historical.loc[0, 'appropriation_wage_adjusted']) - 1) * 100:.1f}%")

print("\nPASSHE Enrollment Decline:")
print(f"  2010: {df_historical.loc[0, 'passhe_enrollment']:,}")
print(f"  2023: {df_historical.loc[13, 'passhe_enrollment']:,}")
print(f"  Decline: {((df_historical.loc[13, 'passhe_enrollment'] / df_historical.loc[0, 'passhe_enrollment']) - 1) * 100:.1f}%")
print(f"  2025: {df_historical.loc[15, 'passhe_enrollment']:,} (First increase in decade!)")

print("\nPer-FTE State Appropriation (SHEEO SHEF FY2024):")
print(f"  PA Per-FTE: $6,833 (2024)")
print(f"  National Average: $11,683")
print(f"  PA Rank: Bottom quartile")
print(f"  Decline since 2001: -40.3%")

# -----------------------------------------------------------------------------
# 3.2 BRAIN DRAIN ANALYSIS
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("BRAIN DRAIN ANALYSIS")
print("-" * 60)

grad_earnings_premium = 32000
lifetime_premium = grad_earnings_premium * 40
graduates_leaving_annually = int(total_enrollment_all * 0.25 * brain_drain_data['leave_pa'])
lost_tax_revenue_annually = graduates_leaving_annually * grad_earnings_premium * state_tax_rate
lost_tax_revenue_lifetime = graduates_leaving_annually * lifetime_premium * state_tax_rate

print(f"Graduate Retention Rates:")
print(f"  Stay in PA: {brain_drain_data['stay_in_pa']*100:.0f}%")
print(f"  Leave PA: {brain_drain_data['leave_pa']*100:.0f}%")
print(f"  PA National Rank: #{brain_drain_data['pa_rank_retention']} out of 50 states")
print(f"\nEconomic Cost of Brain Drain:")
print(f"  Graduates leaving PA annually: {graduates_leaving_annually:,}")
print(f"  Lost annual tax revenue: ${lost_tax_revenue_annually/1e6:.1f}M")
print(f"  Lost lifetime tax revenue (per cohort): ${lost_tax_revenue_lifetime/1e6:.1f}M")

# -----------------------------------------------------------------------------
# 3.3 POLICY SCENARIO MODELING
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("POLICY SCENARIO MODELING")
print("-" * 60)

print(f"\n{'Scenario':<25} {'Econ Impact':<15} {'Change':<10} {'Description'}")
print("-" * 80)
for scenario, params in policy_scenarios.items():
    impact_change = (
        params['appropriation_change'] * 0.3 +
        params['enrollment_change'] * 0.5 +
        params['tuition_change'] * -0.1
    )
    projected_impact = base_economic_impact * (1 + impact_change)
    print(f"{scenario:<25} ${projected_impact/1e9:.1f}B{' '*5} {impact_change*100:+.1f}%{' '*4} {params['description']}")

# -----------------------------------------------------------------------------
# 3.4 ROI ANALYSIS
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("ROI ANALYSIS")
print("-" * 60)

print(f"\nEconomic Impact Components:")
for component, value in economic_impact_components.items():
    print(f"  {component.replace('_', ' ').title()}: ${value/1e9:.2f}B")
print(f"\nTotal Economic Impact: ${total_economic_impact/1e9:.1f}B")
print(f"Total State Appropriation: ${total_state_appropriation/1e6:.0f}M")
print(f"ROI: ${roi_ratio:.2f} for every $1 of state investment")

print(f"\nTax Revenue Generated: ${tax_revenue_generated/1e9:.2f}B")
print(f"Net Return to State: ${(tax_revenue_generated - total_state_appropriation)/1e9:.2f}B")

# Save historical data CSV
df_historical.to_csv(OUTPUT_DIR / 'historical_trends_2010_2026.csv', index=False)
print(f"\nSaved: historical_trends_2010_2026.csv")
