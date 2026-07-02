#!/usr/bin/env python3
"""
Mini LLM Study Pack V1.

Genera in modo veloce:
- riassunto;
- card studio;
- domande e risposte;
- test a scelta multipla.

Base:
- usa il runtime documentale fast_document_qa_summary_v2_cache;
- non usa modelli locali lenti;
- non usa fallback o frasi demo;
- lavora su frasi reali estratte dal documento.

Limiti:
- è V1 strutturata/extractive, non ancora LLM neurale generativo;
- qualità buona su documenti chiari e testuali;
- non inventa contenuti fuori dal documento;
- test e card sono generati da frasi reali del testo.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_document_runtime():
    root = repo_root()
    runtime_path = root / "mini_llm/python/runtime/fast_document_qa_summary_v2_cache.py"

    if not runtime_path.exists():
        raise FileNotFoundError(f"Runtime documentale non trovato: {runtime_path}")

    spec = importlib.util.spec_from_file_location(
        "fast_document_qa_summary_v2_cache",
        runtime_path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare runtime documentale: {runtime_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def normalize(text: str) -> str:
    return " ".join(str(text).replace("\u00a0", " ").strip().split())


def clean_sentence(sentence: str) -> str:
    sentence = normalize(sentence)
    sentence = re.sub(r"^\[Pagina\s+\d+\]\s*", "", sentence, flags=re.IGNORECASE)
    sentence = sentence.strip(" -•")
    return sentence


def sentence_key(sentence: str) -> str:
    return normalize(sentence).lower()


def safe_title(text: str) -> str:
    text = normalize(text)

    text = re.sub(r"^\[Pagina\s+\d+\]\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9' ]+", " ", text)

    words = [
        word.strip("'").lower()
        for word in text.split()
        if len(word.strip("'")) > 3
    ]

    blocked = {
        "della", "delle", "degli", "alla", "allo", "agli",
        "come", "cosa", "sono", "essere", "attraverso",
        "questo", "questa", "quello", "quella", "serve",
        "servono", "possono", "devono", "viene", "vengono",
    }

    selected = []

    for word in words:
        if word in blocked:
            continue
        if word not in selected:
            selected.append(word)
        if len(selected) >= 4:
            break

    if not selected:
        selected = words[:4]

    if not selected:
        return "Concetto chiave"

    return " ".join(selected).capitalize()


def compact_answer(sentence: str, max_words: int = 34) -> str:
    words = clean_sentence(sentence).split()

    if len(words) <= max_words:
        return clean_sentence(sentence)

    return " ".join(words[:max_words]).rstrip(",;:") + "."


@dataclass(frozen=True)
class RankedSentence:
    sentence: str
    score: float
    tokens: Tuple[str, ...]


class MiniLLMStudyPackV1:
    def __init__(self, text: str, max_words_per_chunk: int = 90) -> None:
        self.runtime = load_document_runtime()
        self.engine = self.runtime.FastDocumentQASummaryCache.from_text(
            text,
            max_words_per_chunk=max_words_per_chunk,
        )

    def _all_sentences(self) -> List[str]:
        sentences: List[str] = []
        seen = set()

        for chunk in self.engine.chunks:
            for sentence in chunk.sentences:
                cleaned = clean_sentence(sentence)

                if len(cleaned.split()) < 6:
                    continue

                key = sentence_key(cleaned)

                if key in seen:
                    continue

                seen.add(key)
                sentences.append(cleaned)

        return sentences

    def _rank_sentences(self) -> List[RankedSentence]:
        ranked: List[RankedSentence] = []

        for index, sentence in enumerate(self._all_sentences()):
            tokens = tuple(sorted(set(self.runtime.tokenize(sentence))))

            if len(tokens) < 3:
                continue

            word_count = len(sentence.split())
            score = sum(self.engine.idf.get(token, 1.0) for token in tokens)

            if 9 <= word_count <= 35:
                score += 4.0

            if word_count > 45:
                score -= 3.0

            if index < 4:
                score += 0.5

            ranked.append(RankedSentence(sentence=sentence, score=score, tokens=tokens))

        ranked.sort(key=lambda row: row.score, reverse=True)
        return ranked

    def generate_summary(self, max_sentences: int = 8) -> Dict[str, object]:
        start = time.perf_counter()

        selected: List[str] = []

        for row in self._rank_sentences():
            if len(selected) >= max_sentences:
                break
            selected.append(row.sentence)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return {
            "status": "OK" if selected else "EMPTY",
            "summary": " ".join(selected),
            "sentences_used": len(selected),
            "elapsed_ms": elapsed_ms,
        }

    def generate_cards(self, max_cards: int = 6) -> List[Dict[str, object]]:
        cards: List[Dict[str, object]] = []

        for row in self._rank_sentences():
            if len(cards) >= max_cards:
                break

            title = safe_title(row.sentence)
            message = compact_answer(row.sentence, max_words=32)

            detail_tokens = list(row.tokens[:6])
            detail = ", ".join(detail_tokens) if detail_tokens else title.lower()

            cards.append(
                {
                    "type": "study_card",
                    "title": title,
                    "message": message,
                    "bullets": [
                        f"Concetto: {title}",
                        f"Dettaglio chiave: {message}",
                        f"Parole guida: {detail}",
                    ],
                }
            )

        return cards

    def _make_question_from_sentence(self, sentence: str) -> str:
        s = clean_sentence(sentence)
        low = s.lower()

        patterns = [
            (" servono a ", "A cosa servono {subject}?"),
            (" serve a ", "A cosa serve {subject}?"),
            (" protegge ", "Che cosa protegge {subject}?"),
            (" rafforza ", "Che cosa rafforza {subject}?"),
            (" usa ", "Che cosa usa {subject}?"),
            (" possono ", "Che cosa possono causare {subject}?"),
            (" può ", "Che cosa può causare {subject}?"),
            (" contengono ", "Che cosa contengono {subject}?"),
            (" contiene ", "Che cosa contiene {subject}?"),
            (" è un ", "Che cos'è {subject}?"),
            (" è una ", "Che cos'è {subject}?"),
            (" sono ", "Che cosa sono {subject}?"),
        ]

        for marker, template in patterns:
            if marker in low:
                before = s[: low.index(marker)].strip()
                before = re.sub(r"^(il|lo|la|i|gli|le|un|uno|una)\s+", "", before, flags=re.IGNORECASE)
                subject = before.strip()

                if subject and len(subject.split()) <= 8:
                    return template.format(subject=subject)

        title = safe_title(s)
        return f"Qual è il punto chiave su {title.lower()}?"

    def generate_qa(self, max_questions: int = 8) -> List[Dict[str, object]]:
        qas: List[Dict[str, object]] = []
        seen_questions = set()

        for row in self._rank_sentences():
            if len(qas) >= max_questions:
                break

            question = self._make_question_from_sentence(row.sentence)
            answer = compact_answer(row.sentence, max_words=36)

            if not question.endswith("?"):
                question += "?"

            qkey = sentence_key(question)

            if qkey in seen_questions:
                continue

            seen_questions.add(qkey)

            qas.append(
                {
                    "question": question,
                    "answer": answer,
                    "source_sentence": row.sentence,
                }
            )

        return qas

    def generate_test(self, max_questions: int = 6) -> List[Dict[str, object]]:
        qas = self.generate_qa(max_questions=max_questions + 4)
        answers = [qa["answer"] for qa in qas]

        tests: List[Dict[str, object]] = []

        for index, qa in enumerate(qas):
            if len(tests) >= max_questions:
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

            options = [correct, *distractors[:3]]

            tests.append(
                {
                    "question": qa["question"],
                    "options": options,
                    "correct_index": 0,
                    "answer": correct,
                    "explanation": f"La risposta corretta deriva dal documento: {correct}",
                }
            )

        return tests

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

        status = "OK"

        if summary.get("status") != "OK":
            status = "EMPTY"

        if not cards or not qas or not test:
            status = "PARTIAL"

        return {
            "engine": "mini_llm_study_pack_v1",
            "status": status,
            "elapsed_ms": elapsed_ms,
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
                "V1 structured/extractive, non LLM neurale generativo.",
                "Non inventa fuori dal documento.",
                "Card, Q&A e test derivano da frasi reali del testo.",
                "Il prossimo step LLM userà questo pack come base controllata.",
            ],
        }


def generate_study_pack(text: str) -> Dict[str, object]:
    return MiniLLMStudyPackV1(text).generate_pack()


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
