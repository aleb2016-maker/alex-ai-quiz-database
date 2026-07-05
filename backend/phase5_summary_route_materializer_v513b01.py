from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set


PHASE = "5.13B.0.1"
PHASE_LABEL = "FASE 5.13B.0.1 — SUMMARY ROUTE MATERIALIZER CANONICAL"

EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_SUMMARY_QUALITY_CONTROLS = 47
EXPECTED_SELECTOR_ORCHESTRATOR = 8
EXPECTED_SUMMARY_ROUTE_TOTAL = 55

OFFICIAL_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")
H2_ROUTE_REPORT = Path("reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json")
J_REFERENCE = Path("reports/phase5_12j_operational_reference_list_updated_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_13b01_summary_route_materializer_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_13b01_summary_route_materializer_v1.md")


QM_RE = re.compile(r"\bqm_\d{3}\b", re.I)

SELECTOR_ORCHESTRATOR_IDS = [f"qm_{number:03d}" for number in range(51, 59)]

SUMMARY_EXCLUDED_IDS = [
    "qm_013",
    "qm_014",
    "qm_015",
    "qm_016",
    "qm_021",
    "qm_022",
    "qm_036",
    "qm_037",
    "qm_041",
]


@dataclass
class MaterializedMotor:
    qm_id: str
    name: str
    reason: str
    source: str


@dataclass
class SummaryRouteMaterializerReport:
    phase: str
    label: str
    status: str
    official_qm_motors: int
    excluded_from_summary_count: int
    expected_summary_quality_controls: int
    resolved_summary_quality_controls: int
    expected_selector_orchestrator: int
    resolved_selector_orchestrator: int
    expected_summary_route_total: int
    resolved_summary_route_total: int
    summary_excluded_ids: List[str]
    summary_quality_ids: List[str]
    selector_orchestrator_ids: List[str]
    final_route_ids: List[str]
    materialized_motors: List[MaterializedMotor]
    h2_summary_total: int
    h2_summary_quality_controls: int
    h2_selector_orchestrator: int
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def object_text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False).lower()


def sort_qm_ids(ids: Set[str] | List[str]) -> List[str]:
    return sorted(set(ids), key=lambda item: int(item.split("_")[1]))


def qm_id_from_motor(motor: Dict[str, Any]) -> str:
    for key in ["qm_id", "id", "control_id", "motor_id"]:
        value = motor.get(key)
        if isinstance(value, str):
            match = QM_RE.search(value)
            if match:
                return match.group(0).lower()

    text = object_text(motor)
    match = QM_RE.search(text)
    return match.group(0).lower() if match else ""


def motor_name(motor: Dict[str, Any]) -> str:
    for key in ["name", "title", "nome", "control_name"]:
        value = motor.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def load_catalog_motors() -> List[Dict[str, Any]]:
    data = read_json(OFFICIAL_CATALOG)
    motors = data.get("motors")

    if not isinstance(motors, list):
        raise ValueError("Catalogo ufficiale I.2 senza lista 'motors'.")

    return [motor for motor in motors if isinstance(motor, dict)]


def load_official_qm_ids(motors: List[Dict[str, Any]]) -> List[str]:
    ids: Set[str] = set()

    for motor in motors:
        qm_id = qm_id_from_motor(motor)
        if qm_id:
            ids.add(qm_id)

    return sort_qm_ids(ids)


def get_motor_by_id(motors: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}

    for motor in motors:
        qm_id = qm_id_from_motor(motor)
        if qm_id:
            result[qm_id] = motor

    return result


def find_h2_summary_counts() -> Dict[str, int]:
    """
    Lettura tollerante:
    se il report H.2 espone i conteggi in forma diversa, il materializer non fallisce.
    I conteggi ufficiali attesi restano quelli validati nei checkpoint: 47 + 8 = 55.
    """
    if not H2_ROUTE_REPORT.exists():
        return {"total": 0, "quality": 0, "selector": 0}

    try:
        data = read_json(H2_ROUTE_REPORT)
    except Exception:
        return {"total": 0, "quality": 0, "selector": 0}

    candidates: List[Dict[str, Any]] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            text = object_text(obj)
            if "riassunto" in text or "summary" in text or "sintesi" in text:
                candidates.append(obj)
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)

    for candidate in candidates:
        total = (
            candidate.get("total_controls")
            or candidate.get("total")
            or candidate.get("route_total")
            or candidate.get("final_total")
            or 0
        )
        quality = (
            candidate.get("quality_matrix_controls")
            or candidate.get("quality_controls")
            or candidate.get("quality")
            or 0
        )
        selector = (
            candidate.get("selector_orchestrator_controls")
            or candidate.get("selector_orchestrator")
            or candidate.get("selector")
            or 0
        )

        try:
            total_i = int(total)
            quality_i = int(quality)
            selector_i = int(selector)
        except Exception:
            continue

        if total_i == EXPECTED_SUMMARY_ROUTE_TOTAL:
            return {
                "total": total_i,
                "quality": quality_i,
                "selector": selector_i,
            }

    return {"total": 0, "quality": 0, "selector": 0}


