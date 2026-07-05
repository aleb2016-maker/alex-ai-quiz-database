from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple


PHASE = "5.13A.4"
PHASE_LABEL = "FASE 5.13A.4 — UNIVERSAL CARD TITLE ENGINE"


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "dello", "della", "dei", "degli", "delle",
    "a", "ad", "al", "allo", "alla", "ai", "agli", "alle",
    "da", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
    "in", "nel", "nello", "nella", "nei", "negli", "nelle",
    "con", "su", "sul", "sullo", "sulla", "sui", "sugli", "sulle",
    "per", "tra", "fra", "e", "o", "ma", "che", "come", "quando",
    "questo", "questa", "questi", "queste", "quello", "quella",
    "sono", "viene", "vengono", "essere", "avere", "fare",
    "molto", "anche", "più", "può", "possono", "deve", "devono",
    "ogni", "parte", "modo", "punto", "contenuto", "principale",
}

RELATION_WORDS = {
    "di", "del", "della", "con", "per", "in", "nel", "nella",
    "tra", "verso", "attraverso", "mediante",
}

ACTION_VERBS = {
    "capire", "riconoscere", "applicare", "gestire", "proteggere",
    "migliorare", "ridurre", "evitare", "usare", "trasformare",
    "collegare", "organizzare", "chiarire", "presentare", "valutare",
    "controllare", "prevenire", "spiegare", "costruire", "rafforzare",
}

SEMANTIC_CUES = {
    "risk": {
        "rischio", "rischi", "minaccia", "minacce", "errore", "errori",
        "problema", "problemi", "sospetto", "sospetti", "pericolo",
        "pericoli", "vulnerabilità", "attacco", "attacchi",
    },
    "protection": {
        "protegge", "proteggono", "proteggere", "riduce", "riducono",
        "previene", "prevengono", "evita", "evitano", "sicurezza",
        "salvaguarda", "conserva", "difende",
    },
    "procedure": {
        "richiede", "richiedono", "prevede", "prevedono", "serve",
        "servono", "bisogna", "occorre", "procedura", "procedure",
        "regola", "regole", "controllo", "controlli",
    },
    "process": {
        "gestione", "processo", "processi", "flusso", "passaggio",
        "passaggi", "organizzazione", "coordinamento",
    },
    "transformation": {
        "trasforma", "trasformano", "diventa", "diventano", "porta",
        "portano", "aiuta", "aiutano", "migliora", "migliorano",
    },
    "definition": {
        "è", "sono", "indica", "indicano", "significa", "rappresenta",
        "rappresentano", "consiste", "consistono",
    },
    "benefit": {
        "permette", "permettono", "consente", "consentono", "favorisce",
        "favoriscono", "aiuta", "aiutano", "garantisce", "garantiscono",
    },
}


@dataclass
class TitleCandidate:
    title: str
    strategy: str
    score: int
    defects: List[str] = field(default_factory=list)


