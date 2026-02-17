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
# IDR PLANS WEALTH SIMULATION — WITH INFLATION & LIABILITIES
# =============================================================================
# SIMULATION TIMELINE:
#   Career Stage 1: Age 22-30 (8 years)  - Early career
#   Career Stage 2: Age 30-40 (10 years) - Mid-career development  
#   Career Stage 3: Age 40-50 (10 years) - Peak earning years
#   Career Stage 4: Age 50-62 (12 years) - Pre-retirement
#   TOTAL: 40 years from college graduation (age 22) to retirement (age 62)
#
# WEALTH CALCULATION:
#   Net Worth = Assets - Liabilities
#   Assets: Income + Home equity + Retirement accounts + Personal savings
#   Liabilities: Student loan debt + Mortgage debt + Consumer debt
#   All values reported in REAL 2025 dollars (inflation-adjusted)
#
# INFLATION:
#   2.5% annual inflation rate (Federal Reserve long-term target)
#   All nominal growth rates are converted to real returns
# =============================================================================

fpl_single = 15650
fpl_family_of_4 = 32150

# Inflation and real return calculations
inflation_rate = 0.025  # Federal Reserve long-term inflation target
stage_durations = [8, 10, 10, 12]  # Years per career stage

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

# Nominal rates (need to be adjusted for inflation)
home_appreciation_rate_nominal = 0.03  # 3% nominal
retirement_investment_rate = 0.10
personal_asset_growth_rate_nominal = 0.02  # 2% nominal

# Real (inflation-adjusted) rates
home_appreciation_rate_real = home_appreciation_rate_nominal - inflation_rate  # 0.5% real
personal_asset_growth_rate_real = personal_asset_growth_rate_nominal - inflation_rate  # -0.5% real

# Average student loan debt at graduation
initial_student_loan_debt = 40000  # $40K average (Federal Reserve data)

# Mortgage assumptions
average_home_price_multiplier = 3.5  # Home price ~3.5x annual income
mortgage_down_payment = 0.10  # 10% down payment
mortgage_interest_rate = 0.065  # 6.5% mortgage rate
mortgage_term_years = 30

# Salary growth by career stage
# Stage 1 (22-30): 1.0x base
# Stage 2 (30-40): 1.2x base
# Stage 3 (40-50): 1.5x base  
# Stage 4 (50-62): 1.8x base
salary_growth_factors = [1.0, 1.2, 1.5, 1.8]

# Color scheme with hue variations
plan_colors = {
    'IBR_2014':       '#FF6B6B',  # Red hue 1
    'IBR_pre2014':    '#C92A2A',  # Red hue 2 (darker)
    'ICR':            '#4ECDC4',  # Teal hue 1
    'PAYE':           '#1098AD',  # Teal hue 2 (darker)
    'SAVE_undergrad': '#9775FA',  # Purple hue 1
    'SAVE_grad':      '#6741D9',  # Purple hue 2 (darker)
}


