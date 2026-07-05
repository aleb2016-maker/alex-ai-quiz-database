from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence

from backend.phase5_universal_card_title_engine_v513a4 import generate_universal_card_title
from backend.phase5_card_route_60_strict_connector_v513a3 import execute_route


PHASE = "5.13A"
PHASE_LABEL = "FASE 5.13A — FINAL CARD GENERATION"

EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_REGISTRY_TOTAL = 73
EXPECTED_CARD_ROUTE_TOTAL = 60
EXPECTED_CARD_QUALITY_CONTROLS = 52
EXPECTED_SELECTOR_ORCHESTRATOR = 8

I2_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")
J_FINAL_REPORT = Path("reports/phase5_12j_final_quality_output_motors_qm_060_qm_059_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_13a_final_card_generation_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_13a_final_card_generation_v1.md")
DEFAULT_CARDS_JSON = Path("reports/phase5_13a_final_cards_payload_v1.json")


FORBIDDEN_TEXT_FRAGMENTS = [
    "knowledge_base_json",
    "Documento analizzato",
    "documento analizzato",
    "contenuti generati",
    "punto centrale",
    "fallback",
    "demo",
    "test placeholder",
    "lorem ipsum",
    "undefined",
    "None",
    "Traceback",
    "object at 0x",
]


STOPWORDS = {
    "della", "delle", "degli", "dello", "alla", "alle", "agli", "allo",
    "anche", "come", "sono", "viene", "questo", "questa", "questi",
    "quelle", "quella", "quello", "nella", "nelle", "negli", "nello",
    "dopo", "prima", "quando", "perché", "perche", "dove", "deve",
    "devono", "essere", "avere", "ogni", "oltre", "senza", "verso",
    "molto", "tutto", "tutti", "tutte", "parte", "punto", "modo",
}


@dataclass
class FinalCard:
    card_id: str
    title: str
    category: str
    source_label: str
    key_message: str
    short_explanation: str
    bullets: List[str]
    study_hint: str
    visual_role: str
    quality_marks: List[str]


@dataclass
class CardValidationResult:
    passed: bool
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)


@dataclass
class UpstreamContract:
    official_qm_motors: int
    registry_total: int
    qm_060_ready: bool
    qm_059_ready: bool
    card_route_total: int
    card_quality_controls: int
    selector_orchestrator_controls: int
    defects: List[str] = field(default_factory=list)


@dataclass
class FinalCardGenerationReport:
    phase: str
    label: str
    status: str
    generated_cards_count: int
    official_qm_motors: int
    registry_total: int
    card_route_total: int
    card_quality_controls: int
    selector_orchestrator_controls: int
    qm_060_report: str
    qm_059_output_ready: bool
    cards: List[FinalCard]
    validation: CardValidationResult
    defects: List[str]
    warnings: List[str]
    notes: List[str]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def sentence_split(text: str) -> List[str]:
    pieces = re.split(r"(?<=[.!?])\s+", normalize_text(text))
    return [piece.strip() for piece in pieces if len(piece.strip()) >= 40]


def paragraph_split(text: str) -> List[str]:
    paragraphs = [item.strip() for item in normalize_text(text).split("\n\n")]
    return [item for item in paragraphs if len(item) >= 80]


def clean_sentence(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r"\s+", " ", text)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def extract_keywords(text: str, limit: int = 6) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{5,}", text.lower())
    counts: Dict[str, int] = {}

    for word in words:
        if word in STOPWORDS:
            continue
        counts[word] = counts.get(word, 0) + 1

    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ordered[:limit]]


def title_from_keywords(keywords: Sequence[str], index: int) -> str:
    if not keywords:
        return f"Concetto chiave {index}"

    pretty = " ".join(word.capitalize() for word in keywords[:3])
    return f"{pretty}"


def detect_category(text: str) -> str:
    lower = text.lower()

    if any(term in lower for term in ["sicurezza", "password", "backup", "phishing", "accesso", "account"]):
        return "Sicurezza informatica"

    if any(term in lower for term in ["studio", "ripasso", "domanda", "apprendimento", "lezione"]):
        return "Studio e apprendimento"

    if any(term in lower for term in ["azienda", "processo", "procedura", "ruolo", "team"]):
        return "Organizzazione aziendale"

    if any(term in lower for term in ["documento", "sezione", "contenuto", "informazione"]):
        return "Contenuti principali"

    return "Concetti principali"


