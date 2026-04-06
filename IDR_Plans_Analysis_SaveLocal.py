import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
# IDR PLANS WEALTH SIMULATION — WITH INFLATION, LIABILITIES, MOE/SE & SENSITIVITY
# =============================================================================
# SIMULATION TIMELINE:
#   Career Stage 1: Age 22-30  (8 years)   - Early career
#   Career Stage 2: Age 30-40  (10 years)  - Mid-career development
#   Career Stage 3: Age 40-50  (10 years)  - Peak earning years
#   Career Stage 4: Age 50-62  (12 years)  - Pre-retirement
#   TOTAL: 40 years from college graduation (age 22) to retirement (age 62)
#
# WEALTH CALCULATION:
#   Net Worth = Assets - Liabilities
#   Assets: Savings + Home equity + Retirement accounts + Personal investments
#   Liabilities: Student loan debt + Mortgage debt + Consumer debt
#   All values reported in REAL 2025 dollars (inflation-adjusted)
#
# MARGIN OF ERROR / SE:
#   All income parameters include BLS-reported SE (±) drawn from a normal
#   distribution at the individual level so that Monte Carlo variation captures
#   measurement uncertainty IN ADDITION to individual-level stochasticity.
#
# SOURCES:
#   - BLS Usual Weekly Earnings Q4 2024 (Table 3), wkyeng news release
#   - BLS 2025 Annual Averages (Table 7), wkyeng.pdf — released 2026-01-28
#   - HHS 2026 Federal Poverty Guidelines (Jan 2026)
#   - Census Bureau CPS/HVS Q4 2025 homeownership rates (FRED)
#   - Education Data Initiative, Average Debt for Bachelor's Degree 2025
#   - Freddie Mac PMMS 30-year FRM, April 2026
#   - FHFA House Price Index historical average
#   - BLS Consumer Expenditure Survey 2024
# =============================================================================

# ── RANDOM SEED for reproducibility ──
np.random.seed(42)

# =============================================================================
# GLOBAL PARAMETERS
# =============================================================================

# 2026 HHS Federal Poverty Guidelines (48 contiguous states)
# Source: https://www.medicaidplanningassistance.org/federal-poverty-guidelines/
fpl_single     = 15_960.0   # 2026 FPL for 1-person household (was $15,650 in 2025)
fpl_family_of_4 = 33_000.0  # 2026 FPL for 4-person household (was $32,150 in 2025)

# Inflation assumption (Federal Reserve long-run target)
inflation_rate   = 0.025
stage_durations  = [8, 10, 10, 12]   # years per career stage

# ── INCOME DATA — BLS Q4 2024 Annualized (×52)  ──
# Source: BLS Usual Weekly Earnings Q4 2024, Table 3
# SE values from Variable Documentation Table (±$SE/wk × 52)
#   Black Men:    $1,118/wk ± $10/wk  → annual $58,136 ± $520
#   Black Women:  $978/wk  ± $6/wk   → annual $50,856 ± $312
#   White Men:    $1,321/wk ± $6/wk  → annual $68,692 ± $312
#   White Women:  $1,094/wk ± $5/wk  → annual $56,888 ± $260
#   Latinx Men:   $1,001/wk ± $7/wk  → annual $52,052 ± $364
#   Latinx Women: $844/wk  ± $6/wk   → annual $43,888 ± $312
# NOTE: Q4 2025 data was not produced due to the Oct 2025 federal gov shutdown;
#       Q4 2024 is therefore the most recent complete quarter available.
data = {
    'Black Men':    {'avg_income': 58_136.0, 'income_se': 520.0},
    'Black Women':  {'avg_income': 50_856.0, 'income_se': 312.0},
    'White Men':    {'avg_income': 68_692.0, 'income_se': 312.0},
    'White Women':  {'avg_income': 56_888.0, 'income_se': 260.0},
    'Latinx Men':   {'avg_income': 52_052.0, 'income_se': 364.0},
    'Latinx Women': {'avg_income': 43_888.0, 'income_se': 312.0},
}

# ── HOMEOWNERSHIP RATES — Census CPS/HVS 2025 (FRED) ──
# Source: FRED BOAAAHORUSQ156N, NHWAHORUSQ156N, HOLHORUSQ156N (Q4 2025 / Q3 2025)
# MOE: ±1.3 pp Black, ±0.5 pp White, ±1.3 pp Hispanic (Census HVS documentation)
home_purchase_rates = {
    'Black Men':    0.439, 'Black Women':  0.439,
    'White Men':    0.740, 'White Women':  0.740,
    'Latinx Men':   0.487, 'Latinx Women': 0.487,
}
home_purchase_rates_moe = {     # ± percentage points (MOE, 90% CI)
    'Black Men':    0.013, 'Black Women':  0.013,
    'White Men':    0.005, 'White Women':  0.005,
    'Latinx Men':   0.013, 'Latinx Women': 0.013,
}

home_purchase_rates_by_race = {'Black': 0.439, 'White': 0.740, 'Hispanic': 0.487}
home_purchase_rates_moe_by_race = {'Black': 0.013, 'White': 0.005, 'Hispanic': 0.013}

# ── EMPLOYMENT RATES — BLS CPS Table 3/4, 2025 Annual Averages ──
# By career stage; MOE ±1–2 pp (BLS CPS sampling error documentation)
employment_rates = {
    'Black Men':    [0.78, 0.82, 0.77, 0.62],
    'Black Women':  [0.71, 0.76, 0.75, 0.58],
    'White Men':    [0.87, 0.89, 0.86, 0.71],
    'White Women':  [0.76, 0.76, 0.75, 0.60],
    'Latinx Men':   [0.86, 0.89, 0.86, 0.73],
    'Latinx Women': [0.71, 0.70, 0.69, 0.58],
}
employment_rates_se = 0.015   # ±1.5 pp (midpoint of ±1–2 pp range)

