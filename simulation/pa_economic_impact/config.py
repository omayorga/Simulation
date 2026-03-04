"""Pennsylvania Higher Education Economic Impact Analysis — Shared Configuration

This module contains ALL constants, data dictionaries, helper functions, and imports
shared across all phase files. Each phase imports from this file so it can run independently.

Author: Oscar J. Mayorga
Updated: March 3, 2026
Repository: github.com/omayorga/Simulation

Data Sources:
- Penn State Research: $1.44B (FY2024-25) - psu.edu
- Pitt Research: $1.25B (FY2025) - research.pitt.edu
- Temple Factbook 2024-2025 - ira.temple.edu
- PASSHE Enrollment: 83,000 (Fall 2025) - passhe.edu
- SHEEO SHEF FY2024 Report - shef.sheeo.org
- BLS Employment Data - bls.gov
- Census Population Estimates - census.gov
- BEA RIMS II Multipliers - bea.gov
- EPI State of Working America - epi.org
"""

# NOTE ON FISCAL YEAR REFERENCES:
# - "FY2024-25" refers to Academic Year 2024-2025 (institutional reports)
# - "FY2024" refers to State Fiscal Year ending June 30, 2024 (SHEEO, state budget)
# - "FY2025" refers to State Fiscal Year ending June 30, 2025 (federal agency reports)
# All dollar amounts are normalized to INFLATION_BASE_YEAR (2024) real dollars unless noted.

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
from pathlib import Path
from datetime import datetime
import warnings
import sys
import os
import logging

warnings.filterwarnings('ignore')

# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# OUTPUT DIRECTORY
# =============================================================================
DEFAULT_OUTPUT_DIR = os.environ.get('PA_ECON_OUTPUT_DIR', 'pa_output')
OUTPUT_DIR = Path(DEFAULT_OUTPUT_DIR)
try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    logger.error(f"Cannot create output directory: {e}")
    sys.exit(1)

# =============================================================================
# PLOTTING DEFAULTS
# =============================================================================
# Note: seaborn grid styling disabled for compatibility with large multi-panel
# figures at high DPI. Grid lines are added manually per-axis instead.
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['figure.dpi'] = 150
# Use 150 DPI for saving (overridden per-chart if needed)
SAVE_DPI = 150

# =============================================================================
# GLOBAL ANALYSIS PARAMETERS
# =============================================================================
INFLATION_BASE_YEAR = 2024
TUITION_BASE_YEAR = 2025  # Year from which tuition values in pa_resident_enrollment are sourced
PROJECTION_YEARS = 5
MONTE_CARLO_SIMULATIONS = 10000
RANDOM_SEED = 42
EXCLUDE_FLAGSHIPS = True  # When True, rerun Phases 1-3 without Penn State and Pitt

# =============================================================================
# DATA VALIDATION HELPERS
# =============================================================================

def validate_data_lengths(data_dict, expected_length=None):
    """Validate that all list values in a dictionary have the same length."""
    lengths = {k: len(v) for k, v in data_dict.items() if isinstance(v, list)}
    if not lengths:
        return True
    unique_lengths = set(lengths.values())
    if len(unique_lengths) > 1:
        logger.error(f"Inconsistent data lengths: {lengths}")
        return False
    if expected_length and list(unique_lengths)[0] != expected_length:
        logger.error(f"Expected length {expected_length}, got {list(unique_lengths)[0]}")
        return False
    return True

def validate_positive(value, name):
    """Validate that a value is positive."""
    if value <= 0:
        logger.warning(f"{name} has non-positive value: {value}")
        return False
    return True

# =============================================================================
# PHASE 1 DATA: INSTITUTIONAL DATA
# =============================================================================

