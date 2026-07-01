from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class InferenceEngineV2ContextValidator:
    """
    Validatore Inference Engine V2 Context.

    Controlla:
    - file output presenti;
    - manifest coerente;
    - uso esplicito del contesto multi-token;
    - generazioni presenti;
    - steps con context_tokens;
    - token speciali bloccati non presenti nel testo generato.
    """

    BLOCKED_TOKENS = {"<PAD>", "<BOS>", "<UNK>"}

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        inference_dir = root / "mini_llm" / "data" / "inference_v2_context"
        report_dir = root / "mini_llm" / "reports"

        outputs_path = inference_dir / "inference_engine_v2_context_outputs.json"
        manifest_path = inference_dir / "inference_engine_v2_context_manifest.json"
        report_path = report_dir / "inference_engine_v2_context_report.md"

        for path in [outputs_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        outputs = json.loads(outputs_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self._validate_manifest(manifest, outputs, errors)
        self._validate_outputs(outputs, manifest, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, outputs: List[Dict], errors: List[str]) -> None:
        if manifest.get("versione") != "inference_engine_v2_context":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "generated":
            errors.append("Status inferenza non generated.")

        model = manifest.get("model", {})

        if model.get("vocab_size", 0) < 50:
            errors.append("Vocab size troppo piccolo nel manifest inferenza.")

        if model.get("vector_dim", 0) < 16:
            errors.append("Vector dim troppo piccola nel manifest inferenza.")

        if model.get("context_size", 0) < 2:
            errors.append("Context size troppo piccolo nel manifest inferenza.")

        architecture = model.get("architecture", {})

        if architecture.get("uses_multi_token_context") is not True:
            errors.append("Il manifest non conferma l'uso del contesto multi-token.")

        generation = manifest.get("generation", {})

        if generation.get("uses_context_window") is not True:
            errors.append("Generation non dichiara uses_context_window True.")

        if generation.get("max_new_tokens", 0) <= 0:
            errors.append("max_new_tokens non valido.")

        if generation.get("top_k", 0) <= 0:
            errors.append("top_k non valido.")

        summary = manifest.get("summary", {})

        if summary.get("total_generations") != len(outputs):
            errors.append("Conteggio total_generations incoerente.")

        if summary.get("non_empty_generations", 0) <= 0:
            errors.append("Nessuna generazione non vuota.")

    def _validate_outputs(self, outputs: List[Dict], manifest: Dict, errors: List[str]) -> None:
        if len(outputs) < 3:
            errors.append(f"Poche inferenze generate: {len(outputs)}")

        expected_context_size = manifest.get("model", {}).get("context_size", 0)

        for index, item in enumerate(outputs):
            prompt = item.get("prompt", "")
            generated_text = item.get("generated_text", "")
            generated_tokens = item.get("generated_tokens", [])
            steps = item.get("steps", [])
            context_size = item.get("context_size", 0)

            if not prompt:
                errors.append(f"Inferenza {index}: prompt vuoto.")

            if context_size != expected_context_size:
                errors.append(f"Inferenza {index}: context_size incoerente.")

            if not generated_text.strip():
                errors.append(f"Inferenza {index}: testo generato vuoto.")

            if not generated_tokens:
                errors.append(f"Inferenza {index}: generated_tokens vuoto.")

            if not steps:
                errors.append(f"Inferenza {index}: steps vuoti.")

            for token in generated_tokens:
                if token in self.BLOCKED_TOKENS:
                    errors.append(f"Inferenza {index}: token bloccato generato: {token}")

            for step in steps:
                context_tokens = step.get("context_tokens", [])
                context_ids = step.get("context_ids", [])

                if not context_tokens:
                    errors.append(f"Inferenza {index}: step senza context_tokens.")

                if not context_ids:
                    errors.append(f"Inferenza {index}: step senza context_ids.")

                if len(context_ids) > expected_context_size:
                    errors.append(f"Inferenza {index}: context_ids più lungo del context_size.")

                if not step.get("top_candidates"):
                    errors.append(f"Inferenza {index}: step senza top_candidates.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Inference Engine V2 Context

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_inference_engine_v2_context.md"

    validator = InferenceEngineV2ContextValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Inference Engine V2 Context fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Inference Engine V2 Context superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
