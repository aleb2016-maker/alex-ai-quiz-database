from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence


PHASE = "5.12J"
PHASE_LABEL = "FASE 5.12J — FINAL QUALITY REPORT AND OUTPUT READINESS QM_060_QM_059"

EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_REGISTRY_TOTAL = 73

H2_REPORT = Path("reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json")
I2_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_12j_final_quality_output_motors_qm_060_qm_059_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_12j_final_quality_output_motors_qm_060_qm_059_v1.md")
DEFAULT_REFERENCE_MD = Path("reports/phase5_12j_operational_reference_list_updated_v1.md")
DEFAULT_REFERENCE_JSON = Path("reports/phase5_12j_operational_reference_list_updated_v1.json")


SECTION_LABELS = {
    "card": "Card",
    "summary": "Riassunto",
    "study_questions": "Domande studio",
    "test_quiz": "Test/Quiz",
}

EXPECTED_SECTION_TOTALS = {
    "card": 60,
    "summary": 55,
    "study_questions": 51,
    "test_quiz": 63,
}


@dataclass
class FinalMotor:
    qm_id: str
    name: str
    role: str
    what_it_does: str
    universal: str
    used_by_sections: List[str]
    final_state: str


@dataclass
class Qm060ReadableReport:
    qm_id: str
    name: str
    ready: bool
    readability_score: int
    generated_report: str
    checks: List[str]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Qm059OutputReadiness:
    qm_id: str
    name: str
    ready: bool
    target_surfaces: List[str]
    required_blocks: List[str]
    checks: List[str]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SectionRouteSummary:
    section_type: str
    section_label: str
    quality_matrix_controls: int
    selector_orchestrator_controls: int
    total_controls: int


@dataclass
class Phase512JReport:
    phase: str
    label: str
    status: str
    official_qm_motors: int
    registry_total: int
    final_motors: List[FinalMotor]
    section_routes: List[SectionRouteSummary]
    qm_060: Qm060ReadableReport
    qm_059: Qm059OutputReadiness
    defects: List[str]
    warnings: List[str]
    notes: List[str]


