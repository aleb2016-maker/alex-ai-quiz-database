#!/usr/bin/env python3
"""
Mini LLM Fast Q&A + Summary Current.

Versione: V1 diagnostica/stabile.
Base: current V3.15 Extended Safe Decoder.

Cosa fa:
- carica gli output validati V3.15;
- costruisce un indice lessicale leggero in memoria;
- risponde rapidamente a domande simili ai concetti indicizzati;
- genera un riassunto extractive breve usando le frasi migliori.

Limiti:
- non è ancora un LLM generativo libero;
- non legge ancora PDF lunghi;
- non fa ancora chunking documentale completo;
- usa solo il materiale validato current.
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "ma", "che", "del", "della", "dei", "degli",
    "delle", "al", "allo", "alla", "ai", "agli", "alle",
    "è", "sono", "essere", "può", "possono", "deve", "devono",
    "cosa", "come", "perché", "quando", "quale", "quali",
    "mi", "spiega", "spiegami", "dimmi", "serve", "servono",
    "significa", "vuol", "dire",
}


def normalize(text: str) -> str:
    return " ".join(str(text).lower().strip().split())


def tokenize(text: str) -> List[str]:
    text = normalize(text)
    raw = re.findall(r"[a-zàèéìòù0-9']+", text, flags=re.IGNORECASE)
    return [tok for tok in raw if len(tok) > 2 and tok not in STOPWORDS]


@dataclass(frozen=True)
class KnowledgeItem:
    prompt: str
    output: str
    source_sentence: str
    tokens: Tuple[str, ...]


class FastQASummaryEngine:
    def __init__(self, items: List[KnowledgeItem]) -> None:
        self.items = items
        self.index: Dict[str, List[int]] = {}
        self.idf: Dict[str, float] = {}
        self._build_index()

    @classmethod
    def from_current_outputs(cls, root: Path) -> "FastQASummaryEngine":
        outputs_path = (
            root
            / "mini_llm/data/inference_v315_extended_safe_decoder/"
            / "inference_engine_v315_extended_safe_decoder_outputs.json"
        )

        if not outputs_path.exists():
            raise FileNotFoundError(f"Output current V3.15 non trovato: {outputs_path}")

        data = json.loads(outputs_path.read_text(encoding="utf-8"))
        items: List[KnowledgeItem] = []

        for row in data:
            if row.get("status") != "OK":
                continue

            prompt = str(row.get("prompt", "")).strip()
            output = str(row.get("output", "")).strip()
            source = str(row.get("source_sentence", "")).strip()

            if not prompt or not output:
                continue

            token_set = tuple(sorted(set(tokenize(prompt + " " + output + " " + source))))

            items.append(
                KnowledgeItem(
                    prompt=prompt,
                    output=output,
                    source_sentence=source,
                    tokens=token_set,
                )
            )

        return cls(items)

    def _build_index(self) -> None:
        doc_count = max(1, len(self.items))
        df: Dict[str, int] = {}

        for idx, item in enumerate(self.items):
            for token in item.tokens:
                self.index.setdefault(token, []).append(idx)
                df[token] = df.get(token, 0) + 1

        self.idf = {
            token: math.log((doc_count + 1) / (count + 1)) + 1.0
            for token, count in df.items()
        }

    def _score_item(self, query_tokens: List[str], item: KnowledgeItem) -> float:
        if not query_tokens:
            return 0.0

        item_tokens = set(item.tokens)
        score = 0.0

        prompt_norm = normalize(item.prompt)
        output_norm = normalize(item.output)

        for token in query_tokens:
            if token in item_tokens:
                score += self.idf.get(token, 1.0)

            if token in prompt_norm:
                score += 1.25

            if token in output_norm:
                score += 0.25

        # Bonus per match frase-concetto diretto.
        q_norm = normalize(" ".join(query_tokens))
        if q_norm and q_norm in prompt_norm:
            score += 5.0

        return score

    def ask(self, question: str, top_k: int = 3) -> Dict[str, object]:
        start = time.perf_counter()

        query_tokens = tokenize(question)
        candidate_ids = set()

        for token in query_tokens:
            candidate_ids.update(self.index.get(token, []))

        if not candidate_ids:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return {
                "status": "NO_MATCH",
                "question": question,
                "answer": "",
                "matches": [],
                "elapsed_ms": elapsed_ms,
            }

        scored: List[Tuple[float, KnowledgeItem]] = []

        for idx in candidate_ids:
            item = self.items[idx]
            score = self._score_item(query_tokens, item)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)

        best = scored[:top_k]

        if not best:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return {
                "status": "NO_MATCH",
                "question": question,
                "answer": "",
                "matches": [],
                "elapsed_ms": elapsed_ms,
            }

        answer = best[0][1].output

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return {
            "status": "OK",
            "question": question,
            "answer": answer,
            "matches": [
                {
                    "score": round(score, 4),
                    "prompt": item.prompt,
                    "output": item.output,
                }
                for score, item in best
            ],
            "elapsed_ms": elapsed_ms,
        }

    def summarize(self, max_items: int = 8) -> Dict[str, object]:
        start = time.perf_counter()

        # Ordine semplice ma stabile: privilegia frasi informative, non troppo corte.
        ranked = sorted(
            self.items,
            key=lambda item: (
                len(tokenize(item.output)),
                len(item.output),
            ),
            reverse=True,
        )

        selected: List[str] = []
        seen = set()

        for item in ranked:
            out = item.output.strip()
            key = normalize(out)
            if key in seen:
                continue
            seen.add(key)
            selected.append(out)
            if len(selected) >= max_items:
                break

        summary = " ".join(selected)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return {
            "status": "OK" if summary else "EMPTY",
            "summary": summary,
            "items_used": len(selected),
            "elapsed_ms": elapsed_ms,
        }


def main() -> int:
    root = Path(__file__).resolve().parents[3]

    engine = FastQASummaryEngine.from_current_outputs(root)

    questions = [
        "Che cosa fa il phishing?",
        "A cosa serve un backup?",
        "Come funziona l'autenticazione a due fattori?",
        "Che cos'è il ransomware?",
        "Perché sono importanti gli aggiornamenti software?",
        "Che cosa sono i dati sensibili?",
        "Come si proteggono le credenziali rubate?",
        "Che cosa fa un password manager?",
    ]

    results = [engine.ask(q) for q in questions]
    summary = engine.summarize(max_items=6)

    payload = {
        "engine": "fast_qa_summary_current",
        "base_engine": "inference_engine_v315_extended_safe_decoder",
        "items_loaded": len(engine.items),
        "questions": results,
        "summary": summary,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    failed = [
        row for row in results
        if row.get("status") != "OK" or not str(row.get("answer", "")).strip()
    ]

    if failed:
        return 1

    if summary.get("status") != "OK":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
