from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from backend.phase5_selector_orchestrator_standalone_v512h import (
    CONTROL_IDS as STANDALONE_CONTROL_IDS,
    PHASE as STANDALONE_PHASE,
    build_standalone_motors,
)


PHASE = "5.12H.1"
PHASE_LABEL = "FASE 5.12H.1 — REGISTRY CONNECTOR 65_TO_73 QM_051_QM_058"

EXPECTED_REGISTRY_BEFORE = 65
EXPECTED_LINKED_CONTROLS = 8
EXPECTED_REGISTRY_AFTER = 73

DEFAULT_REPORTS_DIR = Path("reports")

STANDALONE_REPORT_PATH = Path(
    "reports/phase5_12h_selector_orchestrator_standalone_qm_051_qm_058_v1.json"
)

DEFAULT_JSON_REPORT = Path(
    "reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json"
)

DEFAULT_MD_REPORT = Path(
    "reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.md"
)

CONTROL_ID_PATTERN = re.compile(r"\bqm_\d{3}\b", re.IGNORECASE)


@dataclass(frozen=True)
class RegistryLinkedControl:
    registry_slot: int
    control_id: str
    source_phase: str
    linked_phase: str
    name: str
    role: str
    section_scope: List[str]
    input_contract: List[str]
    output_contract: List[str]
    blocking: bool
    backend_source: str
    report_source: str


@dataclass
class RegistryBaseSource:
    path: str
    detected_count: int
    detection_method: str
    unique_qm_ids_seen: int
    selected: bool


@dataclass
class RegistryConnectorReport:
    phase: str
    label: str
    status: str
    registry_before: int
    linked_controls_count: int
    registry_after: int
    expected_registry_after: int
    base_registry_source: RegistryBaseSource
    standalone_report_path: str
    standalone_report_status: str
    linked_control_ids: List[str]
    linked_controls: List[RegistryLinkedControl]
    registry_linked: bool
    matrix_updated: bool
    orchestration_updated: bool
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    next_phase: str = "5.12H.2 - aggiornamento matrice/orchestrazione"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk_values(obj: Any) -> Iterable[Any]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from walk_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_values(item)
    else:
        yield obj


def collect_qm_ids(obj: Any) -> List[str]:
    found: List[str] = []

    for value in walk_values(obj):
        if isinstance(value, str):
            for match in CONTROL_ID_PATTERN.findall(value):
                found.append(match.lower())

    return sorted(set(found), key=lambda item: int(item.split("_")[1]))


def find_numeric_fields(obj: Any, path: str = "") -> List[Tuple[str, int]]:
    found: List[Tuple[str, int]] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else str(key)

            if isinstance(value, bool):
                continue

            if isinstance(value, int):
                found.append((child_path, value))
            else:
                found.extend(find_numeric_fields(value, child_path))

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(find_numeric_fields(value, f"{path}[{index}]"))

    return found


def score_count_field(field_path: str, value: int) -> int:
    lowered = field_path.lower()
    score = 0

    if value == EXPECTED_REGISTRY_BEFORE:
        score += 100

    if "registry" in lowered:
        score += 30

    if "motor" in lowered or "control" in lowered or "quality" in lowered:
        score += 20

    if "count" in lowered or "total" in lowered:
        score += 20

    if "before" in lowered or "current" in lowered or "ready" in lowered:
        score += 10

    if "after" in lowered or "expected" in lowered or "next" in lowered:
        score -= 30

    return score


def detect_registry_count(data: Dict[str, Any]) -> Tuple[int, str]:
    numeric_fields = find_numeric_fields(data)
    scored = [
        (score_count_field(field_path, value), field_path, value)
        for field_path, value in numeric_fields
        if value == EXPECTED_REGISTRY_BEFORE
    ]

    if scored:
        scored.sort(reverse=True)
        _, field_path, value = scored[0]
        return value, f"numeric_field:{field_path}"

    qm_ids = collect_qm_ids(data)
    if len(qm_ids) == EXPECTED_REGISTRY_BEFORE:
        return len(qm_ids), "fallback_unique_qm_ids"

    raise ValueError(
        "Impossibile rilevare un registry base da 65 controlli nel JSON indicato."
    )


def candidate_report_paths(reports_dir: Path) -> List[Path]:
    if not reports_dir.exists():
        return []

    excluded_fragments = (
        "phase5_12h1_registry_connector",
        "phase5_12h_selector_orchestrator_standalone",
    )

    paths = []
    for path in reports_dir.glob("*.json"):
        lowered = path.name.lower()
        if any(fragment in lowered for fragment in excluded_fragments):
            continue
        paths.append(path)

    return sorted(paths, key=lambda item: item.stat().st_mtime, reverse=True)


