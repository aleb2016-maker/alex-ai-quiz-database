from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class KnowledgeDatasetV2CleanValidator:
    """
    Validatore Dataset V2 Clean.

    Controlla:
    - file presenti;
    - JSONL leggibile;
    - split non vuoti;
    - nessun token sporco;
    - nessuna etichetta tecnica tipo input/risposta/istruzione;
    - nessuna ripetizione immediata;
    - testo non troppo corto;
    - manifest coerente.
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

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        training_dir = root / "mini_llm" / "data" / "training"
        report_dir = root / "mini_llm" / "reports"

        full_path = training_dir / "knowledge_dataset_v2_clean.jsonl"
        train_path = training_dir / "knowledge_dataset_v2_clean_train.jsonl"
        val_path = training_dir / "knowledge_dataset_v2_clean_val.jsonl"
        test_path = training_dir / "knowledge_dataset_v2_clean_test.jsonl"
        manifest_path = training_dir / "knowledge_dataset_v2_clean_manifest.json"
        report_path = report_dir / "knowledge_dataset_builder_v2_clean_report.md"

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
        if manifest.get("versione") != "knowledge_dataset_v2_clean":
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

        if len(full_records) <= 0:
            errors.append("Dataset full vuoto.")

        if len(train_records) <= 0:
            errors.append("Dataset train vuoto.")

        if len(val_records) <= 0:
            errors.append("Dataset val vuoto.")

        if len(test_records) <= 0:
            errors.append("Dataset test vuoto.")

        quality = manifest.get("quality", {})

        if quality.get("dirty_token_hits", 1) != 0:
            errors.append("Manifest segnala dirty token hits.")

        if quality.get("immediate_duplicates", 1) != 0:
            errors.append("Manifest segnala duplicati immediati.")

        if quality.get("punctuation_start", 1) != 0:
            errors.append("Manifest segnala punteggiatura iniziale.")

    def _validate_records(self, records: List[Dict], errors: List[str]) -> None:
        seen_ids = set()

        for index, record in enumerate(records, start=1):
            clean_id = record.get("clean_id")
            text = str(record.get("text", "")).strip()

            if not clean_id:
                errors.append(f"Record {index}: clean_id mancante.")

            if clean_id in seen_ids:
                errors.append(f"Record {index}: clean_id duplicato: {clean_id}")

            seen_ids.add(clean_id)

            if not text:
                errors.append(f"Record {index}: text vuoto.")
                continue

            if len(text) < 18:
                errors.append(f"Record {index}: text troppo corto.")

            if text[0] in ".,;:!?-":
                errors.append(f"Record {index}: text inizia con punteggiatura.")

            tokens = [token.lower() for token in self._tokenize(text)]
            lower_text = text.lower()

            for token in tokens:
                if token in self.DIRTY_TOKENS:
                    errors.append(f"Record {index}: token sporco presente: {token}")

            for phrase in self.DIRTY_PHRASES:
                if phrase in lower_text:
                    errors.append(f"Record {index}: frase sporca presente: {phrase}")

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    errors.append(f"Record {index}: ripetizione immediata: {left}")

            if re.search(r"\b(input|output|risposta|istruzione|instruction)\b\s*:", lower_text):
                errors.append(f"Record {index}: etichetta tecnica residua.")

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text, flags=re.IGNORECASE)


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Knowledge Dataset V2 Clean

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_knowledge_dataset_v2_clean.md"

    validator = KnowledgeDatasetV2CleanValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Knowledge Dataset V2 Clean fallita")
        print(f"Report: {report_path}")

        for error in errors[:80]:
            print("-", error)

        if len(errors) > 80:
            print(f"... altri errori: {len(errors) - 80}")

        raise SystemExit(1)

    print("OK - Validazione Knowledge Dataset V2 Clean superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
