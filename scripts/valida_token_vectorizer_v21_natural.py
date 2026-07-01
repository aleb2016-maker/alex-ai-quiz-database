from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class TokenVectorizerV21NaturalValidator:
    SPECIAL_TOKEN_IDS = {
        "<PAD>": 0,
        "<UNK>": 1,
        "<BOS>": 2,
        "<EOS>": 3,
    }

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
        "collegata",
        "collegato",
        "micro",
        "forma",
        "area",
        "operativa",
        "operative",
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
        "crea",
        "creare",
        "genera",
        "generare",
        "training",
        "training_originale",
        "knowledge_engine",
        "knowledge_engine_v14",
        "relazione_operativa",
        "relazioni_operative",
        "micro_informazioni",
        "frasi_rilevanti",
        "aree_operative",
        "dataset",
        "builder",
        "vectorizer",
        "manifest",
        "source",
        "clean",
        "clean_id",
        "source_split",
        "source_clean_id",
        "alex",
        "alessandro",
        "barbarossa",
        "breve",
        "sintesi",
        "template",
    }

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        vectorized_dir = root / "mini_llm" / "data" / "vectorized_v21_natural"
        report_dir = root / "mini_llm" / "reports"

        vocab_path = vectorized_dir / "token_vocab_v21_natural.json"
        embeddings_path = vectorized_dir / "token_embeddings_v21_natural.json"
        train_path = vectorized_dir / "token_sequences_v21_natural_train.jsonl"
        val_path = vectorized_dir / "token_sequences_v21_natural_val.jsonl"
        test_path = vectorized_dir / "token_sequences_v21_natural_test.jsonl"
        manifest_path = vectorized_dir / "token_vectorizer_v21_natural_manifest.json"
        report_path = report_dir / "token_vectorizer_v21_natural_report.md"

        for path in [vocab_path, embeddings_path, train_path, val_path, test_path, manifest_path, report_path]:
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

        self._validate_vocab(vocab, errors)
        self._validate_embeddings(vocab, embeddings, errors)
        self._validate_manifest(manifest, train_records, val_records, test_records, errors)
        self._validate_sequences(vocab, train_records, "train", errors)
        self._validate_sequences(vocab, val_records, "val", errors)
        self._validate_sequences(vocab, test_records, "test", errors)

        return errors

    def _read_jsonl(self, path: Path, errors: List[str]) -> List[Dict]:
        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as error:
                    errors.append(f"JSONL non valido in {path}:{line_number}: {error}")
                    continue

                if not isinstance(payload, dict):
                    errors.append(f"Record non dizionario in {path}:{line_number}")
                    continue

                records.append(payload)

        return records

    def _validate_vocab(self, vocab: Dict, errors: List[str]) -> None:
        if vocab.get("versione") != "token_vocab_v21_natural":
            errors.append("Versione vocabolario errata.")

        token_to_id = vocab.get("token_to_id", {})
        id_to_token = vocab.get("id_to_token", [])

        if vocab.get("vocab_size") != len(id_to_token):
            errors.append("vocab_size incoerente.")

        if len(token_to_id) != len(id_to_token):
            errors.append("token_to_id e id_to_token hanno dimensioni diverse.")

        for token, expected_id in self.SPECIAL_TOKEN_IDS.items():
            if token_to_id.get(token) != expected_id:
                errors.append(f"Special token {token} non ha ID {expected_id}.")

            if len(id_to_token) <= expected_id or id_to_token[expected_id] != token:
                errors.append(f"id_to_token[{expected_id}] non è {token}.")

        dirty_in_vocab = [token for token in id_to_token if str(token).lower() in self.DIRTY_TOKENS]
        numeric_in_vocab = [token for token in id_to_token if self._is_numeric_code_token(str(token).lower())]
        metadata_in_vocab = [token for token in id_to_token if self._is_metadata_shape_token(str(token).lower())]

        if dirty_in_vocab:
            errors.append(f"Token sporchi nel vocabolario: {dirty_in_vocab[:20]}")

        if numeric_in_vocab:
            errors.append(f"Codici numerici nel vocabolario: {numeric_in_vocab[:20]}")

        if metadata_in_vocab:
            errors.append(f"Token metadata nel vocabolario: {metadata_in_vocab[:20]}")

        if len(id_to_token) < 50:
            errors.append("Vocabolario troppo piccolo.")

    def _validate_embeddings(self, vocab: Dict, embeddings: Dict, errors: List[str]) -> None:
        if embeddings.get("versione") != "token_embeddings_v21_natural":
            errors.append("Versione embeddings errata.")

        vocab_size = vocab.get("vocab_size")
        vector_dim = embeddings.get("dimensione")
        matrix = embeddings.get("embedding_matrix", [])

        if embeddings.get("vocab_size") != vocab_size:
            errors.append("Embeddings vocab_size incoerente.")

        if len(matrix) != vocab_size:
            errors.append("Numero righe embedding incoerente.")

        if not isinstance(vector_dim, int) or vector_dim < 32:
            errors.append("Dimensione embedding troppo piccola.")

        if matrix and len(matrix[0]) != vector_dim:
            errors.append("Dimensione prima riga embedding incoerente.")

        if matrix and any(value != 0.0 for value in matrix[0]):
            errors.append("Embedding <PAD> dovrebbe essere tutto zero.")

    def _validate_manifest(
        self,
        manifest: Dict,
        train_records: List[Dict],
        val_records: List[Dict],
        test_records: List[Dict],
        errors: List[str],
    ) -> None:
        if manifest.get("versione") != "token_vectorizer_v21_natural":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "built":
            errors.append("Status manifest non built.")

        settings = manifest.get("settings", {})

        if settings.get("uses_dataset_v21_natural") is not True:
            errors.append("Manifest non dichiara uses_dataset_v21_natural True.")

        if settings.get("max_length", 0) < 32:
            errors.append("max_length troppo corto.")

        if settings.get("vector_dim", 0) < 32:
            errors.append("vector_dim troppo piccola.")

        counts = manifest.get("records", {})

        if counts.get("train") != len(train_records):
            errors.append("Conteggio train incoerente.")

        if counts.get("val") != len(val_records):
            errors.append("Conteggio val incoerente.")

        if counts.get("test") != len(test_records):
            errors.append("Conteggio test incoerente.")

        if counts.get("total") != len(train_records) + len(val_records) + len(test_records):
            errors.append("Conteggio total incoerente.")

        if not train_records or not val_records or not test_records:
            errors.append("Uno split è vuoto.")

        vocab = manifest.get("vocab", {})

        if vocab.get("dirty_tokens_in_vocab"):
            errors.append("Manifest segnala dirty token in vocab.")

        if vocab.get("numeric_code_tokens_in_vocab"):
            errors.append("Manifest segnala codici numerici in vocab.")

        if vocab.get("metadata_shape_tokens_in_vocab"):
            errors.append("Manifest segnala metadata shape in vocab.")

        quality = manifest.get("quality", {})

        for key in [
            "dirty_token_hits",
            "numeric_code_hits",
            "metadata_shape_hits",
            "immediate_duplicates",
            "repeated_bigrams",
            "truncated_sequences",
        ]:
            if quality.get(key, 1) != 0:
                errors.append(f"Manifest segnala problema qualità: {key}={quality.get(key)}")

        if quality.get("unk_ratio", 1.0) > 0.02:
            errors.append("UNK ratio troppo alto.")

    def _validate_sequences(self, vocab: Dict, records: List[Dict], expected_split: str, errors: List[str]) -> None:
        token_to_id = vocab.get("token_to_id", {})
        vocab_size = vocab.get("vocab_size", 0)

        pad_id = token_to_id.get("<PAD>")
        eos_id = token_to_id.get("<EOS>")

        if not records:
            errors.append(f"Split {expected_split} vuoto.")
            return

        for index, record in enumerate(records, start=1):
            if record.get("source_split") != expected_split:
                errors.append(f"{expected_split}:{index}: source_split errato.")

            token_ids = record.get("token_ids", [])
            attention_mask = record.get("attention_mask", [])
            labels = record.get("labels", [])
            tokens = [str(token).lower() for token in record.get("tokens", [])]

            if not token_ids or not attention_mask or not labels:
                errors.append(f"{expected_split}:{index}: token_ids/attention_mask/labels mancanti.")
                continue

            if len(token_ids) != len(attention_mask) or len(token_ids) != len(labels):
                errors.append(f"{expected_split}:{index}: lunghezze incoerenti.")

            if len(token_ids) != record.get("max_length"):
                errors.append(f"{expected_split}:{index}: token_ids non rispetta max_length.")

            if record.get("truncated") is True:
                errors.append(f"{expected_split}:{index}: sequenza troncata.")

            for token in tokens:
                if token in self.DIRTY_TOKENS:
                    errors.append(f"{expected_split}:{index}: token sporco nella sequenza: {token}")

                if self._is_numeric_code_token(token):
                    errors.append(f"{expected_split}:{index}: codice numerico nella sequenza: {token}")

                if self._is_metadata_shape_token(token):
                    errors.append(f"{expected_split}:{index}: metadata shape nella sequenza: {token}")

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    errors.append(f"{expected_split}:{index}: ripetizione immediata: {left}")

            bigrams = list(zip(tokens, tokens[1:]))
            for pos in range(len(bigrams) - 1):
                if bigrams[pos] == bigrams[pos + 1]:
                    errors.append(f"{expected_split}:{index}: bigramma ripetuto.")

            for token_id in token_ids:
                if not isinstance(token_id, int):
                    errors.append(f"{expected_split}:{index}: token_id non intero.")
                    continue

                if token_id < 0 or token_id >= vocab_size:
                    errors.append(f"{expected_split}:{index}: token_id fuori vocabolario.")

            active_positions = [i for i, mask in enumerate(attention_mask) if mask == 1]

            if not active_positions:
                errors.append(f"{expected_split}:{index}: nessun token attivo.")
                continue

            last_active = active_positions[-1]

            if token_ids[last_active] != eos_id:
                errors.append(f"{expected_split}:{index}: ultimo token attivo non è <EOS>.")

            if any(token_id != pad_id for token_id, mask in zip(token_ids, attention_mask) if mask == 0):
                errors.append(f"{expected_split}:{index}: padding non usa <PAD>.")

            valid_labels = [label for label in labels if label != -100]

            if not valid_labels:
                errors.append(f"{expected_split}:{index}: nessuna label valida.")

            for label in valid_labels:
                if label < 0 or label >= vocab_size:
                    errors.append(f"{expected_split}:{index}: label fuori vocabolario.")

    def _is_numeric_code_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()

        if re.fullmatch(r"0\d{2,}", normalized):
            return True

        if re.fullmatch(r"\d{4,}", normalized):
            return True

        return False

    def _is_metadata_shape_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()

        if "_" in normalized:
            return True

        if re.fullmatch(r"[a-zàèéìòù]+v\d+", normalized):
            return True

        if re.search(r"[a-zàèéìòù]+_?[vV]?\d{1,}", normalized):
            return True

        return False


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Token Vectorizer V2.1 Natural

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_token_vectorizer_v21_natural.md"

    validator = TokenVectorizerV21NaturalValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Token Vectorizer V2.1 Natural fallita")
        print(f"Report: {report_path}")

        for error in errors[:100]:
            print("-", error)

        if len(errors) > 100:
            print(f"... altri errori: {len(errors) - 100}")

        raise SystemExit(1)

    print("OK - Validazione Token Vectorizer V2.1 Natural superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
