#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini LLM/RAG - Study Pack Universale V4
Versione progetto: V3.9.7

Obiettivo:
- Generare un pacchetto studio universale partendo da un testo reale.
- Evitare fallback/demo/sentence bank/risposte inventate.
- Bloccare output poveri o generici con QUALITY_BLOCKED.
- Restare indipendente dalla UI: questo file è un runtime separato.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


VERSION = "3.9.7-sp7"
ENGINE_NAME = "mini_llm_universal_study_pack_v4"


ITALIAN_STOPWORDS = {
    "a", "ad", "al", "allo", "alla", "alle", "agli", "ai", "all", "anche", "ancora",
    "avere", "con", "come", "da", "dal", "dallo", "dalla", "dalle", "dagli", "dai",
    "de", "dei", "del", "dello", "della", "delle", "degli", "di", "e", "ed", "è",
    "essere", "fa", "fra", "gli", "ha", "hanno", "ho", "il", "in", "io", "l", "la",
    "le", "lo", "ma", "mi", "ne", "nei", "nel", "nello", "nella", "nelle", "negli",
    "no", "non", "o", "per", "più", "può", "quale", "quali", "quando", "quanto",
    "questa", "queste", "questi", "questo", "se", "si", "sia", "sono", "su", "sul",
    "sullo", "sulla", "sulle", "sugli", "sui", "tra", "un", "una", "uno", "del",
    "che", "chi", "cui", "dove", "dal", "così", "suo", "sua", "sue", "suoi", "ogni",
    "tutti", "tutte", "molto", "molti", "molte", "bene", "male", "prima", "dopo",
}

ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "he", "her", "his", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were", "which", "with", "without", "you", "your",
}

BAD_GENERIC_WORDS = {
    "cosa", "voce", "elemento", "aspetto", "tema", "parte", "argomento", "testo",
    "documento", "contenuto", "informazione", "informazioni", "materiale", "sezione",
    "thing", "item", "topic", "content", "text", "document",
}

BAD_ENDINGS = {
    "e", "o", "ma", "per", "con", "di", "da", "in", "su", "tra", "fra", "un", "una",
    "uno", "il", "lo", "la", "le", "gli", "dei", "del", "della", "delle", "and",
    "or", "with", "of", "the", "a", "an", "to", "for",
}

# Token che possono essere utili dentro una frase, ma NON devono diventare
# concetti chiave. Servono a evitare micro-concetti brutti come
# "significa dati devono", "servizio viene violato" o "utenti usano password".
BAD_CONCEPT_TOKENS = {
    "significa", "significano", "indica", "indicano", "comprende", "comprendono",
    "richiede", "richiedono", "prevede", "prevedono", "consiste", "consistono",
    "deve", "devono", "può", "possono", "viene", "vengono", "vanno",
    "usano", "usa", "usare", "usato", "usati", "utilizza", "utilizzano",
    "serve", "servono", "permette", "permettono", "consente", "consentono",
    "aiuta", "aiutano", "migliora", "migliorano", "riduce", "riducono",
    "dovrebbe", "dovrebbero", "contenere", "contiene", "buona", "buone", "buono",
    "adeguata", "adeguato", "nuovi", "nuovo", "sfrutta", "sfruttano",
    "verso", "secondo", "seconda",
    "evita", "evitano", "gestisce", "gestiscono", "gestire", "proteggere",
    "proteggono", "protetti", "protette", "segnalare", "segnalato", "segnalata",
    "senza", "quando", "perché", "quindi", "inoltre", "oppure", "attraverso",
    "violato", "violata", "compromesso", "compromessa", "coinvolto", "coinvolti",
    "inserito", "inserita", "cartella", "generare", "genera", "quiz", "test",
    "mini-corsi", "minicorsi", "altri", "altro", "chiaro", "chiara", "recuperare",
    "principali", "principale", "protegge", "proteggono", "creare", "crea",
    "poter", "modificare", "accedere", "installare",
    "salvare", "salva", "salvato", "salvati", "salvate", "lunghe", "uniche",
    "manuale", "tecnico", "avanzato", "avanzata",
}

