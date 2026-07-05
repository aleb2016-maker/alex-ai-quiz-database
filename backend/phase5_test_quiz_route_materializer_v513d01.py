#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.0.1 — TEST/QUIZ ROUTE 63 MATERIALIZER

Scopo:
- materializzare la route canonica Test/Quiz da 63 motori;
- usare la matrice qualità già esistente quando disponibile;
- aggiungere gli 8 selector/orchestrator qm_051..qm_058;
- validare 55 controlli qualità + 8 selector = 63.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_REPORT = ROOT / "reports" / "phase5_13d01_test_quiz_route_63_materializer_v1.json"
DEFAULT_MD_REPORT = ROOT / "reports" / "phase5_13d01_test_quiz_route_63_materializer_v1.md"

EXPECTED_TEST_QUALITY_CONTROLS = 55
EXPECTED_SELECTOR_ORCHESTRATOR = 8
EXPECTED_TEST_ROUTE_TOTAL = 63

SELECTOR_ORCHESTRATOR_IDS = [f"qm_{i:03d}" for i in range(51, 59)]

MATRIX_CANDIDATES = [
    ROOT / "reports" / "phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json",
    ROOT / "reports" / "phase5_12f2_section_quality_matrix_with_advanced_language_v1.json",
    ROOT / "reports" / "phase5_12e2_section_quality_matrix_with_test_quiz_v1.json",
]


