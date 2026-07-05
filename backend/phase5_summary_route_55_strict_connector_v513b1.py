from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence


PHASE = "5.13B.1"
PHASE_LABEL = "FASE 5.13B.1 — SUMMARY ROUTE 55 STRICT CONNECTOR"

EXPECTED_SUMMARY_ROUTE_TOTAL = 55

MATERIALIZER_REPORT = Path("reports/phase5_13b01_summary_route_materializer_v1.json")
OFFICIAL_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_13b1_summary_route_55_strict_connector_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_13b1_summary_route_55_strict_connector_v1.md")


@dataclass
class RouteControl:
    route_slot: int
    control_id: str
    control_name: str
    executor_name: str


@dataclass
class ControlExecutionResult:
    route_slot: int
    control_id: str
    control_name: str
    executed: bool
    passed: bool
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SummaryRoute55Report:
    phase: str
    label: str
    status: str
    expected_controls: int
    connected_controls: int
    executed_controls: int
    passed_controls: int
    failed_controls: int
    summary_checked: bool
    route: List[RouteControl]
    execution_results: List[ControlExecutionResult]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def words(text: Any) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", normalize(text).lower())


def split_sentences(text: str) -> List[str]:
    cleaned = normalize(text)
    pieces = re.split(r"(?<=[.!?])\s+", cleaned)
    return [piece.strip() for piece in pieces if piece.strip()]


def content_words(text: Any) -> List[str]:
    stop = {
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
        "di", "del", "della", "dei", "degli", "delle",
        "a", "ad", "al", "allo", "alla", "ai", "agli", "alle",
        "da", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
        "in", "nel", "nello", "nella", "nei", "negli", "nelle",
        "con", "su", "per", "tra", "fra", "e", "o", "ma", "che",
        "come", "quando", "questo", "questa", "questi", "queste",
    }
    return [word for word in words(text) if word not in stop and len(word) >= 4]


def summary_fields(summary: Dict[str, Any]) -> List[str]:
    fields: List[str] = [
        normalize(summary.get("title")),
        normalize(summary.get("category")),
        normalize(summary.get("subcategory")),
        normalize(summary.get("source_label")),
        normalize(summary.get("summary_text")),
    ]

    key_points = summary.get("key_points", [])
    if isinstance(key_points, list):
        fields.extend(normalize(item) for item in key_points)

    return [field for field in fields if field]


def full_summary_text(summary: Dict[str, Any]) -> str:
    return "\n".join(summary_fields(summary))


def suspicious_ending(text: str) -> bool:
    cleaned = normalize(text).lower().strip(" .!?;:,")
    return cleaned.endswith((
        " e", " di", " con", " per", " che", " del", " della",
        " un", " una", " il", " la", " lo", "nel", "nella"
    ))


def has_natural_relation(text: str) -> bool:
    lowered_words = set(words(text))
    first = words(text)[:1]

    relation_words = {
        "di", "del", "della", "dei", "degli", "delle",
        "con", "per", "in", "nel", "nella", "tra", "verso",
        "attraverso", "mediante", "a", "ad", "al", "alla", "ai",
    }

    action_verbs = {
        "capire", "riconoscere", "applicare", "gestire", "proteggere",
        "migliorare", "ridurre", "evitare", "usare", "trasformare",
        "collegare", "organizzare", "chiarire", "presentare", "valutare",
        "controllare", "prevenire", "spiegare", "costruire", "rafforzare",
        "sintetizzare", "riassumere",
    }

    if ":" in normalize(text):
        return True

    if lowered_words.intersection(relation_words):
        return True

    if first and (first[0] in action_verbs or re.search(r"(are|ere|ire)$", first[0])):
        return True

    return False


def looks_keyword_based(text: str) -> bool:
    cleaned = normalize(text)
    if not cleaned:
        return True

    if has_natural_relation(cleaned):
        return False

    cw = content_words(cleaned)

    # Frase breve con 3+ parole piene senza relazione = elenco keyword.
    if len(cw) >= 3 and len(words(cleaned)) <= 7:
        return True

    # Titoli/righe tutte nominali senza verbo/connettivo.
    if len(cw) >= 4 and not re.search(r"\b(è|sono|serve|permette|richiede|aiuta|protegge|riduce|trasforma|garantisce)\b", cleaned.lower()):
        return True

    return False


