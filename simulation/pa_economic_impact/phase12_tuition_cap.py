import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 12: TUITION CAP / PRICE CONTROL SCENARIO
# Blue Collar proposal: cap at min(CPI, 2%) vs current 3% growth
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 12: TUITION CAP SCENARIO — CPI or 2%, whichever is lower")
print("=" * 80)

tuition_cap_rate = min(inflation_rate, 0.02)  # min(2.5% CPI, 2%) = 2%

cum_cost_baseline = 0
cum_cost_capped = 0

for i in range(40):
    year = start_year + i
    cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
    tuition_factor_baseline = (1 + tuition_growth_rate) ** (year - start_year)
    tuition_factor_capped = (1 + tuition_cap_rate) ** (year - start_year)

    annual_baseline = 0
    annual_capped = 0

    for inst, data in pa_resident_enrollment.items():
        pa_students = int(data['total'] * data['in_state_pct'])
        boost = enrollment_boost.get(inst, 0.10)
        ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
        new_students = int(pa_students * boost * ramp)
        total_students = pa_students + new_students

        annual_baseline += total_students * data['tuition'] * tuition_factor_baseline
        annual_capped += total_students * data['tuition'] * tuition_factor_capped

    cum_cost_baseline += annual_baseline / cpi_factor
    cum_cost_capped += annual_capped / cpi_factor

savings_from_cap = cum_cost_baseline - cum_cost_capped

print(f"\nTuition Growth Comparison (40-Year Horizon):")
print(f"  Baseline growth rate: {tuition_growth_rate*100:.1f}%")
print(f"  Capped growth rate:   {tuition_cap_rate*100:.1f}% (min of CPI, 2%)")
print(f"\n  40-Year Cost (Baseline 3%):  ${cum_cost_baseline/1e9:.2f}B")
print(f"  40-Year Cost (Capped 2%):    ${cum_cost_capped/1e9:.2f}B")
print(f"  Savings from Tuition Cap:    ${savings_from_cap/1e9:.2f}B ({savings_from_cap/cum_cost_baseline*100:.1f}%)")

# Save tuition cap comparison
df_tuition_cap = pd.DataFrame([
    {'Scenario': 'Baseline (3% growth)', 'Growth_Rate': tuition_growth_rate, 'Cost_40yr_B': cum_cost_baseline/1e9},
    {'Scenario': 'Capped (2% growth)', 'Growth_Rate': tuition_cap_rate, 'Cost_40yr_B': cum_cost_capped/1e9},
    {'Scenario': 'Savings', 'Growth_Rate': None, 'Cost_40yr_B': savings_from_cap/1e9}
])
df_tuition_cap.to_csv(OUTPUT_DIR / 'tuition_cap_scenario.csv', index=False)
print(f"Saved: tuition_cap_scenario.csv")
