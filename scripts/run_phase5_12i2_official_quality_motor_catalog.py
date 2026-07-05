from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_official_motor_catalog_v512i2 import (
    run_and_write_phase5_12i2_report,
)


def main() -> int:
    report = run_and_write_phase5_12i2_report()

    print(report.status)
    print(f"Official QM motors: {report.official_qm_motors_count}")
    print(f"Registry total after H.2: {report.registry_total_after_h2}")

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
