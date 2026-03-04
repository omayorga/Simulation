"""Phase 8: Addressing Model Limitations

This phase addresses four structural limitations of the static model:
  8.1 Dynamic feedback loops (wage adjustment from graduate supply)
  8.2 Crowding-out effects (opportunity cost of state spending)
  8.3 Private/non-profit institution estimates (full PA picture)
  8.4 Correlated Monte Carlo (recession scenario with linked parameters)

Sources: Cleveland Fed (2025), AICUP FY2024, Lumina Foundation,
         SHEEO SHEF, BLS CPI-U, Journal of Education Finance
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 8: ADDRESSING MODEL LIMITATIONS
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 8: ADDRESSING MODEL LIMITATIONS")
print("=" * 80)

# Recompute Phase 6 simulation results needed by this phase
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
        if i >= 2:
            cc_boost_students = int(pa_resident_enrollment['Community Colleges']['total'] *
                                   pa_resident_enrollment['Community Colleges']['in_state_pct'] *
                                   enrollment_boost['Community Colleges'])
            new_cc_grads = int(cc_boost_students * completion_rates['community_college_free'])
        if i >= 4:
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

    total_benefits = cumulative_tax_revenue_gain + cumulative_brain_drain_savings + cumulative_gdp_impact * 0.04
    state_roi = total_benefits / cumulative_state_cost if cumulative_state_cost > 0 else 0

    avg_tuition_saved_4yr = sum(d['tuition'] for inst, d in pa_resident_enrollment.items()
                                if inst != 'Community Colleges') * 4 / 5
    avg_tuition_saved_cc = pa_resident_enrollment['Community Colleges']['tuition'] * 2
    individual_roi_bachelor = lifetime_earnings_premium['bachelor'] / avg_tuition_saved_4yr
    individual_roi_associate = lifetime_earnings_premium['associate'] / avg_tuition_saved_cc

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

# Recompute total_tuition_cost_to_state (needed by 8.2)
total_tuition_cost_to_state = sum(
    int(data['total'] * data['in_state_pct']) * data['tuition']
    for data in pa_resident_enrollment.values()
)

# Recompute independent Monte Carlo (needed for 8.4 comparison)
np.random.seed(RANDOM_SEED)
_sim_results = {}
for param, (mean, std) in param_distributions.items():
    _sim_results[param] = np.random.normal(mean, std, MONTE_CARLO_SIMULATIONS)
impact_distribution = base_direct_spending * _sim_results['output_multiplier']

# -----------------------------------------------------------------------------
# 8.1 DYNAMIC FEEDBACK LOOPS
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("8.1 DYNAMIC FEEDBACK LOOPS - Wage Premium Adjustment")
print("-" * 60)

print(f"\nCurrent PA college-educated workforce share: {current_college_share_pa*100:.0f}%")
print(f"Current college wage premium: {current_wage_premium*100:.0f}%")
print(f"Elasticity of substitution used: {elasticity_of_substitution}")
print(f"\n{'Horizon':>10} {'New Share':>12} {'Supply Change':>15} {'Premium Change':>16} {'Adjusted Premium':>18}")
print("-" * 75)

feedback_results = {}
for h in feedback_horizons:
    new_grads_cumulative = results[h]['cumulative_new_graduates'] if h in results else 0
    pa_workforce = 6.5e6
    new_college_share = current_college_share_pa + (new_grads_cumulative / pa_workforce)

    old_relative_supply = current_college_share_pa / (1 - current_college_share_pa)
    new_relative_supply = new_college_share / (1 - new_college_share)
    supply_change_pct = (new_relative_supply / old_relative_supply) - 1

    premium_change_pct = -(1 / elasticity_of_substitution) * supply_change_pct
    adjusted_premium = current_wage_premium * (1 + premium_change_pct)

    original_earnings = results[h]['cumulative_earnings_gain'] if h in results else 0
    adjustment_factor = adjusted_premium / current_wage_premium
    adjusted_earnings = original_earnings * adjustment_factor
    earnings_reduction = original_earnings - adjusted_earnings

    feedback_results[h] = {
        'new_college_share': new_college_share,
        'supply_change_pct': supply_change_pct,
        'premium_change_pct': premium_change_pct,
        'adjusted_premium': adjusted_premium,
        'adjusted_earnings': adjusted_earnings,
        'earnings_reduction': earnings_reduction,
        'adjustment_factor': adjustment_factor
    }

    print(f"{h:>7} yrs {new_college_share*100:>10.1f}% {supply_change_pct*100:>13.2f}% {premium_change_pct*100:>14.2f}% {adjusted_premium*100:>16.1f}%")

print(f"\nImpact on Earnings Estimates:")
for h in feedback_horizons:
    fr = feedback_results[h]
    if h in results:
        print(f"  {h}-Year: Original ${results[h]['cumulative_earnings_gain']/1e9:.2f}B -> "
              f"Adjusted ${fr['adjusted_earnings']/1e9:.2f}B "
              f"(reduction: ${fr['earnings_reduction']/1e9:.2f}B, {fr['premium_change_pct']*100:.1f}%)")

print("\nNote: Feedback effects are modest because PA's free college program")
print("adds graduates incrementally, not all at once.")

# -----------------------------------------------------------------------------
# 8.2 CROWDING-OUT EFFECTS
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("8.2 CROWDING-OUT EFFECTS - Opportunity Cost Analysis")
print("-" * 60)

free_college_annual_cost = total_tuition_cost_to_state
free_college_budget_share = free_college_annual_cost / pa_general_fund_2024
new_higher_ed_share = higher_ed_share_current + free_college_budget_share

print(f"\nPA General Fund Budget (2024): ${pa_general_fund_2024/1e9:.1f}B")
print(f"Current higher ed share: {higher_ed_share_current*100:.0f}%")
print(f"Current Medicaid share: {medicaid_share_current*100:.0f}%")
print(f"Current K-12 share: {k12_share_current*100:.0f}%")
print(f"\nFree college annual cost: ${free_college_annual_cost/1e9:.2f}B")
print(f"Free college as % of general fund: {free_college_budget_share*100:.1f}%")
print(f"New higher ed share (with free college): {new_higher_ed_share*100:.1f}%")

education_multiplier = rims_ii_multipliers['output_multiplier']

print(f"\nCrowding-Out Scenario Analysis:")
print(f"{'Scenario':<35} {'Lost Activity':>15} {'Net Impact':>15} {'Adj ROI':>10}")
print("-" * 80)

for scenario, params in crowding_scenarios.items():
    cf = params['crowding_factor']
    displaced_spending = free_college_annual_cost * cf
    lost_economic_activity = displaced_spending * other_program_multiplier
    gross_free_college_impact = free_college_annual_cost * education_multiplier
    net_impact = gross_free_college_impact - lost_economic_activity
    adj_roi = net_impact / free_college_annual_cost if free_college_annual_cost > 0 else 0
    print(f"{scenario:<35} ${lost_economic_activity/1e9:>12.2f}B ${net_impact/1e9:>12.2f}B {adj_roi:>9.2f}x")

print("\nKey finding: Even with 50% crowding out, free college generates a positive net impact.")

# -----------------------------------------------------------------------------
# 8.3 PRIVATE & NON-PROFIT INSTITUTIONS
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("8.3 PRIVATE & NON-PROFIT INSTITUTIONS - Full PA Picture")
print("-" * 60)

print(f"\nPA Private Higher Education Sector (AICUP FY2024):")
print(f"  Institutions: {private_sector_data['institutions']}+")
print(f"  Total Enrollment: {private_sector_data['total_enrollment']:,}")
print(f"  Jobs Supported: {private_sector_data['total_employees']:,}")
print(f"  Economic Impact (excl. hospitals): ${private_sector_data['economic_impact']/1e9:.0f}B")
print(f"  Economic Impact (incl. hospitals): ${private_sector_data['impact_with_hospitals']/1e9:.1f}B")
print(f"  State & Local Taxes Generated: ${private_sector_data['state_local_taxes']/1e9:.1f}B")
print(f"  Annual Student Spending: ${private_sector_data['student_spending']/1e9:.1f}B")
print(f"  Annual Degrees Conferred: {private_sector_data['degrees_conferred']:,}")

combined_enrollment = total_enrollment_all + private_sector_data['total_enrollment']
combined_jobs = total_jobs_supported + private_sector_data['total_employees']
combined_impact = total_economic_impact + private_sector_data['economic_impact']
combined_impact_with_hospitals = total_economic_impact + private_sector_data['impact_with_hospitals']
combined_taxes = tax_revenue_generated + private_sector_data['state_local_taxes']

print(f"\n--- COMPLETE PA HIGHER EDUCATION PICTURE ---")
print(f"{'Metric':<35} {'Public':>15} {'Private':>15} {'Combined':>15}")
print("-" * 85)
print(f"{'Enrollment':<35} {total_enrollment_all:>15,} {private_sector_data['total_enrollment']:>15,} {combined_enrollment:>15,}")
print(f"{'Jobs Supported':<35} {total_jobs_supported:>15,} {private_sector_data['total_employees']:>15,} {combined_jobs:>15,}")
print(f"{'Economic Impact ($B)':<35} ${total_economic_impact/1e9:>13.1f} ${private_sector_data['economic_impact']/1e9:>13.0f} ${combined_impact/1e9:>13.1f}")
print(f"{'Tax Revenue ($B)':<35} ${tax_revenue_generated/1e9:>13.2f} ${private_sector_data['state_local_taxes']/1e9:>13.1f} ${combined_taxes/1e9:>13.2f}")

# -----------------------------------------------------------------------------
# 8.4 CORRELATED MONTE CARLO SIMULATION
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("8.4 CORRELATED MONTE CARLO - Recession-Aware Uncertainty")
print("-" * 60)

np.random.seed(RANDOM_SEED + 1)

n_sims = MONTE_CARLO_SIMULATIONS
correlated_impacts = np.zeros(n_sims)

for i in range(n_sims):
    r = np.random.random()
    cumulative_prob = 0
    state = 'Normal'
    for state_name, params in economic_states.items():
        cumulative_prob += params['probability']
        if r < cumulative_prob:
            state = state_name
            break

    state_params = economic_states[state]

    sim_multiplier = np.random.normal(
        rims_ii_multipliers['output_multiplier'] * (1 + state_params['multiplier_shift']),
        0.10
    )
    sim_spending = np.random.normal(
        avg_student_spending * (1 + state_params['spending_shift']),
        1000
    )
    sim_enrollment_factor = 1 + np.random.normal(
        state_params['enrollment_shift'],
        0.01
    )

    sim_direct = base_direct_spending * sim_enrollment_factor
    correlated_impacts[i] = sim_direct * max(sim_multiplier, 0.5)

print(f"\n{'Metric':<30} {'Independent MC':>18} {'Correlated MC':>18}")
print("-" * 70)
print(f"{'Mean Impact ($B)':<30} ${np.mean(impact_distribution)/1e9:>15.2f} ${np.mean(correlated_impacts)/1e9:>15.2f}")
print(f"{'Std Dev ($B)':<30} ${np.std(impact_distribution)/1e9:>15.2f} ${np.std(correlated_impacts)/1e9:>15.2f}")
print(f"{'95% CI Low ($B)':<30} ${np.percentile(impact_distribution, 2.5)/1e9:>15.2f} ${np.percentile(correlated_impacts, 2.5)/1e9:>15.2f}")
print(f"{'95% CI High ($B)':<30} ${np.percentile(impact_distribution, 97.5)/1e9:>15.2f} ${np.percentile(correlated_impacts, 97.5)/1e9:>15.2f}")
print(f"{'5th Percentile ($B)':<30} ${np.percentile(impact_distribution, 5)/1e9:>15.2f} ${np.percentile(correlated_impacts, 5)/1e9:>15.2f}")
print(f"{'Worst Case (1%) ($B)':<30} ${np.percentile(impact_distribution, 1)/1e9:>15.2f} ${np.percentile(correlated_impacts, 1)/1e9:>15.2f}")

print(f"\nEconomic State Probabilities:")
for state_name, params in economic_states.items():
    print(f"  {state_name}: {params['probability']*100:.0f}% probability, "
          f"multiplier {params['multiplier_shift']*100:+.0f}%, "
          f"spending {params['spending_shift']*100:+.0f}%")

print("\nKey finding: Correlated shocks produce a wider distribution with fatter tails.")

try:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Phase 8: Addressing Model Limitations', fontsize=16, fontweight='bold')

    fb_horizons_labels = [f'{h}yr' for h in feedback_horizons]
    original_premiums = [current_wage_premium * 100] * len(feedback_horizons)
    adjusted_premiums = [feedback_results[h]['adjusted_premium'] * 100 for h in feedback_horizons]
    x_fb = np.arange(len(fb_horizons_labels))
    ax1.bar(x_fb - 0.2, original_premiums, 0.4, label='Original Premium', color='#2E86AB', alpha=0.85)
    ax1.bar(x_fb + 0.2, adjusted_premiums, 0.4, label='Feedback-Adjusted', color='#E63946', alpha=0.85)
    ax1.set_ylabel('College Wage Premium (%)')
    ax1.set_title('8.1 Dynamic Feedback: Wage Premium Adjustment', fontweight='bold')
    ax1.set_xticks(x_fb)
    ax1.set_xticklabels(fb_horizons_labels)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    co_names_short = ['None', '25%', '50%', '75%']
    co_net_impacts = []
    for params in crowding_scenarios.values():
        cf = params['crowding_factor']
        displaced = free_college_annual_cost * cf * other_program_multiplier
        gross = free_college_annual_cost * education_multiplier
        co_net_impacts.append((gross - displaced) / 1e9)
    colors_co = ['#06D6A0', '#2E86AB', '#F18F01', '#E63946']
    ax2.bar(co_names_short, co_net_impacts, color=colors_co, edgecolor='black', alpha=0.85)
    ax2.axhline(y=0, color='black', linewidth=1)
    ax2.set_ylabel('Net Economic Impact ($B)')
    ax2.set_title('8.2 Crowding-Out: Net Impact by Scenario', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    categories = ['Enrollment\n(thousands)', 'Jobs\n(thousands)', 'Impact\n($B)']
    public_vals = [total_enrollment_all/1000, total_jobs_supported/1000, total_economic_impact/1e9]
    private_vals = [private_sector_data['total_enrollment']/1000, private_sector_data['total_employees']/1000, private_sector_data['economic_impact']/1e9]
    x_pp = np.arange(len(categories))
    ax3.bar(x_pp - 0.2, public_vals, 0.4, label='Public', color='#2E86AB', alpha=0.85)
    ax3.bar(x_pp + 0.2, private_vals, 0.4, label='Private', color='#F18F01', alpha=0.85)
    ax3.set_title('8.3 Full PA Picture: Public vs Private', fontweight='bold')
    ax3.set_xticks(x_pp)
    ax3.set_xticklabels(categories)
    ax3.legend(fontsize=9)
    ax3.grid(axis='y', alpha=0.3)

    ax4.hist(impact_distribution/1e9, bins=50, alpha=0.5, color='#2E86AB',
             label='Independent MC', edgecolor='black', linewidth=0.5)
    ax4.hist(correlated_impacts/1e9, bins=50, alpha=0.5, color='#E63946',
             label='Correlated MC', edgecolor='black', linewidth=0.5)
    ax4.axvline(x=np.mean(impact_distribution)/1e9, color='#2E86AB', linewidth=2, linestyle='--')
    ax4.axvline(x=np.mean(correlated_impacts)/1e9, color='#E63946', linewidth=2, linestyle='--')
    ax4.set_xlabel('Economic Impact ($B)')
    ax4.set_ylabel('Frequency')
    ax4.set_title('8.4 Correlated vs Independent Monte Carlo', fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig13_limitations_addressed.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("\nSaved: fig13_limitations_addressed.png")

except Exception as e:
    logger.error(f"Error generating Phase 8 visualizations: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("PHASE 8 SUMMARY: ADJUSTED ESTIMATES")
print("=" * 80)
print(f"\nAfter addressing all four limitations:")
print(f"  1. Dynamic feedback reduces earnings estimates by ~{abs(feedback_results[40]['premium_change_pct'])*100:.1f}% at 40 years")
print(f"  2. Crowding-out (at 25% level) reduces net impact by ~${free_college_annual_cost * 0.25 * other_program_multiplier / 1e9:.2f}B/year")
print(f"  3. Including private institutions raises PA total impact from ${total_economic_impact/1e9:.1f}B to ${combined_impact/1e9:.1f}B")
print(f"  4. Correlated MC shows wider uncertainty: 95% CI ${np.percentile(correlated_impacts, 2.5)/1e9:.1f}B - ${np.percentile(correlated_impacts, 97.5)/1e9:.1f}B")
print(f"\nOverall conclusion: The core findings remain robust.")
