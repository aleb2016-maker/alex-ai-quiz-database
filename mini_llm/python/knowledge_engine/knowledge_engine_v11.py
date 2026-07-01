from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class KnowledgeAnalysisV11:
    categoria_documento: str
    aree_operative: List[str]
    micro_informazioni: List[str]
    frasi_rilevanti: List[str]
    relazioni_operative: List[Dict[str, str]]
    dataset_training: List[Dict[str, str]]
    statistiche: Dict[str, int]


class KnowledgeEngineV11:
    """
    Knowledge Engine V1.1 - Motore Conoscenza Operativo migliorato.

    Differenza rispetto alla V1:
    - meno parole singole generiche;
    - più espressioni operative;
    - meno ripetizioni;
    - filtro sezioni interne di test/demo/RAG;
    - dataset training più pulito.
    """

    STOPWORDS = {
        "della", "delle", "degli", "dello", "dalla", "dalle", "dagli",
        "questo", "questa", "questi", "queste", "sono", "essere",
        "anche", "come", "nelle", "nella", "negli", "dove", "quando",
        "perché", "perche", "quindi", "molto", "senza", "oltre", "sopra",
        "sotto", "verso", "dopo", "prima", "durante", "attraverso",
        "il", "lo", "la", "i", "gli", "le", "un", "una", "uno",
        "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
        "e", "o", "ma", "se", "che", "non", "più", "piu", "del", "dei",
        "al", "alla", "alle", "ai", "nel", "nei", "sul", "sui",
        "sua", "suo", "sue", "suoi", "loro", "ogni", "può", "puo",
        "deve", "devono", "viene", "vengono", "fare", "fatto",
        "modo", "parte", "tipo", "tutti", "tutte",
        "usare", "solo", "stessa", "stesso", "altro", "altri", "altre",
        "possono", "può", "puo", "essere", "avere", "viene", "vengono",
        "quando", "sempre", "spesso", "qualunque", "qualsiasi"
    }

    PROJECT_META_MARKERS = [
        "uso del documento",
        "motore rag",
        "mini-corsi",
        "mini corsi",
        "generare domande",
        "questo documento può essere usato",
        "questo documento puo essere usato",
    ]

    CATEGORY_KEYWORDS = {
        "documento_aziendale": [
            "azienda", "aziendale", "processo", "procedura", "dipendenti",
            "formazione", "sicurezza", "policy", "requisiti", "obiettivi",
            "operativo", "gestione", "organizzazione", "responsabile",
            "controllo", "standard", "qualità", "qualita"
        ],
        "curriculum_vitae": [
            "esperienza", "competenze", "profilo", "candidato", "lavoro",
            "istruzione", "formazione", "capacità", "capacita", "ruolo",
            "professionale", "curriculum", "cv", "mansione", "azienda"
        ],
        "studio_formazione": [
            "lezione", "studio", "argomento", "definizione", "esercizio",
            "corso", "modulo", "apprendimento", "spiegazione", "materia",
            "conoscenza", "verifica", "domanda", "risposta"
        ],
        "sport_allenamento": [
            "allenamento", "serie", "ripetizioni", "forza", "resistenza",
            "recupero", "esercizio", "muscoli", "scheda", "progressione",
            "carico", "mobilità", "mobilita"
        ],
        "racconto_storia": [
            "personaggio", "storia", "racconto", "capitolo", "dialogo",
            "scena", "viaggio", "emozione", "voce", "narrazione",
            "protagonista", "luogo", "tempo"
        ],
        "documento_personale": [
            "documento", "richiesta", "dichiarazione", "certificato",
            "residenza", "identità", "identita", "anagrafica", "modulo",
            "firma", "codice", "fiscale"
        ],
        "progetto_tecnico": [
            "codice", "sistema", "modulo", "funzione", "database",
            "interfaccia", "server", "client", "architettura", "runtime",
            "python", "javascript", "java", "classe", "metodo", "api",
            "backend", "frontend"
        ],
    }

    IMPORTANCE_MARKERS = [
        "obiettivo", "obiettivi", "serve", "permette", "consente",
        "rischio", "rischi", "vantaggio", "vantaggi", "procedura",
        "importante", "richiede", "definisce", "rappresenta",
        "garantisce", "necessario", "necessaria", "controllo",
        "sicurezza", "formazione", "protezione", "gestione",
        "requisito", "requisiti", "riduce", "evitare", "aggiornare",
        "proteggere", "backup", "password", "phishing", "malware",
        "ransomware", "account", "dati"
    ]

    DOMAIN_PHRASES = [
        "sicurezza informatica",
        "password sicure",
        "password manager",
        "dati sensibili",
        "protezione dei dati",
        "autenticazione a due fattori",
        "account online",
        "backup regolari",
        "aggiornamenti software",
        "malware",
        "ransomware",
        "phishing",
        "reti wi-fi pubbliche",
        "permessi utente",
        "privilegi amministrativi",
        "allegati inattesi",
        "software non autorizzato",
        "protezione endpoint",
        "codici temporanei",
    ]

    def analyze(self, text: str) -> KnowledgeAnalysisV11:
        clean_text = self._clean_text(text)
        clean_text = self._remove_project_meta_blocks(clean_text)

        units = self._split_units(clean_text)
        words = self._extract_words(clean_text)

        category = self._detect_category(words)
        operational_areas = self._extract_operational_areas(clean_text, words)
        micro_info = self._extract_micro_information(units, operational_areas)
        relevant_sentences = self._extract_relevant_sentences(units, operational_areas)
        relations = self._build_operational_relations(relevant_sentences, operational_areas)
        training_items = self._build_training_items(
            category=category,
            operational_areas=operational_areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
        )

        stats = {
            "caratteri_testo": len(clean_text),
            "numero_unita_testuali": len(units),
            "numero_parole_utili": len(words),
            "numero_aree_operative": len(operational_areas),
            "numero_micro_informazioni": len(micro_info),
            "numero_frasi_rilevanti": len(relevant_sentences),
            "numero_relazioni_operative": len(relations),
            "numero_training_items": len(training_items),
        }

        return KnowledgeAnalysisV11(
            categoria_documento=category,
            aree_operative=operational_areas,
            micro_informazioni=micro_info,
            frasi_rilevanti=relevant_sentences,
            relazioni_operative=relations,
            dataset_training=training_items,
            statistiche=stats,
        )

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"(?i)testo di esempio", "", text)
        text = re.sub(r"(?i)demo content", "", text)
        text = re.sub(r"(?i)fallback", "", text)
        return text.strip()

    def _remove_project_meta_blocks(self, text: str) -> str:
        lines = text.splitlines()
        cleaned_lines: List[str] = []
        skip_block = False

        for line in lines:
            lowered = line.lower().strip()

            if any(marker in lowered for marker in self.PROJECT_META_MARKERS):
                skip_block = True
                continue

            if skip_block and self._looks_like_heading(line):
                skip_block = False

            if not skip_block:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def _looks_like_heading(self, line: str) -> bool:
        stripped = line.strip()

        if not stripped:
            return False

        if len(stripped.split()) <= 8 and not stripped.endswith((".", ";", ",")):
            return True

        return False

    def _split_units(self, text: str) -> List[str]:
        units: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            if self._is_project_meta(line):
                continue

            if line.startswith(("-", "•", "*")):
                item = re.sub(r"^[-•*]\s*", "", line).strip()
                if self._is_good_unit(item):
                    units.append(item)
                continue

            pieces = re.split(r"(?<=[.!?])\s+", line)

            for piece in pieces:
                piece = piece.strip()
                if self._is_good_unit(piece):
                    units.append(piece)

        return self._dedupe_keep_order(units)

    def _is_good_unit(self, text: str) -> bool:
        if len(text.split()) < 3:
            return False

        if len(text) < 18:
            return False

        if self._is_project_meta(text):
            return False

        lowered = text.lower()

        if re.search(r"^pagina\s+\d+$", lowered):
            return False

        if lowered.startswith("http") or "www." in lowered:
            return False

        return True

    def _is_project_meta(self, text: str) -> bool:
        lowered = text.lower()
        return any(marker in lowered for marker in self.PROJECT_META_MARKERS)

    def _extract_words(self, text: str) -> List[str]:
        raw_words = re.findall(r"\b[a-zàèéìòùA-ZÀÈÉÌÒÙ0-9]{4,}\b", text.lower())
        words: List[str] = []

        for word in raw_words:
            if word in self.STOPWORDS:
                continue

            if word.isdigit():
                continue

            words.append(word)

        return words

    def _detect_category(self, words: List[str]) -> str:
        word_counter = Counter(words)
        scores: Dict[str, int] = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0

            for keyword in keywords:
                score += word_counter.get(keyword, 0)

            scores[category] = score

        best_category = max(scores, key=scores.get)

        if scores[best_category] == 0:
            return "documento_generico"

        return best_category

    def _extract_operational_areas(self, text: str, words: List[str], limit: int = 14) -> List[str]:
        lowered = text.lower()
        candidates: Counter[str] = Counter()

        for phrase in self.DOMAIN_PHRASES:
            if phrase in lowered:
                candidates[phrase] += 8

        tokens = self._extract_words(text)

        for n in (2, 3):
            for index in range(0, max(0, len(tokens) - n + 1)):
                phrase_tokens = tokens[index:index + n]
                phrase = " ".join(phrase_tokens)

                if self._is_valid_area_phrase(phrase):
                    candidates[phrase] += 1

        word_counter = Counter(words)

        for word, count in word_counter.most_common(40):
            if self._is_valid_single_area(word):
                candidates[word] += count

        sorted_candidates = sorted(
            candidates.items(),
            key=lambda item: (item[1], len(item[0].split())),
            reverse=True,
        )

        areas: List[str] = []

        for candidate, _score in sorted_candidates:
            if self._is_too_similar(candidate, areas):
                continue

            areas.append(candidate)

            if len(areas) >= limit:
                break

        return areas

    def _is_valid_area_phrase(self, phrase: str) -> bool:
        words = phrase.split()

        if len(words) < 2:
            return False

        if any(word in self.STOPWORDS for word in words):
            return False

        if len(set(words)) < len(words):
            return False

        if all(len(word) < 5 for word in words):
            return False

        return True

    def _is_valid_single_area(self, word: str) -> bool:
        if word in self.STOPWORDS:
            return False

        if len(word) < 5:
            return False

        banned = {"usare", "solo", "sistema", "sistemi", "utente", "utenti"}
        if word in banned:
            return False

        return True

    def _extract_micro_information(
        self,
        units: List[str],
        operational_areas: List[str],
        limit: int = 30,
    ) -> List[str]:
        scored: List[Tuple[int, str]] = []

        for unit in units:
            lowered = unit.lower()
            score = 0

            for area in operational_areas:
                if area in lowered:
                    score += 3

            for marker in self.IMPORTANCE_MARKERS:
                if marker in lowered:
                    score += 1

            if score <= 0:
                continue

            micro = self._compress_unit_to_micro_info(unit)

            if micro:
                scored.append((score, micro))

        scored.sort(key=lambda item: item[0], reverse=True)

        micro_info: List[str] = []

        for _score, item in scored:
            if self._is_too_similar(item, micro_info):
                continue

            micro_info.append(item)

            if len(micro_info) >= limit:
                break

        return micro_info

    def _compress_unit_to_micro_info(self, unit: str) -> str:
        text = unit.strip()
        text = re.sub(r"\s+", " ", text)

        if len(text.split()) > 18:
            text = " ".join(text.split()[:18]).rstrip(",;:") + "."

        return text

    def _extract_relevant_sentences(
        self,
        units: List[str],
        operational_areas: List[str],
        limit: int = 10,
    ) -> List[str]:
        scored: List[Tuple[int, int, str]] = []

        for index, unit in enumerate(units):
            lowered = unit.lower()
            score = 0

            for area in operational_areas:
                if area in lowered:
                    score += 3

            for marker in self.IMPORTANCE_MARKERS:
                if marker in lowered:
                    score += 2

            if re.search(r"\d|2fa|wi-fi", lowered):
                score += 1

            word_count = len(unit.split())
            if 7 <= word_count <= 45:
                score += 1

            if score > 0:
                scored.append((score, -index, unit))

        scored.sort(reverse=True)

        selected: List[str] = []

        for _score, _neg_index, unit in scored:
            if self._is_too_similar(unit, selected):
                continue

            selected.append(unit)

            if len(selected) >= limit:
                break

        return selected

    def _build_operational_relations(
        self,
        relevant_sentences: List[str],
        operational_areas: List[str],
        limit: int = 14,
    ) -> List[Dict[str, str]]:
        relations: List[Dict[str, str]] = []

        for unit in relevant_sentences:
            lowered = unit.lower()
            present_areas = [area for area in operational_areas if area in lowered]

            if len(present_areas) >= 2:
                for index in range(len(present_areas) - 1):
                    relations.append({
                        "area": present_areas[index],
                        "elemento_collegato": present_areas[index + 1],
                        "tipo": "co_presenza_in_informazione_rilevante",
                    })

                    if len(relations) >= limit:
                        return relations

            elif len(present_areas) == 1:
                relations.append({
                    "area": present_areas[0],
                    "elemento_collegato": self._compress_unit_to_micro_info(unit),
                    "tipo": "area_collegata_a_frase_operativa",
                })

                if len(relations) >= limit:
                    return relations

        return relations

    def _build_training_items(
        self,
        category: str,
        operational_areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
    ) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []

        items.append({
            "input": "Riconosci la categoria operativa del documento.",
            "output": category,
        })

        if operational_areas:
            items.append({
                "input": "Elenca le aree operative principali del documento.",
                "output": ", ".join(operational_areas),
            })

        if micro_info:
            items.append({
                "input": "Elenca le micro-informazioni operative più utili.",
                "output": "; ".join(micro_info[:12]),
            })

        for sentence in relevant_sentences[:6]:
            items.append({
                "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
                "output": sentence,
            })

        if relevant_sentences:
            items.append({
                "input": "Crea una sintesi breve delle informazioni operative più importanti.",
                "output": " ".join(relevant_sentences[:4]),
            })

        return items

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

    def _is_too_similar(self, candidate: str, existing_items: List[str]) -> bool:
        candidate_set = set(candidate.lower().split())

        for item in existing_items:
            item_set = set(item.lower().split())

            if not candidate_set or not item_set:
                continue

            overlap = len(candidate_set & item_set) / max(1, min(len(candidate_set), len(item_set)))

            if overlap >= 0.80:
                return True

        return False

    def to_dict(self, analysis: KnowledgeAnalysisV11) -> Dict:
        return {
            "categoria_documento": analysis.categoria_documento,
            "aree_operative": analysis.aree_operative,
            "micro_informazioni": analysis.micro_informazioni,
            "frasi_rilevanti": analysis.frasi_rilevanti,
            "relazioni_operative": analysis.relazioni_operative,
            "dataset_training": analysis.dataset_training,
            "statistiche": analysis.statistiche,
        }


