import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 11: FULL COST OF ATTENDANCE (COA) MODELING
# Source: Blue Collar proposal — non-tuition costs > 50% of total cost
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 11: FULL COST OF ATTENDANCE (COA) MODELING")
print("Non-tuition costs: housing, food, transportation, books")
print("=" * 80)

print(f"\nNon-Tuition Cost of Attendance:")
print(f"  Four-Year: ${non_tuition_coa['four_year']['total']:,}/year")
print(f"  Two-Year:  ${non_tuition_coa['two_year']['total']:,}/year")
print(f"  Pell-Eligible Share: {pell_share*100:.0f}%")
print(f"  Stipend Coverage Rate: {coa_stipend_coverage*100:.0f}%")

# 11.2 Run COA-adjusted simulation (40-year)
cum_tuition_only_cost = 0
cum_coa_stipend_cost = 0
cum_total_coa_cost = 0

for i in range(40):
    year = start_year + i
    cpi_factor = (1 + inflation_rate) ** (year - INFLATION_BASE_YEAR)
    tuition_factor = (1 + tuition_growth_rate) ** (year - start_year)

    annual_tuition_cost = 0
    annual_coa_stipend = 0
    annual_emergency_cost = 0

    for inst, data in pa_resident_enrollment.items():
        pa_students = int(data['total'] * data['in_state_pct'])
        boost = enrollment_boost.get(inst, 0.10)
        ramp = min(1.0, 0.5 + 0.25 * i) if i < 2 else 1.0
        new_students = int(pa_students * boost * ramp)
        total_students = pa_students + new_students

        # Tuition cost
        tuition_adjusted = data['tuition'] * tuition_factor
        annual_tuition_cost += total_students * tuition_adjusted

        # COA stipend for Pell students
        sector = sector_type[inst]
        coa_amount = non_tuition_coa[sector]['total'] * cpi_factor
        pell_students = int(total_students * pell_share)
        annual_coa_stipend += pell_students * coa_amount * coa_stipend_coverage

        # Emergency grants
        emergency_students = int(pell_students * emergency_grant_eligibility)
        annual_emergency_cost += emergency_students * emergency_grant_per_student * cpi_factor

    cum_tuition_only_cost += annual_tuition_cost / cpi_factor
    cum_coa_stipend_cost += annual_coa_stipend / cpi_factor
    cum_total_coa_cost += (annual_tuition_cost + annual_coa_stipend + annual_emergency_cost) / cpi_factor

# Additional graduates from emergency grants
emergency_additional_grads_40yr = int(
    total_pa_residents * pell_share * emergency_grant_eligibility * completion_boost_emergency * 40
)
emergency_additional_earnings = emergency_additional_grads_40yr * lifetime_earnings_premium['bachelor'] / 2
emergency_total_cost_40yr = cum_total_coa_cost - cum_tuition_only_cost - cum_coa_stipend_cost

print(f"\n--- 40-YEAR COST COMPARISON ---")
print(f"  Tuition-Only State Cost:          ${cum_tuition_only_cost/1e9:.2f}B")
print(f"  COA Stipend Cost (Pell students):  ${cum_coa_stipend_cost/1e9:.2f}B")
print(f"  Emergency Grant Fund Cost:         ${(cum_total_coa_cost - cum_tuition_only_cost - cum_coa_stipend_cost)/1e9:.2f}B")
print(f"  TOTAL with Full COA:               ${cum_total_coa_cost/1e9:.2f}B")
print(f"  Increase over tuition-only:        {((cum_total_coa_cost/cum_tuition_only_cost)-1)*100:.1f}%")
print(f"\n--- EMERGENCY GRANT IMPACT ---")
print(f"  Additional graduates (40yr):       {emergency_additional_grads_40yr:,}")
print(f"  Additional lifetime earnings:      ${emergency_additional_earnings/1e9:.2f}B")

# Save COA comparison
df_coa = pd.DataFrame([
    {'Scenario': 'Tuition Only', 'Cost_40yr_B': cum_tuition_only_cost/1e9},
    {'Scenario': 'Tuition + COA Stipend', 'Cost_40yr_B': (cum_tuition_only_cost + cum_coa_stipend_cost)/1e9},
    {'Scenario': 'Full COA + Emergency Grants', 'Cost_40yr_B': cum_total_coa_cost/1e9}
])
df_coa.to_csv(OUTPUT_DIR / 'coa_modeling_comparison.csv', index=False)
print(f"\nSaved: coa_modeling_comparison.csv")

# COA Visualization
try:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Phase 11: Full Cost of Attendance Modeling (40-Year)', fontsize=14, fontweight='bold')

    scenarios = ['Tuition\nOnly', 'Tuition +\nCOA Stipend', 'Full COA +\nEmergency']
    costs_coa = [cum_tuition_only_cost/1e9,
                 (cum_tuition_only_cost + cum_coa_stipend_cost)/1e9,
                 cum_total_coa_cost/1e9]
    colors_coa = ['#2E86AB', '#F18F01', '#E63946']
    ax1.bar(scenarios, costs_coa, color=colors_coa, edgecolor='black', alpha=0.85)
    ax1.set_ylabel('40-Year State Cost ($ Billion, 2024$)')
    ax1.set_title('Total State Cost by Scenario', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    for i, val in enumerate(costs_coa):
        ax1.text(i, val + 1, f'${val:.1f}B', ha='center', fontweight='bold', fontsize=11)

    # Breakdown pie
    breakdown = [cum_tuition_only_cost/1e9, cum_coa_stipend_cost/1e9,
                 (cum_total_coa_cost - cum_tuition_only_cost - cum_coa_stipend_cost)/1e9]
    labels_pie = ['Tuition Coverage', 'COA Stipends\n(Pell Students)', 'Emergency Grants']
    ax2.pie(breakdown, labels=labels_pie, autopct='%1.1f%%', startangle=90,
            colors=['#2E86AB', '#F18F01', '#E63946'],
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('Cost Breakdown (Full COA Scenario)', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig16_coa_modeling.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig16_coa_modeling.png")

except Exception as e:
    logger.error(f"Error generating Phase 11 visualizations: {e}")
    import traceback
    traceback.print_exc()
