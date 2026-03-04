import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 16: EQUITY MATCH BY STATE WEALTH
# Blue Collar proposal: 3:1 for high-wealth states, 5:1 for low-wealth states
# IMPORTANT: Recomputes results[40] internally (Phase 6 dependency)
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 16: SLIDING-SCALE EQUITY MATCH BY STATE WEALTH")
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

# --- Phase 16 main logic ---
# Determine PA's tier
if pa_gdp_per_capita > national_median_gdp_per_capita * 1.10:
    pa_wealth_tier = 'High-Wealth'
    pa_equity_ratio = 3
elif pa_gdp_per_capita < national_median_gdp_per_capita * 0.90:
    pa_wealth_tier = 'Low-Wealth'
    pa_equity_ratio = 5
else:
    pa_wealth_tier = 'Middle-Wealth'
    pa_equity_ratio = 4  # Interpolated

print(f"\nPA Per-Capita GDP: ${pa_gdp_per_capita:,}")
print(f"National Median GDP/Capita: ${national_median_gdp_per_capita:,}")
print(f"PA Wealth Tier: {pa_wealth_tier}")
print(f"Equity Match Ratio: {pa_equity_ratio}:1")

# Compare with static ratios from Phase 6.5
forty_cost = results[40]['cumulative_state_cost']
print(f"\n40-Year Federal Contribution Comparison:")
for ratio in [1, 3, pa_equity_ratio, 5, 9]:
    fed = forty_cost * ratio
    state_share = forty_cost / (forty_cost + fed) * 100
    label = f" <- PA equity tier" if ratio == pa_equity_ratio else ""
    print(f"  {ratio}:1 match -> Federal: ${fed/1e9:.1f}B, State share: {state_share:.1f}%{label}")
