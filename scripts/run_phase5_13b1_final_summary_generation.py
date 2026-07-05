from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_final_summary_generation_v513b1 import run_and_write_phase5_13b1_reports


def main() -> int:
    report = run_and_write_phase5_13b1_reports()

    print(report.status)
    print(f"Summary generated: {report.summary_generated}")
    print(f"Summary route total: {report.summary_route_total}")
    print(f"Connected controls: {report.route_connected_controls}")
    print(f"Executed controls: {report.route_executed_controls}")
    print(f"Passed controls: {report.route_passed_controls}")
    print(f"Failed controls: {report.route_failed_controls}")
    print(f"qm_059 output ready: {report.qm_059_output_ready}")

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
