from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List


class NeuralModelV3CleanValidator:
    """
    Validatore Neural Model V3 Clean.

    Controlla:
    - file presenti;
    - manifest coerente;
    - pesi dimensionalmente corretti;
    - output embeddings e bias numerici;
    - loss finite;
    - uso dichiarato del Vectorizer V2 Clean;
    - predizioni campione non vuote;
    - nessun token sporco nelle predizioni.
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
        "richiesto",
        "source_task",
        "source_record",
        "record",
        "json",
    }

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        model_dir = root / "mini_llm" / "data" / "model_v3_clean"
        report_dir = root / "mini_llm" / "reports"

        weights_path = model_dir / "neural_model_v3_clean_weights.json"
        manifest_path = model_dir / "neural_model_v3_clean_manifest.json"
        predictions_path = model_dir / "neural_model_v3_clean_sample_predictions.json"
        report_path = report_dir / "neural_model_v3_clean_report.md"

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
        self._validate_predictions(predictions, manifest, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, errors: List[str]) -> None:
        if manifest.get("versione") != "neural_model_v3_clean":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "trained":
            errors.append("Status manifest non trained.")

        settings = manifest.get("settings", {})

        if settings.get("uses_vectorizer_v2_clean") is not True:
            errors.append("Il manifest non dichiara uses_vectorizer_v2_clean True.")

        if settings.get("context_size", 0) < 2:
            errors.append("Context size troppo piccolo.")

        if settings.get("epochs", 0) < 1:
            errors.append("Epoch non valide.")

        model = manifest.get("model", {})

        if model.get("architecture") != "weighted_context_negative_sampling":
            errors.append("Architettura non attesa.")

        if model.get("vocab_size", 0) < 50:
            errors.append("Vocab size troppo piccolo.")

        if model.get("vector_dim", 0) < 32:
            errors.append("Vector dim troppo piccola.")

        examples = manifest.get("examples", {})

        if examples.get("train", 0) <= 0:
            errors.append("Train examples vuoti.")

        if examples.get("val", 0) <= 0:
            errors.append("Val examples vuoti.")

        if examples.get("test", 0) <= 0:
            errors.append("Test examples vuoti.")

        loss = manifest.get("loss", {})

        for key in ["train_sampled_final", "val_full_softmax_final", "test_full_softmax_final"]:
            value = loss.get(key)

            if not self._is_valid_loss(value):
                errors.append(f"Loss non valida: {key}={value}")

        history = loss.get("epoch_history", [])

        if not history:
            errors.append("Epoch history mancante.")

        for item in history:
            if not self._is_valid_loss(item.get("train_sampled_loss")):
                errors.append("Train sampled loss epoch non valida.")

            if not self._is_valid_loss(item.get("val_full_softmax_loss")):
                errors.append("Val full softmax loss epoch non valida.")

        quality = manifest.get("quality", {})

        if quality.get("empty_predictions", 1) != 0:
            errors.append("Manifest segnala predizioni vuote.")

        if quality.get("dirty_prediction_tokens"):
            errors.append("Manifest segnala token sporchi nelle predizioni.")

    def _validate_weights(self, weights: Dict, manifest: Dict, errors: List[str]) -> None:
        if weights.get("versione") != "neural_model_v3_clean_weights":
            errors.append("Versione pesi errata.")

        settings = weights.get("settings", {})
        model = manifest.get("model", {})

        vocab_size = model.get("vocab_size")
        vector_dim = model.get("vector_dim")

        if settings.get("source_vectorizer") != "token_vectorizer_v2_clean":
            errors.append("I pesi non dichiarano source_vectorizer token_vectorizer_v2_clean.")

        if settings.get("vocab_size") != vocab_size:
            errors.append("Vocab size pesi incoerente.")

        if settings.get("vector_dim") != vector_dim:
            errors.append("Vector dim pesi incoerente.")

        id_to_token = weights.get("id_to_token", [])
        token_to_id = weights.get("token_to_id", {})
        output_embeddings = weights.get("output_embeddings", [])
        output_bias = weights.get("output_bias", [])

        if len(id_to_token) != vocab_size:
            errors.append("id_to_token dimensione incoerente.")

        if len(token_to_id) != vocab_size:
            errors.append("token_to_id dimensione incoerente.")

        if len(output_embeddings) != vocab_size:
            errors.append("output_embeddings righe incoerenti.")

        if len(output_bias) != vocab_size:
            errors.append("output_bias lunghezza incoerente.")

        for token in ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]:
            if token not in token_to_id:
                errors.append(f"Special token mancante nei pesi: {token}")

        for row_index, row in enumerate(output_embeddings[: min(20, len(output_embeddings))]):
            if len(row) != vector_dim:
                errors.append(f"Embedding row {row_index} dimensione incoerente.")

            for value in row[: min(20, len(row))]:
                if not self._is_finite_number(value):
                    errors.append(f"Valore embedding non valido in row {row_index}.")

        if not any(abs(float(value)) > 0.000001 for value in output_bias):
            errors.append("Output bias sembra non addestrato: tutti zero.")

    def _validate_predictions(self, predictions: List[Dict], manifest: Dict, errors: List[str]) -> None:
        if not isinstance(predictions, list) or not predictions:
            errors.append("Predizioni campione mancanti.")
            return

        for index, item in enumerate(predictions, start=1):
            top_predictions = item.get("top_predictions", [])

            if not top_predictions:
                errors.append(f"Predizione {index}: top_predictions vuoto.")
                continue

            for prediction in top_predictions:
                token = str(prediction.get("token", "")).lower()

                if not token:
                    errors.append(f"Predizione {index}: token vuoto.")

                if token in self.DIRTY_TOKENS:
                    errors.append(f"Predizione {index}: token sporco: {token}")

                score = prediction.get("score")

                if not self._is_finite_number(score):
                    errors.append(f"Predizione {index}: score non valido.")

                probability = prediction.get("probability_topk")

                if not self._is_finite_number(probability):
                    errors.append(f"Predizione {index}: probability_topk non valida.")

    def _is_valid_loss(self, value) -> bool:
        return self._is_finite_number(value) and 0 <= float(value) < 50

    def _is_finite_number(self, value) -> bool:
        try:
            return math.isfinite(float(value))
        except (TypeError, ValueError):
            return False


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Neural Model V3 Clean

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_neural_model_v3_clean.md"

    validator = NeuralModelV3CleanValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Neural Model V3 Clean fallita")
        print(f"Report: {report_path}")

        for error in errors[:80]:
            print("-", error)

        if len(errors) > 80:
            print(f"... altri errori: {len(errors) - 80}")

        raise SystemExit(1)

    print("OK - Validazione Neural Model V3 Clean superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