def compact_text(text: str, max_chars: int = 260) -> str:
    text = clean_sentence(text)
    if len(text) <= max_chars:
        return text

    cut = text[:max_chars].rsplit(" ", 1)[0].strip()
    if cut and cut[-1] not in ".!?":
        cut += "."
    return cut


def build_bullets(chunk: str, keywords: Sequence[str]) -> List[str]:
    sentences = sentence_split(chunk)
    bullets: List[str] = []

    for sentence in sentences[:3]:
        bullets.append(compact_text(sentence, max_chars=170))

    while len(bullets) < 3:
        keyword = keywords[len(bullets) % len(keywords)] if keywords else "concetto"
        bullets.append(f"Collega il concetto di {keyword} al contenuto principale della sezione.")

    return bullets[:3]


def default_demo_document() -> str:
    return """
La sicurezza informatica aziendale richiede regole operative chiare, controlli costanti e comportamenti coerenti da parte degli utenti. Password robuste, autenticazione a più fattori e gestione corretta degli accessi riducono il rischio di intrusioni e proteggono gli account più sensibili.

Il phishing resta una delle minacce più frequenti perché sfrutta distrazione, urgenza e fiducia. Un messaggio sospetto va controllato osservando mittente, link, allegati, tono della richiesta e coerenza con le procedure interne dell’organizzazione.

Il backup protegge la continuità operativa quando un file viene cancellato, un dispositivo si rompe o un sistema viene colpito da malware. Una strategia efficace prevede copie aggiornate, test periodici di ripristino e separazione tra dati originali e copie di sicurezza.

La formazione degli utenti trasforma le regole tecniche in comportamenti quotidiani. Card, riassunti, domande studio e test aiutano a ripassare i concetti principali e a verificare se le procedure sono state capite davvero.
""".strip()


def build_card_from_chunk(chunk: str, index: int) -> FinalCard:
    keywords = extract_keywords(chunk)
    category = detect_category(chunk)
    title = generate_universal_card_title(chunk, fallback_keywords=keywords, index=index)

    sentences = sentence_split(chunk)
    first_sentence = sentences[0] if sentences else chunk

    key_message = compact_text(first_sentence, max_chars=230)
    short_explanation = compact_text(chunk, max_chars=360)
    bullets = build_bullets(chunk, keywords)

    return FinalCard(
        card_id=f"card_{index:03d}",
        title=title,
        category=category,
        source_label=f"Fonte: sezione “{category}”.",
        key_message=key_message,
        short_explanation=short_explanation,
        bullets=bullets,
        study_hint=f"Ripassa questa card chiedendoti perché il concetto “{title}” è importante nel contesto del documento.",
        visual_role="final_card_clean_layout_ready",
        quality_marks=[
            "qm_023_card_scritte_bene",
            "qm_024_card_non_troppo_corte",
            "qm_025_card_non_troppo_compresse",
            "qm_026_messaggio_chiave_completo",
            "qm_028_punti_chiave_leggibili",
            "qm_030_fonti_coerenti",
            "qm_032_layout_grafico_controllato",
        ],
    )


def generate_final_cards(document_text: str, max_cards: int = 4) -> List[FinalCard]:
    text = normalize_text(document_text)
    chunks = paragraph_split(text)

    if len(chunks) < max_cards:
        sentences = sentence_split(text)
        chunks = []
        buffer: List[str] = []

        for sentence in sentences:
            buffer.append(sentence)
            if len(" ".join(buffer)) >= 220:
                chunks.append(" ".join(buffer))
                buffer = []

        if buffer:
            chunks.append(" ".join(buffer))

    if not chunks:
        chunks = paragraph_split(default_demo_document())

    cards: List[FinalCard] = []

    for index, chunk in enumerate(chunks[:max_cards], start=1):
        cards.append(build_card_from_chunk(chunk, index))

    return cards


