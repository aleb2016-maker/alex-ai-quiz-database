from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set


PHASE = "5.13C.0.1"
PHASE_LABEL = "FASE 5.13C.0.1 — STUDY QUESTIONS ROUTE MATERIALIZER CANONICAL"

EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_STUDY_QUALITY_CONTROLS = 43
EXPECTED_SELECTOR_ORCHESTRATOR = 8
EXPECTED_STUDY_ROUTE_TOTAL = 51

OFFICIAL_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")
DEFAULT_JSON_REPORT = Path("reports/phase5_13c01_study_questions_route_materializer_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_13c01_study_questions_route_materializer_v1.md")

QM_RE = re.compile(r"\bqm_\d{3}\b", re.I)

SELECTOR_ORCHESTRATOR_IDS = [f"qm_{number:03d}" for number in range(51, 59)]

# Route Domande studio:
# 64 motori ufficiali - 13 esclusi = 51 finali.
#
# Esclusi:
# - qm_016: spiegazioni test chiare, specifico Test/Quiz.
# - qm_023, qm_024, qm_025: card scritte/non corte/non compresse, specifici Card.
# - qm_027, qm_028, qm_029, qm_030, qm_031, qm_032: specifici Riassunto/Card/fonti/layout grafico.
# - qm_036, qm_037: risposta corretta interna/visibile, specifici Test/Quiz.
# - qm_041: distrattori forti, specifico Test/Quiz.
#
# Nota: qm_026 resta incluso perché "messaggio chiave completo" è utile anche alle risposte guida.
STUDY_EXCLUDED_IDS = [
    "qm_016",
    "qm_023",
    "qm_024",
    "qm_025",
    "qm_027",
    "qm_028",
    "qm_029",
    "qm_030",
    "qm_031",
    "qm_032",
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
class StudyRouteMaterializerReport:
    phase: str
    label: str
    status: str
    official_qm_motors: int
    excluded_from_study_count: int
    expected_study_quality_controls: int
    resolved_study_quality_controls: int
    expected_selector_orchestrator: int
    resolved_selector_orchestrator: int
    expected_study_route_total: int
    resolved_study_route_total: int
    study_excluded_ids: List[str]
    study_quality_ids: List[str]
    selector_orchestrator_ids: List[str]
    final_route_ids: List[str]
    materialized_motors: List[MaterializedMotor]
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


def materialize_study_route() -> StudyRouteMaterializerReport:
    defects: List[str] = []
    warnings: List[str] = []

    if not OFFICIAL_CATALOG.exists():
        raise FileNotFoundError(f"Catalogo ufficiale mancante: {OFFICIAL_CATALOG}")

    motors = load_catalog_motors()
    official_ids = load_official_qm_ids(motors)
    motor_by_id = get_motor_by_id(motors)

    if len(official_ids) != EXPECTED_OFFICIAL_QM_MOTORS:
        defects.append(
            f"Motori ufficiali attesi 64, trovati {len(official_ids)}"
        )

    missing_exclusions = [
        qm_id for qm_id in STUDY_EXCLUDED_IDS
        if qm_id not in official_ids
    ]

    if missing_exclusions:
        defects.append(
            "Esclusioni Domande studio non presenti nel catalogo ufficiale: "
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
        if qm_id not in set(STUDY_EXCLUDED_IDS)
    ]
    final_route_ids = sort_qm_ids(final_route_ids)

    study_quality_ids = [
        qm_id for qm_id in final_route_ids
        if qm_id not in set(selector_ids)
    ]
    study_quality_ids = sort_qm_ids(study_quality_ids)

    materialized: List[MaterializedMotor] = []

    for qm_id in final_route_ids:
        motor = motor_by_id.get(qm_id, {})
        if qm_id in selector_ids:
            reason = "selector_orchestrator"
        else:
            reason = "study_canonical_quality"

        materialized.append(
            MaterializedMotor(
                qm_id=qm_id,
                name=motor_name(motor),
                reason=reason,
                source=str(OFFICIAL_CATALOG),
            )
        )

    if len(STUDY_EXCLUDED_IDS) != 13:
        defects.append(
            f"Le esclusioni Domande studio devono essere 13, trovate {len(STUDY_EXCLUDED_IDS)}"
        )

    if len(study_quality_ids) != EXPECTED_STUDY_QUALITY_CONTROLS:
        defects.append(
            f"Base qualità Domande studio deve essere 43, trovata {len(study_quality_ids)}"
        )

    if len(selector_ids) != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(
            f"Selector/orchestrator devono essere 8, trovati {len(selector_ids)}"
        )

    if len(final_route_ids) != EXPECTED_STUDY_ROUTE_TOTAL:
        defects.append(
            f"Route finale Domande studio deve essere 51, trovata {len(final_route_ids)}"
        )

    status = (
        "PASS - Fase 5.13C.0.1: STUDY_QUESTIONS_ROUTE_51_MATERIALIZED"
        if not defects
        else "FAIL - Fase 5.13C.0.1: STUDY_QUESTIONS_ROUTE_51_NOT_MATERIALIZED"
    )

    return StudyRouteMaterializerReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        official_qm_motors=len(official_ids),
        excluded_from_study_count=len(STUDY_EXCLUDED_IDS),
        expected_study_quality_controls=EXPECTED_STUDY_QUALITY_CONTROLS,
        resolved_study_quality_controls=len(study_quality_ids),
        expected_selector_orchestrator=EXPECTED_SELECTOR_ORCHESTRATOR,
        resolved_selector_orchestrator=len(selector_ids),
        expected_study_route_total=EXPECTED_STUDY_ROUTE_TOTAL,
        resolved_study_route_total=len(final_route_ids),
        study_excluded_ids=list(STUDY_EXCLUDED_IDS),
        study_quality_ids=study_quality_ids,
        selector_orchestrator_ids=selector_ids,
        final_route_ids=final_route_ids,
        materialized_motors=materialized,
        defects=defects,
        warnings=warnings,
        notes=[
            "Questa fase materializza la route Domande studio in modo canonico.",
            "Non usa keyword del documento e non dipende da un singolo caso.",
            "Parte dai 64 motori ufficiali.",
            "Esclude solo 13 controlli non applicabili alle Domande studio perché specifici di Card/Riassunto/Test.",
            "La route finale deve risultare 64 - 13 = 51.",
            "La base qualità deve risultare 51 - 8 selector/orchestrator = 43.",
            "I selector/orchestrator qm_051-qm_058 devono essere presenti.",
            "Nessuna UI/PDF/app viene modificata.",
        ],
    )


