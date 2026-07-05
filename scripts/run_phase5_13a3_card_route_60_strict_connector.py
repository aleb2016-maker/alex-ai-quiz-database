from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_card_route_60_strict_connector_v513a3 import run_from_file


def main() -> int:
    report = run_from_file()

    print(report.status)
    print(f"Expected controls: {report.expected_controls}")
    print(f"Connected controls: {report.connected_controls}")
    print(f"Executed controls: {report.executed_controls}")
    print(f"Passed controls: {report.passed_controls}")
    print(f"Failed controls: {report.failed_controls}")
    print(f"Cards checked: {report.cards_checked}")

    if report.defects:
        print("Defects:")
        for defect in report.defects:
            print(f"- {defect}")
        return 1

    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