BAD_CONCEPT_PHRASE_PATTERNS = (
    r"\b(significa|devono|deve|viene|vengono|usano|usa|senza|inserito|cartella|generare|recuperare)\b",
    r"\b(dati\s+dispositivi|dispositivi\s+account|rete\s+aziendale\s+account)\b",
    r"\b(servizio\s+viene|utenti\s+usano|password\s+altri|chiaro\s+sistema)\b",
    r"\b(strumenti\s+comportamenti|comportamenti\s+dati|dati\s+riservati\s+controllo)\b",
    r"\b(mini-corsi\s+sicurezza|aziendale\s+account\s+online|solo\s+password)\b",
    r"\b(buona\s+password|password\s+dovrebbe|dovrebbe\s+contenere|password\s+contenere)\b",
    r"\b(nuovi\s+utenti\s+aziendali|buona\s+password\s+dovrebbe)\b",
    r"\b(manuale\s+tecnico\s+avanzato|salvare\s+password|password\s+lunghe|password\s+lunghe\s+uniche)\b",
    r"\b(secondo\s+controllo|seconda\s+verifica)\b",
)

META_SENTENCE_PATTERNS = (
    r"rag/documenti",
    r"`[^`]+`",
    r"\bcartella\b.*\bgenerare\b",
    r"\bgenerare\b.*\b(quiz|test|mini-corsi|minicorsi)\b",
    r"\bpu[oò]\s+essere\s+inserit[oa]\b",
    r"\bfile\s+markdown\b",
    r"\bquesto\s+documento\s+pu[oò]\b",
    r"\bl['’]?obiettivo\s+[èe]\s+spiegare\b",
    r"\butili\s+a\s+dipendenti,?\s+studenti\s+e\s+nuovi\s+utenti\b",
    r"\bmanuale\s+tecnico\s+avanzato\b",
    r"\bsistema\s+rag\b",
    r"\bmateriale\s+formativo\s+chiaro\b",
    r"\bdomande\s+controllate\b",
    r"\bda\s+cui\s+un\s+sistema\s+rag\b",
)


BLOCKED_MARKERS = {
    "fallback", "demo", "lorem ipsum", "placeholder", "sentence_bank",
    "memory_sentence", "anchored_memory", "hardcoded", "risposta esempio",
    "domanda esempio", "contenuto generico",
}

PROFILE_KEYWORDS = {
    "informatica": {
        "password", "backup", "rete", "server", "database", "sicurezza", "accesso",
        "utente", "malware", "phishing", "crittografia", "firewall", "cloud",
        "vulnerabilità", "autenticazione", "privacy", "dati", "software",
    },
    "aziendale": {
        "azienda", "processo", "cliente", "team", "ruolo", "procedura", "qualità",
        "obiettivo", "servizio", "progetto", "budget", "rischio", "compliance",
        "formazione", "responsabile", "organizzazione",
    },
    "sport": {
        "allenamento", "forza", "resistenza", "recupero", "serie", "ripetizioni",
        "atleta", "gara", "esercizio", "mobilità", "cardio", "carico", "tecnica",
    },
    "cv": {
        "esperienza", "competenze", "profilo", "candidato", "formazione", "lavoro",
        "progetto", "responsabilità", "obiettivo", "curriculum", "lingue",
    },
    "narrativa": {
        "personaggio", "storia", "racconto", "capitolo", "scena", "dialogo",
        "voce", "luogo", "tempo", "trama", "conflitto", "finale",
    },
    "poesia": {
        "verso", "strofa", "rima", "immagine", "metafora", "ritmo", "poeta",
        "lirico", "simbolo", "parola", "suono",
    },
    "normativo": {
        "articolo", "comma", "norma", "legge", "regolamento", "obbligo", "diritto",
        "sanzione", "requisito", "autorizzazione",
    },
}


@dataclass
class Concept:
    text: str
    score: float
    count: int
    sentence_index: int
    evidence: str


def normalize_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?m)^\s*(pagina|page)\s+\d+\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d+\s*/\s*\d+\s*$", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    # Mantiene frasi reali e spezza anche elenchi lunghi su newline.
    blocks = re.split(r"\n+", text)
    sentences: List[str] = []
    for block in blocks:
        block = block.strip(" -•\t")
        if not block:
            continue
        parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])", block)
        for part in parts:
            cleaned = clean_sentence(part)
            if cleaned:
                sentences.append(cleaned)
    return sentences


def clean_sentence(sentence: str) -> str:
    s = re.sub(r"\s+", " ", sentence).strip(" -•\t")
    s = s.strip()
    s = re.sub(r"^[\-–—•]\s*", "", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    if s and s[-1] not in ".!?":
        s += "."
    return s


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-]*", text.lower())


def is_meta_sentence(sentence: str) -> bool:
    low = sentence.lower()
    return any(re.search(pattern, low) for pattern in META_SENTENCE_PATTERNS)


