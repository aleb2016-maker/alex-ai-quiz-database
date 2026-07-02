#!/usr/bin/env python3
"""
Mini LLM Study Pack V3 Quality Gate.

Migliora V2:
- card più didattiche;
- opzioni test più corte e leggibili;
- test studente senza risposta corretta visibile;
- answer key separata interna;
- quality gate più severo;
- generazione ancora ultra rapida.

Base:
- riusa Study Pack V2 Quality;
- non usa LLM locali lenti;
- non inventa fuori dal documento.

Limiti:
- ancora structured/extractive;
- non è ancora LLM neurale generativo;
- PDF scannerizzati/OCR esclusi.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List


BAD_QUESTION_FRAGMENTS = [
    "che cosa protegge sicurezza",
    "che cosa usa phishing",
    "che cosa rafforza l'autenticazione",
    "qual è il punto chiave su",
    "possono causare documenti",
]


BAD_CARD_PHRASES = [
    "è un punto centrale del documento",
    "punto chiave su",
]


TEST_CORRECT_INDEX_SEQUENCE = [1, 3, 0, 2]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_v2_module():
    root = repo_root()
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_v2_quality.py"

    if not path.exists():
        raise FileNotFoundError(f"Study Pack V2 non trovato: {path}")

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_v2_quality", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare Study Pack V2: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def normalize(text: str) -> str:
    return " ".join(str(text).replace("\u00a0", " ").strip().split())


def strip_page_prefix(text: str) -> str:
    return re.sub(r"^\[Pagina\s+\d+\]\s*", "", normalize(text), flags=re.IGNORECASE)


def capitalize_first(text: str) -> str:
    text = normalize(text)

    if not text:
        return text

    return text[0].upper() + text[1:]


def word_limit(text: str, max_words: int = 16) -> str:
    text = normalize(text).rstrip(" ,;:")

    words = text.split()

    if len(words) <= max_words:
        if not text.endswith("."):
            text += "."
        return text

    return " ".join(words[:max_words]).rstrip(" ,;:") + "."


def remove_leading_article(text: str) -> str:
    text = normalize(text)
    text = re.sub(r"^(il|lo|la|i|gli|le|un|uno|una)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^l['’]", "", text, flags=re.IGNORECASE)
    return normalize(text)


def compact_option_from_sentence(sentence: str) -> str:
    s = strip_page_prefix(sentence)
    low = s.lower()

    patterns = [
        (" servono a ", ""),
        (" serve a ", ""),
        (" protegge ", "Proteggere "),
        (" rafforza ", "Rafforzare "),
        (" usa ", "Usare "),
        (" aiuta a ", ""),
        (" aiutano a ", "Aiutare a "),
        (" riduce ", "Ridurre "),
        (" correggono ", "Correggere "),
        (" corregge ", "Correggere "),
        (" possono contenere ", "Contenere "),
        (" può contenere ", "Contenere "),
        (" contengono ", "Contenere "),
        (" contiene ", "Contenere "),
        (" hanno ", "Avere "),
        (" ha ", "Avere "),
        (" è un ", "Essere un "),
        (" è una ", "Essere una "),
    ]

    for marker, prefix in patterns:
        idx = low.find(marker)

        if idx <= 0:
            continue

        after = s[idx + len(marker):].strip(" .")
        option = prefix + after
        option = capitalize_first(option)
        return word_limit(option, max_words=16)

    return word_limit(s, max_words=16)


def compact_answer(sentence: str, max_words: int = 34) -> str:
    return word_limit(strip_page_prefix(sentence), max_words=max_words)


def quality_question_ok(question: str) -> bool:
    q = normalize(question)
    low = q.lower()

    if not q.endswith("?"):
        return False

    if len(q.split()) < 5:
        return False

    for fragment in BAD_QUESTION_FRAGMENTS:
        if fragment in low:
            return False

    return True


def option_quality_ok(option: str) -> bool:
    option = normalize(option)

    if not option:
        return False

    if len(option.split()) > 18:
        return False

    if option.endswith("?"):
        return False

    return True


class MiniLLMStudyPackV3QualityGate:
    def __init__(self, text: str, max_words_per_chunk: int = 90) -> None:
        self.v2_module = load_v2_module()
        self.v2_engine = self.v2_module.MiniLLMStudyPackV2Quality(
            text,
            max_words_per_chunk=max_words_per_chunk,
        )

    def generate_summary(self, max_sentences: int = 8) -> Dict[str, object]:
        return self.v2_engine.generate_summary(max_sentences=max_sentences)

    def generate_cards(self, max_cards: int = 6) -> List[Dict[str, object]]:
        v2_cards = self.v2_engine.generate_cards(max_cards=max_cards)
        cards: List[Dict[str, object]] = []

        for card in v2_cards:
            source = str(card.get("source_sentence") or card.get("message") or "")
            title = str(card.get("title") or "Concetto chiave").strip()
            message = compact_answer(source, max_words=34)
            keywords = self.v2_module.make_keywords(source, max_keywords=5)

            cards.append(
                {
                    "type": "study_card_v3",
                    "title": title,
                    "message": message,
                    "bullets": [
                        f"Idea chiave: {title}.",
                        f"Cosa ricordare: {message}",
                        f"Parole guida: {', '.join(keywords) if keywords else title.lower()}.",
                    ],
                    "source_sentence": source,
                }
            )

        return cards

    def generate_qa(self, max_questions: int = 8) -> List[Dict[str, object]]:
        v2_qas = self.v2_engine.generate_qa(max_questions=max_questions + 4)
        qas: List[Dict[str, object]] = []
        seen = set()

        for qa in v2_qas:
            if len(qas) >= max_questions:
                break

            question = normalize(qa.get("question", ""))

            if not quality_question_ok(question):
                continue

            if question.lower() in seen:
                continue

            seen.add(question.lower())

            source = str(qa.get("source_sentence") or qa.get("answer") or "")

            qas.append(
                {
                    "question": question,
                    "answer": compact_answer(source, max_words=34),
                    "source_sentence": strip_page_prefix(source),
                }
            )

        return qas

    def generate_test(self, max_questions: int = 6) -> Dict[str, object]:
        qas = self.generate_qa(max_questions=max_questions + 5)

        candidate_options = []

        for qa in qas:
            option = compact_option_from_sentence(str(qa.get("source_sentence", "")))

            if option_quality_ok(option) and option not in candidate_options:
                candidate_options.append(option)

        internal_test: List[Dict[str, object]] = []
        student_test: List[Dict[str, object]] = []
        answer_key: List[Dict[str, object]] = []

        for index, qa in enumerate(qas):
            if len(internal_test) >= max_questions:
                break

            correct = compact_option_from_sentence(str(qa.get("source_sentence", "")))

            if correct not in candidate_options:
                continue

            distractors = []

            for candidate in candidate_options:
                if candidate == correct:
                    continue
                if candidate in distractors:
                    continue
                distractors.append(candidate)

                if len(distractors) >= 3:
                    break

            if len(distractors) < 3:
                continue

            correct_index = TEST_CORRECT_INDEX_SEQUENCE[index % len(TEST_CORRECT_INDEX_SEQUENCE)]

            options = distractors[:3]
            options.insert(correct_index, correct)

            if len(set(options)) != 4:
                continue

            if not all(option_quality_ok(option) for option in options):
                continue

            item_id = f"q{len(internal_test) + 1:02d}"

            internal_item = {
                "id": item_id,
                "question": qa["question"],
                "options": options,
                "correct_index": correct_index,
                "answer": correct,
                "explanation": (
                    "Per rispondere correttamente bisogna collegare la domanda "
                    f"alla frase del documento: {strip_page_prefix(str(qa.get('source_sentence', '')))}"
                ),
                "source_sentence": strip_page_prefix(str(qa.get("source_sentence", ""))),
            }

            student_item = {
                "id": item_id,
                "question": qa["question"],
                "options": options,
            }

            key_item = {
                "id": item_id,
                "correct_index": correct_index,
                "answer": correct,
                "explanation": internal_item["explanation"],
            }

            internal_test.append(internal_item)
            student_test.append(student_item)
            answer_key.append(key_item)

        return {
            "internal_test": internal_test,
            "student_test": student_test,
            "answer_key": answer_key,
        }

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
        test_payload = self.generate_test(max_questions=max_test_questions)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        internal_test = test_payload["internal_test"]
        student_test = test_payload["student_test"]
        answer_key = test_payload["answer_key"]

        quality_errors: List[str] = []

        if summary.get("status") != "OK":
            quality_errors.append("summary_not_ok")

        if len(cards) < max_cards:
            quality_errors.append("cards_not_enough")

        if len(qas) < max_qas:
            quality_errors.append("qas_not_enough")

        if len(student_test) < max_test_questions:
            quality_errors.append("student_test_not_enough")

        for qa in qas:
            if not quality_question_ok(str(qa.get("question", ""))):
                quality_errors.append(f"bad_question:{qa.get('question')}")

        for card in cards:
            blob = json.dumps(card, ensure_ascii=False).lower()

            for bad in BAD_CARD_PHRASES:
                if bad in blob:
                    quality_errors.append(f"bad_card_phrase:{bad}")

        correct_indexes = [item.get("correct_index") for item in internal_test]

        if len(set(correct_indexes)) < 3:
            quality_errors.append("correct_index_not_mixed_enough")

        for item in internal_test:
            options = item.get("options", [])

            if len(options) != 4:
                quality_errors.append(f"bad_option_count:{item.get('id')}")

            if len(set(options)) != 4:
                quality_errors.append(f"duplicate_options:{item.get('id')}")

            for option in options:
                if not option_quality_ok(str(option)):
                    quality_errors.append(f"bad_option:{option}")

            correct_index = item.get("correct_index")

            if correct_index not in [0, 1, 2, 3]:
                quality_errors.append(f"bad_correct_index:{item.get('id')}")

            elif options[correct_index] != item.get("answer"):
                quality_errors.append(f"correct_index_mismatch:{item.get('id')}")

        for item in student_test:
            forbidden = {"correct_index", "answer", "explanation", "source_sentence"}

            for key in forbidden:
                if key in item:
                    quality_errors.append(f"student_test_leaks_{key}:{item.get('id')}")

        status = "OK" if not quality_errors else "QUALITY_FAIL"

        return {
            "engine": "mini_llm_study_pack_v3_quality_gate",
            "status": status,
            "elapsed_ms": elapsed_ms,
            "quality_errors": quality_errors,
            "summary": summary,
            "cards": cards,
            "qas": qas,
            "test": internal_test,
            "student_test": student_test,
            "answer_key": answer_key,
            "counts": {
                "summary_sentences": summary.get("sentences_used", 0),
                "cards": len(cards),
                "qas": len(qas),
                "test_questions": len(internal_test),
                "student_test_questions": len(student_test),
            },
            "limits": [
                "V3 structured/extractive, non LLM neurale generativo.",
                "Test studente separato da answer key interna.",
                "Opzioni test rese più corte e leggibili.",
                "Non inventa fuori dal documento.",
            ],
        }


def generate_study_pack(text: str) -> Dict[str, object]:
    return MiniLLMStudyPackV3QualityGate(text).generate_pack()


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
    La formazione del personale riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano.
    Le procedure di sicurezza aiutano a gestire incidenti, accessi, backup, dispositivi e comunicazioni interne.
    """

    result = generate_study_pack(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result.get("status") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