@dataclass
class TestQuizRouteMaterializerReport:
    phase: str
    status: str
    expected_test_quality_controls: int
    resolved_test_quality_controls: int
    expected_selector_orchestrator: int
    resolved_selector_orchestrator: int
    expected_test_route_total: int
    resolved_test_route_total: int
    source_matrix: str
    test_quality_ids: List[str]
    selector_orchestrator_ids: List[str]
    final_route_ids: List[str]
    defects: List[str]
    warnings: List[str]


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_id(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith("qm_") and len(raw) == 6:
        return raw
    if raw.startswith("qm_"):
        suffix = raw.split("_", 1)[1]
        if suffix.isdigit():
            return f"qm_{int(suffix):03d}"
    if raw.isdigit():
        return f"qm_{int(raw):03d}"
    return raw


def _unique(values: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        item = _normalize_id(value)
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _extract_from_matrix(data: Dict[str, Any]) -> List[str]:
    sections = data.get("sections") or {}
    test_section = (
        sections.get("test_quiz")
        or sections.get("quiz")
        or sections.get("test")
        or {}
    )

    if isinstance(test_section, dict):
        for key in [
            "active_motor_ids",
            "active_motors",
            "motor_ids",
            "quality_motor_ids",
            "resolved_motor_ids",
        ]:
            values = test_section.get(key)
            if isinstance(values, list):
                return _unique([str(item) for item in values])

    routes = data.get("routes") or data.get("section_routes") or {}
    if isinstance(routes, dict):
        route = routes.get("test_quiz") or routes.get("quiz") or routes.get("test") or {}
        if isinstance(route, dict):
            for key in ["active_motor_ids", "quality_motor_ids", "motor_ids", "final_route_ids"]:
                values = route.get(key)
                if isinstance(values, list):
                    return _unique([str(item) for item in values])

    return []


def _fallback_from_official_catalog() -> List[str]:
    """
    Fallback prudente:
    prova a leggere il catalogo ufficiale se esporta dati compatibili.
    Se non trova API note, restituisce lista vuota e il report fallisce.
    """
    try:
        from backend import phase5_official_motor_catalog_v512i2 as catalog
    except Exception:
        try:
            import phase5_official_motor_catalog_v512i2 as catalog
        except Exception:
            return []

    candidates: List[Any] = []
    for name in [
        "build_official_motor_catalog",
        "build_catalog",
        "get_official_motor_catalog",
        "run",
        "run_and_write",
    ]:
        fn = getattr(catalog, name, None)
        if callable(fn):
            try:
                candidates.append(fn())
            except Exception:
                pass

    ids: List[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            section_values = obj.get("sections") or obj.get("areas") or obj.get("applicable_sections") or []
            mid = obj.get("id") or obj.get("motor_id") or obj.get("qm_id")
            if mid and isinstance(section_values, list) and "test_quiz" in section_values:
                ids.append(str(mid))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
        else:
            section_values = getattr(obj, "sections", None) or getattr(obj, "areas", None)
            mid = getattr(obj, "id", None) or getattr(obj, "motor_id", None) or getattr(obj, "qm_id", None)
            if mid and isinstance(section_values, list) and "test_quiz" in section_values:
                ids.append(str(mid))

    for candidate in candidates:
        walk(candidate)

    return _unique(ids)


def resolve_test_quality_ids() -> tuple[List[str], str, List[str]]:
    warnings: List[str] = []

    for path in MATRIX_CANDIDATES:
        if not path.exists():
            warnings.append(f"matrix_candidate_missing:{path.name}")
            continue
        try:
            ids = _extract_from_matrix(_read_json(path))
        except Exception as exc:
            warnings.append(f"matrix_candidate_read_error:{path.name}:{type(exc).__name__}:{exc}")
            continue
        if ids:
            selector = set(SELECTOR_ORCHESTRATOR_IDS)
            quality_ids = [item for item in ids if item not in selector]
            return quality_ids, str(path.relative_to(ROOT)), warnings

    ids = _fallback_from_official_catalog()
    selector = set(SELECTOR_ORCHESTRATOR_IDS)
    quality_ids = [item for item in ids if item not in selector]
    return quality_ids, "backend.phase5_official_motor_catalog_v512i2:fallback", warnings


def materialize_test_quiz_route() -> TestQuizRouteMaterializerReport:
    defects: List[str] = []
    warnings: List[str] = []

    test_quality_ids, source_matrix, source_warnings = resolve_test_quality_ids()
    warnings.extend(source_warnings)

    test_quality_ids = _unique(test_quality_ids)
    selector_ids = _unique(SELECTOR_ORCHESTRATOR_IDS)
    final_route_ids = _unique(test_quality_ids + selector_ids)

    if len(test_quality_ids) != EXPECTED_TEST_QUALITY_CONTROLS:
        defects.append(
            f"Controlli qualità Test/Quiz attesi {EXPECTED_TEST_QUALITY_CONTROLS}, trovati {len(test_quality_ids)}"
        )

    if len(selector_ids) != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(
            f"Selector/orchestrator attesi {EXPECTED_SELECTOR_ORCHESTRATOR}, trovati {len(selector_ids)}"
        )

    if len(final_route_ids) != EXPECTED_TEST_ROUTE_TOTAL:
        defects.append(
            f"Route Test/Quiz attesa {EXPECTED_TEST_ROUTE_TOTAL}, trovata {len(final_route_ids)}"
        )

    required_ids = [
        "qm_033",  # test separato da card/riassunto/domande studio
        "qm_048",  # ripetizioni meccaniche tra domande
        "qm_051",
        "qm_052",
        "qm_053",
        "qm_054",
        "qm_055",
        "qm_056",
        "qm_057",
        "qm_058",
    ]

    def _route_contains(required_id: str) -> bool:
        return any(
            item == required_id or item.startswith(required_id + "_")
            for item in final_route_ids
        )

    for required in required_ids:
        if not _route_contains(required):
            defects.append(f"Motore obbligatorio mancante nella route Test/Quiz: {required}")

    status = (
        "PASS - Fase 5.13D.0.1: TEST_QUIZ_ROUTE_63_MATERIALIZED"
        if not defects
        else "FAIL - Fase 5.13D.0.1: TEST_QUIZ_ROUTE_63_NOT_MATERIALIZED"
    )

    return TestQuizRouteMaterializerReport(
        phase="5.13D.0.1",
        status=status,
        expected_test_quality_controls=EXPECTED_TEST_QUALITY_CONTROLS,
        resolved_test_quality_controls=len(test_quality_ids),
        expected_selector_orchestrator=EXPECTED_SELECTOR_ORCHESTRATOR,
        resolved_selector_orchestrator=len(selector_ids),
        expected_test_route_total=EXPECTED_TEST_ROUTE_TOTAL,
        resolved_test_route_total=len(final_route_ids),
        source_matrix=source_matrix,
        test_quality_ids=test_quality_ids,
        selector_orchestrator_ids=selector_ids,
        final_route_ids=final_route_ids,
        defects=defects,
        warnings=[] if not defects else warnings,
    )


def render_markdown(report: TestQuizRouteMaterializerReport) -> str:
    lines = [
        "# FASE 5.13D.0.1 — TEST/QUIZ ROUTE 63 MATERIALIZER",
        "",
        f"Status: `{report.status}`",
        "",
        "## Conteggi",
        "",
        f"- Controlli qualità Test/Quiz attesi: `{report.expected_test_quality_controls}`",
        f"- Controlli qualità Test/Quiz risolti: `{report.resolved_test_quality_controls}`",
        f"- Selector/orchestrator attesi: `{report.expected_selector_orchestrator}`",
        f"- Selector/orchestrator risolti: `{report.resolved_selector_orchestrator}`",
        f"- Route Test/Quiz attesa: `{report.expected_test_route_total}`",
        f"- Route Test/Quiz risolta: `{report.resolved_test_route_total}`",
        f"- Sorgente matrice: `{report.source_matrix}`",
        "",
        "## Base qualità Test/Quiz",
        "",
    ]

    for qm_id in report.test_quality_ids:
        lines.append(f"- `{qm_id}`")

    lines.extend(["", "## Selector/orchestrator", ""])
    for qm_id in report.selector_orchestrator_ids:
        lines.append(f"- `{qm_id}`")

    lines.extend(["", "## Route finale Test/Quiz", ""])
    for qm_id in report.final_route_ids:
        lines.append(f"- `{qm_id}`")

    lines.extend(["", "## Defects", ""])
    lines.append("- Nessuno" if not report.defects else "\n".join(f"- `{item}`" for item in report.defects))

    lines.extend(["", "## Warnings", ""])
    lines.append("- Nessuno" if not report.warnings else "\n".join(f"- `{item}`" for item in report.warnings))

    lines.extend([
        "",
        "## Note",
        "",
        "- Questa fase materializza la route canonica Test/Quiz 63.",
        "- Non usa keyword documento.",
        "- Non modifica UI/PDF/app.",
    ])

    return "\n".join(lines) + "\n"


def run_and_write(
    json_path: Path = DEFAULT_JSON_REPORT,
    md_path: Path = DEFAULT_MD_REPORT,
) -> TestQuizRouteMaterializerReport:
    report = materialize_test_quiz_route()
    json_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    report = run_and_write()
    print(report.status)
    print(f"Test/Quiz quality controls: {report.resolved_test_quality_controls}")
    print(f"Selector/orchestrator: {report.resolved_selector_orchestrator}")
    print(f"Test/Quiz route total: {report.resolved_test_route_total}")
    print(f"Source matrix: {report.source_matrix}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")

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