# 1.1 State-Related Universities
state_related_universities = {
    'Penn State': {
        'enrollment': 88000,
        'employees': 17378,
        'faculty': 4838,
        'research_expenditures': 1.44e9,
        'operating_budget': 7.7e9,
        'state_appropriation': 242.1e6,
        'tuition_revenue': 2.8e9,
        'county': 'Centre',
        'campuses': 24,
        'avg_faculty_salary': 100357,
        'avg_staff_salary': 66773
    },
    'University of Pittsburgh': {
        'enrollment': 34525,
        'employees': 14731,
        'faculty': 5332,
        'research_expenditures': 1.25e9,
        'operating_budget': 2.7e9,
        'state_appropriation': 151.5e6,
        'tuition_revenue': 850e6,
        'county': 'Allegheny',
        'campuses': 5,
        'avg_faculty_salary': 99887,
        'avg_staff_salary': 66190
    },
    'Temple University': {
        'enrollment': 32777,
        'employees': 7257,
        'faculty': 3452,
        'research_expenditures': 280e6,
        'operating_budget': 1.23e9,
        'state_appropriation': 158.2e6,
        'tuition_revenue': 650e6,
        'county': 'Philadelphia',
        'campuses': 8,
        'avg_faculty_salary': 95000,
        'avg_staff_salary': 58000
    },
    'Lincoln University': {
        'enrollment': 2101,
        'employees': 350,
        'faculty': 95,
        'research_expenditures': 8e6,
        'operating_budget': 75e6,
        'state_appropriation': 16.4e6,
        'tuition_revenue': 25e6,
        'county': 'Chester',
        'campuses': 1,
        'avg_faculty_salary': 75000,
        'avg_staff_salary': 48000
    }
}

# 1.2 PASSHE Universities
passhe_universities = {
    'West Chester University': {'enrollment': 17400, 'employees': 2100, 'county': 'Chester', 'change_2025': 1.2},
    'Indiana University of PA': {'enrollment': 9200, 'employees': 1400, 'county': 'Indiana', 'change_2025': 0.0},
    'Slippery Rock University': {'enrollment': 8500, 'employees': 1200, 'county': 'Butler', 'change_2025': 2.75},
    'Kutztown University': {'enrollment': 7800, 'employees': 1100, 'county': 'Berks', 'change_2025': -1.5},
    'Shippensburg University': {'enrollment': 5800, 'employees': 900, 'county': 'Cumberland', 'change_2025': 2.6},
    'East Stroudsburg University': {'enrollment': 5500, 'employees': 850, 'county': 'Monroe', 'change_2025': 4.4},
    'Millersville University': {'enrollment': 7200, 'employees': 1000, 'county': 'Lancaster', 'change_2025': 1.3},
    'Bloomsburg University': {'enrollment': 7500, 'employees': 1050, 'county': 'Columbia', 'change_2025': -2.0},
    'Lock Haven University': {'enrollment': 3200, 'employees': 500, 'county': 'Clinton', 'change_2025': -3.0},
    'Cheyney University': {'enrollment': 900, 'employees': 200, 'county': 'Delaware', 'change_2025': 37.9}
}

# 1.3 Community Colleges
community_colleges = {
    'Harrisburg Area CC': {'enrollment': 12880, 'county': 'Dauphin', 'employees': 650},
    'CC of Philadelphia': {'enrollment': 18710, 'county': 'Philadelphia', 'employees': 1200},
    'CC of Allegheny County': {'enrollment': 10451, 'county': 'Allegheny', 'employees': 580},
    'Montgomery County CC': {'enrollment': 8895, 'county': 'Montgomery', 'employees': 520},
    'Northampton County CC': {'enrollment': 8695, 'county': 'Northampton', 'employees': 480},
    'Delaware County CC': {'enrollment': 7638, 'county': 'Delaware', 'employees': 420},
    'Lehigh Carbon CC': {'enrollment': 6385, 'county': 'Lehigh', 'employees': 380},
    'Bucks County CC': {'enrollment': 6098, 'county': 'Bucks', 'employees': 360},
    'Reading Area CC': {'enrollment': 4788, 'county': 'Berks', 'employees': 280},
    'Luzerne County CC': {'enrollment': 4315, 'county': 'Luzerne', 'employees': 260},
    'Westmoreland County CC': {'enrollment': 4200, 'county': 'Westmoreland', 'employees': 250},
    'Butler County CC': {'enrollment': 3500, 'county': 'Butler', 'employees': 200},
    'Beaver County CC': {'enrollment': 2200, 'county': 'Beaver', 'employees': 150},
    'Pennsylvania Highlands CC': {'enrollment': 2100, 'county': 'Cambria', 'employees': 140}
}

