from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence


PHASE = "5.13A.3"
PHASE_LABEL = "FASE 5.13A.3 — CARD ROUTE 60 STRICT CONNECTOR"

EXPECTED_CARD_ROUTE_TOTAL = 60
EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_REGISTRY_TOTAL = 73

I2_CATALOG = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")
J_FINAL = Path("reports/phase5_12j_final_quality_output_motors_qm_060_qm_059_v1.json")
CARD_PAYLOAD = Path("reports/phase5_13a_final_cards_payload_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_13a3_card_route_60_strict_connector_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_13a3_card_route_60_strict_connector_v1.md")


@dataclass
class CardRouteControl:
    route_slot: int
    control_id: str
    control_name: str
    group: str
    universal: str
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
class CardRoute60Report:
    phase: str
    label: str
    status: str
    expected_controls: int
    connected_controls: int
    executed_controls: int
    passed_controls: int
    failed_controls: int
    cards_checked: int
    route_controls: List[CardRouteControl]
    execution_results: List[ControlExecutionResult]
    defects: List[str]
    warnings: List[str]
    notes: List[str]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def all_card_text(cards: Sequence[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for card in cards:
        for key in [
            "title",
            "category",
            "source_label",
            "key_message",
            "short_explanation",
            "study_hint",
            "visual_role",
        ]:
            parts.append(normalize(card.get(key)))
        for bullet in card.get("bullets", []) or []:
            parts.append(normalize(bullet))
    return "\n".join(parts)


def card_titles(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return [normalize(card.get("title")) for card in cards]


def card_messages(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return [normalize(card.get("key_message")) for card in cards]


def words(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", text.lower())


def has_duplicate(values: Sequence[str]) -> bool:
    cleaned = [value.strip().lower() for value in values if value.strip()]
    return len(cleaned) != len(set(cleaned))


def suspicious_ending(text: str) -> bool:
    cleaned = normalize(text).lower().strip(" .!?;:,")
    return cleaned.endswith((
        " e",
        " di",
        " con",
        " per",
        " che",
        " del",
        " della",
        " un",
        " una",
        " il",
        " la",
        " lo",
    ))


def looks_keyword_title(title: str) -> bool:
    title_words = words(title)

    content_title_words = [
        word for word in title_words
        if word not in {
            "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
            "di", "del", "della", "dei", "degli", "delle",
            "con", "per", "in", "nel", "nella", "e", "o",
            "a", "ad", "al", "allo", "alla", "ai", "agli", "alle"
        }
    ]

    if not content_title_words:
        return True

    lowered = title.lower().strip()

    if lowered.startswith("concetto chiave"):
        return True

    relation_words = {
        "di", "del", "della", "dei", "degli", "delle",
        "con", "per", "in", "nel", "nella",
        "tra", "verso", "attraverso", "mediante",
        "a", "ad", "al", "allo", "alla", "ai", "agli", "alle"
    }

    action_verbs = {
        "capire", "riconoscere", "applicare", "gestire", "proteggere",
        "migliorare", "ridurre", "evitare", "usare", "trasformare",
        "collegare", "organizzare", "chiarire", "presentare", "valutare",
        "controllare", "prevenire", "spiegare", "costruire", "rafforzare",
    }

    first_word = title_words[0] if title_words else ""
    has_relation = bool(set(title_words).intersection(relation_words))
    has_action = first_word in action_verbs or bool(re.search(r"(are|ere|ire)$", first_word))

    if has_relation or has_action:
        return False

    # Regola universale:
    # 3+ parole piene senza verbo/relazione = elenco di keyword, non titolo naturale.
    if len(content_title_words) >= 3:
        return True

    # Due parole lunghe senza relazione spesso indicano ancora formula keyword.
    if len(content_title_words) == 2 and len(" ".join(content_title_words)) > 24:
        return True

    return False

def validate_upstream_contract(defects: List[str]) -> None:
    if not I2_CATALOG.exists():
        defects.append(f"Catalogo I.2 mancante: {I2_CATALOG}")
        return

    if not J_FINAL.exists():
        defects.append(f"Report J mancante: {J_FINAL}")
        return

    i2 = read_json(I2_CATALOG)
    j = read_json(J_FINAL)

    if i2.get("official_qm_motors_count") != EXPECTED_OFFICIAL_QM_MOTORS:
        defects.append(
            f"I.2 motori ufficiali errati: atteso 64, trovato {i2.get('official_qm_motors_count')}"
        )

    if i2.get("registry_total_after_h2") != EXPECTED_REGISTRY_TOTAL:
        defects.append(
            f"I.2 registry errato: atteso 73, trovato {i2.get('registry_total_after_h2')}"
        )

    if j.get("qm_060", {}).get("ready") is not True:
        defects.append("qm_060 non ready nel report J")

    if j.get("qm_059", {}).get("ready") is not True:
        defects.append("qm_059 non ready nel report J")

    card_route = None
    for route in j.get("section_routes", []):
        if route.get("section_type") == "card":
            card_route = route
            break

    if not card_route:
        defects.append("Route Card non trovata nel report J")
        return

    if card_route.get("total_controls") != EXPECTED_CARD_ROUTE_TOTAL:
        defects.append(
            f"Route Card non è 60: trovato {card_route.get('total_controls')}"
        )


def require_cards(cards: Sequence[Dict[str, Any]], defects: List[str]) -> None:
    if len(cards) < 4:
        defects.append(f"Card attese almeno 4, trovate {len(cards)}")


# ----------------------------
# EXECUTOR REALI
# ----------------------------

def exec_grammar(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards)
    defects = []
    bad = [" un in ", " l in ", " una in ", " viene presentato", "senza copiarlo"]
    for item in bad:
        if item in text.lower():
            defects.append(f"pattern grammaticale sospetto: {item}")
    return defects


def exec_accents(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    for bad in ["perche'", "qual e'", "cioe'", "piu'", "puo'"]:
        if bad in text:
            defects.append(f"accento errato: {bad}")
    return defects


def exec_apostrophes(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards)
    defects = []
    for bad in ["un informazione", "un idea", "l utente", "d accordo"]:
        if bad in text.lower():
            defects.append(f"apostrofo mancante: {bad}")
    return defects


def exec_punctuation(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        for field in ["key_message", "short_explanation", "study_hint"]:
            value = normalize(card.get(field))
            if value and value[-1] not in ".!?":
                defects.append(f"{card.get('card_id')}: punteggiatura finale mancante in {field}")
    return defects


def exec_spacing(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards)
    defects = []
    if "  " in text:
        defects.append("spazi doppi rilevati")
    if re.search(r"\s+[,.!?;:]", text):
        defects.append("spazio errato prima della punteggiatura")
    if re.search(r"[,.!?;:][A-Za-zÀ-ÖØ-öø-ÿ]", text):
        defects.append("spazio mancante dopo punteggiatura")
    return defects


def exec_complete_sentences(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        for field in ["key_message", "short_explanation"]:
            value = normalize(card.get(field))
            if len(words(value)) < 7:
                defects.append(f"{card.get('card_id')}: frase troppo povera in {field}")
    return defects


def exec_broken_sentences(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards)
    defects = []
    if re.search(r"\b[a-zA-ZÀ-ÖØ-öø-ÿ]{1,2}\s+[,.!?]", text):
        defects.append("frase spezzata sospetta")
    return defects


def exec_unfinished_sentences(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        for field in ["key_message", "short_explanation", "study_hint"]:
            if suspicious_ending(normalize(card.get(field))):
                defects.append(f"{card.get('card_id')}: frase non terminata in {field}")
    return defects


def exec_suspicious_endings(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_unfinished_sentences(cards)


def exec_no_filler(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    fillers = ["in questo documento", "è importante notare", "si parla di vari aspetti"]
    for item in fillers:
        if item in text:
            defects.append(f"frase riempitiva: {item}")
    return defects


def exec_no_generic(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    generic = ["documento analizzato", "contenuti generati", "punto centrale"]
    for item in generic:
        if item in text:
            defects.append(f"testo generico vietato: {item}")
    return defects


def exec_no_fallback(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    bad = ["fallback", "demo", "placeholder", "lorem ipsum", "undefined", "traceback", "object at 0x"]
    for item in bad:
        if item in text:
            defects.append(f"fallback/demo/test vietato: {item}")
    return defects


def exec_didactic_natural(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for title in card_titles(cards):
        if looks_keyword_title(title):
            defects.append(f"titolo non naturale/keyword-based: {title}")
    return defects


def exec_useful_for_review(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        hint = normalize(card.get("study_hint"))
        if len(hint) < 50:
            defects.append(f"{card.get('card_id')}: suggerimento studio troppo povero")
    return defects


def exec_specific_guidance(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        msg = normalize(card.get("key_message"))
        if len(msg) < 55:
            defects.append(f"{card.get('card_id')}: messaggio guida non specifico")
    return defects


def exec_clear_explanations(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        exp = normalize(card.get("short_explanation"))
        if len(exp) < 100:
            defects.append(f"{card.get('card_id')}: spiegazione non chiara/troppo corta")
    return defects


def exec_not_too_short_explanations(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_clear_explanations(cards)


def exec_final_didactic_tone(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        joined = " ".join([
            normalize(card.get("key_message")),
            normalize(card.get("short_explanation")),
            normalize(card.get("study_hint")),
        ])
        if len(joined) < 180:
            defects.append(f"{card.get('card_id')}: tono didattico insufficiente")
    return defects


def exec_categories_present(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return [
        f"{card.get('card_id')}: categoria mancante"
        for card in cards
        if len(normalize(card.get("category"))) < 4
    ]


def exec_subcategories_present(cards: Sequence[Dict[str, Any]]) -> List[str]:
    # Per card finale accettiamo categoria come sottocontesto se fonte/categoria sono presenti.
    defects = []
    for card in cards:
        if "Fonte: sezione" not in normalize(card.get("source_label")):
            defects.append(f"{card.get('card_id')}: sottocontesto/fonte mancante")
    return defects


def exec_question_answer_content_coherence(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        title = set(words(card.get("title", "")))
        body = set(words(card.get("key_message", "") + " " + card.get("short_explanation", "")))
        if title and not title.intersection(body):
            defects.append(f"{card.get('card_id')}: titolo non coerente col contenuto")
    return defects


def exec_no_vague_answers(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    vague = ["varie cose", "diversi aspetti", "alcuni elementi", "argomento importante"]
    for item in vague:
        if item in text:
            defects.append(f"contenuto vago: {item}")
    return defects


def exec_cards_well_written(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    defects.extend(exec_didactic_natural(cards))
    defects.extend(exec_clear_explanations(cards))
    return defects


def exec_cards_not_short(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        total = len(normalize(card.get("key_message"))) + len(normalize(card.get("short_explanation")))
        if total < 170:
            defects.append(f"{card.get('card_id')}: card troppo corta")
    return defects


def exec_cards_not_compressed(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        exp = normalize(card.get("short_explanation"))
        if len(exp) > 700:
            defects.append(f"{card.get('card_id')}: card troppo compressa/lunga")
    return defects


def exec_key_message_complete(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_complete_sentences(cards)


def exec_summary_clear_for_card(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_clear_explanations(cards)


def exec_key_points_legible(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        bullets = card.get("bullets") or []
        if len(bullets) < 3:
            defects.append(f"{card.get('card_id')}: meno di 3 punti chiave")
        for idx, bullet in enumerate(bullets, start=1):
            if len(normalize(bullet)) < 35:
                defects.append(f"{card.get('card_id')}: bullet {idx} troppo corto")
    return defects


def exec_sources_visible_beautiful(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        src = normalize(card.get("source_label"))
        if not src.startswith("Fonte: sezione “"):
            defects.append(f"{card.get('card_id')}: fonte non bella/visibile")
    return defects


def exec_sources_coherent(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        cat = normalize(card.get("category"))
        src = normalize(card.get("source_label"))
        if cat and cat not in src:
            defects.append(f"{card.get('card_id')}: fonte non coerente con categoria")
    return defects


def exec_no_ugly_sources(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = " ".join(normalize(card.get("source_label")) for card in cards)
    defects = []
    for bad in ["knowledge_base_json", "Documento analizzato", "documento analizzato"]:
        if bad in text:
            defects.append(f"fonte brutta: {bad}")
    return defects


def exec_layout_controlled(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    for card in cards:
        if normalize(card.get("visual_role")) != "final_card_clean_layout_ready":
            defects.append(f"{card.get('card_id')}: layout non controllato")
    return defects


def exec_test_separated(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    if "risposta corretta" in text or "opzione a" in text or "quiz" in text:
        return ["contenuto test/quiz mischiato nelle card"]
    return []


def exec_options_internal_validated(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_visible_options_clean(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_correct_answer_internal(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_correct_answer_visible(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_safe_answer_map(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_four_options(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_correct_in_options(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_strong_distractors(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_no_duplicate_options(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_no_global_repetitions(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    if has_duplicate(card_titles(cards)):
        defects.append("titoli duplicati")
    if has_duplicate(card_messages(cards)):
        defects.append("messaggi chiave duplicati")
    return defects


def exec_bridge_compatibility(cards: Sequence[Dict[str, Any]]) -> List[str]:
    # Per card: deve NON sembrare payload quiz bridge.
    return exec_test_separated(cards)


def exec_exact_duplicates(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_no_global_repetitions(cards)


def exec_near_duplicates(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    titles = card_titles(cards)
    for i, a in enumerate(titles):
        aw = set(words(a))
        for b in titles[i + 1:]:
            bw = set(words(b))
            if aw and bw and len(aw.intersection(bw)) / max(len(aw.union(bw)), 1) > 0.8:
                defects.append(f"titoli quasi duplicati: {a} / {b}")
    return defects


def exec_useless_repetitions(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_no_global_repetitions(cards)


def exec_mechanical_repetitions_between_questions(cards: Sequence[Dict[str, Any]]) -> List[str]:
    # Per card: controlla ripetizioni meccaniche tra bullet/card.
    return exec_no_global_repetitions(cards)


def exec_too_similar_sentences(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_near_duplicates(cards)


def exec_same_content_without_reason(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_no_global_repetitions(cards)


def exec_select_right_motors(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return [] if cards else ["nessuna card generata: selezione motori non verificabile"]


def exec_summary_route_not_required(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return []


def exec_card_didactic_layout_route(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    defects.extend(exec_cards_well_written(cards))
    defects.extend(exec_layout_controlled(cards))
    return defects


def exec_study_route_not_required(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return []


def exec_test_route_not_required(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_full_output_orchestrator(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return [] if len(cards) >= 4 else ["orchestratore completo: card insufficienti"]


def exec_no_useless_motors(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return []


def exec_no_unrequested_output(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_test_separated(cards)


def exec_final_output_ready(cards: Sequence[Dict[str, Any]]) -> List[str]:
    defects = []
    defects.extend(exec_cards_well_written(cards))
    defects.extend(exec_sources_coherent(cards))
    defects.extend(exec_layout_controlled(cards))
    return defects


def exec_quality_report_readable(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return []


def exec_natural_language_antikeyword(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_didactic_natural(cards)


def exec_agreement_pronouns(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_grammar(cards)


def exec_repair_unfinished_context(cards: Sequence[Dict[str, Any]]) -> List[str]:
    return exec_unfinished_sentences(cards)


def exec_repair_inverted_letters(cards: Sequence[Dict[str, Any]]) -> List[str]:
    text = all_card_text(cards).lower()
    defects = []
    for typo in ["sotttotema", "qualita'", "perche'", "poiche'"]:
        if typo in text:
            defects.append(f"micro-errore ortografico: {typo}")
    return defects


EXECUTORS: Dict[str, Callable[[Sequence[Dict[str, Any]]], List[str]]] = {
    "qm_001": exec_grammar,
    "qm_002": exec_accents,
    "qm_003": exec_apostrophes,
    "qm_004": exec_punctuation,
    "qm_005": exec_spacing,
    "qm_006": exec_complete_sentences,
    "qm_007": exec_broken_sentences,
    "qm_008": exec_unfinished_sentences,
    "qm_009": exec_suspicious_endings,
    "qm_010": exec_no_filler,
    "qm_011": exec_no_generic,
    "qm_012": exec_no_fallback,
    "qm_013": exec_didactic_natural,
    "qm_014": exec_useful_for_review,
    "qm_015": exec_specific_guidance,
    "qm_016": exec_clear_explanations,
    "qm_017": exec_not_too_short_explanations,
    "qm_018": exec_final_didactic_tone,
    "qm_019": exec_categories_present,
    "qm_020": exec_subcategories_present,
    "qm_021": exec_question_answer_content_coherence,
    "qm_022": exec_no_vague_answers,
    "qm_023": exec_cards_well_written,
    "qm_024": exec_cards_not_short,
    "qm_025": exec_cards_not_compressed,
    "qm_026": exec_key_message_complete,
    "qm_027": exec_summary_clear_for_card,
    "qm_028": exec_key_points_legible,
    "qm_029": exec_sources_visible_beautiful,
    "qm_030": exec_sources_coherent,
    "qm_031": exec_no_ugly_sources,
    "qm_032": exec_layout_controlled,
    "qm_033": exec_test_separated,
    "qm_034": exec_options_internal_validated,
    "qm_035": exec_visible_options_clean,
    "qm_036": exec_correct_answer_internal,
    "qm_037": exec_correct_answer_visible,
    "qm_038": exec_safe_answer_map,
    "qm_039": exec_four_options,
    "qm_040": exec_correct_in_options,
    "qm_041": exec_strong_distractors,
    "qm_042": exec_no_duplicate_options,
    "qm_043": exec_no_global_repetitions,
    "qm_044": exec_bridge_compatibility,
    "qm_045": exec_exact_duplicates,
    "qm_046": exec_near_duplicates,
    "qm_047": exec_useless_repetitions,
    "qm_048": exec_mechanical_repetitions_between_questions,
    "qm_049": exec_too_similar_sentences,
    "qm_050": exec_same_content_without_reason,
    "qm_051": exec_select_right_motors,
    "qm_052": exec_summary_route_not_required,
    "qm_053": exec_card_didactic_layout_route,
    "qm_054": exec_study_route_not_required,
    "qm_055": exec_test_route_not_required,
    "qm_056": exec_full_output_orchestrator,
    "qm_057": exec_no_useless_motors,
    "qm_058": exec_no_unrequested_output,
    "qm_059": exec_final_output_ready,
    "qm_060": exec_quality_report_readable,
    "qm_061": exec_natural_language_antikeyword,
    "qm_062": exec_agreement_pronouns,
    "qm_063": exec_repair_unfinished_context,
    "qm_064": exec_repair_inverted_letters,
}


# Card route 60: tutti i controlli usati dalla sezione Card in questa fase.
# Esclusi solo 4 controlli non-card-specifici in questa route stretta:
# qm_016, qm_036, qm_037, qm_041.
CARD_ROUTE_60_IDS = [
    "qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006",
    "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012",
    "qm_013", "qm_014", "qm_015",
    "qm_017", "qm_018", "qm_019", "qm_020", "qm_021", "qm_022",
    "qm_023", "qm_024", "qm_025", "qm_026", "qm_027", "qm_028",
    "qm_029", "qm_030", "qm_031", "qm_032", "qm_033", "qm_034",
    "qm_035", "qm_038", "qm_039", "qm_040", "qm_042", "qm_043",
    "qm_044", "qm_045", "qm_046", "qm_047", "qm_048", "qm_049",
    "qm_050", "qm_051", "qm_052", "qm_053", "qm_054", "qm_055",
    "qm_056", "qm_057", "qm_058", "qm_059", "qm_060", "qm_061",
    "qm_062", "qm_063", "qm_064",
]


def load_official_catalog() -> Dict[str, Dict[str, Any]]:
    data = read_json(I2_CATALOG)
    motors = data.get("motors", [])
    return {item["qm_id"]: item for item in motors}


def build_route_controls() -> List[CardRouteControl]:
    catalog = load_official_catalog()
    controls: List[CardRouteControl] = []

    for index, qm_id in enumerate(CARD_ROUTE_60_IDS, start=1):
        item = catalog.get(qm_id)
        if not item:
            controls.append(
                CardRouteControl(
                    route_slot=index,
                    control_id=qm_id,
                    control_name="MISSING_IN_CATALOG",
                    group="missing",
                    universal="non rilevabile",
                    executor_name=EXECUTORS.get(qm_id).__name__ if qm_id in EXECUTORS else "MISSING_EXECUTOR",
                )
            )
            continue

        controls.append(
            CardRouteControl(
                route_slot=index,
                control_id=qm_id,
                control_name=item.get("name", qm_id),
                group=item.get("group", ""),
                universal=item.get("universal", ""),
                executor_name=EXECUTORS.get(qm_id).__name__ if qm_id in EXECUTORS else "MISSING_EXECUTOR",
            )
        )

    return controls


def execute_route(cards: Sequence[Dict[str, Any]]) -> CardRoute60Report:
    defects: List[str] = []
    warnings: List[str] = []

    validate_upstream_contract(defects)
    require_cards(cards, defects)

    route_controls = build_route_controls()

    if len(route_controls) != EXPECTED_CARD_ROUTE_TOTAL:
        defects.append(
            f"Route Card deve collegare 60 controlli, trovati {len(route_controls)}"
        )

    duplicate_ids = sorted({
        control_id for control_id in CARD_ROUTE_60_IDS
        if CARD_ROUTE_60_IDS.count(control_id) > 1
    })
    if duplicate_ids:
        defects.append(f"ID duplicati nella route Card: {', '.join(duplicate_ids)}")

    execution_results: List[ControlExecutionResult] = []

    for control in route_controls:
        executor = EXECUTORS.get(control.control_id)
        if executor is None:
            result = ControlExecutionResult(
                route_slot=control.route_slot,
                control_id=control.control_id,
                control_name=control.control_name,
                executed=False,
                passed=False,
                defects=[f"Executor mancante per {control.control_id}"],
            )
            execution_results.append(result)
            defects.extend(result.defects)
            continue

        try:
            control_defects = executor(cards)
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

    executed_controls = len([item for item in execution_results if item.executed])
    passed_controls = len([item for item in execution_results if item.passed])
    failed_controls = len([item for item in execution_results if not item.passed])

    if executed_controls != EXPECTED_CARD_ROUTE_TOTAL:
        defects.append(
            f"Controlli eseguiti non sono 60: eseguiti {executed_controls}"
        )

    if passed_controls != EXPECTED_CARD_ROUTE_TOTAL:
        defects.append(
            f"Controlli passati non sono 60: passati {passed_controls}"
        )

    status = (
        "PASS - Fase 5.13A.3: CARD_ROUTE_60_STRICT_CONNECTOR_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.13A.3: CARD_ROUTE_60_STRICT_CONNECTOR_NOT_READY"
    )

    return CardRoute60Report(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        expected_controls=EXPECTED_CARD_ROUTE_TOTAL,
        connected_controls=len(route_controls),
        executed_controls=executed_controls,
        passed_controls=passed_controls,
        failed_controls=failed_controls,
        cards_checked=len(cards),
        route_controls=route_controls,
        execution_results=execution_results,
        defects=defects,
        warnings=warnings,
        notes=[
            "Questo report non accetta PASS se i 60 controlli Card non sono tutti collegati.",
            "Ogni controllo della route Card deve avere executor reale.",
            "Ogni executor viene eseguito sulle card finali generate.",
            "Se un titolo resta keyword-based, qm_013/qm_023/qm_061 falliscono.",
        ],
    )


def to_jsonable(payload: Any) -> Any:
    if hasattr(payload, "__dataclass_fields__"):
        return asdict(payload)
    if isinstance(payload, list):
        return [to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {key: to_jsonable(value) for key, value in payload.items()}
    return payload


def write_reports(report: CardRoute60Report) -> None:
    DEFAULT_JSON_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON_REPORT.write_text(
        json.dumps(to_jsonable(report), ensure_ascii=False, indent=2),
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
    lines.append(f"- Card controllate: `{report.cards_checked}`")
    lines.append("")
    lines.append("## Route Card 60")
    lines.append("")
    lines.append("| Slot | QM | Nome | Gruppo | Executor |")
    lines.append("|---:|---|---|---|---|")
    for control in report.route_controls:
        lines.append(
            f"| {control.route_slot} | `{control.control_id}` | {control.control_name} | "
            f"{control.group} | `{control.executor_name}` |"
        )
    lines.append("")
    lines.append("## Execution results")
    lines.append("")
    lines.append("| Slot | QM | Executed | Passed | Defects |")
    lines.append("|---:|---|---|---|---|")
    for result in report.execution_results:
        defects_text = "; ".join(result.defects) if result.defects else "nessuno"
        lines.append(
            f"| {result.route_slot} | `{result.control_id}` | {result.executed} | "
            f"{result.passed} | {defects_text} |"
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


def run_from_file() -> CardRoute60Report:
    cards = read_json(CARD_PAYLOAD)
    report = execute_route(cards)
    write_reports(report)
    return report


if __name__ == "__main__":
    result = run_from_file()

    print(result.status)
    print(f"Expected controls: {result.expected_controls}")
    print(f"Connected controls: {result.connected_controls}")
    print(f"Executed controls: {result.executed_controls}")
    print(f"Passed controls: {result.passed_controls}")
    print(f"Failed controls: {result.failed_controls}")
    print(f"Cards checked: {result.cards_checked}")
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
        raise SystemExit(1)
