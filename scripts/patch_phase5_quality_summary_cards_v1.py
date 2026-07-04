# scripts/patch_phase5_quality_summary_cards_v1.py
# =============================================================================
# PATCH FASE 5 — QUALITY SUMMARY + CONCEPT CARDS V1
#
# Modifica SOLO backend:
# - target: backend/motori_scrittura.py
# - aggiunge Fase 5 limitata a:
#   - Riassunto di Qualità
#   - Card Concettuali
#
# NON modifica:
# - Fase 1 MAP
# - Fase 2 REDUCE
# - Fase 3 OUTPUT BUILDER
# - Fase 4 SUPER QUALITY GATE
# - UI / CSS / pulsanti / layout
# =============================================================================

from __future__ import annotations

import shutil
import sys
from pathlib import Path


TARGET_FILE = Path("backend/motori_scrittura.py")
PATCH_MARKER = "FASE 5 — QUALITY SUMMARY CARDS V1"


PHASE5_CODE = r'''

# =============================================================================
# FASE 5 — QUALITY SUMMARY CARDS V1
#
# Pipeline definitiva:
# Estrai → Consolida → Crea bozze → Controlla → Genera qualità
#
# Questa fase prende l'output pulito della Fase 4:
# - SuperQualityGateResult.clean_output
#
# E produce:
# - riassunto narrativo fluido
# - card concettuali strutturate come oggetti JSON
#
# Divieti:
# - non tocca UI/CSS/pulsanti/layout
# - non modifica le Fasi 1–4
# - non inventa fatti esterni
# - non usa fallback/demo
# =============================================================================


@dataclass
class Phase5QualityConfig:
    """
    Configurazione universale Fase 5.

    Tutto è parametrico:
    nessun valore è legato a un documento specifico.
    """

    max_summary_points: int = 24
    facts_per_paragraph: int = 3
    max_cards: int = 12
    max_card_facts: int = 3
    max_micro_concepts_per_card: int = 6
    max_fact_chars: int = 700
    require_phase4_summary_cards_not_blocked: bool = True


@dataclass
class QualitySummaryFinal:
    """
    Riassunto finale di qualità.

    Non è una lista meccanica.
    È testo narrativo diviso in paragrafi.
    """

    titolo: str
    paragrafi: List[str] = field(default_factory=list)
    testo_completo: str = ""
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ConceptCardFinal:
    """
    Card concettuale finale come struttura dati.

    Non contiene UI.
    Non contiene CSS.
    Non contiene layout.
    """

    card_id: str
    titolo: str
    contenuto_esplicativo: str
    micro_concetti: List[str] = field(default_factory=list)
    colore_categoria: str = "#64748B"
    dominio_rilevato: str = "general"
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase5QualitySummaryCardsResult:
    """
    Output complessivo Fase 5 per riassunto + card.
    """

    document_id: str
    phase_name: str = "QUALITY_SUMMARY_CARDS"
    approved: bool = False
    status: str = "PENDING"

    riassunto_qualita: Optional[QualitySummaryFinal] = None
    card_concettuali: List[ConceptCardFinal] = field(default_factory=list)

    quality_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def q5_safe_text(value: Any) -> str:
    """
    Normalizzazione base protetta.
    """

    try:
        if "normalize_text" in globals():
            return normalize_text(value)
        return str(value or "").strip()
    except Exception:
        return ""


def q5_sentence(value: Any) -> str:
    """
    Restituisce una frase con punteggiatura finale.
    """

    try:
        text = q5_fix_italian_typography(q5_safe_text(value))
        text = text.strip()

        if not text:
            return ""

        if text[-1] not in ".!?":
            text += "."

        return text

    except Exception:
        return ""


def q5_limit_text(value: Any, max_chars: int = 700) -> str:
    """
    Limita testo troppo lungo senza spezzare l'intero sistema.
    """

    try:
        text = q5_safe_text(value)

        if max_chars <= 0 or len(text) <= max_chars:
            return text

        return text[:max_chars].rstrip() + "..."

    except Exception:
        return ""


def q5_unique_strings(values: Sequence[Any]) -> List[str]:
    """
    Deduplica prudente mantenendo ordine.
    """

    try:
        if "reduce_unique_strings" in globals():
            return reduce_unique_strings(values)

        output: List[str] = []
        seen = set()

        for value in values:
            text = q5_safe_text(value)
            key = text.lower()

            if text and key not in seen:
                seen.add(key)
                output.append(text)

        return output

    except Exception:
        return []


def q5_fix_italian_typography(text: Any) -> str:
    """
    Controllo tipografico rigido.

    Corregge:
    - doppi spazi
    - spazi prima della punteggiatura
    - apostrofi separati
    - e' / e'' → è
    - perche → perché
    - accenti comuni mancanti
    - sì affermativo in casi conservativi

    Nota:
    la correzione di "si" è volutamente prudente per non rompere
    il pronome impersonale "si" in frasi tipo "si deve fare".
    """

    try:
        value = q5_safe_text(text)

        if not value:
            return ""

        # Normalizza apostrofi strani.
        value = (
            value.replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
            .replace("´", "'")
        )

        # e' / e'' → è
        value = re.sub(
            r"(?<!\w)[eE]['\"]{1,2}(?!\w)",
            lambda m: "È" if m.group(0).startswith("E") else "è",
            value,
        )

        # Apostrofi italiani separati: l ' accesso → l'accesso
        value = re.sub(
            r"\b([lLdDaAuUnN])\s+'\s*",
            lambda m: m.group(1) + "'",
            value,
        )

        accent_map = {
            "perche": "perché",
            "perchè": "perché",
            "poiche": "poiché",
            "poichè": "poiché",
            "affinche": "affinché",
            "affinchè": "affinché",
            "benche": "benché",
            "benchè": "benché",
            "finche": "finché",
            "finchè": "finché",
            "cosi": "così",
            "piu": "più",
            "gia": "già",
            "puo": "può",
            "cio": "ciò",
            "pero": "però",
        }

        for wrong, right in accent_map.items():
            value = re.sub(
                rf"\b{wrong}\b",
                right,
                value,
                flags=re.IGNORECASE,
            )

        # Sì affermativo solo se seguito da punteggiatura o fine frase.
        value = re.sub(
            r"(?<!\w)([sS])i(?=\s*[,!.?;:]|\s*$)",
            lambda m: "Sì" if m.group(1).isupper() else "sì",
            value,
        )

        # Spazi prima della punteggiatura.
        value = re.sub(r"\s+([,.;:!?])", r"\1", value)

        # Spazio dopo punteggiatura, se manca.
        value = re.sub(r"([,.;:!?])(?=[^\s\]\)\}])", r"\1 ", value)

        # Doppi spazi.
        value = re.sub(r"\s+", " ", value).strip()

        return value

    except Exception:
        return q5_safe_text(text)


def q5_lower_first(text: str) -> str:
    """
    Abbassa solo la prima lettera per collegare frasi in modo narrativo.
    """

    try:
        clean = q5_safe_text(text)
        if not clean:
            return ""
        return clean[:1].lower() + clean[1:]
    except Exception:
        return q5_safe_text(text)


def q5_extract_pages_from_gate(gate_result: SuperQualityGateResult) -> List[int]:
    """
    Estrae pagine dal clean_output della Fase 4.
    """

    pages: List[int] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        def add_pages(raw_pages: Any) -> None:
            try:
                for page in raw_pages or []:
                    try:
                        pages.append(int(page))
                    except Exception:
                        pass
            except Exception:
                pass

        summary = clean.get("summary", {})
        if isinstance(summary, dict):
            add_pages(summary.get("source_pages", []))

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                add_pages(card.get("source_pages", []))

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    add_pages(section.get("source_pages", []))

        return sorted(set(pages))

    except Exception:
        return sorted(set(pages))


def q5_extract_facts_from_gate(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
) -> List[str]:
    """
    Estrae facts puliti dalla Fase 4.

    Priorità:
    1. gate_result.clean_output
    2. fallback controllato su OutputBuilderResult
    """

    facts: List[str] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        summary = clean.get("summary", {})
        if isinstance(summary, dict):
            facts.extend(summary.get("key_points", []) or [])

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                facts.extend(card.get("source_facts", []) or [])
                message = card.get("message_key")
                if message:
                    facts.append(message)

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    facts.extend(section.get("key_facts", []) or [])

        if not facts and output_result is not None:
            try:
                facts.extend(qg_collect_source_facts(output_result))
            except Exception:
                pass

        cleaned = [
            q5_limit_text(q5_fix_italian_typography(fact), 900)
            for fact in facts
            if q5_safe_text(fact)
        ]

        return q5_unique_strings(cleaned)

    except Exception:
        return q5_unique_strings(facts)


def q5_extract_concepts_from_gate(gate_result: SuperQualityGateResult) -> List[str]:
    """
    Estrae micro-concetti già presenti nel clean_output.
    """

    concepts: List[str] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                concepts.extend(card.get("micro_concepts", []) or [])

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            concepts.extend(pack.get("global_micro_concepts", []) or [])
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    concepts.extend(section.get("micro_concepts", []) or [])

        return q5_unique_strings(
            [
                q5_fix_italian_typography(concept).lower()
                for concept in concepts
                if q5_safe_text(concept)
            ]
        )

    except Exception:
        return q5_unique_strings(concepts)


def q5_stopwords() -> set:
    """
    Stopword minime per estrazione micro-concetti.
    """

    return {
        "il", "lo", "la", "i", "gli", "le",
        "un", "uno", "una",
        "di", "del", "della", "delle", "degli", "dei",
        "a", "ad", "al", "alla", "alle", "agli", "ai",
        "da", "dal", "dalla", "dalle", "dai",
        "in", "nel", "nella", "nelle", "nei", "negli",
        "con", "su", "per", "tra", "fra",
        "e", "o", "ma", "che",
        "deve", "devono", "essere", "viene", "sono",
        "questo", "questa", "questi", "quelle", "quello",
    }


def q5_word_tokens(text: str) -> List[str]:
    """
    Token parole italiane.
    """

    try:
        return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", q5_safe_text(text).lower())
    except Exception:
        return []


def q5_is_valid_micro_concept(concept: str) -> bool:
    """
    Verifica keyword vera di 2-3 parole.
    """

    try:
        clean = q5_safe_text(concept).lower()
        words = clean.split()

        if len(words) < 2 or len(words) > 3:
            return False

        stops = q5_stopwords()

        if words[0] in stops or words[-1] in stops:
            return False

        if all(word in stops for word in words):
            return False

        if len(clean) < 5:
            return False

        return True

    except Exception:
        return False


def q5_generate_micro_concepts_from_text(text: str, limit: int = 6) -> List[str]:
    """
    Genera micro-concetti 2-3 parole dal testo se quelli della MAP non bastano.
    """

    concepts: List[str] = []

    try:
        tokens = q5_word_tokens(text)
        stops = q5_stopwords()

        candidates: List[str] = []

        for size in (2, 3):
            for index in range(0, max(0, len(tokens) - size + 1)):
                gram = tokens[index:index + size]

                if not gram:
                    continue

                if gram[0] in stops or gram[-1] in stops:
                    continue

                if all(token in stops for token in gram):
                    continue

                candidate = " ".join(gram)
                if q5_is_valid_micro_concept(candidate):
                    candidates.append(candidate)

        concepts = q5_unique_strings(candidates)

        return concepts[:limit]

    except Exception:
        return concepts[:limit]


def q5_select_micro_concepts(
    preferred_concepts: List[str],
    text: str,
    limit: int = 6,
) -> List[str]:
    """
    Seleziona micro-concetti veri di 2-3 parole.
    """

    try:
        valid = [
            q5_safe_text(concept).lower()
            for concept in preferred_concepts
            if q5_is_valid_micro_concept(q5_safe_text(concept))
        ]

        if len(valid) < limit:
            valid.extend(q5_generate_micro_concepts_from_text(text, limit=limit))

        return q5_unique_strings(valid)[:limit]

    except Exception:
        return []


def q5_detect_domain_from_text(text: str, concepts: Optional[List[str]] = None) -> str:
    """
    Rileva dominio base per colore categoria.

    È un classificatore leggero, non un motore semantico pesante.
    """

    try:
        joined = " ".join([q5_safe_text(text)] + list(concepts or [])).lower()

        domain_keywords = {
            "cybersecurity": [
                "accessi", "credenziali", "account", "permessi",
                "sistemi interni", "utenti autorizzati", "sicurezza",
                "rischio", "controllo",
            ],
            "business": [
                "azienda", "processo", "cliente", "mercato",
                "strategia", "vendite", "operativo",
            ],
            "legal": [
                "contratto", "normativa", "obbligo", "diritto",
                "responsabilità", "clausola",
            ],
            "education": [
                "studio", "formazione", "apprendimento", "lezione",
                "competenza", "esame",
            ],
            "health": [
                "salute", "paziente", "clinico", "medico",
                "diagnosi", "terapia",
            ],
            "sport": [
                "allenamento", "forza", "resistenza", "gara",
                "atleta", "recupero",
            ],
        }

        scores: Dict[str, int] = {}

        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for keyword in keywords if keyword in joined)

        best_domain = max(scores, key=scores.get)

        if scores.get(best_domain, 0) <= 0:
            return "general"

        return best_domain

    except Exception:
        return "general"


def q5_color_for_domain(domain: str) -> str:
    """
    Colore categoria associato dinamicamente al dominio rilevato.

    È solo dato.
    Non applica grafica.
    Non tocca CSS.
    """

    try:
        palette = {
            "cybersecurity": "#7C3AED",
            "business": "#0F766E",
            "legal": "#B45309",
            "education": "#0891B2",
            "health": "#16A34A",
            "sport": "#EA580C",
            "creative": "#DB2777",
            "technical": "#2563EB",
            "general": "#64748B",
        }

        return palette.get(q5_safe_text(domain).lower(), palette["general"])

    except Exception:
        return "#64748B"


def q5_title_from_text(text: str, fallback: str = "Punto chiave", max_words: int = 7) -> str:
    """
    Titolo breve da testo/concept.
    """

    try:
        clean = q5_fix_italian_typography(text).strip().rstrip(".")
        words = clean.split()

        if not words:
            return fallback

        title = " ".join(words[:max_words])

        if len(words) > max_words:
            title += "..."

        return title[:1].upper() + title[1:]

    except Exception:
        return fallback


def q5_intro_for_fact(fact: str) -> str:
    """
    Introduzione narrativa in base al tipo di fatto.
    """

    try:
        lowered = fact.lower()

        if "non devono" in lowered or "non deve" in lowered or "vietato" in lowered:
            return "Il documento chiarisce un divieto operativo importante:"

        if "riduce il rischio" in lowered or "previene" in lowered:
            return "Un punto rilevante riguarda la riduzione del rischio:"

        if "deve" in lowered or "devono" in lowered or "obbligo" in lowered:
            return "Il testo definisce anche un obbligo operativo:"

        if "controllo" in lowered or "limita" in lowered:
            return "Il documento descrive una funzione di controllo:"

        return "Un altro punto da considerare è questo:"

    except Exception:
        return "Un punto importante è questo:"


def q5_build_fluid_summary_paragraphs(
    facts: List[str],
    config: Phase5QualityConfig,
) -> List[str]:
    """
    Motore di Scrittura Fluida per il riassunto.

    Trasforma punti separati in paragrafi narrativi coerenti.
    Non usa lista meccanica.
    """

    paragraphs: List[str] = []

    try:
        clean_facts = [
            q5_sentence(q5_limit_text(fact, config.max_fact_chars))
            for fact in facts[: max(0, config.max_summary_points)]
            if q5_safe_text(fact)
        ]

        if not clean_facts:
            return paragraphs

        group_size = max(1, int(config.facts_per_paragraph or 1))

        openings = [
            "Il documento evidenzia che",
            "Sul piano operativo emerge che",
            "In continuità con questi elementi, si osserva che",
            "Nel quadro complessivo, risulta importante che",
        ]

        connectors = [
            "Inoltre,",
            "Allo stesso tempo,",
            "Di conseguenza,",
            "Un altro aspetto collegato è che",
        ]

        for group_index in range(0, len(clean_facts), group_size):
            group = clean_facts[group_index:group_index + group_size]
            paragraph_index = len(paragraphs)
            opening = openings[paragraph_index % len(openings)]

            first = q5_lower_first(group[0]).rstrip(".")
            paragraph = f"{opening} {first}."

            for local_index, sentence in enumerate(group[1:], start=1):
                connector = connectors[(local_index - 1) % len(connectors)]
                paragraph += f" {connector} {q5_lower_first(sentence).rstrip('.')}."

            paragraph = q5_fix_italian_typography(paragraph)
            paragraphs.append(paragraph)

        return paragraphs

    except Exception:
        return paragraphs


def q5_build_quality_summary(
    facts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> QualitySummaryFinal:
    """
    Costruisce il riassunto di qualità.
    """

    summary = QualitySummaryFinal(
        titolo="Riassunto di qualità",
        fonte_pagine=list(pages),
    )

    try:
        paragraphs = q5_build_fluid_summary_paragraphs(facts, config)

        summary.paragrafi = paragraphs
        summary.testo_completo = "\n\n".join(paragraphs)

        if not summary.paragrafi:
            summary.warnings.append("PHASE5_SUMMARY_NO_PARAGRAPHS")

        mechanical_markers = [
            "quale affermazione è supportata dal documento",
            "quale regola o informazione emerge da",
        ]

        lowered = summary.testo_completo.lower()
        for marker in mechanical_markers:
            if marker in lowered:
                summary.warnings.append(f"PHASE5_SUMMARY_MECHANICAL_MARKER: {marker}")

        return summary

    except Exception as exc:
        summary.warnings.append(f"PHASE5_SUMMARY_EXCEPTION: {type(exc).__name__}: {exc}")
        return summary


def q5_build_card_content(facts: List[str]) -> str:
    """
    Crea contenuto esplicativo fluido per una card.

    Non è testo compresso.
    Non è lista.
    """

    try:
        clean_facts = [q5_sentence(fact) for fact in facts if q5_safe_text(fact)]

        if not clean_facts:
            return ""

        first_fact = clean_facts[0]
        intro = q5_intro_for_fact(first_fact)

        body = f"{intro} {q5_lower_first(first_fact)}"

        for fact in clean_facts[1:]:
            body += f" Questo elemento si collega anche al fatto che {q5_lower_first(fact).rstrip('.')}."

        return q5_fix_italian_typography(body)

    except Exception:
        return ""


def q5_build_concept_cards(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> List[ConceptCardFinal]:
    """
    Costruisce card concettuali come oggetti dati JSON-ready.
    """

    cards: List[ConceptCardFinal] = []

    try:
        if not facts:
            return cards

        max_cards = max(0, config.max_cards)
        max_card_facts = max(1, config.max_card_facts)

        for index in range(0, min(len(facts), max_cards)):
            fact = facts[index]
            related_facts = facts[index:index + max_card_facts]

            text_for_domain = " ".join(related_facts)
            micro_concepts = q5_select_micro_concepts(
                preferred_concepts=preferred_concepts,
                text=text_for_domain,
                limit=config.max_micro_concepts_per_card,
            )

            domain = q5_detect_domain_from_text(text_for_domain, micro_concepts)
            color = q5_color_for_domain(domain)

            title_source = micro_concepts[0] if micro_concepts else fact
            title = q5_title_from_text(title_source, fallback=f"Card concettuale {index + 1}", max_words=5)

            content = q5_build_card_content(related_facts)

            card = ConceptCardFinal(
                card_id=f"phase5_card_{index + 1:03d}",
                titolo=title,
                contenuto_esplicativo=content,
                micro_concetti=micro_concepts,
                colore_categoria=color,
                dominio_rilevato=domain,
                fonte_pagine=list(pages),
            )

            if not card.contenuto_esplicativo:
                card.warnings.append("PHASE5_CARD_EMPTY_CONTENT")

            if not card.micro_concetti:
                card.warnings.append("PHASE5_CARD_NO_MICRO_CONCEPTS")

            invalid_concepts = [
                concept for concept in card.micro_concetti
                if not q5_is_valid_micro_concept(concept)
            ]

            if invalid_concepts:
                card.warnings.append(
                    "PHASE5_CARD_INVALID_MICRO_CONCEPTS: " + ", ".join(invalid_concepts)
                )

            cards.append(card)

        return cards

    except Exception:
        return cards


def q5_validate_phase4_for_summary_cards(
    gate_result: SuperQualityGateResult,
    config: Phase5QualityConfig,
) -> List[str]:
    """
    Verifica che la Fase 4 non abbia bloccato summary/cards.

    Se la Fase 4 è bloccata solo per quiz, questa Fase 5 può comunque
    generare riassunto e card.
    """

    errors: List[str] = []

    try:
        blocked_areas = list(getattr(gate_result, "blocked_areas", []) or [])

        if config.require_phase4_summary_cards_not_blocked:
            if "summary" in blocked_areas:
                errors.append("PHASE5_CANNOT_BUILD_SUMMARY_PHASE4_BLOCKED_SUMMARY")
            if "cards" in blocked_areas:
                errors.append("PHASE5_CANNOT_BUILD_CARDS_PHASE4_BLOCKED_CARDS")

        return errors

    except Exception as exc:
        return [f"PHASE5_PHASE4_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q5_find_forbidden_in_final_text(text: str) -> List[str]:
    """
    Controlla firme fallback/demo nel testo finale.
    """

    found: List[str] = []

    try:
        if "find_forbidden_signatures" in globals():
            found.extend(find_forbidden_signatures(text))

        extra = [
            "contenuto demo",
            "documento di esempio",
            "testo di esempio",
            "fallback",
            "lorem ipsum",
            "knowledge_base_json",
            "sicurezza informatica aziendale",
        ]

        lowered = q5_safe_text(text).lower()

        for item in extra:
            if item in lowered:
                found.append(item)

        return q5_unique_strings(found)

    except Exception:
        return found


def build_phase5_quality_summary_cards(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
    config: Optional[Phase5QualityConfig] = None,
) -> Phase5QualitySummaryCardsResult:
    """
    Funzione madre Fase 5.

    Collegamento alla Fase 4:
    - legge SuperQualityGateResult.clean_output
    - usa summary/cards/study_pack puliti dalla Fase 4
    - se la Fase 4 ha bloccato summary/cards, non approva
    - se la Fase 4 ha bloccato solo quiz, può produrre summary/cards

    Output:
    - QualitySummaryFinal
    - List[ConceptCardFinal]
    """

    cfg = config or Phase5QualityConfig()

    result = Phase5QualitySummaryCardsResult(
        document_id=q5_safe_text(getattr(gate_result, "document_id", "")) or "unknown_document",
    )

    try:
        result.errors.extend(q5_validate_phase4_for_summary_cards(gate_result, cfg))

        facts = q5_extract_facts_from_gate(gate_result, output_result)
        concepts = q5_extract_concepts_from_gate(gate_result)
        pages = q5_extract_pages_from_gate(gate_result)

        if not facts:
            result.errors.append("PHASE5_NO_FACTS_AVAILABLE_FROM_PHASE4")

        result.riassunto_qualita = q5_build_quality_summary(facts, pages, cfg)
        result.card_concettuali = q5_build_concept_cards(facts, concepts, pages, cfg)

        final_text_parts: List[str] = []

        if result.riassunto_qualita:
            final_text_parts.append(result.riassunto_qualita.testo_completo)

        for card in result.card_concettuali:
            final_text_parts.append(card.titolo)
            final_text_parts.append(card.contenuto_esplicativo)
            final_text_parts.extend(card.micro_concetti)

        forbidden = q5_find_forbidden_in_final_text("\n".join(final_text_parts))

        if forbidden:
            result.errors.append(
                "PHASE5_FORBIDDEN_SIGNATURES_FOUND: " + ", ".join(forbidden)
            )

        if not result.riassunto_qualita or not result.riassunto_qualita.paragrafi:
            result.errors.append("PHASE5_SUMMARY_EMPTY")

        if not result.card_concettuali:
            result.errors.append("PHASE5_CARDS_EMPTY")

        for card in result.card_concettuali:
            if not card.titolo:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_TITLE_EMPTY")
            if not card.contenuto_esplicativo:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_CONTENT_EMPTY")
            if not card.micro_concetti:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_MICRO_CONCEPTS_EMPTY")
            if not card.colore_categoria.startswith("#"):
                result.errors.append(f"{card.card_id}: PHASE5_CARD_COLOR_INVALID")

        result.quality_report = {
            "facts_used": len(facts),
            "concepts_used": len(concepts),
            "summary_paragraphs": len(result.riassunto_qualita.paragrafi) if result.riassunto_qualita else 0,
            "cards_count": len(result.card_concettuali),
            "source_pages": pages,
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
        }

        if result.errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"PHASE5_QUALITY_SUMMARY_CARDS_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def phase5_quality_summary_cards_result_to_dict(
    result: Phase5QualitySummaryCardsResult,
) -> Dict[str, Any]:
    """
    Serializza Fase 5 in dict JSON-ready.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "QUALITY_SUMMARY_CARDS",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["PHASE5_SERIALIZATION_FAILED"],
        }


def phase5_quality_summary_cards_result_to_json(
    result: Phase5QualitySummaryCardsResult,
    indent: int = 2,
) -> str:
    """
    Serializza Fase 5 in JSON.
    """

    try:
        return json.dumps(
            phase5_quality_summary_cards_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "QUALITY_SUMMARY_CARDS",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [f"PHASE5_JSON_FAILED: {type(exc).__name__}: {exc}"],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 5 — Quality Summary Cards V1
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if PATCH_MARKER in original:
            print("✅ FASE 5 QUALITY SUMMARY CARDS V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_phase5_quality_summary_cards_v1")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + PHASE5_CODE + "\n"

        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch FASE 5 QUALITY SUMMARY CARDS V1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch FASE 5 QUALITY SUMMARY CARDS V1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())