# 1.4 Research Expenditures Detail
research_data = {
    'Penn State': {
        'total': 1.44e9,
        'federal': 922.6e6,
        'nsf': 93e6,
        'hhs': 216.6e6,
        'dod': 416.5e6,
        'source': 'Penn State Research Annual Report FY24-25'
    },
    'University of Pittsburgh': {
        'total': 1.25e9,
        'federal': 850e6,
        'growth_5yr': 0.30,
        'source': 'Pitt Research Annual Report FY2024'
    },
    'Temple University': {
        'total': 280e6,
        'source': 'Temple Factbook (HERD estimate)'
    }
}

# =============================================================================
# DERIVED PHASE 1 AGGREGATES
# =============================================================================
passhe_total_enrollment = sum(u['enrollment'] for u in passhe_universities.values())
passhe_total_employees = sum(u['employees'] for u in passhe_universities.values())
cc_total_enrollment = sum(c['enrollment'] for c in community_colleges.values())
cc_total_employees = sum(c['employees'] for c in community_colleges.values())
total_research = sum(r['total'] for r in research_data.values())

total_enrollment_all = (
    sum(u['enrollment'] for u in state_related_universities.values()) +
    passhe_total_enrollment +
    cc_total_enrollment
)

# =============================================================================
# PHASE 2 DATA: ECONOMIC MULTIPLIERS & EMPLOYMENT
# =============================================================================

# BEA RIMS II Multipliers (Pennsylvania-specific)
rims_ii_multipliers = {
    'output_multiplier': 1.91,
    'employment_multiplier': 11.8,
    'earnings_multiplier': 0.58,
    'value_added_multiplier': 0.95
}

spending_multipliers = {
    'institutional': 2.20,
    'payroll': 1.65,
    'student': 1.45,
    'construction': 2.85,
    'research': 2.40
}

# Employment by Sector
employment_sectors = {
    'Faculty (Instructional)': {'count': 15717, 'avg_salary': 95000, 'benefits_rate': 0.32},
    'Research Staff': {'count': 8500, 'avg_salary': 72000, 'benefits_rate': 0.30},
    'Administration': {'count': 12000, 'avg_salary': 68000, 'benefits_rate': 0.30},
    'Support Staff': {'count': 18000, 'avg_salary': 48000, 'benefits_rate': 0.28},
    'Facilities/Maintenance': {'count': 6500, 'avg_salary': 45000, 'benefits_rate': 0.28},
    'Healthcare (Medical Schools)': {'count': 4200, 'avg_salary': 125000, 'benefits_rate': 0.32},
    'Student Workers': {'count': 25000, 'avg_salary': 12000, 'benefits_rate': 0.05}
}

# Student Off-Campus Spending
student_spending_categories = {
    'Housing (off-campus)': 8500,
    'Food & Groceries': 3200,
    'Transportation': 2400,
    'Entertainment': 1800,
    'Personal/Healthcare': 1200,
    'Books/Supplies': 1100,
    'Clothing': 800,
    'Miscellaneous': 600
}

avg_student_spending = sum(student_spending_categories.values())

# Monte Carlo parameter distributions
param_distributions = {
    'enrollment_elasticity': (-0.037, 0.015),
    'output_multiplier': (1.91, 0.20),
    'employment_multiplier': (11.8, 1.5),
    'student_spending': (avg_student_spending, 2000),
    'retention_rate': (0.81, 0.03)
}

