from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


class KnowledgeDatasetBuilderV2Clean:
    """
    Dataset Builder V2 Clean.

    Scopo:
    creare un dataset più naturale per il mini LLM prima del training.

    Il Dataset V1 contiene anche strutture tecniche utili alla pipeline:
    - instruction
    - input
    - output
    - risposta
    - domanda
    - micro forma
    - testo con marcatori tipo '#'

    Quei token sono utili per dataset istruzionale, ma sporcano un piccolo
    modello generativo next-token. Questo builder crea un dataset V2 pulito
    separato, senza cancellare o modificare il V1.

    Output:
    - knowledge_dataset_v2_clean.jsonl
    - knowledge_dataset_v2_clean_train.jsonl
    - knowledge_dataset_v2_clean_val.jsonl
    - knowledge_dataset_v2_clean_test.jsonl
    - knowledge_dataset_v2_clean_manifest.json
    - report Markdown
    """

    DIRTY_TOKENS = {
        "#",
        "input",
        "output",
        "instruction",
        "istruzione",
        "risposta",
        "domanda",
        "question",
        "answer",
        "completion",
        "prompt",
        "trasforma",
        "riscrivi",
        "collegate",
        "micro",
        "forma",
        "area",
        "operativa",
        "pulite",
        "pulita",
        "complete",
        "completa",
        "analizzato",
        "richiesta",
        "richiesto",
        "source_task",
        "source_record",
        "record",
        "json",
    }

    DIRTY_PHRASES = {
        "area operativa",
        "micro forma",
        "in forma chiara",
        "frase chiara",
        "frase utile",
        "domanda studio",
        "risposta guida",
        "testo analizzato",
        "informazione operativa richiesta",
        "trasforma usando",
        "riscrivi usando",
        "per un riassunto",
        "quale informazione",
    }

    TECHNICAL_FIELD_NAMES = {
        "instruction",
        "istruzione",
        "input",
        "output",
        "prompt",
        "completion",
        "source_task",
        "source_record_id",
        "task",
        "type",
        "category",
        "split",
        "id",
    }

    PREFERRED_CONTENT_FIELDS = {
        "text",
        "clean_text",
        "content",
        "output_text",
        "natural_text",
        "sentence",
        "frase",
        "summary",
        "riassunto",
        "answer_text",
        "risposta_testo",
        "target",
        "completion",
        "output",
        "risposta",
        "value",
    }

    SENTENCE_END = {".", "!", "?"}

    def __init__(
        self,
        root: Path,
        input_full: Path,
        input_train: Path,
        input_val: Path,
        input_test: Path,
        output_dir: Path,
        report_path: Path,
        min_chars: int = 18,
        max_chars: int = 420,
    ):
        self.root = root
        self.input_full = input_full
        self.input_train = input_train
        self.input_val = input_val
        self.input_test = input_test
        self.output_dir = output_dir
        self.report_path = report_path
        self.min_chars = min_chars
        self.max_chars = max_chars

        self.stats = {
            "source_records_total": 0,
            "candidate_texts_total": 0,
            "accepted_texts_total": 0,
            "discarded_empty": 0,
            "discarded_short": 0,
            "discarded_dirty": 0,
            "discarded_duplicate": 0,
            "dirty_removed": 0,
            "phrases_removed": 0,
            "punctuation_repairs": 0,
        }

    def run(self) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        split_inputs = {
            "train": self.input_train,
            "val": self.input_val,
            "test": self.input_test,
        }

        split_records: Dict[str, List[Dict]] = {}

        if all(path.exists() for path in split_inputs.values()):
            for split_name, path in split_inputs.items():
                split_records[split_name] = self._build_split(path=path, split_name=split_name)
        else:
            full_records = self._build_split(path=self.input_full, split_name="full")
            split_records = self._split_records(full_records)

        all_records: List[Dict] = []
        for split_name in ["train", "val", "test"]:
            all_records.extend(split_records.get(split_name, []))

        # Riassegna clean_id globali stabili.
        for index, record in enumerate(all_records, start=1):
            record["clean_id"] = f"clean-v2-{index:05d}"

        # Propaga clean_id globali anche negli split.
        by_tmp_id = {record["tmp_id"]: record["clean_id"] for record in all_records}
        for records in split_records.values():
            for record in records:
                record["clean_id"] = by_tmp_id.get(record["tmp_id"], record["clean_id"])
                record.pop("tmp_id", None)

        for record in all_records:
            record.pop("tmp_id", None)

        output_full = self.output_dir / "knowledge_dataset_v2_clean.jsonl"
        output_train = self.output_dir / "knowledge_dataset_v2_clean_train.jsonl"
        output_val = self.output_dir / "knowledge_dataset_v2_clean_val.jsonl"
        output_test = self.output_dir / "knowledge_dataset_v2_clean_test.jsonl"
        manifest_path = self.output_dir / "knowledge_dataset_v2_clean_manifest.json"

        self._write_jsonl(output_full, all_records)
        self._write_jsonl(output_train, split_records.get("train", []))
        self._write_jsonl(output_val, split_records.get("val", []))
        self._write_jsonl(output_test, split_records.get("test", []))

        quality = self._quality_summary(all_records)

        manifest = {
            "versione": "knowledge_dataset_v2_clean",
            "status": "built",
            "description": "Dataset naturale pulito per training next-token mini LLM.",
            "input_files": {
                "full": str(self.input_full),
                "train": str(self.input_train),
                "val": str(self.input_val),
                "test": str(self.input_test),
            },
            "output_files": {
                "full": str(output_full),
                "train": str(output_train),
                "val": str(output_val),
                "test": str(output_test),
                "manifest": str(manifest_path),
                "report": str(self.report_path),
            },
            "records": {
                "full": len(all_records),
                "train": len(split_records.get("train", [])),
                "val": len(split_records.get("val", [])),
                "test": len(split_records.get("test", [])),
            },
            "cleaning": {
                "dirty_tokens": sorted(self.DIRTY_TOKENS),
                "dirty_phrases": sorted(self.DIRTY_PHRASES),
                "min_chars": self.min_chars,
                "max_chars": self.max_chars,
                "stats": self.stats,
            },
            "quality": quality,
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.report_path.write_text(
            self._build_report(manifest=manifest),
            encoding="utf-8",
        )

        return manifest

    def _build_split(self, path: Path, split_name: str) -> List[Dict]:
        source_records = self._read_jsonl(path)
        accepted: List[Dict] = []
        seen_texts = set()

        for source_index, record in enumerate(source_records, start=1):
            self.stats["source_records_total"] += 1
            candidates = self._extract_candidate_texts(record)
            self.stats["candidate_texts_total"] += len(candidates)

            for candidate_index, raw_text in enumerate(candidates, start=1):
                cleaned_text, clean_stats = self._clean_text(raw_text)

                self.stats["dirty_removed"] += clean_stats["dirty_removed"]
                self.stats["phrases_removed"] += clean_stats["phrases_removed"]
                self.stats["punctuation_repairs"] += clean_stats["punctuation_repairs"]

                decision = self._accept_text(cleaned_text)

                if decision != "accepted":
                    self.stats[decision] += 1
                    continue

                text_key = cleaned_text.lower()

                if text_key in seen_texts:
                    self.stats["discarded_duplicate"] += 1
                    continue

                seen_texts.add(text_key)
                self.stats["accepted_texts_total"] += 1

                source_id = str(
                    record.get("id")
                    or record.get("record_id")
                    or record.get("source_record_id")
                    or f"{split_name}-{source_index:05d}"
                )

                accepted.append(
                    {
                        "clean_id": "",
                        "tmp_id": f"{split_name}-{source_index:05d}-{candidate_index:03d}",
                        "source_record_id": source_id,
                        "source_split": split_name if split_name != "full" else record.get("split", "train"),
                        "source_task": str(record.get("source_task") or record.get("task") or record.get("type") or ""),
                        "text": cleaned_text,
                        "char_count": len(cleaned_text),
                        "token_count_estimate": len(self._tokenize(cleaned_text)),
                        "cleaning": {
                            "from_candidate_index": candidate_index,
                            "dirty_removed": clean_stats["dirty_removed"],
                            "phrases_removed": clean_stats["phrases_removed"],
                            "punctuation_repairs": clean_stats["punctuation_repairs"],
                        },
                    }
                )

        return accepted

    def _read_jsonl(self, path: Path) -> List[Dict]:
        if not path.exists():
            raise FileNotFoundError(f"Dataset sorgente non trovato: {path}")

        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSON non valido in {path}:{line_number}: {error}") from error

                if isinstance(payload, dict):
                    records.append(payload)

        return records

    def _extract_candidate_texts(self, record: Dict) -> List[str]:
        candidates: List[Tuple[int, str]] = []

        # Preferisce campi di contenuto espliciti.
        for key, value in record.items():
            key_lower = str(key).lower()

            if isinstance(value, str) and key_lower in self.PREFERRED_CONTENT_FIELDS:
                score = 100
                if key_lower in {"instruction", "istruzione", "input", "prompt"}:
                    score -= 60
                if key_lower in {"output", "completion", "risposta", "answer_text", "target"}:
                    score += 20

                candidates.append((score, value))

        # Fallback: esplora ricorsivamente il record.
        for path, value in self._walk_strings(record):
            path_lower = ".".join(path).lower()

            if any(part in self.TECHNICAL_FIELD_NAMES for part in path_lower.split(".")):
                score = 20
            else:
                score = 50

            if any(name in path_lower for name in ["output", "completion", "risposta", "answer", "summary", "text"]):
                score += 30

            candidates.append((score, value))

        # Dedup preservando ordine per punteggio.
        candidates.sort(reverse=True, key=lambda item: item[0])

        result: List[str] = []
        seen = set()

        for _score, text in candidates:
            normalized = self._normalize_space(text)

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(normalized)

        return result

    def _walk_strings(self, value, path: Optional[List[str]] = None) -> Iterable[Tuple[List[str], str]]:
        if path is None:
            path = []

        if isinstance(value, dict):
            for key, child in value.items():
                yield from self._walk_strings(child, path + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from self._walk_strings(child, path + [str(index)])
        elif isinstance(value, str):
            yield path, value

    def _clean_text(self, text: str) -> Tuple[str, Dict[str, int]]:
        stats = {
            "dirty_removed": 0,
            "phrases_removed": 0,
            "punctuation_repairs": 0,
        }

        cleaned = str(text)

        # Rimuove markdown e marcatori tecnici.
        before = cleaned
        cleaned = cleaned.replace("#", " ")
        cleaned = cleaned.replace("```", " ")
        cleaned = cleaned.replace(":::", " ")
        cleaned = re.sub(r"^\s*[-*]\s+", "", cleaned, flags=re.MULTILINE)
        if cleaned != before:
            stats["punctuation_repairs"] += 1

        # Rimuove etichette tecniche iniziali tipo "Input:", "Risposta:", "# risposta".
        label_pattern = r"\b(input|output|istruzione|instruction|risposta|domanda|answer|question|prompt|completion)\s*:"
        cleaned, count = re.subn(label_pattern, " ", cleaned, flags=re.IGNORECASE)
        stats["dirty_removed"] += count

        # Rimuove frasi sporche.
        for phrase in sorted(self.DIRTY_PHRASES, key=len, reverse=True):
            pattern = re.escape(phrase)
            cleaned, count = re.subn(pattern, " ", cleaned, flags=re.IGNORECASE)
            stats["phrases_removed"] += count

        tokens = self._tokenize_keep_punctuation(cleaned)
        clean_tokens: List[str] = []

        for token in tokens:
            lower = token.lower().strip()

            if lower in self.DIRTY_TOKENS:
                stats["dirty_removed"] += 1
                continue

            if not token.strip():
                continue

            if clean_tokens and lower == clean_tokens[-1].lower():
                stats["punctuation_repairs"] += 1
                continue

            if clean_tokens and self._is_punctuation(lower) and self._is_punctuation(clean_tokens[-1]):
                stats["punctuation_repairs"] += 1
                continue

            clean_tokens.append(token)

        cleaned = self._detokenize(clean_tokens)
        cleaned = self._normalize_space(cleaned)
        cleaned = self._repair_sentence(cleaned)

        if len(cleaned) > self.max_chars:
            cleaned = self._truncate_to_sentence(cleaned, self.max_chars)

        return cleaned, stats

    def _accept_text(self, text: str) -> str:
        if not text:
            return "discarded_empty"

        if len(text) < self.min_chars:
            return "discarded_short"

        lower_text = text.lower()
        tokens = [token.lower() for token in self._tokenize(text)]

        if any(token in self.DIRTY_TOKENS for token in tokens):
            return "discarded_dirty"

        if any(phrase in lower_text for phrase in self.DIRTY_PHRASES):
            return "discarded_dirty"

        if re.search(r"\b(input|output|risposta|istruzione|instruction)\b\s*:", lower_text):
            return "discarded_dirty"

        if text[0] in ".,;:!?-":
            return "discarded_dirty"

        return "accepted"

    def _split_records(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        if not records:
            return {"train": [], "val": [], "test": []}

        train: List[Dict] = []
        val: List[Dict] = []
        test: List[Dict] = []

        for index, record in enumerate(records):
            mod = index % 10

            if mod == 8:
                record["source_split"] = "val"
                val.append(record)
            elif mod == 9:
                record["source_split"] = "test"
                test.append(record)
            else:
                record["source_split"] = "train"
                train.append(record)

        return {"train": train, "val": val, "test": test}

    def _write_jsonl(self, path: Path, records: List[Dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _quality_summary(self, records: List[Dict]) -> Dict:
        texts = [record["text"] for record in records]
        token_counts = [record["token_count_estimate"] for record in records]
        char_counts = [record["char_count"] for record in records]

        dirty_hits = 0
        immediate_duplicates = 0
        punctuation_start = 0

        for text in texts:
            tokens = [token.lower() for token in self._tokenize(text)]
            dirty_hits += sum(1 for token in tokens if token in self.DIRTY_TOKENS)

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    immediate_duplicates += 1

            if text and text[0] in ".,;:!?-":
                punctuation_start += 1

        most_common_tokens = Counter(
            token.lower()
            for text in texts
            for token in self._tokenize(text)
            if len(token) > 1
        ).most_common(20)

        return {
            "records": len(records),
            "dirty_token_hits": dirty_hits,
            "immediate_duplicates": immediate_duplicates,
            "punctuation_start": punctuation_start,
            "avg_token_count": round(statistics.mean(token_counts), 2) if token_counts else 0,
            "avg_char_count": round(statistics.mean(char_counts), 2) if char_counts else 0,
            "min_char_count": min(char_counts) if char_counts else 0,
            "max_char_count": max(char_counts) if char_counts else 0,
            "top_tokens": most_common_tokens,
        }

    def _build_report(self, manifest: Dict) -> str:
        return f"""# Report Knowledge Dataset Builder V2 Clean

## Stato
{manifest["status"]}

## Obiettivo
Creare un dataset naturale più pulito prima del training del mini LLM.

## Input
```json
{json.dumps(manifest["input_files"], ensure_ascii=False, indent=2)}
```

## Output
```json
{json.dumps(manifest["output_files"], ensure_ascii=False, indent=2)}
```

## Record generati
```json
{json.dumps(manifest["records"], ensure_ascii=False, indent=2)}
```

## Pulizia applicata
```json
{json.dumps(manifest["cleaning"], ensure_ascii=False, indent=2)}
```

## Qualità
```json
{json.dumps(manifest["quality"], ensure_ascii=False, indent=2)}
```

## Nota
Questo dataset V2 Clean non sostituisce il Dataset V1.
Serve come nuova base più naturale per Token Vectorizer V2 e Neural Model V3.
"""

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text, flags=re.IGNORECASE)

    def _tokenize_keep_punctuation(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[.,;:!?()'’\-]", text, flags=re.IGNORECASE)

    def _detokenize(self, tokens: List[str]) -> str:
        text = " ".join(tokens)
        text = text.replace(" ,", ",")
        text = text.replace(" .", ".")
        text = text.replace(" :", ":")
        text = text.replace(" ;", ";")
        text = text.replace(" !", "!")
        text = text.replace(" ?", "?")
        text = text.replace("( ", "(")
        text = text.replace(" )", ")")
        text = text.replace(" ’ ", "’")
        text = text.replace(" ' ", "'")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"([,.;:!?])\1+", r"\1", text)
        return text.strip()

    def _normalize_space(self, text: str) -> str:
        return re.sub(r"\s+", " ", str(text).strip())

    def _is_punctuation(self, token: str) -> bool:
        return token in {".", ",", ";", ":", "!", "?", "-", "(", ")", "’", "'"}

    def _repair_sentence(self, text: str) -> str:
        text = text.strip(" ,;:-")

        if not text:
            return ""

        if text[-1] not in ".!?":
            text += "."

        return text

    def _truncate_to_sentence(self, text: str, max_chars: int) -> str:
        cut = text[:max_chars].rstrip()
        sentence_positions = [cut.rfind("."), cut.rfind("!"), cut.rfind("?")]
        last_sentence = max(sentence_positions)

        if last_sentence >= self.min_chars:
            return cut[: last_sentence + 1].strip()

        return self._repair_sentence(cut)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Knowledge Dataset Builder V2 Clean")

    parser.add_argument("--input-full", default="mini_llm/data/training/knowledge_dataset_v1.jsonl")
    parser.add_argument("--input-train", default="mini_llm/data/training/knowledge_dataset_v1_train.jsonl")
    parser.add_argument("--input-val", default="mini_llm/data/training/knowledge_dataset_v1_val.jsonl")
    parser.add_argument("--input-test", default="mini_llm/data/training/knowledge_dataset_v1_test.jsonl")
    parser.add_argument("--output-dir", default="mini_llm/data/training")
    parser.add_argument("--report", default="mini_llm/reports/knowledge_dataset_builder_v2_clean_report.md")
    parser.add_argument("--min-chars", type=int, default=18)
    parser.add_argument("--max-chars", type=int, default=420)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    builder = KnowledgeDatasetBuilderV2Clean(
        root=root,
        input_full=(root / args.input_full).resolve(),
        input_train=(root / args.input_train).resolve(),
        input_val=(root / args.input_val).resolve(),
        input_test=(root / args.input_test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        min_chars=args.min_chars,
        max_chars=args.max_chars,
    )

    manifest = builder.run()

    print("OK - Knowledge Dataset Builder V2 Clean completato")
    print(f"Dataset completo: {manifest['output_files']['full']}")
    print(f"Train: {manifest['output_files']['train']}")
    print(f"Val: {manifest['output_files']['val']}")
    print(f"Test: {manifest['output_files']['test']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Record totali: {manifest['records']['full']}")
    print(f"Train/Val/Test: {manifest['records']['train']}/{manifest['records']['val']}/{manifest['records']['test']}")
    print(f"Dirty token hits: {manifest['quality']['dirty_token_hits']}")
    print(f"Duplicati immediati: {manifest['quality']['immediate_duplicates']}")


if __name__ == "__main__":
    main()