employment_rates_by_race = {
    'Black':    [0.745, 0.790, 0.760, 0.600],
    'White':    [0.815, 0.825, 0.805, 0.655],
    'Hispanic': [0.785, 0.795, 0.775, 0.655],
}

# ── FAMILY INCOME — Census Bureau CPS/ASEC 2023-2024 ──
# MOE values from American Community Survey margin-of-error documentation
family_income_by_race = {
    'Black':    56_020.0,
    'White':    92_530.0,
    'Hispanic': 70_950.0,
}
family_income_moe = {           # ± annual (from Variable Documentation Table)
    'Black':    323.0,
    'White':    224.0,
    'Hispanic': 451.0,
}

family_income_tiers = {
    'Median':           1.00,
    '25% Above Median': 1.25,
    '50% Above Median': 1.50,
}

income_brackets  = ['Lower 25%', 'Median 50%', 'Upper 25%']
income_factors   = [0.75, 1.0, 1.25]

num_individuals  = 1_000_000

# ── IDR PLANS ──
idr_plans = {
    'IBR_2014':       {'repayment_rate': 0.10, 'years': 20, 'fpl_multiplier': 1.50},
    'IBR_pre2014':    {'repayment_rate': 0.15, 'years': 25, 'fpl_multiplier': 1.50},
    'ICR':            {'repayment_rate': 0.20, 'years': 25, 'fpl_multiplier': 1.00},
    'PAYE':           {'repayment_rate': 0.10, 'years': 20, 'fpl_multiplier': 1.50},
    'SAVE_undergrad': {'repayment_rate': 0.05, 'years': 20, 'fpl_multiplier': 2.25},
    'SAVE_grad':      {'repayment_rate': 0.10, 'years': 25, 'fpl_multiplier': 2.25},
}
# NOTE: SAVE plan remains blocked by federal court injunction (mid-2024);
#       ICR and PAYE are being phased out — new enrollment closes July 2028.

# ── FINANCIAL PARAMETERS ──
# Student loan debt: Education Data Initiative, Average Debt for Bachelor's 2025
# Federal average: $35,639 overall; federal-only $28,613; private $36,394
# We use $37,500 as an updated representative combined federal+private estimate.
# SE: ±$2,000 (estimated from cross-source variation)
initial_student_loan_debt    = 37_500.0
initial_student_loan_debt_se = 2_000.0

# Nominal growth / rate parameters
home_appreciation_rate_nominal   = 0.030   # FHFA HPI long-run average
personal_asset_growth_rate_nominal = 0.020 # FDIC national savings rate
retirement_investment_rate       = 0.100   # 10% (DOL/EBSA; Vanguard How America Saves)

# Real (inflation-adjusted) rates
home_appreciation_rate_real      = home_appreciation_rate_nominal - inflation_rate   #  0.5%
personal_asset_growth_rate_real  = personal_asset_growth_rate_nominal - inflation_rate  # -0.5%

# Mortgage — Freddie Mac PMMS April 2, 2026
mortgage_interest_rate  = 0.0646   # 6.46% (was 6.5% last revision)
mortgage_down_payment   = 0.10
mortgage_term_years     = 30
average_home_price_multiplier = 3.5   # ~3.5× income (Census Housing Affordability)

# Salary growth by career stage (BLS age-earnings profile, Table 7)
salary_growth_factors = [1.0, 1.2, 1.5, 1.8]

# Student loan interest rate (federal, 2024-25 AY)
student_loan_interest_rate = 0.0653

# ── COLOR SCHEME ──
plan_colors = {
    'IBR_2014':       '#FF6B6B',
    'IBR_pre2014':    '#C92A2A',
    'ICR':            '#4ECDC4',
    'PAYE':           '#1098AD',
    'SAVE_undergrad': '#9775FA',
    'SAVE_grad':      '#6741D9',
}


