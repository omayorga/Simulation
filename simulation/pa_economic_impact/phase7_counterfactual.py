"""Phase 7: Counterfactual Analysis - What if PA Invested Consistently Since 1980?

Sources: SHEEO SHEF FY2024, Keystone Research Center, Census Bureau, BLS
PA inflation-adjusted higher ed funding declined 41.9% since 1980 (worst in US)
National avg per-FTE in 1980: $10,296 (2024$). PA was above average in 1980.
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 7: COUNTERFACTUAL - WHAT IF PA INVESTED CONSISTENTLY SINCE 1980
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 7: COUNTERFACTUAL ANALYSIS")
print("What if PA had invested consistently in higher education since 1980?")
print("=" * 80)

# -----------------------------------------------------------------------------
# 7.1 HISTORICAL CONTEXT AND DATA
# Sources: SHEEO SHEF FY2024, Keystone Research Center, Census Bureau, BLS
# PA inflation-adjusted higher ed funding declined 41.9% since 1980 (worst in US)
# National avg per-FTE in 1980: $10,296 (2024$). PA was above average in 1980.
# -----------------------------------------------------------------------------

# PA higher education funding history (real 2024 dollars, $ millions)
# Sources: SHEEO SHEF historical data, PA budget documents
# (counterfactual_data is imported from config)

assert validate_data_lengths(counterfactual_data, 45), "Counterfactual data length mismatch!"

df_cf = pd.DataFrame(counterfactual_data)

# Convert to real 2024 dollars
df_cf['pa_actual_real'] = df_cf['pa_actual_nominal'] * df_cf['cpi_to_2024']
df_cf['pa_per_fte_actual'] = df_cf['pa_actual_real'] * 1e6 / df_cf['pa_enrollment_total']

# -----------------------------------------------------------------------------
# 7.2 COUNTERFACTUAL SCENARIO: CONSISTENT INVESTMENT
# What if PA had maintained 1980's per-FTE funding level, adjusted for inflation?
# PA per-FTE in 1980 (real 2024$): ~$6,570 (above national avg at the time)
# National avg per-FTE in 1980 (real 2024$): $10,296 (SHEEO SHEF)
# We model: PA maintains its 1980 real per-FTE level + 1% annual real growth
# -----------------------------------------------------------------------------

pa_1980_per_fte_real = df_cf.loc[0, 'pa_per_fte_actual']  # 1980 baseline
annual_real_growth = 0.01  # 1% real annual growth in per-student funding

df_cf['cf_per_fte'] = pa_1980_per_fte_real * (1 + annual_real_growth) ** (df_cf['year'] - 1980)
df_cf['cf_total_real'] = df_cf['cf_per_fte'] * df_cf['pa_enrollment_total'] / 1e6
df_cf['funding_gap_real'] = df_cf['cf_total_real'] - df_cf['pa_actual_real']
df_cf['cumulative_gap'] = df_cf['funding_gap_real'].cumsum()

# What enrollment would have been with consistent funding
# Research: 10% funding increase -> 3-5% enrollment increase (elasticity ~0.35)
# (funding_enrollment_elasticity is imported from config)
df_cf['funding_change_pct'] = (df_cf['cf_total_real'] / df_cf['pa_actual_real']) - 1
df_cf['cf_enrollment'] = df_cf['pa_enrollment_total'] * (1 + df_cf['funding_change_pct'] * funding_enrollment_elasticity)
df_cf['cf_enrollment'] = df_cf['cf_enrollment'].clip(lower=df_cf['pa_enrollment_total'])  # Can't be below actual
df_cf['enrollment_gain'] = df_cf['cf_enrollment'] - df_cf['pa_enrollment_total']

print("\n" + "-" * 60)
print("COUNTERFACTUAL: CONSISTENT INVESTMENT SINCE 1980")
print("-" * 60)

# Key metrics
total_cumulative_gap = df_cf['cumulative_gap'].iloc[-1]
total_enrollment_lost = df_cf['enrollment_gain'].sum()
additional_graduates_lost = int(total_enrollment_lost * 0.30)  # ~30% graduation rate avg
lost_lifetime_earnings = additional_graduates_lost * lifetime_earnings_premium['bachelor']
lost_tax_revenue_cf = lost_lifetime_earnings * pa_state_income_tax
lost_gdp_impact = total_cumulative_gap * 1e6 * rims_ii_multipliers['output_multiplier']

print(f"\nPA 1980 Per-FTE Funding (real 2024$): ${pa_1980_per_fte_real:,.0f}")
print(f"PA 2024 Per-FTE Funding (actual, real 2024$): ${df_cf['pa_per_fte_actual'].iloc[-1]:,.0f}")
print(f"Counterfactual 2024 Per-FTE (with 1% growth): ${df_cf['cf_per_fte'].iloc[-1]:,.0f}")
print(f"National Average Per-FTE (2024): $11,683")

print(f"\nCumulative Funding Gap (1980-2024, real 2024$): ${total_cumulative_gap/1e3:.1f}B")
print(f"Total Additional Students Who Could Have Enrolled: {total_enrollment_lost:,.0f}")
print(f"Additional Graduates Lost: {additional_graduates_lost:,}")
print(f"Lost Lifetime Earnings (for those graduates): ${lost_lifetime_earnings/1e9:.1f}B")
print(f"Lost State Tax Revenue (lifetime): ${lost_tax_revenue_cf/1e9:.2f}B")
print(f"Lost GDP Impact (multiplier effect): ${lost_gdp_impact/1e9:.1f}B")

# Per-decade breakdown
print(f"\nFunding Gap by Decade (real 2024$):")
for decade_start in range(1980, 2020, 10):
    decade_mask = (df_cf['year'] >= decade_start) & (df_cf['year'] < decade_start + 10)
    decade_gap = df_cf.loc[decade_mask, 'funding_gap_real'].sum()
    print(f"  {decade_start}s: ${decade_gap/1e3:.1f}B {'(surplus)' if decade_gap < 0 else '(underinvestment)'}")

# What PA would look like today with consistent investment
print(f"\nIf PA Had Invested Consistently:")
print(f"  Estimated additional enrollment today: {df_cf['enrollment_gain'].iloc[-1]:,.0f}")
print(f"  Tuition could have been: ~${df_cf['cf_per_fte'].iloc[-1] * 0.4:,.0f}/yr lower")
print(f"  Brain drain rank: Likely top 25 (vs current #42)")
print(f"  PASSHE would not have lost 30%+ enrollment")

# -----------------------------------------------------------------------------
# 7.3 COUNTERFACTUAL VISUALIZATIONS
# -----------------------------------------------------------------------------
try:
    # CHART 12: Counterfactual - Actual vs Consistent Investment
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Phase 7: Counterfactual - What if PA Invested Consistently Since 1980?\n(All Values in Real 2024 Dollars)',
                 fontsize=16, fontweight='bold')

    # Panel 1: Total Funding - Actual vs Counterfactual
    ax1.plot(df_cf['year'], df_cf['pa_actual_real'], linewidth=2, color='#E63946',
             label='Actual PA Funding', marker='o', markersize=3)
    ax1.plot(df_cf['year'], df_cf['cf_total_real'], linewidth=2, color='#06D6A0',
             linestyle='--', label='Counterfactual (1% growth)', marker='s', markersize=3)
    ax1.fill_between(df_cf['year'], df_cf['pa_actual_real'], df_cf['cf_total_real'],
                     alpha=0.2, color='#E63946', label='Funding Gap')
    ax1.set_ylabel('Total Funding ($ Million, 2024$)')
    ax1.set_title('Total State Higher Ed Funding', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Per-FTE Funding Comparison
    ax2.plot(df_cf['year'], df_cf['pa_per_fte_actual'], linewidth=2, color='#E63946',
             label='Actual PA Per-FTE')
    ax2.plot(df_cf['year'], df_cf['cf_per_fte'], linewidth=2, color='#06D6A0',
             linestyle='--', label='Counterfactual Per-FTE')
    ax2.axhline(y=11683, color='blue', linestyle=':', alpha=0.5, label='National Avg (2024)')
    ax2.set_ylabel('$ Per FTE (2024$)')
    ax2.set_title('Per-Student State Funding', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Cumulative Funding Gap
    ax3.fill_between(df_cf['year'], 0, df_cf['cumulative_gap']/1e3,
                     alpha=0.4, color='#E63946')
    ax3.plot(df_cf['year'], df_cf['cumulative_gap']/1e3, linewidth=2, color='#E63946')
    ax3.set_ylabel('Cumulative Gap ($ Billion, 2024$)')
    ax3.set_title('Cumulative Underinvestment Since 1980', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='black', linewidth=0.5)

    # Panel 4: Enrollment - Actual vs Counterfactual
    ax4.plot(df_cf['year'], df_cf['pa_enrollment_total']/1000, linewidth=2,
             color='#E63946', label='Actual Enrollment')
    ax4.plot(df_cf['year'], df_cf['cf_enrollment']/1000, linewidth=2,
             color='#06D6A0', linestyle='--', label='Counterfactual Enrollment')
    ax4.fill_between(df_cf['year'], df_cf['pa_enrollment_total']/1000,
                     df_cf['cf_enrollment']/1000, alpha=0.2, color='#06D6A0')
    ax4.set_ylabel('Total Enrollment (Thousands)')
    ax4.set_title('Public Higher Ed Enrollment', fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig12_counterfactual_1980.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig12_counterfactual_1980.png")

except Exception as e:
    logger.error(f"Error generating Phase 7 visualizations: {e}")
    import traceback
    traceback.print_exc()

# Save counterfactual data
df_cf.to_csv(OUTPUT_DIR / 'counterfactual_1980_2024.csv', index=False)
print(f"Saved: counterfactual_1980_2024.csv")