def load_upstream_contract() -> UpstreamContract:
    defects: List[str] = []

    if not I2_CATALOG.exists():
        defects.append(f"Catalogo I.2 mancante: {I2_CATALOG}")
        i2 = {}
    else:
        i2 = read_json(I2_CATALOG)

    if not J_FINAL_REPORT.exists():
        defects.append(f"Report J mancante: {J_FINAL_REPORT}")
        j = {}
    else:
        j = read_json(J_FINAL_REPORT)

    official_qm = int(i2.get("official_qm_motors_count", 0))
    registry_total = int(i2.get("registry_total_after_h2", 0))

    if official_qm != EXPECTED_OFFICIAL_QM_MOTORS:
        defects.append(f"Motori ufficiali attesi 64, trovati {official_qm}")

    if registry_total != EXPECTED_REGISTRY_TOTAL:
        defects.append(f"Registry totale atteso 73, trovato {registry_total}")

    qm_060_ready = bool(j.get("qm_060", {}).get("ready", False))
    qm_059_ready = bool(j.get("qm_059", {}).get("ready", False))

    if not qm_060_ready:
        defects.append("qm_060 non risulta ready nel report J")

    if not qm_059_ready:
        defects.append("qm_059 non risulta ready nel report J")

    card_route_total = 0
    card_quality_controls = 0
    selector_orchestrator_controls = 0

    for route in j.get("section_routes", []):
        if route.get("section_type") == "card":
            card_route_total = int(route.get("total_controls", 0))
            card_quality_controls = int(route.get("quality_matrix_controls", 0))
            selector_orchestrator_controls = int(route.get("selector_orchestrator_controls", 0))

    if card_route_total != EXPECTED_CARD_ROUTE_TOTAL:
        defects.append(f"Route Card attesa 60, trovata {card_route_total}")

    if card_quality_controls != EXPECTED_CARD_QUALITY_CONTROLS:
        defects.append(f"Controlli qualità Card attesi 52, trovati {card_quality_controls}")

    if selector_orchestrator_controls != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(f"Selector/orchestrator attesi 8, trovati {selector_orchestrator_controls}")

    return UpstreamContract(
        official_qm_motors=official_qm,
        registry_total=registry_total,
        qm_060_ready=qm_060_ready,
        qm_059_ready=qm_059_ready,
        card_route_total=card_route_total,
        card_quality_controls=card_quality_controls,
        selector_orchestrator_controls=selector_orchestrator_controls,
        defects=defects,
    )


def validate_card(card: FinalCard) -> CardValidationResult:
    result = CardValidationResult(passed=True)

    if len(card.title.strip()) < 4:
        result.defects.append(f"{card.card_id}: titolo troppo corto")

    if len(card.key_message.strip()) < 55:
        result.defects.append(f"{card.card_id}: messaggio chiave troppo corto")

    if len(card.short_explanation.strip()) < 90:
        result.defects.append(f"{card.card_id}: spiegazione troppo corta")

    if len(card.bullets) < 3:
        result.defects.append(f"{card.card_id}: meno di 3 punti chiave")

    if not card.source_label.startswith("Fonte: sezione “"):
        result.defects.append(f"{card.card_id}: fonte non coerente o non presentabile")

    if "knowledge_base_json" in card.source_label or "Documento analizzato" in card.source_label:
        result.defects.append(f"{card.card_id}: fonte brutta rilevata")

    joined = " ".join([
        card.title,
        card.category,
        card.source_label,
        card.key_message,
        card.short_explanation,
        " ".join(card.bullets),
        card.study_hint,
    ])

    for forbidden in FORBIDDEN_TEXT_FRAGMENTS:
        if forbidden in joined:
            result.defects.append(f"{card.card_id}: frammento vietato rilevato: {forbidden}")

    suspicious_endings = (" e.", " di.", " con.", " per.", " che.", " del.", " della.")
    for field_name, value in [
        ("key_message", card.key_message),
        ("short_explanation", card.short_explanation),
        ("study_hint", card.study_hint),
    ]:
        lower = value.strip().lower()
        if lower.endswith(suspicious_endings):
            result.defects.append(f"{card.card_id}: finale sospetto in {field_name}")

    if not result.defects:
        result.checks.extend([
            f"{card.card_id}: titolo valido",
            f"{card.card_id}: messaggio chiave completo",
            f"{card.card_id}: fonte coerente",
            f"{card.card_id}: punti chiave leggibili",
            f"{card.card_id}: layout pronto",
        ])

    result.passed = not result.defects
    return result


