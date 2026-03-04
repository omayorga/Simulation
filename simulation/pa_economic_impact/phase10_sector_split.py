import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 10: SECTOR-SPLIT OUTPUT — CC vs FOUR-YEAR INSTITUTIONS
# Uses the existing sector_type dict to produce separate ROI/cost/benefit tables
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 10: SECTOR-SPLIT ANALYSIS — Community Colleges vs Four-Year")
print("=" * 80)

sector_results = {}

for sector_label in ['two_year', 'four_year']:
    sector_insts = [inst for inst, st in sector_type.items() if st == sector_label]

    cum_state_cost = 0
    cum_new_grads = 0
    cum_earnings = 0
    cum_tax = 0
    annual_data_sector = []

    for i in range(40):
        year = start_year + i
        cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
        tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)
        wage_factor = (1 + wage_growth_real) ** (year - start_year)

        annual_cost = 0
        annual_new_enrollment = 0
        for inst in sector_insts:
            data = pa_resident_enrollment[inst]
            pa_students = int(data['total'] * data['in_state_pct'])
            boost = enrollment_boost.get(inst, 0.10)
            ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
            new_students = int(pa_students * boost * ramp)
            total_students = pa_students + new_students
            cost = total_students * data['tuition'] * tuition_factor
            annual_cost += cost
            annual_new_enrollment += new_students

        cum_state_cost += annual_cost / cpi_factor

        new_grads = 0
        grad_lag = 2 if sector_label == 'two_year' else 4
        completion_key = 'community_college_free' if sector_label == 'two_year' else 'four_year_free'
        earnings_key = 'associate' if sector_label == 'two_year' else 'bachelor'

        if i >= grad_lag:
            for inst in sector_insts:
                data = pa_resident_enrollment[inst]
                boost_students = int(data['total'] * data['in_state_pct'] * enrollment_boost.get(inst, 0.10))
                new_grads += int(boost_students * completion_rates[completion_key])

        cum_new_grads += new_grads
        annual_earnings = new_grads * (lifetime_earnings_premium[earnings_key] / 40) * wage_factor
        cum_earnings += annual_earnings
        cum_tax += annual_earnings * pa_state_income_tax

        annual_data_sector.append({
            'year': year, 'state_cost_real': annual_cost / cpi_factor,
            'new_graduates': new_grads, 'earnings_gain': annual_earnings
        })

    state_roi_sector = cum_tax / cum_state_cost if cum_state_cost > 0 else 0

    sector_results[sector_label] = {
        'institutions': sector_insts,
        'cumulative_state_cost': cum_state_cost,
        'cumulative_new_graduates': cum_new_grads,
        'cumulative_earnings_gain': cum_earnings,
        'cumulative_tax_revenue': cum_tax,
        'state_roi': state_roi_sector,
        'annual_data': annual_data_sector
    }

print(f"\n{'Sector':<18} {'State Cost (40yr)':>18} {'New Grads':>12} {'Earnings Gain':>16} {'Tax Revenue':>14} {'State ROI':>10}")
print("-" * 92)
for sector, r in sector_results.items():
    label = "Community Colleges" if sector == 'two_year' else "Four-Year"
    print(f"{label:<18} ${r['cumulative_state_cost']/1e9:>14.2f}B {r['cumulative_new_graduates']:>11,} "
          f"${r['cumulative_earnings_gain']/1e9:>12.2f}B ${r['cumulative_tax_revenue']/1e9:>10.3f}B {r['state_roi']:>9.3f}x")

# Save sector-split results
df_sector = pd.DataFrame([
    {'Sector': 'Community Colleges' if s == 'two_year' else 'Four-Year',
     'Institutions': ', '.join(r['institutions']),
     'State_Cost_40yr_B': r['cumulative_state_cost'] / 1e9,
     'New_Graduates_40yr': r['cumulative_new_graduates'],
     'Earnings_Gain_40yr_B': r['cumulative_earnings_gain'] / 1e9,
     'Tax_Revenue_40yr_B': r['cumulative_tax_revenue'] / 1e9,
     'State_ROI': r['state_roi']}
    for s, r in sector_results.items()
])
df_sector.to_csv(OUTPUT_DIR / 'sector_split_cc_vs_fouryear.csv', index=False)
print(f"\nSaved: sector_split_cc_vs_fouryear.csv")

# Sector-split visualization
try:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Phase 10: Community College vs Four-Year ROI Comparison (40-Year)', fontsize=14, fontweight='bold')

    sectors = ['Community Colleges', 'Four-Year']
    costs = [sector_results['two_year']['cumulative_state_cost']/1e9,
             sector_results['four_year']['cumulative_state_cost']/1e9]
    grads_s = [sector_results['two_year']['cumulative_new_graduates'],
               sector_results['four_year']['cumulative_new_graduates']]
    rois = [sector_results['two_year']['state_roi'],
            sector_results['four_year']['state_roi']]

    x = np.arange(2)
    ax1.bar(x - 0.2, costs, 0.4, label='State Cost ($B)', color='#E63946', alpha=0.85)
    ax1.bar(x + 0.2, [sector_results['two_year']['cumulative_tax_revenue']/1e9,
                       sector_results['four_year']['cumulative_tax_revenue']/1e9],
            0.4, label='Tax Revenue ($B)', color='#06D6A0', alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(sectors)
    ax1.set_ylabel('$ Billion (2024$)')
    ax1.set_title('Cost vs Revenue by Sector', fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # ROI trajectory over time
    for sector, color, label in [('two_year', '#2E86AB', 'Community Colleges'),
                                  ('four_year', '#F18F01', 'Four-Year')]:
        years_s = [d['year'] for d in sector_results[sector]['annual_data']]
        cum_cost_s = np.cumsum([d['state_cost_real'] for d in sector_results[sector]['annual_data']])
        cum_tax_s = np.cumsum([d['earnings_gain'] * pa_state_income_tax for d in sector_results[sector]['annual_data']])
        roi_traj = cum_tax_s / np.maximum(cum_cost_s, 1)
        ax2.plot(years_s, roi_traj, linewidth=2, color=color, label=label)

    ax2.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Break-Even')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Cumulative State ROI')
    ax2.set_title('ROI Trajectory by Sector', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig15_sector_split_roi.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig15_sector_split_roi.png")

except Exception as e:
    logger.error(f"Error generating Phase 10 visualizations: {e}")
    import traceback
    traceback.print_exc()
