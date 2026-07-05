from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


PHASE = "5.12H"
PHASE_LABEL = "FASE 5.12H — SELECTOR/ORCHESTRATOR STANDALONE QM_051_QM_058"

CONTROL_IDS: Tuple[str, ...] = tuple(f"qm_{i:03d}" for i in range(51, 59))

SECTION_TYPES: Tuple[str, ...] = (
    "card",
    "summary",
    "study_questions",
    "test_quiz",
)

DEFAULT_G2_MATRIX_REPORT = Path(
    "reports/phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json"
)

DEFAULT_JSON_REPORT = Path(
    "reports/phase5_12h_selector_orchestrator_standalone_qm_051_qm_058_v1.json"
)

DEFAULT_MD_REPORT = Path(
    "reports/phase5_12h_selector_orchestrator_standalone_qm_051_qm_058_v1.md"
)


@dataclass(frozen=True)
class SelectorOrchestratorMotor:
    control_id: str
    name: str
    role: str
    order: int
    section_scope: Tuple[str, ...]
    input_contract: Tuple[str, ...]
    output_contract: Tuple[str, ...]
    blocking: bool
    description: str


@dataclass
class SelectionDecision:
    control_id: str
    section_type: str
    selected: bool
    reason: str
    order: int
    role: str
    input_contract: List[str]
    output_contract: List[str]


@dataclass
class OrchestrationStep:
    order: int
    control_id: str
    section_type: str
    role: str
    action: str
    input_contract: List[str]
    output_contract: List[str]
    blocking: bool


@dataclass
class OrchestrationPlan:
    section_type: str
    ready: bool
    selected_controls: List[str]
    steps: List[OrchestrationStep]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase512HReport:
    phase: str
    label: str
    status: str
    registry_linked: bool
    registry_expected_before: int
    registry_expected_after_next_phase: int
    standalone_controls_created: int
    control_ids: List[str]
    sections_validated: List[str]
    g2_matrix_loaded: bool
    g2_matrix_path: str
    plans: List[OrchestrationPlan]
    defects: List[str]
    warnings: List[str]
    next_phase: str


def normalize_section_type(value: str) -> str:
    cleaned = (value or "").strip().lower().replace("-", "_").replace(" ", "_")

    aliases = {
        "cards": "card",
        "flashcard": "card",
        "flashcards": "card",
        "riassunto": "summary",
        "summary": "summary",
        "summaries": "summary",
        "domande_studio": "study_questions",
        "study_question": "study_questions",
        "study_questions": "study_questions",
        "questions": "study_questions",
        "quiz": "test_quiz",
        "test": "test_quiz",
        "test_quiz": "test_quiz",
        "test/quiz": "test_quiz",
    }

    return aliases.get(cleaned, cleaned)


