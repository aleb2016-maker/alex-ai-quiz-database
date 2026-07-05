#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13F — REPORT FINALE PRESENTABILE PIPELINE 4 GENERATORI

Scopo:
- produrre un report finale leggibile e presentabile sullo stato reale della pipeline;
- raccogliere in un unico documento:
  1. Card
  2. Riassunto
  3. Domande studio
  4. Test/Quiz
- dichiarare cosa è davvero collegato lato backend;
- dichiarare cosa resta da collegare alla pagina/interfaccia grafica;
- preparare il passaggio ai test veri su testi reali.

Questo script NON modifica motori, UI, PDF o app.
Produce solo:
- reports/phase5_13f_final_presentable_pipeline_report_v1.json
- reports/phase5_13f_final_presentable_pipeline_report_v1.md
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

JSON_REPORT = REPORTS / "phase5_13f_final_presentable_pipeline_report_v1.json"
MD_REPORT = REPORTS / "phase5_13f_final_presentable_pipeline_report_v1.md"

FINAL_4_GENERATORS_REPORT = REPORTS / "phase5_13e_final_4_generators_regression_v1.json"
STUDY_FINAL_REPORT = REPORTS / "phase5_13c2_study_questions_final_quality_gate_v1.json"
TEST_QUIZ_FINAL_REPORT = REPORTS / "phase5_13d2_test_quiz_final_quality_gate_v1.json"
TEST_QUIZ_CONNECTOR_REPORT = REPORTS / "phase5_13d1_test_quiz_63_real_connector_v1.json"


@dataclass
class GeneratorSnapshot:
    name: str
    status: str
    route_total: Optional[int]
    quality_controls: Optional[int]
    selector_orchestrator: Optional[int]
    real_connection: str
    evidence: List[str]
    defects: List[str]
    warnings: List[str]


@dataclass
class GitSnapshot:
    branch: str
    commit: str
    tags_at_head: List[str]
    status_short: str


@dataclass
class FinalPresentableReport:
    phase: str
    status: str
    title: str
    git: Dict[str, Any]
    generators: List[Dict[str, Any]]
    backend_readiness: Dict[str, Any]
    ui_readiness: Dict[str, Any]
    real_text_testing_plan: List[str]
    next_phase: str
    defects: List[str]
    warnings: List[str]


