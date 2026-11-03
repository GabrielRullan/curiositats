#!/usr/bin/env python3
"""Unified Test Runner for 'Una teringa de curiositats'.

Executes the 4-tier E2E opaque-box test suite with rich filtering,
traceability reporting, and standard unittest compatibility.

Usage:
    python tests/run_tests.py                      # Run all tiers in progressive mode
    python tests/run_tests.py --tier 1             # Run Tier 1 (Feature Coverage) only
    python tests/run_tests.py --tier 2             # Run Tier 2 (Boundary & Corner Cases) only
    python tests/run_tests.py --tier 3             # Run Tier 3 (Cross-Feature Interactions) only
    python tests/run_tests.py --tier 4             # Run Tier 4 (Real-World Workflows) only
    python tests/run_tests.py --strict             # Run in strict mode (no milestone skips allowed)
    python tests/run_tests.py -v                   # Verbose test output
"""

import argparse
import os
from pathlib import Path
import sys
import time
import unittest

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Unified E2E Test Suite Runner for 'Una teringa de curiositats'"
    )
    parser.add_argument(
        "-t", "--tier",
        type=str,
        default="all",
        choices=["1", "2", "3", "4", "all"],
        help="Test tier to execute (1: Features, 2: Boundaries, 3: Interactions, 4: Workflows, all: Default)"
    )
    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Strict mode: disallow milestone skips and assert 100% requirement completion (for M6 / Victory Audit)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=1,
        help="Verbosity level (-v: standard verbose, -vv: debug)"
    )
    return parser.parse_args()


def load_test_suite(tier: str = "all") -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    tier_modules = {
        "1": "tests.test_tier1_features",
        "2": "tests.test_tier2_boundaries",
        "3": "tests.test_tier3_interactions",
        "4": "tests.test_tier4_workflows",
    }

    if tier == "all":
        for mod_name in tier_modules.values():
            suite.addTests(loader.loadTestsFromName(mod_name))
    else:
        mod_name = tier_modules.get(tier)
        if mod_name:
            suite.addTests(loader.loadTestsFromName(mod_name))

    return suite


def main():
    args = parse_arguments()

    if args.strict:
        os.environ["CURIOSTATS_E2E_STRICT"] = "1"

    print("=" * 70)
    print("  UNA TERINGA DE CURIOSITATS -- E2E TEST SUITE RUNNER")
    print("=" * 70)
    print(f"  Execution Mode : {'STRICT (Zero-skip enforced)' if args.strict else 'PROGRESSIVE (Milestone-aware)'}")
    print(f"  Target Scope   : Tier {args.tier.upper()}")
    print(f"  Test Framework : Python {sys.version.split()[0]} standard unittest")
    print(f"  Working Dir    : {PROJECT_ROOT}")
    print("=" * 70)

    suite = load_test_suite(tier=args.tier)
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=args.verbose)
    result = runner.run(suite)
    duration = time.time() - start_time

    total_tests = result.testsRun
    failed_count = len(result.failures)
    error_count = len(result.errors)
    skipped_count = len(result.skipped)
    passed_count = total_tests - failed_count - error_count - skipped_count

    print("\n" + "=" * 70)
    print("  TEST EXECUTION SUMMARY REPORT")
    print("=" * 70)
    print(f"  Total Executed : {total_tests}")
    print(f"  Passed         : {passed_count}")
    print(f"  Skipped        : {skipped_count}")
    print(f"  Failures       : {failed_count}")
    print(f"  Errors         : {error_count}")
    print(f"  Elapsed Time   : {duration:.3f} seconds")
    print("=" * 70)

    if not result.wasSuccessful():
        print("  RESULT: FAILED [X]")
        sys.exit(1)
    else:
        print("  RESULT: SUCCESS [OK]")
        sys.exit(0)


if __name__ == "__main__":
    main()
