from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class KnowledgeStrictRepairV13:
    """
    Knowledge Engine Strict Repair V1.3.

    Prende l'output pulito V1.2 e fa un controllo più severo:
    - trova frasi troncate;
    - prova a sostituirle con la frase completa dal documento sorgente;
    - elimina Domanda/Risposta corretta/titoli;
    - elimina relazioni duplicate;
    - ricostruisce dataset training pulito.
    """

    BAD_PREFIXES = (
        "#",
        "##",
        "###",
        "domanda:",
        "risposta corretta:",
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

    WEAK_FINAL_WORDS = {
        "anche",
        "provare",
        "o",
        "e",
        "di",
        "a",
        "da",
        "con",
        "per",
        "in",
        "su",
        "al",
        "alla",
        "del",
        "della",
        "dei",
        "delle",
        "che",
        "come",
        "se",
        "un",
        "una",
        "uno",
        "il",
        "lo",
        "la",
        "gli",
        "le",
        "i",
    }

    STRONG_AREAS = [
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

    def repair(self, clean_v12: Dict, source_text: str) -> Dict:
        source_units = self._extract_source_units(source_text)

        category = clean_v12.get("categoria_documento", "documento_generico")

        areas = self._repair_areas(
            raw_areas=clean_v12.get("aree_operative", []),
            source_text=source_text,
        )

        micro_info, micro_repairs = self._repair_text_list(
            raw_items=clean_v12.get("micro_informazioni", []),
            source_units=source_units,
            areas=areas,
            limit=24,
        )

        relevant_sentences, relevant_repairs = self._repair_text_list(
            raw_items=clean_v12.get("frasi_rilevanti", []),
            source_units=source_units,
            areas=areas,
            limit=10,
        )

        relations = self._repair_relations(
            raw_relations=clean_v12.get("relazioni_operative", []),
            areas=areas,
            relevant_sentences=relevant_sentences,
        )

        dataset_training = self._build_dataset_training(
            category=category,
            areas=areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
        )

        residual_problems = self._find_residual_problems(
            areas=areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
            relations=relations,
            dataset_training=dataset_training,
        )

        return {
            "versione": "knowledge_engine_strict_repair_v13",
            "categoria_documento": category,
            "aree_operative": areas,
            "micro_informazioni": micro_info,
            "frasi_rilevanti": relevant_sentences,
            "relazioni_operative": relations,
            "dataset_training": dataset_training,
            "quality_report": {
                "micro_riparazioni": micro_repairs,
                "frasi_riparazioni": relevant_repairs,
                "problemi_residui": residual_problems,
            },
            "statistiche": {
                "numero_aree_operative": len(areas),
                "numero_micro_informazioni": len(micro_info),
                "numero_frasi_rilevanti": len(relevant_sentences),
                "numero_relazioni_operative": len(relations),
                "numero_training_items": len(dataset_training),
                "micro_riparazioni": len(micro_repairs),
                "frasi_riparazioni": len(relevant_repairs),
                "problemi_residui": len(residual_problems),
            },
        }

    def _extract_source_units(self, source_text: str) -> List[str]:
        text = source_text.replace("\r", "\n")
        units: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            line = re.sub(r"^[-•*]\s*", "", line).strip()

            if self._is_bad_text(line):
                continue

            if self._looks_like_heading(line):
                continue

            pieces = re.split(r"(?<=[.!?])\s+", line)

            for piece in pieces:
                piece = piece.strip()

                if self._is_good_source_unit(piece):
                    units.append(piece)

        return self._dedupe_keep_order(units)

    def _is_good_source_unit(self, text: str) -> bool:
        if self._is_bad_text(text):
            return False

        if self._looks_incomplete(text):
            return False

        word_count = len(text.split())

        if word_count < 6:
            return False

        if word_count > 70:
            return False

        return True

    def _looks_like_heading(self, text: str) -> bool:
        stripped = text.strip()

        if stripped.startswith("#"):
            return True

        if len(stripped.split()) <= 7 and not stripped.endswith((".", "!", "?")):
            return True

        return False

    def _repair_areas(self, raw_areas: List[str], source_text: str, limit: int = 14) -> List[str]:
        lowered_source = source_text.lower()
        areas: List[str] = []

        for area in self.STRONG_AREAS:
            if area in lowered_source and area not in areas:
                areas.append(area)

        for area in raw_areas:
            area = self._clean_text(area).lower()

            if not area:
                continue

            if self._is_bad_text(area):
                continue

            if area not in areas:
                areas.append(area)

            if len(areas) >= limit:
                break

        return areas[:limit]

    def _repair_text_list(
        self,
        raw_items: List[str],
        source_units: List[str],
        areas: List[str],
        limit: int,
    ) -> Tuple[List[str], List[Dict[str, str]]]:
        candidates: List[Tuple[int, str]] = []
        repairs: List[Dict[str, str]] = []

        for item in raw_items:
            cleaned = self._clean_text(item)

            if self._is_bad_text(cleaned):
                continue

            if self._looks_incomplete(cleaned):
                repaired = self._find_best_completion(cleaned, source_units)

                if repaired and repaired != cleaned:
                    repairs.append({
                        "prima": cleaned,
                        "dopo": repaired,
                    })
                    cleaned = repaired
                else:
                    continue

            if not self._is_usable_output_text(cleaned):
                continue

            candidates.append((self._score(cleaned, areas), cleaned))

        for unit in source_units:
            if not self._mentions_any_area(unit, areas):
                continue

            if not self._is_usable_output_text(unit):
                continue

            candidates.append((self._score(unit, areas), unit))

        candidates.sort(key=lambda item: item[0], reverse=True)

        selected: List[str] = []

        for _score, item in candidates:
            if self._is_too_similar(item, selected):
                continue

            selected.append(item)

            if len(selected) >= limit:
                break

        return selected, repairs

    def _find_best_completion(self, broken_text: str, source_units: List[str]) -> str | None:
        broken_norm = self._normalize_for_match(broken_text)
        broken_words = broken_norm.split()

        if len(broken_words) < 5:
            return None

        prefix = " ".join(broken_words[:8])
        best_unit = None
        best_score = 0.0

        for unit in source_units:
            unit_norm = self._normalize_for_match(unit)
            unit_words = unit_norm.split()

            if not unit_words:
                continue

            overlap = len(set(broken_words) & set(unit_words)) / max(1, len(set(broken_words)))

            prefix_bonus = 0.25 if unit_norm.startswith(prefix) else 0.0
            longer_bonus = 0.15 if len(unit_words) > len(broken_words) else 0.0

            score = overlap + prefix_bonus + longer_bonus

            if score > best_score:
                best_score = score
                best_unit = unit

        if best_score >= 0.62 and best_unit and not self._looks_incomplete(best_unit):
            return best_unit

        return None

    def _repair_relations(
        self,
        raw_relations: List[Dict[str, str]],
        areas: List[str],
        relevant_sentences: List[str],
        limit: int = 14,
    ) -> List[Dict[str, str]]:
        relations: List[Dict[str, str]] = []
        seen_pairs = set()

        for relation in raw_relations:
            area = self._clean_text(relation.get("area", "")).lower()
            linked = self._clean_text(relation.get("elemento_collegato", "")).lower()

            if not area or not linked:
                continue

            if self._is_bad_text(area) or self._is_bad_text(linked):
                continue

            if self._looks_incomplete(area) or self._looks_incomplete(linked):
                continue

            pair = (area, linked)

            if pair in seen_pairs:
                continue

            seen_pairs.add(pair)

            relations.append({
                "area": area,
                "elemento_collegato": linked,
                "tipo": "relazione_operativa_pulita",
            })

            if len(relations) >= limit:
                return relations

        for sentence in relevant_sentences:
            lowered = sentence.lower()
            present = [area for area in areas if area in lowered]

            for index in range(len(present) - 1):
                area = present[index]
                linked = present[index + 1]
                pair = (area, linked)

                if pair in seen_pairs:
                    continue

                seen_pairs.add(pair)

                relations.append({
                    "area": area,
                    "elemento_collegato": linked,
                    "tipo": "co_presenza_pulita",
                })

                if len(relations) >= limit:
                    return relations

        return relations

    def _build_dataset_training(
        self,
        category: str,
        areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
    ) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []

        items.append({
            "input": "Riconosci la categoria operativa del documento.",
            "output": category,
        })

        items.append({
            "input": "Elenca le aree operative principali del documento.",
            "output": ", ".join(areas),
        })

        items.append({
            "input": "Elenca micro-informazioni operative pulite e complete.",
            "output": "; ".join(micro_info[:10]),
        })

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

    def _find_residual_problems(
        self,
        areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
        relations: List[Dict[str, str]],
        dataset_training: List[Dict[str, str]],
    ) -> List[str]:
        problems: List[str] = []
        texts: List[str] = []

        texts.extend(areas)
        texts.extend(micro_info)
        texts.extend(relevant_sentences)

        for relation in relations:
            texts.append(relation.get("area", ""))
            texts.append(relation.get("elemento_collegato", ""))

        for item in dataset_training:
            texts.append(item.get("input", ""))
            texts.append(item.get("output", ""))

        for text in texts:
            if self._is_bad_text(text):
                problems.append(f"Testo sporco: {text}")

            if self._looks_incomplete(text):
                problems.append(f"Testo incompleto: {text}")

        return self._dedupe_keep_order(problems)

    def _is_usable_output_text(self, text: str) -> bool:
        if self._is_bad_text(text):
            return False

        if self._looks_incomplete(text):
            return False

        word_count = len(text.split())

        if word_count < 6:
            return False

        if word_count > 65:
            return False

        return True

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

        if not stripped:
            return True

        lowered = stripped.lower()

        if lowered.endswith((":",";",".")):
            words = re.findall(r"[a-zàèéìòù0-9]+", lowered)

            if words and words[-1] in self.WEAK_FINAL_WORDS:
                return True

        if lowered.endswith((",", ";", ":")):
            return True

        if stripped.endswith("?"):
            return True

        return False

    def _score(self, text: str, areas: List[str]) -> int:
        lowered = text.lower()
        score = 0

        for area in areas:
            if area in lowered:
                score += 4

        strong_words = [
            "sicurezza", "password", "manager", "dati", "sensibili",
            "autenticazione", "2fa", "phishing", "malware", "ransomware",
            "backup", "aggiornamenti", "account", "proteggere", "rischio",
            "riduce", "vulnerabilità", "permessi", "privilegi"
        ]

        for word in strong_words:
            if word in lowered:
                score += 1

        return score

    def _mentions_any_area(self, text: str, areas: List[str]) -> bool:
        lowered = text.lower()
        return any(area in lowered for area in areas)

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"^[-•*]\s*", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize_for_match(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\wàèéìòù0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _is_too_similar(self, candidate: str, existing_items: List[str]) -> bool:
        candidate_set = set(self._normalize_for_match(candidate).split())

        for item in existing_items:
            item_set = set(self._normalize_for_match(item).split())

            if not candidate_set or not item_set:
                continue

            overlap = len(candidate_set & item_set) / max(1, min(len(candidate_set), len(item_set)))

            if overlap >= 0.86:
                return True

        return False

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

    return f"""# Report Knowledge Engine Strict Repair V1.3

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
        description="Knowledge Engine Strict Repair V1.3"
    )

    parser.add_argument(
        "--input-json",
        default="mini_llm/data/output/knowledge_engine_v12_clean_output.json",
        help="JSON pulito V1.2.",
    )

    parser.add_argument(
        "--source",
        default="rag/documenti/documento_rag_sicurezza_informatica_aziendale.md",
        help="Documento sorgente reale.",
    )

    parser.add_argument(
        "--output-json",
        default="mini_llm/data/output/knowledge_engine_v13_strict_output.json",
        help="JSON finale V1.3.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/knowledge_engine_v13_strict_report.md",
        help="Report Markdown V1.3.",
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
        raise FileNotFoundError(f"JSON V1.2 non trovato: {input_json}")

    if not source_path.exists():
        raise FileNotFoundError(f"Documento sorgente non trovato: {source_path}")

    clean_v12 = json.loads(input_json.read_text(encoding="utf-8"))
    source_text = source_path.read_text(encoding="utf-8")

    repair_engine = KnowledgeStrictRepairV13()
    result = repair_engine.repair(clean_v12=clean_v12, source_text=source_text)

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
            source_path=source_path,
            output_json=output_json,
        ),
        encoding="utf-8",
    )

    print("OK - Knowledge Engine Strict Repair V1.3 completato")
    print(f"Input JSON: {input_json}")
    print(f"Documento sorgente: {source_path}")
    print(f"Output JSON V1.3: {output_json}")
    print(f"Report V1.3: {report_path}")
    print(f"Statistiche: {result['statistiche']}")

    problems = result["quality_report"]["problemi_residui"]

    if problems:
        print("ATTENZIONE - Problemi residui:")
        for problem in problems[:12]:
            print("-", problem)
    else:
        print("OK - Nessun problema residuo rilevato dal controllo severo.")


if __name__ == "__main__":
    main()
