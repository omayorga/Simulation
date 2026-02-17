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

fpl_single = 15650
fpl_family_of_4 = 32150

data = {
    'Black Men':    {'avg_income': 54028},
    'Black Women':  {'avg_income': 48984},
    'White Men':    {'avg_income': 70408},
    'White Women':  {'avg_income': 57616},
    'Latinx Men':   {'avg_income': 52156},
    'Latinx Women': {'avg_income': 46228},
}

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

employment_rates = {
    'Black Men':    [0.60, 0.75, 0.85, 0.93],
    'Black Women':  [0.62, 0.77, 0.87, 0.93],
    'White Men':    [0.72, 0.85, 0.93, 0.96],
    'White Women':  [0.73, 0.86, 0.94, 0.97],
    'Latinx Men':   [0.65, 0.80, 0.90, 0.95],
    'Latinx Women': [0.63, 0.78, 0.88, 0.95],
}

employment_rates_by_race = {
    'Black':    [0.61, 0.76, 0.86, 0.93],
    'White':    [0.725, 0.855, 0.935, 0.965],
    'Hispanic': [0.64, 0.79, 0.89, 0.95],
}

income_brackets = ['Lower 25%', 'Median 50%', 'Upper 25%']
income_factors = [0.75, 1.0, 1.25]

num_individuals = 1_000_000

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

# Save each race as separate figure
for race in races:
    fig2, ax = plt.subplots(1, 1, figsize=(12, 7))
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
                    f'${height:,.0f}', ha='center', va='bottom', fontsize=8)

    base_inc = family_income_by_race[race]
    ax.set_title(
        f'Family of 4 — {race} Household\nMedian HH Income: ${base_inc:,}',
        fontsize=13, fontweight='bold'
    )
    ax.set_xticks(x)
    ax.set_xticklabels(tier_names)
    ax.set_ylabel('Average Simulated Wealth ($)')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig2_family_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


# =============================================================================
# PART 3: CROSS-RACIAL COMPARISON CHARTS (SPLIT BY RACE)
# =============================================================================
print("\nGenerating Part 3: Cross-racial comparison charts (split by race)...")

race_colors = {'Black': '#E74C3C', 'White': '#3498DB', 'Hispanic': '#2ECC71'}
plan_names_short = [p.replace('_', ' ') for p in idr_plans.keys()]

