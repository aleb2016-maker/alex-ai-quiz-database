from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class KnowledgeEngineV14Validator:
    """
    Validatore ufficiale Knowledge Engine V1.4.

    Correzioni:
    - non cerca pattern sporchi dentro quality_report;
    - non considera sporca la frase corretta "Il backup serve a recuperare...";
    - accetta categorie tecniche tipo documento_aziendale;
    - controlla solo i campi finali usabili.
    """

    BAD_LINE_PATTERNS = [
        r"^\s*Domanda:",
        r"^\s*Risposta corretta:",
        r"^\s*#\s*Documento RAG di test",
        r"^\s*Uso del documento",
        r"^\s*Per ridurre il rischio malware è importante:\s*$",
        r"^\s*Serve a recuperare informazioni",
        r"^\s*Questo principio riduce",
        r"^\s*Il metodo migliore è usare un password manager\.?$",
    ]

    BAD_CONTAINS_PATTERNS = [
        r"motore RAG",
        r"mini-corsi",
        r"mini corsi",
        r"generare domande",
        r"può provare\.$",
        r"potrebbe cifrare anche\.$",
    ]

    REQUIRED_AREAS = [
        "sicurezza informatica",
        "password sicure",
        "password manager",
        "dati sensibili",
        "autenticazione a due fattori",
        "phishing",
        "malware",
        "ransomware",
        "backup regolari",
        "aggiornamenti software",
    ]

    REQUIRED_FIXED_SENTENCES = [
        "Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.",
        "Il principio del minimo privilegio riduce il danno possibile in caso di errore o compromissione di un account.",
        "Il metodo migliore per gestire password sicure è usare un password manager.",
    ]

    def validate(self, data: Dict) -> List[str]:
        errors: List[str] = []

        self._validate_version(data, errors)
        self._validate_category(data, errors)
        self._validate_counts(data, errors)
        self._validate_required_areas(data, errors)
        self._validate_required_repairs(data, errors)
        self._validate_bad_patterns(data, errors)
        self._validate_training_items(data, errors)
        self._validate_quality_counters(data, errors)

        return errors

    def _validate_version(self, data: Dict, errors: List[str]) -> None:
        version = data.get("versione", "")

        if version != "knowledge_engine_semantic_repair_v14":
            errors.append(f"Versione errata o mancante: {version}")

    def _validate_category(self, data: Dict, errors: List[str]) -> None:
        category = data.get("categoria_documento", "")

        if not category:
            errors.append("Categoria documento mancante.")

        if category == "documento_generico":
            errors.append("Categoria troppo generica: documento_generico.")

    def _validate_counts(self, data: Dict, errors: List[str]) -> None:
        areas = data.get("aree_operative", [])
        micro = data.get("micro_informazioni", [])
        frasi = data.get("frasi_rilevanti", [])
        relazioni = data.get("relazioni_operative", [])
        training = data.get("dataset_training", [])

        if len(areas) < 10:
            errors.append(f"Poche aree operative: {len(areas)}")

        if len(micro) < 15:
            errors.append(f"Poche micro-informazioni: {len(micro)}")

        if len(frasi) < 8:
            errors.append(f"Poche frasi rilevanti: {len(frasi)}")

        if len(relazioni) < 3:
            errors.append(f"Poche relazioni operative: {len(relazioni)}")

        if len(training) < 7:
            errors.append(f"Pochi item training: {len(training)}")

    def _validate_required_areas(self, data: Dict, errors: List[str]) -> None:
        areas = data.get("aree_operative", [])
        areas_text = " | ".join(areas).lower()

        for required in self.REQUIRED_AREAS:
            if required.lower() not in areas_text:
                errors.append(f"Area operativa obbligatoria mancante: {required}")

    def _validate_required_repairs(self, data: Dict, errors: List[str]) -> None:
        final_text = "\n".join(self._collect_final_texts(data))

        for sentence in self.REQUIRED_FIXED_SENTENCES:
            if sentence not in final_text:
                errors.append(f"Frase riparata obbligatoria mancante: {sentence}")

    def _validate_bad_patterns(self, data: Dict, errors: List[str]) -> None:
        final_texts = self._collect_final_texts(data)

        for text in final_texts:
            chunks = self._split_text_for_validation(text)

            for chunk in chunks:
                for pattern in self.BAD_LINE_PATTERNS:
                    if re.search(pattern, chunk, flags=re.IGNORECASE):
                        errors.append(f"Pattern sporco trovato nell'output finale: {pattern} -> {chunk}")

                for pattern in self.BAD_CONTAINS_PATTERNS:
                    if re.search(pattern, chunk, flags=re.IGNORECASE):
                        errors.append(f"Pattern sporco trovato nell'output finale: {pattern} -> {chunk}")

    def _validate_training_items(self, data: Dict, errors: List[str]) -> None:
        training = data.get("dataset_training", [])

        for index, item in enumerate(training):
            item_input = item.get("input", "").strip()
            item_output = item.get("output", "").strip()

            if not item_input:
                errors.append(f"Training item {index}: input vuoto.")

            if not item_output:
                errors.append(f"Training item {index}: output vuoto.")

            # Accetta etichette tecniche tipo documento_aziendale.
            if self._is_category_label(item_output):
                continue

            if len(item_output.split()) < 2:
                errors.append(f"Training item {index}: output troppo corto.")

    def _validate_quality_counters(self, data: Dict, errors: List[str]) -> None:
        stats = data.get("statistiche", {})
        quality = data.get("quality_report", {})

        if stats.get("problemi_residui", 0) != 0:
            errors.append(f"Problemi residui non zero: {stats.get('problemi_residui')}")

        if stats.get("problemi_semantici_residui_v14", 0) != 0:
            errors.append(
                f"Problemi semantici residui non zero: "
                f"{stats.get('problemi_semantici_residui_v14')}"
            )

        if quality.get("problemi_residui"):
            errors.append("quality_report contiene problemi_residui.")

        if quality.get("problemi_semantici_residui_v14"):
            errors.append("quality_report contiene problemi_semantici_residui_v14.")

    def _collect_final_texts(self, data: Dict) -> List[str]:
        """
        Raccoglie solo i campi finali usabili.
        Esclude quality_report, perché contiene anche la cronologia 'prima/dopo'.
        """

        texts: List[str] = []

        texts.extend(data.get("aree_operative", []))
        texts.extend(data.get("micro_informazioni", []))
        texts.extend(data.get("frasi_rilevanti", []))

        for relation in data.get("relazioni_operative", []):
            texts.append(relation.get("area", ""))
            texts.append(relation.get("elemento_collegato", ""))
            texts.append(relation.get("tipo", ""))

        for item in data.get("dataset_training", []):
            texts.append(item.get("input", ""))
            texts.append(item.get("output", ""))

        return texts

    def _split_text_for_validation(self, text: str) -> List[str]:
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

    def _is_category_label(self, text: str) -> bool:
        return bool(re.fullmatch(r"[a-z0-9_]+", text.strip()))


def build_report(json_path: Path, errors: List[str], data: Dict) -> str:
    status = "OK" if not errors else "ERRORE"
    stats = data.get("statistiche", {})

    error_block = (
        "Nessun errore rilevato."
        if not errors
        else "\n".join(f"- {error}" for error in errors)
    )

    return f"""# Validazione Knowledge Engine V1.4

## File validato
{json_path}

## Stato
{status}

## Statistiche output
{json.dumps(stats, ensure_ascii=False, indent=2)}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()

    json_path = root / "mini_llm" / "data" / "output" / "knowledge_engine_v14_semantic_output.json"
    report_path = root / "mini_llm" / "reports" / "validazione_knowledge_engine_v14.md"

    if not json_path.exists():
        raise FileNotFoundError(f"File V1.4 non trovato: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))

    validator = KnowledgeEngineV14Validator()
    errors = validator.validate(data)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(json_path=json_path, errors=errors, data=data),
        encoding="utf-8",
    )

    if errors:
        print("ERRORE - Validazione Knowledge Engine V1.4 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Knowledge Engine V1.4 superata")
    print(f"File validato: {json_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
