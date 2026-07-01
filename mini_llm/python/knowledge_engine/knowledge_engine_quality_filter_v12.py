from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class KnowledgeQualityFilterV12:
    """
    Knowledge Quality Filter V1.2.

    Questo modulo prende l'output del Knowledge Engine V1.1 e lo ripulisce.

    Obiettivi:
    - rimuovere Domanda/Risposta corretta;
    - rimuovere titoli Markdown e sezioni di test;
    - rimuovere frasi tagliate o incomplete;
    - ridurre duplicati e relazioni ripetute;
    - migliorare aree operative;
    - creare un JSON più adatto a riassunti, card e futuro training LLM.
    """

    BAD_PREFIXES = (
        "domanda:",
        "risposta corretta:",
        "#",
        "##",
        "###",
    )

    BAD_CONTAINS = (
        "documento rag di test",
        "uso del documento",
        "motore rag",
        "mini-corsi",
        "mini corsi",
        "generare domande",
        "questo documento può essere usato",
        "questo documento puo essere usato",
    )

    INCOMPLETE_ENDINGS = (
        ":",
        ",",
        ";",
        " o.",
        " e.",
        " di.",
        " che.",
        " con.",
        " per.",
        " in.",
        " su.",
        " al.",
        " alla.",
        " del.",
        " della.",
        " dei.",
        " delle.",
    )

    WEAK_LAST_WORDS = {
        "o", "e", "di", "a", "da", "con", "per", "in", "su", "al", "alla",
        "del", "della", "dei", "delle", "che", "come", "se", "un", "una",
        "uno", "il", "lo", "la", "gli", "le", "i"
    }

    DOMAIN_AREAS = [
        "sicurezza informatica",
        "password sicure",
        "password manager",
        "protezione dei dati",
        "dati sensibili",
        "autenticazione a due fattori",
        "codici temporanei",
        "account online",
        "account amministrativi",
        "phishing",
        "malware",
        "ransomware",
        "backup regolari",
        "aggiornamenti software",
        "allegati inattesi",
        "software non autorizzato",
        "protezione endpoint",
        "privilegi amministrativi",
        "permessi utente",
        "reti wi-fi pubbliche",
    ]

    WEAK_AREAS = {
        "password",
        "account",
        "sistema",
        "sistemi",
        "utente",
        "utenti",
        "dati",
        "informazioni",
        "rischio",
        "software",
    }

    def refine(self, raw_result: Dict, source_text: str) -> Dict:
        category = raw_result.get("categoria_documento", "documento_generico")

        source_units = self._extract_units_from_source(source_text)

        areas = self._build_clean_areas(
            raw_areas=raw_result.get("aree_operative", []),
            source_text=source_text,
        )

        micro_info = self._build_clean_micro_info(
            raw_items=raw_result.get("micro_informazioni", []),
            source_units=source_units,
            areas=areas,
        )

        relevant_sentences = self._build_clean_relevant_sentences(
            raw_items=raw_result.get("frasi_rilevanti", []),
            source_units=source_units,
            areas=areas,
        )

        relations = self._build_clean_relations(
            raw_relations=raw_result.get("relazioni_operative", []),
            areas=areas,
            relevant_sentences=relevant_sentences,
        )

        dataset_training = self._build_clean_training_items(
            category=category,
            areas=areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
        )

        quality_report = self._build_quality_report(
            raw_result=raw_result,
            areas=areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
            relations=relations,
            dataset_training=dataset_training,
        )

        return {
            "versione": "knowledge_engine_quality_filter_v12",
            "categoria_documento": category,
            "aree_operative": areas,
            "micro_informazioni": micro_info,
            "frasi_rilevanti": relevant_sentences,
            "relazioni_operative": relations,
            "dataset_training": dataset_training,
            "quality_report": quality_report,
            "statistiche": {
                "numero_aree_operative": len(areas),
                "numero_micro_informazioni": len(micro_info),
                "numero_frasi_rilevanti": len(relevant_sentences),
                "numero_relazioni_operative": len(relations),
                "numero_training_items": len(dataset_training),
                "problemi_residui": len(quality_report["problemi_residui"]),
            },
        }

    def _extract_units_from_source(self, source_text: str) -> List[str]:
        text = source_text.replace("\r", "\n")
        units: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            line = re.sub(r"^[-•*]\s*", "", line).strip()

            if self._is_bad_text(line):
                continue

            parts = re.split(r"(?<=[.!?])\s+", line)

            for part in parts:
                part = part.strip()

                if self._is_usable_information(part):
                    units.append(part)

        return self._dedupe_keep_order(units)

    def _build_clean_areas(self, raw_areas: List[str], source_text: str, limit: int = 14) -> List[str]:
        lowered_source = source_text.lower()
        areas: List[str] = []

        for area in self.DOMAIN_AREAS:
            if area in lowered_source:
                areas.append(area)

        for area in raw_areas:
            normalized = self._normalize(area)

            if not normalized:
                continue

            if normalized in self.WEAK_AREAS:
                continue

            if self._is_bad_text(normalized):
                continue

            if normalized not in areas:
                areas.append(normalized)

        return areas[:limit]

    def _build_clean_micro_info(
        self,
        raw_items: List[str],
        source_units: List[str],
        areas: List[str],
        limit: int = 24,
    ) -> List[str]:
        candidates: List[Tuple[int, str]] = []

        for item in raw_items:
            item = self._clean_item(item)

            if self._is_usable_information(item):
                candidates.append((self._score_item(item, areas), item))

        for unit in source_units:
            if self._mentions_any_area(unit, areas):
                candidates.append((self._score_item(unit, areas), unit))

        candidates.sort(key=lambda item: item[0], reverse=True)

        result: List[str] = []

        for _score, item in candidates:
            if self._is_too_similar(item, result):
                continue

            result.append(item)

            if len(result) >= limit:
                break

        return result

    def _build_clean_relevant_sentences(
        self,
        raw_items: List[str],
        source_units: List[str],
        areas: List[str],
        limit: int = 10,
    ) -> List[str]:
        candidates: List[Tuple[int, str]] = []

        for item in raw_items:
            item = self._clean_item(item)

            if self._is_usable_information(item):
                candidates.append((self._score_item(item, areas), item))

        for unit in source_units:
            if self._mentions_any_area(unit, areas):
                candidates.append((self._score_item(unit, areas), unit))

        candidates.sort(key=lambda item: item[0], reverse=True)

        selected: List[str] = []

        for _score, item in candidates:
            if self._is_too_similar(item, selected):
                continue

            selected.append(item)

            if len(selected) >= limit:
                break

        return selected

    def _build_clean_relations(
        self,
        raw_relations: List[Dict[str, str]],
        areas: List[str],
        relevant_sentences: List[str],
        limit: int = 14,
    ) -> List[Dict[str, str]]:
        relations: List[Dict[str, str]] = []
        seen = set()

        for relation in raw_relations:
            area = self._normalize(relation.get("area", ""))
            linked = self._normalize(relation.get("elemento_collegato", ""))
            relation_type = relation.get("tipo", "relazione_operativa")

            if not area or not linked:
                continue

            if area in self.WEAK_AREAS:
                continue

            if self._is_bad_text(area) or self._is_bad_text(linked):
                continue

            if not self._is_usable_relation_element(linked, areas):
                continue

            key = (area, linked, relation_type)

            if key in seen:
                continue

            seen.add(key)

            relations.append({
                "area": area,
                "elemento_collegato": linked,
                "tipo": relation_type,
            })

            if len(relations) >= limit:
                return relations

        for sentence in relevant_sentences:
            present_areas = [area for area in areas if area in sentence.lower()]

            if len(present_areas) >= 2:
                for index in range(len(present_areas) - 1):
                    area = present_areas[index]
                    linked = present_areas[index + 1]
                    key = (area, linked, "co_presenza_pulita")

                    if key in seen:
                        continue

                    seen.add(key)

                    relations.append({
                        "area": area,
                        "elemento_collegato": linked,
                        "tipo": "co_presenza_pulita",
                    })

                    if len(relations) >= limit:
                        return relations

        return relations

    def _build_clean_training_items(
        self,
        category: str,
        areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
    ) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = [
            {
                "input": "Riconosci la categoria operativa del documento.",
                "output": category,
            },
            {
                "input": "Elenca le aree operative principali del documento.",
                "output": ", ".join(areas),
            },
            {
                "input": "Elenca micro-informazioni operative pulite e utilizzabili.",
                "output": "; ".join(micro_info[:10]),
            },
        ]

        for sentence in relevant_sentences[:5]:
            items.append({
                "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
                "output": sentence,
            })

        if relevant_sentences:
            items.append({
                "input": "Crea una sintesi operativa breve del documento.",
                "output": " ".join(relevant_sentences[:4]),
            })

        return items

    def _build_quality_report(
        self,
        raw_result: Dict,
        areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
        relations: List[Dict[str, str]],
        dataset_training: List[Dict[str, str]],
    ) -> Dict:
        all_texts: List[str] = []
        all_texts.extend(areas)
        all_texts.extend(micro_info)
        all_texts.extend(relevant_sentences)

        for relation in relations:
            all_texts.append(relation.get("area", ""))
            all_texts.append(relation.get("elemento_collegato", ""))

        for item in dataset_training:
            all_texts.append(item.get("input", ""))
            all_texts.append(item.get("output", ""))

        residual_problems = []

        for text in all_texts:
            if self._is_bad_text(text):
                residual_problems.append(f"Testo sporco residuo: {text}")

            if self._looks_incomplete(text):
                residual_problems.append(f"Testo incompleto residuo: {text}")

        return {
            "aree_input_v11": len(raw_result.get("aree_operative", [])),
            "micro_input_v11": len(raw_result.get("micro_informazioni", [])),
            "frasi_input_v11": len(raw_result.get("frasi_rilevanti", [])),
            "aree_output_v12": len(areas),
            "micro_output_v12": len(micro_info),
            "frasi_output_v12": len(relevant_sentences),
            "relazioni_output_v12": len(relations),
            "training_items_output_v12": len(dataset_training),
            "problemi_residui": residual_problems,
        }

    def _clean_item(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"^[-•*]\s*", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize(self, text: str) -> str:
        return self._clean_item(text).lower()

    def _is_bad_text(self, text: str) -> bool:
        lowered = text.lower().strip()

        if not lowered:
            return True

        if lowered.startswith(self.BAD_PREFIXES):
            return True

        if any(marker in lowered for marker in self.BAD_CONTAINS):
            return True

        return False

    def _looks_incomplete(self, text: str) -> bool:
        stripped = text.strip()
        lowered = stripped.lower()

        if lowered.endswith(self.INCOMPLETE_ENDINGS):
            return True

        words = re.findall(r"\b\w+\b", lowered)

        if words and words[-1] in self.WEAK_LAST_WORDS:
            return True

        if stripped.endswith("?"):
            return True

        return False

    def _is_usable_information(self, text: str) -> bool:
        text = self._clean_item(text)

        if self._is_bad_text(text):
            return False

        if self._looks_incomplete(text):
            return False

        words_count = len(text.split())

        if words_count < 6:
            return False

        if words_count > 45:
            return False

        if text[0].islower():
            return False

        return True

    def _is_usable_relation_element(self, text: str, areas: List[str]) -> bool:
        if text in areas:
            return True

        if self._is_usable_information(text):
            return True

        return False

    def _mentions_any_area(self, text: str, areas: List[str]) -> bool:
        lowered = text.lower()
        return any(area in lowered for area in areas)

    def _score_item(self, text: str, areas: List[str]) -> int:
        lowered = text.lower()
        score = 0

        for area in areas:
            if area in lowered:
                score += 4

        strong_markers = [
            "riduce", "rischio", "sicura", "sicurezza", "protegge", "proteggere",
            "dati", "account", "password", "backup", "malware", "ransomware",
            "phishing", "autenticazione", "permessi", "privilegi", "aggiornamenti"
        ]

        for marker in strong_markers:
            if marker in lowered:
                score += 1

        return score

    def _is_too_similar(self, candidate: str, existing_items: List[str]) -> bool:
        candidate_set = set(candidate.lower().split())

        for item in existing_items:
            item_set = set(item.lower().split())

            if not candidate_set or not item_set:
                continue

            overlap = len(candidate_set & item_set) / max(1, min(len(candidate_set), len(item_set)))

            if overlap >= 0.82:
                return True

        return False

    def _dedupe_keep_order(self, items: List[str]) -> List[str]:
        result: List[str] = []
        seen = set()

        for item in items:
            normalized = item.lower().strip()

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(item)

        return result


def build_report(result: Dict, input_json: Path, source_path: Path, output_json: Path) -> str:
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

    return f"""# Report Knowledge Engine Quality Filter V1.2

## Input JSON
{input_json}

## Documento sorgente
{source_path}

## Output JSON
{output_json}

## Categoria documento
{result["categoria_documento"]}

## Statistiche
{json.dumps(result["statistiche"], ensure_ascii=False, indent=2)}

## Aree operative pulite
{list_block(result["aree_operative"])}

## Micro-informazioni pulite
{list_block(result["micro_informazioni"])}

## Frasi rilevanti pulite
{list_block(result["frasi_rilevanti"])}

## Relazioni operative pulite
{relation_block(result["relazioni_operative"])}

## Dataset training pulito
{json.dumps(result["dataset_training"], ensure_ascii=False, indent=2)}

## Report qualità
{json.dumps(result["quality_report"], ensure_ascii=False, indent=2)}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Knowledge Engine Quality Filter V1.2"
    )

    parser.add_argument(
        "--input-json",
        default="mini_llm/data/output/knowledge_engine_v11_output.json",
        help="JSON prodotto da Knowledge Engine V1.1.",
    )

    parser.add_argument(
        "--source",
        default="rag/documenti/documento_rag_sicurezza_informatica_aziendale.md",
        help="Documento sorgente reale.",
    )

    parser.add_argument(
        "--output-json",
        default="mini_llm/data/output/knowledge_engine_v12_clean_output.json",
        help="JSON pulito V1.2.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/knowledge_engine_v12_clean_report.md",
        help="Report Markdown V1.2.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    root = Path.cwd()

    input_json = (root / args.input_json).resolve()
    source_path = (root / args.source).resolve()
    output_json = (root / args.output_json).resolve()
    report_path = (root / args.report).resolve()

    if not input_json.exists():
        raise FileNotFoundError(f"JSON V1.1 non trovato: {input_json}")

    if not source_path.exists():
        raise FileNotFoundError(f"Documento sorgente non trovato: {source_path}")

    raw_result = json.loads(input_json.read_text(encoding="utf-8"))
    source_text = source_path.read_text(encoding="utf-8")

    filter_engine = KnowledgeQualityFilterV12()
    clean_result = filter_engine.refine(raw_result=raw_result, source_text=source_text)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(clean_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_path.write_text(
        build_report(
            result=clean_result,
            input_json=input_json,
            source_path=source_path,
            output_json=output_json,
        ),
        encoding="utf-8",
    )

    print("OK - Knowledge Engine Quality Filter V1.2 completato")
    print(f"Input JSON: {input_json}")
    print(f"Documento sorgente: {source_path}")
    print(f"Output JSON pulito: {output_json}")
    print(f"Report pulito: {report_path}")
    print(f"Statistiche: {clean_result['statistiche']}")

    residual = clean_result["quality_report"]["problemi_residui"]

    if residual:
        print("ATTENZIONE - Problemi residui trovati:")
        for item in residual[:10]:
            print("-", item)
    else:
        print("OK - Nessun problema residuo rilevato dal filtro qualità.")


if __name__ == "__main__":
    main()
