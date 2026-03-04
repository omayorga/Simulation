"""Phase 1: Institutional Data
Pennsylvania Higher Education Economic Impact Analysis

Sources:
- Penn State, Pitt, Temple institutional reports
- PASSHE system data (passhe.edu)
- Community college data (pacommunitycolleges.org)
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ============================================================================
# PHASE 1: ACTUAL INSTITUTIONAL DATA
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1: INSTITUTIONAL DATA (Real-World Sources)")
print("=" * 80)

# -----------------------------------------------------------------------------
# 1.1 STATE-RELATED UNIVERSITIES (Actual Data)
# Sources: Institutional fact books, IPEDS, PA STAIR Reports
# -----------------------------------------------------------------------------

# Validate state-related data
for name, data in state_related_universities.items():
    validate_positive(data['enrollment'], f"{name} enrollment")
    validate_positive(data['state_appropriation'], f"{name} appropriation")
    if data['research_expenditures'] > data['operating_budget']:
        logger.warning(f"{name}: research exceeds operating budget")

# -----------------------------------------------------------------------------
# 1.2 PASSHE UNIVERSITIES (10 Universities - Fall 2025)
# Source: passhe.edu enrollment reports
# -----------------------------------------------------------------------------

print(f"\nPASSHE System Total Enrollment (Fall 2025): {passhe_total_enrollment:,}")
print(f"PASSHE System Total Employees: {passhe_total_employees:,}")
print(f"PASSHE Retention Rate: 81% (record high, above national average)")
print(f"PASSHE In-State Students: 89%")

# -----------------------------------------------------------------------------
# 1.3 COMMUNITY COLLEGES (14 Institutions)
# Source: collegetuitioncompare.com, pacommunitycolleges.org
# -----------------------------------------------------------------------------

print(f"\nCommunity College Total Enrollment: {cc_total_enrollment:,}")
print(f"Community College Total Employees: {cc_total_employees:,}")

# -----------------------------------------------------------------------------
# 1.4 RESEARCH EXPENDITURES DETAIL
# -----------------------------------------------------------------------------
print("\n" + "-" * 60)
print("RESEARCH EXPENDITURES (FY 2024-25)")
print("-" * 60)

print(f"Total PA State-Related Research: ${total_research/1e9:.2f}B")
for name, data in research_data.items():
    print(f"  {name}: ${data['total']/1e9:.2f}B")
