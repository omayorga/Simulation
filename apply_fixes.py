#!/usr/bin/env python3
"""Apply all 6 date-consistency fixes to PA_economic_impact."""
import sys, os

filepath = sys.argv[1] if len(sys.argv) > 1 else 'PA_economic_impact'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
fixes = []

# FIX 1: Normalize Phase 7 CPI base year
old1 = "3.67, 3.31, 3.12, 3.02, 2.90, 2.80, 2.75, 2.65, 2.55, 2.45,\n    2.32, 2.22, 2.16, 2.10, 2.05, 1.99, 1.93, 1.89, 1.86, 1.82,\n    1.76, 1.71, 1.69, 1.65, 1.61, 1.57, 1.52, 1.47, 1.42, 1.42,\n    1.39, 1.35, 1.33, 1.31, 1.29, 1.28, 1.27, 1.25, 1.22, 1.19,\n    1.18, 1.14, 1.04, 1.00, 1.03"
new1 = "3.56, 3.21, 3.03, 2.93, 2.82, 2.72, 2.67, 2.57, 2.48, 2.38,\n    2.25, 2.16, 2.10, 2.04, 1.99, 1.93, 1.87, 1.83, 1.81, 1.77,\n    1.71, 1.66, 1.64, 1.60, 1.56, 1.52, 1.48, 1.43, 1.38, 1.38,\n    1.35, 1.31, 1.29, 1.27, 1.25, 1.24, 1.23, 1.21, 1.18, 1.16,\n    1.15, 1.11, 1.01, 0.97, 1.00"
if old1 in content:
    content = content.replace(old1, new1)
    # Also fix the comment
    content = content.replace("# Source: BLS CPI-U, base 2024=1.0", "# Source: BLS CPI-U, normalized so 2024=1.0 (consistent with INFLATION_BASE_YEAR)")
    fixes.append("Fix 1: Normalized Phase 7 CPI base year to 2024")

# FIX 2: Add data_type column to historical_data
old2 = '0.021, 0.019, 0.015, 0.008, 0.024, 0.028, 0.015, 0.010, 0.012\n    ]\n}'
new2 = '0.021, 0.019, 0.015, 0.008, 0.024, 0.028, 0.015, 0.010, 0.012\n    ],\n    \'data_type\': [  # Distinguish actual observations from projections\n        \'actual\', \'actual\', \'actual\', \'actual\', \'actual\', \'actual\', \'actual\', \'actual\',\n        \'actual\', \'actual\', \'actual\', \'actual\', \'actual\', \'actual\', \'actual\',\n        \'projected\', \'projected\'\n    ]\n}'
if old2 in content:
    content = content.replace(old2, new2, 1)
    fixes.append("Fix 2: Added data_type column to historical_data")

# FIX 3: Add TUITION_BASE_YEAR constant
old3 = "INFLATION_BASE_YEAR = 2024\nPROJECTION_YEARS = 5"
new3 = "INFLATION_BASE_YEAR = 2024\nTUITION_BASE_YEAR = 2025  # Year from which tuition values in pa_resident_enrollment are sourced\nPROJECTION_YEARS = 5"
if old3 in content:
    content = content.replace(old3, new3)
    fixes.append("Fix 3a: Added TUITION_BASE_YEAR constant")

old3b = "# Current enrollment by sector (PA residents only)\npa_resident_enrollment = {"
new3b = "# Current enrollment by sector (PA residents only)\n# Tuition and enrollment figures are from TUITION_BASE_YEAR (AY 2024-25)\npa_resident_enrollment = {"
if old3b in content:
    content = content.replace(old3b, new3b)
    fixes.append("Fix 3b: Annotated pa_resident_enrollment")

# FIX 4: Parameterize recession years
old4 = "projected_recession_years = [\n    list(range(2030, 2032)),  # ~4 years after start\n    list(range(2039, 2041)),  # mid-cycle\n    list(range(2049, 2051)),  # 2050s downturn\n    list(range(2058, 2060)),  # late-cycle\n]\nrecession_year_set = set()\nfor period in projected_recession_years:\n    recession_year_set.update(period)"
new4 = "# Recession years parameterized from start_year (approx every 9-10 years, each lasting 2 years)\nrecession_offsets = [4, 5, 13, 14, 23, 24, 32, 33]  # Relative to start_year\nrecession_year_set = {start_year + offset for offset in recession_offsets}"
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append("Fix 4: Parameterized recession years")

# FIX 5: Add fiscal year reference note
old5 = "- EPI State of Working America - epi.org\n\"\"\"\n\nimport pandas"
fy_note = """- EPI State of Working America - epi.org\n\"\"\"\n\n# NOTE ON FISCAL YEAR REFERENCES:\n# - \"FY2024-25\" refers to Academic Year 2024-2025 (institutional reports)\n# - \"FY2024\" refers to State Fiscal Year ending June 30, 2024 (SHEEO, state budget)\n# - \"FY2025\" refers to State Fiscal Year ending June 30, 2025 (federal agency reports)\n# All dollar amounts are normalized to INFLATION_BASE_YEAR (2024) real dollars unless noted.\n\nimport pandas"""
if old5 in content:
    content = content.replace(old5, fy_note)
    fixes.append("Fix 5: Added fiscal year reference note")

# FIX 6: Update docstring date
if "Updated: February 18, 2026" in content:
    content = content.replace("Updated: February 18, 2026", "Updated: March 3, 2026")
    fixes.append("Fix 6: Updated docstring date")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Applied {len(fixes)} fixes:")
for fix in fixes:
    print(f"  ✓ {fix}")