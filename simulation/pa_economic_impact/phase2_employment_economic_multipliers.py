"""Phase 2: Employment, Off-Campus Spending & Economic Multipliers
Pennsylvania Higher Education Economic Impact Analysis

Sources:
- BEA RIMS II Multipliers (bea.gov)
- BLS Employment Data (bls.gov)
- Havranek et al. (2018) tuition elasticity meta-analysis
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# PHASE 2: EMPLOYMENT, OFF-CAMPUS SPENDING & ECONOMIC MULTIPLIERS
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: EMPLOYMENT & ECONOMIC IMPACT ANALYSIS")
print("=" * 80)

# BEA RIMS II Multipliers display
print(f"\nRIMS II Multipliers (PA-specific):")
print(f"  Output: {rims_ii_multipliers['output_multiplier']}x")
print(f"  Employment: {rims_ii_multipliers['employment_multiplier']} jobs per $1M")
print(f"  Earnings: {rims_ii_multipliers['earnings_multiplier']}x")

# Employment by Sector
print(f"\nEmployment by Sector:")
print(f"  Total Direct Employment: {total_direct_employment:,}")
print(f"  Total Annual Payroll: ${total_payroll/1e9:.2f}B")

# Indirect/induced employment
print(f"\nTotal Jobs Supported:")
print(f"  Direct: {total_direct_employment:,}")
print(f"  Indirect: {indirect_employment:,}")
print(f"  Induced: {induced_employment:,}")
print(f"  TOTAL: {total_jobs_supported:,}")

# Student Off-Campus Spending
print(f"\nTotal Student Off-Campus Spending: ${total_student_spending/1e9:.2f}B")

# -----------------------------------------------------------------------------
# 2.4 SENSITIVITY ANALYSIS (Monte Carlo Framework)
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("SENSITIVITY ANALYSIS")
print("-" * 60)

np.random.seed(RANDOM_SEED)

simulation_results = {}
for param, (mean, std) in param_distributions.items():
    simulation_results[param] = np.random.normal(mean, std, MONTE_CARLO_SIMULATIONS)

impact_distribution = base_direct_spending * simulation_results['output_multiplier']

print(f"Economic Impact Uncertainty (n={MONTE_CARLO_SIMULATIONS:,} simulations):")
print(f"  Mean: ${np.mean(impact_distribution)/1e9:.2f}B")
print(f"  Std Dev: ${np.std(impact_distribution)/1e9:.2f}B")
print(f"  95% CI: ${np.percentile(impact_distribution, 2.5)/1e9:.2f}B - ${np.percentile(impact_distribution, 97.5)/1e9:.2f}B")

print(f"\nTuition Elasticity Estimates (Havranek et al. 2018):")
print(f"  Overall Mean: -0.037 (near-zero effect)")
print(f"  Public Universities: +0.003 (essentially zero)")
print(f"  Long-run Effect: -0.062 (6x larger than short-run)")