# =============================================================================
# DERIVED PHASE 2 AGGREGATES
# =============================================================================
total_direct_employment = sum(s['count'] for s in employment_sectors.values())
total_payroll = sum(s['count'] * s['avg_salary'] * (1 + s['benefits_rate'])
                    for s in employment_sectors.values())

indirect_employment = int(total_direct_employment * 0.45)
induced_employment = int(total_direct_employment * 0.35)
total_jobs_supported = total_direct_employment + indirect_employment + induced_employment

total_student_spending = total_enrollment_all * avg_student_spending * 0.65

base_direct_spending = 12.5e9

# =============================================================================
# PHASE 3 DATA: HISTORICAL TRENDS, BRAIN DRAIN, POLICY SCENARIOS
# =============================================================================

historical_data = {
    'year': list(range(2010, 2027)),
    'state_appropriation_nominal': [
        580, 390, 395, 400, 410, 420, 435, 450, 468, 487,
        502, 520, 545, 568, 590, 610, 635
    ],
    'passhe_enrollment': [
        119513, 118500, 115000, 112000, 108000, 104000, 100000,
        96000, 92000, 88000, 85000, 83500, 82500, 82000, 82500, 83000, 83000
    ],
    'state_related_enrollment': [
        147000, 148000, 150000, 152000, 154000, 155000, 156000,
        157000, 157500, 157000, 156500, 156000, 156500, 157000, 157403, 157403, 157403
    ],
    'tuition_avg_public': [
        9500, 10200, 11000, 11800, 12500, 13200, 13800, 14300,
        14700, 15000, 15200, 15400, 15600, 15800, 16000, 16200, 16500
    ],
    'cpi_adjustment': [
        0.72, 0.74, 0.76, 0.77, 0.78, 0.78, 0.79, 0.81,
        0.83, 0.85, 0.86, 0.90, 0.97, 1.00, 1.034, 1.06, 1.085
    ],
    'real_wage_growth': [
        -0.003, 0.002, 0.005, 0.002, 0.008, 0.012, 0.015, 0.018,
        0.021, 0.019, 0.015, 0.008, 0.024, 0.028, 0.015, 0.010, 0.012
    ],
    'data_type': [
        'actual', 'actual', 'actual', 'actual', 'actual', 'actual', 'actual', 'actual',
        'actual', 'actual', 'actual', 'actual', 'actual', 'actual', 'actual',
        'projected', 'projected'
    ]
}

# Brain drain data
brain_drain_data = {
    'stay_in_county': 0.42,
    'stay_in_pa': 0.68,
    'leave_pa': 0.32,
    'planning_to_leave': 0.40,
    'uncertain': 0.33,
    'pa_rank_retention': 42
}

grad_earnings_premium = 32000

# Policy scenarios
policy_scenarios = {
    'Baseline': {'appropriation_change': 0.0, 'tuition_change': 0.03, 'enrollment_change': 0.0, 'description': 'Current trajectory'},
    'Tuition Freeze': {'appropriation_change': 0.05, 'tuition_change': 0.0, 'enrollment_change': 0.02, 'description': 'Freeze tuition, increase state funding'},
    'PASSHE Reinvestment': {'appropriation_change': 0.15, 'tuition_change': -0.05, 'enrollment_change': 0.05, 'description': 'Major state investment'},
    'Free Community College': {'appropriation_change': 0.25, 'tuition_change': -1.0, 'enrollment_change': 0.15, 'description': 'Eliminate CC tuition'},
    'Austerity': {'appropriation_change': -0.10, 'tuition_change': 0.08, 'enrollment_change': -0.03, 'description': 'Further state funding cuts'}
}

base_economic_impact = 25e9

# Total state appropriation
total_state_appropriation = (
    sum(u['state_appropriation'] for u in state_related_universities.values()) +
    172.9e6  # PASSHE appropriation
)

