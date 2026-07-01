from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class NeuralModelV1Validator:
    """
    Validatore Neural Model V1.

    Controlla:
    - file modello presenti;
    - manifest coerente;
    - pesi leggibili;
    - dimensioni embedding coerenti;
    - training history presente;
    - loss numeriche;
    - predizioni esempio presenti.
    """

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        model_dir = root / "mini_llm" / "data" / "model_v1"
        report_dir = root / "mini_llm" / "reports"

        weights_path = model_dir / "neural_model_v1_weights.json"
        manifest_path = model_dir / "neural_model_v1_manifest.json"
        predictions_path = model_dir / "neural_model_v1_sample_predictions.json"
        report_path = report_dir / "neural_model_v1_report.md"

        for path in [weights_path, manifest_path, predictions_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        weights = json.loads(weights_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        predictions = json.loads(predictions_path.read_text(encoding="utf-8"))

        self._validate_manifest(manifest, errors)
        self._validate_weights(weights, manifest, errors)
        self._validate_history(manifest, errors)
        self._validate_evaluation(manifest, errors)
        self._validate_predictions(predictions, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, errors: List[str]) -> None:
        if manifest.get("versione") != "neural_model_v1":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "trained":
            errors.append("Status modello non trained.")

        architecture = manifest.get("architecture", {})

        if architecture.get("name") != "neural_bigram_negative_sampling_v1":
            errors.append("Architettura modello errata.")

        if architecture.get("is_first_neural_model") is not True:
            errors.append("Flag is_first_neural_model non True.")

        dimensions = manifest.get("model_dimensions", {})

        if dimensions.get("vocab_size", 0) < 50:
            errors.append("Vocabolario modello troppo piccolo.")

        if dimensions.get("vector_dim", 0) < 16:
            errors.append("Vector dim troppo piccola.")

        data = manifest.get("training_data", {})

        if data.get("train_pairs_used", 0) <= 0:
            errors.append("Nessuna coppia train usata.")

        if data.get("val_pairs", 0) <= 0:
            errors.append("Nessuna coppia validation.")

        if data.get("test_pairs", 0) <= 0:
            errors.append("Nessuna coppia test.")

    def _validate_weights(self, weights: Dict, manifest: Dict, errors: List[str]) -> None:
        if weights.get("versione") != "neural_model_v1_weights":
            errors.append("Versione pesi errata.")

        dimensions = manifest.get("model_dimensions", {})
        vocab_size = dimensions.get("vocab_size")
        vector_dim = dimensions.get("vector_dim")

        input_embeddings = weights.get("input_embeddings", [])
        output_embeddings = weights.get("output_embeddings", [])
        output_bias = weights.get("output_bias", [])

        if len(input_embeddings) != vocab_size:
            errors.append("Numero righe input_embeddings incoerente.")

        if len(output_embeddings) != vocab_size:
            errors.append("Numero righe output_embeddings incoerente.")

        if len(output_bias) != vocab_size:
            errors.append("Numero bias output incoerente.")

        if input_embeddings and len(input_embeddings[0]) != vector_dim:
            errors.append("Dimensione vettore input errata.")

        if output_embeddings and len(output_embeddings[0]) != vector_dim:
            errors.append("Dimensione vettore output errata.")

        if not any(any(abs(value) > 0.000001 for value in row) for row in output_embeddings[1:]):
            errors.append("Output embeddings sembrano tutti zero.")

        if not any(abs(value) > 0.000001 for value in output_bias[1:]):
            errors.append("Output bias sembrano tutti zero, possibile training non avvenuto.")

    def _validate_history(self, manifest: Dict, errors: List[str]) -> None:
        history = manifest.get("history", [])
        hyperparameters = manifest.get("hyperparameters", {})
        expected_epochs = hyperparameters.get("epochs")

        if not history:
            errors.append("Training history mancante.")
            return

        if len(history) != expected_epochs:
            errors.append(f"Numero epoche incoerente: {len(history)} != {expected_epochs}")

        for item in history:
            if item.get("train_loss", 0) <= 0:
                errors.append(f"Train loss non valida in epoch {item.get('epoch')}")

            if item.get("val_loss", 0) <= 0:
                errors.append(f"Val loss non valida in epoch {item.get('epoch')}")

    def _validate_evaluation(self, manifest: Dict, errors: List[str]) -> None:
        evaluation = manifest.get("evaluation", {})

        for key in ["train_loss", "val_loss", "test_loss"]:
            value = evaluation.get(key)

            if not isinstance(value, (int, float)):
                errors.append(f"{key} non numerica.")
                continue

            if value <= 0:
                errors.append(f"{key} non valida: {value}")

        if not evaluation.get("sample_predictions"):
            errors.append("sample_predictions mancanti nel manifest.")

    def _validate_predictions(self, predictions: List[Dict], errors: List[str]) -> None:
        if not predictions:
            errors.append("File predizioni vuoto.")
            return

        for item in predictions:
            if not item.get("input_token"):
                errors.append("Predizione senza input_token.")

            top_predictions = item.get("top_predictions", [])

            if not top_predictions:
                errors.append(f"Nessuna top_prediction per {item.get('input_token')}")
                continue

            for prediction in top_predictions:
                if "token" not in prediction:
                    errors.append("Top prediction senza token.")

                if "score" not in prediction:
                    errors.append("Top prediction senza score.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Neural Model V1

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_neural_model_v1.md"

    validator = NeuralModelV1Validator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Neural Model V1 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Neural Model V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