def normalized_label(label: str) -> str:
    low = re.sub(r"\s+", " ", label.lower()).strip(" -•\t.,;:")
    replacements = {
        "autenticazione a più fattori": "autenticazione multifattore",
        "autenticazione a piu fattori": "autenticazione multifattore",
        "piano di continuità operativa": "continuità operativa",
        "piano di continuita operativa": "continuità operativa",
        "protezione dei dati": "protezione dati",
        "protezione dati personali": "dati personali",
        "password principale": "password manager",
    }
    if low in replacements:
        return replacements[low]
    # Rimuove connettori grammaticali interni quando la frase resta naturale.
    low = re.sub(r"\b(degli|delle|dei|del|della|di|da|a|per)\b", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def explicit_concept_labels(sentence: str) -> List[str]:
    """Estrae locuzioni tecniche leggibili senza usare una sentence bank.

    Le regex non producono contenuto inventato: recuperano solo espressioni
    presenti letteralmente nella frase sorgente e le normalizzano quando
    contengono connettori grammaticali.
    """
    low = sentence.lower()
    patterns = [
        r"sicurezza\s+informatica(?:\s+aziendale)?",
        r"stessa\s+password",
        r"password\s+(?:manager|robuste|deboli|principale)",
        r"credenziali\s+robuste",
        r"strumenti\s+cloud",
        r"sistemi\s+di\s+pagamento",
        r"procedure\s+controllate",
        r"tracciamento\s+(?:delle\s+)?versioni",
        r"urgenza\s+artificiale",
        r"pagine\s+contraffatte",
        r"dati\s+(?:sensibili|personali|riservati)",
        r"account\s+(?:online|amministrativi|inattivi|aziendali)",
        r"autenticazione\s+a\s+pi[ùu]\s+fattori",
        r"(?:e-mail|email)\s+sospette",
        r"link\s+sospetti",
        r"tecnica\s+di\s+phishing",
        r"aggiornamenti\s+(?:software|controllati)",
        r"gestione\s+(?:accessi|incidenti|clienti|fornitori)",
        r"controllo\s+(?:accessi|periodico|qualit[aà])",
        r"backup\s+(?:dei\s+)?dati",
        r"continuit[aà]\s+operativa",
        r"protezione\s+(?:dei\s+)?dati(?:\s+personali)?",
        r"formazione\s+interna",
        r"procedure\s+semplici",
        r"tentativi\s+accesso",
        r"utenti\s+autorizzati",
        r"file\s+critici",
        r"software\s+aggiornati",
        r"controllo\s+qualit[aà]",
        r"tempi\s+risposta",
        r"miglioramento\s+continuo",
        r"documentazione\s+condivisa",
        r"prevenzione\s+infortuni",
        r"diario\s+allenamento",
        r"carico\s+allenante",
        r"recupero\s+muscolare",
        r"tecnica\s+esecutiva",
    ]
    found: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, low):
            label = normalized_label(match.group(0))
            if label and concept_label_quality(label):
                found.append(label)
    return found


def is_content_token(token: str) -> bool:
    t = token.lower().strip("'’-.")
    if len(t) < 4:
        return False
    if t in ITALIAN_STOPWORDS or t in ENGLISH_STOPWORDS:
        return False
    if t in BAD_GENERIC_WORDS or t in BAD_CONCEPT_TOKENS:
        return False
    if re.fullmatch(r"\d+", t):
        return False
    if len(set(t)) <= 2 and len(t) > 5:
        return False
    return True


def concept_label_quality(phrase: str) -> bool:
    """Valida un'etichetta concettuale prima di mostrarla all'utente.

    Il motore deve estrarre micro-concetti leggibili, non pezzi casuali di frase.
    Qui non correggiamo l'output a posteriori: impediamo a concetti brutti di
    entrare nello Study Pack.
    """
    normalized = re.sub(r"\s+", " ", phrase.lower()).strip(" -•	.,;:")
    toks = normalized.split()
    if len(toks) < 2 or len(toks) > 3:
        return False
    if len(set(toks)) != len(toks):
        return False
    if any(t in BAD_GENERIC_WORDS or t in BAD_CONCEPT_TOKENS or t in BAD_ENDINGS for t in toks):
        return False
    if toks[0] in BAD_ENDINGS or toks[-1] in BAD_ENDINGS:
        return False
    if any(re.search(pattern, normalized) for pattern in BAD_CONCEPT_PHRASE_PATTERNS):
        return False
    # Evita catene di sostantivi nate attraversando virgole/elenchi grezzi.
    if len(toks) == 3 and all(len(t) <= 11 for t in toks):
        # Alcuni trigrammi tecnici sono buoni, ma se sembrano solo una lista
        # di oggetti scollegati è meglio preferire bigrammi più leggibili.
        weak_list_tokens = {"dati", "dispositivi", "account", "sistemi", "utenti", "servizio", "rete"}
        if sum(1 for t in toks if t in weak_list_tokens) >= 2:
            return False
    return True