# =============================================================================
# PHASE 3 ROI DATA
# =============================================================================
economic_impact_components = {
    'institutional_spending': 8.5e9,
    'payroll_impact': total_payroll * spending_multipliers['payroll'],
    'student_spending_impact': total_student_spending * spending_multipliers['student'],
    'research_impact': total_research * spending_multipliers['research'],
    'construction_impact': 1.2e9 * spending_multipliers['construction']
}

total_economic_impact = sum(economic_impact_components.values())
roi_ratio = total_economic_impact / total_state_appropriation
tax_revenue_generated = total_economic_impact * 0.04

# =============================================================================
# PHASE 6 DATA: FREE COLLEGE SIMULATION
# =============================================================================

# PA resident enrollment by sector
pa_resident_enrollment = {
    'PASSHE': {'total': 83000, 'in_state_pct': 0.89, 'tuition': 7994},
    'Penn State': {'total': 86557, 'in_state_pct': 0.61, 'tuition': 21098},
    'Pitt': {'total': 34525, 'in_state_pct': 0.72, 'tuition': 21080},
    'Temple': {'total': 32777, 'in_state_pct': 0.79, 'tuition': 19882},
    'Lincoln': {'total': 2101, 'in_state_pct': 0.45, 'tuition': 11380},
    'Community Colleges': {'total': 100855, 'in_state_pct': 0.97, 'tuition': 6170}
}

# Enrollment boost assumptions (based on Tennessee Promise)
enrollment_boost = {
    'Community Colleges': 0.25,
    'PASSHE': 0.15,
    'Penn State': 0.08,
    'Pitt': 0.08,
    'Temple': 0.10,
    'Lincoln': 0.20
}

# Sector type mapping
sector_type = {
    'Community Colleges': 'two_year',
    'PASSHE': 'four_year',
    'Penn State': 'four_year',
    'Pitt': 'four_year',
    'Temple': 'four_year',
    'Lincoln': 'four_year'
}

# Brain drain parameters for free college
brain_drain_baseline = 0.32
brain_drain_free_college = 0.22

# Lifetime earnings premiums (Georgetown CEW, inflation-adjusted to 2024$)
lifetime_earnings_premium = {
    'associate': 495000,
    'bachelor': 1000000,
    'graduate': 1500000
}

# Tax and fiscal parameters
pa_state_income_tax = 0.0307
pa_local_tax_avg = 0.02
federal_tax_effective = 0.15
sales_tax_rate = 0.06

# Fiscal benefit per degree (APLU research)
net_fiscal_benefit_bachelor = 355000
net_fiscal_benefit_associate = 150000

# Degree completion rates
completion_rates = {
    'community_college_current': 0.28,
    'community_college_free': 0.34,
    'four_year_current': 0.62,
    'four_year_free': 0.68
}

# Inflation assumptions
inflation_rate = 0.025
tuition_growth_rate = 0.03
wage_growth_real = 0.012

# Simulation parameters
simulation_horizons = [5, 10, 20, 40]
start_year = 2026

# Federal matching ratios
federal_match_ratios = [1, 3, 5]

# Total PA residents
total_pa_residents = sum(
    int(data['total'] * data['in_state_pct'])
    for data in pa_resident_enrollment.values()
)

# Total tuition cost to state (Year 1)
total_tuition_cost_to_state = sum(
    int(data['total'] * data['in_state_pct']) * data['tuition']
    for data in pa_resident_enrollment.values()
)

state_tax_rate = 0.0307