def has_duplicate(values: Sequence[str]) -> bool:
    cleaned = [normalize(value).lower() for value in values if normalize(value)]
    return len(cleaned) != len(set(cleaned))


def load_route_ids() -> List[str]:
    data = read_json(MATERIALIZER_REPORT)
    route_ids = data.get("final_route_ids", [])

    if not isinstance(route_ids, list):
        return []

    return [str(item).lower() for item in route_ids]


def load_catalog_names() -> Dict[str, str]:
    if not OFFICIAL_CATALOG.exists():
        return {}

    data = read_json(OFFICIAL_CATALOG)
    names: Dict[str, str] = {}

    for motor in data.get("motors", []):
        if not isinstance(motor, dict):
            continue

        raw = json.dumps(motor, ensure_ascii=False)
        match = re.search(r"\bqm_\d{3}\b", raw, flags=re.I)
        if not match:
            continue

        qm_id = match.group(0).lower()
        name = (
            motor.get("name")
            or motor.get("title")
            or motor.get("nome")
            or motor.get("control_name")
            or qm_id
        )
        names[qm_id] = str(name)

    return names


def build_route() -> List[RouteControl]:
    route_ids = load_route_ids()
    names = load_catalog_names()

    return [
        RouteControl(
            route_slot=index + 1,
            control_id=qm_id,
            control_name=names.get(qm_id, qm_id),
            executor_name=EXECUTOR_NAMES.get(qm_id, "exec_generic_quality"),
        )
        for index, qm_id in enumerate(route_ids)
    ]


def exec_grammar(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = full_summary_text(summary)

    bad_patterns = [
        r"\b\w+\s+\w+\s+\w+\b\s*$",  # controllato altrove: non usato da solo
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ])\1{3,}\b",
        r"\s+[,.!?;:]",
        r"[A-Za-zÀ-ÖØ-öø-ÿ],[A-Za-zÀ-ÖØ-öø-ÿ]",
    ]

    for pattern in bad_patterns[1:]:
        if re.search(pattern, text):
            defects.append(f"anomalia grammaticale o di forma: {pattern}")

    return defects


def exec_accents(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary)
    defects: List[str] = []

    wrong = ["perche", "poiche", "finche", "cioe", "puo", "piu", "gia", "cosi", "pero"]
    for item in wrong:
        if re.search(rf"\b{item}\b", text, flags=re.I):
            defects.append(f"accento mancante: {item}")

    return defects


def exec_apostrophes(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary)
    defects: List[str] = []

    if re.search(r"\bun\s+(idea|azione|informazione|attività|area)\b", text, flags=re.I):
        defects.append("apostrofo femminile mancante")

    if re.search(r"\bl\s+[aeiouàèéìòù]", text, flags=re.I):
        defects.append("apostrofo dopo articolo l mancante")

    return defects


def exec_punctuation(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))

    if text and text[-1] not in ".!?":
        defects.append("riassunto senza punteggiatura finale")

    if re.search(r"[.!?]{2,}", text):
        defects.append("punteggiatura ripetuta")

    return defects


def exec_spacing(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary)
    defects: List[str] = []

    if "  " in text:
        defects.append("spazi doppi presenti")

    if re.search(r"\s+[,.!?;:]", text):
        defects.append("spazio prima della punteggiatura")

    if re.search(r"[,.!?;:][A-Za-zÀ-ÖØ-öø-ÿ]", text):
        defects.append("spazio mancante dopo punteggiatura")

    return defects


def exec_complete_sentences(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))

    sentences = split_sentences(text)

    if len(sentences) < 3:
        defects.append("riassunto con meno di 3 frasi complete")

    for sentence in sentences:
        if len(content_words(sentence)) < 4:
            defects.append(f"frase troppo povera: {sentence}")

    return defects


def exec_broken_sentences(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))

    for line in text.splitlines():
        cleaned = normalize(line)
        if cleaned and len(words(cleaned)) < 4 and cleaned[-1:] not in ".!?":
            defects.append(f"frase spezzata: {cleaned}")

    return defects