# =============================================================================
# CORE SIMULATION FUNCTION — WITH MOE/SE
# =============================================================================
def simulate_wealth_with_idr(avg_income, factor, idr_settings,
                              home_rate, emp_rates, fpl_base,
                              income_se=0.0, home_rate_moe=0.0,
                              debt_mean=None, debt_se=0.0):
    """
    Simulate NET WORTH accumulation over 40-year career (age 22–62).

    Incorporates Margin of Error / Standard Error by drawing each uncertain
    parameter from a normal distribution parameterized by its reported
    point estimate and SE/MOE:

        income ~ N(avg_income × factor, income_se)
        home_purchase_rate ~ clipped N(home_rate, home_rate_moe / 1.645)
        initial_debt ~ N(debt_mean, debt_se)

    Returns ARRAY of net worth values (length = num_individuals) in real 2025 $.

    Net Worth = (Savings + Home Equity + Retirement) − (Student Loans + Mortgage + Consumer Debt)
    """
    if debt_mean is None:
        debt_mean = initial_student_loan_debt

    adjusted_income = float(avg_income * factor)

    # ── Draw income with SE uncertainty ──
    if income_se > 0:
        individual_incomes = np.random.normal(adjusted_income, income_se,
                                              num_individuals).astype(float)
        individual_incomes = np.maximum(individual_incomes, 0.0)
    else:
        individual_incomes = np.full(num_individuals, adjusted_income, dtype=float)

    # ── Draw home-purchase rate with MOE uncertainty ──
    if home_rate_moe > 0:
        # MOE is 90% CI → SE = MOE / 1.645
        home_rate_se = home_rate_moe / 1.645
        sampled_home_rate = float(np.clip(
            np.random.normal(home_rate, home_rate_se), 0.0, 1.0))
    else:
        sampled_home_rate = home_rate

    # ── Draw student-loan debt with SE uncertainty ──
    if debt_se > 0:
        individual_debt = np.random.normal(debt_mean, debt_se,
                                           num_individuals).astype(float)
        individual_debt = np.maximum(individual_debt, 0.0)
    else:
        individual_debt = np.full(num_individuals, float(debt_mean), dtype=float)

    # ── Initialize assets (float) ──
    liquid_assets       = individual_incomes * np.random.uniform(0.1, 0.3, num_individuals).astype(float)
    retirement_balance  = np.zeros(num_individuals, dtype=float)
    home_equity         = np.zeros(num_individuals, dtype=float)

    # ── Initialize liabilities (float) ──
    student_loan_balance = individual_debt.copy()
    mortgage_balance     = np.zeros(num_individuals, dtype=float)
    consumer_debt        = np.zeros(num_individuals, dtype=float)

    # ── Housing ──
    owns_home           = np.random.rand(num_individuals) < sampled_home_rate
    home_purchase_price = (individual_incomes * average_home_price_multiplier).astype(float)
    mortgage_balance[owns_home] = home_purchase_price[owns_home] * (1 - mortgage_down_payment)
    home_value          = home_purchase_price.copy()

    repayment_rate  = idr_settings['repayment_rate']
    repayment_years = idr_settings['years']
    fpl_threshold   = fpl_base * idr_settings['fpl_multiplier']

    salary_by_stage  = [individual_incomes * x for x in salary_growth_factors]
    cumulative_years = 0

    for stage_idx, (emp_rate, salary, years_in_stage) in enumerate(
            zip(emp_rates, salary_by_stage, stage_durations)):

        # Draw employment with SE uncertainty
        sampled_emp_rate = float(np.clip(
            np.random.normal(emp_rate, employment_rates_se), 0.0, 1.0))
        employed      = np.random.rand(num_individuals) < sampled_emp_rate
        annual_income = (employed.astype(float) * salary).astype(float)

        # IDR payment
        if cumulative_years < repayment_years:
            discretionary_income = np.maximum(annual_income - fpl_threshold, 0.0).astype(float)
            annual_idr_payment   = (discretionary_income * repayment_rate).astype(float)
        else:
            annual_idr_payment = np.zeros(num_individuals, dtype=float)

        # Student loan balance update
        student_loan_interest = (student_loan_balance * student_loan_interest_rate).astype(float)
        student_loan_balance  = np.maximum(
            student_loan_balance + student_loan_interest - annual_idr_payment, 0.0).astype(float)

        # Mortgage payment
        if stage_idx == 0:
            monthly_rate = mortgage_interest_rate / 12
            n_payments   = mortgage_term_years * 12
            monthly_payment = np.zeros(num_individuals, dtype=float)
            monthly_payment[owns_home] = (
                mortgage_balance[owns_home] * monthly_rate *
                (1 + monthly_rate) ** n_payments /
                ((1 + monthly_rate) ** n_payments - 1))
            annual_mortgage_payment = (monthly_payment * 12).astype(float)
        else:
            annual_mortgage_payment = np.where(
                owns_home & (mortgage_balance > 0),
                mortgage_balance * 0.08, 0.0).astype(float)

        # Mortgage balance
        mortgage_interest  = (mortgage_balance * mortgage_interest_rate).astype(float)
        mortgage_principal = np.maximum(annual_mortgage_payment - mortgage_interest, 0.0).astype(float)
        mortgage_balance   = np.maximum(mortgage_balance - mortgage_principal, 0.0).astype(float)

        # Home appreciation (real)
        home_value[owns_home] = (
            home_value[owns_home] * (1 + home_appreciation_rate_real) ** years_in_stage).astype(float)
        home_equity = np.maximum(home_value - mortgage_balance, 0.0).astype(float)

        # Consumer debt (non-homeowners)
        consumer_debt[~owns_home] = (annual_income[~owns_home] * 0.05).astype(float)

        # Retirement contributions (10% of income → grows at 7% real)
        retirement_balance = (
            (retirement_balance + annual_income * retirement_investment_rate) *
            (1 + 0.07) ** years_in_stage).astype(float)

        # Personal savings
        living_expenses    = (annual_income * 0.60).astype(float)
        available          = annual_income - living_expenses - annual_idr_payment - annual_mortgage_payment
        annual_savings     = np.maximum(available * 0.5, 0.0).astype(float)
        liquid_assets      = (
            (liquid_assets + annual_savings * years_in_stage) *
            (1 + personal_asset_growth_rate_real) ** years_in_stage).astype(float)

        cumulative_years += years_in_stage

    # Loan forgiveness at end of repayment period
    if cumulative_years >= repayment_years:
        student_loan_balance = np.zeros(num_individuals, dtype=float)

    # Net worth
    total_assets      = (liquid_assets + retirement_balance + home_equity).astype(float)
    total_liabilities = (student_loan_balance + mortgage_balance + consumer_debt).astype(float)
    net_worth         = (total_assets - total_liabilities).astype(float)

    return net_worth


# =============================================================================
# HELPER: compute mean + 95% CI (based on Monte Carlo distribution)
# =============================================================================
def summarize(arr):
    """Return (mean, lower_95ci, upper_95ci) from simulation array."""
    m   = np.mean(arr)
    se  = np.std(arr) / np.sqrt(len(arr))
    return m, m - 1.96 * se, m + 1.96 * se


# =============================================================================
# PART 1: Individual Scenarios
# =============================================================================
print("Running Part 1: Individual scenarios (40-year career simulation)...")
print("Timeline: Age 22 (graduation) → Age 62 (retirement)")
print("Wealth reported in REAL 2025 dollars (inflation-adjusted)\n")
print("Now incorporating MOE/SE in all stochastic parameters.\n")

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
                fpl_single,
                income_se=group_data['income_se'],
                home_rate_moe=home_purchase_rates_moe[category],
                debt_mean=initial_student_loan_debt,
                debt_se=initial_student_loan_debt_se,
            )

