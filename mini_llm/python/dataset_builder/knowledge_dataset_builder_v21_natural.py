from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


class KnowledgeDatasetBuilderV21Natural:
    """
    Dataset Builder V2.1 Natural.

    Scopo:
    creare un dataset ancora più naturale del V2 Clean.

    Perché serve:
    Inference V3 Clean ha eliminato token sporchi classici e codici numerici,
    ma ha mostrato ancora contaminazioni tipo:
    - alex
    - knowledge_engine_v14
    - relazioni_operative
    - training_originale
    - "è collegata a"
    - "crea"
    - ripetizioni tipo "password manager password manager"

    Questo builder crea un nuovo dataset V2.1 Natural, più severo:
    - esclude codici numerici/ID;
    - esclude metadati tecnici;
    - esclude token con underscore;
    - esclude nomi/provenienza progettuale;
    - esclude frasi di relazione tecnica;
    - mantiene solo frasi più naturali e complete;
    - aggiunge mini-frasi didattiche pulite ricavate dai contenuti.
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

    MIN_WORDS = 4
    MAX_WORDS = 34

    def __init__(
        self,
        root: Path,
        input_v14: Path,
        input_v2_clean: Path,
        output_dir: Path,
        report_path: Path,
    ):
        self.root = root
        self.input_v14 = input_v14
        self.input_v2_clean = input_v2_clean
        self.output_dir = output_dir
        self.report_path = report_path

        self.stats = {
            "source_records_total": 0,
            "candidate_texts_total": 0,
            "accepted_texts_total": 0,
            "discarded_empty": 0,
            "discarded_short": 0,
            "discarded_too_long": 0,
            "discarded_dirty": 0,
            "discarded_not_natural": 0,
            "discarded_duplicate": 0,
            "synthetic_natural_added": 0,
        }

    def run(self) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        records: List[Dict] = []
        seen = set()

        # 1) Estrae prima dal JSON semantico V1.4, più vicino alla conoscenza pulita.
        if self.input_v14.exists():
            for text in self._extract_from_v14(self.input_v14):
                self._try_add(records, seen, text, "knowledge_engine_v14")

        # 2) Recupera anche testi già ripuliti dal Dataset V2, ma con filtri più duri.
        if self.input_v2_clean.exists():
            for text in self._extract_from_jsonl_text_field(self.input_v2_clean):
                self._try_add(records, seen, text, "knowledge_dataset_v2_clean")

        # 3) Aggiunge frasi didattiche naturali controllate, basate sulle aree note.
        for text in self._synthetic_natural_sentences():
            before = len(records)
            self._try_add(records, seen, text, "synthetic_natural")
            if len(records) > before:
                self.stats["synthetic_natural_added"] += 1

        # ID globali stabili.
        for index, record in enumerate(records, start=1):
            record["natural_id"] = f"natural-v21-{index:05d}"

        split_records = self._split_records(records)

        output_full = self.output_dir / "knowledge_dataset_v21_natural.jsonl"
        output_train = self.output_dir / "knowledge_dataset_v21_natural_train.jsonl"
        output_val = self.output_dir / "knowledge_dataset_v21_natural_val.jsonl"
        output_test = self.output_dir / "knowledge_dataset_v21_natural_test.jsonl"
        manifest_path = self.output_dir / "knowledge_dataset_v21_natural_manifest.json"

        self._write_jsonl(output_full, records)
        self._write_jsonl(output_train, split_records["train"])
        self._write_jsonl(output_val, split_records["val"])
        self._write_jsonl(output_test, split_records["test"])

        quality = self._quality_summary(records)

        manifest = {
            "versione": "knowledge_dataset_v21_natural",
            "status": "built",
            "description": "Dataset V2.1 Natural senza metadati tecnici, codici numerici e frasi scaffolding.",
            "input_files": {
                "knowledge_engine_v14": str(self.input_v14),
                "knowledge_dataset_v2_clean": str(self.input_v2_clean),
            },
            "output_files": {
                "full": str(output_full),
                "train": str(output_train),
                "val": str(output_val),
                "test": str(output_test),
                "manifest": str(manifest_path),
                "report": str(self.report_path),
            },
            "records": {
                "full": len(records),
                "train": len(split_records["train"]),
                "val": len(split_records["val"]),
                "test": len(split_records["test"]),
            },
            "cleaning": {
                "dirty_tokens": sorted(self.DIRTY_TOKENS),
                "dirty_phrases": sorted(self.DIRTY_PHRASES),
                "min_words": self.MIN_WORDS,
                "max_words": self.MAX_WORDS,
                "stats": self.stats,
            },
            "quality": quality,
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.report_path.write_text(
            self._build_report(manifest),
            encoding="utf-8",
        )

        return manifest

    def _extract_from_v14(self, path: Path) -> Iterable[str]:
        payload = json.loads(path.read_text(encoding="utf-8"))

        # Estrazione ricorsiva di stringhe utili dal JSON semantico.
        for _path, value in self._walk_strings(payload):
            text = str(value).strip()

            if text:
                yield text

    def _extract_from_jsonl_text_field(self, path: Path) -> Iterable[str]:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = str(record.get("text", "")).strip()

                if text:
                    yield text

    def _walk_strings(self, value, path: Optional[List[str]] = None) -> Iterable[Tuple[List[str], str]]:
        if path is None:
            path = []

        if isinstance(value, dict):
            for key, child in value.items():
                yield from self._walk_strings(child, path + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from self._walk_strings(child, path + [str(index)])
        elif isinstance(value, str):
            yield path, value

    def _try_add(self, records: List[Dict], seen: set, raw_text: str, source: str) -> None:
        self.stats["source_records_total"] += 1
        self.stats["candidate_texts_total"] += 1

        text = self._clean_text(raw_text)
        decision = self._accept_text(text)

        if decision != "accepted":
            self.stats[decision] += 1
            return

        key = text.lower()

        if key in seen:
            self.stats["discarded_duplicate"] += 1
            return

        seen.add(key)
        self.stats["accepted_texts_total"] += 1

        records.append(
            {
                "natural_id": "",
                "source": source,
                "text": text,
                "char_count": len(text),
                "word_count": len(self._word_tokens(text)),
                "token_count_estimate": len(self._tokenize(text)),
                "dataset_version": "knowledge_dataset_v21_natural",
            }
        )

    def _clean_text(self, text: str) -> str:
        cleaned = str(text)

        cleaned = cleaned.replace("#", " ")
        cleaned = cleaned.replace("```", " ")
        cleaned = cleaned.replace(":::", " ")

        # Rimuove etichette tecniche.
        cleaned = re.sub(
            r"\b(input|output|istruzione|instruction|risposta|domanda|answer|question|prompt|completion)\s*:",
            " ",
            cleaned,
            flags=re.IGNORECASE,
        )

        # Rimuove codici tipo clean-v2-00001, 00084, V14, ecc.
        cleaned = re.sub(r"\bclean[-_]?v?\d+[-_]?\d*\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bsource[-_][a-z0-9_]+\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b0\d{2,}\b", " ", cleaned)
        cleaned = re.sub(r"\b\d{4,}\b", " ", cleaned)
        cleaned = re.sub(r"\b[a-zàèéìòù]+_+[a-z0-9_]+\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b[a-zàèéìòù]+v\d+\b", " ", cleaned, flags=re.IGNORECASE)

        for phrase in sorted(self.DIRTY_PHRASES, key=len, reverse=True):
            cleaned = re.sub(re.escape(phrase), " ", cleaned, flags=re.IGNORECASE)

        tokens = self._tokenize_keep_punctuation(cleaned)
        clean_tokens: List[str] = []

        for token in tokens:
            normalized = token.lower().strip()

            if not normalized:
                continue

            if normalized in self.DIRTY_TOKENS:
                continue

            if self._is_numeric_code_token(normalized):
                continue

            if self._is_metadata_shape_token(normalized):
                continue

            if clean_tokens and normalized == clean_tokens[-1].lower():
                continue

            if clean_tokens and self._is_punctuation(normalized) and self._is_punctuation(clean_tokens[-1]):
                continue

            clean_tokens.append(token)

        cleaned = self._detokenize(clean_tokens)
        cleaned = self._normalize_space(cleaned)
        cleaned = cleaned.strip(" ,;:-")

        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."

        return cleaned

    def _accept_text(self, text: str) -> str:
        if not text:
            return "discarded_empty"

        words = self._word_tokens(text)

        if len(words) < self.MIN_WORDS:
            return "discarded_short"

        if len(words) > self.MAX_WORDS:
            return "discarded_too_long"

        lower_text = text.lower()
        tokens = [token.lower() for token in self._tokenize(text)]

        if text[0] in ".,;:!?-":
            return "discarded_dirty"

        if any(token in self.DIRTY_TOKENS for token in tokens):
            return "discarded_dirty"

        if any(self._is_numeric_code_token(token) for token in tokens):
            return "discarded_dirty"

        if any(self._is_metadata_shape_token(token) for token in tokens):
            return "discarded_dirty"

        if any(phrase in lower_text for phrase in self.DIRTY_PHRASES):
            return "discarded_dirty"

        # Richiede almeno un concetto di dominio per evitare frasi generiche/progettuali.
        if not any(token in self.CONTENT_HINTS for token in tokens):
            return "discarded_not_natural"

        # Evita testo con troppe punteggiature/strutture.
        if lower_text.count(":") > 0:
            return "discarded_dirty"

        # Evita pattern ripetitivi tipo "password manager password manager".
        bigrams = list(zip(tokens, tokens[1:]))
        for index in range(len(bigrams) - 1):
            if bigrams[index] == bigrams[index + 1]:
                return "discarded_dirty"

        return "accepted"

    def _synthetic_natural_sentences(self) -> List[str]:
        return [
            "Una password sicura deve essere lunga, unica e difficile da indovinare.",
            "Un password manager aiuta a conservare password diverse per ogni servizio.",
            "La sicurezza informatica protegge dati, account e dispositivi da accessi non autorizzati.",
            "I dati sensibili devono essere protetti con attenzione e condivisi solo quando necessario.",
            "L'autenticazione a due fattori aggiunge una protezione ulteriore agli account online.",
            "I codici temporanei aiutano a verificare l'identità durante l'accesso a un servizio.",
            "Gli account amministrativi devono essere usati solo quando servono privilegi elevati.",
            "Il phishing prova a ingannare l'utente per rubare credenziali o dati sensibili.",
            "Il malware può danneggiare sistemi, rubare informazioni o bloccare i dispositivi.",
            "Il ransomware può cifrare i dati e chiedere un riscatto per sbloccarli.",
            "I backup regolari aiutano a recuperare informazioni dopo errori, guasti o attacchi.",
            "Gli aggiornamenti software correggono vulnerabilità e migliorano la sicurezza dei sistemi.",
            "Il principio del minimo privilegio limita i danni in caso di errore o compromissione.",
            "Un account online deve essere protetto con password robuste e controlli di accesso.",
            "La protezione dei dati richiede attenzione, backup e buone pratiche quotidiane.",
            "Le credenziali non devono essere condivise con persone o siti non affidabili.",
        ]

    def _split_records(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        train: List[Dict] = []
        val: List[Dict] = []
        test: List[Dict] = []

        for index, record in enumerate(records):
            mod = index % 10

            if mod == 8:
                split = "val"
                val.append(record)
            elif mod == 9:
                split = "test"
                test.append(record)
            else:
                split = "train"
                train.append(record)

            record["split"] = split

        return {"train": train, "val": val, "test": test}

    def _write_jsonl(self, path: Path, records: List[Dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _quality_summary(self, records: List[Dict]) -> Dict:
        texts = [record["text"] for record in records]
        tokens_all = [token.lower() for text in texts for token in self._tokenize(text)]

        dirty = [token for token in tokens_all if token in self.DIRTY_TOKENS]
        numeric = [token for token in tokens_all if self._is_numeric_code_token(token)]
        metadata = [token for token in tokens_all if self._is_metadata_shape_token(token)]
        punctuation_start = sum(1 for text in texts if text and text[0] in ".,;:!?-")

        immediate_duplicates = 0
        repeated_bigrams = 0

        for text in texts:
            tokens = [token.lower() for token in self._tokenize(text)]

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    immediate_duplicates += 1

            bigrams = list(zip(tokens, tokens[1:]))
            for index in range(len(bigrams) - 1):
                if bigrams[index] == bigrams[index + 1]:
                    repeated_bigrams += 1

        word_counts = [record["word_count"] for record in records]

        return {
            "records": len(records),
            "dirty_token_hits": len(dirty),
            "numeric_code_hits": len(numeric),
            "metadata_shape_hits": len(metadata),
            "punctuation_start": punctuation_start,
            "immediate_duplicates": immediate_duplicates,
            "repeated_bigrams": repeated_bigrams,
            "avg_word_count": round(statistics.mean(word_counts), 2) if word_counts else 0,
            "min_word_count": min(word_counts) if word_counts else 0,
            "max_word_count": max(word_counts) if word_counts else 0,
            "top_tokens": Counter(tokens_all).most_common(25),
        }

    def _build_report(self, manifest: Dict) -> str:
        return f"""# Report Knowledge Dataset Builder V2.1 Natural

