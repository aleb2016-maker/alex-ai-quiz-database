from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_orchestration_matrix_v512h2 import (
    run_and_write_phase5_12h2_reports,
)


def main() -> int:
    report = run_and_write_phase5_12h2_reports()

    print(report.status)
    print(f"Registry total motors: {report.registry_total_motors}")
    print(f"Matrix updated: {report.matrix_updated}")
    print(f"Orchestration updated: {report.orchestration_updated}")

    print("Section routes:")
    for route in report.section_routes:
        print(
            f"- {route.section_label}: "
            f"{route.g2_quality_controls_count} + "
            f"{route.selector_orchestrator_controls_count} = "
            f"{route.total_controls_after_h2}"
        )

    if report.defects:
        print("Defects:")
        for defect in report.defects:
            print(f"- {defect}")
        return 1

    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")

    print(f"Next phase: {report.next_phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