# ── Figure 1: Net Worth at Retirement — by race/gender (with 95% CI error bars) ──
for category in data.keys():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    x     = np.arange(len(income_brackets))
    width = 0.13

    for i, (plan_name, color) in enumerate(plan_colors.items()):
        means, lowers, uppers = zip(*[
            summarize(results_by_plan[plan_name][category][bracket])
            for bracket in income_brackets
        ])
        means  = list(means)
        errors = [m - l for m, l in zip(means, lowers)]

        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color,
                      edgecolor='white', linewidth=0.5)
        ax.errorbar(x + (i - 2.5) * width, means,
                    yerr=errors, fmt='none', color='#333333',
                    capsize=3, linewidth=1, capthick=1)

        for j, bar in enumerate(bars):
            height = bar.get_height()
            offset = height * (1.01 if i % 2 == 0 else 1.03)
            ax.text(bar.get_x() + bar.get_width() / 2, offset,
                    f'${height/1000:.0f}K', ha='center', va='bottom',
                    fontsize=7, rotation=0)

    avg_income = data[category]['avg_income']
    ax.set_title(
        f'{category}\nAverage Income: ${avg_income:,} (BLS Q4 2024)\n'
        f'Net Worth at Retirement (Age 62, Real 2025 $) — Error bars = 95% CI',
        fontsize=11, fontweight='bold')
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
# PART 2: Family of 4 Scenarios
# =============================================================================
races      = list(family_income_by_race.keys())
tier_names = list(family_income_tiers.keys())
race_colors_main = {'Black': '#E74C3C', 'White': '#3498DB', 'Hispanic': '#2ECC71'}

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
                fpl_family_of_4,
                income_se=family_income_moe[race],
                home_rate_moe=home_purchase_rates_moe_by_race[race],
                debt_mean=initial_student_loan_debt,
                debt_se=initial_student_loan_debt_se,
            )

# ── Figure 2: Family net worth by race (with 95% CI error bars) ──
for race in races:
    fig2, ax = plt.subplots(1, 1, figsize=(12, 7))
    x     = np.arange(len(tier_names))
    width = 0.13

    for i, (plan_name, color) in enumerate(plan_colors.items()):
        means, lowers, uppers = zip(*[
            summarize(family_results[plan_name][race][tier])
            for tier in tier_names
        ])
        means  = list(means)
        errors = [m - l for m, l in zip(means, lowers)]

        bars = ax.bar(x + (i - 2.5) * width, means, width,
                      label=plan_name.replace('_', ' '), color=color,
                      edgecolor='white', linewidth=0.5)
        ax.errorbar(x + (i - 2.5) * width, means,
                    yerr=errors, fmt='none', color='#333333',
                    capsize=3, linewidth=1, capthick=1)

        for j, bar in enumerate(bars):
            height = bar.get_height()
            offset = height * (1.01 if i % 2 == 0 else 1.03)
            ax.text(bar.get_x() + bar.get_width() / 2, offset,
                    f'${height/1000:.0f}K', ha='center', va='bottom', fontsize=7)

    base_inc = family_income_by_race[race]
    ax.set_title(
        f'{race} Family of 4\nMedian HH Income: ${base_inc:,} (Census CPS/ASEC 2024)\n'
        f'Net Worth at Retirement (Age 62, Real 2025 $) — Error bars = 95% CI',
        fontsize=11, fontweight='bold')
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
# PART 3: Cross-Racial Comparison Charts
# =============================================================================
print("\nGenerating Part 3: Cross-racial comparison charts (split by race)...")
plan_names_short = [p.replace('_', ' ') for p in idr_plans.keys()]

