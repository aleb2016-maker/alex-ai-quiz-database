from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class KnowledgeDatasetV1Validator:
    """
    Validatore Knowledge Dataset V1.

    Controlla:
    - JSONL leggibile;
    - campi obbligatori;
    - ID unici;
    - output non vuoti;
    - assenza pattern sporchi;
    - split coerenti;
    - presenza task obbligatori;
    - presenza frasi riparate importanti.
    """

    REQUIRED_FIELDS = [
        "id",
        "source",
        "source_section",
        "task",
        "instruction",
        "input",
        "output",
        "text",
        "tags",
        "quality",
    ]

    REQUIRED_TASKS = [
        "classificazione_documento",
        "estrazione_aree_operative",
        "normalizzazione_area_operativa",
        "micro_informazione_operativa",
        "riscrittura_per_riassunto",
        "frase_rilevante",
        "domanda_risposta_operativa",
        "relazione_operativa",
        "training_item_originale_v14",
    ]

    REQUIRED_SENTENCES = [
        "Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.",
        "Il principio del minimo privilegio riduce il danno possibile in caso di errore o compromissione di un account.",
        "Il metodo migliore per gestire password sicure è usare un password manager.",
    ]

    BAD_PATTERNS = [
        r"^\s*Domanda:",
        r"^\s*Risposta corretta:",
        r"^\s*#\s*Documento RAG di test",
        r"^\s*Serve a recuperare informazioni",
        r"^\s*Questo principio riduce",
        r"^\s*Il metodo migliore è usare un password manager\.?$",
        r"^\s*Per ridurre il rischio malware è importante:\s*$",
        r"può provare\.$",
        r"potrebbe cifrare anche\.$",
    ]

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        full_path = root / "mini_llm" / "data" / "training" / "knowledge_dataset_v1.jsonl"
        train_path = root / "mini_llm" / "data" / "training" / "knowledge_dataset_v1_train.jsonl"
        val_path = root / "mini_llm" / "data" / "training" / "knowledge_dataset_v1_val.jsonl"
        test_path = root / "mini_llm" / "data" / "training" / "knowledge_dataset_v1_test.jsonl"
        manifest_path = root / "mini_llm" / "data" / "training" / "knowledge_dataset_v1_manifest.json"

        for path in [full_path, train_path, val_path, test_path, manifest_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        full_records = self._read_jsonl(full_path, errors)
        train_records = self._read_jsonl(train_path, errors)
        val_records = self._read_jsonl(val_path, errors)
        test_records = self._read_jsonl(test_path, errors)

        if errors:
            return errors

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self._validate_records(full_records, errors)
        self._validate_splits(full_records, train_records, val_records, test_records, manifest, errors)
        self._validate_tasks(full_records, errors)
        self._validate_required_sentences(full_records, errors)
        self._validate_bad_patterns(full_records, errors)

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
                    errors.append(f"JSON non valido in {path}:{line_number} -> {error}")

        return records

    def _validate_records(self, records: List[Dict], errors: List[str]) -> None:
        if len(records) < 40:
            errors.append(f"Dataset troppo piccolo: {len(records)} record. Minimo richiesto: 40.")

        ids = set()

        for index, record in enumerate(records):
            for field in self.REQUIRED_FIELDS:
                if field not in record:
                    errors.append(f"Record {index}: campo mancante: {field}")

            record_id = record.get("id", "")

            if not record_id:
                errors.append(f"Record {index}: id vuoto.")

            if record_id in ids:
                errors.append(f"ID duplicato: {record_id}")

            ids.add(record_id)

            instruction = record.get("instruction", "").strip()
            output = record.get("output", "").strip()
            text = record.get("text", "").strip()
            quality = record.get("quality", {})

            if not instruction:
                errors.append(f"Record {record_id}: instruction vuota.")

            if not output:
                errors.append(f"Record {record_id}: output vuoto.")

            if "### Istruzione" not in text or "### Risposta" not in text:
                errors.append(f"Record {record_id}: campo text non formattato correttamente.")

            if not quality.get("validated"):
                errors.append(f"Record {record_id}: quality.validated non è True.")

            if not quality.get("usable_for_training"):
                errors.append(f"Record {record_id}: usable_for_training non è True.")

    def _validate_splits(
        self,
        full_records: List[Dict],
        train_records: List[Dict],
        val_records: List[Dict],
        test_records: List[Dict],
        manifest: Dict,
        errors: List[str],
    ) -> None:
        total_split = len(train_records) + len(val_records) + len(test_records)

        if total_split != len(full_records):
            errors.append(
                f"Split incoerenti: train+val+test={total_split}, full={len(full_records)}"
            )

        counts = manifest.get("counts", {})

        if counts.get("total_records") != len(full_records):
            errors.append("Manifest incoerente: total_records errato.")

        if counts.get("train_records") != len(train_records):
            errors.append("Manifest incoerente: train_records errato.")

        if counts.get("val_records") != len(val_records):
            errors.append("Manifest incoerente: val_records errato.")

        if counts.get("test_records") != len(test_records):
            errors.append("Manifest incoerente: test_records errato.")

    def _validate_tasks(self, records: List[Dict], errors: List[str]) -> None:
        tasks = {record.get("task", "") for record in records}

        for required_task in self.REQUIRED_TASKS:
            if required_task not in tasks:
                errors.append(f"Task obbligatorio mancante: {required_task}")

    def _validate_required_sentences(self, records: List[Dict], errors: List[str]) -> None:
        all_text = "\n".join(record.get("output", "") for record in records)

        for sentence in self.REQUIRED_SENTENCES:
            if sentence not in all_text:
                errors.append(f"Frase obbligatoria mancante nel dataset: {sentence}")

    def _validate_bad_patterns(self, records: List[Dict], errors: List[str]) -> None:
        for record in records:
            record_id = record.get("id", "")
            texts = [
                record.get("instruction", ""),
                record.get("input", ""),
                record.get("output", ""),
                record.get("text", ""),
            ]

            for text in texts:
                chunks = self._split_for_validation(text)

                for chunk in chunks:
                    for pattern in self.BAD_PATTERNS:
                        if re.search(pattern, chunk, flags=re.IGNORECASE):
                            errors.append(
                                f"Pattern sporco nel record {record_id}: {pattern} -> {chunk}"
                            )

    def _split_for_validation(self, text: str) -> List[str]:
        chunks: List[str] = []

        for piece in text.split(";"):
            piece = piece.strip()

            if not piece:
                continue

            subpieces = re.split(r"(?<=[.!?])\s+", piece)

            for subpiece in subpieces:
                subpiece = subpiece.strip()

                if subpiece:
                    chunks.append(subpiece)

        return chunks


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"

    error_block = (
        "Nessun errore rilevato."
        if not errors
        else "\n".join(f"- {error}" for error in errors)
    )

    return f"""# Validazione Knowledge Dataset V1

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_knowledge_dataset_v1.md"

    validator = KnowledgeDatasetV1Validator()
    errors = validator.validate(root=root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(errors=errors, root=root),
        encoding="utf-8",
    )

    if errors:
        print("ERRORE - Validazione Knowledge Dataset V1 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Knowledge Dataset V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