# =============================================================================
# PHASE 7 DATA: COUNTERFACTUAL
# =============================================================================
counterfactual_data = {
    'year': list(range(1980, 2025)),
    'pa_actual_nominal': [
        680, 700, 650, 660, 680, 710, 740, 760, 790, 820,
        850, 830, 810, 820, 840, 860, 880, 900, 920, 950,
        1000, 1050, 950, 900, 880, 890, 920, 950, 920, 700,
        580, 390, 395, 400, 410, 420, 435, 450, 468, 487,
        502, 520, 545, 568, 590
    ],
    'cpi_to_2024': [
        3.56, 3.21, 3.03, 2.93, 2.82, 2.72, 2.67, 2.57, 2.48, 2.38,
        2.25, 2.16, 2.10, 2.04, 1.99, 1.93, 1.87, 1.83, 1.81, 1.77,
        1.71, 1.66, 1.64, 1.60, 1.56, 1.52, 1.48, 1.43, 1.38, 1.38,
        1.35, 1.31, 1.29, 1.27, 1.25, 1.24, 1.23, 1.21, 1.18, 1.16,
        1.15, 1.11, 1.01, 0.97, 1.00
    ],
    'pa_enrollment_total': [
        380000, 385000, 390000, 395000, 398000, 400000, 402000, 405000, 408000, 410000,
        412000, 415000, 418000, 420000, 422000, 420000, 418000, 416000, 414000, 412000,
        410000, 408000, 405000, 400000, 395000, 390000, 385000, 382000, 380000, 378000,
        375000, 370000, 365000, 360000, 355000, 350000, 348000, 345000, 342000, 340000,
        338000, 336000, 334000, 332000, 340000
    ]
}

# Counterfactual parameters
funding_enrollment_elasticity = 0.35

# =============================================================================
# PHASE 8 DATA: LIMITATIONS
# =============================================================================

# Dynamic feedback parameters
elasticity_of_substitution = 3.0
current_college_share_pa = 0.35
current_wage_premium = 0.89
feedback_horizons = [10, 20, 40]

# Crowding-out parameters
pa_general_fund_2024 = 45.5e9
higher_ed_share_current = 0.09
medicaid_share_current = 0.28
k12_share_current = 0.38
other_program_multiplier = 1.50

crowding_scenarios = {
    'No crowding out (new revenue)': {'description': 'Funded entirely by new revenue or federal aid', 'crowding_factor': 0.0},
    'Partial crowding out (25%)': {'description': '25% comes from other programs (education, infrastructure)', 'crowding_factor': 0.25},
    'Moderate crowding out (50%)': {'description': '50% displaces other state spending', 'crowding_factor': 0.50},
    'High crowding out (75%)': {'description': '75% displaces other state spending', 'crowding_factor': 0.75}
}

# Private sector data (AICUP FY2024)
private_sector_data = {
    'institutions': 80,
    'total_enrollment': 279000,
    'total_employees': 195120,
    'economic_impact': 29e9,
    'impact_with_hospitals': 65.6e9,
    'state_local_taxes': 1.5e9,
    'student_spending': 5.3e9,
    'degrees_conferred': 77000,
    'source': 'AICUP Economic Impact Report FY2024'
}

major_private_institutions = {
    'University of Pennsylvania': {'enrollment': 28711, 'county': 'Philadelphia'},
    'Drexel University': {'enrollment': 21703, 'county': 'Philadelphia'},
    'Carnegie Mellon University': {'enrollment': 15596, 'county': 'Allegheny'},
    'Villanova University': {'enrollment': 10111, 'county': 'Delaware'},
    'Thomas Jefferson University': {'enrollment': 8315, 'county': 'Philadelphia'},
    'Duquesne University': {'enrollment': 8137, 'county': 'Allegheny'},
    'Lehigh University': {'enrollment': 7590, 'county': 'Northampton'},
    "Saint Joseph's University": {'enrollment': 7201, 'county': 'Philadelphia'},
}

# Correlated Monte Carlo economic states
economic_states = {
    'Expansion': {'probability': 0.35, 'multiplier_shift': 0.15, 'spending_shift': 0.10, 'enrollment_shift': 0.03},
    'Normal': {'probability': 0.40, 'multiplier_shift': 0.0, 'spending_shift': 0.0, 'enrollment_shift': 0.0},
    'Recession': {'probability': 0.25, 'multiplier_shift': -0.20, 'spending_shift': -0.15, 'enrollment_shift': 0.02}
}

# =============================================================================
# PHASE 9 DATA: DEMOGRAPHICS
# =============================================================================

