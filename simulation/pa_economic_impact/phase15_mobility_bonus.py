import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 15: MOBILITY BONUS PREMIUM (20% for MSIs / High-Pell Institutions)
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 15: MOBILITY BONUS PREMIUM (20% for MSIs / High-Pell)")
print("=" * 80)

print(f"\nMobility Bonus Rate: {mobility_bonus_rate*100:.0f}% per-pupil premium")
print(f"\n{'Institution':<30} {'Type':<18} {'Pell %':>7} {'Students':>10} {'Annual Bonus':>14}")
print("-" * 82)

total_bonus_annual = 0
for inst, data in mobility_bonus_institutions.items():
    # Per-pupil funding (use avg state appropriation per student as base)
    base_per_pupil = total_state_appropriation / total_enrollment_all
    bonus = data['enrollment'] * base_per_pupil * mobility_bonus_rate
    total_bonus_annual += bonus
    print(f"{inst:<30} {data['type']:<18} {data['pell_share']*100:>6.0f}% {data['enrollment']:>9,} ${bonus/1e6:>11.2f}M")

print(f"\nTotal Annual Mobility Bonus Cost: ${total_bonus_annual/1e6:.2f}M")
print(f"40-Year Cost (inflation-adjusted): ${total_bonus_annual * 40 / 1e9:.2f}B")

# County-level multiplier effect
print(f"\nCounty-Level Multiplier Effects from Mobility Bonus:")
bonus_by_county = {}
for inst, data in mobility_bonus_institutions.items():
    county = data['county']
    base_per_pupil = total_state_appropriation / total_enrollment_all
    bonus = data['enrollment'] * base_per_pupil * mobility_bonus_rate
    if county not in bonus_by_county:
        bonus_by_county[county] = 0
    bonus_by_county[county] += bonus

for county, bonus in sorted(bonus_by_county.items(), key=lambda x: x[1], reverse=True):
    multiplied = bonus * rims_ii_multipliers['output_multiplier']
    print(f"  {county}: ${bonus/1e6:.2f}M direct -> ${multiplied/1e6:.2f}M total impact")