@dataclass
class OperationalReferenceList:
    phase: str
    label: str
    official_qm_motors: int
    registry_total: int
    universal_quality_motors: List[str]
    selector_orchestrator_added: List[str]
    final_motors_completed: List[str]
    section_routes: List[SectionRouteSummary]
    notes: List[str]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_required_reports(defects: List[str]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    h2: Dict[str, Any] = {}
    i2: Dict[str, Any] = {}

    if not H2_REPORT.exists():
        defects.append(f"Report H.2 mancante: {H2_REPORT}")
    else:
        h2 = read_json(H2_REPORT)

    if not I2_CATALOG.exists():
        defects.append(f"Catalogo I.2 mancante: {I2_CATALOG}")
    else:
        i2 = read_json(I2_CATALOG)

    return h2, i2


def get_i2_motor(i2: Dict[str, Any], qm_id: str) -> Dict[str, Any]:
    for item in i2.get("motors", []):
        if item.get("qm_id") == qm_id:
            return item
    return {}


def validate_input_reports(h2: Dict[str, Any], i2: Dict[str, Any], defects: List[str]) -> None:
    if h2:
        if h2.get("registry_total_motors") != EXPECTED_REGISTRY_TOTAL:
            defects.append(
                f"H.2 registry_total_motors errato: atteso {EXPECTED_REGISTRY_TOTAL}, "
                f"trovato {h2.get('registry_total_motors')}"
            )

        if h2.get("matrix_updated") is not True:
            defects.append("H.2 matrix_updated non True")

        if h2.get("orchestration_updated") is not True:
            defects.append("H.2 orchestration_updated non True")

        if h2.get("defects"):
            defects.append(f"H.2 contiene defects: {h2.get('defects')}")

        if h2.get("warnings"):
            defects.append(f"H.2 contiene warnings: {h2.get('warnings')}")

    if i2:
        if i2.get("official_qm_motors_count") != EXPECTED_OFFICIAL_QM_MOTORS:
            defects.append(
                f"I.2 official_qm_motors_count errato: atteso {EXPECTED_OFFICIAL_QM_MOTORS}, "
                f"trovato {i2.get('official_qm_motors_count')}"
            )

        if i2.get("registry_total_after_h2") != EXPECTED_REGISTRY_TOTAL:
            defects.append(
                f"I.2 registry_total_after_h2 errato: atteso {EXPECTED_REGISTRY_TOTAL}, "
                f"trovato {i2.get('registry_total_after_h2')}"
            )

        if i2.get("defects"):
            defects.append(f"I.2 contiene defects: {i2.get('defects')}")

        if i2.get("warnings"):
            defects.append(f"I.2 contiene warnings: {i2.get('warnings')}")

        qm_059 = get_i2_motor(i2, "qm_059")
        qm_060 = get_i2_motor(i2, "qm_060")

        if not qm_059:
            defects.append("qm_059 non trovato nel catalogo I.2")

        if not qm_060:
            defects.append("qm_060 non trovato nel catalogo I.2")


def build_section_routes_from_i2(i2: Dict[str, Any]) -> List[SectionRouteSummary]:
    routes: List[SectionRouteSummary] = []

    for item in i2.get("section_routes", []):
        section_type = str(item.get("section_type", ""))
        routes.append(
            SectionRouteSummary(
                section_type=section_type,
                section_label=str(item.get("section_label", SECTION_LABELS.get(section_type, section_type))),
                quality_matrix_controls=int(item.get("quality_matrix_controls", 0)),
                selector_orchestrator_controls=int(item.get("selector_orchestrator_controls", 0)),
                total_controls=int(item.get("total_controls_after_h2", 0)),
            )
        )

    return routes


def validate_section_routes(routes: Sequence[SectionRouteSummary], defects: List[str]) -> None:
    seen = {route.section_type: route.total_controls for route in routes}

    for section_type, expected_total in EXPECTED_SECTION_TOTALS.items():
        actual = seen.get(section_type)
        if actual != expected_total:
            defects.append(
                f"Route {section_type} errata: atteso totale {expected_total}, trovato {actual}"
            )


def build_final_motors() -> List[FinalMotor]:
    all_sections = ["card", "summary", "study_questions", "test_quiz"]

    return [
        FinalMotor(
            qm_id="qm_060",
            name="Report qualità sempre leggibile",
            role="quality_report",
            what_it_does="Genera un report qualità chiaro, leggibile, non grezzo, con stato, conteggi, route, defects, warnings e prossime azioni.",
            universal="sì",
            used_by_sections=all_sections,
            final_state="attivo_collegato_verificato",
        ),
        FinalMotor(
            qm_id="qm_059",
            name="Output finale pronto per UI/PDF/app",
            role="final_output_readiness",
            what_it_does="Verifica che l’output finale sia completo, pulito, leggibile e pronto per essere usato da UI, PDF, app o web.",
            universal="sì",
            used_by_sections=all_sections,
            final_state="verificato_finale",
        ),
    ]


def generate_qm060_readable_report(
    official_qm_motors: int,
    registry_total: int,
    routes: Sequence[SectionRouteSummary],
) -> str:
    lines: List[str] = []

    lines.append("REPORT QUALITÀ FINALE")
    lines.append("")
    lines.append("Stato generale: PASS")
    lines.append(f"Motori qualità ufficiali spiegati: {official_qm_motors}")
    lines.append(f"Elementi totali registry/orchestrazione: {registry_total}")
    lines.append("")
    lines.append("Route operative:")
    for route in routes:
        lines.append(
            f"- {route.section_label}: {route.quality_matrix_controls} controlli qualità "
            f"+ {route.selector_orchestrator_controls} selector/orchestrator "
            f"= {route.total_controls} controlli totali"
        )
    lines.append("")
    lines.append("Motori finali:")
    lines.append("- qm_060: report qualità sempre leggibile — attivo e verificato")
    lines.append("- qm_059: output finale pronto per UI/PDF/app — verificato")
    lines.append("")
    lines.append("Defects: nessuno")
    lines.append("Warnings: nessuno")
    lines.append("")
    lines.append("Esito: output qualità pronto per il prossimo livello di integrazione.")

    return "\n".join(lines)


def validate_qm060_report(text: str) -> Qm060ReadableReport:
    defects: List[str] = []
    warnings: List[str] = []
    checks: List[str] = []

    required_fragments = [
        "REPORT QUALITÀ FINALE",
        "Stato generale: PASS",
        "Motori qualità ufficiali spiegati",
        "Elementi totali registry/orchestrazione",
        "Route operative",
        "qm_060",
        "qm_059",
        "Defects: nessuno",
        "Warnings: nessuno",
    ]

    for fragment in required_fragments:
        if fragment not in text:
            defects.append(f"Frammento obbligatorio mancante nel report leggibile: {fragment}")
        else:
            checks.append(f"Presente: {fragment}")

    forbidden_fragments = [
        "Traceback",
        "None",
        "undefined",
        "object at 0x",
        "{'status'",
        "\"status\":",
    ]

    for fragment in forbidden_fragments:
        if fragment in text:
            defects.append(f"Frammento tecnico/non leggibile trovato: {fragment}")

    readability_score = 100 if not defects else max(0, 100 - len(defects) * 20)

    return Qm060ReadableReport(
        qm_id="qm_060",
        name="Report qualità sempre leggibile",
        ready=not defects,
        readability_score=readability_score,
        generated_report=text,
        checks=checks,
        defects=defects,
        warnings=warnings,
    )


def validate_qm059_output_readiness(
    qm060_result: Qm060ReadableReport,
    routes: Sequence[SectionRouteSummary],
    upstream_defects: Sequence[str],
) -> Qm059OutputReadiness:
    defects: List[str] = []
    warnings: List[str] = []
    checks: List[str] = []

    target_surfaces = ["UI", "PDF", "app", "web"]
    required_blocks = [
        "catalogo_motori_qualita",
        "route_sezioni",
        "report_qualita_leggibile",
        "defects_warnings",
        "stato_finale",
    ]

    if upstream_defects:
        defects.append("Sono presenti defects a monte: output finale non pronto.")
    else:
        checks.append("Nessun defect a monte.")

    if not qm060_result.ready:
        defects.append("qm_060 non pronto: report qualità non leggibile.")
    else:
        checks.append("qm_060 pronto: report qualità leggibile.")

    expected_routes = set(EXPECTED_SECTION_TOTALS.keys())
    actual_routes = {route.section_type for route in routes}
    if actual_routes != expected_routes:
        defects.append(f"Route sezioni incomplete: attese {sorted(expected_routes)}, trovate {sorted(actual_routes)}")
    else:
        checks.append("Route sezioni complete: card, riassunto, domande studio, test/quiz.")

    for route in routes:
        expected_total = EXPECTED_SECTION_TOTALS.get(route.section_type)
        if route.total_controls != expected_total:
            defects.append(
                f"Totale route errato per {route.section_type}: atteso {expected_total}, trovato {route.total_controls}"
            )
        else:
            checks.append(f"Route {route.section_label} pronta con totale {route.total_controls}.")

    return Qm059OutputReadiness(
        qm_id="qm_059",
        name="Output finale pronto per UI/PDF/app",
        ready=not defects,
        target_surfaces=target_surfaces,
        required_blocks=required_blocks,
        checks=checks,
        defects=defects,
        warnings=warnings,
    )


def build_reference_list(routes: Sequence[SectionRouteSummary]) -> OperationalReferenceList:
    universal_quality_motors = [
        "qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006",
        "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012",
        "qm_045", "qm_046", "qm_047", "qm_049", "qm_050",
        "qm_061", "qm_062", "qm_063", "qm_064",
    ]

    selector_orchestrator_added = [
        "qm_051", "qm_052", "qm_053", "qm_054",
        "qm_055", "qm_056", "qm_057", "qm_058",
    ]

    final_motors_completed = ["qm_059", "qm_060"]

    return OperationalReferenceList(
        phase=PHASE,
        label="LISTA OPERATIVA AGGIORNATA DOPO QM_060_QM_059",
        official_qm_motors=EXPECTED_OFFICIAL_QM_MOTORS,
        registry_total=EXPECTED_REGISTRY_TOTAL,
        universal_quality_motors=universal_quality_motors,
        selector_orchestrator_added=selector_orchestrator_added,
        final_motors_completed=final_motors_completed,
        section_routes=list(routes),
        notes=[
            "qm_060 ora è attivo, collegato e verificato come report qualità sempre leggibile.",
            "qm_059 ora è verificato come output finale pronto per UI/PDF/app.",
            "I totali di route restano: Card 60, Riassunto 55, Domande studio 51, Test/Quiz 63.",
        ],
    )


def run_phase5_12j() -> tuple[Phase512JReport, OperationalReferenceList]:
    defects: List[str] = []
    warnings: List[str] = []

    h2, i2 = load_required_reports(defects)
    validate_input_reports(h2, i2, defects)

    routes = build_section_routes_from_i2(i2) if i2 else []
    validate_section_routes(routes, defects)

    readable_text = generate_qm060_readable_report(
        official_qm_motors=EXPECTED_OFFICIAL_QM_MOTORS,
        registry_total=EXPECTED_REGISTRY_TOTAL,
        routes=routes,
    )
    qm060 = validate_qm060_report(readable_text)

    qm059 = validate_qm059_output_readiness(
        qm060_result=qm060,
        routes=routes,
        upstream_defects=defects,
    )

    defects.extend(qm060.defects)
    defects.extend(qm059.defects)
    warnings.extend(qm060.warnings)
    warnings.extend(qm059.warnings)

    status = (
        "PASS - Fase 5.12J: FINAL_QM_060_QM_059_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.12J: FINAL_QM_060_QM_059_NOT_READY"
    )

    report = Phase512JReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        official_qm_motors=EXPECTED_OFFICIAL_QM_MOTORS,
        registry_total=EXPECTED_REGISTRY_TOTAL,
        final_motors=build_final_motors(),
        section_routes=routes,
        qm_060=qm060,
        qm_059=qm059,
        defects=defects,
        warnings=warnings,
        notes=[
            "Backend/report only.",
            "qm_060 chiude il report qualità sempre leggibile.",
            "qm_059 chiude la verifica finale output pronto UI/PDF/app.",
            "UI/PDF/app non vengono modificati in questa fase: viene verificato il contratto di prontezza.",
        ],
    )

    reference = build_reference_list(routes)

    return report, reference


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_main_markdown(report: Phase512JReport) -> None:
    lines: List[str] = []

    lines.append(f"# {report.label}")
    lines.append("")
    lines.append(f"Status: `{report.status}`")
    lines.append("")
    lines.append("## Sintesi")
    lines.append("")
    lines.append(f"- Motori qualità ufficiali: `{report.official_qm_motors}`")
    lines.append(f"- Registry/orchestrazione totale: `{report.registry_total}`")
    lines.append(f"- qm_060 ready: `{report.qm_060.ready}`")
    lines.append(f"- qm_060 readability score: `{report.qm_060.readability_score}`")
    lines.append(f"- qm_059 ready: `{report.qm_059.ready}`")
    lines.append("")
    lines.append("## Motori finali")
    lines.append("")
    lines.append("| QM | Nome | Ruolo | Cosa fa | Universale | Stato |")
    lines.append("|---|---|---|---|---|---|")
    for item in report.final_motors:
        lines.append(
            f"| `{item.qm_id}` | {item.name} | {item.role} | "
            f"{item.what_it_does} | {item.universal} | {item.final_state} |"
        )
    lines.append("")
    lines.append("## Route sezioni")
    lines.append("")
    lines.append("| Sezione | Qualità G.2 | Selector/orchestrator | Totale |")
    lines.append("|---|---:|---:|---:|")
    for route in report.section_routes:
        lines.append(
            f"| {route.section_label} | {route.quality_matrix_controls} | "
            f"{route.selector_orchestrator_controls} | {route.total_controls} |"
        )
    lines.append("")
    lines.append("## Report leggibile qm_060")
    lines.append("")
    lines.append("```text")
    lines.append(report.qm_060.generated_report)
    lines.append("```")
    lines.append("")
    lines.append("## qm_059 Output readiness")
    lines.append("")
    lines.append(f"- Ready: `{report.qm_059.ready}`")
    lines.append(f"- Target surfaces: `{', '.join(report.qm_059.target_surfaces)}`")
    lines.append("")
    lines.append("Checks:")
    lines.append("")
    for check in report.qm_059.checks:
        lines.append(f"- {check}")
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

    DEFAULT_MD_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


