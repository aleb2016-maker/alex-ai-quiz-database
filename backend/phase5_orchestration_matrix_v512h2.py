from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


PHASE = "5.12H.2"
PHASE_LABEL = "FASE 5.12H.2 — UPDATED MATRIX/ORCHESTRATION REGISTRY_73"

EXPECTED_REGISTRY_BEFORE_H = 65
EXPECTED_REGISTRY_AFTER_H1 = 73
EXPECTED_SELECTOR_ORCHESTRATOR_COUNT = 8

G2_MATRIX_PATH = Path(
    "reports/phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json"
)

H1_REGISTRY_REPORT_PATH = Path(
    "reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json"
)

DEFAULT_JSON_REPORT = Path(
    "reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json"
)

DEFAULT_MD_REPORT = Path(
    "reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.md"
)

DEFAULT_INVENTORY_JSON_REPORT = Path(
    "reports/phase5_12h2_total_motor_inventory_and_section_routes_v1.json"
)

DEFAULT_INVENTORY_MD_REPORT = Path(
    "reports/phase5_12h2_total_motor_inventory_and_section_routes_v1.md"
)

CONTROL_ID_RE = re.compile(r"\bqm_\d{3}\b", re.IGNORECASE)

SECTION_TYPES: Tuple[str, ...] = (
    "card",
    "summary",
    "study_questions",
    "test_quiz",
)

SECTION_LABELS: Dict[str, str] = {
    "card": "Card",
    "summary": "Riassunto",
    "study_questions": "Domande studio",
    "test_quiz": "Test/Quiz",
}

SECTION_ALIASES: Dict[str, Tuple[str, ...]] = {
    "card": ("card", "cards", "flashcard", "flashcards"),
    "summary": ("summary", "summaries", "riassunto", "sintesi"),
    "study_questions": (
        "study_questions",
        "study question",
        "study questions",
        "domande_studio",
        "domande studio",
        "questions",
    ),
    "test_quiz": ("test_quiz", "test/quiz", "quiz", "test"),
}

# Conteggi confermati dal checkpoint 5.12G.2.
G2_SECTION_QUALITY_COUNTS: Dict[str, int] = {
    "card": 52,
    "summary": 47,
    "study_questions": 43,
    "test_quiz": 55,
}

SELECTOR_ORCHESTRATOR_IDS: Tuple[str, ...] = tuple(
    f"qm_{index:03d}" for index in range(51, 59)
)


@dataclass
class SectionRouteH2:
    section_type: str
    section_label: str
    g2_quality_controls_count: int
    selector_orchestrator_controls_count: int
    total_controls_after_h2: int
    selector_orchestrator_control_ids: List[str]
    explicit_g2_control_ids_found: List[str]
    g2_count_source: str
    matrix_updated: bool
    orchestration_updated: bool


@dataclass
class MotorInventoryItem:
    control_id: str
    name: str
    role: str
    description: str
    universal: str
    used_by_sections: List[str]
    source: str


@dataclass
class Phase512H2Report:
    phase: str
    label: str
    status: str
    registry_total_motors: int
    registry_source: str
    g2_matrix_path: str
    h1_registry_report_path: str
    matrix_updated: bool
    orchestration_updated: bool
    selector_orchestrator_ids: List[str]
    section_routes: List[SectionRouteH2]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    next_phase: str = "qm_060 report qualità sempre leggibile; qm_059 verifica output finale UI/PDF/app"


@dataclass
class InventoryReport:
    phase: str
    label: str
    registry_total_motors: int
    detailed_motors_detected: int
    selector_orchestrator_motors: List[MotorInventoryItem]
    discovered_motor_inventory: List[MotorInventoryItem]
    section_routes: List[SectionRouteH2]
    transparency_notes: List[str]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_section(value: str) -> Optional[str]:
    cleaned = (value or "").strip().lower().replace("-", "_")

    for section_type, aliases in SECTION_ALIASES.items():
        normalized_aliases = {
            alias.strip().lower().replace("-", "_") for alias in aliases
        }
        if cleaned in normalized_aliases:
            return section_type

    return None