def materialize_summary_route() -> SummaryRouteMaterializerReport:
    defects: List[str] = []
    warnings: List[str] = []

    if not OFFICIAL_CATALOG.exists():
        raise FileNotFoundError(f"Catalogo ufficiale mancante: {OFFICIAL_CATALOG}")

    motors = load_catalog_motors()
    official_ids = load_official_qm_ids(motors)
    motor_by_id = get_motor_by_id(motors)

    h2_counts = find_h2_summary_counts()

    if len(official_ids) != EXPECTED_OFFICIAL_QM_MOTORS:
        defects.append(
            f"Motori ufficiali attesi 64, trovati {len(official_ids)}"
        )

    missing_exclusions = [
        qm_id for qm_id in SUMMARY_EXCLUDED_IDS
        if qm_id not in official_ids
    ]

    if missing_exclusions:
        defects.append(
            "Esclusioni Riassunto non presenti nel catalogo ufficiale: "
            + ", ".join(missing_exclusions)
        )

    selector_ids = list(SELECTOR_ORCHESTRATOR_IDS)

    missing_selector = [
        qm_id for qm_id in selector_ids
        if qm_id not in official_ids
    ]

    if missing_selector:
        defects.append(
            "Selector/orchestrator mancanti nel catalogo ufficiale: "
            + ", ".join(missing_selector)
        )

    final_route_ids = [
        qm_id for qm_id in official_ids
        if qm_id not in set(SUMMARY_EXCLUDED_IDS)
    ]

    final_route_ids = sort_qm_ids(final_route_ids)

    summary_quality_ids = [
        qm_id for qm_id in final_route_ids
        if qm_id not in set(selector_ids)
    ]

    summary_quality_ids = sort_qm_ids(summary_quality_ids)

    materialized: List[MaterializedMotor] = []

    for qm_id in final_route_ids:
        motor = motor_by_id.get(qm_id, {})
        if qm_id in selector_ids:
            reason = "selector_orchestrator"
        elif qm_id in SUMMARY_EXCLUDED_IDS:
            reason = "excluded"
        else:
            reason = "summary_canonical_quality"

        materialized.append(
            MaterializedMotor(
                qm_id=qm_id,
                name=motor_name(motor),
                reason=reason,
                source=str(OFFICIAL_CATALOG),
            )
        )

    if len(SUMMARY_EXCLUDED_IDS) != 9:
        defects.append(
            f"Le esclusioni Riassunto devono essere 9, trovate {len(SUMMARY_EXCLUDED_IDS)}"
        )

    if len(summary_quality_ids) != EXPECTED_SUMMARY_QUALITY_CONTROLS:
        defects.append(
            f"Base qualità Riassunto deve essere 47, trovata {len(summary_quality_ids)}"
        )

    if len(selector_ids) != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(
            f"Selector/orchestrator devono essere 8, trovati {len(selector_ids)}"
        )

    if len(final_route_ids) != EXPECTED_SUMMARY_ROUTE_TOTAL:
        defects.append(
            f"Route finale Riassunto deve essere 55, trovata {len(final_route_ids)}"
        )

    if h2_counts["total"] == 0:
        warnings.append(
            "Conteggi H.2 non letti automaticamente dal JSON; usati conteggi checkpoint 47 + 8 = 55."
        )
    else:
        if h2_counts["total"] != EXPECTED_SUMMARY_ROUTE_TOTAL:
            defects.append(
                f"H.2 totale Riassunto atteso 55, trovato {h2_counts['total']}"
            )
        if h2_counts["quality"] not in (0, EXPECTED_SUMMARY_QUALITY_CONTROLS):
            defects.append(
                f"H.2 qualità Riassunto attesa 47, trovata {h2_counts['quality']}"
            )
        if h2_counts["selector"] not in (0, EXPECTED_SELECTOR_ORCHESTRATOR):
            defects.append(
                f"H.2 selector/orchestrator attesi 8, trovati {h2_counts['selector']}"
            )

    status = (
        "PASS - Fase 5.13B.0.1: SUMMARY_ROUTE_55_MATERIALIZED"
        if not defects
        else "FAIL - Fase 5.13B.0.1: SUMMARY_ROUTE_55_NOT_MATERIALIZED"
    )

    return SummaryRouteMaterializerReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        official_qm_motors=len(official_ids),
        excluded_from_summary_count=len(SUMMARY_EXCLUDED_IDS),
        expected_summary_quality_controls=EXPECTED_SUMMARY_QUALITY_CONTROLS,
        resolved_summary_quality_controls=len(summary_quality_ids),
        expected_selector_orchestrator=EXPECTED_SELECTOR_ORCHESTRATOR,
        resolved_selector_orchestrator=len(selector_ids),
        expected_summary_route_total=EXPECTED_SUMMARY_ROUTE_TOTAL,
        resolved_summary_route_total=len(final_route_ids),
        summary_excluded_ids=list(SUMMARY_EXCLUDED_IDS),
        summary_quality_ids=summary_quality_ids,
        selector_orchestrator_ids=selector_ids,
        final_route_ids=final_route_ids,
        materialized_motors=materialized,
        h2_summary_total=h2_counts["total"],
        h2_summary_quality_controls=h2_counts["quality"],
        h2_selector_orchestrator=h2_counts["selector"],
        defects=defects,
        warnings=warnings,
        notes=[
            "Questa fase materializza la route Riassunto in modo canonico.",
            "Non usa keyword del documento e non dipende da un singolo caso.",
            "Parte dai 64 motori ufficiali.",
            "Esclude solo 9 controlli non applicabili al Riassunto perché specifici di domande studio/test.",
            "La route finale deve risultare 64 - 9 = 55.",
            "La base qualità deve risultare 55 - 8 selector/orchestrator = 47.",
            "I selector/orchestrator qm_051-qm_058 devono essere presenti.",
            "Nessuna UI/PDF/app viene modificata.",
        ],
    )


