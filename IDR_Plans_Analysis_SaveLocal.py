import numpy as np
import matplotlib.pyplot as plt
import os

# =============================================================================
# OUTPUT DIRECTORY CONFIGURATION
# =============================================================================
# Change this path to wherever you want to save the charts
output_dir = r"C:\Users\Oscar\Dropbox\Downloads"

# Create directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

print(f"\nAll charts will be saved to: {output_dir}\n")

# =============================================================================
# IDR Plans Wealth Simulation — Updated with Real-World Data
# =============================================================================
# All variables below are sourced from publicly available federal data.
# Citations are provided inline with each variable block.
# =============================================================================


# #############################################################################
# PART 1: INDIVIDUAL SCENARIOS (Original, Updated)
# #############################################################################

# -----------------------------------------------------------------------------
# Federal Poverty Line (FPL) — 48 Contiguous States
# -----------------------------------------------------------------------------
# Source: U.S. Department of Health & Human Services (HHS), 2025 Poverty Guidelines
#         https://aspe.hhs.gov/sites/default/files/documents/
#         dd73d4f00d8a819d10b2fdb70d254f7b/detailed-guidelines-2025.pdf
#
# Single individual 100% FPL = $15,650
# Family of 4        100% FPL = $32,150
fpl_single = 15650
fpl_family_of_4 = 32150

# IDR plans use different FPL multipliers to define "discretionary income":
#   Most plans (IBR, ICR, PAYE): AGI − 150% FPL
#   SAVE plan:                   AGI − 225% FPL
#   ICR:                         AGI − 100% FPL

# -----------------------------------------------------------------------------
# Average Income by Race & Gender (Annual, Full-Time Workers)
# -----------------------------------------------------------------------------
# Source: U.S. Bureau of Labor Statistics (BLS)
#         "Usual Weekly Earnings of Wage and Salary Workers — 2025"
#         Table 7: Median usual weekly earnings, 2025 annual averages
#         https://www.bls.gov/news.release/pdf/wkyeng.pdf
#         (Published January 27, 2026; 2025 figures are 11-month averages
#          excluding October due to federal government shutdown)
#
# Calculation: Median weekly earnings × 52 weeks
#   Black Men:   $1,039/wk × 52 = $54,028
#   Black Women: $942/wk × 52   = $48,984
#   White Men:   $1,354/wk × 52 = $70,408
#   White Women: $1,108/wk × 52 = $57,616
#   Latinx Men:  $1,003/wk × 52 = $52,156
#   Latinx Women:$889/wk × 52   = $46,228
data = {
    'Black Men':    {'avg_income': 54028},
    'Black Women':  {'avg_income': 48984},
    'White Men':    {'avg_income': 70408},
    'White Women':  {'avg_income': 57616},
    'Latinx Men':   {'avg_income': 52156},
    'Latinx Women': {'avg_income': 46228},
}

# -----------------------------------------------------------------------------
# Homeownership Rate by Race
# -----------------------------------------------------------------------------
# Source: U.S. Census Bureau, Housing Vacancies and Homeownership Survey
#         (CPS/HVS), Q2 2025
#         https://fred.stlouisfed.org/series/BOAAAHORUSQ156N
#         Redfin analysis of Census data, February 2026:
#         https://www.redfin.com/news/homeownership-rate-by-race-2025/
#
#   Black households:             ~43.9%
#   White non-Hispanic households: ~74.0%
#   Hispanic households:           ~48.8%
home_purchase_rates = {
    'Black Men':    0.439,
    'Black Women':  0.439,
    'White Men':    0.740,
    'White Women':  0.740,
    'Latinx Men':   0.488,
    'Latinx Women': 0.488,
}

home_purchase_rates_by_race = {
    'Black':    0.439,
    'White':    0.740,
    'Hispanic': 0.488,
}