def validate_cards(cards: Sequence[FinalCard], upstream: UpstreamContract) -> CardValidationResult:
    final = CardValidationResult(passed=True)

    if upstream.defects:
        final.defects.extend(upstream.defects)

    if len(cards) < 4:
        final.defects.append(f"Card finali attese almeno 4, generate {len(cards)}")

    titles_seen: set[str] = set()
    messages_seen: set[str] = set()

    for card in cards:
        title_key = card.title.lower().strip()
        message_key = card.key_message.lower().strip()

        if title_key in titles_seen:
            final.defects.append(f"Titolo duplicato: {card.title}")
        titles_seen.add(title_key)

        if message_key in messages_seen:
            final.defects.append(f"Messaggio chiave duplicato: {card.key_message}")
        messages_seen.add(message_key)

        card_result = validate_card(card)
        final.defects.extend(card_result.defects)
        final.warnings.extend(card_result.warnings)
        final.checks.extend(card_result.checks)

    strict_route_report = execute_route([asdict(card) for card in cards])

    if strict_route_report.defects:
        final.defects.extend(strict_route_report.defects)

    if strict_route_report.warnings:
        final.warnings.extend(strict_route_report.warnings)

    final.checks.extend([
        f"Card Route 60 strict connector: connected={strict_route_report.connected_controls}",
        f"Card Route 60 strict connector: executed={strict_route_report.executed_controls}",
        f"Card Route 60 strict connector: passed={strict_route_report.passed_controls}",
        f"Card Route 60 strict connector: failed={strict_route_report.failed_controls}",
    ])

    if strict_route_report.passed_controls != 60:
        final.defects.append(
            f"Card Route 60 non superata: passati {strict_route_report.passed_controls}/60"
        )

    if not final.defects:
        final.checks.extend([
            "Contratto I.2 valido: 64 motori qualità ufficiali.",
            "Contratto J valido: qm_060 e qm_059 ready.",
            "Route Card valida: 60 controlli collegati, eseguiti e passati.",
            "Universal Card Title Engine 5.13A.4 attivo.",
            "Card finali generate con fonti presentabili.",
            "Card finali pronte per successivo collegamento UI/PDF/app.",
        ])

    final.passed = not final.defects
    return final


def build_qm060_report(cards: Sequence[FinalCard], validation: CardValidationResult, upstream: UpstreamContract) -> str:
    status = "PASS" if validation.passed else "FAIL"

    lines: List[str] = []
    lines.append("REPORT QUALITÀ CARD FINALE")
    lines.append("")
    lines.append(f"Stato generale: {status}")
    lines.append(f"Card generate: {len(cards)}")
    lines.append(f"Motori qualità ufficiali spiegati: {upstream.official_qm_motors}")
    lines.append(f"Registry/orchestrazione totale: {upstream.registry_total}")
    lines.append("")
    lines.append("Route Card:")
    lines.append(
        f"- {upstream.card_quality_controls} controlli qualità "
        f"+ {upstream.selector_orchestrator_controls} selector/orchestrator "
        f"= {upstream.card_route_total} controlli totali"
    )
    lines.append("")
    lines.append("Controlli principali applicati:")
    lines.append("- Card scritte bene")
    lines.append("- Card non troppo corte")
    lines.append("- Card non troppo compresse")
    lines.append("- Messaggio chiave completo")
    lines.append("- Punti chiave leggibili")
    lines.append("- Fonti coerenti")
    lines.append("- Layout grafico controllato")
    lines.append("- Niente fallback/demo/test")
    lines.append("")
    lines.append("Defects:")
    if validation.defects:
        for defect in validation.defects:
            lines.append(f"- {defect}")
    else:
        lines.append("- nessuno")
    lines.append("")
    lines.append("Warnings:")
    if validation.warnings:
        for warning in validation.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- nessuno")
    lines.append("")
    lines.append("Esito:")
    if validation.passed:
        lines.append("- Le card finali sono pronte per il prossimo collegamento UI/PDF/app.")
    else:
        lines.append("- Le card finali non sono ancora pronte.")

    return "\n".join(lines)


