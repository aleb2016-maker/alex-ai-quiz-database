#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.3 - Universal long-doc card real quality.

Modulo deterministico per migliorare SOLO le card dei documenti lunghi.
Usa global_map/block_digests/fatti/sezioni/frasi fonte e produce card
tracciabili, specifiche e didattiche senza toccare summary, quiz, study o QM.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Sequence, Tuple

PHASE = "5.15G.3"

GENERIC_TITLES = {
    "apertura del documento",
    "aspetto operativo del documento",
    "aspetto importante del documento",
    "concetto",
    "concetto operativo",
    "controllo",
    "contenuto principale",
    "documento",
    "documento operativo",
    "procedura",
    "processo",
    "sezione",
    "tema generale",
    "tema principale",
    "punto chiave",
    "elemento rilevante",
    "informazione utile",
    "manuale aziendale completo rag v1",
    "sezione del documento",
    "riferimento sezione",
    "documento analizzato",
}

BAD_NOISE = [
    "non contiene dati reali",
    "collegato alla demo",
    "demo",
    "fallback",
    "script",
    "test tecnico",
    "documento fixture",
    "fixture tecnica",
    "risposta corretta",
    "opzione corretta",
    "distrattore",
    "quiz_payload",
    "keyword:",
]

TEMPLATE_PHRASES = [
    "il documento evidenzia aspetti importanti",
    "la sezione descrive elementi rilevanti",
    "questo concetto è utile per comprendere il testo",
    "questo concetto e' utile per comprendere il testo",
    "il contenuto mostra diverse informazioni",
    "la card evidenzia",
    "nel contesto",
    "la sezione",
    "questo passaggio",
]

TECHNICAL_TITLE_RE = re.compile(r"\b(?:MAN-[A-Z]+-\d+|REF\b|CTRL[-_ ]?\d+|fixture|riferimento sezione|macro-area)\b", re.I)
CONTROL_RE = re.compile(r"\bCTRL[-_\s]?[A-Z0-9]{2,}(?:[-_][A-Z0-9]{1,})?\b", re.I)

STOPWORDS = {
    "alla", "alle", "allo", "agli", "della", "delle", "degli", "dello",
    "nella", "nelle", "negli", "nello", "questa", "questo", "questi", "queste",
    "quella", "quello", "sono", "viene", "vengono", "deve", "devono",
    "essere", "avere", "come", "quando", "dopo", "prima", "ogni", "anche",
    "dove", "quale", "quali", "documento", "sezione", "passaggio", "aspetto",
    "contesto", "descrive", "procedura", "per", "con", "tra", "fra", "una",
    "uno", "gli", "dei", "del", "che", "nel", "nei", "sul", "sui", "dal",
    "dai", "sua", "suo", "sue", "il", "lo", "la", "le", "e", "o", "a",
    "di", "da", "in", "su", "al", "ai", "ad", "ed",
}

PROFILE_CARD_DATA: Dict[str, Dict[str, Any]] = {
    "manuale_aziendale": {
        "card_style": "Card operativa con processo, controllo, responsabilita, rischio e applicazione concreta.",
        "preferred_card_types": ["process", "control", "responsibility", "risk", "procedure", "example"],
        "expected_learning_value": "Capire cosa fare, chi deve farlo, quale controllo lo prova e quale rischio evita.",
    },
    "dispensa_scolastica_universitaria": {
        "card_style": "Card didattica con concetto, definizione, esempio, confronto ed errore comune.",
        "preferred_card_types": ["definition", "concept", "example", "comparison", "common_error"],
        "expected_learning_value": "Studiare concetti e collegamenti con spiegazione chiara ed esempio.",
    },
    "documento_tecnico": {
        "card_style": "Card tecnica con componente, configurazione, procedura, errore e architettura.",
        "preferred_card_types": ["component", "configuration", "procedure", "error", "architecture"],
        "expected_learning_value": "Capire componenti, flussi, condizioni operative e rischi tecnici.",
    },
    "documento_legale_amministrativo": {
        "card_style": "Card normativa con obbligo, soggetto, scadenza, vincolo e conseguenza.",
        "preferred_card_types": ["obligation", "subject", "deadline", "constraint", "consequence"],
        "expected_learning_value": "Distinguere soggetti, obblighi, vincoli e conseguenze operative.",
    },
    "cv_profilo_professionale": {
        "card_style": "Card professionale con competenza, esperienza, risultato, obiettivo e valore.",
        "preferred_card_types": ["skill", "experience", "result", "objective", "professional_value"],
        "expected_learning_value": "Ricostruire competenze, risultati e coerenza del profilo.",
    },
    "storia_racconto": {
        "card_style": "Card narrativa con evento, personaggio, conflitto, svolta e tema.",
        "preferred_card_types": ["event", "character", "conflict", "turning_point", "theme"],
        "expected_learning_value": "Seguire arco narrativo, personaggi, conflitti e trasformazioni.",
    },
    "poesia_testo_letterario": {
        "card_style": "Card critica con immagine, tema, figura retorica, tono e interpretazione.",
        "preferred_card_types": ["image", "theme", "figure", "tone", "interpretation"],
        "expected_learning_value": "Leggere immagini, simboli, tono e interpretazione del testo.",
    },
    "sport_allenamento": {
        "card_style": "Card pratica con esercizio, tecnica, progressione, recupero e obiettivo.",
        "preferred_card_types": ["exercise", "technique", "progression", "recovery", "goal"],
        "expected_learning_value": "Applicare tecnica, progressione e recupero in modo consapevole.",
    },
    "appunti_misti": {
        "card_style": "Card di studio con concetto centrale, priorita, collegamento e domanda aperta.",
        "preferred_card_types": ["concept", "priority", "connection", "open_question", "example"],
        "expected_learning_value": "Ordinare priorita, collegamenti e domande utili al ripasso.",
    },
}