def sentence_concept_spans(sentence: str) -> List[List[str]]:
    """Restituisce token consecutivi reali, senza attraversare stopword o elenchi.

    SP3: non basta ignorare la punteggiatura. Anche congiunzioni e preposizioni
    devono interrompere lo span, altrimenti da frasi come "strumenti e
    comportamenti usati per proteggere dati" nascono etichette artificiali come
    "strumenti comportamenti dati".
    """
    spans: List[List[str]] = []
    current: List[str] = []
    raw_tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-]*|[,;:()\[\]{}]", sentence.lower())
    for tok in raw_tokens:
        if re.fullmatch(r"[,;:()\[\]{}]", tok):
            if current:
                spans.append(current)
                current = []
            continue
        if is_content_token(tok):
            current.append(tok)
        else:
            if current:
                spans.append(current)
                current = []
    if current:
        spans.append(current)
    return [span for span in spans if span]


def sentence_quality(sentence: str) -> bool:
    words = tokenize(sentence)
    # V3.9.7-SP1: gli elementi studio usano la frase sorgente come
    # messaggio chiave/fonte/risposta guida. Se la frase sorgente è
    # troppo corta, il validatore finale la blocca. Quindi la soglia
    # viene alzata qui, prima della generazione, invece di correggere
    # l’output dopo.
    if len(words) < 9:
        return False
    if len(sentence) < 45 or len(sentence) > 320:
        return False
    low = sentence.lower()
    if is_meta_sentence(sentence):
        return False
    if any(marker in low for marker in BLOCKED_MARKERS):
        return False
    if re.search(r"\b(un|una|uno|il|la|lo|le|gli)\s+in\s+(un|una|uno|il|la|lo)\b", low):
        return False
    if re.search(r"\b(l|un|una|uno)\s+in\b", low):
        return False
    if tokenize(sentence)[-1] in BAD_ENDINGS:
        return False
    return True


def meaningful_sentences(sentences: List[str]) -> List[Tuple[int, str]]:
    result = []
    for idx, sentence in enumerate(sentences):
        if sentence_quality(sentence):
            result.append((idx, sentence))
    return result


def extract_concepts(sentences: List[Tuple[int, str]], limit: int = 18) -> List[Concept]:
    unigram_counts: Counter[str] = Counter()
    phrase_counts: Counter[str] = Counter()
    first_seen: Dict[str, Tuple[int, str]] = {}

    for idx, sentence in sentences:
        spans = sentence_concept_spans(sentence)
        toks = [t for span in spans for t in span]
        unigram_counts.update(toks)

        for phrase in explicit_concept_labels(sentence):
            phrase_counts[phrase] += 2
            first_seen.setdefault(phrase, (idx, sentence))

        # Frasi da 2-3 parole significative consecutive dentro lo stesso span.
        # Non attraversiamo virgole/elenchi, così evitiamo etichette tipo
        # "dati dispositivi account".
        for span in spans:
            for n in (2, 3):
                for i in range(0, max(0, len(span) - n + 1)):
                    phrase_tokens = span[i:i + n]
                    if len(phrase_tokens) != n:
                        continue
                    phrase = " ".join(phrase_tokens)
                    if not concept_label_quality(phrase):
                        continue
                    phrase_counts[phrase] += 1
                    first_seen.setdefault(phrase, (idx, sentence))

    concepts: List[Concept] = []

    for phrase, count in phrase_counts.items():
        idx, evidence = first_seen[phrase]
        token_bonus = sum(math.log1p(unigram_counts[t]) for t in phrase.split())
        length_bonus = 1.25 if len(phrase.split()) == 2 else 1.45
        early_bonus = 1.0 / (1.0 + idx * 0.03)
        score = (count * 3.0 + token_bonus) * length_bonus * early_bonus
        concepts.append(Concept(phrase, score, count, idx, evidence))

    # Niente fallback a parole singole: se non ci sono abbastanza micro-concetti
    # leggibili, il blocco qualità deve fallire invece di inventare etichette povere.

    concepts.sort(key=lambda c: (-c.score, c.sentence_index, c.text))

    deduped: List[Concept] = []
    used_tokens: List[set[str]] = []
    sentence_usage: Counter[int] = Counter()
    for concept in concepts:
        toks = set(concept.text.split())
        if sentence_usage[concept.sentence_index] >= 2:
            continue
        if any(len(toks & old) / max(1, min(len(toks), len(old))) >= 0.80 for old in used_tokens):
            continue
        if concept.text in BAD_GENERIC_WORDS or not concept_label_quality(concept.text):
            continue
        deduped.append(concept)
        used_tokens.append(toks)
        sentence_usage[concept.sentence_index] += 1
        if len(deduped) >= limit:
            break

    # Secondo giro: se il limite per frase ha stretto troppo, riempi senza superare 3 concetti per frase.
    if len(deduped) < limit:
        for concept in concepts:
            if concept in deduped:
                continue
            toks = set(concept.text.split())
            if sentence_usage[concept.sentence_index] >= 3:
                continue
            if any(len(toks & old) / max(1, min(len(toks), len(old))) >= 0.90 for old in used_tokens):
                continue
            deduped.append(concept)
            used_tokens.append(toks)
            sentence_usage[concept.sentence_index] += 1
            if len(deduped) >= limit:
                break

    return deduped