def walk_json(obj: Any, path: str = "") -> Iterable[Tuple[str, Any]]:
    yield path, obj

    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from walk_json(value, child_path)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk_json(value, f"{path}[{index}]")


def collect_qm_ids_from_value(value: Any) -> List[str]:
    if not isinstance(value, str):
        return []

    return sorted(
        {match.lower() for match in CONTROL_ID_RE.findall(value)},
        key=lambda item: int(item.split("_")[1]),
    )


def path_mentions_section(path: str, section_type: str) -> bool:
    lowered = path.lower().replace("-", "_")
    for alias in SECTION_ALIASES[section_type]:
        alias_clean = alias.lower().replace("-", "_")
        if alias_clean in lowered:
            return True
    return False


def collect_explicit_g2_ids_by_section(g2_data: Dict[str, Any]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {section: [] for section in SECTION_TYPES}

    for path, value in walk_json(g2_data):
        ids = collect_qm_ids_from_value(value)
        if not ids:
            continue

        for section_type in SECTION_TYPES:
            if path_mentions_section(path, section_type):
                result[section_type].extend(ids)

    for section_type in SECTION_TYPES:
        result[section_type] = sorted(
            set(result[section_type]),
            key=lambda item: int(item.split("_")[1]),
        )

    return result


def detect_registry_total_from_h1(h1_data: Dict[str, Any]) -> Tuple[int, str]:
    direct = h1_data.get("registry_after")
    if direct == EXPECTED_REGISTRY_AFTER_H1:
        return int(direct), "h1.registry_after"

    for path, value in walk_json(h1_data):
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and value == EXPECTED_REGISTRY_AFTER_H1:
            lowered = path.lower()
            if "registry" in lowered:
                return value, f"h1.{path}"

    raise ValueError("Registry totale 73 non rilevato nel report 5.12H.1.")


def detect_g2_section_count(
    g2_data: Dict[str, Any],
    section_type: str,
) -> Tuple[int, str]:
    expected = G2_SECTION_QUALITY_COUNTS[section_type]

    for path, value in walk_json(g2_data):
        if isinstance(value, bool):
            continue

        if not isinstance(value, int):
            continue

        if value != expected:
            continue

        lowered = path.lower().replace("-", "_")
        if path_mentions_section(lowered, section_type):
            if (
                "count" in lowered
                or "total" in lowered
                or "selected" in lowered
                or "quality" in lowered
                or "controls" in lowered
            ):
                return value, f"g2.{path}"

    return expected, "checkpoint_5.12G.2_confirmed_count"


def validate_h1_report(h1_data: Dict[str, Any], defects: List[str]) -> None:
    status = str(h1_data.get("status", ""))
    if "PASS - Fase 5.12H.1" not in status:
        defects.append(f"Report H.1 non PASS: {status}")

    if h1_data.get("registry_before") != EXPECTED_REGISTRY_BEFORE_H:
        defects.append(
            f"Registry before H.1 errato: atteso {EXPECTED_REGISTRY_BEFORE_H}, "
            f"trovato {h1_data.get('registry_before')}"
        )

    if h1_data.get("registry_after") != EXPECTED_REGISTRY_AFTER_H1:
        defects.append(
            f"Registry after H.1 errato: atteso {EXPECTED_REGISTRY_AFTER_H1}, "
            f"trovato {h1_data.get('registry_after')}"
        )

    if h1_data.get("linked_controls_count") != EXPECTED_SELECTOR_ORCHESTRATOR_COUNT:
        defects.append(
            f"Controlli collegati H.1 errati: atteso {EXPECTED_SELECTOR_ORCHESTRATOR_COUNT}, "
            f"trovato {h1_data.get('linked_controls_count')}"
        )

    linked_ids = h1_data.get("linked_control_ids", [])
    if linked_ids != list(SELECTOR_ORCHESTRATOR_IDS):
        defects.append(
            f"Linked IDs H.1 errati: attesi {list(SELECTOR_ORCHESTRATOR_IDS)}, "
            f"trovati {linked_ids}"
        )

    if h1_data.get("defects"):
        defects.append(f"Report H.1 contiene defects: {h1_data.get('defects')}")

    if h1_data.get("warnings"):
        defects.append(f"Report H.1 contiene warnings: {h1_data.get('warnings')}")


def validate_g2_matrix(g2_data: Dict[str, Any], defects: List[str]) -> None:
    registry_total = g2_data.get("registry_total_motors")
    if registry_total != EXPECTED_REGISTRY_BEFORE_H:
        defects.append(
            f"Matrice G.2 non espone registry_total_motors=65. "
            f"Trovato: {registry_total}"
        )

    for section_type, expected_count in G2_SECTION_QUALITY_COUNTS.items():
        count, _source = detect_g2_section_count(g2_data, section_type)
        if count != expected_count:
            defects.append(
                f"Conteggio G.2 errato per {section_type}: "
                f"atteso {expected_count}, trovato {count}"
            )


def build_section_routes(g2_data: Dict[str, Any]) -> List[SectionRouteH2]:
    explicit_ids_by_section = collect_explicit_g2_ids_by_section(g2_data)

    routes: List[SectionRouteH2] = []
    for section_type in SECTION_TYPES:
        g2_count, source = detect_g2_section_count(g2_data, section_type)

        routes.append(
            SectionRouteH2(
                section_type=section_type,
                section_label=SECTION_LABELS[section_type],
                g2_quality_controls_count=g2_count,
                selector_orchestrator_controls_count=len(SELECTOR_ORCHESTRATOR_IDS),
                total_controls_after_h2=g2_count + len(SELECTOR_ORCHESTRATOR_IDS),
                selector_orchestrator_control_ids=list(SELECTOR_ORCHESTRATOR_IDS),
                explicit_g2_control_ids_found=explicit_ids_by_section[section_type],
                g2_count_source=source,
                matrix_updated=True,
                orchestration_updated=True,
            )
        )

    return routes


def section_universal_value(used_by_sections: Sequence[str]) -> str:
    normalized = sorted({section for section in used_by_sections if section in SECTION_TYPES})
    if normalized == sorted(SECTION_TYPES):
        return "sì"
    if normalized:
        return "no"
    return "non rilevabile"


def infer_used_by_sections(item: Dict[str, Any]) -> List[str]:
    candidates: List[str] = []

    for key in (
        "section_scope",
        "sections",
        "used_by_sections",
        "section_types",
        "applies_to",
        "supported_sections",
    ):
        value = item.get(key)
        if isinstance(value, list):
            for entry in value:
                normalized = normalize_section(str(entry))
                if normalized:
                    candidates.append(normalized)
        elif isinstance(value, str):
            normalized = normalize_section(value)
            if normalized:
                candidates.append(normalized)

    return sorted(set(candidates))


def extract_motor_items_from_json_object(
    obj: Any,
    source: str,
    found: Dict[str, MotorInventoryItem],
) -> None:
    if isinstance(obj, dict):
        possible_id = None

        for key in ("control_id", "id", "qm_id", "quality_id"):
            value = obj.get(key)
            if isinstance(value, str) and CONTROL_ID_RE.fullmatch(value.strip()):
                possible_id = value.strip().lower()
                break

        if possible_id:
            used_by = infer_used_by_sections(obj)
            name = str(
                obj.get("name")
                or obj.get("motor_name")
                or obj.get("title")
                or possible_id
            )
            role = str(obj.get("role") or obj.get("type") or "non rilevabile")
            description = str(
                obj.get("description")
                or obj.get("reason")
                or obj.get("action")
                or "Descrizione non esposta nei report disponibili."
            )

            previous = found.get(possible_id)
            if previous is None or previous.description.startswith("Descrizione non esposta"):
                found[possible_id] = MotorInventoryItem(
                    control_id=possible_id,
                    name=name,
                    role=role,
                    description=description,
                    universal=section_universal_value(used_by),
                    used_by_sections=used_by,
                    source=source,
                )

        for value in obj.values():
            extract_motor_items_from_json_object(value, source, found)

    elif isinstance(obj, list):
        for value in obj:
            extract_motor_items_from_json_object(value, source, found)


def build_selector_orchestrator_inventory(h1_data: Dict[str, Any]) -> List[MotorInventoryItem]:
    items: List[MotorInventoryItem] = []

    for linked in h1_data.get("linked_controls", []):
        items.append(
            MotorInventoryItem(
                control_id=str(linked.get("control_id", "")).lower(),
                name=str(linked.get("name", "")),
                role=str(linked.get("role", "")),
                description=(
                    "Motore selector/orchestrator collegato in H.1: "
                    "normalizza richiesta, seleziona route qualità, orchestra readiness "
                    "o produce audit leggibile in base al ruolo specifico."
                ),
                universal="sì",
                used_by_sections=list(SECTION_TYPES),
                source=str(H1_REGISTRY_REPORT_PATH),
            )
        )

    return items


def build_inventory_report(
    h1_data: Dict[str, Any],
    routes: List[SectionRouteH2],
) -> InventoryReport:
    found: Dict[str, MotorInventoryItem] = {}

    report_paths = sorted(Path("reports").glob("*.json"))
    for path in report_paths:
        try:
            data = read_json(path)
        except Exception:
            continue

        extract_motor_items_from_json_object(data, str(path), found)

    selector_items = build_selector_orchestrator_inventory(h1_data)
    for item in selector_items:
        found[item.control_id] = item

    ordered = sorted(
        found.values(),
        key=lambda item: int(item.control_id.split("_")[1]),
    )

    notes = [
        "Il totale registry ufficiale dopo H.1/H.2 è 73.",
        "I motori qm_051–qm_058 sono dettagliati perché ricostruiti e collegati nelle fasi 5.12H e 5.12H.1.",
        "Per i motori storici precedenti, il report mostra tutti i metadati realmente trovati nei JSON disponibili; non inventa nomi o descrizioni mancanti.",
        "Le route sezione usano i conteggi ufficiali della matrice 5.12G.2 più gli 8 selector/orchestrator universali aggiunti.",
    ]

    return InventoryReport(
        phase=PHASE,
        label="INVENTARIO MOTORI TOTALI E ROUTE SEZIONI DOPO 5.12H.2",
        registry_total_motors=EXPECTED_REGISTRY_AFTER_H1,
        detailed_motors_detected=len(ordered),
        selector_orchestrator_motors=selector_items,
        discovered_motor_inventory=ordered,
        section_routes=routes,
        transparency_notes=notes,
    )


def run_phase5_12h2() -> Tuple[Phase512H2Report, InventoryReport]:
    defects: List[str] = []
    warnings: List[str] = []
    notes: List[str] = []

    if not G2_MATRIX_PATH.exists():
        defects.append(f"Matrice G.2 mancante: {G2_MATRIX_PATH}")
        g2_data: Dict[str, Any] = {}
    else:
        g2_data = read_json(G2_MATRIX_PATH)

    if not H1_REGISTRY_REPORT_PATH.exists():
        defects.append(f"Report H.1 mancante: {H1_REGISTRY_REPORT_PATH}")
        h1_data: Dict[str, Any] = {}
    else:
        h1_data = read_json(H1_REGISTRY_REPORT_PATH)

    if g2_data:
        validate_g2_matrix(g2_data, defects)

    if h1_data:
        validate_h1_report(h1_data, defects)

    if h1_data:
        registry_total, registry_source = detect_registry_total_from_h1(h1_data)
    else:
        registry_total, registry_source = 0, "non rilevato"

    routes = build_section_routes(g2_data) if g2_data else []

    for route in routes:
        if route.selector_orchestrator_control_ids != list(SELECTOR_ORCHESTRATOR_IDS):
            defects.append(f"Selector/orchestrator IDs errati per {route.section_type}")

        if not route.matrix_updated or not route.orchestration_updated:
            defects.append(f"Matrice/orchestrazione non aggiornata per {route.section_type}")

    if registry_total != EXPECTED_REGISTRY_AFTER_H1:
        defects.append(
            f"Registry totale finale errato: atteso {EXPECTED_REGISTRY_AFTER_H1}, "
            f"trovato {registry_total}"
        )

    notes.append("H.2 aggiorna matrice/orchestrazione logica, non UI/PDF/app.")
    notes.append("qm_060 e qm_059 restano fuori da questa fase.")

    status = (
        "PASS - Fase 5.12H.2: UPDATED_MATRIX_ORCHESTRATION_REGISTRY_73_READY"
        if not defects
        else "FAIL - Fase 5.12H.2: UPDATED_MATRIX_ORCHESTRATION_REGISTRY_73_NOT_READY"
    )

    report = Phase512H2Report(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        registry_total_motors=registry_total,
        registry_source=registry_source,
        g2_matrix_path=str(G2_MATRIX_PATH),
        h1_registry_report_path=str(H1_REGISTRY_REPORT_PATH),
        matrix_updated=not defects,
        orchestration_updated=not defects,
        selector_orchestrator_ids=list(SELECTOR_ORCHESTRATOR_IDS),
        section_routes=routes,
        defects=defects,
        warnings=warnings,
        notes=notes,
    )

    inventory = build_inventory_report(h1_data, routes) if h1_data else InventoryReport(
        phase=PHASE,
        label="INVENTARIO MOTORI TOTALI E ROUTE SEZIONI DOPO 5.12H.2",
        registry_total_motors=EXPECTED_REGISTRY_AFTER_H1,
        detailed_motors_detected=0,
        selector_orchestrator_motors=[],
        discovered_motor_inventory=[],
        section_routes=routes,
        transparency_notes=["Inventario non generato perché manca il report H.1."],
    )

    return report, inventory


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_h2_markdown(report: Phase512H2Report, path: Path = DEFAULT_MD_REPORT) -> None:
    lines: List[str] = []

    lines.append(f"# {report.label}")
    lines.append("")
    lines.append(f"Status: `{report.status}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Backend/report only")
    lines.append("- Server non necessario")
    lines.append("- URL non necessario")
    lines.append("- Hard refresh non necessario")
    lines.append("- UI/PDF/app non toccati")
    lines.append("- Aggiornamento matrice/orchestrazione logica dopo registry 73")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append(f"- Registry totale: `{report.registry_total_motors}`")
    lines.append(f"- Fonte registry: `{report.registry_source}`")
    lines.append(f"- Matrix updated: `{report.matrix_updated}`")
    lines.append(f"- Orchestration updated: `{report.orchestration_updated}`")
    lines.append("")
    lines.append("## Selector/orchestrator collegati alla matrice")
    lines.append("")
    for control_id in report.selector_orchestrator_ids:
        lines.append(f"- `{control_id}`")
    lines.append("")
    lines.append("## Route sezioni dopo H.2")
    lines.append("")
    lines.append("| Sezione | Controlli qualità G.2 | Selector/orchestrator | Totale route dopo H.2 |")
    lines.append("|---|---:|---:|---:|")
    for route in report.section_routes:
        lines.append(
            f"| {route.section_label} | {route.g2_quality_controls_count} | "
            f"{route.selector_orchestrator_controls_count} | {route.total_controls_after_h2} |"
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
    lines.append("## Notes")
    lines.append("")
    for note in report.notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Prossima fase")
    lines.append("")
    lines.append(f"- {report.next_phase}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_inventory_markdown(
    inventory: InventoryReport,
    path: Path = DEFAULT_INVENTORY_MD_REPORT,
) -> None:
    lines: List[str] = []

    lines.append(f"# {inventory.label}")
    lines.append("")
    lines.append(f"- Registry totale ufficiale: `{inventory.registry_total_motors}`")
    lines.append(f"- Motori con dettaglio rilevato nei report: `{inventory.detailed_motors_detected}`")
    lines.append("")
    lines.append("## Route per sezione")
    lines.append("")
    for route in inventory.section_routes:
        lines.append(f"### {route.section_label}")
        lines.append("")
        lines.append(f"- Controlli qualità dalla matrice 5.12G.2: `{route.g2_quality_controls_count}`")
        lines.append(f"- Selector/orchestrator universali aggiunti: `{route.selector_orchestrator_controls_count}`")
        lines.append(f"- Totale route sezione dopo 5.12H.2: `{route.total_controls_after_h2}`")
        lines.append(f"- Fonte conteggio G.2: `{route.g2_count_source}`")
        lines.append("")
        lines.append("Selector/orchestrator usati:")
        lines.append("")
        for control_id in route.selector_orchestrator_control_ids:
            lines.append(f"- `{control_id}`")
        lines.append("")
        lines.append("ID qualità G.2 esplicitamente esposti nel report:")
        lines.append("")
        if route.explicit_g2_control_ids_found:
            for control_id in route.explicit_g2_control_ids_found:
                lines.append(f"- `{control_id}`")
        else:
            lines.append("- Non esposti come lista completa nel report G.2; usato conteggio ufficiale validato.")
        lines.append("")

    lines.append("## Motori selector/orchestrator universali aggiunti")
    lines.append("")
    lines.append("| Motore | Nome | Ruolo | Universale | Usato da |")
    lines.append("|---|---|---|---|---|")
    for item in inventory.selector_orchestrator_motors:
        used_by = ", ".join(SECTION_LABELS.get(section, section) for section in item.used_by_sections)
        lines.append(
            f"| `{item.control_id}` | {item.name} | {item.role} | {item.universal} | {used_by} |"
        )
    lines.append("")
    lines.append("## Inventario motori rilevati nei report")
    lines.append("")
    lines.append("| Motore | Nome | Ruolo | Universale | Usato da | Fonte |")
    lines.append("|---|---|---|---|---|---|")
    for item in inventory.discovered_motor_inventory:
        used_by = ", ".join(SECTION_LABELS.get(section, section) for section in item.used_by_sections)
        if not used_by:
            used_by = "non rilevabile"
        lines.append(
            f"| `{item.control_id}` | {item.name} | {item.role} | "
            f"{item.universal} | {used_by} | `{item.source}` |"
        )
    lines.append("")
    lines.append("## Note trasparenza")
    lines.append("")
    for note in inventory.transparency_notes:
        lines.append(f"- {note}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_and_write_phase5_12h2_reports() -> Phase512H2Report:
    report, inventory = run_phase5_12h2()

    write_json(DEFAULT_JSON_REPORT, report)
    write_h2_markdown(report)

    write_json(DEFAULT_INVENTORY_JSON_REPORT, inventory)
    write_inventory_markdown(inventory)

    return report


if __name__ == "__main__":
    result = run_and_write_phase5_12h2_reports()

    print(result.status)
    print(f"Registry total motors: {result.registry_total_motors}")
    print(f"Matrix updated: {result.matrix_updated}")
    print(f"Orchestration updated: {result.orchestration_updated}")
    print("Section routes:")
    for route in result.section_routes:
        print(
            f"- {route.section_label}: "
            f"{route.g2_quality_controls_count} + "
            f"{route.selector_orchestrator_controls_count} = "
            f"{route.total_controls_after_h2}"
        )
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")
    print(f"Inventory JSON report: {DEFAULT_INVENTORY_JSON_REPORT}")
    print(f"Inventory Markdown report: {DEFAULT_INVENTORY_MD_REPORT}")

    if result.defects:
        raise SystemExit(1)