def _clean_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", str(text or "").replace("\r", "\n")).strip()


def _word_tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def _word_count(text: str) -> int:
    return len(_word_tokens(text))


def _finish_sentence(text: str) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip(" -•\t"))
    if clean and clean[-1] not in ".!?":
        clean += "."
    return clean


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", _clean_spaces(text))
    return [_finish_sentence(part) for part in parts if _word_count(part) >= 6]


def _dedupe_plain(items: Iterable[str], limit: int | None = None) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        clean = re.sub(r"\s+", " ", str(item or "").strip(" .,:;"))
        if not clean:
            continue
        key = re.sub(r"[^a-z0-9àèéìòù]+", " ", clean.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def _keywords(text: str, limit: int = 10) -> List[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", str(text or ""))]
    counts = Counter(w for w in words if w not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def _normal_key(text: str) -> str:
    words = [w for w in re.findall(r"[a-zàèéìòù0-9]{4,}", str(text or "").lower()) if w not in STOPWORDS]
    return " ".join(words[:12])


def _has_noise(text: str) -> bool:
    low = str(text or "").lower()
    return any(item in low for item in BAD_NOISE)


def _remove_template_noise(text: str) -> str:
    clean = _finish_sentence(text)
    if _has_noise(clean):
        return ""
    clean = re.sub(r"\bNel contesto\s+[^,]{1,100},\s+la sezione\s+[^,]{1,100}\s+descrive\s+", "", clean, flags=re.I)
    clean = re.sub(r"\bLa sezione\s+[^,]{1,100}\s+descrive\s+", "", clean, flags=re.I)
    clean = re.sub(r"\bLa procedura richiede(?: che)?\s+", "Occorre ", clean, flags=re.I)
    clean = re.sub(r"\bOgni attivit[aà] deve\s+", "Le attivita prevedono di ", clean, flags=re.I)
    clean = re.sub(r"\bQuesto passaggio\b", "Questa parte", clean, flags=re.I)
    clean = re.sub(r"\bIl controllo\s+(CTRL[-_\s]?[A-Z0-9_-]+)\s+evita passaggi informali\b", r"\1 rende verificabile il flusso", clean, flags=re.I)
    clean = re.sub(r"\bRiferimento sezione:\s*MAN-[A-Z]+-[0-9.]+\b", "", clean, flags=re.I)
    clean = re.sub(r"\s+", " ", clean).strip(" ;,.-")
    return _finish_sentence(clean) if clean else ""


def _clean_title(title: str, fallback_terms: Sequence[str] = ()) -> str:
    raw = re.sub(r"\s+", " ", str(title or "").strip(" .:-"))
    raw = re.sub(r"^keyword\s*:\s*", "", raw, flags=re.I)
    raw = re.sub(r"^\d{1,4}(?:\.\d{1,3})*\s*[-.)]?\s*", "", raw)
    low = raw.lower()
    if low.startswith("riferimento sezione") or "rag v" in low or TECHNICAL_TITLE_RE.search(raw):
        raw = ""
    if not raw or raw.lower() in GENERIC_TITLES:
        raw = " ".join(str(term).strip().capitalize() for term in fallback_terms[:3] if str(term).strip())
    raw = re.sub(r"\b(ctrl|man)[-_ ][a-z0-9.-]+\b", "", raw, flags=re.I)
    raw = re.sub(r"\s+", " ", raw).strip(" .:-")
    if not raw:
        raw = "Concetto operativo"
    return raw[:1].upper() + raw[1:84]


def _title_terms_from_material(sentence: str, digest: Dict[str, Any], limit: int = 4) -> List[str]:
    candidates: List[str] = []
    candidates.extend(digest.get("main_topics") or [])
    candidates.extend(digest.get("good_keywords") or [])
    candidates.extend(_keywords(sentence, 10))
    out: List[str] = []
    weak_terms = {
        "controllo", "passaggi", "workflow", "ruoli", "evidenze", "verifica",
        "traccia", "scritta", "registro", "operativo", "responsabile", "processo",
        "keyword", "corretta", "risposta", "risultato", "finale", "success",
    }
    for term in candidates:
        clean = re.sub(r"\b(?:ctrl|man)[-_ ][a-z0-9.-]+\b", "", str(term), flags=re.I)
        clean = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9 ]+", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip().lower()
        if not clean or clean in STOPWORDS or clean in GENERIC_TITLES or clean in weak_terms:
            continue
        out.append(clean)
    return _dedupe_plain(out, limit)


def _scenario_title(sentence: str, digest: Dict[str, Any]) -> str:
    topic_terms = _title_terms_from_material(sentence, digest, 3)
    topic = " ".join(topic_terms[:2]).strip()
    patterns = [
        (r"\bgestire\s+([^,.]{4,70}?)\s+quando\s+([^,.]{8,90})", "{a}: {b}"),
        (r"\briferimento principale\s+(?:e|è)\s+([^,.]{4,70})", "Riferimento {a}"),
        (r"\bverifica\s+(giornaliera|settimanale|mensile|trimestrale)\b", "Verifica {a}"),
        (r"\bchi ha autorizzato l'azione\b", "Autorizzazioni e sistemi coinvolti"),
        (r"\bevidenze sufficienti\b", "Evidenze e nota di miglioramento"),
        (r"\brischi residui\b", "Rischi residui ed evidenze"),
    ]
    for pattern, template in patterns:
        match = re.search(pattern, sentence, flags=re.I)
        if not match:
            continue
        groups = match.groups()
        first = groups[0].strip() if groups else ""
        second = groups[1].strip() if len(groups) > 1 else ""
        title = template.format(a=first, b=second)
        if topic and topic not in title.lower():
            title = f"{topic}: {title}"
        return _clean_title(title, topic_terms)
    if topic:
        return _clean_title(topic, topic_terms)
    return _clean_title("", _keywords(sentence, 6))


def _public_safe_title(title: str, terms: Sequence[str] = ()) -> str:
    clean = _clean_title(title, terms)
    low = clean.lower()
    if low in GENERIC_TITLES or _normal_key(clean) in {"aspetto operativo documento", "concetto operativo"}:
        clean = _clean_title("", terms)
    words = _word_tokens(clean)
    if len(words) <= 4:
        qualifier = ""
        for term in terms:
            term_clean = re.sub(r"\b(?:ctrl|man)[-_ ][a-z0-9.-]+\b", "", str(term), flags=re.I)
            term_clean = re.sub(r"\s+", " ", term_clean).strip(" .,:;-")
            if _word_count(term_clean) >= 2 and term_clean.lower() not in clean.lower():
                qualifier = term_clean
                break
        if qualifier:
            clean = f"{clean} nel contesto {qualifier}"
        else:
            clean = f"{clean} nel flusso operativo"
    return clean[:1].upper() + clean[1:96]


def _title_similarity_key(title: str) -> str:
    weak = {"controllo", "procedura", "processo", "flusso", "contesto", "operativo", "operativa"}
    words = []
    for word in re.findall(r"[a-zàèéìòù0-9]{4,}", str(title or "").lower()):
        if word in STOPWORDS or word in weak or word.startswith("operativ"):
            continue
        words.append(word)
    return " ".join(sorted(words[:6]))


def _concept_type_from_text(text: str, profile: str) -> str:
    low = str(text or "").lower()
    if any(marker in low for marker in ["risch", "errore", "anomalia", "incidente", "critic"]):
        return "risk"
    if CONTROL_RE.search(text) or "controll" in low:
        return "control"
    if any(marker in low for marker in ["procedura", "processo", "flusso", "fase", "passo"]):
        return "procedure"
    if any(marker in low for marker in ["responsabile", "owner", "team", "ruolo", "ufficio"]):
        return "responsibility"
    if any(marker in low for marker in ["definisce", "significa", "si intende", "definizione"]):
        return "definition"
    if any(marker in low for marker in ["esempio", "caso", "applicazione", "rileva"]):
        return "example"
    preferred = PROFILE_CARD_DATA.get(profile, PROFILE_CARD_DATA["appunti_misti"])["preferred_card_types"]
    return str(preferred[0])


def _extract_title_from_sentence(sentence: str, digest: Dict[str, Any], profile: str) -> str:
    clean = _remove_template_noise(sentence)
    patterns = [
        r"\bgestire\s+([^,.]{4,90}?)\s+quando\b",
        r"\bgovernare\s+([^,.]{4,90}?)\s+con\b",
        r"\bcollegata? a\s+([^,.]{4,80})",
        r"\bsu\s+([^,.]{4,80})",
    ]
    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.I)
        if match:
            return _clean_title(match.group(1), digest.get("main_topics", []))
    topics = digest.get("main_topics") or digest.get("good_keywords") or _keywords(clean, 5)
    scenario = _scenario_title(clean, digest)
    if scenario.lower() not in GENERIC_TITLES and _normal_key(scenario) not in {"aspetto operativo documento", "concetto operativo"}:
        return scenario
    title = _clean_title(digest.get("title", ""), topics)
    if title.lower() in GENERIC_TITLES or _normal_key(title) in {"aspetto operativo documento", "concetto operativo"}:
        return scenario
    return title


def _specific_terms(digest: Dict[str, Any], sentence: str, limit: int = 8) -> List[str]:
    terms: List[str] = []
    terms.extend(digest.get("main_topics", [])[:5])
    terms.extend(_keywords(sentence, 6))
    terms.extend(digest.get("controls", [])[:3])
    return _dedupe_plain([term for term in terms if str(term).lower() not in STOPWORDS], limit)


def detect_card_document_profile(global_map: Dict[str, Any], original_text_sample: str, g2_profile: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if isinstance(g2_profile, dict) and g2_profile.get("tipo_testo") in PROFILE_CARD_DATA:
        base = dict(g2_profile)
    else:
        try:
            from backend.phase5_15g2_universal_long_summary_smoothing import detect_document_profile
            base = detect_document_profile(global_map, original_text_sample)
        except Exception:
            topics = " ".join(str(x) for x in global_map.get("global_topics", []))
            sample = f"{topics} {original_text_sample}".lower()
            tipo = "manuale_aziendale" if any(x in sample for x in ["procedura", "controllo", "audit"]) else "appunti_misti"
            base = {"tipo_testo": tipo, "confidence": 0.45, "focus_keywords": _keywords(sample, 12)}
    tipo = str(base.get("tipo_testo") or "appunti_misti")
    data = PROFILE_CARD_DATA.get(tipo, PROFILE_CARD_DATA["appunti_misti"])
    return {
        "tipo_testo": tipo,
        "confidence": float(base.get("confidence") or 0.5),
        "focus_keywords": _dedupe_plain(base.get("focus_keywords") or global_map.get("global_topics", []), 12),
        "card_style": data["card_style"],
        "preferred_card_types": list(data["preferred_card_types"]),
        "forbidden_generic_titles": sorted(GENERIC_TITLES),
        "expected_learning_value": data["expected_learning_value"],
    }


def _candidate_from_sentence(digest: Dict[str, Any], sentence: str, source_key: str, profile: str, ordinal: int) -> Dict[str, Any] | None:
    clean_sentence = _remove_template_noise(sentence)
    if not clean_sentence or _word_count(clean_sentence) < 8 or _has_noise(clean_sentence):
        return None
    terms = _specific_terms(digest, clean_sentence, 10)
    title_seed = _extract_title_from_sentence(clean_sentence, digest, profile)
    if title_seed.lower() in GENERIC_TITLES or TECHNICAL_TITLE_RE.search(title_seed) or "keyword" in title_seed.lower():
        title_seed = _clean_title("", terms)
    concept_type = _concept_type_from_text(clean_sentence, profile)
    facts = _dedupe_plain([clean_sentence] + [str(x) for x in digest.get(source_key, [])], 4)
    examples = [item for item in facts if re.search(r"\b(?:caso|esempio|applica|rileva|quando)\b", item, flags=re.I)][:2]
    if not examples:
        examples = [_finish_sentence(f"Applicazione: usare {title_seed.lower()} per collegare {', '.join(terms[:3])} a una verifica concreta")]
    why = _finish_sentence(f"Conta perché collega {title_seed.lower()} a {', '.join(terms[:4]) or 'un riferimento concreto'} e rende lo studio verificabile sulla fonte")
    score = 0.2 + min(0.3, len(terms) * 0.04) + (0.2 if examples else 0.0) + (0.2 if digest.get("controls") else 0.0)
    return {
        "concept_id": f"card_concept_{ordinal:03d}",
        "title_seed": title_seed,
        "source_section": _clean_title(str(digest.get("title") or f"Blocco {digest.get('index', ordinal)}"), terms),
        "source_theme": ", ".join((digest.get("main_topics") or terms)[:4]),
        "source_chunk_ids": [int(digest.get("index") or ordinal)],
        "source_sentence": clean_sentence,
        "concept_type": concept_type,
        "specific_terms": terms,
        "facts": facts,
        "examples": examples,
        "why_it_matters": why,
        "importance_score": round(min(1.0, score + min(0.2, int(digest.get("word_count") or 0) / 9000)), 3),
        "coverage_score": round(min(1.0, 0.4 + (int(digest.get("index") or 1) % 7) * 0.05), 3),
        "teaching_value_score": round(min(1.0, score + 0.15), 3),
        "raw_material": clean_sentence,
    }


def extract_card_concepts_from_long_doc(global_map: Dict[str, Any], g2_summary_result: Dict[str, Any] | None = None, original_text: str = "") -> List[Dict[str, Any]]:
    profile = "appunti_misti"
    if isinstance(g2_summary_result, dict):
        profile_data = g2_summary_result.get("profile") or g2_summary_result.get("document_profile") or {}
        if isinstance(profile_data, dict):
            profile = str(profile_data.get("tipo_testo") or profile)
    digests = list(global_map.get("block_digests") or [])
    concepts: List[Dict[str, Any]] = []
    ordinal = 1
    source_keys = ["procedures", "risks", "responsibilities", "definitions", "operational_facts", "operational_decisions"]
    for digest in digests:
        for key in source_keys:
            values = digest.get(key) if isinstance(digest.get(key), list) else []
            for sentence in values[:2]:
                candidate = _candidate_from_sentence(digest, str(sentence), key, profile, ordinal)
                if candidate:
                    concepts.append(candidate)
                    ordinal += 1
        if len([c for c in concepts if digest.get("index") in c.get("source_chunk_ids", [])]) < 2:
            candidate = _candidate_from_sentence(digest, str(digest.get("summary_anchor") or ""), "summary_anchor", profile, ordinal)
            if candidate:
                concepts.append(candidate)
                ordinal += 1
    if len(concepts) < 24 and original_text:
        for sentence in _split_sentences(original_text)[:260]:
            fake_digest = {"index": ordinal, "title": "Documento", "main_topics": _keywords(sentence, 6), "word_count": _word_count(sentence)}
            candidate = _candidate_from_sentence(fake_digest, sentence, "source", profile, ordinal)
            if candidate:
                concepts.append(candidate)
                ordinal += 1
            if len(concepts) >= 48:
                break
    return concepts


def _concept_score(concept: Dict[str, Any], profile: Dict[str, Any]) -> float:
    score = float(concept.get("importance_score") or 0.0)
    score += float(concept.get("coverage_score") or 0.0) * 0.3
    score += float(concept.get("teaching_value_score") or 0.0) * 0.5
    score += 0.3 if concept.get("source_sentence") else -0.4
    score += 0.2 if concept.get("examples") else -0.2
    score += min(0.3, len(concept.get("specific_terms") or []) * 0.04)
    if concept.get("concept_type") in profile.get("preferred_card_types", []):
        score += 0.2
    title = str(concept.get("title_seed") or "")
    if title.lower() in GENERIC_TITLES or TECHNICAL_TITLE_RE.search(title):
        score -= 1.0
    if _has_noise(title + " " + str(concept.get("source_sentence") or "")):
        score -= 2.0
    return round(score, 3)


def rank_card_concepts(card_concepts: Sequence[Dict[str, Any]], document_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    seen = set()
    for concept in card_concepts:
        title = _clean_title(str(concept.get("title_seed") or ""), concept.get("specific_terms") or [])
        if title.lower() in GENERIC_TITLES or _has_noise(title):
            continue
        key = " ".join(sorted(_normal_key(title + " " + " ".join(concept.get("specific_terms") or [])).split()[:8]))
        if not key or key in seen:
            continue
        seen.add(key)
        item = dict(concept)
        item["title_seed"] = title
        item["ranking_score"] = _concept_score(item, document_profile)
        if item["ranking_score"] > 0:
            filtered.append(item)
    filtered.sort(key=lambda item: (-float(item.get("ranking_score") or 0), min(item.get("source_chunk_ids") or [9999])))

    out: List[Dict[str, Any]] = []
    per_chunk: Dict[int, int] = {}
    unique_chunks = {
        int((concept.get("source_chunk_ids") or [0])[0] or 0)
        for concept in filtered
    }
    per_chunk_limit = 2 if len(unique_chunks) >= 6 else 6
    for concept in filtered:
        chunk = int((concept.get("source_chunk_ids") or [0])[0] or 0)
        if per_chunk.get(chunk, 0) >= per_chunk_limit:
            continue
        out.append(concept)
        per_chunk[chunk] = per_chunk.get(chunk, 0) + 1
    return out or filtered


def _message_for(concept: Dict[str, Any], profile: Dict[str, Any]) -> str:
    title = str(concept.get("title_seed") or "concetto")
    terms = ", ".join((concept.get("specific_terms") or [])[:4])
    return _finish_sentence(f"{title} serve a collegare {terms or 'i riferimenti principali'} a una decisione o verifica concreta della fonte")


def _explanation_for(concept: Dict[str, Any], profile: Dict[str, Any]) -> str:
    source = str(concept.get("source_sentence") or "")
    why = str(concept.get("why_it_matters") or "")
    return _finish_sentence(f"{_remove_template_noise(source)} {why}")


def _example_for(concept: Dict[str, Any], profile: Dict[str, Any]) -> str:
    examples = concept.get("examples") or []
    if examples:
        return _finish_sentence(_remove_template_noise(str(examples[0])))
    terms = ", ".join((concept.get("specific_terms") or [])[:3])
    return _finish_sentence(f"Applicazione: ripassa {concept.get('title_seed', 'il concetto')} collegando {terms} alla frase fonte indicata")


def build_traceable_study_cards(ranked_concepts: Sequence[Dict[str, Any]], document_profile: Dict[str, Any], max_cards: int | None = None) -> Dict[str, Any]:
    max_cards = max_cards or 12
    cards: List[Dict[str, Any]] = []
    for index, concept in enumerate(list(ranked_concepts)[:max_cards], start=1):
        title = _public_safe_title(str(concept.get("title_seed") or ""), concept.get("specific_terms") or [])
        message = _message_for(concept, document_profile)
        explanation = _explanation_for(concept, document_profile)
        example = _example_for(concept, document_profile)
        source_sentence = _remove_template_noise(str(concept.get("source_sentence") or ""))
        source_section = _clean_title(str(concept.get("source_section") or ""), concept.get("specific_terms") or [])
        terms = _dedupe_plain(concept.get("specific_terms") or [], 8)
        teaching = min(1.0, float(concept.get("teaching_value_score") or 0.5) + 0.15)
        specificity = min(1.0, 0.35 + len(terms) * 0.07 + (0.15 if source_sentence else 0.0))
        card = {
            "card_id": f"long_card_v515g3_{index:03d}",
            "id": f"long_card_v515g3_{index:03d}",
            "concept_id": concept.get("concept_id") or f"card_concept_{index:03d}",
            "title": title,
            "titolo": title,
            "subtitle": f"{concept.get('concept_type', 'concept')} · {source_section}",
            "message_key": message,
            "key_message": message,
            "messaggio_chiave": message,
            "explanation": explanation,
            "spiegazione": explanation,
            "short_explanation": explanation,
            "spiegazione_breve": explanation,
            "example": example,
            "esempio": example,
            "source_section": source_section,
            "source_theme": concept.get("source_theme") or ", ".join(terms[:4]),
            "source_sentence": source_sentence,
            "why_it_matters": concept.get("why_it_matters") or message,
            "card_type": concept.get("concept_type") or "concept",
            "points": _dedupe_plain([message, explanation, example, source_sentence], 4),
            "bullets": _dedupe_plain([message, explanation, example, source_sentence], 4),
            "bullet_points": _dedupe_plain([message, explanation, example, source_sentence], 4),
            "fatto_origine": source_sentence,
            "study_tip": _finish_sentence(f"Studia {title.lower()} partendo dall'esempio e verifica i termini: {', '.join(terms[:4])}"),
            "source_label": f"Fonte: {source_section}",
            "source": f"Fonte: {source_section}",
            "fonte": f"Fonte: {source_section}",
            "macro_area": source_section,
            "macro_area_index": int((concept.get("source_chunk_ids") or [index])[0] or index),
            "keywords": terms,
            "micro_concetti": terms,
            "quality_trace": {
                "specific_terms_used": terms,
                "facts_used": concept.get("facts") or [source_sentence],
                "genericity_score": round(1.0 - specificity, 3),
                "teaching_value_score": round(teaching, 3),
                "specificity_score": round(specificity, 3),
                "traceability_ok": bool(source_sentence or source_section),
            },
            "quality_rewrite": "v515g3_traceable_long_doc_card",
            "card_payload": True,
            "quiz_payload": False,
        }
        cards.append(card)
    return {"items": cards, "cards": cards, "profile": document_profile}


def improve_card_specificity_and_teaching_value(cards: Sequence[Dict[str, Any]], document_profile: Dict[str, Any]) -> Dict[str, Any]:
    improved: List[Dict[str, Any]] = []
    seen = set()
    seen_titles = set()
    warnings: List[str] = []
    for card in cards:
        item = dict(card)
        terms = item.get("keywords") or item.get("micro_concetti") or []
        title = _public_safe_title(str(item.get("title") or item.get("titolo") or ""), terms)
        if title.lower() in GENERIC_TITLES or TECHNICAL_TITLE_RE.search(title):
            title = _public_safe_title("", terms)
        title_key = _title_similarity_key(title) or _normal_key(title)
        if title_key in seen_titles:
            warnings.append(f"duplicate_title_skipped:{title}")
            continue
        seen_titles.add(title_key)
        key = _normal_key(title + " " + str(item.get("source_sentence") or ""))
        if key in seen:
            warnings.append(f"duplicate_card_skipped:{title}")
            continue
        seen.add(key)
        item["title"] = item["titolo"] = title
        if _word_count(item.get("message_key") or item.get("key_message") or "") < 10:
            item["message_key"] = item["key_message"] = item["messaggio_chiave"] = _message_for({"title_seed": title, "specific_terms": terms}, document_profile)
        if _word_count(item.get("explanation") or "") < 18:
            source = str(item.get("source_sentence") or item.get("fatto_origine") or "")
            item["explanation"] = item["spiegazione"] = _finish_sentence(f"{source} {item.get('why_it_matters') or item.get('message_key')}")
        if _word_count(item.get("example") or "") < 8:
            item["example"] = item["esempio"] = _finish_sentence(f"Applicazione: usa {title.lower()} per collegare {', '.join(terms[:3])} alla fonte indicata")
        if not item.get("source_sentence") and item.get("fatto_origine"):
            item["source_sentence"] = item["fatto_origine"]
        item["points"] = item["bullets"] = item["bullet_points"] = _dedupe_plain([
            item.get("message_key"), item.get("explanation"), item.get("example"), item.get("source_sentence")
        ], 4)
        improved.append(item)
    return {"items": improved, "warnings": warnings, "profile": document_profile}


def _backfill_cards_from_global_map(existing_cards: Sequence[Dict[str, Any]], global_map: Dict[str, Any], profile: Dict[str, Any], target_cards: int) -> List[Dict[str, Any]]:
    cards = [dict(card) for card in existing_cards]
    seen_titles = {_title_similarity_key(str(card.get("title") or "")) or _normal_key(str(card.get("title") or "")) for card in cards}
    for digest in global_map.get("block_digests") or []:
        if len(cards) >= target_cards:
            break
        source_sentence = _remove_template_noise(
            str((digest.get("operational_facts") or digest.get("procedures") or digest.get("responsibilities") or [digest.get("summary_anchor", "")])[0])
        )
        if not source_sentence:
            continue
        terms = _specific_terms(digest, source_sentence, 8)
        topic = _clean_title(str(digest.get("title") or ""), terms)
        if topic.lower() in GENERIC_TITLES or TECHNICAL_TITLE_RE.search(topic):
            topic = _clean_title("", terms)
        title = _public_safe_title(f"Verifica documentata di {topic}", terms)
        title_key = _title_similarity_key(title) or _normal_key(title)
        if title_key in seen_titles:
            title = _public_safe_title(f"Applicazione controllata di {topic}", terms)
            title_key = _title_similarity_key(title) or _normal_key(title)
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        concept = {
            "concept_id": f"card_concept_backfill_{len(cards) + 1:03d}",
            "title_seed": title,
            "source_section": topic,
            "source_theme": ", ".join(terms[:4]),
            "source_chunk_ids": [int(digest.get("index") or len(cards) + 1)],
            "source_sentence": source_sentence,
            "concept_type": _concept_type_from_text(source_sentence, str(profile.get("tipo_testo") or "")),
            "specific_terms": terms,
            "facts": [source_sentence],
            "examples": [_finish_sentence(f"Applicazione: verifica {topic.lower()} usando {', '.join(terms[:3])} e la frase fonte indicata")],
            "why_it_matters": _finish_sentence(f"Conta perché collega {topic.lower()} a una fonte verificabile e completa la copertura delle card"),
            "teaching_value_score": 0.82,
        }
        built = build_traceable_study_cards([concept], profile, max_cards=1).get("items") or []
        if built:
            built[0]["card_id"] = built[0]["id"] = f"long_card_v515g3_{len(cards) + 1:03d}"
            cards.append(built[0])
    return cards[:target_cards]


def _count_duplicates(cards: Sequence[Dict[str, Any]], field: str) -> int:
    values = [_normal_key(str(card.get(field) or "")) for card in cards]
    counts = Counter(value for value in values if value)
    return sum(count - 1 for count in counts.values() if count > 1)


def _template_phrase_count(cards: Sequence[Dict[str, Any]]) -> int:
    blob = "\n".join(str(card.get(key) or "") for card in cards for key in ["title", "message_key", "key_message", "explanation", "example"])
    low = blob.lower()
    return sum(low.count(phrase) for phrase in TEMPLATE_PHRASES)


def _generic_title_count(cards: Sequence[Dict[str, Any]]) -> int:
    count = 0
    for card in cards:
        title = str(card.get("title") or card.get("titolo") or "").strip()
        if title.lower() in GENERIC_TITLES or TECHNICAL_TITLE_RE.search(title):
            count += 1
    return count


def _specificity_scores(cards: Sequence[Dict[str, Any]]) -> List[float]:
    scores = []
    for card in cards:
        trace = card.get("quality_trace") if isinstance(card.get("quality_trace"), dict) else {}
        if "specificity_score" in trace:
            scores.append(float(trace.get("specificity_score") or 0.0))
        else:
            terms = card.get("keywords") or []
            scores.append(min(1.0, 0.35 + len(terms) * 0.07))
    return scores


def _teaching_scores(cards: Sequence[Dict[str, Any]]) -> List[float]:
    scores = []
    for card in cards:
        trace = card.get("quality_trace") if isinstance(card.get("quality_trace"), dict) else {}
        scores.append(float(trace.get("teaching_value_score") or 0.55))
    return scores


def validate_real_card_quality(cards_result: Dict[str, Any], document_profile: Dict[str, Any], original_text: str = "", global_map: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cards = list(cards_result.get("items") or cards_result.get("cards") or [])
    defects: List[str] = []
    warnings: List[str] = []
    cards_count = len(cards)
    cards_without_concept = sum(1 for card in cards if not card.get("concept_id"))
    generic_title_count = _generic_title_count(cards)
    template_phrase_count = _template_phrase_count(cards)
    duplicate_card_count = _count_duplicates(cards, "title")
    traceable = [card for card in cards if card.get("source_sentence") or card.get("source_section") or card.get("source_theme")]
    with_source_sentence = [card for card in cards if card.get("source_sentence")]
    with_examples = [card for card in cards if card.get("example") or card.get("esempio")]
    source_rate = round(len(traceable) / max(1, cards_count), 3)
    diversity = round(1.0 - duplicate_card_count / max(1, cards_count), 3)
    teaching_scores = _teaching_scores(cards)
    specificity_scores = _specificity_scores(cards)
    avg_teaching = round(sum(teaching_scores) / max(1, len(teaching_scores)), 3)
    avg_specificity = round(sum(specificity_scores) / max(1, len(specificity_scores)), 3)
    too_short = sum(1 for card in cards if _word_count(str(card.get("explanation") or "")) < 14)
    noise_count = sum(1 for card in cards if _has_noise(" ".join(str(card.get(k) or "") for k in ["title", "message_key", "explanation", "example"])))

    if cards_count <= 0:
        defects.append("cards_count_zero")
    if cards_without_concept:
        defects.append("cards_without_concept_id")
    if generic_title_count:
        defects.append("generic_or_technical_titles_present")
    if template_phrase_count:
        defects.append("template_phrases_present")
    if source_rate < 0.8:
        defects.append("traceability_rate_below_80_percent")
    if duplicate_card_count > max(1, cards_count // 8):
        defects.append("duplicate_card_count_high")
    if avg_teaching < 0.62:
        warnings.append("average_teaching_value_low")
    if avg_specificity < 0.62:
        warnings.append("average_specificity_low")
    if diversity < 0.85:
        warnings.append("diversity_score_low")
    if len(with_examples) < max(1, int(cards_count * 0.75)):
        warnings.append("few_cards_with_examples")
    if len(with_source_sentence) < max(1, int(cards_count * 0.7)):
        warnings.append("few_cards_with_source_sentence")
    if too_short:
        warnings.append("some_cards_too_short")
    if noise_count:
        defects.append("demo_fallback_script_noise_present")

    return {
        "pass": not defects,
        "warnings": warnings,
        "defects": defects,
        "metrics": {
            "cards_count": cards_count,
            "traceability_rate": source_rate,
            "generic_title_count": generic_title_count,
            "template_phrase_count": template_phrase_count,
            "duplicate_card_count": duplicate_card_count,
            "average_teaching_value_score": avg_teaching,
            "average_specificity_score": avg_specificity,
            "diversity_score": diversity,
            "cards_with_examples": len(with_examples),
            "cards_with_source_sentence": len(with_source_sentence),
            "cards_without_concept_id": cards_without_concept,
            "too_short_cards": too_short,
            "noise_count": noise_count,
        },
    }


def build_long_doc_cards_g3(global_map: Dict[str, Any], original_text: str, g2_profile: Dict[str, Any] | None = None, max_cards: int | None = None) -> Dict[str, Any]:
    profile = detect_card_document_profile(global_map, original_text[:14000], g2_profile)
    concepts = extract_card_concepts_from_long_doc(global_map, {"profile": profile}, original_text)
    ranked = rank_card_concepts(concepts, profile)
    target_cards = max_cards or 12
    built = build_traceable_study_cards(ranked, profile, max_cards=target_cards * 2)
    improved = improve_card_specificity_and_teaching_value(built.get("items", []), profile)
    improved["items"] = list(improved.get("items") or [])[:target_cards]
    if len(improved["items"]) < min(8, target_cards):
        improved["items"] = _backfill_cards_from_global_map(improved["items"], global_map, profile, target_cards)
    improved["cards"] = improved["items"]
    validation = validate_real_card_quality(improved, profile, original_text, global_map)
    items = improved.get("items", [])
    toc = [
        {
            "theme": card.get("title"),
            "macro_area": card.get("source_section") or card.get("macro_area"),
            "concept": (card.get("keywords") or [card.get("card_type", "concept")])[0],
        }
        for card in items
    ]
    metrics = {
        **validation.get("metrics", {}),
        "concepts_extracted": len(concepts),
        "concepts_ranked": len(ranked),
        "covered_macro_areas": sorted({int(card.get("macro_area_index") or 0) for card in items if card.get("macro_area_index")}),
        "validation_pass": validation.get("pass"),
    }
    return {
        "items": items,
        "cards": items,
        "dynamic_toc": toc,
        "profile": profile,
        "concepts": concepts,
        "ranked_concepts": ranked,
        "validation": validation,
        "warnings": _dedupe_plain(list(improved.get("warnings") or []) + list(validation.get("warnings") or [])),
        "defects": validation.get("defects", []),
        "metrics": metrics,
    }