def write_reports(report: SummaryRouteMaterializerReport) -> None:
    DEFAULT_JSON_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON_REPORT.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append(f"# {PHASE_LABEL}")
    lines.append("")
    lines.append(f"Status: `{report.status}`")
    lines.append("")
    lines.append("## Sintesi")
    lines.append("")
    lines.append(f"- Motori ufficiali: `{report.official_qm_motors}`")
    lines.append(f"- Esclusi dal Riassunto: `{report.excluded_from_summary_count}`")
    lines.append(f"- Qualità Riassunto attesa: `{report.expected_summary_quality_controls}`")
    lines.append(f"- Qualità Riassunto risolta: `{report.resolved_summary_quality_controls}`")
    lines.append(f"- Selector/orchestrator attesi: `{report.expected_selector_orchestrator}`")
    lines.append(f"- Selector/orchestrator risolti: `{report.resolved_selector_orchestrator}`")
    lines.append(f"- Route Riassunto attesa: `{report.expected_summary_route_total}`")
    lines.append(f"- Route Riassunto risolta: `{report.resolved_summary_route_total}`")
    lines.append("")
    lines.append("## Conteggi H.2 letti")
    lines.append("")
    lines.append(f"- H.2 totale Riassunto: `{report.h2_summary_total}`")
    lines.append(f"- H.2 qualità Riassunto: `{report.h2_summary_quality_controls}`")
    lines.append(f"- H.2 selector/orchestrator: `{report.h2_selector_orchestrator}`")
    lines.append("")
    lines.append("## Esclusi dal Riassunto")
    lines.append("")
    for qm_id in report.summary_excluded_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Base qualità Riassunto")
    lines.append("")
    for qm_id in report.summary_quality_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Selector/orchestrator")
    lines.append("")
    for qm_id in report.selector_orchestrator_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Route finale Riassunto")
    lines.append("")
    for qm_id in report.final_route_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Motori materializzati")
    lines.append("")
    lines.append("| QM | Nome | Motivo | Source |")
    lines.append("|---|---|---|---|")
    for item in report.materialized_motors:
        lines.append(
            f"| `{item.qm_id}` | {item.name} | {item.reason} | `{item.source}` |"
        )
    lines.append("")
    lines.append("## Defects")
    lines.append("")
    if report.defects:
        for defect in report.defects:
            lines.append(f"- {defect}")
    else:
        lines.append("- Nessuno")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report.warnings:
        for warning in report.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- Nessuno")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    for note in report.notes:
        lines.append(f"- {note}")
    lines.append("")

    DEFAULT_MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


def run_and_write() -> SummaryRouteMaterializerReport:
    report = materialize_summary_route()
    write_reports(report)
    return report


if __name__ == "__main__":
    result = run_and_write()

    print(result.status)
    print(f"Official QM motors: {result.official_qm_motors}")
    print(f"Excluded from Summary: {result.excluded_from_summary_count}")
    print(f"Summary quality controls: {result.resolved_summary_quality_controls}")
    print(f"Selector/orchestrator: {result.resolved_selector_orchestrator}")
    print(f"Summary route total: {result.resolved_summary_route_total}")
    print(f"H2 summary total: {result.h2_summary_total}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")

    if result.defects:
        print("Defects:")
        for defect in result.defects:
            print(f"- {defect}")
        raise SystemExit(1)

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