def build_markdown_report(result: Dict, input_path: Path, output_json_path: Path) -> str:
    def list_block(items: List[str]) -> str:
        if not items:
            return "- Nessun elemento rilevato."
        return "\n".join(f"- {item}" for item in items)

    def relations_block(items: List[Dict[str, str]]) -> str:
        if not items:
            return "- Nessuna relazione operativa rilevata."

        lines = []
        for item in items:
            area = item.get("area", "")
            linked = item.get("elemento_collegato", "")
            relation_type = item.get("tipo", "")
            lines.append(f"- {area} -> {linked} ({relation_type})")

        return "\n".join(lines)

    stats_text = json.dumps(result["statistiche"], ensure_ascii=False, indent=2)
    training_text = json.dumps(result["dataset_training"], ensure_ascii=False, indent=2)

    return f"""# Report Knowledge Engine V1.1

## File analizzato
{input_path}

## Output JSON
{output_json_path}

## Categoria documento
{result["categoria_documento"]}

## Statistiche
{stats_text}

## Aree operative
{list_block(result["aree_operative"])}

## Micro-informazioni operative
{list_block(result["micro_informazioni"])}

## Frasi rilevanti
{list_block(result["frasi_rilevanti"])}

## Relazioni operative
{relations_block(result["relazioni_operative"])}

## Dataset training iniziale
{training_text}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Knowledge Engine V1.1 - Motore Conoscenza Operativo"
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Percorso del file TXT/MD da analizzare. Se assente usa il documento RAG reale di default.",
    )

    parser.add_argument(
        "--output-json",
        default=None,
        help="Percorso output JSON.",
    )

    parser.add_argument(
        "--report",
        default=None,
        help="Percorso report Markdown.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[3]

    default_input_path = (
        root
        / "rag"
        / "documenti"
        / "documento_rag_sicurezza_informatica_aziendale.md"
    )

    input_path = Path(args.input).expanduser().resolve() if args.input else default_input_path

    output_json_path = (
        Path(args.output_json).expanduser().resolve()
        if args.output_json
        else root / "mini_llm" / "data" / "output" / "knowledge_engine_v11_output.json"
    )

    report_path = (
        Path(args.report).expanduser().resolve()
        if args.report
        else root / "mini_llm" / "reports" / "knowledge_engine_v11_report.md"
    )

    if not input_path.exists():
        raise FileNotFoundError(f"File da analizzare non trovato: {input_path}")

    text = input_path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError(f"Il file è vuoto: {input_path}")

    engine = KnowledgeEngineV11()
    analysis = engine.analyze(text)
    result = engine.to_dict(analysis)

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    output_json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = build_markdown_report(
        result=result,
        input_path=input_path,
        output_json_path=output_json_path,
    )

    report_path.write_text(report, encoding="utf-8")

    print("OK - Knowledge Engine V1.1 completato")
    print(f"File analizzato: {input_path}")
    print(f"Output JSON: {output_json_path}")
    print(f"Report: {report_path}")
    print(f"Categoria: {result['categoria_documento']}")
    print(f"Statistiche: {result['statistiche']}")


if __name__ == "__main__":
    main()