demographic_shares = {
    'race': {
        'White': 0.60, 'Black': 0.12, 'Hispanic': 0.10,
        'Asian': 0.07, 'Other/Multiracial': 0.11
    },
    'gender': {'Female': 0.57, 'Male': 0.43},
    'first_gen': {'First-Generation': 0.33, 'Continuing-Generation': 0.67},
    'income': {'Low-Income (Pell)': 0.40, 'Middle-Income': 0.35, 'Upper-Income': 0.25}
}

completion_rate_multipliers = {
    'race': {
        'White': {'cc': 1.07, 'four_yr': 1.05},
        'Black': {'cc': 0.71, 'four_yr': 0.68},
        'Hispanic': {'cc': 0.82, 'four_yr': 0.75},
        'Asian': {'cc': 1.14, 'four_yr': 1.15},
        'Other/Multiracial': {'cc': 0.96, 'four_yr': 0.93}
    },
    'gender': {
        'Female': {'cc': 1.08, 'four_yr': 1.07},
        'Male': {'cc': 0.91, 'four_yr': 0.92}
    },
    'first_gen': {
        'First-Generation': {'cc': 0.80, 'four_yr': 0.75},
        'Continuing-Generation': {'cc': 1.10, 'four_yr': 1.12}
    },
    'income': {
        'Low-Income (Pell)': {'cc': 0.78, 'four_yr': 0.72},
        'Middle-Income': {'cc': 1.05, 'four_yr': 1.05},
        'Upper-Income': {'cc': 1.20, 'four_yr': 1.22}
    }
}

free_college_boost_by_group = {
    'race': {'White': 0.05, 'Black': 0.08, 'Hispanic': 0.08, 'Asian': 0.04, 'Other/Multiracial': 0.06},
    'gender': {'Female': 0.06, 'Male': 0.06},
    'first_gen': {'First-Generation': 0.09, 'Continuing-Generation': 0.04},
    'income': {'Low-Income (Pell)': 0.10, 'Middle-Income': 0.06, 'Upper-Income': 0.03}
}

# =============================================================================
# PHASE 11 DATA: COST OF ATTENDANCE
# =============================================================================
non_tuition_coa = {
    'four_year': {
        'housing': 8500, 'food': 4000, 'transportation': 2000,
        'books_supplies': 1200, 'personal': 1800, 'total': 17500
    },
    'two_year': {
        'housing': 6000, 'food': 3500, 'transportation': 2500,
        'books_supplies': 1000, 'personal': 1500, 'total': 14500
    }
}

pell_share = 0.40
coa_stipend_coverage = 0.60
emergency_grant_per_student = 750
emergency_grant_eligibility = 0.15
completion_boost_emergency = 0.025

# =============================================================================
# PHASE 13 DATA: COUNTER-CYCLICAL MATCHING
# =============================================================================
recession_offsets = [4, 5, 13, 14, 23, 24, 32, 33]
recession_year_set = {start_year + offset for offset in recession_offsets}
base_ratios = [3, 5]
recession_ratio = 9

# =============================================================================
# PHASE 15 DATA: MOBILITY BONUS
# =============================================================================
mobility_bonus_institutions = {
    'Lincoln': {'type': 'HBCU', 'pell_share': 0.85, 'enrollment': 2101, 'county': 'Chester'},
    'Cheyney University': {'type': 'HBCU', 'pell_share': 0.80, 'enrollment': 900, 'county': 'Delaware'},
    'CC of Philadelphia': {'type': 'High-Pell CC', 'pell_share': 0.65, 'enrollment': 18710, 'county': 'Philadelphia'},
    'Reading Area CC': {'type': 'High-Pell CC', 'pell_share': 0.58, 'enrollment': 4788, 'county': 'Berks'},
    'Luzerne County CC': {'type': 'High-Pell CC', 'pell_share': 0.55, 'enrollment': 4315, 'county': 'Luzerne'},
    'East Stroudsburg University': {'type': 'High-Pell PASSHE', 'pell_share': 0.52, 'enrollment': 5500, 'county': 'Monroe'},
}
mobility_bonus_rate = 0.20