def detect_profile(text: str) -> Dict[str, Any]:
    toks = Counter(tokenize(text))
    scores = {}
    for profile, keywords in PROFILE_KEYWORDS.items():
        score = sum(toks[k] for k in keywords)
        if score:
            scores[profile] = score
    if not scores:
        return {"primary": "universale", "scores": {}}
    ordered = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return {"primary": ordered[0][0], "scores": dict(ordered)}


def compress_sentence(sentence: str, max_chars: int = 210) -> str:
    s = clean_sentence(sentence)
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars].rsplit(" ", 1)[0].rstrip(",;:")
    if tokenize(cut) and tokenize(cut)[-1] in BAD_ENDINGS:
        cut = " ".join(cut.split()[:-1])
    return cut.rstrip(".") + "."


def sentence_focus(sentence: str, concept: str) -> str:
    words = [w for w in tokenize(sentence) if is_content_token(w)]
    concept_words = set(concept.split())
    focus_words = [w for w in words if w not in concept_words][:5]
    if not focus_words:
        return "i passaggi principali del documento"
    return " ".join(focus_words[:4])


def enough_field_words(value: str, minimum: int = 8) -> bool:
    return len(tokenize(value)) >= minimum


def evidence_for_field(concept: Concept, max_chars: int = 240, minimum: int = 8) -> str:
    """Restituisce una frase sorgente utilizzabile nei campi validati.

    Non inventa contenuto di dominio: parte sempre dalla frase sorgente
    del documento. Se la frase compressa diventasse troppo corta, usa
    la stessa evidenza con una cornice tecnica minima, così il validatore
    segnala comunque contenuto collegato al testo e non una risposta
    tronca.
    """
    evidence = compress_sentence(concept.evidence, max_chars)
    if enough_field_words(evidence, minimum):
        return evidence

    expanded = clean_sentence(f"Il documento collega {concept.text} a questo passaggio: {concept.evidence}")
    expanded = compress_sentence(expanded, max_chars)
    if enough_field_words(expanded, minimum):
        return expanded

    # Ultima difesa: meglio bloccare in validazione che produrre una
    # frase vuota o un fallback. Non aggiungiamo contenuti demo.
    return evidence


def select_summary_sentences(sentences: List[Tuple[int, str]], concepts: List[Concept], limit: int = 6) -> List[str]:
    concept_terms = [c.text for c in concepts[:12]]
    selected: List[str] = []
    used_tokens: List[set[str]] = []

    scored: List[Tuple[float, int, str]] = []
    for idx, sentence in sentences:
        low = sentence.lower()
        coverage = sum(1 for term in concept_terms if term in low)
        content_count = sum(1 for t in tokenize(sentence) if is_content_token(t))
        score = coverage * 3.0 + min(content_count, 18) * 0.25 + 1.0 / (1 + idx)
        scored.append((score, idx, sentence))

    for _, _, sentence in sorted(scored, key=lambda x: (-x[0], x[1])):
        toks = set(t for t in tokenize(sentence) if is_content_token(t))
        if any(len(toks & old) / max(1, min(len(toks), len(old))) > 0.65 for old in used_tokens):
            continue
        selected.append(compress_sentence(sentence, 260))
        used_tokens.append(toks)
        if len(selected) >= limit:
            break

    return selected


