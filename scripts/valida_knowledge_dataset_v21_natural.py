from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class KnowledgeDatasetV21NaturalValidator:
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
        "è collegata a",
        "e collegata a",
        "è collegato a",
        "e collegato a",
        "relazione operativa",
        "relazioni operative",
        "training originale",
        "knowledge engine",
        "dataset builder",
        "token vectorizer",
        "neural model",
    }

    CONTENT_HINTS = {
        "password",
        "manager",
        "sicurezza",
        "informatica",
        "backup",
        "ransomware",
        "phishing",
        "malware",
        "dati",
        "sensibili",
        "autenticazione",
        "fattori",
        "account",
        "codici",
        "temporanei",
        "aggiornamenti",
        "software",
        "privilegio",
        "amministrativi",
        "protezione",
        "credenziali",
    }

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        training_dir = root / "mini_llm" / "data" / "training"
        report_dir = root / "mini_llm" / "reports"

        full_path = training_dir / "knowledge_dataset_v21_natural.jsonl"
        train_path = training_dir / "knowledge_dataset_v21_natural_train.jsonl"
        val_path = training_dir / "knowledge_dataset_v21_natural_val.jsonl"
        test_path = training_dir / "knowledge_dataset_v21_natural_test.jsonl"
        manifest_path = training_dir / "knowledge_dataset_v21_natural_manifest.json"
        report_path = report_dir / "knowledge_dataset_builder_v21_natural_report.md"

        for path in [full_path, train_path, val_path, test_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        full_records = self._read_jsonl(full_path, errors)
        train_records = self._read_jsonl(train_path, errors)
        val_records = self._read_jsonl(val_path, errors)
        test_records = self._read_jsonl(test_path, errors)

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"Manifest JSON non valido: {error}")
            return errors

        self._validate_manifest(manifest, full_records, train_records, val_records, test_records, errors)
        self._validate_records(full_records, errors)

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

    def _validate_manifest(
        self,
        manifest: Dict,
        full_records: List[Dict],
        train_records: List[Dict],
        val_records: List[Dict],
        test_records: List[Dict],
        errors: List[str],
    ) -> None:
        if manifest.get("versione") != "knowledge_dataset_v21_natural":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "built":
            errors.append("Status manifest non built.")

        counts = manifest.get("records", {})

        if counts.get("full") != len(full_records):
            errors.append("Conteggio full incoerente.")

        if counts.get("train") != len(train_records):
            errors.append("Conteggio train incoerente.")

        if counts.get("val") != len(val_records):
            errors.append("Conteggio val incoerente.")

        if counts.get("test") != len(test_records):
            errors.append("Conteggio test incoerente.")

        if len(full_records) < 20:
            errors.append("Dataset V2.1 Natural troppo piccolo.")

        if not train_records or not val_records or not test_records:
            errors.append("Uno split è vuoto.")

        quality = manifest.get("quality", {})

        for key in [
            "dirty_token_hits",
            "numeric_code_hits",
            "metadata_shape_hits",
            "punctuation_start",
            "immediate_duplicates",
            "repeated_bigrams",
        ]:
            if quality.get(key, 1) != 0:
                errors.append(f"Manifest segnala problema qualità: {key}={quality.get(key)}")

    def _validate_records(self, records: List[Dict], errors: List[str]) -> None:
        seen_ids = set()

        for index, record in enumerate(records, start=1):
            natural_id = record.get("natural_id")
            text = str(record.get("text", "")).strip()
            split = record.get("split")

            if not natural_id:
                errors.append(f"Record {index}: natural_id mancante.")

            if natural_id in seen_ids:
                errors.append(f"Record {index}: natural_id duplicato.")

            seen_ids.add(natural_id)

            if split not in {"train", "val", "test"}:
                errors.append(f"Record {index}: split non valido.")

            if not text:
                errors.append(f"Record {index}: text vuoto.")
                continue

            words = self._word_tokens(text)

            if len(words) < 4:
                errors.append(f"Record {index}: troppo corto.")

            if len(words) > 34:
                errors.append(f"Record {index}: troppo lungo.")

            if text[0] in ".,;:!?-":
                errors.append(f"Record {index}: inizia con punteggiatura.")

            tokens = [token.lower() for token in self._tokenize(text)]
            lower_text = text.lower()

            if not any(token in self.CONTENT_HINTS for token in tokens):
                errors.append(f"Record {index}: nessun concetto di dominio.")

            for token in tokens:
                if token in self.DIRTY_TOKENS:
                    errors.append(f"Record {index}: token sporco: {token}")

                if self._is_numeric_code_token(token):
                    errors.append(f"Record {index}: codice numerico: {token}")

                if self._is_metadata_shape_token(token):
                    errors.append(f"Record {index}: metadata shape: {token}")

            for phrase in self.DIRTY_PHRASES:
                if phrase in lower_text:
                    errors.append(f"Record {index}: frase sporca: {phrase}")

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    errors.append(f"Record {index}: duplicato immediato: {left}")

            bigrams = list(zip(tokens, tokens[1:]))
            for pos in range(len(bigrams) - 1):
                if bigrams[pos] == bigrams[pos + 1]:
                    errors.append(f"Record {index}: bigramma ripetuto.")

            if ":" in text:
                errors.append(f"Record {index}: due punti residui.")

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _word_tokens(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù]+", text.lower(), flags=re.IGNORECASE)

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

    return f"""# Validazione Knowledge Dataset V2.1 Natural

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_knowledge_dataset_v21_natural.md"

    validator = KnowledgeDatasetV21NaturalValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Knowledge Dataset V2.1 Natural fallita")
        print(f"Report: {report_path}")

        for error in errors[:100]:
            print("-", error)

        if len(errors) > 100:
            print(f"... altri errori: {len(errors) - 100}")

        raise SystemExit(1)

    print("OK - Validazione Knowledge Dataset V2.1 Natural superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