def build_standalone_motors() -> List[SelectorOrchestratorMotor]:
    all_sections = SECTION_TYPES

    return [
        SelectorOrchestratorMotor(
            control_id="qm_051",
            name="section_intent_selector",
            role="selector",
            order=10,
            section_scope=all_sections,
            input_contract=("requested_section", "document_profile", "available_quality_matrix"),
            output_contract=("normalized_section", "section_generation_intent"),
            blocking=True,
            description="Normalizza la sezione richiesta e impedisce selezioni ambigue.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_052",
            name="section_capability_selector",
            role="selector",
            order=20,
            section_scope=all_sections,
            input_contract=("normalized_section", "available_quality_matrix"),
            output_contract=("eligible_quality_controls", "excluded_quality_controls"),
            blocking=True,
            description="Seleziona solo i controlli compatibili con la sezione richiesta.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_053",
            name="contextual_duplicate_selector",
            role="selector",
            order=30,
            section_scope=all_sections,
            input_contract=("eligible_quality_controls", "contextual_duplicate_policy"),
            output_contract=("duplicate_policy_decision", "duplicate_safe_controls"),
            blocking=True,
            description="Applica la politica sui duplicati contestuali senza far rientrare duplicati grezzi.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_054",
            name="quality_route_selector",
            role="selector",
            order=40,
            section_scope=all_sections,
            input_contract=("duplicate_safe_controls", "section_generation_intent"),
            output_contract=("quality_route", "route_reason"),
            blocking=True,
            description="Costruisce il percorso qualità corretto per card, riassunto, domande studio o test.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_055",
            name="section_execution_orchestrator",
            role="orchestrator",
            order=50,
            section_scope=all_sections,
            input_contract=("quality_route", "document_profile", "cleaned_input"),
            output_contract=("ordered_execution_steps", "section_runtime_contract"),
            blocking=True,
            description="Ordina i controlli selezionati in una sequenza eseguibile.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_056",
            name="quality_conflict_orchestrator",
            role="orchestrator",
            order=60,
            section_scope=all_sections,
            input_contract=("ordered_execution_steps", "excluded_quality_controls"),
            output_contract=("resolved_quality_conflicts", "blocking_conflicts"),
            blocking=True,
            description="Risolve conflitti tra controlli e blocca combinazioni incompatibili.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_057",
            name="section_readiness_orchestrator",
            role="orchestrator",
            order=70,
            section_scope=all_sections,
            input_contract=("resolved_quality_conflicts", "section_runtime_contract"),
            output_contract=("section_ready", "readiness_reasons"),
            blocking=True,
            description="Verifica che la sezione sia pronta prima della generazione finale.",
        ),
        SelectorOrchestratorMotor(
            control_id="qm_058",
            name="orchestration_audit_orchestrator",
            role="orchestrator",
            order=80,
            section_scope=all_sections,
            input_contract=("section_ready", "readiness_reasons", "quality_route"),
            output_contract=("auditable_orchestration_trace", "human_readable_route_summary"),
            blocking=False,
            description="Produce una traccia leggibile e verificabile dell'orchestrazione.",
        ),
    ]


def load_optional_g2_matrix(path: Path = DEFAULT_G2_MATRIX_REPORT) -> Dict[str, Any]:
    if not path.exists():
        return {
            "loaded": False,
            "path": str(path),
            "data": {},
            "warning": "Matrice 5.12G.2 non trovata: validazione standalone eseguita senza import matrice.",
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "loaded": False,
            "path": str(path),
            "data": {},
            "warning": f"Matrice 5.12G.2 presente ma non leggibile: {exc}",
        }

    return {
        "loaded": True,
        "path": str(path),
        "data": data,
        "warning": "",
    }