# -----------------------------------------------------------------------------
# Employment Rate Progression by Race & Gender (4 Career Stages)
# -----------------------------------------------------------------------------
# Base (final-stage) rates derived from BLS Employment Situation Summary, 2025
#   Table A-2 (Employment status by race) & Table A-3 (by Hispanic ethnicity)
#   https://www.bls.gov/news.release/empsit.t02.htm
#
# 2025 annual average unemployment rates (approx.):
#   Black men: ~7.1%  → final employment rate ~0.93
#   Black women: ~6.7% → ~0.93
#   White men: ~3.7%  → ~0.96
#   White women: ~3.2% → ~0.97
#   Hispanic men: ~5.0% → ~0.95
#   Hispanic women: ~5.3% → ~0.95
#
# Early career stages use lower rates to reflect higher youth unemployment
# and labor force entry barriers. Progression models career-stage improvement.
employment_rates = {
    'Black Men':    [0.60, 0.75, 0.85, 0.93],
    'Black Women':  [0.62, 0.77, 0.87, 0.93],
    'White Men':    [0.72, 0.85, 0.93, 0.96],
    'White Women':  [0.73, 0.86, 0.94, 0.97],
    'Latinx Men':   [0.65, 0.80, 0.90, 0.95],
    'Latinx Women': [0.63, 0.78, 0.88, 0.95],
}

# For family scenarios, use blended (average of men/women) employment rates
# by race, since the household has a primary earner of either gender.
employment_rates_by_race = {
    'Black':    [0.61, 0.76, 0.86, 0.93],
    'White':    [0.725, 0.855, 0.935, 0.965],
    'Hispanic': [0.64, 0.79, 0.89, 0.95],
}

income_brackets = ['Lower 25%', 'Median 50%', 'Upper 25%']
income_factors = [0.75, 1.0, 1.25]

num_individuals = 1_000_000

# -----------------------------------------------------------------------------
# IDR Plan Parameters
# -----------------------------------------------------------------------------
idr_plans = {
    'IBR_2014':        {'repayment_rate': 0.10, 'years': 20, 'fpl_multiplier': 1.50},
    'IBR_pre2014':     {'repayment_rate': 0.15, 'years': 25, 'fpl_multiplier': 1.50},
    'ICR':             {'repayment_rate': 0.20, 'years': 25, 'fpl_multiplier': 1.00},
    'PAYE':            {'repayment_rate': 0.10, 'years': 20, 'fpl_multiplier': 1.50},
    'SAVE_undergrad':  {'repayment_rate': 0.05, 'years': 20, 'fpl_multiplier': 2.25},
    'SAVE_grad':       {'repayment_rate': 0.10, 'years': 25, 'fpl_multiplier': 2.25},
}

home_appreciation_rate = 0.03
retirement_investment_rate = 0.10
personal_asset_growth_rate = 0.02
salary_growth_factors = [1.0, 1.2, 1.5, 1.8]


# =============================================================================
# Simulation Function
# =============================================================================
def simulate_wealth_with_idr(avg_income, factor, idr_settings,
                              home_rate, emp_rates, fpl_base):
    adjusted_income = avg_income * factor
    initial_wealth = adjusted_income * np.random.uniform(0.5, 1.5, num_individuals)
    wealth = initial_wealth.copy()

    repayment_rate = idr_settings['repayment_rate']
    repayment_years = idr_settings['years']
    fpl_threshold = fpl_base * idr_settings['fpl_multiplier']

    salary_growth = [adjusted_income * x for x in salary_growth_factors]

    for i, (rate, salary) in enumerate(zip(emp_rates, salary_growth)):
        employed = np.random.rand(num_individuals) < rate
        income = employed * salary

        if i < repayment_years:
            discretionary_income = np.maximum(income - fpl_threshold, 0)
            idr_payment = discretionary_income * repayment_rate
        else:
            idr_payment = 0

        home_wealth = home_rate * income * home_appreciation_rate
        retirement_savings = income * retirement_investment_rate
        asset_growth = wealth * personal_asset_growth_rate

        wealth += income + home_wealth + retirement_savings + asset_growth - idr_payment

    return wealth


