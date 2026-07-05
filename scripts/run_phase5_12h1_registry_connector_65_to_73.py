from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_registry_connector_v512h1 import (
    run_and_write_phase5_12h1_report,
)


def main() -> int:
    report = run_and_write_phase5_12h1_report()

    print(report.status)
    print(f"Registry before: {report.registry_before}")
    print(f"Linked controls: {report.linked_controls_count}")
    print(f"Registry after: {report.registry_after}")
    print(f"Expected registry after: {report.expected_registry_after}")
    print(f"Base registry source: {report.base_registry_source.path}")
    print(f"Linked control IDs: {', '.join(report.linked_control_ids)}")
    print(f"Matrix updated: {report.matrix_updated}")
    print(f"Orchestration updated: {report.orchestration_updated}")
    print(f"Next phase: {report.next_phase}")

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
