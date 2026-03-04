"""Phase 9: Demographic-Segmented Free College Analysis

Broken down by Race, Gender, First-Generation Status, and Income Tier

Sources: IPEDS, NCES Digest of Education Statistics, Pell Grant data
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 9: DEMOGRAPHIC-SEGMENTED ANALYSIS
# Sources: IPEDS, NCES Digest of Education Statistics, Pell Grant data
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 9: DEMOGRAPHIC-SEGMENTED FREE COLLEGE ANALYSIS")
print("Broken down by Race, Gender, First-Generation Status, and Income Tier")
print("=" * 80)

# 9.1 Demographic enrollment shares — imported from config (demographic_shares)
# 9.2 Differential completion rates by demographic — imported from config
#     (completion_rate_multipliers, free_college_boost_by_group)
# Base rates: CC current=0.28, CC free=0.34, 4yr current=0.62, 4yr free=0.68

# Recompute total_pa_residents for this phase (same calculation as Phase 6)
total_pa_residents = sum(
    int(data['total'] * data['in_state_pct'])
    for data in pa_resident_enrollment.values()
)

# 9.3 Run demographic-segmented simulation (40-year horizon)
demographic_results = {}
horizon_demo = 40

for dimension, groups in demographic_shares.items():
    demographic_results[dimension] = {}
    for group, share in groups.items():
        group_pa_residents = int(total_pa_residents * share)

        # Completion rates for this group
        cc_mult = completion_rate_multipliers[dimension][group]['cc']
        four_yr_mult = completion_rate_multipliers[dimension][group]['four_yr']

        cc_rate_current = completion_rates['community_college_current'] * cc_mult
        cc_rate_free = min(cc_rate_current + free_college_boost_by_group[dimension][group], 0.65)
        four_yr_rate_current = completion_rates['four_year_current'] * four_yr_mult
        four_yr_rate_free = min(four_yr_rate_current + free_college_boost_by_group[dimension][group], 0.90)

        # Simplified 40-year projection for this group
        cum_state_cost = 0
        cum_new_grads = 0
        cum_earnings = 0

        for i in range(horizon_demo):
            year = start_year + i
            cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
            tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)
            wage_factor = (1 + wage_growth_real) ** (year - start_year)

            # State cost for this group
            annual_cost = 0
            for inst, data in pa_resident_enrollment.items():
                pa_students_group = int(data['total'] * data['in_state_pct'] * share)
                boost = enrollment_boost.get(inst, 0.10)
                ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
                new_students = int(pa_students_group * boost * ramp)
                total_students = pa_students_group + new_students
                cost = total_students * data['tuition'] * tuition_factor
                annual_cost += cost

            cum_state_cost += annual_cost / cpi_factor

            # New graduates
            new_cc_grads = 0
            new_4yr_grads = 0
            if i >= 2:
                cc_group = int(pa_resident_enrollment['Community Colleges']['total'] *
                              pa_resident_enrollment['Community Colleges']['in_state_pct'] *
                              share * enrollment_boost['Community Colleges'])
                new_cc_grads = int(cc_group * cc_rate_free)
            if i >= 4:
                four_yr_group = sum(
                    int(pa_resident_enrollment[inst]['total'] *
                        pa_resident_enrollment[inst]['in_state_pct'] *
                        share * enrollment_boost.get(inst, 0.10))
                    for inst in ['PASSHE', 'Penn State', 'Pitt', 'Temple', 'Lincoln']
                )
                new_4yr_grads = int(four_yr_group * four_yr_rate_free)

            cum_new_grads += new_cc_grads + new_4yr_grads

            annual_earnings_cc = new_cc_grads * (lifetime_earnings_premium['associate'] / 40) * wage_factor
            annual_earnings_4yr = new_4yr_grads * (lifetime_earnings_premium['bachelor'] / 40) * wage_factor
            cum_earnings += annual_earnings_cc + annual_earnings_4yr

        cum_tax = cum_earnings * pa_state_income_tax

        demographic_results[dimension][group] = {
            'share': share,
            'pa_residents': group_pa_residents,
            'state_cost_40yr': cum_state_cost,
            'new_graduates_40yr': cum_new_grads,
            'earnings_gain_40yr': cum_earnings,
            'tax_revenue_40yr': cum_tax,
            'cc_completion_current': cc_rate_current,
            'cc_completion_free': cc_rate_free,
            'four_yr_completion_current': four_yr_rate_current,
            'four_yr_completion_free': four_yr_rate_free
        }

# Print demographic results
for dimension, groups in demographic_results.items():
    print(f"\n--- {dimension.upper()} ---")
    print(f"{'Group':<25} {'Share':>6} {'PA Students':>12} {'New Grads':>10} {'Earnings Gain':>15} {'CC Comp Rate':>12}")
    print("-" * 85)
    for group, r in groups.items():
        print(f"{group:<25} {r['share']*100:>5.0f}% {r['pa_residents']:>11,} {r['new_graduates_40yr']:>9,} "
              f"${r['earnings_gain_40yr']/1e9:>11.2f}B {r['cc_completion_free']*100:>10.1f}%")

# Save demographic results
demo_rows = []
for dimension, groups in demographic_results.items():
    for group, r in groups.items():
        demo_rows.append({
            'Dimension': dimension,
            'Group': group,
            'Share': r['share'],
            'PA_Residents': r['pa_residents'],
            'State_Cost_40yr_B': r['state_cost_40yr'] / 1e9,
            'New_Graduates_40yr': r['new_graduates_40yr'],
            'Earnings_Gain_40yr_B': r['earnings_gain_40yr'] / 1e9,
            'Tax_Revenue_40yr_B': r['tax_revenue_40yr'] / 1e9,
            'CC_Completion_Current': r['cc_completion_current'],
            'CC_Completion_Free': r['cc_completion_free'],
            'FourYr_Completion_Current': r['four_yr_completion_current'],
            'FourYr_Completion_Free': r['four_yr_completion_free']
        })
df_demographic = pd.DataFrame(demo_rows)
df_demographic.to_csv(OUTPUT_DIR / 'demographic_segmented_analysis.csv', index=False)
print(f"\nSaved: demographic_segmented_analysis.csv")

# 9.4 Demographic Visualization
try:
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Phase 9: Demographic-Segmented Free College Impact (40-Year, 2024$)',
                 fontsize=16, fontweight='bold')

    for idx, (dimension, ax) in enumerate(zip(['race', 'gender', 'first_gen', 'income'], axes.flat)):
        groups = demographic_results[dimension]
        group_names = list(groups.keys())
        new_grads = [groups[g]['new_graduates_40yr'] for g in group_names]

        colors_demo = plt.cm.Set2(range(len(group_names)))
        bars = ax.bar(range(len(group_names)), new_grads, color=colors_demo, edgecolor='black', alpha=0.85)
        ax.set_title(f'By {dimension.replace("_", " ").title()}', fontweight='bold')
        ax.set_ylabel('New Graduates (40yr)')
        ax.set_xticks(range(len(group_names)))
        ax.set_xticklabels([g.replace(' ', '\n') for g in group_names], fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        for i, val in enumerate(new_grads):
            ax.text(i, val + max(new_grads)*0.02, f'{val:,}', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig13_demographic_segmentation.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig13_demographic_segmentation.png")

    # Completion rate gap chart
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Completion Rate Gaps: Current vs Free College by Race', fontsize=14, fontweight='bold')

    race_groups = list(demographic_results['race'].keys())
    cc_current = [demographic_results['race'][g]['cc_completion_current'] for g in race_groups]
    cc_free = [demographic_results['race'][g]['cc_completion_free'] for g in race_groups]
    four_yr_current = [demographic_results['race'][g]['four_yr_completion_current'] for g in race_groups]
    four_yr_free = [demographic_results['race'][g]['four_yr_completion_free'] for g in race_groups]

    x = np.arange(len(race_groups))
    width = 0.35
    axes[0].bar(x - width/2, [c*100 for c in cc_current], width, label='Current', color='#E63946', alpha=0.8)
    axes[0].bar(x + width/2, [c*100 for c in cc_free], width, label='Free College', color='#06D6A0', alpha=0.8)
    axes[0].set_title('Community College Completion Rates', fontweight='bold')
    axes[0].set_ylabel('Completion Rate (%)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(race_groups, fontsize=9)
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)

    axes[1].bar(x - width/2, [c*100 for c in four_yr_current], width, label='Current', color='#E63946', alpha=0.8)
    axes[1].bar(x + width/2, [c*100 for c in four_yr_free], width, label='Free College', color='#06D6A0', alpha=0.8)
    axes[1].set_title('Four-Year Completion Rates', fontweight='bold')
    axes[1].set_ylabel('Completion Rate (%)')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(race_groups, fontsize=9)
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig14_completion_rate_gaps.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig14_completion_rate_gaps.png")

except Exception as e:
    logger.error(f"Error generating Phase 9 visualizations: {e}")
    import traceback
    traceback.print_exc()