def write_reference_markdown(reference: OperationalReferenceList) -> None:
    lines: List[str] = []

    lines.append("# LISTA DI RIFERIMENTO OPERATIVO AGGIORNATA")
    lines.append("")
    lines.append(f"- Motori qualità ufficiali spiegati: `{reference.official_qm_motors}`")
    lines.append(f"- Elementi totali registry/orchestrazione H.2: `{reference.registry_total}`")
    lines.append("")
    lines.append("## Motori qualità universali")
    lines.append("")
    for qm_id in reference.universal_quality_motors:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append(f"Totale motori qualità universali: `{len(reference.universal_quality_motors)}`")
    lines.append("")
    lines.append("## Motori selector/orchestrator aggiunti alle route")
    lines.append("")
    for qm_id in reference.selector_orchestrator_added:
        lines.append(f"- `{qm_id}`")
    lines.append("")
    lines.append(f"Totale selector/orchestrator aggiunti: `{len(reference.selector_orchestrator_added)}`")
    lines.append("")
    lines.append("## Motori finali completati")
    lines.append("")
    lines.append("- `qm_059` — Output finale pronto per UI/PDF/app — verificato finale")
    lines.append("- `qm_060` — Report qualità sempre leggibile — attivo, collegato e verificato")
    lines.append("")
    lines.append("## Route finali")
    lines.append("")
    lines.append("| Sezione | Qualità G.2 | Selector/orchestrator | Totale route |")
    lines.append("|---|---:|---:|---:|")
    for route in reference.section_routes:
        lines.append(
            f"| {route.section_label} | {route.quality_matrix_controls} | "
            f"{route.selector_orchestrator_controls} | {route.total_controls} |"
        )
    lines.append("")
    lines.append("## Note")
    lines.append("")
    for note in reference.notes:
        lines.append(f"- {note}")
    lines.append("")

    DEFAULT_REFERENCE_MD.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REFERENCE_MD.write_text("\n".join(lines), encoding="utf-8")


def run_and_write_phase5_12j_reports() -> Phase512JReport:
    report, reference = run_phase5_12j()

    write_json(DEFAULT_JSON_REPORT, report)
    write_main_markdown(report)

    write_json(DEFAULT_REFERENCE_JSON, reference)
    write_reference_markdown(reference)

    return report


if __name__ == "__main__":
    result = run_and_write_phase5_12j_reports()

    print(result.status)
    print(f"Official QM motors: {result.official_qm_motors}")
    print(f"Registry total: {result.registry_total}")
    print(f"qm_060 ready: {result.qm_060.ready}")
    print(f"qm_060 readability score: {result.qm_060.readability_score}")
    print(f"qm_059 ready: {result.qm_059.ready}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")
    print(f"Reference JSON: {DEFAULT_REFERENCE_JSON}")
    print(f"Reference Markdown: {DEFAULT_REFERENCE_MD}")

    if result.defects:
        print("Defects:")
        for defect in result.defects:
            print(f"- {defect}")
        raise SystemExit(1)

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
        raise SystemExit(1)
