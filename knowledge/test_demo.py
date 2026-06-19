#!/usr/bin/env python3
"""
test_demo.py — deterministic retrieval test for the Tega knowledge base demo.

This does NOT call Ollama / the LLM. It only tests the file-selection
step in query.py (frontmatter parsing, graph building, keyword
matching, related-link traversal), so you can confirm retrieval is
correct before you're standing in front of the team relying on a
model response to prove it.

Run from the knowledge/ directory:
    python test_demo.py
Exit code is 0 if all cases pass, 1 if any fail.
"""

import sys
from pathlib import Path

import query

# Each case: (label, question, expected sorted list of file ids).
# Expected ids were derived by running query.select_files() against the
# current knowledge/ content and confirming the result by hand against
# the frontmatter `related` chains (see DEMO.md for the chain diagram).
TEST_CASES = [
    (
        "single-file (customer_002 minimal cluster)",
        "Where is Greenfield Aggregates Ltd located and what is their daily throughput?",
        ["customer_002", "product_hydrocyclone", "rule_design_rules", "rule_standards"],
    ),
    (
        "cross-file (customer_001 full chain: customer -> project -> product -> report)",
        "What trommel wear issues has Los Andes Cobre reported and which panel spec did we supply?",
        [
            "customer_001",
            "product_trommel_panel",
            "project_customer_001_trommel",
            "report_wear_2026_01",
            "rule_design_rules",
            "rule_standards",
        ],
    ),
    (
        "missing data (asks for a figure that is not in the knowledge base)",
        "What is the drum motor power rating for the Los Andes Cobre trommel?",
        [
            "customer_001",
            "product_trommel_panel",
            "project_customer_001_trommel",
            "report_wear_2026_01",
            "rule_design_rules",
            "rule_standards",
        ],
    ),
]


def run_tests() -> bool:
    graph = query.build_graph()
    all_passed = True

    print(f"Loaded graph with {len(graph)} files from {query.KNOWLEDGE_ROOT}\n")

    for label, question, expected_ids in TEST_CASES:
        selected_ids = query.select_files(question, graph)
        expected_sorted = sorted(expected_ids)
        passed = selected_ids == expected_sorted

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {label}")
        print(f'  question : "{question}"')
        print(f"  selected : {selected_ids}")
        if not passed:
            print(f"  expected : {expected_sorted}")
            missing = set(expected_sorted) - set(selected_ids)
            extra = set(selected_ids) - set(expected_sorted)
            if missing:
                print(f"  missing  : {sorted(missing)}")
            if extra:
                print(f"  unexpected extra: {sorted(extra)}")
        print()

        all_passed = all_passed and passed

    return all_passed


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    success = run_tests()
    print("=" * 70)
    print("ALL TESTS PASSED" if success else "SOME TESTS FAILED")
    sys.exit(0 if success else 1)
