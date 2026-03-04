import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 14: EXCLUDE FLAGSHIPS RERUN (Penn State & Pitt)
# Reruns Phases 1-3 impact calculations without Penn State and Pitt
# IMPORTANT: Recomputes results[40] internally (Phase 6 dependency)
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 14: ECONOMIC IMPACT EXCLUDING PENN STATE & PITT")
print("Cleaner messaging for regional/community institution policy briefs")
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

# --- Phase 14 main logic ---
if EXCLUDE_FLAGSHIPS:
    flagship_names = ['Penn State', 'University of Pittsburgh']

    # Recalculate Phase 1 totals
    non_flagship_universities = {k: v for k, v in state_related_universities.items() if k not in flagship_names}

    nf_enrollment = sum(u['enrollment'] for u in non_flagship_universities.values())
    nf_employees = sum(u['employees'] for u in non_flagship_universities.values())
    nf_research = sum(u['research_expenditures'] for u in non_flagship_universities.values())
    nf_appropriation = sum(u['state_appropriation'] for u in non_flagship_universities.values())
    nf_operating = sum(u['operating_budget'] for u in non_flagship_universities.values())

    # Add PASSHE and CC
    total_nf_enrollment = nf_enrollment + passhe_total_enrollment + cc_total_enrollment
    total_nf_employees = nf_employees + passhe_total_employees + cc_total_employees

    # Recalculate economic impact without flagships
    nf_payroll = sum(s['count'] * s['avg_salary'] * (1 + s['benefits_rate'])
                     for s in employment_sectors.values()) * 0.55  # ~55% of payroll is non-flagship

    nf_economic_impact = {
        'institutional_spending': nf_operating + passhe_total_enrollment * 15000 + cc_total_enrollment * 10000,
        'payroll_impact': nf_payroll * spending_multipliers['payroll'],
        'student_spending_impact': total_nf_enrollment * avg_student_spending * 0.65 * spending_multipliers['student'],
        'research_impact': nf_research * spending_multipliers['research'],
        'construction_impact': 0.4e9 * spending_multipliers['construction']
    }

    total_nf_impact = sum(nf_economic_impact.values())
    total_nf_appropriation = nf_appropriation + 172.9e6  # PASSHE appropriation
    nf_roi = total_nf_impact / total_nf_appropriation if total_nf_appropriation > 0 else 0

    print(f"\n--- WITH FLAGSHIPS (Full Model) ---")
    print(f"  Total Enrollment:    {total_enrollment_all:,}")
    print(f"  Economic Impact:     ${total_economic_impact/1e9:.1f}B")
    print(f"  State Appropriation: ${total_state_appropriation/1e6:.0f}M")
    print(f"  ROI:                 ${roi_ratio:.2f} per $1")

    print(f"\n--- WITHOUT FLAGSHIPS (Excluding Penn State & Pitt) ---")
    print(f"  Total Enrollment:    {total_nf_enrollment:,}")
    print(f"  Economic Impact:     ${total_nf_impact/1e9:.1f}B")
    print(f"  State Appropriation: ${total_nf_appropriation/1e6:.0f}M")
    print(f"  ROI:                 ${nf_roi:.2f} per $1")

    # Free college simulation without flagships
    nf_pa_enrollment = {k: v for k, v in pa_resident_enrollment.items() if k not in ['Penn State', 'Pitt']}

    cum_nf_state_cost = 0
    cum_nf_grads = 0
    for i in range(40):
        year = start_year + i
        cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
        tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)
        wage_factor = (1 + wage_growth_real) ** (year - start_year)

        annual_cost = 0
        for inst, data in nf_pa_enrollment.items():
            pa_students = int(data['total'] * data['in_state_pct'])
            boost = enrollment_boost.get(inst, 0.10)
            ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
            new_students = int(pa_students * boost * ramp)
            total_students = pa_students + new_students
            annual_cost += total_students * data['tuition'] * tuition_factor

        cum_nf_state_cost += annual_cost / cpi_factor

        new_grads = 0
        if i >= 2:
            cc_boost = int(nf_pa_enrollment['Community Colleges']['total'] *
                          nf_pa_enrollment['Community Colleges']['in_state_pct'] *
                          enrollment_boost['Community Colleges'])
            new_grads += int(cc_boost * completion_rates['community_college_free'])
        if i >= 4:
            for inst in ['PASSHE', 'Temple', 'Lincoln']:
                if inst in nf_pa_enrollment:
                    data = nf_pa_enrollment[inst]
                    boost_students = int(data['total'] * data['in_state_pct'] * enrollment_boost.get(inst, 0.10))
                    new_grads += int(boost_students * completion_rates['four_year_free'])
        cum_nf_grads += new_grads

    print(f"\n--- FREE COLLEGE WITHOUT FLAGSHIPS (40-Year) ---")
    print(f"  State Cost:     ${cum_nf_state_cost/1e9:.2f}B (vs ${results[40]['cumulative_state_cost']/1e9:.2f}B with flagships)")
    print(f"  New Graduates:  {cum_nf_grads:,} (vs {results[40]['cumulative_new_graduates']:,} with flagships)")
    print(f"  Cost Reduction: {(1 - cum_nf_state_cost/results[40]['cumulative_state_cost'])*100:.1f}%")

    df_nf = pd.DataFrame([
        {'Scenario': 'With Flagships', 'State_Cost_40yr_B': results[40]['cumulative_state_cost']/1e9,
         'New_Graduates': results[40]['cumulative_new_graduates']},
        {'Scenario': 'Without Flagships', 'State_Cost_40yr_B': cum_nf_state_cost/1e9,
         'New_Graduates': cum_nf_grads}
    ])
    df_nf.to_csv(OUTPUT_DIR / 'exclude_flagships_comparison.csv', index=False)
    print(f"Saved: exclude_flagships_comparison.csv")
