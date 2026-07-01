from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class InferenceEngineV21CleanValidator:
    """
    Validatore Inference Engine V2.1 Clean.

    Controlla:
    - file output presenti;
    - manifest coerente;
    - clean decoding attivo;
    - generazioni presenti;
    - nessun token sporco;
    - nessuna ripetizione immediata;
    - nessuna punteggiatura come primo token;
    - token generati entro limite breve.
    """

    BLOCKED_TOKENS = {"<PAD>", "<BOS>", "<UNK>"}

    DIRTY_TOKENS = {
        "#",
        "input",
        "output",
        "risposta",
        "istruzione",
        "domanda",
        "trasforma",
        "riscrivi",
        "collegate",
        "micro",
        "forma",
        "area",
        "operativa",
        "pulite",
        "pulita",
        "complete",
        "completa",
        "analizzato",
        "richiesta",
    }

    PUNCTUATION_TOKENS = {".", ",", ";", ":", "!", "?", "-", "(", ")", "’", "'"}

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        inference_dir = root / "mini_llm" / "data" / "inference_v21_clean"
        report_dir = root / "mini_llm" / "reports"

        outputs_path = inference_dir / "inference_engine_v21_clean_outputs.json"
        manifest_path = inference_dir / "inference_engine_v21_clean_manifest.json"
        report_path = report_dir / "inference_engine_v21_clean_report.md"

        for path in [outputs_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        outputs = json.loads(outputs_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self._validate_manifest(manifest, outputs, errors)
        self._validate_outputs(outputs, manifest, errors)
        self._validate_quality_summary(manifest, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, outputs: List[Dict], errors: List[str]) -> None:
        if manifest.get("versione") != "inference_engine_v21_clean":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "generated":
            errors.append("Status inferenza non generated.")

        model = manifest.get("model", {})

        if model.get("context_size", 0) < 2:
            errors.append("Context size troppo piccolo nel manifest inferenza.")

        generation = manifest.get("generation", {})

        if generation.get("uses_context_window") is not True:
            errors.append("Generation non dichiara uses_context_window True.")

        if generation.get("uses_clean_decoding") is not True:
            errors.append("Clean decoding non attivo.")

        if generation.get("max_new_tokens", 0) > 20:
            errors.append("max_new_tokens troppo alto per V2.1 Clean.")

        summary = manifest.get("summary", {})

        if summary.get("total_generations") != len(outputs):
            errors.append("Conteggio total_generations incoerente.")

        if summary.get("non_empty_generations", 0) <= 0:
            errors.append("Nessuna generazione non vuota.")

        filters = manifest.get("filters", {})

        if not filters.get("dirty_tokens"):
            errors.append("Lista dirty_tokens mancante.")

    def _validate_outputs(self, outputs: List[Dict], manifest: Dict, errors: List[str]) -> None:
        if len(outputs) < 3:
            errors.append(f"Poche inferenze generate: {len(outputs)}")

        expected_context_size = manifest.get("model", {}).get("context_size", 0)
        max_new_tokens = manifest.get("generation", {}).get("max_new_tokens", 0)

        for index, item in enumerate(outputs):
            prompt = item.get("prompt", "")
            generated_text = item.get("generated_text", "")
            tokens = [str(token).lower().strip() for token in item.get("generated_tokens", [])]
            steps = item.get("steps", [])
            context_size = item.get("context_size", 0)

            if not prompt:
                errors.append(f"Inferenza {index}: prompt vuoto.")

            if context_size != expected_context_size:
                errors.append(f"Inferenza {index}: context_size incoerente.")

            if not generated_text.strip():
                errors.append(f"Inferenza {index}: testo generato vuoto.")

            if not tokens:
                errors.append(f"Inferenza {index}: generated_tokens vuoto.")

            if len(tokens) > max_new_tokens:
                errors.append(f"Inferenza {index}: troppi token generati.")

            if tokens and tokens[0] in self.PUNCTUATION_TOKENS:
                errors.append(f"Inferenza {index}: primo token è punteggiatura.")

            for token in tokens:
                if token in self.BLOCKED_TOKENS:
                    errors.append(f"Inferenza {index}: token bloccato generato: {token}")

                if token in self.DIRTY_TOKENS:
                    errors.append(f"Inferenza {index}: token sporco generato: {token}")

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    errors.append(f"Inferenza {index}: ripetizione immediata: {left}")

            if not steps:
                errors.append(f"Inferenza {index}: steps vuoti.")

            for step in steps:
                context_ids = step.get("context_ids", [])

                if context_ids and len(context_ids) > expected_context_size:
                    errors.append(f"Inferenza {index}: context_ids più lungo del context_size.")

    def _validate_quality_summary(self, manifest: Dict, errors: List[str]) -> None:
        quality = manifest.get("summary", {}).get("quality", {})

        if quality.get("dirty_tokens_found", 0) != 0:
            errors.append("Il riepilogo qualità segnala token sporchi.")

        if quality.get("immediate_duplicates_found", 0) != 0:
            errors.append("Il riepilogo qualità segnala duplicati immediati.")

        if quality.get("punctuation_start_found", 0) != 0:
            errors.append("Il riepilogo qualità segnala punteggiatura iniziale.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Inference Engine V2.1 Clean

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_inference_engine_v21_clean.md"

    validator = InferenceEngineV21CleanValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Inference Engine V2.1 Clean fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Inference Engine V2.1 Clean superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