def make_question(concept: Concept) -> Dict[str, str]:
    concept_label = concept.text.replace("_", " ")
    low = concept.evidence.lower()
    if "password manager" in concept_label:
        question = f"A cosa serve il {concept_label}?"
    elif "sicurezza informatica" in concept_label and any(v in low for v in ("insieme", "pratiche", "strumenti", "comportamenti")):
        question = f"Come viene definita {concept_label} nel documento?"
    elif any(v in low for v in ("rischio", "vulnerabile", "violato", "phishing", "sospetti", "deboli")):
        question = f"Quale rischio viene collegato a {concept_label}?"
    elif any(v in low for v in ("deve", "devono", "richiede", "obbligo", "necessario", "regola", "disponibilità significa")):
        question = f"Quale regola operativa riguarda {concept_label}?"
    elif any(v in low for v in ("permette", "consente", "aiuta", "migliora", "riduce", "protegge", "proteggere")):
        question = f"Quale funzione svolge il concetto di {concept_label}?"
    else:
        question = f"Che cosa chiarisce il documento su {concept_label}?"
    question = question.rstrip(" .?!") + "?"
    return {
        "domanda": question,
        "risposta_guida": evidence_for_field(concept, 240, 8),
        "concetto_collegato": concept.text,
    }


def make_card(concept: Concept) -> Dict[str, str]:
    evidence = evidence_for_field(concept, 240, 8)
    return {
        "titolo": concept.text.title(),
        "messaggio_chiave": evidence_for_field(concept, 220, 8),
        "spiegazione": compress_sentence(
            f"Il passaggio chiarisce il tema {concept.text}: {evidence}",
            280,
        ),
        "fonte_testuale": evidence_for_field(concept, 260, 8),
    }


def make_glossary(concept: Concept) -> Dict[str, str]:
    return {
        "termine": concept.text,
        "definizione_operativa": compress_sentence(concept.evidence, 220),
    }


def make_quiz(concepts: List[Concept], limit: int = 6) -> List[Dict[str, Any]]:
    quiz: List[Dict[str, Any]] = []
    usable = concepts[: max(limit + 6, 12)]
    if len(usable) < 8:
        return quiz

    for i, concept in enumerate(usable[:limit]):
        correct = compress_sentence(concept.evidence, 170)
        distractors: List[str] = []
        for other in usable:
            if other.text == concept.text:
                continue
            option = compress_sentence(other.evidence, 170)
            if option != correct and option not in distractors:
                distractors.append(option)
            if len(distractors) >= 3:
                break

        options = [correct] + distractors[:3]
        if len(options) != 4 or len(set(options)) != 4:
            continue

        # Rotazione deterministica, senza random: mantiene test ripetibile.
        shift = i % 4
        options = options[shift:] + options[:shift]

        quiz.append({
            "domanda": f"Secondo il documento, quale affermazione descrive meglio {concept.text}?",
            "opzioni": options,
            "risposta_corretta": correct,
            "spiegazione": compress_sentence(
                f"La risposta corretta coincide con il passaggio del documento usato come fonte per {concept.text}.",
                220,
            ),
            "concetto_collegato": concept.text,
        })

    return quiz


def make_review_plan(concepts: List[Concept]) -> List[Dict[str, str]]:
    buckets = [
        ("Giorno 1", "Leggi la sintesi e sottolinea i concetti portanti."),
        ("Giorno 2", "Studia le card e riscrivi a parole tue i messaggi chiave."),
        ("Giorno 3", "Rispondi alle domande guida senza guardare le risposte."),
        ("Giorno 4", "Esegui il quiz e correggi gli errori partendo dalle fonti testuali."),
    ]
    top = [c.text for c in concepts[:8]]
    plan = []
    for day, task in buckets:
        plan.append({
            "fase": day,
            "attivita": task,
            "concetti_da_ripassare": ", ".join(top[:4] if day in ("Giorno 1", "Giorno 2") else top[4:8] or top[:4]),
        })
    return plan