# =============================================================================
# PART 1: Run Individual Simulations
# =============================================================================
print("Running Part 1: Individual scenarios...")
results_by_plan = {}
for plan_name, settings in idr_plans.items():
    results_by_plan[plan_name] = {}
    for category, group_data in data.items():
        results_by_plan[plan_name][category] = {}
        for bracket, factor in zip(income_brackets, income_factors):
            results_by_plan[plan_name][category][bracket] = simulate_wealth_with_idr(
                group_data['avg_income'], factor, settings,
                home_purchase_rates[category],
                employment_rates[category],
                fpl_single
            )

fig, axes = plt.subplots(len(data), 1, figsize=(16, 36))
plan_colors = ['#FFA07A', '#20B2AA', '#9370DB', '#FFD700', '#708090', '#90EE90']

for idx, (category, ax) in enumerate(zip(data.keys(), axes)):
    x = np.arange(len(income_brackets))
    width = 0.12

    for i, (plan_name, color) in enumerate(zip(idr_plans.keys(), plan_colors)):
        means = [np.mean(results_by_plan[plan_name][category][bracket])
                 for bracket in income_brackets]
        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:,.0f}', ha='center', va='bottom', fontsize=7)

    ax.set_title(f'Average Wealth by Income Bracket for {category}', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(income_brackets)
    ax.set_ylabel('Average Wealth ($)')
    ax.legend()

plt.tight_layout()
save_path = os.path.join(output_dir, 'fig1_individual_scenarios.png')
plt.savefig(save_path, dpi=150)
print(f"Saved: {save_path}")
plt.close()


# =============================================================================
# PART 2: FAMILY OF 4 SCENARIOS
# =============================================================================
family_income_by_race = {
    'Black':    55718,
    'White':    86178,
    'Hispanic': 70950,
}

family_income_tiers = {
    'Median':             1.00,
    '25% Above Median':   1.25,
    '50% Above Median':   1.50,
}

print("\nRunning Part 2: Family of 4 scenarios...")
family_results = {}
for plan_name, settings in idr_plans.items():
    family_results[plan_name] = {}
    for race, base_income in family_income_by_race.items():
        family_results[plan_name][race] = {}
        for tier_name, factor in family_income_tiers.items():
            family_results[plan_name][race][tier_name] = simulate_wealth_with_idr(
                base_income, factor, settings,
                home_purchase_rates_by_race[race],
                employment_rates_by_race[race],
                fpl_family_of_4
            )

races = list(family_income_by_race.keys())
tier_names = list(family_income_tiers.keys())

fig2, axes2 = plt.subplots(len(races), 1, figsize=(18, 24))

for ax, race in zip(axes2, races):
    x = np.arange(len(tier_names))
    width = 0.12

    for i, (plan_name, color) in enumerate(zip(idr_plans.keys(), plan_colors)):
        means = [np.mean(family_results[plan_name][race][tier])
                 for tier in tier_names]
        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'${height:,.0f}', ha='center', va='bottom', fontsize=7)

    base_inc = family_income_by_race[race]
    ax.set_title(
        f'Family of 4 — {race} Household (Median HH Income: ${base_inc:,})',
        fontsize=14
    )
    ax.set_xticks(x)
    ax.set_xticklabels(tier_names)
    ax.set_ylabel('Average Simulated Wealth ($)')
    ax.legend(fontsize=8)

