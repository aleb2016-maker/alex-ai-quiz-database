#!/usr/bin/env python3
"""
Mini LLM Long Document RAG V3.9.1 Semantic Repair Gate.

Fix rispetto al primo tentativo V3.9.1:
- non blocca più frasi corrette tipo "Il phishing della pagina 1 usa...";
- accetta domande corrette che iniziano con "Che cosa...", "Quale...", "A cosa...";
- usa sentence-safe chunking;
- evita frasi spezzate e fuse;
- mantiene abbastanza frasi su 500 pagine;
- passa allo Study Pack Current solo contesto pulito.

Linea:
- V3.8/V3.8.6 = gate semantico;
- V3.15 = current stabile;
- Study Pack Current V3 = output controllato;
- V3.9 = RAG lungo tecnico;
- V3.9.1 = semantic repair per RAG lungo.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


ENGINE_NAME = "mini_llm_long_document_rag_v391_semantic_repair"

BASELINE_LINEAGE = {
    "semantic_quality_line": "V3.8/V3.8.6",
    "current_engine": "V3.15 stable current",
    "study_pack_current": "Study Pack Current V3 Quality Gate",
    "output_modes": "Output Modes V1",
    "long_document_rag": "V3.9.1 Semantic Repair Gate",
}


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "dello", "della", "dei", "degli", "delle",
    "a", "ad", "al", "allo", "alla", "ai", "agli", "alle",
    "da", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
    "in", "nel", "nello", "nella", "nei", "negli", "nelle",
    "con", "su", "per", "tra", "fra", "e", "o", "ma", "che",
    "è", "sono", "essere", "come", "anche", "più", "meno",
    "questo", "questa", "questi", "queste", "quello", "quella",
    "può", "possono", "deve", "devono", "viene", "vengono",
}


BAD_STATEMENT_STARTS = {
    "della", "dello", "delle", "degli", "dei", "del",
    "pagina", "pagine",
    "e", "o", "ma", "per", "con", "tra", "fra",
}


GOOD_QUESTION_STARTS = {
    "che", "quale", "quali", "a", "perché", "come", "quando", "dove", "chi",
}


BAD_ENDINGS = {
    "alla", "allo", "alle", "agli", "al", "a", "di", "del", "della",
    "dello", "delle", "e", "o", "ma", "che", "con", "per", "tra", "fra",
}


@dataclass(frozen=True)
class PageBlock:
    page_number: int
    text: str
    word_count: int


@dataclass(frozen=True)
class SentenceBlock:
    sentence_id: int
    page_number: int
    text: str
    word_count: int
    tokens: Tuple[str, ...]
    exact_signature: str
    semantic_signature: str


@dataclass(frozen=True)
class ChunkBlock:
    chunk_id: int
    page_start: int
    page_end: int
    text: str
    word_count: int
    tokens: Tuple[str, ...]
    sentence_ids: Tuple[int, ...]


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    page_start: int
    page_end: int
    score: float
    text: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def normalize(text: str) -> str:
    return " ".join(str(text).replace("\u00a0", " ").strip().split())


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(text).lower())

    return [
        word
        for word in words
        if len(word) > 2 and word not in STOPWORDS
    ]


def split_sentences_raw(text: str) -> List[str]:
    text = normalize(text)

    if not text:
        return []

    raw = re.split(r"(?<=[.!?])\s+", text)
    return [normalize(sentence).strip(" -•") for sentence in raw if normalize(sentence).strip(" -•")]


def exact_signature(sentence: str) -> str:
    return normalize(sentence).lower()


def semantic_signature(sentence: str) -> str:
    text = normalize(sentence).lower()
    text = re.sub(r"\bpagina\s+\d+\b", "pagina #", text)
    text = re.sub(r"\b\d+\b", "#", text)
    return text


def first_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return re.sub(r"^[\"'“”‘’(\[]+", "", words[0]).lower().strip(".,;:!?")


def last_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return words[-1].lower().strip(".,;:!?\"'“”‘’)]}")


def is_complete_statement(sentence: str) -> bool:
    s = normalize(sentence)

    if not s:
        return False

    words = s.split()

    if len(words) < 7:
        return False

    if len(words) > 46:
        return False

    if not re.search(r"[.!]$", s):
        return False

    if first_word(s) in BAD_STATEMENT_STARTS:
        return False

    if last_word(s) in BAD_ENDINGS:
        return False

    # Blocca fusioni evidenti: due frasi finite incollate senza punteggiatura.
    if re.search(r"\b(dati|credenziali|backup|informazioni|password)\s+(Il|La|I|Gli|Le|Un|Una|L')\b", s):
        return False

    # Blocca frammenti che iniziano al centro della frase.
    if re.search(r"^(della|dello|delle|degli|dei|del|pagina)\s+", s.lower()):
        return False

    return True


def is_good_question(question: str) -> bool:
    q = normalize(question)

    if not q.endswith("?"):
        return False

    if len(q.split()) < 5:
        return False

    start = first_word(q)

    if start not in GOOD_QUESTION_STARTS:
        return False

    if re.search(r"^(della|dello|delle|degli|dei|del|pagina)\s+", q.lower()):
        return False

    if re.search(r"\b\?\s+\w+", q):
        return False

    return True


def semantic_gate_text(text: str, label: str) -> List[str]:
    errors: List[str] = []
    sentences = split_sentences_raw(text)

    if not sentences:
        errors.append(f"{label}:empty_or_no_sentences")
        return errors

    for sentence in sentences:
        if sentence.endswith("?"):
            if not is_good_question(sentence):
                errors.append(f"{label}:bad_question:{sentence[:140]}")
        else:
            if not is_complete_statement(sentence):
                errors.append(f"{label}:bad_sentence:{sentence[:140]}")

    return errors


def split_text_into_logical_pages(text: str, words_per_page: int = 320) -> List[PageBlock]:
    raw_text = str(text).strip()

    if not raw_text:
        return []

    markers = list(re.finditer(r"\[PAGE\s+(\d+)\]", raw_text, flags=re.IGNORECASE))

    if markers:
        pages: List[PageBlock] = []

        for index, marker in enumerate(markers):
            page_number = int(marker.group(1))
            start = marker.end()
            end = markers[index + 1].start() if index + 1 < len(markers) else len(raw_text)
            page_text = normalize(raw_text[start:end])

            if not page_text:
                continue

            pages.append(
                PageBlock(
                    page_number=page_number,
                    text=page_text,
                    word_count=len(page_text.split()),
                )
            )

        pages.sort(key=lambda page: page.page_number)

        return [
            PageBlock(
                page_number=index + 1,
                text=page.text,
                word_count=page.word_count,
            )
            for index, page in enumerate(pages)
        ]

    words = normalize(raw_text).split()
    pages = []

    for start in range(0, len(words), words_per_page):
        page_words = words[start:start + words_per_page]

        if not page_words:
            continue

        page_text = " ".join(page_words)

        pages.append(
            PageBlock(
                page_number=len(pages) + 1,
                text=page_text,
                word_count=len(page_words),
            )
        )

    return pages


def build_sentence_blocks(pages: Sequence[PageBlock]) -> List[SentenceBlock]:
    sentence_blocks: List[SentenceBlock] = []
    seen_exact = set()

    for page in pages:
        for raw_sentence in split_sentences_raw(page.text):
            sentence = normalize(raw_sentence)

            if not is_complete_statement(sentence):
                continue

            exact = exact_signature(sentence)

            if exact in seen_exact:
                continue

            seen_exact.add(exact)

            tokens = tuple(sorted(set(tokenize(sentence))))

            sentence_blocks.append(
                SentenceBlock(
                    sentence_id=len(sentence_blocks),
                    page_number=page.page_number,
                    text=sentence,
                    word_count=len(sentence.split()),
                    tokens=tokens,
                    exact_signature=exact,
                    semantic_signature=semantic_signature(sentence),
                )
            )

    return sentence_blocks


def build_sentence_safe_chunks(
    sentence_blocks: Sequence[SentenceBlock],
    max_words_per_chunk: int = 180,
    overlap_sentences: int = 1,
) -> List[ChunkBlock]:
    chunks: List[ChunkBlock] = []
    current: List[SentenceBlock] = []
    current_words = 0

    def flush_chunk() -> None:
        nonlocal current, current_words

        if not current:
            return

        text = " ".join(sentence.text for sentence in current)
        tokens = tuple(sorted(set(tokenize(text))))

        chunks.append(
            ChunkBlock(
                chunk_id=len(chunks),
                page_start=current[0].page_number,
                page_end=current[-1].page_number,
                text=text,
                word_count=sum(sentence.word_count for sentence in current),
                tokens=tokens,
                sentence_ids=tuple(sentence.sentence_id for sentence in current),
            )
        )

        if overlap_sentences > 0:
            current = current[-overlap_sentences:]
            current_words = sum(sentence.word_count for sentence in current)
        else:
            current = []
            current_words = 0

    for sentence in sentence_blocks:
        if current_words + sentence.word_count > max_words_per_chunk and current:
            flush_chunk()

        current.append(sentence)
        current_words += sentence.word_count

    if current:
        flush_chunk()

    return chunks


def idf_from_chunks(chunks: Sequence[ChunkBlock]) -> Dict[str, float]:
    document_frequency: Dict[str, int] = {}

    for chunk in chunks:
        for token in set(chunk.tokens):
            document_frequency[token] = document_frequency.get(token, 0) + 1

    total = max(1, len(chunks))

    return {
        token: math.log((1 + total) / (1 + frequency)) + 1.0
        for token, frequency in document_frequency.items()
    }


def load_study_pack_current():
    root = repo_root()
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_current.py"

    if not path.exists():
        raise FileNotFoundError(f"Study Pack Current non trovato: {path}")

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_current_for_v391", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare Study Pack Current: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


class MiniLLMLongDocumentRAGV391SemanticRepair:
    def __init__(
        self,
        text: str,
        words_per_page: int = 320,
        max_words_per_chunk: int = 180,
        overlap_sentences: int = 1,
    ) -> None:
        start = time.perf_counter()

        self.text = normalize(text)
        self.words_per_page = words_per_page
        self.max_words_per_chunk = max_words_per_chunk
        self.overlap_sentences = overlap_sentences

        self.pages = split_text_into_logical_pages(
            text,
            words_per_page=words_per_page,
        )

        self.sentences = build_sentence_blocks(self.pages)

        self.chunks = build_sentence_safe_chunks(
            self.sentences,
            max_words_per_chunk=max_words_per_chunk,
            overlap_sentences=overlap_sentences,
        )

        self.idf = idf_from_chunks(self.chunks)
        self.build_ms = (time.perf_counter() - start) * 1000.0

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def sentence_count(self) -> int:
        return len(self.sentences)

    @property
    def word_count(self) -> int:
        return sum(page.word_count for page in self.pages)

    def compression_targets(self) -> Dict[str, int]:
        pages = self.page_count

        return {
            "source_pages": pages,
            "quality_summary_pages_10_percent": max(1, math.ceil(pages * 0.10)),
            "brief_summary_pages_1_percent": max(1, math.ceil(pages * 0.01)),
        }

    def retrieve(self, query: str, top_k: int = 8) -> List[RetrievedChunk]:
        query_tokens = set(tokenize(query))

        if not query_tokens:
            return []

        results: List[RetrievedChunk] = []

        for chunk in self.chunks:
            chunk_tokens = set(chunk.tokens)
            overlap = query_tokens.intersection(chunk_tokens)

            if not overlap:
                continue

            score = sum(self.idf.get(token, 1.0) for token in overlap)
            score += len(overlap) * 0.25

            results.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    score=round(score, 6),
                    text=chunk.text,
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

    def answer_query(
        self,
        query: str,
        top_k: int = 8,
        max_sentences: int = 5,
    ) -> Dict[str, object]:
        start = time.perf_counter()

        retrieved = self.retrieve(query, top_k=top_k)
        query_tokens = set(tokenize(query))

        selected: List[Dict[str, object]] = []
        seen_semantic = set()

        for item in retrieved:
            for sentence in split_sentences_raw(item.text):
                if not is_complete_statement(sentence):
                    continue

                sentence_tokens = set(tokenize(sentence))
                overlap = sentence_tokens.intersection(query_tokens)

                if not overlap:
                    continue

                signature = semantic_signature(sentence)

                if signature in seen_semantic:
                    continue

                seen_semantic.add(signature)

                selected.append(
                    {
                        "page_start": item.page_start,
                        "page_end": item.page_end,
                        "score": round(sum(self.idf.get(token, 1.0) for token in overlap), 6),
                        "sentence": sentence,
                    }
                )

        selected.sort(key=lambda row: row["score"], reverse=True)
        selected = selected[:max_sentences]

        answer = " ".join(row["sentence"] for row in selected)
        quality_errors = semantic_gate_text(answer, "answer") if answer else ["answer:empty"]

        return {
            "status": "OK" if answer and not quality_errors else "QUALITY_FAIL",
            "query": query,
            "answer": answer,
            "sentences_used": len(selected),
            "quality_errors": quality_errors,
            "retrieved_chunks": [
                {
                    "chunk_id": item.chunk_id,
                    "page_start": item.page_start,
                    "page_end": item.page_end,
                    "score": item.score,
                }
                for item in retrieved
            ],
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        }

    def progressive_summary(
        self,
        quality_ratio: float = 0.10,
        brief_ratio: float = 0.01,
        sentences_per_quality_page: int = 10,
        sentences_per_brief_page: int = 8,
        max_quality_sentences: int = 160,
        max_brief_sentences: int = 40,
    ) -> Dict[str, object]:
        start = time.perf_counter()

        targets = self.compression_targets()

        quality_target_pages = max(1, math.ceil(self.page_count * quality_ratio))
        brief_target_pages = max(1, math.ceil(self.page_count * brief_ratio))

        quality_sentence_target = min(
            max_quality_sentences,
            max(8, quality_target_pages * sentences_per_quality_page),
        )

        brief_sentence_target = min(
            max_brief_sentences,
            max(4, brief_target_pages * sentences_per_brief_page),
        )

        ranked: List[Dict[str, object]] = []

        for sentence in self.sentences:
            tokens = set(sentence.tokens)

            if len(tokens) < 3:
                continue

            score = sum(self.idf.get(token, 1.0) for token in tokens)

            if 10 <= sentence.word_count <= 34:
                score += 3.0

            if sentence.word_count > 42:
                score -= 2.0

            ranked.append(
                {
                    "page_start": sentence.page_number,
                    "page_end": sentence.page_number,
                    "score": round(score, 6),
                    "sentence": sentence.text,
                }
            )

        ranked.sort(key=lambda row: row["score"], reverse=True)

        quality_rows = ranked[:quality_sentence_target]
        brief_rows = ranked[:brief_sentence_target]

        quality_summary = " ".join(row["sentence"] for row in quality_rows)
        brief_summary = " ".join(row["sentence"] for row in brief_rows)

        quality_errors = []
        quality_errors.extend(semantic_gate_text(quality_summary, "quality_summary"))
        quality_errors.extend(semantic_gate_text(brief_summary, "brief_summary"))

        return {
            "status": "OK" if quality_summary and brief_summary and not quality_errors else "QUALITY_FAIL",
            "targets": {
                **targets,
                "quality_sentence_target_used": quality_sentence_target,
                "brief_sentence_target_used": brief_sentence_target,
                "quality_ratio": quality_ratio,
                "brief_ratio": brief_ratio,
            },
            "quality_summary": quality_summary,
            "brief_summary": brief_summary,
            "quality_sentences": len(quality_rows),
            "brief_sentences": len(brief_rows),
            "quality_errors": quality_errors,
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        }

    def context_for_study_pack(
        self,
        query: str,
        top_k: int = 40,
        max_chars: int = 24000,
        max_sentences: int = 48,
    ) -> Dict[str, object]:
        retrieved = self.retrieve(query, top_k=top_k)

        selected_sentences: List[str] = []
        refs: List[Dict[str, object]] = []
        seen_semantic = set()
        total_chars = 0

        for item in retrieved:
            refs.append(
                {
                    "chunk_id": item.chunk_id,
                    "page_start": item.page_start,
                    "page_end": item.page_end,
                    "score": item.score,
                }
            )

            for sentence in split_sentences_raw(item.text):
                if not is_complete_statement(sentence):
                    continue

                signature = semantic_signature(sentence)

                if signature in seen_semantic:
                    continue

                seen_semantic.add(signature)

                if total_chars + len(sentence) > max_chars:
                    break

                selected_sentences.append(sentence)
                total_chars += len(sentence)

                if len(selected_sentences) >= max_sentences:
                    break

            if len(selected_sentences) >= max_sentences or total_chars >= max_chars:
                break

        context = " ".join(selected_sentences)
        quality_errors = semantic_gate_text(context, "context") if context else ["context:empty"]

        return {
            "status": "OK" if context and not quality_errors else "QUALITY_FAIL",
            "query": query,
            "context": context,
            "context_chars": len(context),
            "sentences": len(selected_sentences),
            "quality_errors": quality_errors,
            "references": refs,
        }

    def study_pack_from_query(
        self,
        query: str,
        top_k: int = 40,
        max_chars: int = 24000,
    ) -> Dict[str, object]:
        start = time.perf_counter()

        context_payload = self.context_for_study_pack(
            query=query,
            top_k=top_k,
            max_chars=max_chars,
        )

        if context_payload["status"] != "OK":
            return {
                "status": "NO_CONTEXT",
                "query": query,
                "context": context_payload,
                "study_pack": {},
                "elapsed_ms": (time.perf_counter() - start) * 1000.0,
            }

        current_module = load_study_pack_current()
        pack = current_module.generate_study_pack(str(context_payload["context"]))

        semantic_errors: List[str] = []

        for index, card in enumerate(pack.get("cards", [])):
            text = str(card.get("message", ""))

            if semantic_gate_text(text, f"study_pack:card_{index}"):
                semantic_errors.extend(semantic_gate_text(text, f"study_pack:card_{index}"))

        for index, qa in enumerate(pack.get("qas", [])):
            question = str(qa.get("question", ""))
            answer = str(qa.get("answer", ""))

            if not is_good_question(question):
                semantic_errors.append(f"study_pack:qa_{index}:bad_question:{question[:140]}")

            semantic_errors.extend(semantic_gate_text(answer, f"study_pack:qa_{index}:answer"))

        for index, item in enumerate(pack.get("student_test", [])):
            question = str(item.get("question", ""))

            if not is_good_question(question):
                semantic_errors.append(f"study_pack:test_{index}:bad_question:{question[:140]}")

            for option_index, option in enumerate(item.get("options", [])):
                option_text = str(option)

                # Le opzioni possono essere brevi, ma non devono essere spezzate o fuse.
                if len(option_text.split()) >= 7 and option_text.endswith("."):
                    semantic_errors.extend(
                        semantic_gate_text(
                            option_text,
                            f"study_pack:test_{index}:option_{option_index}",
                        )
                    )
                elif re.search(r"^(della|dello|delle|degli|dei|del|pagina)\s+", option_text.lower()):
                    semantic_errors.append(
                        f"study_pack:test_{index}:option_{option_index}:bad_start:{option_text[:140]}"
                    )

        status = "OK" if pack.get("status") == "OK" and not semantic_errors else "QUALITY_FAIL"

        return {
            "status": status,
            "query": query,
            "context": {
                "context_chars": context_payload["context_chars"],
                "sentences": context_payload["sentences"],
                "quality_errors": context_payload["quality_errors"],
                "references": context_payload["references"],
            },
            "study_pack": pack,
            "semantic_errors": semantic_errors,
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        }

    def diagnostics(self) -> Dict[str, object]:
        return {
            "engine": ENGINE_NAME,
            "lineage": BASELINE_LINEAGE,
            "status": "OK" if self.pages and self.chunks and self.sentences else "EMPTY",
            "pages": self.page_count,
            "words": self.word_count,
            "sentences": self.sentence_count,
            "chunks": self.chunk_count,
            "build_ms": self.build_ms,
            "words_per_page": self.words_per_page,
            "max_words_per_chunk": self.max_words_per_chunk,
            "overlap_sentences": self.overlap_sentences,
            "compression_targets": self.compression_targets(),
            "limits": [
                "V3.9.1 RAG lungo structured/extractive.",
                "Sentence-safe chunking.",
                "Semantic Repair Gate.",
                "Non ancora LLM neurale generativo.",
                "Non ancora OCR.",
            ],
        }


def build_long_document_rag(text: str) -> MiniLLMLongDocumentRAGV391SemanticRepair:
    return MiniLLMLongDocumentRAGV391SemanticRepair(text)


def main() -> int:
    sample = "\n".join(
        f"[PAGE {page}] "
        f"La sicurezza informatica nella pagina {page} protegge dati, account e sistemi aziendali. "
        f"I backup della pagina {page} servono a recuperare informazioni dopo guasti o errori. "
        f"Il phishing nella pagina {page} usa l'inganno per ottenere credenziali e dati sensibili. "
        f"Le procedure della pagina {page} aiutano a gestire incidenti, accessi e comunicazioni interne."
        for page in range(1, 21)
    )

    rag = build_long_document_rag(sample)

    result = {
        "diagnostics": rag.diagnostics(),
        "answer": rag.answer_query("Che cosa fa il phishing?", top_k=8),
        "summary": rag.progressive_summary(max_quality_sentences=20, max_brief_sentences=6),
        "study_pack": rag.study_pack_from_query("sicurezza phishing backup procedure credenziali", top_k=12),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    statuses = [
        result["diagnostics"]["status"],
        result["answer"]["status"],
        result["summary"]["status"],
        result["study_pack"]["status"],
    ]

    return 0 if all(status == "OK" for status in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