def discover_base_registry_source() -> Tuple[RegistryBaseSource, Dict[str, Any]]:
    env_path = os.environ.get("PHASE5_BASE_REGISTRY_REPORT", "").strip()
    if env_path:
        path = Path(env_path)
        data = read_json(path)
        count, method = detect_registry_count(data)
        return (
            RegistryBaseSource(
                path=str(path),
                detected_count=count,
                detection_method=f"env:{method}",
                unique_qm_ids_seen=len(collect_qm_ids(data)),
                selected=True,
            ),
            data,
        )

    candidates: List[Tuple[int, Path, Dict[str, Any], int, str]] = []

    for path in candidate_report_paths(DEFAULT_REPORTS_DIR):
        try:
            data = read_json(path)
            count, method = detect_registry_count(data)
        except Exception:
            continue

        filename = path.name.lower()
        score = 0

        if count == EXPECTED_REGISTRY_BEFORE:
            score += 1000

        if "registry" in filename:
            score += 200

        if "quality" in filename:
            score += 50

        if "snapshot" in filename:
            score += 30

        score += int(path.stat().st_mtime)

        candidates.append((score, path, data, count, method))

    if not candidates:
        raise FileNotFoundError(
            "Nessun report registry base da 65 trovato in reports/. "
            "Puoi forzare il file con PHASE5_BASE_REGISTRY_REPORT=path/del/report.json"
        )

    candidates.sort(reverse=True, key=lambda item: item[0])
    _, path, data, count, method = candidates[0]

    return (
        RegistryBaseSource(
            path=str(path),
            detected_count=count,
            detection_method=method,
            unique_qm_ids_seen=len(collect_qm_ids(data)),
            selected=True,
        ),
        data,
    )


def load_standalone_report(path: Path = STANDALONE_REPORT_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Report standalone 5.12H mancante: {path}")

    data = read_json(path)
    status = str(data.get("status", ""))

    if "PASS - Fase 5.12H" not in status:
        raise ValueError(f"Report standalone 5.12H non PASS: {status}")

    control_ids = data.get("control_ids", [])
    if list(control_ids) != list(STANDALONE_CONTROL_IDS):
        raise ValueError(
            f"Control IDs standalone non coerenti. "
            f"Attesi {list(STANDALONE_CONTROL_IDS)}, trovati {control_ids}"
        )

    defects = data.get("defects", [])
    warnings = data.get("warnings", [])

    if defects:
        raise ValueError(f"Report standalone 5.12H contiene defects: {defects}")

    if warnings:
        raise ValueError(f"Report standalone 5.12H contiene warnings: {warnings}")

    return data


def build_registry_linked_controls() -> List[RegistryLinkedControl]:
    motors = build_standalone_motors()

    linked: List[RegistryLinkedControl] = []
    for offset, motor in enumerate(motors, start=1):
        linked.append(
            RegistryLinkedControl(
                registry_slot=EXPECTED_REGISTRY_BEFORE + offset,
                control_id=motor.control_id,
                source_phase=STANDALONE_PHASE,
                linked_phase=PHASE,
                name=motor.name,
                role=motor.role,
                section_scope=list(motor.section_scope),
                input_contract=list(motor.input_contract),
                output_contract=list(motor.output_contract),
                blocking=motor.blocking,
                backend_source="backend/phase5_selector_orchestrator_standalone_v512h.py",
                report_source=str(STANDALONE_REPORT_PATH),
            )
        )

    return linked


def validate_registry_connection(
    base_source: RegistryBaseSource,
    standalone_report: Dict[str, Any],
    linked_controls: Sequence[RegistryLinkedControl],
) -> Tuple[List[str], List[str]]:
    defects: List[str] = []
    warnings: List[str] = []

    if base_source.detected_count != EXPECTED_REGISTRY_BEFORE:
        defects.append(
            f"Registry base non coerente: atteso {EXPECTED_REGISTRY_BEFORE}, "
            f"trovato {base_source.detected_count}"
        )

    linked_ids = [control.control_id for control in linked_controls]

    if linked_ids != list(STANDALONE_CONTROL_IDS):
        defects.append(
            f"ID collegati non coerenti: attesi {list(STANDALONE_CONTROL_IDS)}, "
            f"trovati {linked_ids}"
        )

    if len(linked_controls) != EXPECTED_LINKED_CONTROLS:
        defects.append(
            f"Numero controlli collegati errato: atteso {EXPECTED_LINKED_CONTROLS}, "
            f"trovato {len(linked_controls)}"
        )

    if len(set(linked_ids)) != len(linked_ids):
        defects.append(f"Duplicati nei controlli collegati: {linked_ids}")

    expected_slots = list(
        range(EXPECTED_REGISTRY_BEFORE + 1, EXPECTED_REGISTRY_AFTER + 1)
    )
    actual_slots = [control.registry_slot for control in linked_controls]
    if actual_slots != expected_slots:
        defects.append(
            f"Slot registry errati: attesi {expected_slots}, trovati {actual_slots}"
        )

    registry_after = base_source.detected_count + len(linked_controls)
    if registry_after != EXPECTED_REGISTRY_AFTER:
        defects.append(
            f"Conteggio registry finale errato: atteso {EXPECTED_REGISTRY_AFTER}, "
            f"trovato {registry_after}"
        )

    standalone_status = str(standalone_report.get("status", ""))
    if "PASS - Fase 5.12H" not in standalone_status:
        defects.append(f"Standalone report non PASS: {standalone_status}")

    roles = [control.role for control in linked_controls]
    if roles[:4] != ["selector", "selector", "selector", "selector"]:
        defects.append(f"Primi 4 controlli non sono selector: {roles[:4]}")

    if roles[4:] != ["orchestrator", "orchestrator", "orchestrator", "orchestrator"]:
        defects.append(f"Ultimi 4 controlli non sono orchestrator: {roles[4:]}")

    if (
        "fallback_unique_qm_ids" in base_source.detection_method
        and base_source.unique_qm_ids_seen < EXPECTED_REGISTRY_BEFORE
    ):
        warnings.append(
            "Il report base è stato rilevato tramite ID qm_* ma espone meno di 65 ID leggibili."
        )

    return defects, warnings


def run_phase5_12h1_registry_connection() -> RegistryConnectorReport:
    base_source, _base_data = discover_base_registry_source()
    standalone_report = load_standalone_report()
    linked_controls = build_registry_linked_controls()

    defects, warnings = validate_registry_connection(
        base_source=base_source,
        standalone_report=standalone_report,
        linked_controls=linked_controls,
    )

    registry_after = base_source.detected_count + len(linked_controls)

    status = (
        "PASS - Fase 5.12H.1: REGISTRY_CONNECTOR_65_TO_73_QM_051_QM_058_READY"
        if not defects
        else "FAIL - Fase 5.12H.1: REGISTRY_CONNECTOR_65_TO_73_QM_051_QM_058_NOT_READY"
    )

    return RegistryConnectorReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        registry_before=base_source.detected_count,
        linked_controls_count=len(linked_controls),
        registry_after=registry_after,
        expected_registry_after=EXPECTED_REGISTRY_AFTER,
        base_registry_source=base_source,
        standalone_report_path=str(STANDALONE_REPORT_PATH),
        standalone_report_status=str(standalone_report.get("status", "")),
        linked_control_ids=[control.control_id for control in linked_controls],
        linked_controls=list(linked_controls),
        registry_linked=not defects,
        matrix_updated=False,
        orchestration_updated=False,
        defects=defects,
        warnings=warnings,
    )