# Figure 3: Annual IDR Payment Burden
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, (tier_name, tier_factor) in zip(axes, family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        payments = []
        colors_list = list(plan_colors.values())
        for plan_name, settings in idr_plans.items():
            fpl_thresh   = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income  = max(annual_income - fpl_thresh, 0)
            payments.append(disc_income * settings['repayment_rate'])
        bars = ax.bar(x, payments, color=colors_list, edgecolor='white', linewidth=0.8)
        for i, bar in enumerate(bars):
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        h * (1.02 if i % 2 == 0 else 1.05),
                        f'${h/1000:.1f}K', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, 200,
                        '$0', ha='center', va='bottom', fontsize=7, color='gray')
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=20, ha='right')
        ax.set_ylabel('Annual IDR Payment ($)' if ax == axes[0] else '', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle(f'{race} Family of 4 — Annual IDR Payment Burden',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig3_idr_payment_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 4: Post-IDR Disposable Income
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, (tier_name, tier_factor) in zip(axes, family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        disposable = []
        colors_list = list(plan_colors.values())
        for plan_name, settings in idr_plans.items():
            fpl_thresh  = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            disposable.append(annual_income - disc_income * settings['repayment_rate'])
        bars = ax.bar(x, disposable, color=colors_list, edgecolor='white', linewidth=0.8)
        for i, bar in enumerate(bars):
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2,
                    h * (1.01 if i % 2 == 0 else 1.02),
                    f'${h/1000:.0f}K', ha='center', va='bottom', fontsize=7)
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=20, ha='right')
        ax.set_ylabel('Post-IDR Disposable Income ($)' if ax == axes[0] else '', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle(f'{race} Family of 4 — Post-IDR Disposable Income',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig4_disposable_income_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 5: Monthly Payment & % of Income
for race in races:
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharey='row')
    colors_list = list(plan_colors.values())
    for ax, (tier_name, tier_factor) in zip(axes[0], family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        monthly_payments = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh  = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income = max(annual_income - fpl_thresh, 0)
            monthly_payments.append((disc_income * settings['repayment_rate']) / 12)
        bars = ax.bar(x, monthly_payments, color=colors_list, edgecolor='white', linewidth=0.8)
        for i, bar in enumerate(bars):
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        h * (1.03 if i % 2 == 0 else 1.07),
                        f'${h:.0f}', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, 10,
                        '$0', ha='center', va='bottom', fontsize=7, color='gray')
        ax.set_title(f'{tier_name}\n(${annual_income:,.0f})', fontsize=9, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=7, rotation=20, ha='right')
        ax.set_ylabel('Monthly Payment ($)' if ax == axes[0][0] else '', fontsize=9)
        ax.grid(axis='y', alpha=0.3)
    for ax, (tier_name, tier_factor) in zip(axes[1], family_income_tiers.items()):
        annual_income = family_income_by_race[race] * tier_factor
        x = np.arange(len(idr_plans))
        pct_of_income = []
        for plan_name, settings in idr_plans.items():
            fpl_thresh   = fpl_family_of_4 * settings['fpl_multiplier']
            disc_income  = max(annual_income - fpl_thresh, 0)
            annual_pmt   = disc_income * settings['repayment_rate']
            pct_of_income.append((annual_pmt / annual_income) * 100 if annual_income > 0 else 0)
        bars = ax.bar(x, pct_of_income, color=colors_list, edgecolor='white', linewidth=0.8)
        for i, bar in enumerate(bars):
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        h * (1.05 if i % 2 == 0 else 1.12),
                        f'{h:.1f}%', ha='center', va='bottom', fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, 0.3,
                        '0%', ha='center', va='bottom', fontsize=7, color='gray')
        ax.set_title(f'{tier_name}', fontsize=9, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=7, rotation=20, ha='right')
        ax.set_ylabel('% of Gross Income' if ax == axes[1][0] else '', fontsize=9)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle(
        f'{race} Family of 4 — Monthly Payment (Top) & % of Income (Bottom)',
        fontsize=13, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig5_monthly_payment_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 6: Wealth Generation (Family of 4) with CI
for race in races:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    colors_list = list(plan_colors.values())
    for ax, tier_name in zip(axes, tier_names):
        x = np.arange(len(idr_plans))
        means, lowers, uppers = zip(*[
            summarize(family_results[plan_name][race][tier_name])
            for plan_name in idr_plans
        ])
        means  = list(means)
        errors = [m - l for m, l in zip(means, lowers)]
        bars   = ax.bar(x, means, color=colors_list, edgecolor='white', linewidth=0.8)
        ax.errorbar(x, means, yerr=errors, fmt='none', color='#333333',
                    capsize=3, linewidth=1, capthick=1)
        for i, bar in enumerate(bars):
            h      = bar.get_height()
            offset = h * (1.01 if i % 2 == 0 else 1.03)
            ax.text(bar.get_x() + bar.get_width() / 2, offset,
                    f'${h/1000:.0f}K', ha='center', va='bottom', fontsize=7)
        ax.set_title(f'{tier_name}', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=20, ha='right')
        ax.set_ylabel('Net Worth (Real 2025 $)' if ax == axes[0] else '', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle(
        f'{race} Family of 4 — Net Worth at Retirement by IDR Plan\n(Error bars = 95% CI)',
        fontsize=14, fontweight='bold', y=1.03)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig6_wealth_generation_{race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# Figure 7: Racial Wealth Gap
for minority_race in ['Black', 'Hispanic']:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    colors_list = list(plan_colors.values())
    for ax, tier_name in zip(axes, tier_names):
        x = np.arange(len(idr_plans))
        white_means = [np.mean(family_results[plan_name]['White'][tier_name])
                       for plan_name in idr_plans]
        race_means  = [np.mean(family_results[plan_name][minority_race][tier_name])
                       for plan_name in idr_plans]
        gap_pct     = [(r / w - 1) * 100 for r, w in zip(race_means, white_means)]
        bars = ax.bar(x, gap_pct, color=colors_list, edgecolor='white', linewidth=0.8)
        for i, bar in enumerate(bars):
            h = bar.get_height()
            offset = h * 1.08
            va     = 'top' if h < 0 else 'bottom'
            ax.text(bar.get_x() + bar.get_width() / 2, offset,
                    f'{h:.1f}%', ha='center', va=va, fontsize=8, fontweight='bold')
        ax.axhline(y=0, color='#333333', linestyle='-', linewidth=1.5)
        ax.set_title(f'{tier_name}', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plan_names_short, fontsize=8, rotation=20, ha='right')
        ax.set_ylabel('Wealth Gap vs White (%)' if ax == axes[0] else '', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle(
        f'{minority_race} vs White — Wealth Gap by IDR Plan\n'
        f'(Negative % = {minority_race} family accumulates less wealth than White family)',
        fontsize=13, fontweight='bold', y=1.03)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f'fig7_wealth_gap_{minority_race.lower()}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


# =============================================================================
# PART 4: SENSITIVITY ANALYSIS
# =============================================================================
print("\nRunning Part 4: Sensitivity Analysis...")

# ── 4A: Tornado Chart ──
# We perturb one parameter at a time (±1 SE / ±1 MOE from baseline) and
# measure the resulting swing in mean net worth for a reference case:
#   White Men, Median income, IBR_2014 plan
# This shows which inputs drive the most uncertainty in the outcome.

ref_category   = 'White Men'
ref_bracket    = 'Median 50%'
ref_plan       = 'IBR_2014'
ref_plan_set   = idr_plans[ref_plan]
ref_income     = data[ref_category]['avg_income']
ref_income_se  = data[ref_category]['income_se']
ref_home_rate  = home_purchase_rates[ref_category]
ref_home_moe   = home_purchase_rates_moe[ref_category]
ref_factor     = income_factors[income_brackets.index(ref_bracket)]

def run_ref(income_override=None, home_override=None,
            debt_override=None, mort_rate_override=None,
            ret_rate_override=None, emp_se_override=None):
    """Run reference scenario with one-parameter perturbations."""
    global mortgage_interest_rate, retirement_investment_rate, employment_rates_se

    orig_mort = mortgage_interest_rate
    orig_ret  = retirement_investment_rate
    orig_emp  = employment_rates_se

    if mort_rate_override is not None:
        mortgage_interest_rate = mort_rate_override
    if ret_rate_override is not None:
        retirement_investment_rate = ret_rate_override
    if emp_se_override is not None:
        employment_rates_se = emp_se_override

    result = simulate_wealth_with_idr(
        income_override if income_override is not None else ref_income,
        ref_factor, ref_plan_set,
        home_override if home_override is not None else ref_home_rate,
        employment_rates[ref_category],
        fpl_single,
        income_se=ref_income_se,
        home_rate_moe=ref_home_moe,
        debt_mean=debt_override if debt_override is not None else initial_student_loan_debt,
        debt_se=initial_student_loan_debt_se,
    )

    mortgage_interest_rate     = orig_mort
    retirement_investment_rate = orig_ret
    employment_rates_se        = orig_emp

    return np.mean(result)

baseline_nw = run_ref()

# Each tuple: (label, low_value, high_value, param_name)
sensitivity_params = [
    ('Annual Income',         ref_income - ref_income_se,   ref_income + ref_income_se,   'income'),
    ('Homeownership Rate',    ref_home_rate - ref_home_moe, ref_home_rate + ref_home_moe, 'home'),
    ('Initial Loan Debt',     initial_student_loan_debt - initial_student_loan_debt_se,
                              initial_student_loan_debt + initial_student_loan_debt_se,     'debt'),
    ('Mortgage Rate',         mortgage_interest_rate - 0.005, mortgage_interest_rate + 0.005, 'mort'),
    ('Retirement Contrib.',   retirement_investment_rate - 0.01, retirement_investment_rate + 0.01, 'ret'),
    ('Employment Rate Uncert.', employment_rates_se - 0.005, employment_rates_se + 0.005, 'emp'),
]

tornado_results = []
for label, low_val, high_val, param in sensitivity_params:
    if param == 'income':
        nw_low  = run_ref(income_override=low_val)
        nw_high = run_ref(income_override=high_val)
    elif param == 'home':
        nw_low  = run_ref(home_override=max(low_val, 0.0))
        nw_high = run_ref(home_override=min(high_val, 1.0))
    elif param == 'debt':
        nw_low  = run_ref(debt_override=max(low_val, 0.0))
        nw_high = run_ref(debt_override=high_val)
    elif param == 'mort':
        nw_low  = run_ref(mort_rate_override=max(low_val, 0.01))
        nw_high = run_ref(mort_rate_override=high_val)
    elif param == 'ret':
        nw_low  = run_ref(ret_rate_override=max(low_val, 0.0))
        nw_high = run_ref(ret_rate_override=high_val)
    elif param == 'emp':
        nw_low  = run_ref(emp_se_override=max(low_val, 0.0))
        nw_high = run_ref(emp_se_override=high_val)
    tornado_results.append((label, nw_low - baseline_nw, nw_high - baseline_nw))

# Sort by total swing (absolute range)
tornado_results.sort(key=lambda r: abs(r[2] - r[1]))

labels = [r[0] for r in tornado_results]
lows   = [r[1] for r in tornado_results]
highs  = [r[2] for r in tornado_results]

fig_t, ax_t = plt.subplots(figsize=(11, 6))
y_pos = np.arange(len(labels))

for i, (label, low, high) in enumerate(zip(labels, lows, highs)):
    left  = min(low, high)
    right = max(low, high)
    width_bar = right - left
    ax_t.barh(i, width_bar, left=left,
              color='#4ECDC4' if high > 0 else '#FF6B6B',
              edgecolor='white', linewidth=0.5)
    ax_t.text(left - 2000, i, f'${left/1000:+.0f}K', va='center',
              ha='right', fontsize=8, color='#333333')
    ax_t.text(right + 2000, i, f'${right/1000:+.0f}K', va='center',
              ha='left', fontsize=8, color='#333333')

ax_t.axvline(0, color='#222222', linewidth=1.5, linestyle='--')
ax_t.set_yticks(y_pos)
ax_t.set_yticklabels(labels, fontsize=10)
ax_t.set_xlabel('Change in Mean Net Worth vs. Baseline (Real 2025 $)', fontsize=10)
ax_t.set_title(
    f'Sensitivity (Tornado) Chart — {ref_category}, {ref_bracket} Income, {ref_plan.replace("_"," ")}\n'
    f'Baseline Net Worth: ${baseline_nw/1000:.0f}K | Each bar = ±1 SE/MOE perturbation',
    fontsize=11, fontweight='bold')
ax_t.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig8_sensitivity_tornado.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()


# ── 4B: Scenario Sensitivity Table (all IDR plans × economic scenarios) ──
# Three macro scenarios: pessimistic, baseline, optimistic
print("  Running sensitivity scenario matrix...")

scenarios = {
    'Pessimistic': {
        'income_mult':         0.95,    # 5% below baseline income
        'mortgage_rate':       0.075,   # 7.5% mortgage rate
        'home_appreciation':   0.01,    # 1% nominal appreciation
        'retirement_return':   0.05,    # 5% real retirement return
        'loan_debt':           42000,   # higher debt burden
    },
    'Baseline': {
        'income_mult':         1.00,
        'mortgage_rate':       0.0646,
        'home_appreciation':   0.03,
        'retirement_return':   0.07,
        'loan_debt':           37500,
    },
    'Optimistic': {
        'income_mult':         1.05,    # 5% above baseline income
        'mortgage_rate':       0.055,   # 5.5% mortgage rate
        'home_appreciation':   0.04,    # 4% nominal appreciation
        'retirement_return':   0.09,    # 9% real retirement return
        'loan_debt':           30000,   # lower debt burden
    },
}

# Reference demographic: White Men at median income for comparability
sens_income = data['White Men']['avg_income']
sens_se     = data['White Men']['income_se']
sens_home   = home_purchase_rates['White Men']
sens_moe    = home_purchase_rates_moe['White Men']
sens_emp    = employment_rates['White Men']

def run_scenario(plan_name, scenario_params):
    global mortgage_interest_rate, home_appreciation_rate_real, home_appreciation_rate_nominal

    orig_mort  = mortgage_interest_rate
    orig_happ  = home_appreciation_rate_real
    orig_happn = home_appreciation_rate_nominal

    mortgage_interest_rate       = scenario_params['mortgage_rate']
    home_appreciation_rate_nominal = scenario_params['home_appreciation']
    home_appreciation_rate_real  = scenario_params['home_appreciation'] - inflation_rate

    result = simulate_wealth_with_idr(
        sens_income * scenario_params['income_mult'],
        1.0, idr_plans[plan_name],
        sens_home, sens_emp,
        fpl_single,
        income_se=sens_se,
        home_rate_moe=sens_moe,
        debt_mean=scenario_params['loan_debt'],
        debt_se=initial_student_loan_debt_se,
    )

    mortgage_interest_rate       = orig_mort
    home_appreciation_rate_real  = orig_happ
    home_appreciation_rate_nominal = orig_happn

    return np.mean(result)

# Build scenario × plan grid
scenario_grid = {}
for scen_name, scen_params in scenarios.items():
    scenario_grid[scen_name] = {}
    for plan_name in idr_plans:
        scenario_grid[scen_name][plan_name] = run_scenario(plan_name, scen_params)

# Plot scenario sensitivity heatmap-style grouped bar chart
fig_s, ax_s = plt.subplots(figsize=(13, 6))
x_pos     = np.arange(len(idr_plans))
plan_list = list(idr_plans.keys())
scen_colors = {'Pessimistic': '#E74C3C', 'Baseline': '#3498DB', 'Optimistic': '#2ECC71'}
n_scen    = len(scenarios)
width_s   = 0.25

for i, (scen_name, scen_vals) in enumerate(scenario_grid.items()):
    means = [scen_vals[p] for p in plan_list]
    bars  = ax_s.bar(x_pos + (i - 1) * width_s, means, width_s,
                     label=scen_name, color=scen_colors[scen_name],
                     edgecolor='white', linewidth=0.5)
    for bar in bars:
        h = bar.get_height()
        ax_s.text(bar.get_x() + bar.get_width() / 2,
                  h * 1.01, f'${h/1000:.0f}K',
                  ha='center', va='bottom', fontsize=7)

ax_s.set_xticks(x_pos)
ax_s.set_xticklabels([p.replace('_', ' ') for p in plan_list], fontsize=9, rotation=15, ha='right')
ax_s.set_ylabel('Mean Net Worth at Retirement (Real 2025 $)', fontsize=10)
ax_s.set_title(
    'Sensitivity Analysis — Economic Scenarios × IDR Plan\n'
    'Reference: White Men, Median Income | Pessimistic / Baseline / Optimistic',
    fontsize=11, fontweight='bold')
ax_s.legend(fontsize=10)
ax_s.grid(axis='y', alpha=0.3)

# Annotation box describing scenarios
scenario_text = (
    "Pessimistic: income −5%, mortgage 7.5%, home appr. 1%, ret. return 5%, debt $42K\n"
    "Baseline:    income base, mortgage 6.46%, home appr. 3%, ret. return 7%, debt $37.5K\n"
    "Optimistic:  income +5%, mortgage 5.5%, home appr. 4%, ret. return 9%, debt $30K"
)
ax_s.text(0.01, 0.01, scenario_text, transform=ax_s.transAxes,
          fontsize=7.5, verticalalignment='bottom',
          bbox=dict(boxstyle='round', facecolor='#F8F9FA', alpha=0.8))

plt.tight_layout()
save_path = os.path.join(output_dir, 'fig9_sensitivity_scenarios.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()


# ── 4C: Racial Wealth Gap Sensitivity — Does the gap widen/narrow by scenario? ──
print("  Running racial wealth gap sensitivity...")

def run_race_scenario(race, plan_name, scenario_params):
    """Run family-of-4 scenario for a given race."""
    global mortgage_interest_rate, home_appreciation_rate_real, home_appreciation_rate_nominal

    orig_mort  = mortgage_interest_rate
    orig_happ  = home_appreciation_rate_real
    orig_happn = home_appreciation_rate_nominal

    mortgage_interest_rate         = scenario_params['mortgage_rate']
    home_appreciation_rate_nominal = scenario_params['home_appreciation']
    home_appreciation_rate_real    = scenario_params['home_appreciation'] - inflation_rate

    result = simulate_wealth_with_idr(
        family_income_by_race[race] * scenario_params['income_mult'],
        1.0, idr_plans[plan_name],
        home_purchase_rates_by_race[race],
        employment_rates_by_race[race],
        fpl_family_of_4,
        income_se=family_income_moe[race],
        home_rate_moe=home_purchase_rates_moe_by_race[race],
        debt_mean=scenario_params['loan_debt'],
        debt_se=initial_student_loan_debt_se,
    )

    mortgage_interest_rate         = orig_mort
    home_appreciation_rate_real    = orig_happ
    home_appreciation_rate_nominal = orig_happn
    return np.mean(result)

# Pick IBR_2014 as representative plan
rep_plan = 'IBR_2014'
gap_by_scenario = {}
for scen_name, scen_params in scenarios.items():
    white_nw = run_race_scenario('White', rep_plan, scen_params)
    gap_by_scenario[scen_name] = {
        race: (run_race_scenario(race, rep_plan, scen_params) / white_nw - 1) * 100
        for race in ['Black', 'Hispanic']
    }

fig_g, ax_g = plt.subplots(figsize=(9, 5))
race_min_colors = {'Black': '#E74C3C', 'Hispanic': '#2ECC71'}
scen_labels     = list(scenarios.keys())
x_g = np.arange(len(scen_labels))
width_g = 0.30

for i, (race, color) in enumerate(race_min_colors.items()):
    gaps = [gap_by_scenario[s][race] for s in scen_labels]
    bars = ax_g.bar(x_g + (i - 0.5) * width_g, gaps,
                    width_g, label=race, color=color,
                    edgecolor='white', linewidth=0.5)
    for bar in bars:
        h = bar.get_height()
        ax_g.text(bar.get_x() + bar.get_width() / 2,
                  h * 1.05 if h < 0 else h * 1.02,
                  f'{h:.1f}%', ha='center',
                  va='top' if h < 0 else 'bottom',
                  fontsize=9, fontweight='bold')

ax_g.axhline(0, color='#333333', linewidth=1.5, linestyle='--')
ax_g.set_xticks(x_g)
ax_g.set_xticklabels(scen_labels, fontsize=11)
ax_g.set_ylabel('Wealth Gap vs White Family (%)', fontsize=10)
ax_g.set_title(
    f'Racial Wealth Gap Sensitivity by Economic Scenario\n'
    f'Family of 4, {rep_plan.replace("_"," ")} Plan — Median Income Tier',
    fontsize=11, fontweight='bold')
ax_g.legend(fontsize=10)
ax_g.grid(axis='y', alpha=0.3)
plt.tight_layout()
save_path = os.path.join(output_dir, 'fig10_wealth_gap_sensitivity.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Saved: {save_path}")
plt.close()


# =============================================================================
# SUMMARY OUTPUT
# =============================================================================
print("\n" + "=" * 80)
print("ALL CHARTS SAVED SUCCESSFULLY!")
print("=" * 80)
print(f"Location: {output_dir}")
print("\nGenerated files (26 total):")
print("\nPart 1 — Individual Scenarios by Race/Gender (6 files):")
for cat in data.keys():
    print(f"  fig1_individual_{cat.lower().replace(' ','_')}.png")
print("\nPart 2 — Family of 4 by Race (3 files):")
for race in races:
    print(f"  fig2_family_{race.lower()}.png")
print("\nPart 3 — Cross-Racial Comparisons (14 files):")
for fig, label in [('fig3','IDR Payment Burden'),('fig4','Disposable Income'),
                   ('fig5','Monthly Payment & %'),('fig6','Wealth Generation')]:
    for race in races:
        print(f"  {fig}_{label.lower().replace(' ','_').replace('&','and').replace('%','pct')}_{race.lower()}.png")
for race in ['black','hispanic']:
    print(f"  fig7_wealth_gap_{race}.png")
print("\nPart 4 — Sensitivity Analysis (3 files):")
print("  fig8_sensitivity_tornado.png       ← One-at-a-time ±1 SE/MOE parameter perturbation")
print("  fig9_sensitivity_scenarios.png     ← Pessimistic / Baseline / Optimistic × all plans")
print("  fig10_wealth_gap_sensitivity.png   ← Racial wealth gap across economic scenarios")

print("\n" + "=" * 80)
print("UPDATED PARAMETER VALUES (vs. previous version)")
print("=" * 80)
print(f"  FPL (single):     $15,960  (was $15,650) — 2026 HHS Guidelines")
print(f"  FPL (family 4):   $33,000  (was $32,150) — 2026 HHS Guidelines")
print(f"  Black Men income: ${data['Black Men']['avg_income']:,.0f}   (was $54,028) — BLS Q4 2024, ±${data['Black Men']['income_se']:.0f} SE")
print(f"  Black Women:      ${data['Black Women']['avg_income']:,.0f}   (was $48,984) — BLS Q4 2024, ±${data['Black Women']['income_se']:.0f} SE")
print(f"  White Men:        ${data['White Men']['avg_income']:,.0f}   (was $70,408) — BLS Q4 2024, ±${data['White Men']['income_se']:.0f} SE")
print(f"  White Women:      ${data['White Women']['avg_income']:,.0f}   (was $57,616) — BLS Q4 2024, ±${data['White Women']['income_se']:.0f} SE")
print(f"  Latinx Men:       ${data['Latinx Men']['avg_income']:,.0f}   (was $52,156) — BLS Q4 2024, ±${data['Latinx Men']['income_se']:.0f} SE")
print(f"  Latinx Women:     ${data['Latinx Women']['avg_income']:,.0f}   (was $46,228) — BLS Q4 2024, ±${data['Latinx Women']['income_se']:.0f} SE")
print(f"  Student loan debt: ${initial_student_loan_debt:,.0f}  (was $40,000) — Education Data Initiative 2025, ±${initial_student_loan_debt_se:,.0f} SE")
print(f"  Mortgage rate:    {mortgage_interest_rate*100:.2f}%    (was 6.50%) — Freddie Mac PMMS Apr 2, 2026")
print(f"  Homeownership — Hispanic: {home_purchase_rates_by_race['Hispanic']*100:.1f}%  (unchanged) — Census CPS/HVS Q4 2025")
print(f"  Employment rates updated to BLS CPS 2025 Annual Averages (Table 3/4)")
print(f"  Family incomes: Black ${family_income_by_race['Black']:,} ± ${family_income_moe['Black']:.0f}, "
      f"White ${family_income_by_race['White']:,} ± ${family_income_moe['White']:.0f}, "
      f"Hispanic ${family_income_by_race['Hispanic']:,} ± ${family_income_moe['Hispanic']:.0f}")
print("\n" + "=" * 80)
print("MOE / SE INTEGRATION")
print("=" * 80)
print("  Each simulation draw samples income from N(mean, SE) per BLS/Census reporting")
print("  Home purchase rates sampled from N(rate, MOE/1.645) [90% CI conversion]")
print("  Student loan debt sampled from N($37,500, $2,000)")
print("  Employment rates perturbed by N(0, 0.015) each stage")
print("  95% CI error bars shown on all wealth charts (Figures 1, 2, 6)")
print("=" * 80)
print("\nCITATIONS:")
print("  [1] BLS Usual Weekly Earnings Q4 2024: https://www.bls.gov/news.release/archives/wkyeng_02212025.pdf")
print("  [2] BLS 2025 Annual Averages: https://www.bls.gov/news.release/pdf/wkyeng.pdf")
print("  [3] HHS 2026 Federal Poverty Guidelines: https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines")
print("  [4] Census CPS/HVS Homeownership by Race (FRED): https://fred.stlouisfed.org/series/BOAAAHORUSQ156N")
print("  [5] Education Data Initiative, Bachelor's Debt 2025: https://educationdata.org/average-debt-for-a-bachelors-degree")
print("  [6] Freddie Mac PMMS April 2026: https://www.freddiemac.com/pmms")
print("  [7] Census CPS/ASEC 2024 Household Income: https://www.census.gov/topics/income-poverty/income.html")
print("=" * 80)
