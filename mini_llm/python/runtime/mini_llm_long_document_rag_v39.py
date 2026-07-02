#!/usr/bin/env python3
"""
Mini LLM Long Document RAG V3.9.

Prosegue dal filone mini LLM V3.8/V3.15.

Obiettivo:
- documenti lunghi fino a 500 pagine;
- chunking;
- indice RAG leggero;
- retrieval;
- risposta da domanda;
- riassunto progressivo;
- target 10% e 1%;
- contesto RAG vario per Study Pack Current V3.

Limiti:
- structured/extractive;
- non ancora LLM neurale generativo;
- no OCR;
- non genera ancora davvero 50 pagine finali di riassunto.
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


ENGINE_NAME = "mini_llm_long_document_rag_v39"

BASELINE_LINEAGE = {
    "semantic_quality_line": "V3.8/V3.8.6",
    "current_engine": "V3.15 stable current",
    "study_pack_current": "Study Pack Current V3 Quality Gate",
    "output_modes": "Output Modes V1",
    "long_document_rag": "V3.9",
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


@dataclass(frozen=True)
class PageBlock:
    page_number: int
    text: str
    word_count: int


@dataclass(frozen=True)
class ChunkBlock:
    chunk_id: int
    page_start: int
    page_end: int
    text: str
    word_count: int
    tokens: Tuple[str, ...]


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


def split_sentences(text: str) -> List[str]:
    text = normalize(text)

    if not text:
        return []

    raw = re.split(r"(?<=[.!?])\s+", text)
    sentences: List[str] = []

    for sentence in raw:
        cleaned = normalize(sentence).strip(" -•")

        if len(cleaned.split()) >= 6:
            sentences.append(cleaned)

    return sentences


def sentence_signature(sentence: str) -> str:
    """
    Deduplica frasi ripetute in pagine diverse.
    Esempio:
    'Il phishing della pagina 12 usa...' e
    'Il phishing della pagina 45 usa...'
    diventano la stessa firma.
    """
    text = normalize(sentence).lower()
    text = re.sub(r"\bpagina\s+\d+\b", "pagina #", text)
    text = re.sub(r"\b\d+\b", "#", text)
    return text


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


def build_chunks_from_pages(
    pages: Sequence[PageBlock],
    max_words_per_chunk: int = 180,
    overlap_words: int = 30,
) -> List[ChunkBlock]:
    chunks: List[ChunkBlock] = []
    current_words: List[str] = []
    current_page_start = 1
    current_page_end = 1
    safe_overlap = max(0, min(overlap_words, max_words_per_chunk // 2))

    def flush_chunk() -> None:
        nonlocal current_words, current_page_start, current_page_end

        if not current_words:
            return

        chunk_text = " ".join(current_words)
        tokens = tuple(sorted(set(tokenize(chunk_text))))

        chunks.append(
            ChunkBlock(
                chunk_id=len(chunks),
                page_start=current_page_start,
                page_end=current_page_end,
                text=chunk_text,
                word_count=len(current_words),
                tokens=tokens,
            )
        )

        if safe_overlap > 0:
            current_words = current_words[-safe_overlap:]
            current_page_start = current_page_end
        else:
            current_words = []

    for page in pages:
        page_words = page.text.split()

        if not current_words:
            current_page_start = page.page_number

        current_page_end = page.page_number

        for word in page_words:
            current_words.append(word)

            if len(current_words) >= max_words_per_chunk:
                flush_chunk()

    if current_words:
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

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_current_for_v39", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare Study Pack Current: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


class MiniLLMLongDocumentRAGV39:
    def __init__(
        self,
        text: str,
        words_per_page: int = 320,
        max_words_per_chunk: int = 180,
        overlap_words: int = 30,
    ) -> None:
        start = time.perf_counter()

        self.text = normalize(text)
        self.words_per_page = words_per_page
        self.max_words_per_chunk = max_words_per_chunk
        self.overlap_words = overlap_words

        self.pages = split_text_into_logical_pages(
            text,
            words_per_page=words_per_page,
        )

        self.chunks = build_chunks_from_pages(
            self.pages,
            max_words_per_chunk=max_words_per_chunk,
            overlap_words=overlap_words,
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
            score += len(overlap) * 0.20

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
        seen = set()

        for item in retrieved:
            for sentence in split_sentences(item.text):
                sentence_tokens = set(tokenize(sentence))
                overlap = sentence_tokens.intersection(query_tokens)

                if not overlap:
                    continue

                signature = sentence_signature(sentence)

                if signature in seen:
                    continue

                seen.add(signature)

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

        return {
            "status": "OK" if answer else "NO_MATCH",
            "query": query,
            "answer": answer,
            "sentences_used": len(selected),
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
        seen = set()

        for chunk in self.chunks:
            for sentence in split_sentences(chunk.text):
                signature = sentence_signature(sentence)

                if signature in seen:
                    continue

                seen.add(signature)

                tokens = set(tokenize(sentence))

                if len(tokens) < 3:
                    continue

                score = sum(self.idf.get(token, 1.0) for token in tokens)

                if 10 <= len(sentence.split()) <= 36:
                    score += 3.0

                if len(sentence.split()) > 60:
                    score -= 2.0

                ranked.append(
                    {
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "score": round(score, 6),
                        "sentence": sentence,
                    }
                )

        ranked.sort(key=lambda row: row["score"], reverse=True)

        quality_rows = ranked[:quality_sentence_target]
        brief_rows = ranked[:brief_sentence_target]

        quality_summary = " ".join(row["sentence"] for row in quality_rows)
        brief_summary = " ".join(row["sentence"] for row in brief_rows)

        return {
            "status": "OK" if quality_summary and brief_summary else "EMPTY",
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
        seen = set()
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

            for sentence in split_sentences(item.text):
                signature = sentence_signature(sentence)

                if signature in seen:
                    continue

                seen.add(signature)

                if total_chars + len(sentence) > max_chars:
                    break

                selected_sentences.append(sentence)
                total_chars += len(sentence)

                if len(selected_sentences) >= max_sentences:
                    break

            if len(selected_sentences) >= max_sentences or total_chars >= max_chars:
                break

        context = " ".join(selected_sentences)

        return {
            "status": "OK" if context else "NO_CONTEXT",
            "query": query,
            "context": context,
            "context_chars": len(context),
            "sentences": len(selected_sentences),
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

        return {
            "status": "OK" if pack.get("status") == "OK" else pack.get("status"),
            "query": query,
            "context": {
                "context_chars": context_payload["context_chars"],
                "sentences": context_payload["sentences"],
                "references": context_payload["references"],
            },
            "study_pack": pack,
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        }

    def diagnostics(self) -> Dict[str, object]:
        return {
            "engine": ENGINE_NAME,
            "lineage": BASELINE_LINEAGE,
            "status": "OK" if self.pages and self.chunks else "EMPTY",
            "pages": self.page_count,
            "words": self.word_count,
            "chunks": self.chunk_count,
            "build_ms": self.build_ms,
            "words_per_page": self.words_per_page,
            "max_words_per_chunk": self.max_words_per_chunk,
            "overlap_words": self.overlap_words,
            "compression_targets": self.compression_targets(),
            "limits": [
                "V3.9 RAG lungo structured/extractive.",
                "Non ancora LLM neurale generativo.",
                "Non ancora OCR.",
                "Non ancora generazione materiale finale completo da 50 pagine.",
            ],
        }


def build_long_document_rag(text: str) -> MiniLLMLongDocumentRAGV39:
    return MiniLLMLongDocumentRAGV39(text)


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
        "answer": rag.answer_query("Che cosa fa il phishing?", top_k=5),
        "summary": rag.progressive_summary(max_quality_sentences=20, max_brief_sentences=6),
        "study_pack": rag.study_pack_from_query("sicurezza phishing backup procedure credenziali", top_k=12),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result["diagnostics"]["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
