import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 17: FEDERAL REVENUE MECHANISMS TABLE
# Source: Blue Collar proposal — ~$997B in potential annual revenue
# IMPORTANT: Recomputes results[40] internally (Phase 6 dependency)
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 17: FEDERAL REVENUE MECHANISMS — FUNDING FEASIBILITY")
print("=" * 80)

# --- Recompute results[40] from Phase 6 ---
results = {}
for horizon in simulation_horizons:
    years = list(range(start_year, start_year + horizon))

    cumulative_state_cost = 0
    cumulative_new_graduates = 0
    cumulative_earnings_gain = 0
    cumulative_tax_revenue_gain = 0
    cumulative_gdp_impact = 0
    cumulative_brain_drain_savings = 0
    annual_data = []
    cumulative_state_tax_only = 0

    grad_lag_cc = 2
    grad_lag_4yr = 4

    for i, year in enumerate(years):
        cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
        tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)
        wage_factor = (1 + wage_growth_real) ** (year - start_year)

        annual_state_cost_nominal = 0
        annual_new_enrollment = 0
        for inst, data in pa_resident_enrollment.items():
            pa_students = int(data['total'] * data['in_state_pct'])
            boost = enrollment_boost.get(inst, 0.10)
            ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
            new_students = int(pa_students * boost * ramp)
            total_students = pa_students + new_students
            tuition_adjusted = data['tuition'] * tuition_factor
            cost = total_students * tuition_adjusted
            annual_state_cost_nominal += cost
            annual_new_enrollment += new_students

        annual_state_cost_real = annual_state_cost_nominal / cpi_factor
        cumulative_state_cost += annual_state_cost_real

        new_cc_grads = 0
        new_4yr_grads = 0
        if i >= grad_lag_cc:
            cc_boost_students = int(pa_resident_enrollment['Community Colleges']['total'] *
                                    pa_resident_enrollment['Community Colleges']['in_state_pct'] *
                                    enrollment_boost['Community Colleges'])
            new_cc_grads = int(cc_boost_students * completion_rates['community_college_free'])
        if i >= grad_lag_4yr:
            four_yr_boost = sum(
                int(pa_resident_enrollment[inst]['total'] *
                    pa_resident_enrollment[inst]['in_state_pct'] *
                    enrollment_boost.get(inst, 0.10))
                for inst in ['PASSHE', 'Penn State', 'Pitt', 'Temple', 'Lincoln']
            )
            new_4yr_grads = int(four_yr_boost * completion_rates['four_year_free'])

        cumulative_new_graduates += new_cc_grads + new_4yr_grads

        annual_earnings_cc = new_cc_grads * (lifetime_earnings_premium['associate'] / 40) * wage_factor
        annual_earnings_4yr = new_4yr_grads * (lifetime_earnings_premium['bachelor'] / 40) * wage_factor
        annual_earnings_gain = annual_earnings_cc + annual_earnings_4yr
        cumulative_earnings_gain += annual_earnings_gain

        state_tax_gain = annual_earnings_gain * pa_state_income_tax
        local_tax_gain = annual_earnings_gain * pa_local_tax_avg
        sales_tax_gain = annual_earnings_gain * 0.70 * sales_tax_rate
        annual_tax_gain = state_tax_gain + local_tax_gain + sales_tax_gain
        cumulative_tax_revenue_gain += annual_tax_gain
        cumulative_state_tax_only += state_tax_gain / cpi_factor

        total_annual_grads = int(total_pa_residents * 0.25)
        grads_retained = int(total_annual_grads * (brain_drain_baseline - brain_drain_free_college))
        retained_earnings = grads_retained * grad_earnings_premium * wage_factor
        retained_tax = retained_earnings * pa_state_income_tax
        cumulative_brain_drain_savings += retained_tax

        new_student_spending = annual_new_enrollment * avg_student_spending * 0.65
        institutional_spending_increase = annual_state_cost_nominal * 0.60
        gdp_contribution = (new_student_spending * spending_multipliers['student'] +
                            institutional_spending_increase * spending_multipliers['institutional'] +
                            annual_earnings_gain * spending_multipliers['payroll'])
        cumulative_gdp_impact += gdp_contribution / cpi_factor

        annual_data.append({
            'year': year,
            'state_cost_real': annual_state_cost_real,
            'new_enrollment': annual_new_enrollment,
            'new_graduates': new_cc_grads + new_4yr_grads,
            'earnings_gain': annual_earnings_gain,
            'tax_gain': annual_tax_gain,
            'brain_drain_savings': retained_tax,
            'gdp_impact': gdp_contribution / cpi_factor
        })

    avg_tuition_saved_4yr = sum(d['tuition'] for inst, d in pa_resident_enrollment.items()
                                if inst != 'Community Colleges') * 4 / 5
    avg_tuition_saved_cc = pa_resident_enrollment['Community Colleges']['tuition'] * 2
    individual_roi_bachelor = lifetime_earnings_premium['bachelor'] / avg_tuition_saved_4yr
    individual_roi_associate = lifetime_earnings_premium['associate'] / avg_tuition_saved_cc

    total_benefits = cumulative_tax_revenue_gain + cumulative_brain_drain_savings + cumulative_gdp_impact * 0.04
    state_roi = total_benefits / cumulative_state_cost if cumulative_state_cost > 0 else 0

    results[horizon] = {
        'cumulative_state_cost': cumulative_state_cost,
        'cumulative_new_graduates': cumulative_new_graduates,
        'cumulative_earnings_gain': cumulative_earnings_gain,
        'cumulative_tax_revenue': cumulative_tax_revenue_gain,
        'cumulative_brain_drain_savings': cumulative_brain_drain_savings,
        'cumulative_gdp_impact': cumulative_gdp_impact,
        'state_roi': state_roi,
        'individual_roi_bachelor': individual_roi_bachelor,
        'individual_roi_associate': individual_roi_associate,
        'annual_data': annual_data,
        'cumulative_state_tax_only': cumulative_state_tax_only,
    }