def write_json_report(
    report: RegistryConnectorReport,
    path: Path = DEFAULT_JSON_REPORT,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(
    report: RegistryConnectorReport,
    path: Path = DEFAULT_MD_REPORT,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

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
    lines.append("- Matrice/orchestrazione finale non aggiornata in questa fase")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append(f"- Registry prima: `{report.registry_before}`")
    lines.append(f"- Controlli collegati: `{report.linked_controls_count}`")
    lines.append(f"- Registry dopo: `{report.registry_after}`")
    lines.append(f"- Registry atteso dopo fase: `{report.expected_registry_after}`")
    lines.append(f"- Registry linked: `{report.registry_linked}`")
    lines.append("")
    lines.append("## Fonte registry base")
    lines.append("")
    lines.append(f"- Path: `{report.base_registry_source.path}`")
    lines.append(f"- Conteggio rilevato: `{report.base_registry_source.detected_count}`")
    lines.append(f"- Metodo rilevamento: `{report.base_registry_source.detection_method}`")
    lines.append(f"- ID qm_* visti nel report base: `{report.base_registry_source.unique_qm_ids_seen}`")
    lines.append("")
    lines.append("## Fonte standalone")
    lines.append("")
    lines.append(f"- Path: `{report.standalone_report_path}`")
    lines.append(f"- Status: `{report.standalone_report_status}`")
    lines.append("")
    lines.append("## Controlli collegati")
    lines.append("")
    lines.append("| Slot | Controllo | Ruolo | Nome | Blocking |")
    lines.append("|---:|---|---|---|---|")
    for control in report.linked_controls:
        lines.append(
            f"| {control.registry_slot} | `{control.control_id}` | "
            f"{control.role} | {control.name} | `{control.blocking}` |"
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
    lines.append("## Stato aggiornamenti successivi")
    lines.append("")
    lines.append(f"- Matrix updated: `{report.matrix_updated}`")
    lines.append(f"- Orchestration updated: `{report.orchestration_updated}`")
    lines.append("")
    lines.append("## Prossima fase")
    lines.append("")
    lines.append(f"- {report.next_phase}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_and_write_phase5_12h1_report() -> RegistryConnectorReport:
    report = run_phase5_12h1_registry_connection()
    write_json_report(report)
    write_markdown_report(report)
    return report


if __name__ == "__main__":
    result = run_and_write_phase5_12h1_report()
    print(result.status)
    print(f"Registry before: {result.registry_before}")
    print(f"Linked controls: {result.linked_controls_count}")
    print(f"Registry after: {result.registry_after}")
    print(f"Base registry source: {result.base_registry_source.path}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")

    if result.defects:
        raise SystemExit(1)
