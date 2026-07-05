from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_selector_orchestrator_standalone_v512h import (
    run_and_write_phase5_12h_report,
)


def main() -> int:
    report = run_and_write_phase5_12h_report()

    print(report.status)
    print(f"Standalone controls created: {report.standalone_controls_created}")
    print(f"Control IDs: {', '.join(report.control_ids)}")
    print(f"Registry linked: {report.registry_linked}")
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
