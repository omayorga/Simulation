"""Pennsylvania Higher Education Economic Impact Analysis — Master Runner

Executes all 18 phases in order. Each phase can also be run independently.

Usage:
    python run_all.py                     # Run all phases
    python run_all.py 1 6 8              # Run specific phases (1, 6, 8)
    python run_all.py --list             # List all phases

Author: Oscar J. Mayorga
Updated: March 3, 2026
Repository: github.com/omayorga/Simulation
"""

import sys
import os
import subprocess
import time

# Ensure we're in the right directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Phase definitions
PHASES = {
    1: ('phase1_institutional_data.py', 'Institutional Data (Penn State, Pitt, Temple, PASSHE, CCs)'),
    2: ('phase2_employment_economic_multipliers.py', 'Employment & Economic Multipliers'),
    3: ('phase3_historical_trends.py', 'Historical Trends, Brain Drain, Policy Scenarios, ROI'),
    4: ('phase4_county_level.py', 'County-Level Economic Impact'),
    5: ('phase5_visualizations.py', 'Visualizations (Charts 1-8)'),
    6: ('phase6_free_college.py', 'Free College for PA Residents - Policy Simulation'),
    7: ('phase7_counterfactual.py', 'Counterfactual - What if PA Invested Since 1980'),
    8: ('phase8_limitations.py', 'Addressing Model Limitations'),
    9: ('phase9_demographics.py', 'Demographic-Segmented Analysis'),
    10: ('phase10_sector_split.py', 'Sector-Split CC vs Four-Year'),
    11: ('phase11_cost_of_attendance.py', 'Full Cost of Attendance Modeling'),
    12: ('phase12_tuition_cap.py', 'Tuition Cap Scenario'),
    13: ('phase13_federal_matching.py', 'Counter-Cyclical Federal Matching'),
    14: ('phase14_exclude_flagships.py', 'Exclude Flagships (Penn State & Pitt)'),
    15: ('phase15_mobility_bonus.py', 'Mobility Bonus Premium'),
    16: ('phase16_equity_match.py', 'Equity Match by State Wealth'),
    17: ('phase17_revenue_mechanisms.py', 'Federal Revenue Mechanisms'),
    18: ('phase18_mobility_value_score.py', 'Mobility Value Score & Completion Gap'),
}


def run_phase(phase_num, filename, description):
    """Run a single phase file and report status."""
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ERROR: {filename} not found!")
        return False

    print(f"\n{'=' * 80}")
    print(f"RUNNING PHASE {phase_num}: {description}")
    print(f"File: {filename}")
    print(f"{'=' * 80}")

    start = time.time()
    result = subprocess.run(
        [sys.executable, filepath],
        cwd=SCRIPT_DIR,
        capture_output=False
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n  Phase {phase_num} completed successfully ({elapsed:.1f}s)")
        return True
    else:
        print(f"\n  ERROR: Phase {phase_num} failed with return code {result.returncode} ({elapsed:.1f}s)")
        return False


def list_phases():
    """Print all available phases."""
    print("\nAvailable Phases:")
    print("-" * 70)
    for num, (filename, desc) in sorted(PHASES.items()):
        print(f"  Phase {num:>2}: {desc}")
        print(f"           -> {filename}")
    print()


def main():
    print("=" * 80)
    print("PENNSYLVANIA HIGHER EDUCATION ECONOMIC IMPACT ANALYSIS")
    print("Comprehensive Multi-Phase Analysis")
    print(f"Runner started at: {time.strftime('%B %d, %Y %H:%M:%S')}")
    print("=" * 80)

    # Parse arguments
    if '--list' in sys.argv:
        list_phases()
        return

    if len(sys.argv) > 1 and sys.argv[1] != '--list':
        # Run specific phases
        try:
            phases_to_run = [int(x) for x in sys.argv[1:]]
        except ValueError:
            print("Usage: python run_all.py [phase_numbers...]")
            print("       python run_all.py --list")
            sys.exit(1)
    else:
        # Run all phases
        phases_to_run = sorted(PHASES.keys())

    # Validate phase numbers
    invalid = [p for p in phases_to_run if p not in PHASES]
    if invalid:
        print(f"ERROR: Invalid phase number(s): {invalid}")
        print(f"Valid phases: {sorted(PHASES.keys())}")
        sys.exit(1)

    # Run phases
    total_start = time.time()
    results = {}

    for phase_num in phases_to_run:
        filename, description = PHASES[phase_num]
        success = run_phase(phase_num, filename, description)
        results[phase_num] = success

    # Summary
    total_elapsed = time.time() - total_start
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)

    succeeded = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for phase_num, success in sorted(results.items()):
        status = "OK" if success else "FAILED"
        _, desc = PHASES[phase_num]
        print(f"  Phase {phase_num:>2}: [{status}] {desc}")

    print(f"\nTotal: {succeeded} succeeded, {failed} failed")
    print(f"Total time: {total_elapsed:.1f}s")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
