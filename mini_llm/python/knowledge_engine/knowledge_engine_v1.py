from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class KnowledgeAnalysis:
    categoria_documento: str
    aree_principali: List[str]
    micro_informazioni: List[str]
    frasi_rilevanti: List[str]
    relazioni_operative: List[Dict[str, str]]
    dataset_training: List[Dict[str, str]]
    statistiche: Dict[str, int]


class KnowledgeEngineV1:
    """
    Knowledge Engine V1 - Motore Conoscenza Operativo.

    Legge testo reale e lo trasforma in conoscenza strutturata:
    categoria, aree principali, micro-informazioni, frasi rilevanti,
    relazioni operative e prime coppie input/output per futuro training LLM.
    """

    STOPWORDS = {
        "della", "delle", "degli", "dello", "dalla", "dalle", "dagli",
        "questo", "questa", "questi", "queste", "sono", "essere",
        "anche", "come", "nelle", "nella", "negli", "dove", "quando",
        "perché", "quindi", "molto", "senza", "oltre", "sopra",
        "sotto", "verso", "dopo", "prima", "durante", "attraverso",
        "il", "lo", "la", "i", "gli", "le", "un", "una", "uno",
        "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
        "e", "o", "ma", "se", "che", "non", "più", "del", "dei",
        "al", "alla", "alle", "ai", "nel", "nei", "sul", "sui",
        "sua", "suo", "sue", "suoi", "loro", "ogni", "può", "puo",
        "deve", "devono", "viene", "vengono", "fare", "fatto",
        "modo", "parte", "tipo", "tutti", "tutte"
    }

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
        "requisito", "requisiti"
    ]

    def analyze(self, text: str) -> KnowledgeAnalysis:
        clean_text = self._clean_text(text)
        sentences = self._split_sentences(clean_text)
        words = self._extract_words(clean_text)

        category = self._detect_category(words)
        main_areas = self._extract_main_areas(words)
        micro_info = self._build_micro_information(clean_text, main_areas)
        relevant_sentences = self._extract_relevant_sentences(sentences, main_areas)
        relations = self._build_operational_relations(main_areas, micro_info)
        training_items = self._build_training_items(
            category=category,
            main_areas=main_areas,
            micro_info=micro_info,
            relevant_sentences=relevant_sentences,
        )

        stats = {
            "caratteri_testo": len(clean_text),
            "numero_frasi": len(sentences),
            "numero_parole_utili": len(words),
            "numero_aree_principali": len(main_areas),
            "numero_micro_informazioni": len(micro_info),
            "numero_frasi_rilevanti": len(relevant_sentences),
            "numero_relazioni_operative": len(relations),
            "numero_training_items": len(training_items),
        }

        return KnowledgeAnalysis(
            categoria_documento=category,
            aree_principali=main_areas,
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

    def _split_sentences(self, text: str) -> List[str]:
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences: List[str] = []

        for sentence in raw_sentences:
            sentence = sentence.strip()

            if len(sentence.split()) < 6:
                continue

            if len(sentence) < 35:
                continue

            if self._looks_like_noise(sentence):
                continue

            sentences.append(sentence)

        return sentences

    def _looks_like_noise(self, sentence: str) -> bool:
        lowered = sentence.lower().strip()

        noise_patterns = [
            r"^pagina\s+\d+",
            r"^indice$",
            r"^copyright",
            r"^www\.",
            r"https?://",
            r"^\d+$",
        ]

        return any(re.search(pattern, lowered) for pattern in noise_patterns)

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

    def _extract_main_areas(self, words: List[str], limit: int = 14) -> List[str]:
        counter = Counter(words)
        main_areas: List[str] = []

        for word, count in counter.most_common():
            if len(word) < 4:
                continue

            if count < 2 and len(main_areas) >= 6:
                continue

            main_areas.append(word)

            if len(main_areas) >= limit:
                break

        return main_areas

    def _build_micro_information(self, text: str, main_areas: List[str]) -> List[str]:
        lowered = text.lower()
        micro_info: List[str] = []

        for area in main_areas:
            pattern = (
                rf"\b(?:[a-zàèéìòù0-9]{{4,}}\s+){{0,2}}"
                rf"{re.escape(area)}"
                rf"(?:\s+[a-zàèéìòù0-9]{{4,}}){{0,3}}\b"
            )

            matches = re.findall(pattern, lowered)

            for match in matches:
                cleaned = " ".join(match.split())

                if not cleaned:
                    continue

                if len(cleaned.split()) > 6:
                    continue

                if cleaned not in micro_info:
                    micro_info.append(cleaned)

                if len(micro_info) >= 30:
                    return micro_info

        return micro_info

    def _extract_relevant_sentences(
        self,
        sentences: List[str],
        main_areas: List[str],
        limit: int = 10,
    ) -> List[str]:
        scored: List[tuple[int, int, str]] = []

        for index, sentence in enumerate(sentences):
            lowered = sentence.lower()
            score = 0

            for area in main_areas:
                if re.search(rf"\b{re.escape(area)}\b", lowered):
                    score += 2

            if re.search(r"\d", sentence):
                score += 1

            for marker in self.IMPORTANCE_MARKERS:
                if marker in lowered:
                    score += 2

            words_count = len(sentence.split())

            if 12 <= words_count <= 45:
                score += 1

            if score > 0:
                scored.append((score, -index, sentence))

        scored.sort(reverse=True)

        relevant: List[str] = []

        for _score, _negative_index, sentence in scored:
            if sentence not in relevant:
                relevant.append(sentence)

            if len(relevant) >= limit:
                break

        return relevant

    def _build_operational_relations(
        self,
        main_areas: List[str],
        micro_info: List[str],
    ) -> List[Dict[str, str]]:
        relations: List[Dict[str, str]] = []

        for area in main_areas:
            linked_items = [
                item for item in micro_info
                if re.search(rf"\b{re.escape(area)}\b", item)
            ]

            for item in linked_items[:3]:
                relations.append({
                    "area": area,
                    "elemento_collegato": item,
                    "tipo": "area_operativa_collegata_a_micro_informazione",
                })

                if len(relations) >= 14:
                    return relations

        for index in range(len(micro_info) - 1):
            relations.append({
                "area": micro_info[index],
                "elemento_collegato": micro_info[index + 1],
                "tipo": "vicinanza_operativa",
            })

            if len(relations) >= 14:
                break

        return relations

    def _build_training_items(
        self,
        category: str,
        main_areas: List[str],
        micro_info: List[str],
        relevant_sentences: List[str],
    ) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []

        items.append({
            "input": "Riconosci la categoria operativa del documento.",
            "output": category,
        })

        if main_areas:
            items.append({
                "input": "Elenca le aree principali del documento.",
                "output": ", ".join(main_areas),
            })

        if micro_info:
            items.append({
                "input": "Elenca le micro-informazioni operative del documento.",
                "output": ", ".join(micro_info),
            })

        for sentence in relevant_sentences[:6]:
            items.append({
                "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
                "output": sentence,
            })

        if relevant_sentences:
            items.append({
                "input": "Crea una sintesi breve delle informazioni più importanti.",
                "output": " ".join(relevant_sentences[:3]),
            })

        return items

    def to_dict(self, analysis: KnowledgeAnalysis) -> Dict:
        return {
            "categoria_documento": analysis.categoria_documento,
            "aree_principali": analysis.aree_principali,
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

    return f"""# Report Knowledge Engine V1

## File analizzato
{input_path}

## Output JSON
{output_json_path}

## Categoria documento
{result["categoria_documento"]}

## Statistiche
{stats_text}

## Aree principali
{list_block(result["aree_principali"])}

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
        description="Knowledge Engine V1 - Motore Conoscenza Operativo"
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
        else root / "mini_llm" / "data" / "output" / "knowledge_engine_v1_output.json"
    )

    report_path = (
        Path(args.report).expanduser().resolve()
        if args.report
        else root / "mini_llm" / "reports" / "knowledge_engine_v1_report.md"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"File da analizzare non trovato: {input_path}\n"
            "Passa un file reale oppure controlla che il documento RAG esista."
        )

    text = input_path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError(f"Il file è vuoto: {input_path}")

    engine = KnowledgeEngineV1()
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

    print("OK - Knowledge Engine V1 completato")
    print(f"File analizzato: {input_path}")
    print(f"Output JSON: {output_json_path}")
    print(f"Report: {report_path}")
    print(f"Categoria: {result['categoria_documento']}")
    print(f"Statistiche: {result['statistiche']}")


if __name__ == "__main__":
    main()