## Stato
{manifest["status"]}

## Obiettivo
Creare un dataset naturale più severo per rimuovere metadati, ID, codici e frasi progettuali.

## Input
```json
{json.dumps(manifest["input_files"], ensure_ascii=False, indent=2)}
```

## Output
```json
{json.dumps(manifest["output_files"], ensure_ascii=False, indent=2)}
```

## Record
```json
{json.dumps(manifest["records"], ensure_ascii=False, indent=2)}
```

## Pulizia
```json
{json.dumps(manifest["cleaning"], ensure_ascii=False, indent=2)}
```

## Qualità
```json
{json.dumps(manifest["quality"], ensure_ascii=False, indent=2)}
```

## Nota
Questo dataset è più piccolo ma più naturale.
Serve per rigenerare Vectorizer V2.1, Neural Model V3.1 e Inference V3.1.
"""

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _tokenize_keep_punctuation(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[.,;:!?()'’\-]", text, flags=re.IGNORECASE)

    def _word_tokens(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù]+", text.lower(), flags=re.IGNORECASE)

    def _detokenize(self, tokens: List[str]) -> str:
        text = " ".join(tokens)
        text = text.replace(" ,", ",")
        text = text.replace(" .", ".")
        text = text.replace(" :", ":")
        text = text.replace(" ;", ";")
        text = text.replace(" !", "!")
        text = text.replace(" ?", "?")
        text = text.replace("( ", "(")
        text = text.replace(" )", ")")
        text = text.replace(" ’ ", "’")
        text = text.replace(" ' ", "'")
        return re.sub(r"\s+", " ", text).strip()

    def _normalize_space(self, text: str) -> str:
        return re.sub(r"\s+", " ", str(text).strip())

    def _is_punctuation(self, token: str) -> bool:
        return token in {".", ",", ";", ":", "!", "?", "-", "(", ")", "'", "’"}

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Knowledge Dataset Builder V2.1 Natural")

    parser.add_argument("--input-v14", default="mini_llm/data/output/knowledge_engine_v14_semantic_output.json")
    parser.add_argument("--input-v2-clean", default="mini_llm/data/training/knowledge_dataset_v2_clean.jsonl")
    parser.add_argument("--output-dir", default="mini_llm/data/training")
    parser.add_argument("--report", default="mini_llm/reports/knowledge_dataset_builder_v21_natural_report.md")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    builder = KnowledgeDatasetBuilderV21Natural(
        root=root,
        input_v14=(root / args.input_v14).resolve(),
        input_v2_clean=(root / args.input_v2_clean).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
    )

    manifest = builder.run()

    print("OK - Knowledge Dataset Builder V2.1 Natural completato")
    print(f"Dataset completo: {manifest['output_files']['full']}")
    print(f"Train: {manifest['output_files']['train']}")
    print(f"Val: {manifest['output_files']['val']}")
    print(f"Test: {manifest['output_files']['test']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Record totali: {manifest['records']['full']}")
    print(f"Train/Val/Test: {manifest['records']['train']}/{manifest['records']['val']}/{manifest['records']['test']}")
    print(f"Dirty token hits: {manifest['quality']['dirty_token_hits']}")
    print(f"Numeric code hits: {manifest['quality']['numeric_code_hits']}")
    print(f"Metadata shape hits: {manifest['quality']['metadata_shape_hits']}")
    print(f"Repeated bigrams: {manifest['quality']['repeated_bigrams']}")


if __name__ == "__main__":
    main()