def write_reports(report: StudyRouteMaterializerReport) -> None:
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
    lines.append(f"- Esclusi dalle Domande studio: `{report.excluded_from_study_count}`")
    lines.append(f"- Qualità Domande studio attesa: `{report.expected_study_quality_controls}`")
    lines.append(f"- Qualità Domande studio risolta: `{report.resolved_study_quality_controls}`")
    lines.append(f"- Selector/orchestrator attesi: `{report.expected_selector_orchestrator}`")
    lines.append(f"- Selector/orchestrator risolti: `{report.resolved_selector_orchestrator}`")
    lines.append(f"- Route Domande studio attesa: `{report.expected_study_route_total}`")
    lines.append(f"- Route Domande studio risolta: `{report.resolved_study_route_total}`")
    lines.append("")
    lines.append("## Esclusi dalle Domande studio")
    lines.append("")
    for qm_id in report.study_excluded_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Base qualità Domande studio")
    lines.append("")
    for qm_id in report.study_quality_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Selector/orchestrator")
    lines.append("")
    for qm_id in report.selector_orchestrator_ids:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append("## Route finale Domande studio")
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


def run_and_write() -> StudyRouteMaterializerReport:
    report = materialize_study_route()
    write_reports(report)
    return report


if __name__ == "__main__":
    result = run_and_write()

    print(result.status)
    print(f"Official QM motors: {result.official_qm_motors}")
    print(f"Excluded from Study Questions: {result.excluded_from_study_count}")
    print(f"Study quality controls: {result.resolved_study_quality_controls}")
    print(f"Selector/orchestrator: {result.resolved_selector_orchestrator}")
    print(f"Study route total: {result.resolved_study_route_total}")
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
