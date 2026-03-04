"""Phase 5: Visualizations (Charts 1-8)
Pennsylvania Higher Education Economic Impact Analysis

Generates all 8 charts (fig1 through fig8) from Phases 1-4 data.
All data is recomputed here so this file runs independently.
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# RECOMPUTE INTERMEDIATE DATA NEEDED FOR VISUALIZATIONS
# ============================================================================

# --- Phase 3 data: df_historical ---
assert validate_data_lengths(historical_data, 17), "Historical data length mismatch!"
df_historical = pd.DataFrame(historical_data)
df_historical['state_appropriation_real'] = (
    df_historical['state_appropriation_nominal'] / df_historical['cpi_adjustment']
)
df_historical['total_enrollment'] = (
    df_historical['passhe_enrollment'] + df_historical['state_related_enrollment']
)
df_historical['appropriation_per_fte'] = (
    df_historical['state_appropriation_real'] * 1e6 / df_historical['total_enrollment']
)
df_historical['cumulative_wage_factor'] = (1 + df_historical['real_wage_growth']).cumprod()
df_historical['appropriation_wage_adjusted'] = (
    df_historical['state_appropriation_real'] / df_historical['cumulative_wage_factor']
)
df_historical['per_fte_wage_adjusted'] = (
    df_historical['appropriation_wage_adjusted'] * 1e6 / df_historical['total_enrollment']
)
df_historical['tuition_real'] = (
    df_historical['tuition_avg_public'] / df_historical['cpi_adjustment']
)

# --- Phase 2 data: Monte Carlo ---
np.random.seed(RANDOM_SEED)
simulation_results = {}
for param, (mean, std) in param_distributions.items():
    simulation_results[param] = np.random.normal(mean, std, MONTE_CARLO_SIMULATIONS)
impact_distribution = base_direct_spending * simulation_results['output_multiplier']

# --- Phase 4 data: county ---
county_impact = {}

for name, data in state_related_universities.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['operating_budget']

for name, data in passhe_universities.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['enrollment'] * 15000

for name, data in community_colleges.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['enrollment'] * 10000

for county, data in county_impact.items():
    data['direct_impact'] = data['spending']
    data['total_impact'] = data['spending'] * rims_ii_multipliers['output_multiplier']
    data['jobs_supported'] = int(data['employees'] * 1.8)
    data['student_spending'] = data['enrollment'] * avg_student_spending * 0.65

df_county = pd.DataFrame([
    {
        'County': county,
        'Enrollment': data['enrollment'],
        'Employees': data['employees'],
        'Institutions': len(data['institutions']),
        'Direct_Impact_M': data['direct_impact'] / 1e6,
        'Total_Impact_M': data['total_impact'] / 1e6,
        'Jobs_Supported': data['jobs_supported'],
        'Student_Spending_M': data['student_spending'] / 1e6
    }
    for county, data in county_impact.items()
]).sort_values('Total_Impact_M', ascending=False)

df_county_no_bigflagships = df_county[~df_county['County'].isin(['Centre', 'Allegheny'])]

# ============================================================================
# PHASE 5: VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Save historical data (also done in phase3, but needed if running standalone)
df_historical.to_csv(OUTPUT_DIR / 'historical_trends_2010_2026.csv', index=False)
print(f"\nSaved: historical_trends_2010_2026.csv")

try:
    # CHART 1: Historical Trends with Wage-Adjusted Line (IMPROVED)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Pennsylvania Higher Education Historical Trends (2010-2026)',
                 fontsize=16, fontweight='bold')

    ax1.plot(df_historical['year'], df_historical['state_appropriation_real'],
             marker='o', linewidth=2, color='#2E86AB', label='CPI-Adjusted (2024 $)')
    ax1.plot(df_historical['year'], df_historical['appropriation_wage_adjusted'],
             marker='s', linewidth=2, color='#E63946', linestyle='--', label='Wage-Adjusted')
    ax1.set_title('State Appropriations', fontweight='bold')
    ax1.set_ylabel('Appropriation ($ Million)')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9)

    ax2.plot(df_historical['year'], df_historical['passhe_enrollment'],
             marker='s', linewidth=2, color='#A23B72')
    ax2.axvline(x=2025, color='green', linestyle='--', alpha=0.5, label='First Increase')
    ax2.set_title('PASSHE Enrollment Decline & Recovery', fontweight='bold')
    ax2.set_ylabel('Total Enrollment')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9)

    ax3.plot(df_historical['year'], df_historical['appropriation_per_fte'],
             marker='^', linewidth=2, color='#F18F01', label='CPI-Adjusted')
    ax3.plot(df_historical['year'], df_historical['per_fte_wage_adjusted'],
             marker='v', linewidth=2, color='#C73E1D', linestyle='--', label='Wage-Adjusted')
    ax3.axhline(y=11683, color='red', linestyle=':', alpha=0.5, label='National Avg')
    ax3.set_title('Per-Student State Funding', fontweight='bold')
    ax3.set_ylabel('$ per FTE')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9)

    ax4.plot(df_historical['year'], df_historical['tuition_avg_public'],
             marker='D', linewidth=2, color='#C73E1D', label='Nominal')
    ax4.plot(df_historical['year'], df_historical['tuition_real'],
             marker='o', linewidth=2, color='#06D6A0', linestyle='--', label='Real (2024 $)')
    ax4.set_title('Average In-State Tuition', fontweight='bold')
    ax4.set_ylabel('Annual Tuition ($)')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_historical_trends.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig1_historical_trends.png")

    # CHART 2: Employment by Sector
    fig, ax = plt.subplots(figsize=(12, 8))
    sector_names = list(employment_sectors.keys())
    sector_counts = [s['count'] for s in employment_sectors.values()]
    colors = plt.cm.Set3(range(len(sector_names)))
    ax.barh(sector_names, sector_counts, color=colors, edgecolor='black', alpha=0.8)
    ax.set_xlabel('Number of Employees', fontsize=12, fontweight='bold')
    ax.set_title('Higher Education Employment by Sector (2025)', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    for i, count in enumerate(sector_counts):
        ax.text(count + 500, i, f'{count:,}', va='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig2_employment_by_sector.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig2_employment_by_sector.png")

    # CHART 3: Research Expenditures
    fig, ax = plt.subplots(figsize=(10, 7))
    research_institutions = list(research_data.keys())
    research_totals = [r['total']/1e9 for r in research_data.values()]
    ax.bar(research_institutions, research_totals, color=['#1F77B4', '#FF7F0E', '#2CA02C'],
           edgecolor='black', alpha=0.85)
    ax.set_ylabel('Research Expenditures ($ Billion)', fontsize=12, fontweight='bold')
    ax.set_title('Research Expenditures (FY 2024-25)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    for i, val in enumerate(research_totals):
        ax.text(i, val + 0.05, f'${val:.2f}B', ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_research_expenditures.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig3_research_expenditures.png")

    # CHART 4: Policy Scenario Comparison
    fig, ax = plt.subplots(figsize=(12, 7))
    scenario_names = list(policy_scenarios.keys())
    scenario_impacts = []
    for params in policy_scenarios.values():
        ic = params['appropriation_change'] * 0.3 + params['enrollment_change'] * 0.5 + params['tuition_change'] * -0.1
        scenario_impacts.append(base_economic_impact * (1 + ic) / 1e9)
    colors_policy = ['gray', 'green', 'blue', 'purple', 'red']
    ax.barh(scenario_names, scenario_impacts, color=colors_policy, edgecolor='black', alpha=0.8)
    ax.axvline(x=base_economic_impact/1e9, color='black', linestyle='--', linewidth=2, label='Baseline')
    ax.set_xlabel('Total Economic Impact ($ Billion)', fontsize=12, fontweight='bold')
    ax.set_title('Policy Scenario Economic Impact Projections', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    ax.legend()
    for i, val in enumerate(scenario_impacts):
        ax.text(val + 0.3, i, f'${val:.1f}B', va='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_policy_scenarios.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig4_policy_scenarios.png")

    # CHART 5: Economic Impact Pie
    fig, ax = plt.subplots(figsize=(10, 10))
    labels = [c.replace('_', ' ').title() for c in economic_impact_components.keys()]
    sizes = list(economic_impact_components.values())
    colors_pie = plt.cm.Set2(range(len(labels)))
    explode = (0.05, 0, 0, 0.05, 0)
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
           startangle=90, colors=colors_pie, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax.set_title(f'Total Economic Impact: ${total_economic_impact/1e9:.1f}B',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_economic_impact_breakdown.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig5_economic_impact_breakdown.png")

    # CHART 6: ROI & Tax Revenue
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.bar(['State\nInvestment', 'Economic\nReturn'],
            [total_state_appropriation/1e9, total_economic_impact/1e9],
            color=['#E63946', '#06D6A0'], edgecolor='black', alpha=0.85)
    ax1.set_ylabel('$ Billion', fontsize=12, fontweight='bold')
    ax1.set_title(f'ROI: ${roi_ratio:.2f} per $1 Invested', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    for i, val in enumerate([total_state_appropriation/1e9, total_economic_impact/1e9]):
        ax1.text(i, val + 0.5, f'${val:.1f}B', ha='center', fontsize=11, fontweight='bold')
    ax2.bar(['State\nAppropriation', 'Tax Revenue\nGenerated', 'Net Return\nto State'],
            [total_state_appropriation/1e9, tax_revenue_generated/1e9,
             (tax_revenue_generated - total_state_appropriation)/1e9],
            color=['#E63946', '#118AB2', '#06D6A0'], edgecolor='black', alpha=0.85)
    ax2.set_ylabel('$ Billion', fontsize=12, fontweight='bold')
    ax2.set_title('Tax Revenue Generation & Net Return', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(y=0, color='black', linewidth=1)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig6_roi_and_tax_revenue.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig6_roi_and_tax_revenue.png")

    # CHART 7: County-Level Economic Impact
    fig, ax = plt.subplots(figsize=(14, 8))
    top_counties = df_county_no_bigflagships.head(12)  # Exclude Penn State UP and Pitt for messaging
    bars = ax.barh(top_counties['County'], top_counties['Total_Impact_M'],
                   color=plt.cm.viridis(np.linspace(0.3, 0.9, len(top_counties))),
                   edgecolor='black', alpha=0.85)
    ax.set_xlabel('Total Economic Impact ($ Millions)', fontsize=12, fontweight='bold')
    ax.set_title('County-Level Higher Education Economic Impact', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    for i, val in enumerate(top_counties['Total_Impact_M']):
        ax.text(val + 50, i, f'${val:,.0f}M', va='center', fontsize=9, fontweight='bold')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig7_county_impact.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig7_county_impact.png")

    # CHART 8: Monte Carlo Distribution
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.hist(impact_distribution/1e9, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(impact_distribution)/1e9, color='red', linewidth=2,
               label=f'Mean: ${np.mean(impact_distribution)/1e9:.1f}B')
    ci_low = np.percentile(impact_distribution, 2.5)/1e9
    ci_high = np.percentile(impact_distribution, 97.5)/1e9
    ax.axvline(x=ci_low, color='orange', linestyle='--', linewidth=1.5, label=f'95% CI: ${ci_low:.1f}B')
    ax.axvline(x=ci_high, color='orange', linestyle='--', linewidth=1.5, label=f'95% CI: ${ci_high:.1f}B')
    ax.set_xlabel('Economic Impact ($ Billion)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'Monte Carlo: Economic Impact Uncertainty (n={MONTE_CARLO_SIMULATIONS:,})',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig8_monte_carlo_distribution.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig8_monte_carlo_distribution.png")

except Exception as e:
    logger.error(f"Error generating visualizations: {e}")
    import traceback
    traceback.print_exc()
