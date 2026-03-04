import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 13: COUNTER-CYCLICAL FEDERAL MATCHING (up to 9:1 during recessions)
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 13: COUNTER-CYCLICAL FEDERAL MATCHING")
print("Dynamic 9:1 match during recessions, base ratio otherwise")
print("=" * 80)

print(f"\nProjected recession years: {sorted(recession_year_set)}")
print(f"Recession ratio: {recession_ratio}:1")

dynamic_match_results = {}

for base_ratio in base_ratios:
    cum_state_cost_dm = 0
    cum_federal_static = 0
    cum_federal_dynamic = 0

    for i in range(40):
        year = start_year + i
        cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
        tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)

        annual_state_cost = 0
        for inst, data in pa_resident_enrollment.items():
            pa_students = int(data['total'] * data['in_state_pct'])
            boost = enrollment_boost.get(inst, 0.10)
            ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
            new_students = int(pa_students * boost * ramp)
            total_students = pa_students + new_students
            cost = total_students * data['tuition'] * tuition_factor
            annual_state_cost += cost

        annual_real = annual_state_cost / cpi_factor
        cum_state_cost_dm += annual_real

        # Static match
        cum_federal_static += annual_real * base_ratio

        # Dynamic match (9:1 during recessions)
        current_ratio = recession_ratio if year in recession_year_set else base_ratio
        cum_federal_dynamic += annual_real * current_ratio

    dynamic_match_results[base_ratio] = {
        'state_cost': cum_state_cost_dm,
        'federal_static': cum_federal_static,
        'federal_dynamic': cum_federal_dynamic,
        'dynamic_premium': cum_federal_dynamic - cum_federal_static
    }

    print(f"\n  Base Ratio {base_ratio}:1")
    print(f"    40-Year State Cost:            ${cum_state_cost_dm/1e9:.2f}B")
    print(f"    Federal (static {base_ratio}:1):        ${cum_federal_static/1e9:.2f}B")
    print(f"    Federal (dynamic, 9:1 recession): ${cum_federal_dynamic/1e9:.2f}B")
    print(f"    Counter-cyclical premium:       ${(cum_federal_dynamic - cum_federal_static)/1e9:.2f}B")
    print(f"    State effective share (static):  {cum_state_cost_dm/(cum_state_cost_dm + cum_federal_static)*100:.1f}%")
    print(f"    State effective share (dynamic): {cum_state_cost_dm/(cum_state_cost_dm + cum_federal_dynamic)*100:.1f}%")

# Save dynamic match results
df_dynamic = pd.DataFrame([
    {'Base_Ratio': f"{r}:1",
     'State_Cost_B': d['state_cost']/1e9,
     'Federal_Static_B': d['federal_static']/1e9,
     'Federal_Dynamic_B': d['federal_dynamic']/1e9,
     'Countercyclical_Premium_B': d['dynamic_premium']/1e9}
    for r, d in dynamic_match_results.items()
])
df_dynamic.to_csv(OUTPUT_DIR / 'counter_cyclical_matching.csv', index=False)
print(f"\nSaved: counter_cyclical_matching.csv")
