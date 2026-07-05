from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.phase5_final_card_generation_v513a import (
    run_and_write_phase5_13a_reports,
)


def main() -> int:
    report = run_and_write_phase5_13a_reports()

    print(report.status)
    print(f"Cards generated: {report.generated_cards_count}")
    print(f"Official QM motors: {report.official_qm_motors}")
    print(f"Registry total: {report.registry_total}")
    print(f"Card route total: {report.card_route_total}")
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
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