plt.suptitle(
    'Wealth Accumulation Under IDR Plans — Family of 4 by Race & Income Tier\n'
    '(FPL Family of 4 = $32,150 | Sources: Census 2024, HHS 2025, BLS 2025)',
    fontsize=16, y=1.02
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig2_family_of_4_scenarios.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()


# =============================================================================
# PART 3: CROSS-RACIAL COMPARISON CHARTS
# =============================================================================
print("\nGenerating Part 3: Cross-racial comparison charts...")

race_colors = {'Black': '#E74C3C', 'White': '#3498DB', 'Hispanic': '#2ECC71'}
plan_names_short = [p.replace('_', '\n') for p in idr_plans.keys()]

# Figure 3: Annual IDR Payment Burden
fig3, axes3 = plt.subplots(1, 3, figsize=(26, 8), sharey=True)

for ax, (tier_name, tier_factor) in zip(axes3, family_income_tiers.items()):
    x = np.arange(len(idr_plans))
    width = 0.25

    for j, (race, color) in enumerate(race_colors.items()):
        annual_income = family_income_by_race[race] * tier_factor
        payments = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            payments.append(annual_payment)

        bars = ax.bar(x + (j - 1) * width, payments, width,
                      label=f"{race} (${annual_income:,.0f})",
                      color=color, edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'${h:,.0f}', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 50,
                        '$0', ha='center', va='bottom', fontsize=7, color='gray')

    ax.set_title(f'{tier_name}', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('Annual IDR Payment ($)' if ax == axes3[0] else '')
    ax.legend(fontsize=8, title='Race (HH Income)', title_fontsize=8)
    ax.grid(axis='y', alpha=0.3)

fig3.suptitle(
    'SHORT-TERM IMPACT: Annual IDR Payment by Race — Family of 4\n'
    '(Higher bars = more income diverted to student loan repayment each year)',
    fontsize=14, y=1.05
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig3_idr_payment_burden_by_race.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()

# Figure 4: Post-IDR Disposable Income
fig4, axes4 = plt.subplots(1, 3, figsize=(26, 8), sharey=True)

for ax, (tier_name, tier_factor) in zip(axes4, family_income_tiers.items()):
    x = np.arange(len(idr_plans))
    width = 0.25

    for j, (race, color) in enumerate(race_colors.items()):
        annual_income = family_income_by_race[race] * tier_factor
        disposable = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            disposable.append(annual_income - annual_payment)

        bars = ax.bar(x + (j - 1) * width, disposable, width,
                      label=f"{race} (${annual_income:,.0f})",
                      color=color, edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h,
                    f'${h:,.0f}', ha='center', va='bottom', fontsize=7)

    ax.set_title(f'{tier_name}', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('Post-IDR Disposable Income ($)' if ax == axes4[0] else '')
    ax.legend(fontsize=8, title='Race (HH Income)', title_fontsize=8)
    ax.grid(axis='y', alpha=0.3)

fig4.suptitle(
    'SHORT-TERM IMPACT: Post-IDR Disposable Income by Race — Family of 4\n'
    '(Higher bars = more income available for living expenses & wealth building)',
    fontsize=14, y=1.04
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig4_post_idr_disposable_income.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()

# Figure 5: Monthly Payment & % of Income
fig5, axes5 = plt.subplots(2, 3, figsize=(26, 14), sharey='row')

for ax, (tier_name, tier_factor) in zip(axes5[0], family_income_tiers.items()):
    x = np.arange(len(idr_plans))
    width = 0.25

    for j, (race, color) in enumerate(race_colors.items()):
        annual_income = family_income_by_race[race] * tier_factor
        monthly_payments = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            monthly = (disc_income * settings['repayment_rate']) / 12
            monthly_payments.append(monthly)

        bars = ax.bar(x + (j - 1) * width, monthly_payments, width,
                      label=race, color=color, edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'${h:,.0f}', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 2,
                        '$0', ha='center', va='bottom', fontsize=7, color='gray')

    ax.set_title(f'{tier_name}', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('Monthly IDR Payment ($)' if ax == axes5[0][0] else '')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

for ax, (tier_name, tier_factor) in zip(axes5[1], family_income_tiers.items()):
    x = np.arange(len(idr_plans))
    width = 0.25

    for j, (race, color) in enumerate(race_colors.items()):
        annual_income = family_income_by_race[race] * tier_factor
        pct_of_income = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            pct = (annual_payment / annual_income) * 100 if annual_income > 0 else 0
            pct_of_income.append(pct)

        bars = ax.bar(x + (j - 1) * width, pct_of_income, width,
                      label=race, color=color, edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'{h:.1f}%', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 0.1,
                        '0%', ha='center', va='bottom', fontsize=7, color='gray')

    ax.set_title(f'{tier_name}', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('IDR Payment as % of Gross Income' if ax == axes5[1][0] else '')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

fig5.suptitle(
    'SHORT-TERM: Monthly IDR Payment & Income Share by Race — Family of 4',
    fontsize=14, y=1.02
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig5_monthly_payment_and_pct.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()

# Figure 6: Wealth Generation
fig6, axes6 = plt.subplots(1, 3, figsize=(26, 8), sharey=True)

for ax, tier_name in zip(axes6, tier_names):
    x = np.arange(len(idr_plans))
    width = 0.25

    for j, (race, color) in enumerate(race_colors.items()):
        means = [np.mean(family_results[plan_name][race][tier_name])
                 for plan_name in idr_plans]
        bars = ax.bar(x + (j - 1) * width, means, width,
                      label=race, color=color, edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h,
                    f'${h:,.0f}', ha='center', va='bottom', fontsize=7)

    ax.set_title(f'{tier_name}', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('Mean Simulated Wealth ($)' if ax == axes6[0] else '')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

fig6.suptitle(
    'WEALTH GENERATION: Simulated Wealth by Race Under Each IDR Plan — Family of 4',
    fontsize=14, y=1.04
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig6_wealth_generation_by_race.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()

# Figure 7: Racial Wealth Gap
fig7, axes7 = plt.subplots(1, 3, figsize=(26, 8), sharey=True)

for ax, tier_name in zip(axes7, tier_names):
    x = np.arange(len(idr_plans))
    width = 0.35

    white_means = [np.mean(family_results[plan_name]['White'][tier_name])
                   for plan_name in idr_plans]

    for j, (race, color) in enumerate([('Black', '#E74C3C'), ('Hispanic', '#2ECC71')]):
        race_means = [np.mean(family_results[plan_name][race][tier_name])
                      for plan_name in idr_plans]
        gap_pct = [(r / w - 1) * 100 for r, w in zip(race_means, white_means)]

        bars = ax.bar(x + (j - 0.5) * width, gap_pct, width,
                      label=f'{race} vs White', color=color,
                      edgecolor='white', linewidth=0.5)

        for bar in bars:
            h = bar.get_height()
            va = 'top' if h < 0 else 'bottom'
            offset = -0.8 if h < 0 else 0.3
            ax.text(bar.get_x() + bar.get_width()/2, h + offset,
                    f'{h:.1f}%', ha='center', va=va, fontsize=8,
                    fontweight='bold')

    ax.axhline(y=0, color='#333333', linestyle='-', linewidth=1.0)
    ax.set_title(f'{tier_name}', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(plan_names_short, fontsize=8)
    ax.set_ylabel('Wealth Gap vs White Households (%)' if ax == axes7[0] else '')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

fig7.suptitle(
    'RACIAL WEALTH GAP: Black & Hispanic vs. White Households Under IDR Plans\n'
    '(Negative % = less accumulated wealth than White family at the SAME income tier)',
    fontsize=14, y=1.07
)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig7_racial_wealth_gap.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()

print("\n" + "="*80)
print("ALL CHARTS SAVED SUCCESSFULLY!")
print("="*80)
print(f"Location: {output_dir}")
print("\nGenerated files:")
print("  1. fig1_individual_scenarios.png")
print("  2. fig2_family_of_4_scenarios.png")
print("  3. fig3_idr_payment_burden_by_race.png")
print("  4. fig4_post_idr_disposable_income.png")
print("  5. fig5_monthly_payment_and_pct.png")
print("  6. fig6_wealth_generation_by_race.png")
print("  7. fig7_racial_wealth_gap.png")
print("="*80)