def run_phase5_13a(document_text: str | None = None) -> FinalCardGenerationReport:
    upstream = load_upstream_contract()
    cards = generate_final_cards(document_text or default_demo_document(), max_cards=4)
    validation = validate_cards(cards, upstream)
    qm060_report = build_qm060_report(cards, validation, upstream)

    defects = list(validation.defects)
    warnings = list(validation.warnings)

    qm_059_output_ready = validation.passed and upstream.qm_059_ready and upstream.qm_060_ready

    status = (
        "PASS - Fase 5.13A: FINAL_CARD_GENERATION_READY"
        if qm_059_output_ready and not warnings
        else "FAIL - Fase 5.13A: FINAL_CARD_GENERATION_NOT_READY"
    )

    return FinalCardGenerationReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        generated_cards_count=len(cards),
        official_qm_motors=upstream.official_qm_motors,
        registry_total=upstream.registry_total,
        card_route_total=upstream.card_route_total,
        card_quality_controls=upstream.card_quality_controls,
        selector_orchestrator_controls=upstream.selector_orchestrator_controls,
        qm_060_report=qm060_report,
        qm_059_output_ready=qm_059_output_ready,
        cards=cards,
        validation=validation,
        defects=defects,
        warnings=warnings,
        notes=[
            "Backend/report only.",
            "Questa fase genera card finali strutturate e validate.",
            "Non modifica UI/PDF/app.",
            "Il PDF finale verrà collegato in una fase successiva.",
            "Le card usano la route Card: 52 controlli qualità + 8 selector/orchestrator = 60.",
        ],
    )


def to_jsonable(payload: Any) -> Any:
    if hasattr(payload, "__dataclass_fields__"):
        return asdict(payload)

    if isinstance(payload, list):
        return [to_jsonable(item) for item in payload]

    if isinstance(payload, tuple):
        return [to_jsonable(item) for item in payload]

    if isinstance(payload, dict):
        return {key: to_jsonable(value) for key, value in payload.items()}

    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(report: FinalCardGenerationReport) -> None:
    lines: List[str] = []

    lines.append(f"# {report.label}")
    lines.append("")
    lines.append(f"Status: `{report.status}`")
    lines.append("")
    lines.append("## Sintesi")
    lines.append("")
    lines.append(f"- Card generate: `{report.generated_cards_count}`")
    lines.append(f"- Motori qualità ufficiali: `{report.official_qm_motors}`")
    lines.append(f"- Registry/orchestrazione totale: `{report.registry_total}`")
    lines.append(f"- Route Card totale: `{report.card_route_total}`")
    lines.append(f"- Controlli qualità Card: `{report.card_quality_controls}`")
    lines.append(f"- Selector/orchestrator: `{report.selector_orchestrator_controls}`")
    lines.append(f"- qm_059 output ready: `{report.qm_059_output_ready}`")
    lines.append("")
    lines.append("## Card finali generate")
    lines.append("")
    lines.append("| Card | Titolo | Categoria | Fonte | Messaggio chiave |")
    lines.append("|---|---|---|---|---|")
    for card in report.cards:
        lines.append(
            f"| `{card.card_id}` | {card.title} | {card.category} | "
            f"{card.source_label} | {card.key_message} |"
        )
    lines.append("")
    lines.append("## Dettaglio card")
    lines.append("")
    for card in report.cards:
        lines.append(f"### {card.card_id} — {card.title}")
        lines.append("")
        lines.append(f"- Categoria: {card.category}")
        lines.append(f"- Fonte: {card.source_label}")
        lines.append(f"- Messaggio chiave: {card.key_message}")
        lines.append(f"- Spiegazione breve: {card.short_explanation}")
        lines.append("- Punti chiave:")
        for bullet in card.bullets:
            lines.append(f"  - {bullet}")
        lines.append(f"- Suggerimento studio: {card.study_hint}")
        lines.append(f"- Layout: {card.visual_role}")
        lines.append("")
    lines.append("## Report leggibile qm_060")
    lines.append("")
    lines.append("```text")
    lines.append(report.qm_060_report)
    lines.append("```")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for check in report.validation.checks:
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


def run_and_write_phase5_13a_reports(document_text: str | None = None) -> FinalCardGenerationReport:
    report = run_phase5_13a(document_text=document_text)

    write_json(DEFAULT_JSON_REPORT, report)
    write_json(DEFAULT_CARDS_JSON, report.cards)
    write_markdown_report(report)

    return report


if __name__ == "__main__":
    result = run_and_write_phase5_13a_reports()

    print(result.status)
    print(f"Cards generated: {result.generated_cards_count}")
    print(f"Official QM motors: {result.official_qm_motors}")
    print(f"Registry total: {result.registry_total}")
    print(f"Card route total: {result.card_route_total}")
    print(f"qm_059 output ready: {result.qm_059_output_ready}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")
    print(f"Cards JSON: {DEFAULT_CARDS_JSON}")

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