# Figure 3: Annual IDR Payment Burden - BY RACE
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    
    for ax, (tier_name, tier_factor) in zip(axes, family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        
        payments = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            payments.append(annual_payment)
        
        bars = ax.bar(x, payments, color=race_colors[race], edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'${h:,.0f}', ha='center', va='bottom', fontsize=8)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 100,
                        '$0', ha='center', va='bottom', fontsize=8, color='gray')
        
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=9, rotation=15, ha='right')
        ax.set_ylabel('Annual IDR Payment ($)' if ax == axes[0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{race} Family of 4 — Annual IDR Payment Burden',
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig3_idr_payment_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 4: Post-IDR Disposable Income - BY RACE
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    
    for ax, (tier_name, tier_factor) in zip(axes, family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        
        disposable = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            disposable.append(annual_income - annual_payment)
        
        bars = ax.bar(x, disposable, color=race_colors[race], edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h,
                    f'${h:,.0f}', ha='center', va='bottom', fontsize=8)
        
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=9, rotation=15, ha='right')
        ax.set_ylabel('Post-IDR Disposable Income ($)' if ax == axes[0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{race} Family of 4 — Post-IDR Disposable Income',
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig4_disposable_income_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 5: Monthly Payment & % of Income - BY RACE
for race in races:
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharey='row')
    
    # Row 1: Monthly payment in dollars
    for ax, (tier_name, tier_factor) in zip(axes[0], family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        
        monthly_payments = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            monthly = (disc_income * settings['repayment_rate']) / 12
            monthly_payments.append(monthly)
        
        bars = ax.bar(x, monthly_payments, color=race_colors[race], edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'${h:,.0f}', ha='center', va='bottom', fontsize=8)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 5,
                        '$0', ha='center', va='bottom', fontsize=8, color='gray')
        
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=15, ha='right')
        ax.set_ylabel('Monthly Payment ($)' if ax == axes[0][0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    # Row 2: Payment as % of income
    for ax, (tier_name, tier_factor) in zip(axes[1], family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        
        pct_of_income = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            pct = (annual_payment / annual_income) * 100 if annual_income > 0 else 0
            pct_of_income.append(pct)
        
        bars = ax.bar(x, pct_of_income, color=race_colors[race], edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h,
                        f'{h:.1f}%', ha='center', va='bottom', fontsize=8)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 0.2,
                        '0%', ha='center', va='bottom', fontsize=8, color='gray')
        
        ax.set_title(f'{tier_name}', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=15, ha='right')
        ax.set_ylabel('% of Gross Income' if ax == axes[1][0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{race} Family of 4 — Monthly Payment (Top) & % of Income (Bottom)',
        fontsize=13, fontweight='bold', y=0.995
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig5_monthly_payment_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 6: Wealth Generation - BY RACE
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    
    for ax, tier_name in zip(axes, tier_names):
        x = np.arange(len(idr_plans))
        means = [np.mean(family_results[plan_name][race][tier_name])
                 for plan_name in idr_plans]
        
        bars = ax.bar(x, means, color=race_colors[race], edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h,
                    f'${h:,.0f}', ha='center', va='bottom', fontsize=8)
        
        ax.set_title(f'{tier_name}', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=9, rotation=15, ha='right')
        ax.set_ylabel('Simulated Wealth ($)' if ax == axes[0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{race} Family of 4 — Simulated Wealth by IDR Plan',
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig6_wealth_generation_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 7: Racial Wealth Gap (Black and Hispanic vs White) - BY MINORITY RACE
for minority_race, color in [('Black', '#E74C3C'), ('Hispanic', '#2ECC71')]:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    
    for ax, tier_name in zip(axes, tier_names):
        x = np.arange(len(idr_plans))
        
        white_means = [np.mean(family_results[plan_name]['White'][tier_name])
                       for plan_name in idr_plans]
        race_means = [np.mean(family_results[plan_name][minority_race][tier_name])
                      for plan_name in idr_plans]
        gap_pct = [(r / w - 1) * 100 for r, w in zip(race_means, white_means)]
        
        bars = ax.bar(x, gap_pct, color=color, edgecolor='white', linewidth=0.8)
        
        for bar in bars:
            h = bar.get_height()
            va = 'top' if h < 0 else 'bottom'
            offset = -1.0 if h < 0 else 0.5
            ax.text(bar.get_x() + bar.get_width()/2, h + offset,
                    f'{h:.1f}%', ha='center', va=va, fontsize=9, fontweight='bold')
        
        ax.axhline(y=0, color='#333333', linestyle='-', linewidth=1.5)
        ax.set_title(f'{tier_name}', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=9, rotation=15, ha='right')
        ax.set_ylabel('Wealth Gap vs White (%)' if ax == axes[0] else '')
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{minority_race} vs White — Wealth Gap by IDR Plan\n'
        f'(Negative % = {minority_race} family accumulates less wealth than White family)',
        fontsize=13, fontweight='bold', y=1.05
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig7_wealth_gap_{minority_race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

print("\n" + "="*80)
print("ALL CHARTS SAVED SUCCESSFULLY!")
print("="*80)
print(f"Location: {output_dir}")
print("\nGenerated files (17 total):")
print("\nPart 1 - Individual Scenarios:")
print("  1. fig1_individual_scenarios.png")
print("\nPart 2 - Family of 4 by Race (3 files):")
print("  2. fig2_family_black.png")
print("  3. fig2_family_white.png")
print("  4. fig2_family_hispanic.png")
print("\nPart 3 - Cross-Racial Comparisons (13 files):")
print("  Figure 3 - IDR Payment Burden (3):")
print("    5. fig3_idr_payment_black.png")
print("    6. fig3_idr_payment_white.png")
print("    7. fig3_idr_payment_hispanic.png")
print("  Figure 4 - Disposable Income (3):")
print("    8. fig4_disposable_income_black.png")
print("    9. fig4_disposable_income_white.png")
print("   10. fig4_disposable_income_hispanic.png")
print("  Figure 5 - Monthly Payment & % (3):")
print("   11. fig5_monthly_payment_black.png")
print("   12. fig5_monthly_payment_white.png")
print("   13. fig5_monthly_payment_hispanic.png")
print("  Figure 6 - Wealth Generation (3):")
print("   14. fig6_wealth_generation_black.png")
print("   15. fig6_wealth_generation_white.png")
print("   16. fig6_wealth_generation_hispanic.png")
print("  Figure 7 - Racial Wealth Gap (2):")
print("   17. fig7_wealth_gap_black.png")
print("   18. fig7_wealth_gap_hispanic.png")
print("="*80)
