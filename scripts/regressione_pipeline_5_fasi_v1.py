import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

PYTHON = sys.executable

TARGET_FILE = ROOT / "backend" / "motori_scrittura.py"

MARKERS = [
    "MAP_COVERAGE_V1",
    "FASE 2 — REDUCE V1",
    "FASE 3 — OUTPUT BUILDER V1",
    "FASE 4 — SUPER QUALITY GATE V1",
    "FASE 5 — QUALITY SUMMARY CARDS V1",
    "FASE 5.1 — MICRO CONCEPTS CARDS QUALITY PATCH",
]

COMMANDS = [
    {
        "name": "compile_motori_scrittura",
        "cmd": [PYTHON, "-m", "py_compile", "backend/motori_scrittura.py"],
    },
    {
        "name": "test_map_phase_v1",
        "cmd": [PYTHON, "backend/test_map_phase_v1.py"],
    },
    {
        "name": "test_map_phase_json_corrotto_v1",
        "cmd": [PYTHON, "backend/test_map_phase_json_corrotto_v1.py"],
    },
    {
        "name": "test_map_phase_client_reale_v1",
        "cmd": [PYTHON, "backend/test_map_phase_client_reale_v1.py"],
    },
    {
        "name": "test_map_phase_coverage_reale_v1",
        "cmd": [PYTHON, "backend/test_map_phase_coverage_reale_v1.py"],
    },
    {
        "name": "test_reduce_phase_v1",
        "cmd": [PYTHON, "backend/test_reduce_phase_v1.py"],
    },
    {
        "name": "test_output_builder_phase_v1",
        "cmd": [PYTHON, "backend/test_output_builder_phase_v1.py"],
    },
    {
        "name": "test_super_quality_gate_phase_v1",
        "cmd": [PYTHON, "backend/test_super_quality_gate_phase_v1.py"],
    },
    {
        "name": "test_phase5_quality_summary_cards_v1",
        "cmd": [PYTHON, "backend/test_phase5_quality_summary_cards_v1.py"],
    },
    {
        "name": "test_phase5_micro_concepts_cards_v11",
        "cmd": [PYTHON, "backend/test_phase5_micro_concepts_cards_v11.py"],
    },
]


def check_markers():
    errors = []

    if not TARGET_FILE.exists():
        return [f"File mancante: {TARGET_FILE}"]

    text = TARGET_FILE.read_text(encoding="utf-8")

    for marker in MARKERS:
        if marker not in text:
            errors.append(f"Marker mancante in motori_scrittura.py: {marker}")

    return errors


def run_command(item):
    name = item["name"]
    cmd = item["cmd"]

    print("\n" + "=" * 80)
    print(f"▶ {name}")
    print(" ".join(cmd))
    print("=" * 80)

    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        if completed.stdout:
            print(completed.stdout)

        if completed.stderr:
            print(completed.stderr)

        return {
            "name": name,
            "cmd": cmd,
            "returncode": completed.returncode,
            "passed": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    except Exception as exc:
        print(f"❌ ERRORE NON GESTITO in {name}: {type(exc).__name__}: {exc}")
        return {
            "name": name,
            "cmd": cmd,
            "returncode": -1,
            "passed": False,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


def main():
    started_at = datetime.now().isoformat(timespec="seconds")

    print("REGRESSIONE PIPELINE 5 FASI V1")
    print(f"Root progetto: {ROOT}")
    print(f"Python: {PYTHON}")
    print(f"Avvio: {started_at}")

    marker_errors = check_markers()

    results = []

    if marker_errors:
        print("\n❌ MARKER CHECK FALLITO")
        for error in marker_errors:
            print(f"- {error}")

        report = {
            "started_at": started_at,
            "finished_at": datetime.now().isoformat(timespec="seconds"),
            "passed": False,
            "marker_errors": marker_errors,
            "results": [],
        }

        json_path = REPORTS_DIR / "regressione_pipeline_5_fasi_v1.json"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return 1

    print("\n✅ Marker principali presenti in backend/motori_scrittura.py")

    for item in COMMANDS:
        result = run_command(item)
        results.append(result)

        if not result["passed"]:
            print(f"\n❌ REGRESSIONE INTERROTTA: {result['name']} FALLITO")
            break

    passed = all(item["passed"] for item in results) and len(results) == len(COMMANDS)

    finished_at = datetime.now().isoformat(timespec="seconds")

    report = {
        "started_at": started_at,
        "finished_at": finished_at,
        "passed": passed,
        "marker_errors": [],
        "total_commands": len(COMMANDS),
        "executed_commands": len(results),
        "passed_commands": len([item for item in results if item["passed"]]),
        "failed_commands": len([item for item in results if not item["passed"]]),
        "results": results,
    }

    json_path = REPORTS_DIR / "regressione_pipeline_5_fasi_v1.json"
    md_path = REPORTS_DIR / "regressione_pipeline_5_fasi_v1.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Regressione Pipeline 5 Fasi V1",
        "",
        f"- Avvio: `{started_at}`",
        f"- Fine: `{finished_at}`",
        f"- Esito: `{'PASS' if passed else 'FAIL'}`",
        f"- Comandi eseguiti: `{len(results)}/{len(COMMANDS)}`",
        "",
        "## Risultati",
        "",
    ]

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- `{status}` — `{item['name']}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n" + "=" * 80)

    if passed:
        print("✅ REGRESSIONE PIPELINE 5 FASI V1 PASSATA")
    else:
        print("❌ REGRESSIONE PIPELINE 5 FASI V1 FALLITA")

    print(f"Report JSON: {json_path}")
    print(f"Report MD:   {md_path}")
    print("=" * 80)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
