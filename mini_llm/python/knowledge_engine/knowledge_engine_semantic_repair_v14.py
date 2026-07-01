from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


class KnowledgeSemanticRepairV14:
    """
    Knowledge Engine Semantic Repair V1.4.

    Questo modulo prende l'output V1.3 e corregge frasi concluse
    grammaticalmente ma ambigue semanticamente.

    Esempio:
    "Serve a recuperare informazioni..."
    diventa:
    "Il backup serve a recuperare informazioni..."
    """

    def repair(self, strict_v13: Dict) -> Dict:
        result = dict(strict_v13)

        semantic_repairs: List[Dict[str, str]] = []

        result["micro_informazioni"] = self._repair_text_list(
            items=result.get("micro_informazioni", []),
            semantic_repairs=semantic_repairs,
        )

        result["frasi_rilevanti"] = self._repair_text_list(
            items=result.get("frasi_rilevanti", []),
            semantic_repairs=semantic_repairs,
        )

        result["dataset_training"] = self._repair_dataset_training(
            items=result.get("dataset_training", []),
            semantic_repairs=semantic_repairs,
        )

        result["relazioni_operative"] = self._repair_relations(
            relations=result.get("relazioni_operative", []),
            semantic_repairs=semantic_repairs,
        )

        residual_problems = self._find_semantic_residual_problems(result)

        result["versione"] = "knowledge_engine_semantic_repair_v14"

        previous_quality = result.get("quality_report", {})

        result["quality_report"] = {
            **previous_quality,
            "semantic_repairs_v14": semantic_repairs,
            "problemi_semantici_residui_v14": residual_problems,
        }

        previous_stats = result.get("statistiche", {})

        result["statistiche"] = {
            **previous_stats,
            "semantic_repairs_v14": len(semantic_repairs),
            "problemi_semantici_residui_v14": len(residual_problems),
        }

        return result

    def _repair_text_list(
        self,
        items: List[str],
        semantic_repairs: List[Dict[str, str]],
    ) -> List[str]:
        repaired_items: List[str] = []

        for item in items:
            repaired = self._repair_sentence(item)

            if repaired != item:
                semantic_repairs.append({
                    "prima": item,
                    "dopo": repaired,
                })

            if repaired not in repaired_items:
                repaired_items.append(repaired)

        return repaired_items

    def _repair_dataset_training(
        self,
        items: List[Dict[str, str]],
        semantic_repairs: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        repaired_items: List[Dict[str, str]] = []

        for item in items:
            new_item = dict(item)
            output = new_item.get("output", "")

            repaired_output = self._repair_long_text(output)

            if repaired_output != output:
                semantic_repairs.append({
                    "prima": output,
                    "dopo": repaired_output,
                })

            new_item["output"] = repaired_output
            repaired_items.append(new_item)

        return repaired_items

    def _repair_relations(
        self,
        relations: List[Dict[str, str]],
        semantic_repairs: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        repaired_relations: List[Dict[str, str]] = []

        for relation in relations:
            new_relation = dict(relation)

            linked = new_relation.get("elemento_collegato", "")
            repaired_linked = self._repair_sentence(linked)

            if repaired_linked != linked:
                semantic_repairs.append({
                    "prima": linked,
                    "dopo": repaired_linked,
                })

            new_relation["elemento_collegato"] = repaired_linked

            if new_relation not in repaired_relations:
                repaired_relations.append(new_relation)

        return repaired_relations

    def _repair_long_text(self, text: str) -> str:
        if not text:
            return text

        # Ripara frasi separate da punto + spazio.
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        repaired_parts = [self._repair_sentence(part) for part in parts if part.strip()]

        repaired = " ".join(repaired_parts)

        # Ripara anche blocchi separati da punto e virgola usati nel dataset.
        chunks = [chunk.strip() for chunk in repaired.split(";")]
        repaired_chunks = [self._repair_sentence(chunk) for chunk in chunks if chunk]

        if len(repaired_chunks) > 1:
            return "; ".join(repaired_chunks)

        return repaired

    def _repair_sentence(self, sentence: str) -> str:
        text = sentence.strip()

        if not text:
            return text

        lowered = text.lower()

        # Caso trovato nel report:
        # "Serve a recuperare informazioni..." senza soggetto.
        if lowered.startswith("serve a recuperare informazioni"):
            return self._ensure_final_dot(
                "Il backup serve a recuperare informazioni"
                + text[len("Serve a recuperare informazioni"):]
            )

        # Caso generico: "Serve a ..." senza soggetto.
        if lowered.startswith("serve a "):
            return self._ensure_final_dot(
                "Questa misura operativa " + text[0].lower() + text[1:]
            )

        # Frase formalmente corretta ma vaga: "Questo principio..."
        if lowered.startswith("questo principio riduce il danno"):
            return self._ensure_final_dot(
                text.replace(
                    "Questo principio",
                    "Il principio del minimo privilegio",
                    1,
                )
            )

        if lowered.startswith("questo principio"):
            return self._ensure_final_dot(
                text.replace(
                    "Questo principio",
                    "Questo principio operativo",
                    1,
                )
            )

        # Frase troppo generica.
        if lowered == "il metodo migliore è usare un password manager.":
            return "Il metodo migliore per gestire password sicure è usare un password manager."

        if lowered == "il metodo migliore è usare un password manager":
            return "Il metodo migliore per gestire password sicure è usare un password manager."

        return text

    def _ensure_final_dot(self, text: str) -> str:
        text = text.strip()

        if not text.endswith((".", "!", "?")):
            text += "."

        return text

    def _find_semantic_residual_problems(self, result: Dict) -> List[str]:
        problems: List[str] = []
        texts: List[str] = []

        texts.extend(result.get("micro_informazioni", []))
        texts.extend(result.get("frasi_rilevanti", []))

        for item in result.get("dataset_training", []):
            texts.append(item.get("output", ""))

        for relation in result.get("relazioni_operative", []):
            texts.append(relation.get("elemento_collegato", ""))

        weak_starts = (
            "Serve a ",
            "Questo principio ",
            "Il metodo migliore è ",
        )

        for text in texts:
            for weak_start in weak_starts:
                if weak_start in text:
                    problems.append(f"Possibile frase semanticamente ambigua: {text}")

        return self._dedupe_keep_order(problems)

    def _dedupe_keep_order(self, items: List[str]) -> List[str]:
        result: List[str] = []
        seen = set()

        for item in items:
            key = item.lower().strip()

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result


def build_report(result: Dict, input_json: Path, output_json: Path) -> str:
    def list_block(items: List[str]) -> str:
        if not items:
            return "- Nessun elemento."
        return "\n".join(f"- {item}" for item in items)

    def relation_block(items: List[Dict[str, str]]) -> str:
        if not items:
            return "- Nessuna relazione."
        return "\n".join(
            f"- {item.get('area', '')} -> {item.get('elemento_collegato', '')} ({item.get('tipo', '')})"
            for item in items
        )

    return f"""# Report Knowledge Engine Semantic Repair V1.4

## Input JSON
{input_json}

## Output JSON
{output_json}

## Categoria documento
{result["categoria_documento"]}

## Statistiche
{json.dumps(result["statistiche"], ensure_ascii=False, indent=2)}

## Aree operative
{list_block(result["aree_operative"])}

## Micro-informazioni
{list_block(result["micro_informazioni"])}

## Frasi rilevanti
{list_block(result["frasi_rilevanti"])}

## Relazioni operative
{relation_block(result["relazioni_operative"])}

## Dataset training
{json.dumps(result["dataset_training"], ensure_ascii=False, indent=2)}

## Report qualità
{json.dumps(result["quality_report"], ensure_ascii=False, indent=2)}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Knowledge Engine Semantic Repair V1.4"
    )

    parser.add_argument(
        "--input-json",
        default="mini_llm/data/output/knowledge_engine_v13_strict_output.json",
        help="JSON V1.3 strict.",
    )

    parser.add_argument(
        "--output-json",
        default="mini_llm/data/output/knowledge_engine_v14_semantic_output.json",
        help="JSON V1.4 semantic.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/knowledge_engine_v14_semantic_report.md",
        help="Report Markdown V1.4.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    input_json = (root / args.input_json).resolve()
    output_json = (root / args.output_json).resolve()
    report_path = (root / args.report).resolve()

    if not input_json.exists():
        raise FileNotFoundError(f"JSON V1.3 non trovato: {input_json}")

    strict_v13 = json.loads(input_json.read_text(encoding="utf-8"))

    repair_engine = KnowledgeSemanticRepairV14()
    result = repair_engine.repair(strict_v13=strict_v13)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_path.write_text(
        build_report(
            result=result,
            input_json=input_json,
            output_json=output_json,
        ),
        encoding="utf-8",
    )

    print("OK - Knowledge Engine Semantic Repair V1.4 completato")
    print(f"Input JSON: {input_json}")
    print(f"Output JSON V1.4: {output_json}")
    print(f"Report V1.4: {report_path}")
    print(f"Statistiche: {result['statistiche']}")

    problems = result["quality_report"]["problemi_semantici_residui_v14"]

    if problems:
        print("ATTENZIONE - Problemi semantici residui:")
        for problem in problems[:12]:
            print("-", problem)
    else:
        print("OK - Nessun problema semantico residuo rilevato.")


if __name__ == "__main__":
    main()
