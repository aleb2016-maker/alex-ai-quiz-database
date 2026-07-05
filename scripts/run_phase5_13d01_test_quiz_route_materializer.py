#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_test_quiz_route_materializer_v513d01 import run_and_write


def main() -> int:
    report = run_and_write()
    print(report.status)
    print(f"Test/Quiz quality controls: {report.resolved_test_quality_controls}")
    print(f"Selector/orchestrator: {report.resolved_selector_orchestrator}")
    print(f"Test/Quiz route total: {report.resolved_test_route_total}")
    print(f"Source matrix: {report.source_matrix}")

    if report.defects:
        print("Defects:")
        for defect in report.defects:
            print(f"- {defect}")
        return 1

    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
