from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_final_quality_output_motors_v512j import (
    run_and_write_phase5_12j_reports,
)


def main() -> int:
    report = run_and_write_phase5_12j_reports()

    print(report.status)
    print(f"Official QM motors: {report.official_qm_motors}")
    print(f"Registry total: {report.registry_total}")
    print(f"qm_060 ready: {report.qm_060.ready}")
    print(f"qm_060 readability score: {report.qm_060.readability_score}")
    print(f"qm_059 ready: {report.qm_059.ready}")

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