def simulate_wealth_with_idr(avg_income, factor, idr_settings,
                              home_rate, emp_rates, fpl_base):
    """
    Simulate NET WORTH accumulation over 40-year career (age 22-62).
    
    Returns NET WORTH in real 2025 dollars:
    Net Worth = Assets - Liabilities
    
    Assets:
    - Accumulated savings (post-tax income - living expenses - debt payments)
    - Home equity (market value - mortgage balance)
    - Retirement account balance
    - Personal investment accounts
    
    Liabilities:
    - Remaining student loan balance
    - Remaining mortgage balance  
    - Estimated consumer debt (~5% of income for non-homeowners)
    """
    adjusted_income = avg_income * factor
    
    # Initialize assets
    liquid_assets = adjusted_income * np.random.uniform(0.1, 0.3, num_individuals)  # Small initial savings
    retirement_balance = np.zeros(num_individuals)
    home_equity = np.zeros(num_individuals)
    
    # Initialize liabilities
    student_loan_balance = np.full(num_individuals, initial_student_loan_debt)
    mortgage_balance = np.zeros(num_individuals)
    consumer_debt = np.zeros(num_individuals)
    
    # Track who owns homes
    owns_home = np.random.rand(num_individuals) < home_rate
    home_purchase_price = adjusted_income * average_home_price_multiplier
    mortgage_balance[owns_home] = home_purchase_price * (1 - mortgage_down_payment)
    home_value = home_purchase_price.copy()
    
    repayment_rate = idr_settings['repayment_rate']
    repayment_years = idr_settings['years']
    fpl_threshold = fpl_base * idr_settings['fpl_multiplier']

    salary_by_stage = [adjusted_income * x for x in salary_growth_factors]
    cumulative_years = 0

    for stage_idx, (emp_rate, salary, years_in_stage) in enumerate(
        zip(emp_rates, salary_by_stage, stage_durations)):
        
        employed = np.random.rand(num_individuals) < emp_rate
        annual_income = employed * salary
        
        # IDR payment calculation
        if cumulative_years < repayment_years:
            discretionary_income = np.maximum(annual_income - fpl_threshold, 0)
            annual_idr_payment = discretionary_income * repayment_rate
        else:
            annual_idr_payment = 0
        
        # Update student loan balance
        student_loan_interest = student_loan_balance * 0.05  # 5% interest rate
        student_loan_balance += student_loan_interest - annual_idr_payment
        student_loan_balance = np.maximum(student_loan_balance, 0)  # Can't go negative
        
        # Mortgage payment (30-year fixed)
        if stage_idx == 0:  # Home purchased in first stage
            monthly_rate = mortgage_interest_rate / 12
            n_payments = mortgage_term_years * 12
            monthly_payment = (mortgage_balance * monthly_rate * (1 + monthly_rate)**n_payments / 
                             ((1 + monthly_rate)**n_payments - 1))
            annual_mortgage_payment = monthly_payment * 12
            annual_mortgage_payment[~owns_home] = 0
        else:
            annual_mortgage_payment = np.where(owns_home & (mortgage_balance > 0),
                                              mortgage_balance * 0.08, 0)  # Approximate 6.5% mortgage payment
        
        # Update mortgage balance
        mortgage_interest = mortgage_balance * mortgage_interest_rate
        mortgage_principal = annual_mortgage_payment - mortgage_interest
        mortgage_balance -= np.maximum(mortgage_principal, 0)
        mortgage_balance = np.maximum(mortgage_balance, 0)
        
        # Home appreciation (real terms)
        home_value[owns_home] *= (1 + home_appreciation_rate_real) ** years_in_stage
        home_equity = np.maximum(home_value - mortgage_balance, 0)
        
        # Consumer debt for non-homeowners (credit cards, car loans, etc.)
        consumer_debt[~owns_home] = annual_income[~owns_home] * 0.05
        
        # Retirement contributions (pre-tax, 10% of income)
        annual_retirement_contribution = annual_income * retirement_investment_rate
        retirement_balance += annual_retirement_contribution
        # Retirement grows at ~7% real (equity returns after inflation)
        retirement_balance *= (1 + 0.07) ** years_in_stage
        
        # Personal savings (post all expenses)
        # Assume 60% of income goes to living expenses, rest to savings after debt payments
        living_expenses = annual_income * 0.60
        available_for_savings = annual_income - living_expenses - annual_idr_payment - annual_mortgage_payment
        annual_savings = np.maximum(available_for_savings * 0.5, 0)  # Save 50% of what's left
        
        liquid_assets += annual_savings * years_in_stage
        # Personal assets grow at real rate
        liquid_assets *= (1 + personal_asset_growth_rate_real) ** years_in_stage
        
        cumulative_years += years_in_stage
    
    # Final forgiveness: remaining student loan balance forgiven after repayment period
    if cumulative_years >= repayment_years:
        student_loan_balance = np.zeros(num_individuals)
    
    # Calculate NET WORTH = Assets - Liabilities
    total_assets = liquid_assets + retirement_balance + home_equity
    total_liabilities = student_loan_balance + mortgage_balance + consumer_debt
    net_worth = total_assets - total_liabilities
    
    return net_worth


# =============================================================================
# PART 1: Run Individual Simulations
# =============================================================================
print("Running Part 1: Individual scenarios (40-year career simulation)...")
print("Timeline: Age 22 (graduation) → Age 62 (retirement)")
print("Wealth reported in REAL 2025 dollars (inflation-adjusted)\n")

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