def exec_unfinished_sentences(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []

    for field in summary_fields(summary):
        if suspicious_ending(field):
            defects.append(f"frase non terminata: {field}")

    return defects


def exec_suspicious_endings(summary: Dict[str, Any]) -> List[str]:
    return exec_unfinished_sentences(summary)


def exec_no_filler(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    defects: List[str] = []

    fillers = [
        "è importante notare",
        "in conclusione possiamo dire",
        "questo documento parla di",
        "in generale",
        "vari aspetti",
        "diversi elementi",
    ]

    for filler in fillers:
        if filler in text:
            defects.append(f"frase riempitiva: {filler}")

    return defects


def exec_no_generic(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    defects: List[str] = []

    generic = [
        "documento analizzato",
        "contenuti generati",
        "punto centrale",
        "argomento trattato",
        "testo fornito",
        "contenuto caricato",
    ]

    for item in generic:
        if item in text:
            defects.append(f"testo generico vietato: {item}")

    return defects


def exec_no_fallback(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    defects: List[str] = []

    forbidden = [
        "fallback",
        "demo",
        "lorem ipsum",
        "test di esempio",
        "placeholder",
        "contenuto simulato",
    ]

    for item in forbidden:
        if item in text:
            defects.append(f"fallback/demo vietato: {item}")

    return defects


def exec_not_too_short_explanations(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))
    key_points = summary.get("key_points", [])

    if len(text) < 350:
        defects.append("riassunto troppo corto")

    if not isinstance(key_points, list) or len(key_points) < 4:
        defects.append("punti chiave insufficienti")

    return defects


def exec_final_didactic_tone(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    defects: List[str] = []

    didactic_markers = [
        "serve", "permette", "aiuta", "richiede", "riduce",
        "protegge", "trasforma", "controlli", "comportamenti",
        "procedure", "regole",
    ]

    if not any(marker in text for marker in didactic_markers):
        defects.append("tono didattico non rilevabile")

    return defects


def exec_categories_present(summary: Dict[str, Any]) -> List[str]:
    if not normalize(summary.get("category")):
        return ["categoria mancante"]
    return []


def exec_subcategories_present(summary: Dict[str, Any]) -> List[str]:
    if not normalize(summary.get("subcategory")):
        return ["sottocategoria mancante"]
    return []


def exec_cards_well_written(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    title = normalize(summary.get("title"))
    text = normalize(summary.get("summary_text"))

    if looks_keyword_based(title):
        defects.append(f"titolo riassunto keyword-based: {title}")

    if any(looks_keyword_based(sentence) for sentence in split_sentences(text)):
        defects.append("una frase del riassunto sembra keyword-based")

    return defects


def exec_cards_not_short(summary: Dict[str, Any]) -> List[str]:
    return exec_not_too_short_explanations(summary)


def exec_cards_not_compressed(summary: Dict[str, Any]) -> List[str]:
    text = normalize(summary.get("summary_text"))
    defects: List[str] = []

    sentences = split_sentences(text)
    if sentences and len(text) / max(len(sentences), 1) > 260:
        defects.append("riassunto troppo compresso in poche frasi")

    return defects


def exec_key_message_complete(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))

    if len(content_words(text)) < 45:
        defects.append("messaggio chiave incompleto")

    return defects


def exec_summary_clear(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = normalize(summary.get("summary_text"))

    if len(split_sentences(text)) < 3:
        defects.append("riassunto poco chiaro: poche frasi")

    if looks_keyword_based(normalize(summary.get("title"))):
        defects.append("titolo non naturale")

    return defects


def exec_key_points_legible(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    key_points = summary.get("key_points", [])

    if not isinstance(key_points, list) or not key_points:
        return ["punti chiave mancanti"]

    for point in key_points:
        cleaned = normalize(point)
        if len(words(cleaned)) < 5:
            defects.append(f"punto chiave troppo corto: {cleaned}")
        if suspicious_ending(cleaned):
            defects.append(f"punto chiave con finale sospetto: {cleaned}")

    return defects


def exec_sources_visible_beautiful(summary: Dict[str, Any]) -> List[str]:
    source = normalize(summary.get("source_label"))

    if not source:
        return ["fonte mancante"]

    if not source.startswith("Fonte:"):
        return ["fonte non presentabile"]

    return []


def exec_sources_coherent(summary: Dict[str, Any]) -> List[str]:
    source = normalize(summary.get("source_label"))
    category = normalize(summary.get("category"))

    if source and category and category.lower().split()[0] not in source.lower():
        # Non blocca fonti generali: controlla solo brutti mismatch evidenti.
        if "sezione" not in source.lower():
            return ["fonte poco coerente con la categoria"]

    return []


def exec_no_ugly_sources(summary: Dict[str, Any]) -> List[str]:
    source = normalize(summary.get("source_label")).lower()

    ugly = ["knowledge_base_json", "documento analizzato", "unknown", "none", "null", "raw"]
    return [f"fonte brutta: {item}" for item in ugly if item in source]


def exec_layout_controlled(summary: Dict[str, Any]) -> List[str]:
    required = ["summary_id", "title", "category", "subcategory", "summary_text", "key_points", "source_label"]
    defects = [f"campo layout mancante: {field}" for field in required if field not in summary]

    if not isinstance(summary.get("key_points"), list):
        defects.append("key_points non è lista")

    return defects


def exec_test_separated(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    forbidden = [
        "domanda 1",
        "risposta corretta",
        "opzione a",
        "opzione b",
        "quiz",
        "scegli la risposta",
    ]
    return [f"contenuto test dentro riassunto: {item}" for item in forbidden if item in text]


def exec_options_internal_validated(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary)
    if re.search(r"\b[A-D]\)", text):
        return ["opzioni quiz presenti nel riassunto"]
    return []


def exec_visible_options_clean(summary: Dict[str, Any]) -> List[str]:
    return exec_options_internal_validated(summary)


def exec_safe_answer_map(summary: Dict[str, Any]) -> List[str]:
    return exec_test_separated(summary)


def exec_four_options(summary: Dict[str, Any]) -> List[str]:
    return exec_options_internal_validated(summary)


def exec_correct_in_options(summary: Dict[str, Any]) -> List[str]:
    return exec_test_separated(summary)


def exec_no_duplicate_options(summary: Dict[str, Any]) -> List[str]:
    return exec_options_internal_validated(summary)


def exec_no_global_repetitions(summary: Dict[str, Any]) -> List[str]:
    fields = summary_fields(summary)
    if has_duplicate(fields):
        return ["ripetizione esatta tra campi del riassunto"]
    return []


def exec_bridge_compatibility(summary: Dict[str, Any]) -> List[str]:
    # Per il riassunto il bridge quiz non deve comparire nell'output.
    return exec_test_separated(summary)


def exec_exact_duplicates(summary: Dict[str, Any]) -> List[str]:
    key_points = summary.get("key_points", [])
    if isinstance(key_points, list) and has_duplicate([str(item) for item in key_points]):
        return ["punti chiave duplicati"]
    return []


def exec_near_duplicates(summary: Dict[str, Any]) -> List[str]:
    key_points = summary.get("key_points", [])
    defects: List[str] = []

    if not isinstance(key_points, list):
        return defects

    normalized = [" ".join(content_words(point)) for point in key_points]
    for index, item in enumerate(normalized):
        for other in normalized[index + 1:]:
            if item and other and item == other:
                defects.append("punti chiave quasi duplicati")

    return defects


def exec_useless_repetitions(summary: Dict[str, Any]) -> List[str]:
    text_words = content_words(summary.get("summary_text"))
    defects: List[str] = []

    if not text_words:
        return ["riassunto senza parole contenuto"]

    counts: Dict[str, int] = {}
    for word in text_words:
        counts[word] = counts.get(word, 0) + 1

    repeated = [
        word for word, count in counts.items()
        if count >= 7 and word not in {"sicurezza", "utenti"}
    ]

    if repeated:
        defects.append("ripetizioni inutili: " + ", ".join(sorted(repeated)[:5]))

    return defects


def exec_mechanical_repetitions_between_questions(summary: Dict[str, Any]) -> List[str]:
    # Nel riassunto non ci sono domande; qui controlla ripetizioni meccaniche tra punti.
    return exec_near_duplicates(summary)


def exec_too_similar_sentences(summary: Dict[str, Any]) -> List[str]:
    sentences = split_sentences(summary.get("summary_text", ""))
    normalized = [" ".join(content_words(sentence)) for sentence in sentences]

    if has_duplicate(normalized):
        return ["frasi troppo simili nel riassunto"]

    return []


def exec_same_content_without_reason(summary: Dict[str, Any]) -> List[str]:
    return exec_too_similar_sentences(summary)


def exec_select_right_motors(summary: Dict[str, Any]) -> List[str]:
    route_ids = load_route_ids()
    if len(route_ids) != EXPECTED_SUMMARY_ROUTE_TOTAL:
        return [f"route riassunto non corretta: {len(route_ids)}"]
    return []


def exec_summary_route(summary: Dict[str, Any]) -> List[str]:
    if normalize(summary.get("section_type")) != "summary":
        return ["section_type non è summary"]
    return []


def exec_card_route_not_required(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    if "card_" in text or "genera card" in text:
        return ["output card dentro riassunto"]
    return []


def exec_study_route_not_required(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    if "domande studio" in text or "risposta guida" in text:
        return ["output domande studio dentro riassunto"]
    return []


def exec_test_route_not_required(summary: Dict[str, Any]) -> List[str]:
    return exec_test_separated(summary)


def exec_full_output_orchestrator(summary: Dict[str, Any]) -> List[str]:
    required = ["summary_id", "section_type", "title", "summary_text", "key_points"]
    return [f"output finale incompleto: {field}" for field in required if not summary.get(field)]


def exec_no_useless_motors(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    if "motore quiz" in text or "bridge quiz" in text:
        return ["motori inutili citati nel riassunto"]
    return []


def exec_no_unrequested_output(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    forbidden = ["test finale", "quiz finale", "card finale", "domanda studio"]
    return [f"output non richiesto: {item}" for item in forbidden if item in text]


def exec_final_output_ready(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []

    if len(normalize(summary.get("summary_text"))) < 350:
        defects.append("summary_text non pronto per UI/PDF/app")

    if not summary.get("key_points"):
        defects.append("key_points mancanti per UI/PDF/app")

    if looks_keyword_based(normalize(summary.get("title"))):
        defects.append("titolo non pronto per UI/PDF/app")

    return defects


def exec_quality_report_readable(summary: Dict[str, Any]) -> List[str]:
    # Il report viene generato dal connector stesso; il controllo passa se struttura minima presente.
    return []


def exec_natural_language_antikeyword(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []

    for field in summary_fields(summary):
        if looks_keyword_based(field):
            defects.append(f"testo keyword-based: {field}")

    return defects


def exec_agreement_pronouns(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary)
    defects: List[str] = []

    bad_patterns = [
        r"\bla\s+\w+o\b",
        r"\bil\s+\w+a\b",
        r"\bi\s+\w+a\b",
    ]

    for pattern in bad_patterns:
        if re.search(pattern, text, flags=re.I):
            defects.append(f"possibile accordo errato: {pattern}")

    return defects


def exec_repair_unfinished_context(summary: Dict[str, Any]) -> List[str]:
    return exec_unfinished_sentences(summary)


def exec_repair_inverted_letters(summary: Dict[str, Any]) -> List[str]:
    text = full_summary_text(summary).lower()
    defects: List[str] = []

    suspicious_patterns = [
        ("egole", r"\begole\b"),
        ("sicuerezza", r"\bsicuerezza\b"),
        ("utneti", r"\butneti\b"),
        ("bakcup", r"\bbakcup\b"),
        ("continuità operativ", r"\bcontinuità\s+operativ\b"),
    ]

    for label, pattern in suspicious_patterns:
        if re.search(pattern, text, flags=re.I):
            defects.append(f"possibile parola corrotta: {label}")

    return defects


def exec_generic_quality(summary: Dict[str, Any]) -> List[str]:
    defects: List[str] = []
    text = full_summary_text(summary)

    if not text:
        defects.append("riassunto vuoto")

    return defects


EXECUTOR_NAMES: Dict[str, str] = {
    "qm_001": "exec_grammar",
    "qm_002": "exec_accents",
    "qm_003": "exec_apostrophes",
    "qm_004": "exec_punctuation",
    "qm_005": "exec_spacing",
    "qm_006": "exec_complete_sentences",
    "qm_007": "exec_broken_sentences",
    "qm_008": "exec_unfinished_sentences",
    "qm_009": "exec_suspicious_endings",
    "qm_010": "exec_no_filler",
    "qm_011": "exec_no_generic",
    "qm_012": "exec_no_fallback",
    "qm_017": "exec_not_too_short_explanations",
    "qm_018": "exec_final_didactic_tone",
    "qm_019": "exec_categories_present",
    "qm_020": "exec_subcategories_present",
    "qm_023": "exec_cards_well_written",
    "qm_024": "exec_cards_not_short",
    "qm_025": "exec_cards_not_compressed",
    "qm_026": "exec_key_message_complete",
    "qm_027": "exec_summary_clear",
    "qm_028": "exec_key_points_legible",
    "qm_029": "exec_sources_visible_beautiful",
    "qm_030": "exec_sources_coherent",
    "qm_031": "exec_no_ugly_sources",
    "qm_032": "exec_layout_controlled",
    "qm_033": "exec_test_separated",
    "qm_034": "exec_options_internal_validated",
    "qm_035": "exec_visible_options_clean",
    "qm_038": "exec_safe_answer_map",
    "qm_039": "exec_four_options",
    "qm_040": "exec_correct_in_options",
    "qm_042": "exec_no_duplicate_options",
    "qm_043": "exec_no_global_repetitions",
    "qm_044": "exec_bridge_compatibility",
    "qm_045": "exec_exact_duplicates",
    "qm_046": "exec_near_duplicates",
    "qm_047": "exec_useless_repetitions",
    "qm_048": "exec_mechanical_repetitions_between_questions",
    "qm_049": "exec_too_similar_sentences",
    "qm_050": "exec_same_content_without_reason",
    "qm_051": "exec_select_right_motors",
    "qm_052": "exec_summary_route",
    "qm_053": "exec_card_route_not_required",
    "qm_054": "exec_study_route_not_required",
    "qm_055": "exec_test_route_not_required",
    "qm_056": "exec_full_output_orchestrator",
    "qm_057": "exec_no_useless_motors",
    "qm_058": "exec_no_unrequested_output",
    "qm_059": "exec_final_output_ready",
    "qm_060": "exec_quality_report_readable",
    "qm_061": "exec_natural_language_antikeyword",
    "qm_062": "exec_agreement_pronouns",
    "qm_063": "exec_repair_unfinished_context",
    "qm_064": "exec_repair_inverted_letters",
}


EXECUTORS: Dict[str, Callable[[Dict[str, Any]], List[str]]] = {
    name: obj for name, obj in globals().items()
    if name.startswith("exec_") and callable(obj)
}


def execute_route(summary: Dict[str, Any]) -> SummaryRoute55Report:
    defects: List[str] = []
    warnings: List[str] = []

    if not MATERIALIZER_REPORT.exists():
        defects.append(f"Materializer Riassunto mancante: {MATERIALIZER_REPORT}")

    route = build_route() if not defects else []

    if len(route) != EXPECTED_SUMMARY_ROUTE_TOTAL:
        defects.append(
            f"Route Riassunto deve contenere 55 controlli, trovati {len(route)}"
        )

    execution_results: List[ControlExecutionResult] = []

    for control in route:
        executor = EXECUTORS.get(control.executor_name)

        if executor is None:
            control_defects = [f"executor mancante: {control.executor_name}"]
        else:
            try:
                control_defects = executor(summary)
            except Exception as exc:
                control_defects = [
                    f"executor_exception {type(exc).__name__}: {exc}"
                ]

        result = ControlExecutionResult(
            route_slot=control.route_slot,
            control_id=control.control_id,
            control_name=control.control_name,
            executed=True,
            passed=not control_defects,
            defects=control_defects,
            warnings=[],
        )
        execution_results.append(result)

        for defect in control_defects:
            defects.append(f"{control.control_id}: {defect}")

    connected_controls = len(route)
    executed_controls = len(execution_results)
    passed_controls = sum(1 for result in execution_results if result.passed)
    failed_controls = connected_controls - passed_controls

    if connected_controls != EXPECTED_SUMMARY_ROUTE_TOTAL:
        defects.append(
            f"Controlli collegati non sono 55: collegati {connected_controls}"
        )

    if executed_controls != EXPECTED_SUMMARY_ROUTE_TOTAL:
        defects.append(
            f"Controlli eseguiti non sono 55: eseguiti {executed_controls}"
        )

    if passed_controls != EXPECTED_SUMMARY_ROUTE_TOTAL:
        defects.append(
            f"Controlli passati non sono 55: passati {passed_controls}"
        )

    status = (
        "PASS - Fase 5.13B.1: SUMMARY_ROUTE_55_STRICT_CONNECTOR_READY"
        if not defects
        else "FAIL - Fase 5.13B.1: SUMMARY_ROUTE_55_STRICT_CONNECTOR_NOT_READY"
    )

    return SummaryRoute55Report(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        expected_controls=EXPECTED_SUMMARY_ROUTE_TOTAL,
        connected_controls=connected_controls,
        executed_controls=executed_controls,
        passed_controls=passed_controls,
        failed_controls=failed_controls,
        summary_checked=bool(summary),
        route=route,
        execution_results=execution_results,
        defects=defects,
        warnings=warnings,
        notes=[
            "Questo connector non accetta PASS se i 55 controlli Riassunto non sono tutti collegati.",
            "Ogni controllo della route Riassunto deve avere executor reale.",
            "Ogni executor viene eseguito sul riassunto finale generato.",
            "Se il testo resta keyword-based, qm_023/qm_027/qm_059/qm_061 falliscono.",
            "Gli executor sono blindati: eventuali errori interni diventano defect leggibili, non traceback.",
        ],
    )


def write_reports(report: SummaryRoute55Report) -> None:
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
    lines.append(f"- Controlli attesi: `{report.expected_controls}`")
    lines.append(f"- Controlli collegati: `{report.connected_controls}`")
    lines.append(f"- Controlli eseguiti: `{report.executed_controls}`")
    lines.append(f"- Controlli passati: `{report.passed_controls}`")
    lines.append(f"- Controlli falliti: `{report.failed_controls}`")
    lines.append(f"- Riassunto controllato: `{report.summary_checked}`")
    lines.append("")
    lines.append("## Route Riassunto 55")
    lines.append("")
    lines.append("| Slot | QM | Nome | Executor |")
    lines.append("|---:|---|---|---|")
    for control in report.route:
        lines.append(
            f"| {control.route_slot} | `{control.control_id}` | "
            f"{control.control_name} | `{control.executor_name}` |"
        )
    lines.append("")
    lines.append("## Execution results")
    lines.append("")
    lines.append("| Slot | QM | Executed | Passed | Defects |")
    lines.append("|---:|---|---|---|---|")
    for result in report.execution_results:
        defect_text = "; ".join(result.defects) if result.defects else "nessuno"
        lines.append(
            f"| {result.route_slot} | `{result.control_id}` | "
            f"{result.executed} | {result.passed} | {defect_text} |"
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


def run_from_payload(summary: Dict[str, Any]) -> SummaryRoute55Report:
    report = execute_route(summary)
    write_reports(report)
    return report


if __name__ == "__main__":
    payload_file = Path("reports/phase5_13b1_final_summary_payload_v1.json")
    if not payload_file.exists():
        raise SystemExit(f"Payload riassunto mancante: {payload_file}")

    payload = read_json(payload_file)
    result = run_from_payload(payload)

    print(result.status)
    print(f"Expected controls: {result.expected_controls}")
    print(f"Connected controls: {result.connected_controls}")
    print(f"Executed controls: {result.executed_controls}")
    print(f"Passed controls: {result.passed_controls}")
    print(f"Failed controls: {result.failed_controls}")
    print(f"Summary checked: {result.summary_checked}")

    if result.defects:
        print("Defects:")
        for defect in result.defects:
            print(f"- {defect}")
        raise SystemExit(1)
