"""Phase 6: Free College for PA Residents - Policy Simulation

Starting Fall 2026 | PA Residents Only | Inflation-Adjusted

Sources: PASSHE, Penn State, Pitt, Temple, PA Community Colleges, SHEEO,
         Tennessee Promise, Georgetown CEW, APLU, BLS
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# PHASE 6: FREE COLLEGE FOR PA RESIDENTS - POLICY SIMULATION
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 6: FREE COLLEGE FOR PA RESIDENTS - POLICY SIMULATION")
print("Starting Fall 2026 | PA Residents Only | Inflation-Adjusted")
print("=" * 80)

_total_pa_residents = 0
_total_tuition_cost_to_state = 0
for inst, data in pa_resident_enrollment.items():
    pa_students = int(data['total'] * data['in_state_pct'])
    annual_tuition_cost = pa_students * data['tuition']
    _total_pa_residents += pa_students
    _total_tuition_cost_to_state += annual_tuition_cost
    print(f"  {inst}: {pa_students:,} PA residents x ${data['tuition']:,} = ${annual_tuition_cost/1e6:.1f}M")

print(f"\nTotal PA Resident Students: {_total_pa_residents:,}")
print(f"Total Annual Tuition Cost to State (Year 1): ${_total_tuition_cost_to_state/1e9:.2f}B")

total_pa_residents = _total_pa_residents
total_tuition_cost_to_state = _total_tuition_cost_to_state

print("\n" + "-" * 60)
print("FREE COLLEGE SIMULATION RESULTS")
print("-" * 60)

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

        grad_lag_cc = 2
        grad_lag_4yr = 4

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

print(f"\n{'='*80}")
print("FREE COLLEGE SIMULATION RESULTS SUMMARY (All values in 2024 dollars)")
print(f"{'='*80}")
print(f"\n{'Horizon':<10} {'State Cost':>14} {'New Grads':>12} {'Earnings Gain':>16} {'Tax Revenue':>14} {'State ROI':>10}")
print("-" * 80)
for horizon in simulation_horizons:
    r = results[horizon]
    print(f"{horizon} Years{'':<4} ${r['cumulative_state_cost']/1e9:>10.1f}B {r['cumulative_new_graduates']:>11,} ${r['cumulative_earnings_gain']/1e9:>12.1f}B ${r['cumulative_tax_revenue']/1e9:>10.2f}B {r['state_roi']:>9.2f}x")

print(f"\n--- ROI TO INDIVIDUALS ---")
print(f"Bachelor's Degree Holder: {results[40]['individual_roi_bachelor']:.1f}x return on tuition saved")
print(f"Associate Degree Holder: {results[40]['individual_roi_associate']:.1f}x return on tuition saved")
print(f"Lifetime earnings premium (Bachelor's): ${lifetime_earnings_premium['bachelor']:,}")
print(f"Lifetime earnings premium (Associate): ${lifetime_earnings_premium['associate']:,}")

print(f"\n--- BRAIN DRAIN REDUCTION ---")
print(f"Baseline brain drain: {brain_drain_baseline*100:.0f}% of graduates leave PA")
print(f"Projected with free college: {brain_drain_free_college*100:.0f}% leave PA")
for horizon in simulation_horizons:
    r = results[horizon]
    print(f"  {horizon}-Year cumulative retained tax revenue: ${r['cumulative_brain_drain_savings']/1e6:.1f}M")

print(f"\n--- GDP / ECONOMIC MULTIPLIER IMPACT ---")
for horizon in simulation_horizons:
    r = results[horizon]
    print(f"  {horizon}-Year cumulative GDP impact: ${r['cumulative_gdp_impact']/1e9:.2f}B")

try:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Phase 6: Free College for PA Residents - Policy Simulation\n(Starting Fall 2026, Inflation-Adjusted to 2024$)',
                 fontsize=16, fontweight='bold')

    horizons_labels = [f'{h} Year' for h in simulation_horizons]
    costs = [results[h]['cumulative_state_cost']/1e9 for h in simulation_horizons]
    tax_rev = [results[h]['cumulative_tax_revenue']/1e9 for h in simulation_horizons]
    brain_sav = [results[h]['cumulative_brain_drain_savings']/1e9 for h in simulation_horizons]

    x_pos = np.arange(len(horizons_labels))
    width = 0.25
    ax1.bar(x_pos - width, costs, width, label='State Cost', color='#E63946', alpha=0.85)
    ax1.bar(x_pos, tax_rev, width, label='Tax Revenue Gain', color='#06D6A0', alpha=0.85)
    ax1.bar(x_pos + width, brain_sav, width, label='Brain Drain Savings', color='#118AB2', alpha=0.85)
    ax1.set_xlabel('Time Horizon')
    ax1.set_ylabel('$ Billion (2024$)')
    ax1.set_title('State Investment vs Returns', fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(horizons_labels)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    roi_values = [results[h]['state_roi'] for h in simulation_horizons]
    colors_roi = ['#E63946' if r < 1 else '#06D6A0' for r in roi_values]
    ax2.bar(horizons_labels, roi_values, color=colors_roi, edgecolor='black', alpha=0.85)
    ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='Break-Even')
    ax2.set_ylabel('ROI Ratio (Benefits / Cost)')
    ax2.set_title('State Return on Investment', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    for i, val in enumerate(roi_values):
        ax2.text(i, val + 0.05, f'{val:.2f}x', ha='center', fontweight='bold', fontsize=11)

    grads = [results[h]['cumulative_new_graduates'] for h in simulation_horizons]
    ax3.bar(horizons_labels, grads, color='#A23B72', edgecolor='black', alpha=0.85)
    ax3.set_ylabel('Cumulative Additional Graduates')
    ax3.set_title('New Graduates from Free College', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    for i, val in enumerate(grads):
        ax3.text(i, val + 500, f'{val:,}', ha='center', fontweight='bold', fontsize=10)

    earnings = [results[h]['cumulative_earnings_gain']/1e9 for h in simulation_horizons]
    gdp = [results[h]['cumulative_gdp_impact']/1e9 for h in simulation_horizons]
    ax4.bar(x_pos - 0.2, earnings, 0.4, label='Earnings Gain', color='#F18F01', alpha=0.85)
    ax4.bar(x_pos + 0.2, gdp, 0.4, label='GDP Impact', color='#2E86AB', alpha=0.85)
    ax4.set_ylabel('$ Billion (2024$)')
    ax4.set_title('Economic Growth from Free College', fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(horizons_labels)
    ax4.legend(fontsize=9)
    ax4.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig9_free_college_roi.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig9_free_college_roi.png")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle('Free College for PA: 40-Year Economic Projection (2024$)',
                 fontsize=16, fontweight='bold')

    data_40 = results[40]['annual_data']
    years_40 = [d['year'] for d in data_40]
    costs_40 = [d['state_cost_real']/1e9 for d in data_40]
    tax_40 = [d['tax_gain']/1e9 for d in data_40]
    brain_40 = [d['brain_drain_savings']/1e9 for d in data_40]
    benefits_40 = [t + b for t, b in zip(tax_40, brain_40)]

    ax1.fill_between(years_40, costs_40, alpha=0.3, color='#E63946', label='State Cost')
    ax1.fill_between(years_40, benefits_40, alpha=0.3, color='#06D6A0', label='Combined Benefits')
    ax1.plot(years_40, costs_40, color='#E63946', linewidth=2)
    ax1.plot(years_40, benefits_40, color='#06D6A0', linewidth=2)
    ax1.set_ylabel('$ Billion (2024$)')
    ax1.set_title('Annual State Cost vs Benefits', fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    cum_cost = np.cumsum(costs_40)
    cum_benefit = np.cumsum(benefits_40)
    cum_net = [b - c for b, c in zip(cum_benefit, cum_cost)]

    ax2.plot(years_40, cum_net, color='#2E86AB', linewidth=2.5)
    ax2.fill_between(years_40, cum_net, alpha=0.3,
                     where=[n >= 0 for n in cum_net], color='#06D6A0', label='Net Positive')
    ax2.fill_between(years_40, cum_net, alpha=0.3,
                     where=[n < 0 for n in cum_net], color='#E63946', label='Net Negative')
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Cumulative Net Benefit ($ Billion, 2024$)')
    ax2.set_title('Cumulative Net Fiscal Impact to PA', fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig10_free_college_40yr_timeline.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig10_free_college_40yr_timeline.png")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('Free College: Return on Investment for Individuals vs State',
                 fontsize=14, fontweight='bold')

    degree_types = ["Associate's\n(2-Year)", "Bachelor's\n(4-Year)"]
    earnings_premium = [lifetime_earnings_premium['associate']/1000, lifetime_earnings_premium['bachelor']/1000]

    x_ind = np.arange(len(degree_types))
    ax1.bar(x_ind - 0.2, [pa_resident_enrollment['Community Colleges']['tuition'] * 2 / 1000,
                           sum(d['tuition'] for inst, d in pa_resident_enrollment.items()
                               if inst != 'Community Colleges') * 4 / 5 / 1000],
            0.4, label='Tuition Saved (Free College)', color='#06D6A0', edgecolor='black')
    ax1.bar(x_ind + 0.2, earnings_premium, 0.4,
            label='Lifetime Earnings Premium', color='#F18F01', edgecolor='black')
    ax1.set_ylabel('$ Thousands')
    ax1.set_title('Individual: Tuition Saved vs Earnings Gain', fontweight='bold')
    ax1.set_xticks(x_ind)
    ax1.set_xticklabels(degree_types)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    state_rois = [results[h]['state_roi'] for h in simulation_horizons]
    ax2.plot(simulation_horizons, state_rois, marker='o', linewidth=2.5, color='#2E86AB', markersize=10)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, label='Break-Even (1.0x)')
    ax2.fill_between(simulation_horizons, state_rois, 1.0,
                     where=[r >= 1.0 for r in state_rois], alpha=0.2, color='#06D6A0')
    ax2.fill_between(simulation_horizons, state_rois, 1.0,
                     where=[r < 1.0 for r in state_rois], alpha=0.2, color='#E63946')
    ax2.set_xlabel('Years After Implementation')
    ax2.set_ylabel('State ROI (Benefits / Cost)')
    ax2.set_title('State ROI Trajectory Over Time', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    for h, r in zip(simulation_horizons, state_rois):
        ax2.annotate(f'{r:.2f}x', (h, r), textcoords='offset points',
                    xytext=(0, 12), ha='center', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig11_free_college_individual_roi.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig11_free_college_individual_roi.png")

except Exception as e:
    logger.error(f"Error generating Phase 6 visualizations: {e}")
    import traceback
    traceback.print_exc()

df_free_college = pd.DataFrame([
    {'Horizon': f'{h} Years',
     'State_Cost_B': f"${results[h]['cumulative_state_cost']/1e9:.2f}",
     'New_Graduates': results[h]['cumulative_new_graduates'],
     'Earnings_Gain_B': f"${results[h]['cumulative_earnings_gain']/1e9:.2f}",
     'Tax_Revenue_B': f"${results[h]['cumulative_tax_revenue']/1e9:.3f}",
     'Brain_Drain_Savings_M': f"${results[h]['cumulative_brain_drain_savings']/1e6:.1f}",
     'GDP_Impact_B': f"${results[h]['cumulative_gdp_impact']/1e9:.2f}",
     'State_ROI': f"{results[h]['state_roi']:.2f}x"}
    for h in simulation_horizons
])
df_free_college.to_csv(OUTPUT_DIR / 'free_college_simulation_results.csv', index=False)
print(f"Saved: free_college_simulation_results.csv")

df_annual_40 = pd.DataFrame(results[40]['annual_data'])
df_annual_40.to_csv(OUTPUT_DIR / 'free_college_40yr_annual.csv', index=False)
print(f"Saved: free_college_40yr_annual.csv")

print("\nFederal Matching Scenarios (Free College, 40-Year Horizon)")
print("-" * 60)
forty = results[40]
for ratio in federal_match_ratios:
    federal_contribution = forty['cumulative_state_cost'] * ratio
    total_public_cost = forty['cumulative_state_cost'] + federal_contribution
    effective_state_share = forty['cumulative_state_cost'] / total_public_cost
    print(f"Match {ratio}:1 -> State share = {effective_state_share*100:5.1f}% of total program cost")