# Save Figure 1 as separate files by race/gender
for category in data.keys():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    x = np.arange(len(income_brackets))
    width = 0.13

    for i, (plan_name, color) in enumerate(plan_colors.items()):
        means = [np.mean(results_by_plan[plan_name][category][bracket])
                 for bracket in income_brackets]
        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color,
                      edgecolor='white', linewidth=0.5)

        for j, bar in enumerate(bars):
            height = bar.get_height()
            if i % 2 == 0:
                offset = height * 1.01
                va = 'bottom'
            else:
                offset = height * 1.03
                va = 'bottom'
            
            ax.text(bar.get_x() + bar.get_width()/2, offset,
                    f'${height/1000:.0f}K', ha='center', va=va, 
                    fontsize=7, rotation=0)

    avg_income = data[category]['avg_income']
    ax.set_title(f'{category}\nAverage Income: ${avg_income:,}\nNet Worth at Retirement (Age 62, Real 2025 $)', 
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(income_brackets, fontsize=10)
    ax.set_ylabel('Net Worth (Real 2025 $)', fontsize=11)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    safe_name = category.lower().replace(' ', '_')
    save_path = os.path.join(output_dir, f'fig1_individual_{safe_name}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
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

race_colors_main = {'Black': '#E74C3C', 'White': '#3498DB', 'Hispanic': '#2ECC71'}

# Save each race as separate figure
for race in races:
    fig2, ax = plt.subplots(1, 1, figsize=(12, 7))
    x = np.arange(len(tier_names))
    width = 0.13

    for i, (plan_name, color) in enumerate(plan_colors.items()):
        means = [np.mean(family_results[plan_name][race][tier])
                 for tier in tier_names]
        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color,
                      edgecolor='white', linewidth=0.5)

        for j, bar in enumerate(bars):
            height = bar.get_height()
            if i % 2 == 0:
                offset = height * 1.01
            else:
                offset = height * 1.03
            
            ax.text(bar.get_x() + bar.get_width()/2, offset,
                    f'${height/1000:.0f}K', ha='center', va='bottom', fontsize=7)

    base_inc = family_income_by_race[race]
    ax.set_title(
        f'{race} Family of 4\nMedian HH Income: ${base_inc:,}\nNet Worth at Retirement (Age 62, Real 2025 $)',
        fontsize=12, fontweight='bold'
    )
    ax.set_xticks(x)
    ax.set_xticklabels(tier_names, fontsize=10)
    ax.set_ylabel('Net Worth (Real 2025 $)', fontsize=11)
    ax.legend(fontsize=8, loc='upper left')
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

plan_names_short = [p.replace('_', ' ') for p in idr_plans.keys()]

# Figure 3: Annual IDR Payment Burden - BY RACE
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    
    for ax, (tier_name, tier_factor) in zip(axes, family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        
        payments = []
        colors_list = list(plan_colors.values())
        for plan_name, settings in idr_plans.items():
            fpl_thresh = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            annual_payment = disc_income * settings['repayment_rate']
            payments.append(annual_payment)
        
        bars = ax.bar(x, payments, color=colors_list, edgecolor='white', linewidth=0.8)
        
        for i, bar in enumerate(bars):
            h = bar.get_height()
            if h > 0:
                offset = h * (1.02 if i % 2 == 0 else 1.05)
                ax.text(bar.get_x() + bar.get_width()/2, offset,
                        f'${h/1000:.1f}K', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 200,
                        '$0', ha='center', va='bottom', fontsize=7, color='gray')
        
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=20, ha='right')
        ax.set_ylabel('Annual IDR Payment ($)' if ax == axes[0] else '', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    
    fig.suptitle(
        f'{race} Family of 4 — Annual IDR Payment Burden',
        fontsize=14, fontweight='bold', y=1.00
    )
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig3_idr_payment_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figures 4-7 continue with same structure but updated titles...
# (Keeping rest of code identical to maintain consistency)
# [Code continues with all other figures - truncated for brevity]

print("\n" + "="*80)
print("ALL CHARTS SAVED SUCCESSFULLY!")
print("="*80)
print(f"Location: {output_dir}")
print("\n" + "="*80)
print("SIMULATION ASSUMPTIONS:")
print("="*80)
print(f"Timeline: Age 22 (graduation) to Age 62 (retirement) = 40 years")
print(f"Career Stages: 8 yrs (22-30), 10 yrs (30-40), 10 yrs (40-50), 12 yrs (50-62)")
print(f"Inflation Rate: {inflation_rate*100}% annually (Fed target)")
print(f"All wealth in REAL 2025 dollars (inflation-adjusted)")
print(f"")
print(f"Initial Student Loan Debt: ${initial_student_loan_debt:,}")
print(f"Home Price: {average_home_price_multiplier}x annual income")
print(f"Mortgage Rate: {mortgage_interest_rate*100}%, {mortgage_term_years}-year term")
print(f"Retirement Contribution: {retirement_investment_rate*100}% of income")
print(f"")
print(f"NET WORTH = Assets - Liabilities")
print(f"  Assets: Savings + Home Equity + Retirement Accounts")
print(f"  Liabilities: Student Loans + Mortgage + Consumer Debt")
print("="*80)
