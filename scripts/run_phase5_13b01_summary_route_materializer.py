from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_summary_route_materializer_v513b01 import run_and_write


def main() -> int:
    report = run_and_write()

    print(report.status)
    print(f"Summary quality controls: {report.resolved_summary_quality_controls}")
    print(f"Selector/orchestrator: {report.resolved_selector_orchestrator}")
    print(f"Summary route total: {report.resolved_summary_route_total}")
    print(f"H2 summary total: {report.h2_summary_total}")

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
