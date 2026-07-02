#!/usr/bin/env python3
"""
Fast Document Q&A + Summary V2 Cache.

Scopo:
- indicizzare testo documentale una sola volta;
- salvare cache persistente su disco;
- ricaricare rapidamente chunk, indice e idf;
- rispondere a domande successive senza ricostruire tutto;
- generare riassunto extractive veloce.

Limiti:
- non legge ancora PDF direttamente;
- non fa OCR;
- non produce ancora riassunto progressivo 10%/1%;
- Q&A e summary sono extractive, non generazione libera.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "ma", "che", "del", "della", "dei", "degli",
    "delle", "al", "allo", "alla", "ai", "agli", "alle",
    "è", "sono", "essere", "può", "possono", "deve", "devono",
    "cosa", "come", "perché", "quando", "quale", "quali",
    "mi", "spiega", "spiegami", "dimmi", "serve", "servono",
    "significa", "vuol", "dire", "questo", "questa", "questi",
    "quelle", "quello", "quella", "nel", "nella", "nelle",
    "sul", "sulla", "dagli", "dallo", "dalla",
}


def normalize(text: str) -> str:
    return " ".join(str(text).replace("\u00a0", " ").strip().split())


def normalize_low(text: str) -> str:
    return normalize(text).lower()


def tokenize(text: str) -> List[str]:
    raw = re.findall(r"[a-zàèéìòù0-9']+", normalize_low(text), flags=re.IGNORECASE)
    return [tok for tok in raw if len(tok) > 2 and tok not in STOPWORDS]


def split_sentences(text: str) -> List[str]:
    clean = normalize(text)

    if not clean:
        return []

    parts = re.split(r"(?<=[.!?])\s+", clean)
    sentences: List[str] = []

    for part in parts:
        part = part.strip()
        if len(part) < 8:
            continue
        sentences.append(part)

    return sentences


def document_hash(text: str, max_words_per_chunk: int) -> str:
    payload = f"{max_words_per_chunk}\n{normalize(text)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: int
    text: str
    sentences: Tuple[str, ...]
    tokens: Tuple[str, ...]


class FastDocumentQASummaryCache:
    def __init__(
        self,
        chunks: List[DocumentChunk],
        index: Dict[str, List[int]] | None = None,
        idf: Dict[str, float] | None = None,
        cache_key: str = "",
    ) -> None:
        self.chunks = chunks
        self.index: Dict[str, List[int]] = index or {}
        self.idf: Dict[str, float] = idf or {}
        self.cache_key = cache_key

        if not self.index or not self.idf:
            self._build_index()

    @classmethod
    def from_text(cls, text: str, max_words_per_chunk: int = 90) -> "FastDocumentQASummaryCache":
        sentences = split_sentences(text)
        chunks: List[DocumentChunk] = []

        current_sentences: List[str] = []
        current_words = 0

        def flush() -> None:
            nonlocal current_sentences, current_words

            if not current_sentences:
                return

            chunk_text = " ".join(current_sentences)
            token_set = tuple(sorted(set(tokenize(chunk_text))))
            chunks.append(
                DocumentChunk(
                    chunk_id=len(chunks),
                    text=chunk_text,
                    sentences=tuple(current_sentences),
                    tokens=token_set,
                )
            )
            current_sentences = []
            current_words = 0

        for sentence in sentences:
            word_count = len(sentence.split())

            if current_sentences and current_words + word_count > max_words_per_chunk:
                flush()

            current_sentences.append(sentence)
            current_words += word_count

        flush()

        return cls(chunks, cache_key=document_hash(text, max_words_per_chunk))

    @classmethod
    def from_text_with_cache(
        cls,
        text: str,
        cache_dir: Path,
        max_words_per_chunk: int = 90,
    ) -> Tuple["FastDocumentQASummaryCache", Dict[str, object]]:
        cache_dir.mkdir(parents=True, exist_ok=True)

        key = document_hash(text, max_words_per_chunk)
        cache_path = cache_dir / f"{key}.json"

        start = time.perf_counter()

        if cache_path.exists():
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            chunks = [
                DocumentChunk(
                    chunk_id=int(row["chunk_id"]),
                    text=str(row["text"]),
                    sentences=tuple(row["sentences"]),
                    tokens=tuple(row["tokens"]),
                )
                for row in payload["chunks"]
            ]

            engine = cls(
                chunks=chunks,
                index={str(k): [int(x) for x in v] for k, v in payload["index"].items()},
                idf={str(k): float(v) for k, v in payload["idf"].items()},
                cache_key=key,
            )

            elapsed_ms = (time.perf_counter() - start) * 1000.0

            return engine, {
                "cache_status": "HIT",
                "cache_key": key,
                "cache_path": str(cache_path),
                "elapsed_ms": elapsed_ms,
                "chunks": len(chunks),
            }

        engine = cls.from_text(text, max_words_per_chunk=max_words_per_chunk)
        engine.cache_key = key
        engine.save_cache(cache_path)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return engine, {
            "cache_status": "MISS_BUILT",
            "cache_key": key,
            "cache_path": str(cache_path),
            "elapsed_ms": elapsed_ms,
            "chunks": len(engine.chunks),
        }

    def save_cache(self, cache_path: Path) -> None:
        payload = {
            "version": "fast_document_qa_summary_v2_cache",
            "cache_key": self.cache_key,
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "sentences": list(chunk.sentences),
                    "tokens": list(chunk.tokens),
                }
                for chunk in self.chunks
            ],
            "index": self.index,
            "idf": self.idf,
        }

        cache_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _build_index(self) -> None:
        doc_count = max(1, len(self.chunks))
        df: Dict[str, int] = {}

        self.index = {}

        for idx, chunk in enumerate(self.chunks):
            for token in chunk.tokens:
                self.index.setdefault(token, []).append(idx)
                df[token] = df.get(token, 0) + 1

        self.idf = {
            token: math.log((doc_count + 1) / (count + 1)) + 1.0
            for token, count in df.items()
        }

    def _score_chunk(self, query_tokens: Sequence[str], chunk: DocumentChunk) -> float:
        if not query_tokens:
            return 0.0

        chunk_tokens = set(chunk.tokens)
        text_low = normalize_low(chunk.text)
        score = 0.0

        for token in query_tokens:
            if token in chunk_tokens:
                score += self.idf.get(token, 1.0)
            if token in text_low:
                score += 0.35

        return score

    def retrieve(self, question: str, top_k: int = 4) -> List[Tuple[float, DocumentChunk]]:
        query_tokens = tokenize(question)
        candidate_ids = set()

        for token in query_tokens:
            candidate_ids.update(self.index.get(token, []))

        scored: List[Tuple[float, DocumentChunk]] = []

        for idx in candidate_ids:
            chunk = self.chunks[idx]
            score = self._score_chunk(query_tokens, chunk)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:top_k]

    def _best_sentence(self, question: str, chunks: List[Tuple[float, DocumentChunk]]) -> str:
        query_tokens = tokenize(question)

        best_score = 0.0
        best_sentence = ""

        for _, chunk in chunks:
            for sentence in chunk.sentences:
                sent_tokens = set(tokenize(sentence))
                score = 0.0

                for token in query_tokens:
                    if token in sent_tokens:
                        score += self.idf.get(token, 1.0) + 0.5

                if len(sentence.split()) < 5:
                    score *= 0.4

                if score > best_score:
                    best_score = score
                    best_sentence = sentence

        return best_sentence

    def ask(self, question: str, top_k: int = 4) -> Dict[str, object]:
        start = time.perf_counter()

        matches = self.retrieve(question, top_k=top_k)
        answer = self._best_sentence(question, matches) if matches else ""

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return {
            "status": "OK" if answer else "NO_MATCH",
            "question": question,
            "answer": answer,
            "elapsed_ms": elapsed_ms,
            "matches": [
                {
                    "score": round(score, 4),
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                }
                for score, chunk in matches
            ],
        }

    def summarize(self, max_sentences: int = 8) -> Dict[str, object]:
        start = time.perf_counter()

        sentence_scores: List[Tuple[float, str]] = []

        for chunk in self.chunks:
            for sentence in chunk.sentences:
                tokens = tokenize(sentence)
                if len(tokens) < 4:
                    continue

                unique_tokens = set(tokens)
                score = sum(self.idf.get(tok, 1.0) for tok in unique_tokens)

                word_count = len(sentence.split())
                if 8 <= word_count <= 35:
                    score += 2.0
                if word_count > 45:
                    score -= 2.0

                sentence_scores.append((score, sentence))

        sentence_scores.sort(key=lambda pair: pair[0], reverse=True)

        selected: List[str] = []
        seen = set()

        for _, sentence in sentence_scores:
            key = normalize_low(sentence)
            if key in seen:
                continue
            seen.add(key)
            selected.append(sentence)
            if len(selected) >= max_sentences:
                break

        summary = " ".join(selected)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return {
            "status": "OK" if summary else "EMPTY",
            "summary": summary,
            "sentences_used": len(selected),
            "elapsed_ms": elapsed_ms,
        }


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    cache_dir = root / "mini_llm/data/fast_runtime/cache_v2"

    sample = """
    La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
    Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
    I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
    L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
    Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
    Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
    """

    engine, cache_info = FastDocumentQASummaryCache.from_text_with_cache(sample, cache_dir)
    result = engine.ask("Che cosa fa il phishing?")
    summary = engine.summarize(max_sentences=3)

    payload = {
        "engine": "fast_document_qa_summary_v2_cache",
        "cache_info": cache_info,
        "answer": result,
        "summary": summary,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if result.get("status") != "OK":
        return 1

    if summary.get("status") != "OK":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
