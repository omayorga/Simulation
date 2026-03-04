"""Phase 4: County-Level Economic Impact Analysis
Pennsylvania Higher Education Economic Impact Analysis

Sources:
- BEA RIMS II Multipliers (bea.gov)
- Institutional enrollment & employee data
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# PHASE 4: COUNTY-LEVEL ECONOMIC IMPACT ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: COUNTY-LEVEL ECONOMIC IMPACT ANALYSIS")
print("=" * 80)

# Build county-level aggregation from all institutions
county_impact = {}

# Add state-related universities
for name, data in state_related_universities.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['operating_budget']

# Add PASSHE universities
for name, data in passhe_universities.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['enrollment'] * 15000  # Est. per-student spending

# Add community colleges
for name, data in community_colleges.items():
    county = data['county']
    if county not in county_impact:
        county_impact[county] = {'enrollment': 0, 'employees': 0, 'institutions': [], 'spending': 0}
    county_impact[county]['enrollment'] += data['enrollment']
    county_impact[county]['employees'] += data['employees']
    county_impact[county]['institutions'].append(name)
    county_impact[county]['spending'] += data['enrollment'] * 10000  # Est. per-student spending

# Calculate county-level economic impact
for county, data in county_impact.items():
    data['direct_impact'] = data['spending']
    data['total_impact'] = data['spending'] * rims_ii_multipliers['output_multiplier']
    data['jobs_supported'] = int(data['employees'] * 1.8)  # Direct + indirect
    data['student_spending'] = data['enrollment'] * avg_student_spending * 0.65

# Create county DataFrame
df_county = pd.DataFrame([
    {
        'County': county,
        'Enrollment': data['enrollment'],
        'Employees': data['employees'],
        'Institutions': len(data['institutions']),
        'Direct_Impact_M': data['direct_impact'] / 1e6,
        'Total_Impact_M': data['total_impact'] / 1e6,
        'Jobs_Supported': data['jobs_supported'],
        'Student_Spending_M': data['student_spending'] / 1e6
    }
    for county, data in county_impact.items()
]).sort_values('Total_Impact_M', ascending=False)

print("\nTop 10 Counties by Economic Impact:")
print(f"{'County':<18} {'Enrollment':>10} {'Employees':>10} {'Impact ($M)':>12} {'Jobs':>8}")
print("-" * 62)
for _, row in df_county.head(10).iterrows():
    print(f"{row['County']:<18} {row['Enrollment']:>10,} {row['Employees']:>10,} ${row['Total_Impact_M']:>10,.0f}M {row['Jobs_Supported']:>7,}")

df_county.to_csv(OUTPUT_DIR / 'county_economic_impact.csv', index=False)
print(f"\nSaved: county_economic_impact.csv")

# Exclude statistical outliers (Penn State UP and Pitt) for messaging-focused analysis
df_county_no_bigflagships = df_county[~df_county['County'].isin(['Centre', 'Allegheny'])]
df_county_no_bigflagships.to_csv(OUTPUT_DIR / 'county_economic_impact_no_flagships.csv', index=False)
print("\nSaved: county_economic_impact_no_flagships.csv (excludes Penn State UP and Pitt)")
