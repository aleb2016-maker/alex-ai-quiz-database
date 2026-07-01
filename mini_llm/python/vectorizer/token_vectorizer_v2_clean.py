from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class TokenVectorizerV2Clean:
    """
    Token Vectorizer V2 Clean.

    Usa il Dataset V2 Clean, cioè:
    - knowledge_dataset_v2_clean_train.jsonl
    - knowledge_dataset_v2_clean_val.jsonl
    - knowledge_dataset_v2_clean_test.jsonl

    Differenza rispetto al Vectorizer V1:
    - legge il campo naturale "text" del Dataset V2 Clean;
    - crea un vocabolario V2 separato;
    - crea embeddings V2 separati;
    - crea sequenze token V2 separate;
    - non sovrascrive il Vectorizer V1.

    Output:
    - mini_llm/data/vectorized_v2/token_vocab_v2_clean.json
    - mini_llm/data/vectorized_v2/token_embeddings_v2_clean.json
    - mini_llm/data/vectorized_v2/token_sequences_v2_clean_train.jsonl
    - mini_llm/data/vectorized_v2/token_sequences_v2_clean_val.jsonl
    - mini_llm/data/vectorized_v2/token_sequences_v2_clean_test.jsonl
    - mini_llm/data/vectorized_v2/token_vectorizer_v2_clean_manifest.json
    """

    SPECIAL_TOKENS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]

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

    def __init__(
        self,
        train_path: Path,
        val_path: Path,
        test_path: Path,
        output_dir: Path,
        report_path: Path,
        max_length: int = 128,
        vector_dim: int = 96,
        min_frequency: int = 1,
    ):
        self.train_path = train_path
        self.val_path = val_path
        self.test_path = test_path
        self.output_dir = output_dir
        self.report_path = report_path
        self.max_length = max_length
        self.vector_dim = vector_dim
        self.min_frequency = min_frequency

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.embedding_matrix: List[List[float]] = []

    def run(self) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        train_records = self._read_jsonl(self.train_path)
        val_records = self._read_jsonl(self.val_path)
        test_records = self._read_jsonl(self.test_path)

        all_records = train_records + val_records + test_records

        if not all_records:
            raise ValueError("Dataset V2 Clean vuoto: impossibile creare il vectorizer.")

        vocab_counter = self._build_vocab_counter(all_records)
        self._build_vocab(vocab_counter)
        self._build_embeddings()

        train_sequences = self._vectorize_records(train_records, "train")
        val_sequences = self._vectorize_records(val_records, "val")
        test_sequences = self._vectorize_records(test_records, "test")

        vocab_path = self.output_dir / "token_vocab_v2_clean.json"
        embeddings_path = self.output_dir / "token_embeddings_v2_clean.json"
        train_out = self.output_dir / "token_sequences_v2_clean_train.jsonl"
        val_out = self.output_dir / "token_sequences_v2_clean_val.jsonl"
        test_out = self.output_dir / "token_sequences_v2_clean_test.jsonl"
        manifest_path = self.output_dir / "token_vectorizer_v2_clean_manifest.json"

        vocab_payload = {
            "versione": "token_vocab_v2_clean",
            "description": "Vocabolario V2 costruito dal Dataset V2 Clean.",
            "special_tokens": self.SPECIAL_TOKENS,
            "token_to_id": self.token_to_id,
            "id_to_token": self.id_to_token,
            "vocab_size": len(self.id_to_token),
            "min_frequency": self.min_frequency,
            "source": "knowledge_dataset_v2_clean",
        }

        embeddings_payload = {
            "versione": "token_embeddings_v2_clean",
            "description": "Embedding iniziali deterministici V2 per Token Vectorizer V2 Clean.",
            "dimensione": self.vector_dim,
            "vocab_size": len(self.id_to_token),
            "embedding_matrix": self.embedding_matrix,
            "source_vocab": str(vocab_path),
            "normalization": "deterministic_hash_unit_norm",
        }

        vocab_path.write_text(
            json.dumps(vocab_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        embeddings_path.write_text(
            json.dumps(embeddings_payload, ensure_ascii=False),
            encoding="utf-8",
        )

        self._write_jsonl(train_out, train_sequences)
        self._write_jsonl(val_out, val_sequences)
        self._write_jsonl(test_out, test_sequences)

        quality = self._quality_summary(
            train_sequences=train_sequences,
            val_sequences=val_sequences,
            test_sequences=test_sequences,
            vocab_counter=vocab_counter,
        )

        manifest = {
            "versione": "token_vectorizer_v2_clean",
            "status": "built",
            "description": "Tokenizzazione e vettorizzazione V2 del Dataset V2 Clean.",
            "input_files": {
                "train": str(self.train_path),
                "val": str(self.val_path),
                "test": str(self.test_path),
            },
            "output_files": {
                "vocab": str(vocab_path),
                "embeddings": str(embeddings_path),
                "train_sequences": str(train_out),
                "val_sequences": str(val_out),
                "test_sequences": str(test_out),
                "manifest": str(manifest_path),
                "report": str(self.report_path),
            },
            "settings": {
                "max_length": self.max_length,
                "vector_dim": self.vector_dim,
                "min_frequency": self.min_frequency,
                "special_tokens": self.SPECIAL_TOKENS,
                "uses_clean_dataset_v2": True,
            },
            "records": {
                "train": len(train_sequences),
                "val": len(val_sequences),
                "test": len(test_sequences),
                "total": len(train_sequences) + len(val_sequences) + len(test_sequences),
            },
            "vocab": {
                "vocab_size": len(self.id_to_token),
                "dirty_tokens_in_vocab": self._dirty_tokens_in_vocab(),
                "top_tokens": vocab_counter.most_common(30),
            },
            "quality": quality,
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.report_path.write_text(
            self._build_report(manifest),
            encoding="utf-8",
        )

        return manifest

    def _read_jsonl(self, path: Path) -> List[Dict]:
        if not path.exists():
            raise FileNotFoundError(f"Dataset non trovato: {path}")

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

                if not isinstance(payload, dict):
                    raise ValueError(f"Record non dizionario in {path}:{line_number}")

                text = str(payload.get("text", "")).strip()

                if not text:
                    raise ValueError(f"Record senza campo text in {path}:{line_number}")

                records.append(payload)

        return records

    def _build_vocab_counter(self, records: List[Dict]) -> Counter:
        counter: Counter = Counter()

        for record in records:
            text = str(record["text"])
            tokens = self._tokenize(text)
            counter.update(tokens)

        return counter

    def _build_vocab(self, counter: Counter) -> None:
        self.token_to_id = {}
        self.id_to_token = []

        for token in self.SPECIAL_TOKENS:
            self.token_to_id[token] = len(self.id_to_token)
            self.id_to_token.append(token)

        normal_tokens = [
            (token, count)
            for token, count in counter.items()
            if count >= self.min_frequency
            and token not in self.SPECIAL_TOKENS
            and token.lower() not in self.DIRTY_TOKENS
        ]

        # Frequenza decrescente, poi ordine alfabetico per stabilità.
        normal_tokens.sort(key=lambda item: (-item[1], item[0]))

        for token, _count in normal_tokens:
            if token in self.token_to_id:
                continue

            self.token_to_id[token] = len(self.id_to_token)
            self.id_to_token.append(token)

    def _build_embeddings(self) -> None:
        self.embedding_matrix = []

        for token_id, token in enumerate(self.id_to_token):
            if token == "<PAD>":
                vector = [0.0 for _ in range(self.vector_dim)]
            else:
                vector = self._deterministic_embedding(token=token, token_id=token_id)

            self.embedding_matrix.append(vector)

    def _deterministic_embedding(self, token: str, token_id: int) -> List[float]:
        values: List[float] = []
        counter = 0

        while len(values) < self.vector_dim:
            digest = hashlib.sha256(
                f"v2-clean::{token_id}::{token}::{counter}".encode("utf-8")
            ).digest()

            for byte in digest:
                value = (byte / 255.0) * 2.0 - 1.0
                values.append(value)

                if len(values) == self.vector_dim:
                    break

            counter += 1

        norm = math.sqrt(sum(value * value for value in values))

        if norm == 0:
            return [0.0 for _ in values]

        return [round(value / norm, 8) for value in values]

    def _vectorize_records(self, records: List[Dict], split: str) -> List[Dict]:
        sequences: List[Dict] = []

        pad_id = self.token_to_id["<PAD>"]
        unk_id = self.token_to_id["<UNK>"]
        bos_id = self.token_to_id["<BOS>"]
        eos_id = self.token_to_id["<EOS>"]

        for index, record in enumerate(records, start=1):
            text = str(record["text"]).strip()
            tokens = self._tokenize(text)

            token_ids = [bos_id]
            token_ids.extend(self.token_to_id.get(token, unk_id) for token in tokens)
            token_ids.append(eos_id)

            original_length = len(token_ids)
            truncated = False

            if len(token_ids) > self.max_length:
                token_ids = token_ids[: self.max_length]
                token_ids[-1] = eos_id
                truncated = True

            attention_mask = [1 for _ in token_ids]

            while len(token_ids) < self.max_length:
                token_ids.append(pad_id)
                attention_mask.append(0)

            labels = self._build_next_token_labels(token_ids=token_ids, attention_mask=attention_mask)

            sequences.append(
                {
                    "sequence_id": f"v2-clean-{split}-{index:05d}",
                    "source_clean_id": record.get("clean_id", ""),
                    "source_record_id": record.get("source_record_id", ""),
                    "source_split": split,
                    "text": text,
                    "tokens": tokens,
                    "token_ids": token_ids,
                    "attention_mask": attention_mask,
                    "labels": labels,
                    "original_length": original_length,
                    "max_length": self.max_length,
                    "truncated": truncated,
                    "token_count": len(tokens),
                    "char_count": len(text),
                    "dataset_version": "knowledge_dataset_v2_clean",
                    "vectorizer_version": "token_vectorizer_v2_clean",
                }
            )

        return sequences

    def _build_next_token_labels(self, token_ids: List[int], attention_mask: List[int]) -> List[int]:
        labels: List[int] = []

        for index in range(len(token_ids)):
            if attention_mask[index] != 1:
                labels.append(-100)
                continue

            if index + 1 >= len(token_ids) or attention_mask[index + 1] != 1:
                labels.append(-100)
                continue

            labels.append(token_ids[index + 1])

        return labels

    def _write_jsonl(self, path: Path, records: List[Dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _quality_summary(
        self,
        train_sequences: List[Dict],
        val_sequences: List[Dict],
        test_sequences: List[Dict],
        vocab_counter: Counter,
    ) -> Dict:
        all_sequences = train_sequences + val_sequences + test_sequences
        original_lengths = [record["original_length"] for record in all_sequences]
        token_counts = [record["token_count"] for record in all_sequences]

        dirty_hits = 0
        immediate_duplicates = 0
        unk_count = 0
        total_active_tokens = 0
        truncated_count = 0

        unk_id = self.token_to_id["<UNK>"]

        for record in all_sequences:
            tokens = [token.lower() for token in record["tokens"]]
            dirty_hits += sum(1 for token in tokens if token in self.DIRTY_TOKENS)

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    immediate_duplicates += 1

            active_ids = [
                token_id
                for token_id, mask in zip(record["token_ids"], record["attention_mask"])
                if mask == 1
            ]

            total_active_tokens += len(active_ids)
            unk_count += sum(1 for token_id in active_ids if token_id == unk_id)

            if record["truncated"]:
                truncated_count += 1

        unk_ratio = round(unk_count / total_active_tokens, 6) if total_active_tokens else 0

        return {
            "sequences_total": len(all_sequences),
            "dirty_token_hits": dirty_hits,
            "immediate_duplicates": immediate_duplicates,
            "truncated_sequences": truncated_count,
            "unk_count": unk_count,
            "unk_ratio": unk_ratio,
            "avg_original_length": round(statistics.mean(original_lengths), 2) if original_lengths else 0,
            "max_original_length": max(original_lengths) if original_lengths else 0,
            "avg_token_count": round(statistics.mean(token_counts), 2) if token_counts else 0,
            "vocab_unique_raw_tokens": len(vocab_counter),
        }

    def _dirty_tokens_in_vocab(self) -> List[str]:
        return [
            token
            for token in self.id_to_token
            if token.lower() in self.DIRTY_TOKENS
        ]

    def _build_report(self, manifest: Dict) -> str:
        return f"""# Report Token Vectorizer V2 Clean

## Stato
{manifest["status"]}

## Obiettivo
Vectorizzare il Dataset V2 Clean senza sovrascrivere il Vectorizer V1.

## Input
```json
{json.dumps(manifest["input_files"], ensure_ascii=False, indent=2)}
```

## Output
```json
{json.dumps(manifest["output_files"], ensure_ascii=False, indent=2)}
```

## Impostazioni
```json
{json.dumps(manifest["settings"], ensure_ascii=False, indent=2)}
```

## Record
```json
{json.dumps(manifest["records"], ensure_ascii=False, indent=2)}
```

## Vocabolario
```json
{json.dumps(manifest["vocab"], ensure_ascii=False, indent=2)}
```

## Qualità
```json
{json.dumps(manifest["quality"], ensure_ascii=False, indent=2)}
```

## Nota
Questo blocco prepara la base numerica pulita per Neural Model V3.
"""

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text, flags=re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Token Vectorizer V2 Clean")

    parser.add_argument("--train", default="mini_llm/data/training/knowledge_dataset_v2_clean_train.jsonl")
    parser.add_argument("--val", default="mini_llm/data/training/knowledge_dataset_v2_clean_val.jsonl")
    parser.add_argument("--test", default="mini_llm/data/training/knowledge_dataset_v2_clean_test.jsonl")
    parser.add_argument("--output-dir", default="mini_llm/data/vectorized_v2")
    parser.add_argument("--report", default="mini_llm/reports/token_vectorizer_v2_clean_report.md")
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--vector-dim", type=int, default=96)
    parser.add_argument("--min-frequency", type=int, default=1)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    vectorizer = TokenVectorizerV2Clean(
        train_path=(root / args.train).resolve(),
        val_path=(root / args.val).resolve(),
        test_path=(root / args.test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        max_length=args.max_length,
        vector_dim=args.vector_dim,
        min_frequency=args.min_frequency,
    )

    manifest = vectorizer.run()

    print("OK - Token Vectorizer V2 Clean completato")
    print(f"Vocabolario: {manifest['output_files']['vocab']}")
    print(f"Embeddings: {manifest['output_files']['embeddings']}")
    print(f"Train sequences: {manifest['output_files']['train_sequences']}")
    print(f"Validation sequences: {manifest['output_files']['val_sequences']}")
    print(f"Test sequences: {manifest['output_files']['test_sequences']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Record totali: {manifest['records']['total']}")
    print(f"Vocab size: {manifest['vocab']['vocab_size']}")
    print(f"Vector dim: {manifest['settings']['vector_dim']}")
    print(f"Max length: {manifest['settings']['max_length']}")
    print(f"Dirty tokens in vocab: {manifest['vocab']['dirty_tokens_in_vocab']}")
    print(f"Troncati: {manifest['quality']['truncated_sequences']}")
    print(f"UNK ratio: {manifest['quality']['unk_ratio']}")


if __name__ == "__main__":
    main()
