from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class TokenVectorizerV1:
    """
    Token Vectorizer V1.

    Trasforma il dataset JSONL del mini LLM in:
    - vocabolario token -> id;
    - sequenze numeriche train/val/test;
    - maschere attention_mask;
    - labels per previsione del token successivo;
    - matrice di vettori iniziali deterministici.

    Nota importante:
    questi vettori sono inizializzazioni numeriche stabili, non ancora embedding addestrati.
    Il modello imparerà a modificarli nella fase di training neurale.
    """

    SPECIAL_TOKENS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]

    def __init__(
        self,
        train_path: Path,
        val_path: Path,
        test_path: Path,
        output_dir: Path,
        max_vocab_size: int = 8000,
        min_frequency: int = 1,
        max_length: int = 256,
        vector_dim: int = 64,
        lowercase: bool = True,
    ):
        self.train_path = train_path
        self.val_path = val_path
        self.test_path = test_path
        self.output_dir = output_dir
        self.max_vocab_size = max_vocab_size
        self.min_frequency = min_frequency
        self.max_length = max_length
        self.vector_dim = vector_dim
        self.lowercase = lowercase

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.frequencies: Counter[str] = Counter()

    def run(self) -> Dict:
        train_records = self._read_jsonl(self.train_path)
        val_records = self._read_jsonl(self.val_path)
        test_records = self._read_jsonl(self.test_path)

        self._build_vocab(train_records)

        vectorized_train = self._vectorize_records(train_records, split="train")
        vectorized_val = self._vectorize_records(val_records, split="val")
        vectorized_test = self._vectorize_records(test_records, split="test")

        embeddings = self._build_embedding_matrix()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        vocab_path = self.output_dir / "token_vocab_v1.json"
        embeddings_path = self.output_dir / "token_embeddings_v1.json"
        train_out_path = self.output_dir / "token_sequences_v1_train.jsonl"
        val_out_path = self.output_dir / "token_sequences_v1_val.jsonl"
        test_out_path = self.output_dir / "token_sequences_v1_test.jsonl"
        manifest_path = self.output_dir / "token_vectorizer_v1_manifest.json"

        self._write_jsonl(train_out_path, vectorized_train)
        self._write_jsonl(val_out_path, vectorized_val)
        self._write_jsonl(test_out_path, vectorized_test)

        vocab_payload = {
            "versione": "token_vectorizer_v1",
            "tokenizer": "regex_word_punctuation_v1",
            "lowercase": self.lowercase,
            "special_tokens": {
                "<PAD>": 0,
                "<UNK>": 1,
                "<BOS>": 2,
                "<EOS>": 3,
            },
            "max_vocab_size": self.max_vocab_size,
            "min_frequency": self.min_frequency,
            "vocab_size": len(self.id_to_token),
            "id_to_token": self.id_to_token,
            "token_to_id": self.token_to_id,
            "token_frequencies": dict(self.frequencies),
        }

        vocab_path.write_text(
            json.dumps(vocab_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        embeddings_payload = {
            "versione": "token_embeddings_initial_v1",
            "description": "Vettori iniziali deterministici per token. Non sono ancora embedding addestrati.",
            "dimensione": self.vector_dim,
            "vocab_size": len(self.id_to_token),
            "initialization": "sha256_deterministic_uniform_minus_0_05_plus_0_05",
            "embedding_matrix": embeddings,
        }

        embeddings_path.write_text(
            json.dumps(embeddings_payload, ensure_ascii=False),
            encoding="utf-8",
        )

        manifest = self._build_manifest(
            train_records=train_records,
            val_records=val_records,
            test_records=test_records,
            vectorized_train=vectorized_train,
            vectorized_val=vectorized_val,
            vectorized_test=vectorized_test,
            vocab_path=vocab_path,
            embeddings_path=embeddings_path,
            train_out_path=train_out_path,
            val_out_path=val_out_path,
            test_out_path=test_out_path,
        )

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return manifest

    def _read_jsonl(self, path: Path) -> List[Dict]:
        if not path.exists():
            raise FileNotFoundError(f"Dataset JSONL non trovato: {path}")

        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSON non valido in {path}:{line_number}: {error}") from error

        if not records:
            raise ValueError(f"Nessun record letto da: {path}")

        return records

    def _build_vocab(self, records: List[Dict]) -> None:
        for record in records:
            text = self._record_text(record)
            self.frequencies.update(self._tokenize(text))

        self.id_to_token = list(self.SPECIAL_TOKENS)
        self.token_to_id = {token: index for index, token in enumerate(self.id_to_token)}

        candidates = [
            (token, frequency)
            for token, frequency in self.frequencies.items()
            if frequency >= self.min_frequency and token not in self.token_to_id
        ]

        candidates.sort(key=lambda item: (-item[1], item[0]))

        remaining_slots = max(0, self.max_vocab_size - len(self.id_to_token))

        for token, _frequency in candidates[:remaining_slots]:
            self.token_to_id[token] = len(self.id_to_token)
            self.id_to_token.append(token)

    def _vectorize_records(self, records: List[Dict], split: str) -> List[Dict]:
        output: List[Dict] = []

        for index, record in enumerate(records):
            text = self._record_text(record)
            tokens = self._tokenize(text)
            tokens = ["<BOS>"] + tokens + ["<EOS>"]

            token_ids = [self.token_to_id.get(token, self.token_to_id["<UNK>"]) for token in tokens]
            original_length = len(token_ids)

            token_ids = token_ids[: self.max_length]
            attention_mask = [1] * len(token_ids)

            while len(token_ids) < self.max_length:
                token_ids.append(self.token_to_id["<PAD>"])
                attention_mask.append(0)

            labels = self._build_next_token_labels(token_ids=token_ids, attention_mask=attention_mask)

            output.append(
                {
                    "id": f"token-seq-v1-{split}-{index + 1:05d}",
                    "split": split,
                    "source_record_id": record.get("id", ""),
                    "source_task": record.get("task", ""),
                    "source_section": record.get("source_section", ""),
                    "text": text,
                    "tokens_preview": tokens[:40],
                    "token_ids": token_ids,
                    "attention_mask": attention_mask,
                    "labels": labels,
                    "length_before_padding": min(original_length, self.max_length),
                    "original_token_length": original_length,
                    "truncated": original_length > self.max_length,
                }
            )

        return output

    def _build_next_token_labels(self, token_ids: List[int], attention_mask: List[int]) -> List[int]:
        labels: List[int] = []

        for index in range(len(token_ids)):
            next_index = index + 1

            if next_index >= len(token_ids):
                labels.append(-100)
                continue

            if attention_mask[index] == 0 or attention_mask[next_index] == 0:
                labels.append(-100)
                continue

            labels.append(token_ids[next_index])

        return labels

    def _record_text(self, record: Dict) -> str:
        text = record.get("text", "")

        if not text:
            instruction = record.get("instruction", "")
            input_text = record.get("input", "")
            output = record.get("output", "")
            text = f"### Istruzione\n{instruction}\n\n### Input\n{input_text}\n\n### Risposta\n{output}"

        return self._clean_text(text)

    def _tokenize(self, text: str) -> List[str]:
        if self.lowercase:
            text = text.lower()

        # Cattura parole italiane con accenti, numeri, underscore, e punteggiatura separata.
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text, flags=re.IGNORECASE)

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text).strip().split())

    def _build_embedding_matrix(self) -> List[List[float]]:
        matrix: List[List[float]] = []

        for token_id, token in enumerate(self.id_to_token):
            if token == "<PAD>":
                vector = [0.0] * self.vector_dim
            else:
                vector = self._deterministic_vector(token=token, token_id=token_id)

            matrix.append(vector)

        return matrix

    def _deterministic_vector(self, token: str, token_id: int) -> List[float]:
        vector: List[float] = []

        counter = 0

        while len(vector) < self.vector_dim:
            raw = f"{token}|{token_id}|{counter}".encode("utf-8")
            digest = hashlib.sha256(raw).digest()

            for byte in digest:
                # byte 0..255 -> valore circa -0.05..+0.05
                value = (byte / 255.0) * 0.10 - 0.05
                vector.append(round(value, 8))

                if len(vector) >= self.vector_dim:
                    break

            counter += 1

        return self._normalize_vector(vector)

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(value * value for value in vector))

        if norm == 0:
            return vector

        return [round(value / norm, 8) for value in vector]

    def _write_jsonl(self, path: Path, records: Iterable[Dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _build_manifest(
        self,
        train_records: List[Dict],
        val_records: List[Dict],
        test_records: List[Dict],
        vectorized_train: List[Dict],
        vectorized_val: List[Dict],
        vectorized_test: List[Dict],
        vocab_path: Path,
        embeddings_path: Path,
        train_out_path: Path,
        val_out_path: Path,
        test_out_path: Path,
    ) -> Dict:
        task_counts = Counter(record.get("task", "") for record in train_records + val_records + test_records)
        train_lengths = [record["original_token_length"] for record in vectorized_train]
        val_lengths = [record["original_token_length"] for record in vectorized_val]
        test_lengths = [record["original_token_length"] for record in vectorized_test]
        all_lengths = train_lengths + val_lengths + test_lengths

        return {
            "versione": "token_vectorizer_v1",
            "status": "generated",
            "language": "it",
            "input_files": {
                "train": str(self.train_path),
                "val": str(self.val_path),
                "test": str(self.test_path),
            },
            "output_files": {
                "vocab": str(vocab_path),
                "embeddings": str(embeddings_path),
                "train_sequences": str(train_out_path),
                "val_sequences": str(val_out_path),
                "test_sequences": str(test_out_path),
            },
            "tokenizer": {
                "type": "regex_word_punctuation_v1",
                "lowercase": self.lowercase,
                "max_vocab_size": self.max_vocab_size,
                "min_frequency": self.min_frequency,
                "vocab_size": len(self.id_to_token),
                "special_tokens": {
                    "<PAD>": 0,
                    "<UNK>": 1,
                    "<BOS>": 2,
                    "<EOS>": 3,
                },
            },
            "vectorization": {
                "max_length": self.max_length,
                "vector_dim": self.vector_dim,
                "labels": "next_token_prediction",
                "pad_label_value": -100,
            },
            "counts": {
                "train_records": len(train_records),
                "val_records": len(val_records),
                "test_records": len(test_records),
                "total_records": len(train_records) + len(val_records) + len(test_records),
                "vectorized_train_records": len(vectorized_train),
                "vectorized_val_records": len(vectorized_val),
                "vectorized_test_records": len(vectorized_test),
            },
            "length_stats": {
                "min_original_tokens": min(all_lengths) if all_lengths else 0,
                "max_original_tokens": max(all_lengths) if all_lengths else 0,
                "avg_original_tokens": round(sum(all_lengths) / len(all_lengths), 2) if all_lengths else 0,
                "truncated_records": sum(
                    1
                    for record in vectorized_train + vectorized_val + vectorized_test
                    if record["truncated"]
                ),
            },
            "source_task_counts": dict(task_counts),
        }


def build_report(manifest: Dict) -> str:
    return f"""# Report Token Vectorizer V1

## Stato
{manifest.get("status")}

## Record
- Train: {manifest["counts"]["train_records"]}
- Validation: {manifest["counts"]["val_records"]}
- Test: {manifest["counts"]["test_records"]}
- Totale: {manifest["counts"]["total_records"]}

## Tokenizer
- Tipo: {manifest["tokenizer"]["type"]}
- Vocabolario: {manifest["tokenizer"]["vocab_size"]}
- Max length: {manifest["vectorization"]["max_length"]}

## Vettori
- Dimensione vettore: {manifest["vectorization"]["vector_dim"]}
- Inizializzazione: deterministica SHA256
- Nota: questi vettori non sono ancora embedding addestrati.

## Statistiche lunghezza
```json
{json.dumps(manifest["length_stats"], ensure_ascii=False, indent=2)}
```

## Manifest completo
```json
{json.dumps(manifest, ensure_ascii=False, indent=2)}
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Token Vectorizer V1")

    parser.add_argument(
        "--train",
        default="mini_llm/data/training/knowledge_dataset_v1_train.jsonl",
        help="Dataset train JSONL.",
    )

    parser.add_argument(
        "--val",
        default="mini_llm/data/training/knowledge_dataset_v1_val.jsonl",
        help="Dataset validation JSONL.",
    )

    parser.add_argument(
        "--test",
        default="mini_llm/data/training/knowledge_dataset_v1_test.jsonl",
        help="Dataset test JSONL.",
    )

    parser.add_argument(
        "--output-dir",
        default="mini_llm/data/vectorized",
        help="Cartella output vettorializzazione.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/token_vectorizer_v1_report.md",
        help="Report Markdown.",
    )

    parser.add_argument("--max-vocab-size", type=int, default=8000)
    parser.add_argument("--min-frequency", type=int, default=1)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--vector-dim", type=int, default=64)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    vectorizer = TokenVectorizerV1(
        train_path=(root / args.train).resolve(),
        val_path=(root / args.val).resolve(),
        test_path=(root / args.test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        max_vocab_size=args.max_vocab_size,
        min_frequency=args.min_frequency,
        max_length=args.max_length,
        vector_dim=args.vector_dim,
    )

    manifest = vectorizer.run()

    report_path = (root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(manifest), encoding="utf-8")

    print("OK - Token Vectorizer V1 completato")
    print(f"Vocabolario: {manifest['output_files']['vocab']}")
    print(f"Embeddings: {manifest['output_files']['embeddings']}")
    print(f"Train sequences: {manifest['output_files']['train_sequences']}")
    print(f"Validation sequences: {manifest['output_files']['val_sequences']}")
    print(f"Test sequences: {manifest['output_files']['test_sequences']}")
    print(f"Report: {report_path}")
    print(f"Record totali: {manifest['counts']['total_records']}")
    print(f"Vocab size: {manifest['tokenizer']['vocab_size']}")
    print(f"Vector dim: {manifest['vectorization']['vector_dim']}")
    print(f"Max length: {manifest['vectorization']['max_length']}")
    print(f"Record troncati: {manifest['length_stats']['truncated_records']}")


if __name__ == "__main__":
    main()