# --- Phase 17 main logic ---
pa_annual_free_college_cost = results[40]['cumulative_state_cost'] / 40  # Average annual

total_national_revenue = sum(m['annual_revenue_B'] for m in revenue_mechanisms.values())

print(f"\nPA Annual Free College Cost (avg): ${pa_annual_free_college_cost/1e9:.2f}B")
print(f"PA Population Share: {pa_population_share*100:.1f}%")
print(f"\n{'Mechanism':<35} {'National Rev':>12} {'PA Share':>10} {'Covers PA Cost':>15}")
print("-" * 75)

mechanism_rows = []
for mech, data in revenue_mechanisms.items():
    pa_share = data['annual_revenue_B'] * pa_population_share
    covers_pct = (pa_share * 1e9) / pa_annual_free_college_cost * 100 if pa_annual_free_college_cost > 0 else 0
    print(f"{mech:<35} ${data['annual_revenue_B']:>8}B ${pa_share:>7.1f}B {covers_pct:>13.1f}%")
    mechanism_rows.append({
        'Mechanism': mech,
        'National_Revenue_B': data['annual_revenue_B'],
        'PA_Share_B': pa_share,
        'Covers_PA_Cost_Pct': covers_pct,
        'Source': data['source']
    })

print(f"\n{'TOTAL':<35} ${total_national_revenue:>8}B ${total_national_revenue * pa_population_share:>7.1f}B "
      f"{(total_national_revenue * pa_population_share * 1e9) / pa_annual_free_college_cost * 100:>13.1f}%")

df_mechanisms = pd.DataFrame(mechanism_rows)
df_mechanisms.to_csv(OUTPUT_DIR / 'federal_revenue_mechanisms.csv', index=False)
print(f"\nSaved: federal_revenue_mechanisms.csv")
