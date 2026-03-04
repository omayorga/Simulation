import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# =============================================================================
# PHASE 18: MOBILITY VALUE SCORE (MVS) & COMPLETION GAP METRICS
# Source: Chetty et al. (2017) Opportunity Insights, College Scorecard
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 18: MOBILITY VALUE SCORE (MVS) & COMPLETION GAP")
print("=" * 80)

print(f"\n{'Institution':<30} {'Pell%':>6} {'Comp%':>6} {'MVS':>6} {'Comp Gap':>9} {'Mobility Bonus':>15}")
print("-" * 78)

mvs_rows = []
for inst, data in institution_mvs_data.items():
    # MVS = Pell share x completion rate x earnings premium factor (scaled 0-100)
    mvs = data['pell_share'] * data['completion_rate'] * data['earnings_premium_factor'] * 100

    # Expected completion rate given Pell share
    expected_completion = national_avg_completion * (1 - data['pell_share'] * pell_completion_penalty)
    completion_gap = data['completion_rate'] - expected_completion  # Positive = outperforming

    # Mobility bonus eligibility
    qualifies = data['pell_share'] >= 0.50 or data['type'] == 'HBCU'

    print(f"{inst:<30} {data['pell_share']*100:>5.0f}% {data['completion_rate']*100:>5.0f}% {mvs:>5.1f} "
          f"{completion_gap*100:>+7.1f}pp {'YES' if qualifies else 'no':>14}")

    mvs_rows.append({
        'Institution': inst,
        'Type': data['type'],
        'Pell_Share': data['pell_share'],
        'Completion_Rate': data['completion_rate'],
        'Expected_Completion': expected_completion,
        'Completion_Gap_pp': completion_gap * 100,
        'MVS_Score': mvs,
        'Mobility_Bonus_Eligible': qualifies
    })

df_mvs = pd.DataFrame(mvs_rows).sort_values('MVS_Score', ascending=False)
df_mvs.to_csv(OUTPUT_DIR / 'mobility_value_scores.csv', index=False)
print(f"\nSaved: mobility_value_scores.csv")

# MVS Visualization
try:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle('Phase 18: Mobility Value Score & Completion Gap by Institution', fontsize=14, fontweight='bold')

    sorted_mvs = df_mvs.sort_values('MVS_Score', ascending=True)
    colors_mvs = ['#E63946' if e else '#2E86AB' for e in sorted_mvs['Mobility_Bonus_Eligible']]
    ax1.barh(sorted_mvs['Institution'], sorted_mvs['MVS_Score'], color=colors_mvs, edgecolor='black', alpha=0.85)
    ax1.set_xlabel('Mobility Value Score')
    ax1.set_title('MVS (Pell × Completion × Earnings)', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#E63946', label='Mobility Bonus Eligible'),
                      Patch(facecolor='#2E86AB', label='Not Eligible')]
    ax1.legend(handles=legend_elements, fontsize=9)

    sorted_gap = df_mvs.sort_values('Completion_Gap_pp', ascending=True)
    colors_gap = ['#06D6A0' if g >= 0 else '#E63946' for g in sorted_gap['Completion_Gap_pp']]
    ax2.barh(sorted_gap['Institution'], sorted_gap['Completion_Gap_pp'], color=colors_gap, edgecolor='black', alpha=0.85)
    ax2.axvline(x=0, color='black', linewidth=1)
    ax2.set_xlabel('Completion Gap (pp vs Expected)')
    ax2.set_title('Completion Gap (+ = Outperforming)', fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig17_mvs_completion_gap.png', dpi=SAVE_DPI, bbox_inches='tight')
    plt.close()
    print("Saved: fig17_mvs_completion_gap.png")

except Exception as e:
    logger.error(f"Error generating Phase 18 visualizations: {e}")
    import traceback
    traceback.print_exc()
