from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


class KnowledgeDatasetBuilderV1:
    """
    Knowledge Dataset Builder V1.

    Trasforma l'output pulito del Knowledge Engine V1.4 in un database JSONL
    utilizzabile per il futuro training di un mini LLM.

    Input atteso:
    - mini_llm/data/output/knowledge_engine_v14_semantic_output.json

    Output generati:
    - mini_llm/data/training/knowledge_dataset_v1.jsonl
    - mini_llm/data/training/knowledge_dataset_v1_train.jsonl
    - mini_llm/data/training/knowledge_dataset_v1_val.jsonl
    - mini_llm/data/training/knowledge_dataset_v1_test.jsonl
    - mini_llm/data/training/knowledge_dataset_v1_manifest.json
    - mini_llm/reports/knowledge_dataset_builder_v1_report.md
    """

    BAD_OUTPUT_STARTS = (
        "domanda:",
        "risposta corretta:",
        "# documento rag di test",
        "serve a recuperare informazioni",
        "questo principio riduce",
        "il metodo migliore è usare un password manager",
        "per ridurre il rischio malware è importante:",
    )

    BAD_OUTPUT_ENDINGS = (
        "può provare.",
        "potrebbe cifrare anche.",
    )

    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.records: List[Dict] = []
        self._seen_hashes = set()

    def build(self) -> List[Dict]:
        data = json.loads(self.source_path.read_text(encoding="utf-8"))

        category = data.get("categoria_documento", "")
        areas = data.get("aree_operative", [])
        micro_info = data.get("micro_informazioni", [])
        relevant_sentences = data.get("frasi_rilevanti", [])
        relations = data.get("relazioni_operative", [])
        training_items = data.get("dataset_training", [])

        self._add_category_record(category)
        self._add_area_records(category, areas)
        self._add_micro_information_records(micro_info, areas)
        self._add_relevant_sentence_records(relevant_sentences, areas)
        self._add_relation_records(relations)
        self._add_original_training_items(training_items)

        return self.records

    def _add_category_record(self, category: str) -> None:
        self._add_record(
            task="classificazione_documento",
            instruction="Riconosci la categoria operativa del documento.",
            input_text="Documento analizzato dal Knowledge Engine.",
            output_text=category,
            tags=["categoria", "classificazione", "knowledge_engine"],
            source_section="categoria_documento",
        )

    def _add_area_records(self, category: str, areas: List[str]) -> None:
        self._add_record(
            task="estrazione_aree_operative",
            instruction="Elenca le aree operative principali del documento.",
            input_text=f"Categoria documento: {category}",
            output_text=", ".join(areas),
            tags=["aree_operative", "estrazione", "knowledge_engine"],
            source_section="aree_operative",
        )

        for area in areas:
            self._add_record(
                task="normalizzazione_area_operativa",
                instruction="Trasforma l'area operativa in una voce pulita e riutilizzabile.",
                input_text=area,
                output_text=area,
                tags=["area_operativa", "normalizzazione"],
                source_section="aree_operative",
            )

            self._add_record(
                task="domanda_su_area_operativa",
                instruction="Rispondi in modo sintetico indicando l'area operativa richiesta.",
                input_text=f"Quale area operativa è collegata a: {area}?",
                output_text=area,
                tags=["area_operativa", "qa"],
                source_section="aree_operative",
            )

    def _add_micro_information_records(self, micro_info: List[str], areas: List[str]) -> None:
        for info in micro_info:
            matched_areas = self._match_areas(info, areas)
            area_text = ", ".join(matched_areas) if matched_areas else "generale"

            self._add_record(
                task="micro_informazione_operativa",
                instruction="Memorizza questa micro-informazione come conoscenza operativa pulita.",
                input_text=f"Aree collegate: {area_text}",
                output_text=info,
                tags=["micro_informazione", "conoscenza_operativa"],
                source_section="micro_informazioni",
            )

            self._add_record(
                task="riscrittura_per_riassunto",
                instruction="Riscrivi questa informazione in forma chiara per un riassunto.",
                input_text=info,
                output_text=info,
                tags=["riassunto", "riscrittura", "micro_informazione"],
                source_section="micro_informazioni",
            )

            self._add_record(
                task="qa_micro_informazione",
                instruction="Rispondi alla domanda usando la micro-informazione operativa.",
                input_text=f"Quale informazione utile riguarda: {area_text}?",
                output_text=info,
                tags=["qa", "micro_informazione", "conoscenza_operativa"],
                source_section="micro_informazioni",
            )

    def _add_relevant_sentence_records(self, sentences: List[str], areas: List[str]) -> None:
        for sentence in sentences:
            matched_areas = self._match_areas(sentence, areas)
            area_text = ", ".join(matched_areas) if matched_areas else "generale"

            self._add_record(
                task="frase_rilevante",
                instruction="Estrai una frase rilevante e completa dal documento.",
                input_text=f"Area operativa: {area_text}",
                output_text=sentence,
                tags=["frase_rilevante", "estrazione"],
                source_section="frasi_rilevanti",
            )

            self._add_record(
                task="domanda_risposta_operativa",
                instruction="Rispondi alla domanda usando una frase chiara del documento.",
                input_text=f"Quale informazione operativa è importante per: {area_text}?",
                output_text=sentence,
                tags=["qa", "domanda_risposta", "conoscenza_operativa"],
                source_section="frasi_rilevanti",
            )

            self._add_record(
                task="riassunto_frase_rilevante",
                instruction="Trasforma la frase rilevante in una voce utile per un riassunto operativo.",
                input_text=f"Area operativa: {area_text}",
                output_text=sentence,
                tags=["riassunto", "frase_rilevante"],
                source_section="frasi_rilevanti",
            )

    def _add_relation_records(self, relations: List[Dict[str, str]]) -> None:
        for relation in relations:
            area = relation.get("area", "").strip()
            linked = relation.get("elemento_collegato", "").strip()
            relation_type = relation.get("tipo", "").strip() or "relazione_operativa"

            if not area or not linked:
                continue

            self._add_record(
                task="relazione_operativa",
                instruction="Descrivi una relazione operativa tra due elementi del documento.",
                input_text=f"Elemento A: {area}\nElemento B: {linked}",
                output_text=f"{area} è collegato a {linked}. Tipo relazione: {relation_type}.",
                tags=["relazione", "knowledge_graph", "conoscenza_operativa"],
                source_section="relazioni_operative",
            )

    def _add_original_training_items(self, training_items: List[Dict[str, str]]) -> None:
        for item in training_items:
            item_input = item.get("input", "").strip()
            item_output = item.get("output", "").strip()

            if not item_input or not item_output:
                continue

            self._add_record(
                task="training_item_originale_v14",
                instruction=item_input,
                input_text="Output Knowledge Engine V1.4",
                output_text=item_output,
                tags=["training_originale", "knowledge_engine_v14"],
                source_section="dataset_training",
            )

    def _add_record(
        self,
        task: str,
        instruction: str,
        input_text: str,
        output_text: str,
        tags: List[str],
        source_section: str,
    ) -> None:
        instruction = self._clean_text(instruction)
        input_text = self._clean_text(input_text)
        output_text = self._clean_text(output_text)

        if not instruction or not output_text:
            return

        if self._has_bad_pattern(output_text):
            return

        record_hash = self._hash_record(task, instruction, input_text, output_text)

        if record_hash in self._seen_hashes:
            return

        self._seen_hashes.add(record_hash)

        record_id = f"ke-dataset-v1-{len(self.records) + 1:05d}"

        text = (
            f"### Istruzione\n{instruction}\n\n"
            f"### Input\n{input_text}\n\n"
            f"### Risposta\n{output_text}"
        )

        record = {
            "id": record_id,
            "source": "knowledge_engine_v14_semantic_output",
            "source_file": str(self.source_path),
            "source_section": source_section,
            "task": task,
            "instruction": instruction,
            "input": input_text,
            "output": output_text,
            "text": text,
            "tags": tags,
            "quality": {
                "validated": True,
                "language": "it",
                "usable_for_training": True,
            },
        }

        self.records.append(record)

    def _match_areas(self, text: str, areas: List[str]) -> List[str]:
        lowered = text.lower()
        matched = []

        for area in areas:
            if area.lower() in lowered:
                matched.append(area)

        return matched

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text).strip().split())

    def _has_bad_pattern(self, text: str) -> bool:
        lowered = text.lower().strip()

        for pattern in self.BAD_OUTPUT_STARTS:
            if lowered.startswith(pattern):
                return True

        for pattern in self.BAD_OUTPUT_ENDINGS:
            if lowered.endswith(pattern):
                return True

        return False

    def _hash_record(
        self,
        task: str,
        instruction: str,
        input_text: str,
        output_text: str,
    ) -> str:
        raw = f"{task}|{instruction}|{input_text}|{output_text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def split_dataset(records: List[Dict], seed: int = 42) -> Dict[str, List[Dict]]:
    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)

    if total < 10:
        return {
            "train": shuffled,
            "val": [],
            "test": [],
        }

    val_count = max(1, round(total * 0.10))
    test_count = max(1, round(total * 0.10))
    train_count = total - val_count - test_count

    return {
        "train": shuffled[:train_count],
        "val": shuffled[train_count:train_count + val_count],
        "test": shuffled[train_count + val_count:],
    }