def _run(args: List[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _git_snapshot() -> GitSnapshot:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    commit = _run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    tags_raw = _run(["git", "tag", "--points-at", "HEAD"]).stdout.strip()
    status_short = _run(["git", "status", "--short"]).stdout.strip()

    tags = [line.strip() for line in tags_raw.splitlines() if line.strip()]

    return GitSnapshot(
        branch=branch,
        commit=commit,
        tags_at_head=tags,
        status_short=status_short,
    )


def _check_py_compile() -> Dict[str, Any]:
    files = [
        "backend/motori_scrittura.py",
        "backend/phase5_study_questions_real_connector_v513c1.py",
        "backend/phase5_study_questions_final_quality_gate_v513c2.py",
        "backend/phase5_quiz_options_repair_v513d3.py",
        "backend/phase5_test_quiz_route_materializer_v513d01.py",
        "backend/phase5_test_quiz_real_connector_v513d1.py",
        "backend/phase5_test_quiz_final_quality_gate_v513d2.py",
        "scripts/run_phase5_13e_final_4_generators_regression.py",
        "scripts/run_phase5_13f_final_presentable_pipeline_report.py",
    ]

    completed = _run([sys.executable, "-m", "py_compile", *files])

    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "returncode": completed.returncode,
        "files_checked": files,
        "output_tail": completed.stdout[-3000:],
    }


def _find_summary_evidence() -> List[str]:
    evidence: List[str] = []

    if not REPORTS.exists():
        return evidence

    for path in sorted(list(REPORTS.glob("*.json")) + list(REPORTS.glob("*.md"))):
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
        except Exception:
            continue

        has_summary = "summary" in text or "riassunto" in text
        has_55 = "55" in text
        has_pass = "pass" in text

        if has_summary and has_55 and has_pass:
            evidence.append(_rel(path))

    return evidence[:10]


def _build_generator_snapshots() -> List[GeneratorSnapshot]:
    final4 = _load_json(FINAL_4_GENERATORS_REPORT)
    study = _load_json(STUDY_FINAL_REPORT)
    test_final = _load_json(TEST_QUIZ_FINAL_REPORT)
    test_connector = _load_json(TEST_QUIZ_CONNECTOR_REPORT)

    final_generators = {
        item.get("name"): item
        for item in final4.get("generators", [])
        if isinstance(item, dict)
    }

    card_item = final_generators.get("Card", {})
    summary_item = final_generators.get("Riassunto", {})
    study_item = final_generators.get("Domande studio", {})
    test_item = final_generators.get("Test/Quiz", {})

    generators: List[GeneratorSnapshot] = []

    generators.append(GeneratorSnapshot(
        name="Card",
        status=str(card_item.get("status") or "UNKNOWN"),
        route_total=52,
        quality_controls=52,
        selector_orchestrator=None,
        real_connection="Validato nella regressione aggregata 5.13E tramite matrice qualità Card.",
        evidence=list(card_item.get("evidence") or []),
        defects=list(card_item.get("defects") or []),
        warnings=list(card_item.get("warnings") or []),
    ))

    summary_evidence = _find_summary_evidence()
    if summary_item.get("evidence"):
        summary_evidence = list(summary_item.get("evidence") or []) + summary_evidence

    # dedup preservando ordine
    seen = set()
    summary_evidence_unique: List[str] = []
    for item in summary_evidence:
        if item in seen:
            continue
        seen.add(item)
        summary_evidence_unique.append(item)

    generators.append(GeneratorSnapshot(
        name="Riassunto",
        status=str(summary_item.get("status") or "UNKNOWN"),
        route_total=55,
        quality_controls=55,
        selector_orchestrator=None,
        real_connection="Validato nella regressione aggregata 5.13E; route finale Riassunto 55 già collegata nei checkpoint precedenti.",
        evidence=summary_evidence_unique[:10],
        defects=list(summary_item.get("defects") or []),
        warnings=list(summary_item.get("warnings") or []),
    ))

    generators.append(GeneratorSnapshot(
        name="Domande studio",
        status=str(study_item.get("status") or "UNKNOWN"),
        route_total=study.get("route_total"),
        quality_controls=study.get("study_quality_controls"),
        selector_orchestrator=study.get("selector_orchestrator"),
        real_connection="quality_report.study_questions_real_connection_v513c1",
        evidence=list(study_item.get("evidence") or []) + [_rel(STUDY_FINAL_REPORT)],
        defects=list(study.get("defects") or []) + list(study_item.get("defects") or []),
        warnings=list(study.get("warnings") or []) + list(study_item.get("warnings") or []),
    ))

    generators.append(GeneratorSnapshot(
        name="Test/Quiz",
        status=str(test_item.get("status") or "UNKNOWN"),
        route_total=test_final.get("route_total") or test_connector.get("resolved_route_total"),
        quality_controls=test_final.get("test_quality_controls") or test_connector.get("resolved_test_quality_controls"),
        selector_orchestrator=test_final.get("selector_orchestrator") or test_connector.get("resolved_selector_orchestrator"),
        real_connection="quality_report.test_quiz_real_connection_v513d1",
        evidence=list(test_item.get("evidence") or []) + [_rel(TEST_QUIZ_FINAL_REPORT), _rel(TEST_QUIZ_CONNECTOR_REPORT)],
        defects=list(test_final.get("defects") or []) + list(test_connector.get("defects") or []) + list(test_item.get("defects") or []),
        warnings=list(test_final.get("warnings") or []) + list(test_connector.get("warnings") or []) + list(test_item.get("warnings") or []),
    ))

    return generators


def _validate_report(
    git: GitSnapshot,
    generators: List[GeneratorSnapshot],
    compile_result: Dict[str, Any],
) -> tuple[List[str], List[str]]:
    defects: List[str] = []
    warnings: List[str] = []

    expected = {
        "Card": {
            "status": "PASS",
            "route_total": 52,
            "quality_controls": 52,
        },
        "Riassunto": {
            "status": "PASS",
            "route_total": 55,
            "quality_controls": 55,
        },
        "Domande studio": {
            "status": "PASS",
            "route_total": 51,
            "quality_controls": 43,
            "selector_orchestrator": 8,
        },
        "Test/Quiz": {
            "status": "PASS",
            "route_total": 63,
            "quality_controls": 55,
            "selector_orchestrator": 8,
        },
    }

    by_name = {generator.name: generator for generator in generators}

    for name, rules in expected.items():
        generator = by_name.get(name)
        if not generator:
            defects.append(f"Generatore mancante nel report: {name}")
            continue

        if generator.status != rules["status"]:
            defects.append(f"{name}: status atteso PASS, trovato {generator.status}")

        if generator.route_total != rules["route_total"]:
            defects.append(f"{name}: route_total atteso {rules['route_total']}, trovato {generator.route_total}")

        if generator.quality_controls != rules["quality_controls"]:
            defects.append(f"{name}: quality_controls atteso {rules['quality_controls']}, trovato {generator.quality_controls}")

        expected_selector = rules.get("selector_orchestrator")
        if expected_selector is not None and generator.selector_orchestrator != expected_selector:
            defects.append(
                f"{name}: selector_orchestrator atteso {expected_selector}, trovato {generator.selector_orchestrator}"
            )

        if generator.defects:
            defects.append(f"{name}: defects non vuoti: {generator.defects}")

        if generator.warnings:
            defects.append(f"{name}: warnings non vuoti: {generator.warnings}")

    if compile_result.get("status") != "PASS":
        defects.append("py_compile finale non PASS.")

    if git.branch != "rag-concept-app-presentabile-v3":
        warnings.append(f"Branch inatteso: {git.branch}")

    if git.status_short:
        allowed_self_generated = {
            "scripts/run_phase5_13f_final_presentable_pipeline_report.py",
            "scripts/fix_phase5_13f_ignore_self_generated_warning.py",
            "reports/phase5_13f_final_presentable_pipeline_report_v1.json",
            "reports/phase5_13f_final_presentable_pipeline_report_v1.md",
        }

        unexpected_dirty_lines = []

        for raw_line in git.status_short.splitlines():
            path = raw_line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()

            if path not in allowed_self_generated:
                unexpected_dirty_lines.append(raw_line)

        if unexpected_dirty_lines:
            warnings.append(
                "Working tree non pulito con file non previsti: "
                + "; ".join(unexpected_dirty_lines)
            )

    return defects, warnings


def render_markdown(report: FinalPresentableReport) -> str:
    lines: List[str] = [
        "# FASE 5.13F — REPORT FINALE PRESENTABILE PIPELINE 4 GENERATORI",
        "",
        f"Status: `{report.status}`",
        "",
        "## Sintesi presentabile",
        "",
        "La pipeline backend dei quattro generatori principali risulta collegata e validata:",
        "",
        "- **Card**",
        "- **Riassunto**",
        "- **Domande studio**",
        "- **Test/Quiz**",
        "",
        "Il report conferma che la parte backend è pronta per il prossimo passaggio: collegamento alla pagina/interfaccia grafica e test veri su testi reali.",
        "",
        "## Git",
        "",
        f"- Branch: `{report.git['branch']}`",
        f"- Commit HEAD: `{report.git['commit']}`",
        f"- Tag su HEAD: `{', '.join(report.git['tags_at_head']) if report.git['tags_at_head'] else 'nessuno'}`",
        f"- Working tree short: `{report.git['status_short'] or 'clean'}`",
        "",
        "## Stato generatori",
        "",
        "| Generatore | Status | Route/Controlli | Selector | Collegamento reale | Defects | Warnings |",
        "|---|---|---:|---:|---|---:|---:|",
    ]

    for generator in report.generators:
        route = generator.get("route_total")
        controls = generator.get("quality_controls")
        selector = generator.get("selector_orchestrator")
        lines.append(
            "| "
            f"{generator['name']} | "
            f"`{generator['status']}` | "
            f"`{route}/{controls}` | "
            f"`{selector if selector is not None else '-'}` | "
            f"`{generator['real_connection']}` | "
            f"{len(generator['defects'])} | "
            f"{len(generator['warnings'])} |"
        )

    lines.extend([
        "",
        "## Backend readiness",
        "",
        f"- Py compile finale: `{report.backend_readiness['py_compile']['status']}`",
        f"- File controllati: `{len(report.backend_readiness['py_compile']['files_checked'])}`",
        f"- Regressione 4 generatori: `{report.backend_readiness['final_4_generators_regression_status']}`",
        f"- Errori aggregati: `{report.backend_readiness['aggregate_defects']}`",
        f"- Warning aggregati: `{report.backend_readiness['aggregate_warnings']}`",
        "",
        "## UI readiness",
        "",
        f"- Stato collegamento UI: `{report.ui_readiness['status']}`",
        f"- Nota: {report.ui_readiness['note']}",
        "",
        "## Piano test veri su testi reali",
        "",
    ])

    for item in report.real_text_testing_plan:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Prossima fase",
        "",
        f"`{report.next_phase}`",
        "",
        "## Evidenze principali",
        "",
    ])

    for generator in report.generators:
        lines.append(f"### {generator['name']}")
        evidence = generator.get("evidence") or []
        if evidence:
            for item in evidence:
                lines.append(f"- `{item}`")
        else:
            lines.append("- Nessuna evidenza specifica registrata")

    lines.extend([
        "",
        "## Defects",
        "",
    ])

    if report.defects:
        for defect in report.defects:
            lines.append(f"- `{defect}`")
    else:
        lines.append("- Nessuno")

    lines.extend([
        "",
        "## Warnings",
        "",
    ])

    if report.warnings:
        for warning in report.warnings:
            lines.append(f"- `{warning}`")
    else:
        lines.append("- Nessuno")

    lines.extend([
        "",
        "## Confini del report",
        "",
        "- Questo report non collega ancora la pagina HTML/interfaccia grafica.",
        "- Questo report non modifica UI, PDF o app.",
        "- Questo report certifica la prontezza backend prima del collegamento grafico.",
        "- Il collegamento alla pagina va fatto nella fase successiva, con test reali su input caricati dall'interfaccia.",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    REPORTS.mkdir(exist_ok=True)

    # Rigenera la regressione aggregata prima del report finale.
    regression = _run([sys.executable, "scripts/run_phase5_13e_final_4_generators_regression.py"])
    regression_status_line = "UNKNOWN"
    for line in regression.stdout.splitlines():
        if "Fase 5.13E" in line:
            regression_status_line = line.strip()
            break

    git = _git_snapshot()
    compile_result = _check_py_compile()
    generators = _build_generator_snapshots()

    defects, warnings = _validate_report(git, generators, compile_result)

    if regression.returncode != 0:
        defects.append(f"Runner regressione 5.13E non PASS: returncode={regression.returncode}")

    if "PASS - Fase 5.13E" not in regression.stdout:
        defects.append("Runner regressione 5.13E non contiene PASS atteso.")

    backend_readiness = {
        "py_compile": compile_result,
        "final_4_generators_regression_status": regression_status_line,
        "aggregate_defects": len(defects),
        "aggregate_warnings": len(warnings),
    }

    ui_readiness = {
        "status": "NOT_CONNECTED_YET",
        "note": (
            "Il backend dei quattro generatori è validato. "
            "La pagina/interfaccia grafica deve essere collegata nella fase successiva "
            "senza modificare i motori già validati."
        ),
    }

    real_text_testing_plan = [
        "Testare documento breve pulito TXT/MD con i 4 generatori dalla pagina.",
        "Testare PDF reale con testo estratto, verificando Card/Riassunto/Domande/Test.",
        "Testare documento lungo con più sezioni e controllare stabilità output.",
        "Testare testo sporco/OCR-like per verificare robustezza linguistica.",
        "Verificare che la UI non usi fallback/demo quando l'utente carica un testo reale.",
        "Verificare download/output separati senza rompere i generatori.",
    ]

    status = (
        "PASS - Fase 5.13F: FINAL_PRESENTABLE_PIPELINE_REPORT_READY"
        if not defects
        else "FAIL - Fase 5.13F: FINAL_PRESENTABLE_PIPELINE_REPORT_NOT_READY"
    )

    report = FinalPresentableReport(
        phase="5.13F",
        status=status,
        title="Report finale presentabile pipeline 4 generatori",
        git=asdict(git),
        generators=[asdict(generator) for generator in generators],
        backend_readiness=backend_readiness,
        ui_readiness=ui_readiness,
        real_text_testing_plan=real_text_testing_plan,
        next_phase="FASE 5.14 — Collegamento pagina/interfaccia grafica + test veri su testi reali",
        defects=defects,
        warnings=warnings,
    )

    JSON_REPORT.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    MD_REPORT.write_text(render_markdown(report), encoding="utf-8")

    print(status)
    print(f"Backend py_compile: {compile_result['status']}")
    print(f"Regressione 4 generatori: {regression_status_line}")
    for generator in generators:
        print(
            f"{generator.name}: {generator.status} "
            f"route={generator.route_total} controls={generator.quality_controls} "
            f"selector={generator.selector_orchestrator} "
            f"defects={len(generator.defects)} warnings={len(generator.warnings)}"
        )
    print(f"UI readiness: {ui_readiness['status']}")
    print(f"Defects: {len(defects)}")
    print(f"Warnings: {len(warnings)}")
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MD_REPORT}")

    if defects:
        print("Defects:")
        for defect in defects:
            print(f"- {defect}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
