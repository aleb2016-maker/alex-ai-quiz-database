from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_summary_route_55_strict_connector_v513b1 import run_from_payload


def main() -> int:
    payload_file = PROJECT_ROOT / "reports/phase5_13b1_final_summary_payload_v1.json"

    if not payload_file.exists():
        print(f"Payload riassunto mancante: {payload_file}")
        return 1

    payload = json.loads(payload_file.read_text(encoding="utf-8"))
    report = run_from_payload(payload)

    print(report.status)
    print(f"Expected controls: {report.expected_controls}")
    print(f"Connected controls: {report.connected_controls}")
    print(f"Executed controls: {report.executed_controls}")
    print(f"Passed controls: {report.passed_controls}")
    print(f"Failed controls: {report.failed_controls}")
    print(f"Summary checked: {report.summary_checked}")

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