# =============================================================================
# PHASE 16 DATA: EQUITY MATCH
# =============================================================================
pa_gdp_per_capita = 67000
national_median_gdp_per_capita = 65000

# =============================================================================
# PHASE 17 DATA: FEDERAL REVENUE MECHANISMS
# =============================================================================
pa_population_share = 0.039

revenue_mechanisms = {
    'Financial Transaction Tax (FTT)': {'annual_revenue_B': 180, 'source': 'CBO/JCT estimate'},
    'Wealth Tax (2% on >$50M)': {'annual_revenue_B': 250, 'source': 'Saez & Zucman (2019)'},
    'Corporate Minimum Tax (21%)': {'annual_revenue_B': 150, 'source': 'Treasury estimate'},
    'Estate Tax Reform': {'annual_revenue_B': 40, 'source': 'CBO baseline'},
    'Capital Gains as Income': {'annual_revenue_B': 120, 'source': 'TPC analysis'},
    'Carried Interest Loophole': {'annual_revenue_B': 18, 'source': 'JCT estimate'},
    'Stock Buyback Tax (4%)': {'annual_revenue_B': 45, 'source': 'JCT/CBO'},
    'Offshore Tax Haven Reform': {'annual_revenue_B': 60, 'source': 'ITEP estimate'},
    'Medicare Surtax Expansion': {'annual_revenue_B': 35, 'source': 'CBO score'},
    'Carbon Fee ($50/ton)': {'annual_revenue_B': 55, 'source': 'CBO/Resources for Future'},
    'Excess Profits Tax': {'annual_revenue_B': 30, 'source': 'Brookings estimate'},
    'IRS Enforcement Funding': {'annual_revenue_B': 14, 'source': 'CBO/IRA scoring'}
}

# =============================================================================
# PHASE 18 DATA: MVS
# =============================================================================
institution_mvs_data = {
    'Lincoln University': {'pell_share': 0.85, 'completion_rate': 0.32, 'earnings_premium_factor': 1.3, 'type': 'HBCU'},
    'Cheyney University': {'pell_share': 0.80, 'completion_rate': 0.18, 'earnings_premium_factor': 1.2, 'type': 'HBCU'},
    'CC of Philadelphia': {'pell_share': 0.65, 'completion_rate': 0.15, 'earnings_premium_factor': 1.0, 'type': 'CC'},
    'Harrisburg Area CC': {'pell_share': 0.45, 'completion_rate': 0.22, 'earnings_premium_factor': 1.0, 'type': 'CC'},
    'Temple University': {'pell_share': 0.38, 'completion_rate': 0.72, 'earnings_premium_factor': 1.5, 'type': 'State-Related'},
    'West Chester University': {'pell_share': 0.30, 'completion_rate': 0.72, 'earnings_premium_factor': 1.2, 'type': 'PASSHE'},
    'Indiana University of PA': {'pell_share': 0.42, 'completion_rate': 0.55, 'earnings_premium_factor': 1.1, 'type': 'PASSHE'},
    'East Stroudsburg University': {'pell_share': 0.52, 'completion_rate': 0.48, 'earnings_premium_factor': 1.0, 'type': 'PASSHE'},
    'Kutztown University': {'pell_share': 0.40, 'completion_rate': 0.58, 'earnings_premium_factor': 1.1, 'type': 'PASSHE'},
    'Penn State': {'pell_share': 0.22, 'completion_rate': 0.87, 'earnings_premium_factor': 1.8, 'type': 'State-Related'},
    'University of Pittsburgh': {'pell_share': 0.25, 'completion_rate': 0.84, 'earnings_premium_factor': 1.7, 'type': 'State-Related'},
}

pell_completion_penalty = 0.33
national_avg_completion = 0.60
