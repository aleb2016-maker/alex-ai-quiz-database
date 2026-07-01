from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List


class TokenVectorizerV1Validator:
    """
    Validatore Token Vectorizer V1.

    Controlla:
    - presenza output;
    - vocabolario coerente;
    - embedding matrix coerente;
    - sequenze numeriche train/val/test leggibili;
    - token_ids, attention_mask e labels della stessa lunghezza;
    - special token corretti;
    - nessuna sequenza vuota.
    """

    REQUIRED_SPECIAL_TOKENS = {
        "<PAD>": 0,
        "<UNK>": 1,
        "<BOS>": 2,
        "<EOS>": 3,
    }

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        output_dir = root / "mini_llm" / "data" / "vectorized"
        report_dir = root / "mini_llm" / "reports"

        vocab_path = output_dir / "token_vocab_v1.json"
        embeddings_path = output_dir / "token_embeddings_v1.json"
        train_path = output_dir / "token_sequences_v1_train.jsonl"
        val_path = output_dir / "token_sequences_v1_val.jsonl"
        test_path = output_dir / "token_sequences_v1_test.jsonl"
        manifest_path = output_dir / "token_vectorizer_v1_manifest.json"
        report_path = report_dir / "token_vectorizer_v1_report.md"

        for path in [
            vocab_path,
            embeddings_path,
            train_path,
            val_path,
            test_path,
            manifest_path,
            report_path,
        ]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
        embeddings = json.loads(embeddings_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        train_records = self._read_jsonl(train_path, errors)
        val_records = self._read_jsonl(val_path, errors)
        test_records = self._read_jsonl(test_path, errors)

        if errors:
            return errors

        self._validate_vocab(vocab, errors)
        self._validate_embeddings(vocab, embeddings, manifest, errors)
        self._validate_manifest(manifest, train_records, val_records, test_records, errors)
        self._validate_sequences(train_records, split="train", manifest=manifest, errors=errors)
        self._validate_sequences(val_records, split="val", manifest=manifest, errors=errors)
        self._validate_sequences(test_records, split="test", manifest=manifest, errors=errors)

        return errors

    def _read_jsonl(self, path: Path, errors: List[str]) -> List[Dict]:
        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    errors.append(f"JSON non valido in {path}:{line_number}: {error}")

        return records

    def _validate_vocab(self, vocab: Dict, errors: List[str]) -> None:
        if vocab.get("versione") != "token_vectorizer_v1":
            errors.append("Versione vocabolario errata.")

        token_to_id = vocab.get("token_to_id", {})
        id_to_token = vocab.get("id_to_token", [])
        vocab_size = vocab.get("vocab_size")

        if vocab_size != len(id_to_token):
            errors.append("vocab_size non coincide con id_to_token.")

        if len(token_to_id) != len(id_to_token):
            errors.append("token_to_id e id_to_token hanno lunghezze diverse.")

        for token, expected_id in self.REQUIRED_SPECIAL_TOKENS.items():
            actual_id = token_to_id.get(token)

            if actual_id != expected_id:
                errors.append(f"Special token errato: {token} -> {actual_id}, atteso {expected_id}")

            if expected_id >= len(id_to_token) or id_to_token[expected_id] != token:
                errors.append(f"id_to_token errato per {token}.")

        if len(id_to_token) < 50:
            errors.append(f"Vocabolario troppo piccolo: {len(id_to_token)} token.")

    def _validate_embeddings(self, vocab: Dict, embeddings: Dict, manifest: Dict, errors: List[str]) -> None:
        matrix = embeddings.get("embedding_matrix", [])
        dimension = embeddings.get("dimensione")
        vocab_size = vocab.get("vocab_size")

        if embeddings.get("versione") != "token_embeddings_initial_v1":
            errors.append("Versione embeddings errata.")

        if dimension != manifest.get("vectorization", {}).get("vector_dim"):
            errors.append("Dimensione embeddings incoerente con manifest.")

        if len(matrix) != vocab_size:
            errors.append(f"Embedding matrix incoerente: {len(matrix)} righe, vocab {vocab_size}.")

        if not matrix:
            errors.append("Embedding matrix vuota.")
            return

        pad_vector = matrix[0]

        if any(value != 0.0 for value in pad_vector):
            errors.append("Vettore <PAD> non è tutto zero.")

        for index, vector in enumerate(matrix[: min(len(matrix), 30)]):
            if len(vector) != dimension:
                errors.append(f"Vettore {index} ha dimensione errata: {len(vector)}")

            if index != 0:
                norm = math.sqrt(sum(value * value for value in vector))

                if norm < 0.95 or norm > 1.05:
                    errors.append(f"Vettore {index} non normalizzato correttamente: norm={norm}")

    def _validate_manifest(
        self,
        manifest: Dict,
        train_records: List[Dict],
        val_records: List[Dict],
        test_records: List[Dict],
        errors: List[str],
    ) -> None:
        if manifest.get("versione") != "token_vectorizer_v1":
            errors.append("Versione manifest errata.")

        counts = manifest.get("counts", {})

        if counts.get("vectorized_train_records") != len(train_records):
            errors.append("Conteggio train incoerente nel manifest.")

        if counts.get("vectorized_val_records") != len(val_records):
            errors.append("Conteggio validation incoerente nel manifest.")

        if counts.get("vectorized_test_records") != len(test_records):
            errors.append("Conteggio test incoerente nel manifest.")

        if counts.get("total_records") != len(train_records) + len(val_records) + len(test_records):
            errors.append("Conteggio totale incoerente nel manifest.")

    def _validate_sequences(
        self,
        records: List[Dict],
        split: str,
        manifest: Dict,
        errors: List[str],
    ) -> None:
        expected_length = manifest.get("vectorization", {}).get("max_length")
        pad_id = self.REQUIRED_SPECIAL_TOKENS["<PAD>"]
        bos_id = self.REQUIRED_SPECIAL_TOKENS["<BOS>"]

        if not records:
            errors.append(f"Nessun record nello split {split}.")
            return

        for record in records:
            record_id = record.get("id", "")
            token_ids = record.get("token_ids", [])
            attention_mask = record.get("attention_mask", [])
            labels = record.get("labels", [])

            if record.get("split") != split:
                errors.append(f"{record_id}: split errato: {record.get('split')} atteso {split}")

            if len(token_ids) != expected_length:
                errors.append(f"{record_id}: token_ids length errata: {len(token_ids)}")

            if len(attention_mask) != expected_length:
                errors.append(f"{record_id}: attention_mask length errata: {len(attention_mask)}")

            if len(labels) != expected_length:
                errors.append(f"{record_id}: labels length errata: {len(labels)}")

            if not token_ids or token_ids[0] != bos_id:
                errors.append(f"{record_id}: primo token non è <BOS>.")

            if not all(isinstance(value, int) for value in token_ids):
                errors.append(f"{record_id}: token_ids contiene valori non interi.")

            if not all(value in (0, 1) for value in attention_mask):
                errors.append(f"{record_id}: attention_mask contiene valori diversi da 0/1.")

            if sum(attention_mask) <= 1:
                errors.append(f"{record_id}: sequenza quasi vuota.")

            for token_id, mask in zip(token_ids, attention_mask):
                if mask == 0 and token_id != pad_id:
                    errors.append(f"{record_id}: token padding con id non PAD.")

            if not all(isinstance(value, int) for value in labels):
                errors.append(f"{record_id}: labels contiene valori non interi.")

            if all(value == -100 for value in labels):
                errors.append(f"{record_id}: labels tutte ignorate.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Token Vectorizer V1

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_token_vectorizer_v1.md"

    validator = TokenVectorizerV1Validator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Token Vectorizer V1 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Token Vectorizer V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