def validate_pack(pack: Dict[str, Any], source_text: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    source_low = source_text.lower()

    if pack.get("status") == "QUALITY_BLOCKED":
        errors.extend(pack.get("quality_errors", []))
        return False, errors

    required = ["sintesi", "concetti_chiave", "card_studio", "domande_guida", "quiz", "glossario", "piano_ripasso"]
    for key in required:
        if key not in pack or not pack[key]:
            errors.append(f"Sezione mancante o vuota: {key}")

    serialized = json.dumps(pack, ensure_ascii=False).lower()
    for marker in BLOCKED_MARKERS:
        if marker in serialized and marker not in source_low:
            errors.append(f"Marker vietato trovato nell'output: {marker}")

    for bad in ("un in una", "l in", "è sicurezza un in", "è password un in"):
        if bad in serialized:
            errors.append(f"Frase nonsense rilevata: {bad}")

    banned_runtime_fragments = (
        "rag/documenti", "cartella `", "generare quiz", "generare test",
        "mini-corsi sulla sicurezza", "quale ruolo ha", "rispetto a", "??",
        "è collegato a", "strumenti comportamenti", "chiaro sistema recuperare",
        "password altri account", "solo password", "secondo controllo",
    )
    for fragment in banned_runtime_fragments:
        if fragment in serialized:
            errors.append(f"Frammento innaturale o tecnico vietato nell'output: {fragment}")

    concepts = pack.get("concetti_chiave", [])
    if len(concepts) < 8:
        errors.append("Meno di 8 concetti chiave generati.")
    if len(set(c.lower() for c in concepts)) != len(concepts):
        errors.append("Concetti chiave duplicati.")

    for idx, concept in enumerate(concepts, start=1):
        if not concept_label_quality(str(concept)):
            errors.append(f"Concetto chiave #{idx} non naturale o incompleto: {concept}")


    for section_name in ("sintesi",):
        for idx, item in enumerate(pack.get(section_name, []), start=1):
            toks = tokenize(str(item))
            if len(toks) < 8:
                errors.append(f"{section_name} #{idx} troppo corta.")
            if toks and toks[-1] in BAD_ENDINGS:
                errors.append(f"{section_name} #{idx} termina male: {toks[-1]}")

    for idx, card in enumerate(pack.get("card_studio", []), start=1):
        for field in ("titolo", "messaggio_chiave", "spiegazione", "fonte_testuale"):
            value = str(card.get(field, "")).strip()
            if not value:
                errors.append(f"Card #{idx}: campo vuoto {field}")
            if field != "titolo" and len(tokenize(value)) < 8:
                errors.append(f"Card #{idx}: {field} troppo corto.")
            if tokenize(value) and tokenize(value)[-1] in BAD_ENDINGS:
                errors.append(f"Card #{idx}: {field} termina male.")

    for idx, item in enumerate(pack.get("domande_guida", []), start=1):
        q = str(item.get("domanda", "")).strip()
        a = str(item.get("risposta_guida", "")).strip()
        if not q.endswith("?"):
            errors.append(f"Domanda guida #{idx} non termina con punto interrogativo.")
        if len(tokenize(q)) < 6:
            errors.append(f"Domanda guida #{idx} troppo corta.")
        if len(tokenize(a)) < 8:
            errors.append(f"Risposta guida #{idx} troppo corta.")

    for idx, item in enumerate(pack.get("quiz", []), start=1):
        options = item.get("opzioni", [])
        correct = item.get("risposta_corretta", "")
        if len(options) != 4:
            errors.append(f"Quiz #{idx}: opzioni diverse da 4.")
        if len(set(options)) != len(options):
            errors.append(f"Quiz #{idx}: opzioni duplicate.")
        if correct not in options:
            errors.append(f"Quiz #{idx}: risposta corretta non presente nelle opzioni.")
        for opt in options:
            if len(tokenize(str(opt))) < 7:
                errors.append(f"Quiz #{idx}: opzione troppo corta.")

    return len(errors) == 0, errors


def build_study_pack(raw_text: str, source_name: str = "documento") -> Dict[str, Any]:
    text = normalize_text(raw_text)
    all_sentences = split_sentences(text)
    sentences = meaningful_sentences(all_sentences)
    profile = detect_profile(text)
    concepts = extract_concepts(sentences)

    quality_errors: List[str] = []
    if len(text) < 700:
        quality_errors.append("Testo troppo corto per generare uno Study Pack affidabile.")
    if len(sentences) < 8:
        quality_errors.append("Poche frasi informative utilizzabili dopo la pulizia.")
    if len(concepts) < 8:
        quality_errors.append("Pochi micro-concetti specifici estratti dal documento.")

    if quality_errors:
        return {
            "engine": ENGINE_NAME,
            "version": VERSION,
            "status": "QUALITY_BLOCKED",
            "source_name": source_name,
            "profile": profile,
            "quality_errors": quality_errors,
            "raw_chars": len(raw_text),
            "cleaned_chars": len(text),
            "usable_sentences": len(sentences),
            "concept_count": len(concepts),
        }

    summary = select_summary_sentences(sentences, concepts, limit=6)
    cards = [make_card(c) for c in concepts[:8]]
    questions = [make_question(c) for c in concepts[:8]]
    quiz = make_quiz(concepts, limit=6)
    glossary = [make_glossary(c) for c in concepts[:10]]
    review_plan = make_review_plan(concepts)

    title_concepts = " · ".join(c.text.title() for c in concepts[:3])

    pack: Dict[str, Any] = {
        "engine": ENGINE_NAME,
        "version": VERSION,
        "status": "OK",
        "source_name": source_name,
        "profile": profile,
        "titolo": f"Study Pack Universale V4 - {title_concepts}",
        "raw_chars": len(raw_text),
        "cleaned_chars": len(text),
        "usable_sentences": len(sentences),
        "concetti_chiave": [c.text for c in concepts[:10]],
        "sintesi": summary,
        "card_studio": cards,
        "domande_guida": questions,
        "quiz": quiz,
        "glossario": glossary,
        "piano_ripasso": review_plan,
        "quality_notes": [
            "Output generato solo dal testo sorgente.",
            "Nessun contenuto precotto o memoria fraseologica utilizzati.",
            "Se la qualità minima non è raggiunta, il motore restituisce blocco qualità.",
            "SP4: concetti incompleti e frasi meta-tecniche vengono esclusi prima della generazione.",
            "SP5: righe meta sul progetto RAG/manuale tecnico e concetti verbali vengono scartati.",
            "SP6: concetti chiave esposti limitati ai migliori 10 e filtro finale su concetti orfani/spuri.",
            "SP7: il validatore distingue frasi fonte legittime da concetti chiave brutti.",
        ],
    }

    ok, errors = validate_pack(pack, text)
    if not ok:
        return {
            "engine": ENGINE_NAME,
            "version": VERSION,
            "status": "QUALITY_BLOCKED",
            "source_name": source_name,
            "profile": profile,
            "quality_errors": errors,
            "raw_chars": len(raw_text),
            "cleaned_chars": len(text),
            "usable_sentences": len(sentences),
            "concept_count": len(concepts),
        }

    return pack


def render_markdown(pack: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {pack.get('titolo', 'Study Pack Universale V4')}")
    lines.append("")
    lines.append(f"- Engine: `{pack.get('engine')}`")
    lines.append(f"- Versione: `{pack.get('version')}`")
    lines.append(f"- Stato: `{pack.get('status')}`")
    lines.append(f"- Profilo: `{pack.get('profile', {}).get('primary', 'universale')}`")
    lines.append("")

    if pack.get("status") == "QUALITY_BLOCKED":
        lines.append("## Quality Block")
        for error in pack.get("quality_errors", []):
            lines.append(f"- {error}")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Concetti chiave")
    for concept in pack.get("concetti_chiave", []):
        lines.append(f"- {concept}")
    lines.append("")

    lines.append("## Sintesi")
    for item in pack.get("sintesi", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Card studio")
    for card in pack.get("card_studio", []):
        lines.append(f"### {card['titolo']}")
        lines.append(f"**Messaggio chiave:** {card['messaggio_chiave']}")
        lines.append("")
        lines.append(f"**Spiegazione:** {card['spiegazione']}")
        lines.append("")
        lines.append(f"**Fonte testuale:** {card['fonte_testuale']}")
        lines.append("")

    lines.append("## Domande guida")
    for item in pack.get("domande_guida", []):
        lines.append(f"- **{item['domanda']}**")
        lines.append(f"  - {item['risposta_guida']}")
    lines.append("")

    lines.append("## Quiz")
    for idx, item in enumerate(pack.get("quiz", []), start=1):
        lines.append(f"{idx}. **{item['domanda']}**")
        for opt in item["opzioni"]:
            lines.append(f"   - {opt}")
        lines.append(f"   _Spiegazione:_ {item['spiegazione']}")
    lines.append("")

    lines.append("## Glossario")
    for item in pack.get("glossario", []):
        lines.append(f"- **{item['termine']}**: {item['definizione_operativa']}")
    lines.append("")

    lines.append("## Piano ripasso")
    for item in pack.get("piano_ripasso", []):
        lines.append(f"- **{item['fase']}**: {item['attivita']} Concetti: {item['concetti_da_ripassare']}")
    lines.append("")

    return "\n".join(lines)


def run_cli() -> int:
    parser = argparse.ArgumentParser(description="Genera Study Pack Universale V4 da un documento testuale.")
    parser.add_argument("--input", required=True, help="File TXT/MD sorgente.")
    parser.add_argument("--out-json", required=True, help="Percorso output JSON.")
    parser.add_argument("--out-md", required=False, help="Percorso output Markdown.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERRORE: file input non trovato: {input_path}", file=sys.stderr)
        return 2

    raw = input_path.read_text(encoding="utf-8", errors="replace")
    pack = build_study_pack(raw, source_name=input_path.name)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.out_md:
        out_md = Path(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(pack), encoding="utf-8")

    if pack.get("status") == "QUALITY_BLOCKED":
        print("QUALITY_BLOCKED")
        for error in pack.get("quality_errors", []):
            print(f"- {error}")
        return 1

    print("OK")
    print(f"JSON: {out_json}")
    if args.out_md:
        print(f"MD: {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
