import numpy as np
import matplotlib.pyplot as plt

# Detailed data template for Race, Gender, and Income Groups (placeholder values)
data = {
    'Black Men': {'avg_income': 38000},
    'Black Women': {'avg_income': 32000},
    'White Men': {'avg_income': 48000},
    'White Women': {'avg_income': 42000},
    'Latinx Men': {'avg_income': 39000},
    'Latinx Women': {'avg_income': 34000}
}

income_brackets = ['Lower 25%', 'Median 50%', 'Upper 25%']
income_factors = [0.75, 1.0, 1.25]

# Simulation parameters
num_individuals = 1_000_000

# Enhanced wealth simulation function
def simulate_wealth(avg_income, factor, debt=True):
    adjusted_income = avg_income * factor
    initial_wealth = adjusted_income * np.random.uniform(0.5, 1.5, num_individuals)

    # College debt factor
    debt_amount = np.random.normal(35000, 10000, num_individuals) if debt else 0

    # Post-college wealth growth
    employment_rates = [0.7, 0.8, 0.9, 0.95]
    salary_growth = [adjusted_income * x for x in [1.1, 1.2, 1.5, 2.0]]
    home_purchase_rate = 0.5
    home_appreciation_rate = 0.03
    retirement_investment_rate = 0.1
    college_debt_payment_rate = 0.4
    personal_asset_growth_rate = 0.02

    wealth = initial_wealth - debt_amount

    for rate, salary in zip(employment_rates, salary_growth):
        employed = np.random.rand(num_individuals) < rate
        income = employed * salary

        home_wealth = home_purchase_rate * income * home_appreciation_rate
        retirement_savings = income * retirement_investment_rate
        debt_payments = debt_amount * college_debt_payment_rate
        asset_growth = wealth * personal_asset_growth_rate

        wealth += income + home_wealth + retirement_savings + asset_growth - debt_payments

    return wealth

# Run simulations and collect results
results_with_debt = {}
results_no_debt = {}
for category, group_data in data.items():
    results_with_debt[category] = {}
    results_no_debt[category] = {}
    for bracket, factor in zip(income_brackets, income_factors):
        results_with_debt[category][bracket] = simulate_wealth(group_data['avg_income'], factor, debt=True)
        results_no_debt[category][bracket] = simulate_wealth(group_data['avg_income'], factor, debt=False)

# Visualization
fig, axes = plt.subplots(len(data), 1, figsize=(12, 30))

for ax, category in zip(axes, data.keys()):
    means_debt = [np.mean(results_with_debt[category][bracket]) for bracket in income_brackets]
    means_no_debt = [np.mean(results_no_debt[category][bracket]) for bracket in income_brackets]
    for bracket, m_debt, m_no_debt in zip(income_brackets, means_debt, means_no_debt):
        print(f"{category} - {bracket}: With Debt ${m_debt:,.0f}, No Debt ${m_no_debt:,.0f}")

    x = np.arange(len(income_brackets))
    width = 0.35
    bars1 = ax.bar(x - width/2, means_debt, width, label='With Debt', color='#FFA07A')
    bars2 = ax.bar(x + width/2, means_no_debt, width, label='No Debt', color='#20B2AA')

    ax.set_title(f'Average Wealth by Income Bracket for {category}')
    ax.set_xticks(x)
    ax.set_xticklabels(income_brackets)
    ax.set_ylabel('Average Wealth ($)')
    ax.legend()

    # Add numerical values above bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:,.0f}', ha='center', va='bottom')

plt.tight_layout()
output_path = r"C:\Users\OJM EQRC\OneDrive\Desktop\wealth_simulation.png"
plt.savefig(output_path)