def write_jsonl(path: Path, records: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_manifest(
    source_path: Path,
    full_path: Path,
    train_path: Path,
    val_path: Path,
    test_path: Path,
    records: List[Dict],
    splits: Dict[str, List[Dict]],
) -> Dict:
    task_counter = Counter(record["task"] for record in records)

    return {
        "versione": "knowledge_dataset_builder_v1",
        "source_path": str(source_path),
        "outputs": {
            "full": str(full_path),
            "train": str(train_path),
            "val": str(val_path),
            "test": str(test_path),
        },
        "counts": {
            "total_records": len(records),
            "train_records": len(splits["train"]),
            "val_records": len(splits["val"]),
            "test_records": len(splits["test"]),
        },
        "tasks": dict(task_counter),
        "format": "jsonl",
        "language": "it",
        "status": "generated",
    }


def build_report(manifest: Dict, sample_records: List[Dict]) -> str:
    samples = []

    for record in sample_records[:8]:
        samples.append(
            f"### {record['id']} - {record['task']}\n\n"
            f"**Istruzione:** {record['instruction']}\n\n"
            f"**Input:** {record['input']}\n\n"
            f"**Output:** {record['output']}\n"
        )

    sample_block = "\n---\n".join(samples) if samples else "Nessun esempio disponibile."
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)

    return f"""# Report Knowledge Dataset Builder V1

## Manifest
{manifest_text}

## Esempi record
{sample_block}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Knowledge Dataset Builder V1"
    )

    parser.add_argument(
        "--source",
        default="mini_llm/data/output/knowledge_engine_v14_semantic_output.json",
        help="File JSON prodotto dal Knowledge Engine V1.4.",
    )

    parser.add_argument(
        "--output-dir",
        default="mini_llm/data/training",
        help="Cartella output dataset.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/knowledge_dataset_builder_v1_report.md",
        help="Report Markdown.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    source_path = (root / args.source).resolve()
    output_dir = (root / args.output_dir).resolve()
    report_path = (root / args.report).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"File sorgente non trovato: {source_path}")

    builder = KnowledgeDatasetBuilderV1(source_path=source_path)
    records = builder.build()

    if not records:
        raise ValueError("Nessun record generato dal Dataset Builder V1.")

    splits = split_dataset(records)

    full_path = output_dir / "knowledge_dataset_v1.jsonl"
    train_path = output_dir / "knowledge_dataset_v1_train.jsonl"
    val_path = output_dir / "knowledge_dataset_v1_val.jsonl"
    test_path = output_dir / "knowledge_dataset_v1_test.jsonl"
    manifest_path = output_dir / "knowledge_dataset_v1_manifest.json"

    write_jsonl(full_path, records)
    write_jsonl(train_path, splits["train"])
    write_jsonl(val_path, splits["val"])
    write_jsonl(test_path, splits["test"])

    manifest = build_manifest(
        source_path=source_path,
        full_path=full_path,
        train_path=train_path,
        val_path=val_path,
        test_path=test_path,
        records=records,
        splits=splits,
    )

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(manifest=manifest, sample_records=records),
        encoding="utf-8",
    )

    print("OK - Knowledge Dataset Builder V1 completato")
    print(f"Sorgente: {source_path}")
    print(f"Dataset completo: {full_path}")
    print(f"Train: {train_path}")
    print(f"Validation: {val_path}")
    print(f"Test: {test_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Report: {report_path}")
    print(f"Record totali: {len(records)}")
    print(f"Split: train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}")


if __name__ == "__main__":
    main()