def normalize_text(text: str) -> str:
    cleaned = "" if text is None else str(text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def split_sentences(text: str) -> List[str]:
    pieces = re.split(r"(?<=[.!?])\s+", normalize_text(text))
    return [piece.strip() for piece in pieces if len(piece.strip()) >= 20]


def words(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", normalize_text(text).lower())


def content_words(text: str) -> List[str]:
    return [
        word for word in words(text)
        if word not in STOPWORDS and len(word) >= 4
    ]


def compact_phrase(text: str, max_words: int = 5) -> str:
    cleaned = normalize_text(text)
    cleaned = re.sub(r"^[,;:\-\s]+", "", cleaned)
    cleaned = re.sub(r"[,;:\-\s]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    tokens = cleaned.split()
    if len(tokens) > max_words:
        tokens = tokens[:max_words]

    phrase = " ".join(tokens).strip(" .!?;:,")
    return phrase.lower()


def sentence_case(text: str) -> str:
    cleaned = normalize_text(text).strip(" .!?;:,")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return cleaned
    return cleaned[0].upper() + cleaned[1:]


def strip_leading_article(phrase: str) -> str:
    cleaned = normalize_text(phrase).strip(" .!?;:,")
    cleaned = re.sub(
        r"^(il|lo|la|i|gli|le|un|uno|una|l')\s+",
        "",
        cleaned,
        flags=re.I,
    )
    return cleaned.strip()


def article_phrase(phrase: str) -> str:
    cleaned = strip_leading_article(phrase)
    if not cleaned:
        return cleaned

    first = cleaned.split()[0].lower()

    if first.startswith(("a", "e", "i", "o", "u")):
        return f"l’{cleaned}"

    if first.endswith(("zione", "sione", "tà", "trice")):
        return f"la {cleaned}"

    if first.endswith("a") and not first.endswith(("ma", "pa")):
        return f"la {cleaned}"

    if first.endswith("i"):
        return f"i {cleaned}"

    return f"il {cleaned}"


def preposition_a_phrase(phrase: str) -> str:
    cleaned = strip_leading_article(phrase)
    if not cleaned:
        return cleaned

    first = cleaned.split()[0].lower()

    if first.startswith(("a", "e", "i", "o", "u")):
        return f"all’{cleaned}"

    if first.endswith(("zione", "sione", "tà", "trice")):
        return f"alla {cleaned}"

    if first.endswith("a") and not first.endswith(("ma", "pa")):
        return f"alla {cleaned}"

    if first.endswith("i"):
        return f"ai {cleaned}"

    return f"al {cleaned}"




def detect_semantic_frame(chunk: str) -> str:
    lower_words = set(words(chunk))
    best_frame = "concept"
    best_score = 0

    for frame, cues in SEMANTIC_CUES.items():
        score = len(lower_words.intersection(cues))
        if score > best_score:
            best_frame = frame
            best_score = score

    return best_frame


def first_relevant_sentence(chunk: str) -> str:
    sentences = split_sentences(chunk)
    if not sentences:
        return normalize_text(chunk)

    # Prende la prima frase abbastanza informativa, non una frase microscopica.
    for sentence in sentences:
        if len(content_words(sentence)) >= 4:
            return sentence

    return sentences[0]


def extract_subject_before_verb(sentence: str) -> str:
    verbs = [
        " richiede ", " richiedono ", " resta ", " restano ",
        " protegge ", " proteggono ", " trasforma ", " trasformano ",
        " permette ", " permettono ", " consente ", " consentono ",
        " prevede ", " prevedono ", " riduce ", " riducono ",
        " aiuta ", " aiutano ", " è ", " sono ",
    ]

    lower = f" {sentence.lower()} "
    best_pos = None
    best_verb = ""

    for verb in verbs:
        pos = lower.find(verb)
        if pos != -1 and (best_pos is None or pos < best_pos):
            best_pos = pos
            best_verb = verb.strip()

    if best_pos is None:
        return ""

    subject = sentence[:best_pos].strip(" ,;:.")
    subject = re.sub(r"^(il|lo|la|i|gli|le|un|uno|una)\s+", "", subject, flags=re.I)
    return compact_phrase(subject, max_words=5)


def extract_object_after_verb(sentence: str, verbs: Iterable[str]) -> str:
    cleaned_sentence = normalize_text(sentence)

    for verb in verbs:
        pattern = r"\b" + re.escape(verb) + r"\b\s+(.+)"
        match = re.search(pattern, cleaned_sentence, flags=re.I)
        if not match:
            continue

        raw = match.group(1).strip(" ,;:.")
        raw = re.split(
            r"\bquando\b|\bperché\b|\bperche\b|\bse\b|\bche\b|[.;,]",
            raw,
            maxsplit=1,
            flags=re.I,
        )[0]

        return compact_phrase(raw, max_words=5)

    return ""

def extract_transform_pair(sentence: str) -> Tuple[str, str]:
    # Regola universale: X trasforma Y in Z.
    match = re.search(
        r"\btrasform\w*\s+(.+?)\s+in\s+(.+?)(?:[.;,]|$)",
        sentence,
        flags=re.I,
    )
    if not match:
        return "", ""

    source = compact_phrase(match.group(1), max_words=5)
    target = compact_phrase(match.group(2), max_words=5)
    return source, target


def extract_main_concept(chunk: str, fallback_keywords: Sequence[str] | None = None) -> str:
    sentence = first_relevant_sentence(chunk)

    subject = extract_subject_before_verb(sentence)
    if subject and len(content_words(subject)) >= 1:
        return subject

    candidates: Dict[str, int] = {}
    tokens = content_words(chunk)

    # Candidati bigram/trigram nell'ordine del testo, non keyword isolate.
    for n in (3, 2, 1):
        for i in range(0, max(len(tokens) - n + 1, 0)):
            phrase_words = tokens[i:i + n]
            if not phrase_words:
                continue
            phrase = " ".join(phrase_words)
            candidates[phrase] = candidates.get(phrase, 0) + n

    if candidates:
        return sorted(candidates.items(), key=lambda item: (-item[1], len(item[0])))[0][0]

    if fallback_keywords:
        usable = [kw for kw in fallback_keywords if kw and kw.lower() not in STOPWORDS]
        if usable:
            return " ".join(usable[:2]).lower()

    return "concetto principale"


def has_relation_or_action(title: str) -> bool:
    lowered_words = set(words(title))
    first = words(title)[:1]

    if lowered_words.intersection(RELATION_WORDS):
        return True

    if first and first[0] in ACTION_VERBS:
        return True

    if first and re.search(r"(are|ere|ire)$", first[0]):
        return True

    return False


def looks_like_keyword_pile(title: str) -> bool:
    title_words = content_words(title)

    if not title_words:
        return True

    lowered = normalize_text(title).lower()

    if lowered.startswith("concetto chiave"):
        return True

    if has_relation_or_action(title):
        return False

    # Regola generale: 3+ parole piene senza relazione = lista di keyword.
    if len(title_words) >= 3:
        return True

    # Due parole molto nominali senza verbo/connettivo sono deboli, ma non sempre bloccanti.
    if len(title_words) == 2 and len(" ".join(title_words)) > 22:
        return True

    return False


def title_has_content_overlap(title: str, chunk: str) -> bool:
    title_set = set(content_words(title))
    chunk_set = set(content_words(chunk))

    if not title_set:
        return False

    # Almeno un termine reale del titolo deve venire dal contenuto.
    return bool(title_set.intersection(chunk_set))


def validate_candidate(title: str, chunk: str) -> List[str]:
    defects: List[str] = []

    cleaned = normalize_text(title)

    if len(cleaned) < 8:
        defects.append("titolo troppo corto")

    if len(cleaned) > 90:
        defects.append("titolo troppo lungo")

    if looks_like_keyword_pile(cleaned):
        defects.append("titolo keyword-based")

    if not title_has_content_overlap(cleaned, chunk):
        defects.append("titolo non collegato al contenuto")

    if cleaned.endswith((" e", " di", " con", " per", " che", " del", " della")):
        defects.append("titolo con finale sospetto")

    return defects


def build_candidates(chunk: str, fallback_keywords: Sequence[str] | None = None) -> List[TitleCandidate]:
    sentence = first_relevant_sentence(chunk)
    frame = detect_semantic_frame(chunk)
    concept = extract_main_concept(chunk, fallback_keywords=fallback_keywords)
    candidates: List[TitleCandidate] = []

    transform_source, transform_target = extract_transform_pair(sentence)
    if transform_source and transform_target:
        title = sentence_case(f"trasformare {transform_source} in {transform_target}")
        candidates.append(TitleCandidate(title=title, strategy="transformation_relation", score=95))

    protected_object = extract_object_after_verb(
        sentence,
        verbs=["protegge", "proteggono", "difende", "difendono", "salvaguarda", "salvaguardano"],
    )
    if protected_object and concept:
        title = sentence_case(f"proteggere {protected_object} con {article_phrase(concept)}")
        candidates.append(TitleCandidate(title=title, strategy="protection_relation", score=92))

    required_object = extract_object_after_verb(
        sentence,
        verbs=["richiede", "richiedono", "prevede", "prevedono"],
    )
    if required_object and concept:
        title = sentence_case(f"gestire {article_phrase(concept)} con {required_object}")
        candidates.append(TitleCandidate(title=title, strategy="procedure_relation", score=88))

    if frame == "risk" and concept:
        title = sentence_case(f"riconoscere i rischi legati {preposition_a_phrase(concept)}")
        candidates.append(TitleCandidate(title=title, strategy="risk_relation", score=86))

    if frame == "procedure" and concept:
        title = sentence_case(f"applicare {article_phrase(concept)} in modo corretto")
        candidates.append(TitleCandidate(title=title, strategy="procedure_action", score=82))

    if frame == "process" and concept:
        title = sentence_case(f"organizzare {article_phrase(concept)} con un processo chiaro")
        candidates.append(TitleCandidate(title=title, strategy="process_action", score=80))

    if frame == "benefit" and concept:
        title = sentence_case(f"usare {article_phrase(concept)} per ottenere un risultato concreto")
        candidates.append(TitleCandidate(title=title, strategy="benefit_action", score=76))

    # Fallback universale, non specifico di dominio.
    if concept:
        candidates.append(
            TitleCandidate(
                title=sentence_case(f"capire il ruolo di {article_phrase(concept)}"),
                strategy="universal_role_fallback",
                score=65,
            )
        )

    return candidates


def repair_candidate(candidate: TitleCandidate, chunk: str) -> TitleCandidate:
    defects = validate_candidate(candidate.title, chunk)

    if not defects:
        candidate.defects = []
        return candidate

    concept = extract_main_concept(chunk)
    repaired_title = sentence_case(f"capire il ruolo di {article_phrase(concept)}")

    repaired = TitleCandidate(
        title=repaired_title,
        strategy=f"repair_from_{candidate.strategy}",
        score=max(candidate.score - 5, 50),
        defects=validate_candidate(repaired_title, chunk),
    )

    return repaired


def generate_universal_card_title(
    chunk: str,
    fallback_keywords: Sequence[str] | None = None,
    index: int = 1,
) -> str:
    candidates = build_candidates(chunk, fallback_keywords=fallback_keywords)
    repaired_candidates = [repair_candidate(candidate, chunk) for candidate in candidates]

    valid_candidates = [
        candidate for candidate in repaired_candidates
        if not candidate.defects
    ]

    if valid_candidates:
        best = sorted(valid_candidates, key=lambda item: -item.score)[0]
        return best.title

    # Ultima difesa: se anche il repair non passa, crea titolo esplicito e tracciabile.
    concept = extract_main_concept(chunk, fallback_keywords=fallback_keywords)
    emergency = sentence_case(f"capire il ruolo di {article_phrase(concept)}")

    if not validate_candidate(emergency, chunk):
        return emergency

    return f"Capire il contenuto principale della card {index}"