class SelectorOrchestratorStandalone512H:
    def __init__(self, motors: Optional[Sequence[SelectorOrchestratorMotor]] = None) -> None:
        self.motors = list(motors or build_standalone_motors())
        self._validate_motor_library()

    def _validate_motor_library(self) -> None:
        ids = [motor.control_id for motor in self.motors]

        if ids != list(CONTROL_IDS):
            raise ValueError(
                f"Controlli standalone non coerenti. Attesi {list(CONTROL_IDS)}, trovati {ids}"
            )

        orders = [motor.order for motor in self.motors]
        if orders != sorted(orders):
            raise ValueError("Ordine motori selettore/orchestratore non crescente.")

        if len(set(ids)) != len(ids):
            raise ValueError("Sono presenti control_id duplicati nei motori 5.12H.")

        for motor in self.motors:
            if motor.role not in {"selector", "orchestrator"}:
                raise ValueError(f"Ruolo non valido per {motor.control_id}: {motor.role}")

            if not motor.input_contract:
                raise ValueError(f"Input contract mancante per {motor.control_id}")

            if not motor.output_contract:
                raise ValueError(f"Output contract mancante per {motor.control_id}")

            unknown_sections = set(motor.section_scope) - set(SECTION_TYPES)
            if unknown_sections:
                raise ValueError(
                    f"Sezioni non riconosciute per {motor.control_id}: {sorted(unknown_sections)}"
                )

    def select_for_section(self, section_type: str) -> List[SelectionDecision]:
        normalized = normalize_section_type(section_type)

        decisions: List[SelectionDecision] = []
        for motor in self.motors:
            selected = normalized in motor.section_scope
            decisions.append(
                SelectionDecision(
                    control_id=motor.control_id,
                    section_type=normalized,
                    selected=selected,
                    reason=(
                        "Controllo selezionato per la sezione richiesta."
                        if selected
                        else "Controllo escluso perché fuori scope sezione."
                    ),
                    order=motor.order,
                    role=motor.role,
                    input_contract=list(motor.input_contract),
                    output_contract=list(motor.output_contract),
                )
            )

        return decisions

    def build_plan(self, section_type: str) -> OrchestrationPlan:
        normalized = normalize_section_type(section_type)
        defects: List[str] = []
        warnings: List[str] = []

        if normalized not in SECTION_TYPES:
            defects.append(f"Sezione non supportata: {section_type}")

        decisions = self.select_for_section(normalized)
        selected_decisions = [decision for decision in decisions if decision.selected]

        selected_ids = [decision.control_id for decision in selected_decisions]
        if selected_ids != list(CONTROL_IDS):
            defects.append(
                f"Selezione incompleta per {normalized}: attesi {list(CONTROL_IDS)}, trovati {selected_ids}"
            )

        steps: List[OrchestrationStep] = []
        for decision in selected_decisions:
            steps.append(
                OrchestrationStep(
                    order=decision.order,
                    control_id=decision.control_id,
                    section_type=normalized,
                    role=decision.role,
                    action=self._action_for(decision.control_id, normalized),
                    input_contract=decision.input_contract,
                    output_contract=decision.output_contract,
                    blocking=decision.control_id != "qm_058",
                )
            )

        self._validate_plan_order(normalized, steps, defects)
        self._validate_contract_chain(normalized, steps, defects)
        self._validate_no_demo_or_placeholder_text(normalized, steps, defects)

        return OrchestrationPlan(
            section_type=normalized,
            ready=not defects,
            selected_controls=selected_ids,
            steps=steps,
            defects=defects,
            warnings=warnings,
        )

    @staticmethod
    def _action_for(control_id: str, section_type: str) -> str:
        action_map = {
            "qm_051": f"normalizza richiesta sezione {section_type}",
            "qm_052": f"seleziona controlli qualità compatibili con {section_type}",
            "qm_053": f"applica politica duplicati contestuali per {section_type}",
            "qm_054": f"costruisce route qualità per {section_type}",
            "qm_055": f"ordina esecuzione motori per {section_type}",
            "qm_056": f"risolve conflitti qualità per {section_type}",
            "qm_057": f"verifica readiness sezione {section_type}",
            "qm_058": f"produce audit leggibile orchestrazione {section_type}",
        }
        return action_map[control_id]

    @staticmethod
    def _validate_plan_order(
        section_type: str,
        steps: Sequence[OrchestrationStep],
        defects: List[str],
    ) -> None:
        ids = [step.control_id for step in steps]

        required_order = list(CONTROL_IDS)
        if ids != required_order:
            defects.append(
                f"Ordine errato per {section_type}: atteso {required_order}, trovato {ids}"
            )

        selectors = [step.control_id for step in steps if step.role == "selector"]
        orchestrators = [step.control_id for step in steps if step.role == "orchestrator"]

        if selectors != ["qm_051", "qm_052", "qm_053", "qm_054"]:
            defects.append(
                f"Blocco selector errato per {section_type}: trovato {selectors}"
            )

        if orchestrators != ["qm_055", "qm_056", "qm_057", "qm_058"]:
            defects.append(
                f"Blocco orchestrator errato per {section_type}: trovato {orchestrators}"
            )

    @staticmethod
    def _validate_contract_chain(
        section_type: str,
        steps: Sequence[OrchestrationStep],
        defects: List[str],
    ) -> None:
        produced = {
            "requested_section",
            "document_profile",
            "available_quality_matrix",
            "contextual_duplicate_policy",
            "cleaned_input",
        }

        for step in steps:
            missing = [item for item in step.input_contract if item not in produced]
            if missing:
                defects.append(
                    f"Contratto input mancante per {section_type}/{step.control_id}: {missing}"
                )
            produced.update(step.output_contract)

    @staticmethod
    def _validate_no_demo_or_placeholder_text(
        section_type: str,
        steps: Sequence[OrchestrationStep],
        defects: List[str],
    ) -> None:
        forbidden_fragments = (
            "lorem ipsum",
            "testo demo obbligatorio",
            "frase hardcoded",
            "placeholder non sostituito",
        )

        serialized = json.dumps([asdict(step) for step in steps], ensure_ascii=False).lower()
        for fragment in forbidden_fragments:
            if fragment in serialized:
                defects.append(
                    f"Testo vietato trovato in orchestrazione {section_type}: {fragment}"
                )


