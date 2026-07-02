#!/usr/bin/env python3
"""
Mini LLM Study Pack V2 Quality.

Migliora V1 senza romperla:
- domande più naturali in italiano;
- titoli card meno meccanici;
- test con risposta corretta non sempre in posizione 0;
- quality gate interno contro domande brutte;
- generazione ancora ultra rapida.

Base:
- riusa Mini LLM Study Pack V1;
- riusa runtime documentale/cache;
- non usa modelli locali lenti;
- non inventa fuori dal documento.

Limiti:
- è ancora structured/extractive, non LLM neurale generativo;
- la qualità dipende dalla chiarezza del documento;
- il prossimo step potrà collegarlo alla CLI e poi al livello LLM vero.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List


ARTICLES = {
    "il",
    "lo",
    "la",
    "i",
    "gli",
    "le",
    "un",
    "uno",
    "una",
}


VERB_PATTERNS = [
    (" possono contenere ", "Che cosa possono contenere {subject}?"),
    (" può contenere ", "Che cosa può contenere {subject}?"),
    (" contengono ", "Che cosa contengono {subject}?"),
    (" contiene ", "Che cosa contiene {subject}?"),
    (" servono a ", "A cosa servono {subject}?"),
    (" serve a ", "A cosa serve {subject}?"),
    (" protegge ", "Che cosa protegge {subject}?"),
    (" rafforza ", "Che cosa rafforza {subject}?"),
    (" usa ", "Che cosa usa {subject}?"),
    (" aiuta a ", "A cosa aiuta {subject}?"),
    (" aiutano a ", "A cosa aiutano {subject}?"),
    (" riduce ", "Che cosa riduce {subject}?"),
    (" correggono ", "Che cosa correggono {subject}?"),
    (" corregge ", "Che cosa corregge {subject}?"),
    (" è un ", "Che cos'è {subject}?"),
    (" è una ", "Che cos'è {subject}?"),
    (" sono ", "Che cosa sono {subject}?"),
    (" possono ", "Che cosa possono fare {subject}?"),
    (" può ", "Che cosa può fare {subject}?"),
]


BAD_QUESTION_FRAGMENTS = [
    "che cosa protegge sicurezza",
    "che cosa usa phishing",
    "che cosa rafforza l'autenticazione",
    "che cosa rafforza L'autenticazione",
    "qual è il punto chiave su",
    "possono causare documenti",
    "usa phishing",
    "protegge sicurezza",
]


TITLE_BAD_WORDS = {
    "recuperare",
    "protegge",
    "rafforza",
    "convincere",
    "fornire",
    "riduce",
    "correggono",
    "corregge",
    "contenere",
    "contengono",
    "servono",
    "serve",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_v1_module():
    root = repo_root()
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_v1.py"

    if not path.exists():
        raise FileNotFoundError(f"Study Pack V1 non trovato: {path}")

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_v1", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare Study Pack V1: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def normalize(text: str) -> str:
    return " ".join(str(text).replace("\u00a0", " ").strip().split())


def strip_page_prefix(text: str) -> str:
    return re.sub(r"^\[Pagina\s+\d+\]\s*", "", normalize(text), flags=re.IGNORECASE)


def sentence_case(text: str) -> str:
    text = normalize(text)

    if not text:
        return text

    return text[0].upper() + text[1:]


def lowercase_first_for_question(text: str) -> str:
    text = normalize(text)

    if not text:
        return text

    words = text.split()

    if not words:
        return text

    first = words[0]

    if first.lower() in ARTICLES:
        words[0] = first.lower()
        return " ".join(words)

    if first.startswith("L'") or first.startswith("L’"):
        words[0] = "l'" + first[2:]
        return " ".join(words)

    return text[0].lower() + text[1:]


def strip_leading_article(text: str) -> str:
    text = normalize(text)

    text = re.sub(r"^(il|lo|la|i|gli|le|un|uno|una)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^l['’]", "", text, flags=re.IGNORECASE)

    return normalize(text)


def extract_subject(sentence: str) -> str:
    s = strip_page_prefix(sentence)
    low = s.lower()

    best_index = None

    for marker, _template in VERB_PATTERNS:
        idx = low.find(marker)

        if idx <= 0:
            continue

        if best_index is None or idx < best_index:
            best_index = idx

    if best_index is None:
        words = s.split()
        return " ".join(words[: min(5, len(words))])

    return normalize(s[:best_index])


def natural_title(sentence: str) -> str:
    subject = strip_leading_article(extract_subject(sentence))

    if not subject:
        return "Concetto chiave"

    words = subject.split()
    cleaned_words = []

    for word in words:
        raw = word.strip(" ,.;:!?").lower()

        if raw in TITLE_BAD_WORDS:
            continue

        cleaned_words.append(word.strip(" ,.;:!?"))

        if len(cleaned_words) >= 5:
            break

    if not cleaned_words:
        cleaned_words = words[:4]

    title = " ".join(cleaned_words)
    return sentence_case(title)


def natural_question(sentence: str) -> str:
    s = strip_page_prefix(sentence)
    low = s.lower()

    for marker, template in VERB_PATTERNS:
        idx = low.find(marker)

        if idx <= 0:
            continue

        subject = s[:idx].strip()
        subject = lowercase_first_for_question(subject)

        if not subject:
            continue

        question = template.format(subject=subject)
        question = normalize(question)

        if not question.endswith("?"):
            question += "?"

        return sentence_case(question)

    title = natural_title(s).lower()
    return f"Quale informazione importante viene data su {title}?"


def is_bad_question(question: str) -> bool:
    q = normalize(question)
    low = q.lower()

    if not q.endswith("?"):
        return True

    if len(q.split()) < 5:
        return True

    if "  " in q:
        return True

    for fragment in BAD_QUESTION_FRAGMENTS:
        if fragment.lower() in low:
            return True

    return False


def compact_answer(sentence: str, max_words: int = 36) -> str:
    text = strip_page_prefix(sentence)
    words = text.split()

    if len(words) <= max_words:
        return text

    return " ".join(words[:max_words]).rstrip(",;:") + "."


def make_keywords(sentence: str, max_keywords: int = 5) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", sentence.lower())

    blocked = {
        "della",
        "delle",
        "degli",
        "alla",
        "allo",
        "agli",
        "alle",
        "come",
        "cosa",
        "sono",
        "essere",
        "attraverso",
        "questo",
        "questa",
        "quello",
        "quella",
        "serve",
        "servono",
        "possono",
        "devono",
        "viene",
        "vengono",
        "senza",
        "tutte",
        "oltre",
        "durante",
    }

    result = []

    for word in words:
        if len(word) <= 3:
            continue
        if word in blocked:
            continue
        if word not in result:
            result.append(word)
        if len(result) >= max_keywords:
            break

    return result


class MiniLLMStudyPackV2Quality:
    def __init__(self, text: str, max_words_per_chunk: int = 90) -> None:
        self.v1_module = load_v1_module()
        self.v1_engine = self.v1_module.MiniLLMStudyPackV1(
            text,
            max_words_per_chunk=max_words_per_chunk,
        )

    def _ranked_sentences(self):
        return self.v1_engine._rank_sentences()

    def generate_summary(self, max_sentences: int = 8) -> Dict[str, object]:
        return self.v1_engine.generate_summary(max_sentences=max_sentences)

    def generate_cards(self, max_cards: int = 6) -> List[Dict[str, object]]:
        cards: List[Dict[str, object]] = []

        for row in self._ranked_sentences():
            if len(cards) >= max_cards:
                break

            title = natural_title(row.sentence)
            message = compact_answer(row.sentence, max_words=34)
            keywords = make_keywords(row.sentence, max_keywords=5)

            cards.append(
                {
                    "type": "study_card",
                    "title": title,
                    "message": message,
                    "bullets": [
                        f"Da ricordare: {message}",
                        f"Perché conta: {title} è un punto centrale del documento.",
                        f"Parole guida: {', '.join(keywords) if keywords else title.lower()}",
                    ],
                    "source_sentence": row.sentence,
                }
            )

        return cards

    def generate_qa(self, max_questions: int = 8) -> List[Dict[str, object]]:
        qas: List[Dict[str, object]] = []
        seen = set()

        for row in self._ranked_sentences():
            if len(qas) >= max_questions:
                break

            question = natural_question(row.sentence)

            if is_bad_question(question):
                continue

            key = question.lower()

            if key in seen:
                continue

            seen.add(key)

            qas.append(
                {
                    "question": question,
                    "answer": compact_answer(row.sentence, max_words=38),
                    "source_sentence": row.sentence,
                }
            )

        return qas

    def generate_test(self, max_questions: int = 6) -> List[Dict[str, object]]:
        qas = self.generate_qa(max_questions=max_questions + 5)
        answers = [qa["answer"] for qa in qas]

        test: List[Dict[str, object]] = []

        for index, qa in enumerate(qas):
            if len(test) >= max_questions:
                break

            correct = qa["answer"]

            distractors: List[str] = []

            for candidate in answers:
                if candidate == correct:
                    continue
                if candidate in distractors:
                    continue
                distractors.append(candidate)
                if len(distractors) >= 3:
                    break

            if len(distractors) < 3:
                continue

            correct_index = index % 4
            options = distractors[:3]
            options.insert(correct_index, correct)

            test.append(
                {
                    "question": qa["question"],
                    "options": options,
                    "correct_index": correct_index,
                    "answer": correct,
                    "explanation": f"La risposta corretta è: {correct}",
                    "source_sentence": qa["source_sentence"],
                }
            )

        return test

    def generate_pack(
        self,
        max_summary_sentences: int = 8,
        max_cards: int = 6,
        max_qas: int = 8,
        max_test_questions: int = 6,
    ) -> Dict[str, object]:
        start = time.perf_counter()

        summary = self.generate_summary(max_sentences=max_summary_sentences)
        cards = self.generate_cards(max_cards=max_cards)
        qas = self.generate_qa(max_questions=max_qas)
        test = self.generate_test(max_questions=max_test_questions)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        quality_errors = []

        for qa in qas:
            if is_bad_question(qa.get("question", "")):
                quality_errors.append(f"bad_question:{qa.get('question')}")

        correct_indexes = [item.get("correct_index") for item in test]

        if len(set(correct_indexes)) < 2:
            quality_errors.append("test_correct_index_not_mixed")

        status = "OK"

        if summary.get("status") != "OK":
            status = "EMPTY"

        if not cards or not qas or not test:
            status = "PARTIAL"

        if quality_errors:
            status = "QUALITY_FAIL"

        return {
            "engine": "mini_llm_study_pack_v2_quality",
            "status": status,
            "elapsed_ms": elapsed_ms,
            "quality_errors": quality_errors,
            "summary": summary,
            "cards": cards,
            "qas": qas,
            "test": test,
            "counts": {
                "summary_sentences": summary.get("sentences_used", 0),
                "cards": len(cards),
                "qas": len(qas),
                "test_questions": len(test),
            },
            "limits": [
                "V2 structured/extractive, non LLM neurale generativo.",
                "Migliora domande, card e test rispetto a V1.",
                "Non inventa fuori dal documento.",
                "Il prossimo step potrà collegarlo alla CLI e poi a LLM generativo controllato.",
            ],
        }


def generate_study_pack(text: str) -> Dict[str, object]:
    return MiniLLMStudyPackV2Quality(text).generate_pack()


def main() -> int:
    sample = """
    La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
    Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
    I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
    L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
    Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
    Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
    Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
    Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
    Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.
    I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.
    """

    result = generate_study_pack(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result.get("status") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
