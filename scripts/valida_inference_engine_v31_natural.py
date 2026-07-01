from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class InferenceEngineV31NaturalValidator:
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
        "breve",
        "sintesi",
        "template",
    }

    DOMAIN_TOKENS = {
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
        "dispositivi",
        "vulnerabilità",
        "sistemi",
        "accesso",
    }

    PUNCTUATION_TOKENS = {".", ",", ";", ":", "!", "?", "-", "(", ")", "'", "’"}

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        output_dir = root / "mini_llm" / "data" / "inference_v31_natural"
        report_dir = root / "mini_llm" / "reports"

        outputs_path = output_dir / "inference_engine_v31_natural_outputs.json"
        manifest_path = output_dir / "inference_engine_v31_natural_manifest.json"
        report_path = report_dir / "inference_engine_v31_natural_report.md"

        for path in [outputs_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        try:
            outputs = json.loads(outputs_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"JSON non valido: {error}")
            return errors

        self._validate_manifest(manifest, outputs, errors)
        self._validate_outputs(outputs, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, outputs: List[Dict], errors: List[str]) -> None:
        if manifest.get("versione") != "inference_engine_v31_natural":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "completed":
            errors.append("Status manifest non completed.")

        settings = manifest.get("settings", {})

        if settings.get("uses_neural_model_v31_natural") is not True:
            errors.append("Manifest non dichiara uses_neural_model_v31_natural True.")

        if settings.get("uses_vectorizer_v21_natural") is not True:
            errors.append("Manifest non dichiara uses_vectorizer_v21_natural True.")

        if settings.get("uses_dataset_v21_natural") is not True:
            errors.append("Manifest non dichiara uses_dataset_v21_natural True.")

        if settings.get("quality_fallback_enabled") is not True:
            errors.append("Manifest non dichiara quality_fallback_enabled True.")

        model = manifest.get("model", {})

        if model.get("vocab_size", 0) < 50:
            errors.append("Vocab size troppo piccolo.")

        if model.get("vector_dim", 0) < 32:
            errors.append("Vector dim troppo piccola.")

        summary = manifest.get("summary", {})

        if summary.get("generations_total") != len(outputs):
            errors.append("Conteggio generazioni incoerente.")

        if summary.get("non_empty_generations") != len(outputs):
            errors.append("Almeno una generazione è vuota secondo il manifest.")

        quality = manifest.get("quality", {})

        checks_zero = [
            "dirty_tokens_count",
            "numeric_tokens_count",
            "metadata_tokens_count",
            "immediate_duplicate_generations",
            "repeated_bigram_generations",
            "punctuation_start",
            "empty_generations",
            "too_short_generations",
            "no_domain_generations",
        ]

        for key in checks_zero:
            if quality.get(key, 1) != 0:
                errors.append(f"Manifest segnala problema qualità: {key}={quality.get(key)}")

    def _validate_outputs(self, outputs: List[Dict], errors: List[str]) -> None:
        if not isinstance(outputs, list) or not outputs:
            errors.append("Output inferenze vuoto.")
            return

        for index, item in enumerate(outputs, start=1):
            text = str(item.get("generated_text", "")).strip()
            tokens = [str(token) for token in item.get("generated_tokens", [])]

            if not text:
                errors.append(f"Inferenza {index}: testo generato vuoto.")

            if not tokens:
                errors.append(f"Inferenza {index}: generated_tokens vuoto.")
                continue

            if text and text[0] in ".,;:!?-":
                errors.append(f"Inferenza {index}: testo inizia con punteggiatura.")

            if len([token for token in tokens if token not in self.PUNCTUATION_TOKENS]) < 6:
                errors.append(f"Inferenza {index}: troppo corta.")

            if not any(token.lower() in self.DOMAIN_TOKENS for token in tokens):
                errors.append(f"Inferenza {index}: nessun concetto di dominio.")

            for token in tokens:
                normalized = token.lower().strip()

                if normalized in self.DIRTY_TOKENS:
                    errors.append(f"Inferenza {index}: token sporco presente: {token}")

                if self._is_numeric_code_token(normalized):
                    errors.append(f"Inferenza {index}: codice numerico presente: {token}")

                if self._is_metadata_shape_token(normalized):
                    errors.append(f"Inferenza {index}: token metadata presente: {token}")

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    errors.append(f"Inferenza {index}: duplicato immediato: {left}")

            bigrams = list(zip(tokens, tokens[1:]))

            for pos in range(len(bigrams) - 1):
                if bigrams[pos] == bigrams[pos + 1]:
                    errors.append(f"Inferenza {index}: bigramma ripetuto.")

            if item.get("model_version") != "neural_model_v31_natural":
                errors.append(f"Inferenza {index}: model_version errata.")

            if item.get("inference_version") != "inference_engine_v31_natural":
                errors.append(f"Inferenza {index}: inference_version errata.")

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


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Inference Engine V3.1 Natural

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_inference_engine_v31_natural.md"

    validator = InferenceEngineV31NaturalValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Inference Engine V3.1 Natural fallita")
        print(f"Report: {report_path}")

        for error in errors[:100]:
            print("-", error)

        if len(errors) > 100:
            print(f"... altri errori: {len(errors) - 100}")

        raise SystemExit(1)

    print("OK - Validazione Inference Engine V3.1 Natural superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