def run_phase5_12h_validation() -> Phase512HReport:
    matrix = load_optional_g2_matrix()
    engine = SelectorOrchestratorStandalone512H()

    plans = [engine.build_plan(section_type) for section_type in SECTION_TYPES]

    defects: List[str] = []
    warnings: List[str] = []

    if matrix.get("warning"):
        warnings.append(str(matrix["warning"]))

    for plan in plans:
        defects.extend(plan.defects)
        warnings.extend(plan.warnings)

    all_ids = [motor.control_id for motor in engine.motors]
    if all_ids != list(CONTROL_IDS):
        defects.append(
            f"Libreria motori non coerente: attesi {list(CONTROL_IDS)}, trovati {all_ids}"
        )

    for plan in plans:
        if not plan.ready:
            defects.append(f"Piano non pronto per sezione {plan.section_type}")

    status = (
        "PASS - Fase 5.12H: SELECTOR_ORCHESTRATOR_STANDALONE_QM_051_QM_058_READY"
        if not defects
        else "FAIL - Fase 5.12H: SELECTOR_ORCHESTRATOR_STANDALONE_QM_051_QM_058_NOT_READY"
    )

    return Phase512HReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        registry_linked=False,
        registry_expected_before=65,
        registry_expected_after_next_phase=73,
        standalone_controls_created=len(CONTROL_IDS),
        control_ids=list(CONTROL_IDS),
        sections_validated=list(SECTION_TYPES),
        g2_matrix_loaded=bool(matrix.get("loaded")),
        g2_matrix_path=str(matrix.get("path", DEFAULT_G2_MATRIX_REPORT)),
        plans=plans,
        defects=defects,
        warnings=warnings,
        next_phase="5.12H.1 - collegamento registry 65 -> 73",
    )


def write_json_report(report: Phase512HReport, path: Path = DEFAULT_JSON_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(report: Phase512HReport, path: Path = DEFAULT_MD_REPORT) -> None:
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
    lines.append("- Registry non collegato in questa fase")
    lines.append("")
    lines.append("## Controlli ricostruiti standalone")
    lines.append("")
    for control_id in report.control_ids:
        lines.append(f"- `{control_id}`")
    lines.append("")
    lines.append("## Risultato")
    lines.append("")
    lines.append(f"- Controlli standalone creati: `{report.standalone_controls_created}`")
    lines.append(f"- Registry prima della prossima fase: `{report.registry_expected_before}`")
    lines.append(f"- Registry atteso dopo 5.12H.1: `{report.registry_expected_after_next_phase}`")
    lines.append(f"- Matrice 5.12G.2 caricata: `{report.g2_matrix_loaded}`")
    lines.append(f"- Path matrice: `{report.g2_matrix_path}`")
    lines.append("")
    lines.append("## Sezioni validate")
    lines.append("")
    for plan in report.plans:
        lines.append(f"### {plan.section_type}")
        lines.append("")
        lines.append(f"- Ready: `{plan.ready}`")
        lines.append(f"- Controlli selezionati: `{', '.join(plan.selected_controls)}`")
        lines.append("")
        lines.append("| Ordine | Controllo | Ruolo | Azione |")
        lines.append("|---:|---|---|---|")
        for step in plan.steps:
            lines.append(
                f"| {step.order} | `{step.control_id}` | {step.role} | {step.action} |"
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

    lines.append("## Prossima fase")
    lines.append("")
    lines.append(f"- {report.next_phase}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_and_write_phase5_12h_report() -> Phase512HReport:
    report = run_phase5_12h_validation()
    write_json_report(report)
    write_markdown_report(report)
    return report


if __name__ == "__main__":
    result = run_and_write_phase5_12h_report()
    print(result.status)
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")

    if result.defects:
        raise SystemExit(1)
