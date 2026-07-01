from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class NeuralBigramModelV1:
    """
    Neural Model V1.

    Primo modello neurale leggero per il mini LLM.

    Architettura:
    - input embedding: vettori token caricati da Token Vectorizer V1;
    - output embedding: matrice addestrabile token -> token successivo;
    - training: negative sampling su coppie token corrente -> token successivo;
    - validazione: loss media su validation/test;
    - inferenza: suggerisce i token successivi più probabili.

    Nota:
    è un primo modello neurale pratico, non ancora un Transformer.
    Serve a verificare che la pipeline addestri davvero pesi numerici.
    """

    SPECIAL_TOKEN_IDS = {
        "PAD": 0,
        "UNK": 1,
        "BOS": 2,
        "EOS": 3,
    }

    def __init__(
        self,
        vocab_path: Path,
        embeddings_path: Path,
        train_sequences_path: Path,
        val_sequences_path: Path,
        test_sequences_path: Path,
        output_dir: Path,
        epochs: int = 6,
        learning_rate: float = 0.05,
        negative_samples: int = 8,
        max_train_pairs: int = 8000,
        seed: int = 42,
    ):
        self.vocab_path = vocab_path
        self.embeddings_path = embeddings_path
        self.train_sequences_path = train_sequences_path
        self.val_sequences_path = val_sequences_path
        self.test_sequences_path = test_sequences_path
        self.output_dir = output_dir
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.negative_samples = negative_samples
        self.max_train_pairs = max_train_pairs
        self.seed = seed

        self.random = random.Random(seed)

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.vocab_size = 0
        self.vector_dim = 0

        self.input_embeddings: List[List[float]] = []
        self.output_embeddings: List[List[float]] = []
        self.output_bias: List[float] = []

        self.negative_sampling_pool: List[int] = []

    def run(self) -> Dict:
        self._load_vocab_and_embeddings()

        train_records = self._read_jsonl(self.train_sequences_path)
        val_records = self._read_jsonl(self.val_sequences_path)
        test_records = self._read_jsonl(self.test_sequences_path)

        train_pairs = self._extract_pairs(train_records)
        val_pairs = self._extract_pairs(val_records)
        test_pairs = self._extract_pairs(test_records)

        if not train_pairs:
            raise ValueError("Nessuna coppia token->target trovata nel train set.")

        self.random.shuffle(train_pairs)
        train_pairs = train_pairs[: self.max_train_pairs]

        self._initialize_output_embeddings()
        self._build_negative_sampling_pool(train_pairs)

        history = self._train(train_pairs=train_pairs, val_pairs=val_pairs)
        eval_result = self._evaluate_all(train_pairs=train_pairs, val_pairs=val_pairs, test_pairs=test_pairs)

        manifest = self._save_outputs(
            train_pairs=train_pairs,
            val_pairs=val_pairs,
            test_pairs=test_pairs,
            history=history,
            eval_result=eval_result,
        )

        return manifest

    def _load_vocab_and_embeddings(self) -> None:
        if not self.vocab_path.exists():
            raise FileNotFoundError(f"Vocabolario non trovato: {self.vocab_path}")

        if not self.embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings non trovati: {self.embeddings_path}")

        vocab_payload = json.loads(self.vocab_path.read_text(encoding="utf-8"))
        embeddings_payload = json.loads(self.embeddings_path.read_text(encoding="utf-8"))

        self.token_to_id = vocab_payload["token_to_id"]
        self.id_to_token = vocab_payload["id_to_token"]
        self.vocab_size = int(vocab_payload["vocab_size"])

        self.input_embeddings = embeddings_payload["embedding_matrix"]
        self.vector_dim = int(embeddings_payload["dimensione"])

        if len(self.input_embeddings) != self.vocab_size:
            raise ValueError("Embedding matrix e vocabolario hanno dimensioni incoerenti.")

        if self.vocab_size < 10:
            raise ValueError("Vocabolario troppo piccolo per training neurale.")

    def _read_jsonl(self, path: Path) -> List[Dict]:
        if not path.exists():
            raise FileNotFoundError(f"Sequenze token non trovate: {path}")

        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSON non valido in {path}:{line_number}: {error}") from error

        return records

    def _extract_pairs(self, records: List[Dict]) -> List[Tuple[int, int]]:
        pairs: List[Tuple[int, int]] = []

        pad_id = self.SPECIAL_TOKEN_IDS["PAD"]

        for record in records:
            token_ids = record.get("token_ids", [])
            labels = record.get("labels", [])
            attention_mask = record.get("attention_mask", [])

            for token_id, label, mask in zip(token_ids, labels, attention_mask):
                if mask != 1:
                    continue

                if label == -100:
                    continue

                if token_id == pad_id or label == pad_id:
                    continue

                if token_id < 0 or token_id >= self.vocab_size:
                    continue

                if label < 0 or label >= self.vocab_size:
                    continue

                pairs.append((int(token_id), int(label)))

        return pairs

    def _initialize_output_embeddings(self) -> None:
        self.output_embeddings = []
        self.output_bias = [0.0 for _ in range(self.vocab_size)]

        for token_id in range(self.vocab_size):
            if token_id == self.SPECIAL_TOKEN_IDS["PAD"]:
                vector = [0.0 for _ in range(self.vector_dim)]
            else:
                vector = self._deterministic_small_vector(token_id=token_id)

            self.output_embeddings.append(vector)

    def _deterministic_small_vector(self, token_id: int) -> List[float]:
        local_random = random.Random(self.seed + token_id * 7919)
        return [round(local_random.uniform(-0.02, 0.02), 8) for _ in range(self.vector_dim)]

    def _build_negative_sampling_pool(self, train_pairs: List[Tuple[int, int]]) -> None:
        counts = Counter(target for _source, target in train_pairs)

        weighted_ids: List[int] = []

        for token_id, count in counts.items():
            if token_id == self.SPECIAL_TOKEN_IDS["PAD"]:
                continue

            weight = max(1, int((count ** 0.75) * 10))
            weighted_ids.extend([token_id] * weight)

        if not weighted_ids:
            weighted_ids = list(range(1, self.vocab_size))

        self.negative_sampling_pool = weighted_ids

    def _train(self, train_pairs: List[Tuple[int, int]], val_pairs: List[Tuple[int, int]]) -> List[Dict]:
        history: List[Dict] = []

        for epoch in range(1, self.epochs + 1):
            self.random.shuffle(train_pairs)

            losses: List[float] = []

            for source_id, target_id in train_pairs:
                loss = self._train_pair(source_id=source_id, target_id=target_id)
                losses.append(loss)

            train_loss = round(statistics.mean(losses), 6) if losses else 0.0
            val_loss = round(self._evaluate_pairs(val_pairs), 6) if val_pairs else 0.0

            history.append(
                {
                    "epoch": epoch,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "pairs_used": len(train_pairs),
                    "learning_rate": self.learning_rate,
                    "negative_samples": self.negative_samples,
                }
            )

            print(
                f"Epoch {epoch}/{self.epochs} - "
                f"train_loss={train_loss} - val_loss={val_loss} - pairs={len(train_pairs)}"
            )

        return history

    def _train_pair(self, source_id: int, target_id: int) -> float:
        source_vector = self.input_embeddings[source_id]
        positive_loss = self._update_binary_pair(source_vector, target_id, label=1.0)

        negative_losses: List[float] = []

        for _ in range(self.negative_samples):
            negative_id = self._sample_negative(exclude=target_id)
            negative_loss = self._update_binary_pair(source_vector, negative_id, label=0.0)
            negative_losses.append(negative_loss)

        return positive_loss + sum(negative_losses)

    def _update_binary_pair(self, source_vector: List[float], output_id: int, label: float) -> float:
        output_vector = self.output_embeddings[output_id]
        bias = self.output_bias[output_id]

        score = self._dot(source_vector, output_vector) + bias
        probability = self._sigmoid(score)
        error = probability - label

        old_output_vector = list(output_vector)

        for index in range(self.vector_dim):
            output_vector[index] -= self.learning_rate * error * source_vector[index]

        self.output_bias[output_id] -= self.learning_rate * error

        # Aggiorna anche l'embedding di input sorgente in modo leggero.
        # Qui usiamo un update piccolo per rendere la rappresentazione appresa,
        # non solo una matrice output addestrata.
        source_update_scale = self.learning_rate * 0.10 * error

        for index in range(self.vector_dim):
            source_vector[index] -= source_update_scale * old_output_vector[index]

        return self._binary_cross_entropy(probability, label)

    def _sample_negative(self, exclude: int) -> int:
        for _attempt in range(20):
            candidate = self.random.choice(self.negative_sampling_pool)

            if candidate != exclude and candidate != self.SPECIAL_TOKEN_IDS["PAD"]:
                return candidate

        candidate = self.random.randint(1, self.vocab_size - 1)

        if candidate == exclude:
            candidate = (candidate + 1) % self.vocab_size

            if candidate == self.SPECIAL_TOKEN_IDS["PAD"]:
                candidate = self.SPECIAL_TOKEN_IDS["UNK"]

        return candidate

    def _evaluate_all(
        self,
        train_pairs: List[Tuple[int, int]],
        val_pairs: List[Tuple[int, int]],
        test_pairs: List[Tuple[int, int]],
    ) -> Dict:
        return {
            "train_loss": round(self._evaluate_pairs(train_pairs[: min(len(train_pairs), 2000)]), 6),
            "val_loss": round(self._evaluate_pairs(val_pairs), 6) if val_pairs else 0.0,
            "test_loss": round(self._evaluate_pairs(test_pairs), 6) if test_pairs else 0.0,
            "sample_predictions": self._sample_predictions(),
        }

    def _evaluate_pairs(self, pairs: List[Tuple[int, int]]) -> float:
        if not pairs:
            return 0.0

        losses: List[float] = []

        sample_pairs = pairs[: min(len(pairs), 2000)]

        for source_id, target_id in sample_pairs:
            source_vector = self.input_embeddings[source_id]

            positive_probability = self._score_probability(source_vector, target_id)
            positive_loss = self._binary_cross_entropy(positive_probability, 1.0)

            negative_losses: List[float] = []

            for _ in range(min(4, self.negative_samples)):
                negative_id = self._sample_negative(exclude=target_id)
                negative_probability = self._score_probability(source_vector, negative_id)
                negative_losses.append(self._binary_cross_entropy(negative_probability, 0.0))

            losses.append(positive_loss + sum(negative_losses))

        return statistics.mean(losses)

    def _score_probability(self, source_vector: List[float], output_id: int) -> float:
        score = self._dot(source_vector, self.output_embeddings[output_id]) + self.output_bias[output_id]
        return self._sigmoid(score)

    def _sample_predictions(self) -> List[Dict]:
        sample_tokens = [
            "password",
            "sicurezza",
            "backup",
            "phishing",
            "dati",
            "ransomware",
        ]

        predictions: List[Dict] = []

        for token in sample_tokens:
            token_id = self.token_to_id.get(token)

            if token_id is None:
                continue

            top = self.predict_next_tokens(token_id=token_id, top_k=8)

            predictions.append(
                {
                    "input_token": token,
                    "input_id": token_id,
                    "top_predictions": top,
                }
            )

        return predictions

    def predict_next_tokens(self, token_id: int, top_k: int = 10) -> List[Dict]:
        source_vector = self.input_embeddings[token_id]
        scored: List[Tuple[float, int]] = []

        for candidate_id in range(self.vocab_size):
            if candidate_id == self.SPECIAL_TOKEN_IDS["PAD"]:
                continue

            score = self._dot(source_vector, self.output_embeddings[candidate_id]) + self.output_bias[candidate_id]
            scored.append((score, candidate_id))

        scored.sort(reverse=True, key=lambda item: item[0])

        result: List[Dict] = []

        for score, candidate_id in scored[:top_k]:
            result.append(
                {
                    "token": self.id_to_token[candidate_id],
                    "token_id": candidate_id,
                    "score": round(score, 6),
                    "probability_sigmoid": round(self._sigmoid(score), 6),
                }
            )

        return result

    def _save_outputs(
        self,
        train_pairs: List[Tuple[int, int]],
        val_pairs: List[Tuple[int, int]],
        test_pairs: List[Tuple[int, int]],
        history: List[Dict],
        eval_result: Dict,
    ) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        model_path = self.output_dir / "neural_model_v1_weights.json"
        manifest_path = self.output_dir / "neural_model_v1_manifest.json"
        predictions_path = self.output_dir / "neural_model_v1_sample_predictions.json"

        weights = {
            "versione": "neural_model_v1_weights",
            "architecture": "neural_bigram_negative_sampling_v1",
            "vocab_size": self.vocab_size,
            "vector_dim": self.vector_dim,
            "token_to_id": self.token_to_id,
            "id_to_token": self.id_to_token,
            "input_embeddings": self.input_embeddings,
            "output_embeddings": self.output_embeddings,
            "output_bias": self.output_bias,
        }

        model_path.write_text(
            json.dumps(weights, ensure_ascii=False),
            encoding="utf-8",
        )

        predictions_path.write_text(
            json.dumps(eval_result["sample_predictions"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        manifest = {
            "versione": "neural_model_v1",
            "status": "trained",
            "architecture": {
                "name": "neural_bigram_negative_sampling_v1",
                "description": "Embedding input + embedding output, training token corrente -> token successivo con negative sampling.",
                "is_transformer": False,
                "is_first_neural_model": True,
            },
            "input_files": {
                "vocab": str(self.vocab_path),
                "initial_embeddings": str(self.embeddings_path),
                "train_sequences": str(self.train_sequences_path),
                "val_sequences": str(self.val_sequences_path),
                "test_sequences": str(self.test_sequences_path),
            },
            "output_files": {
                "weights": str(model_path),
                "manifest": str(manifest_path),
                "sample_predictions": str(predictions_path),
            },
            "hyperparameters": {
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "negative_samples": self.negative_samples,
                "max_train_pairs": self.max_train_pairs,
                "seed": self.seed,
            },
            "model_dimensions": {
                "vocab_size": self.vocab_size,
                "vector_dim": self.vector_dim,
                "input_embedding_rows": len(self.input_embeddings),
                "output_embedding_rows": len(self.output_embeddings),
                "output_bias_values": len(self.output_bias),
            },
            "training_data": {
                "train_pairs_used": len(train_pairs),
                "val_pairs": len(val_pairs),
                "test_pairs": len(test_pairs),
            },
            "history": history,
            "evaluation": eval_result,
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return manifest

    def _dot(self, left: List[float], right: List[float]) -> float:
        return sum(a * b for a, b in zip(left, right))

    def _sigmoid(self, value: float) -> float:
        if value >= 0:
            z = math.exp(-value)
            return 1 / (1 + z)

        z = math.exp(value)
        return z / (1 + z)

    def _binary_cross_entropy(self, probability: float, label: float) -> float:
        eps = 1e-8
        probability = min(max(probability, eps), 1 - eps)
        return -(label * math.log(probability) + (1 - label) * math.log(1 - probability))


def build_report(manifest: Dict) -> str:
    history_lines = []

    for item in manifest.get("history", []):
        history_lines.append(
            f"- Epoch {item['epoch']}: train_loss={item['train_loss']}, "
            f"val_loss={item['val_loss']}, pairs={item['pairs_used']}"
        )

    history_block = "\n".join(history_lines) if history_lines else "Nessuna epoca registrata."

    predictions_block = json.dumps(
        manifest.get("evaluation", {}).get("sample_predictions", []),
        ensure_ascii=False,
        indent=2,
    )

    return f"""# Report Neural Model V1

## Stato
{manifest.get("status")}

## Architettura
- Nome: {manifest["architecture"]["name"]}
- Primo modello neurale: {manifest["architecture"]["is_first_neural_model"]}
- Transformer: {manifest["architecture"]["is_transformer"]}

## Dimensioni modello
- Vocabolario: {manifest["model_dimensions"]["vocab_size"]}
- Dimensione vettori: {manifest["model_dimensions"]["vector_dim"]}
- Righe embedding input: {manifest["model_dimensions"]["input_embedding_rows"]}
- Righe embedding output: {manifest["model_dimensions"]["output_embedding_rows"]}

## Dati training
- Train pairs usate: {manifest["training_data"]["train_pairs_used"]}
- Validation pairs: {manifest["training_data"]["val_pairs"]}
- Test pairs: {manifest["training_data"]["test_pairs"]}

## Iperparametri
```json
{json.dumps(manifest["hyperparameters"], ensure_ascii=False, indent=2)}
```

## Storia training
{history_block}

## Valutazione
```json
{json.dumps(manifest["evaluation"], ensure_ascii=False, indent=2)}
```

## Esempi predizione token successivo
```json
{predictions_block}
```

## Nota
Questo è un primo modello neurale pratico. Non è ancora un Transformer e non è ancora un LLM completo.
Serve a verificare che la pipeline possa addestrare pesi numerici partendo da token e vettori.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Neural Model V1")

    parser.add_argument(
        "--vocab",
        default="mini_llm/data/vectorized/token_vocab_v1.json",
        help="Vocabolario token V1.",
    )

    parser.add_argument(
        "--embeddings",
        default="mini_llm/data/vectorized/token_embeddings_v1.json",
        help="Embeddings iniziali V1.",
    )

    parser.add_argument(
        "--train",
        default="mini_llm/data/vectorized/token_sequences_v1_train.jsonl",
        help="Sequenze train.",
    )

    parser.add_argument(
        "--val",
        default="mini_llm/data/vectorized/token_sequences_v1_val.jsonl",
        help="Sequenze validation.",
    )

    parser.add_argument(
        "--test",
        default="mini_llm/data/vectorized/token_sequences_v1_test.jsonl",
        help="Sequenze test.",
    )

    parser.add_argument(
        "--output-dir",
        default="mini_llm/data/model_v1",
        help="Cartella output modello.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/neural_model_v1_report.md",
        help="Report Markdown.",
    )

    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--negative-samples", type=int, default=8)
    parser.add_argument("--max-train-pairs", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=42)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    model = NeuralBigramModelV1(
        vocab_path=(root / args.vocab).resolve(),
        embeddings_path=(root / args.embeddings).resolve(),
        train_sequences_path=(root / args.train).resolve(),
        val_sequences_path=(root / args.val).resolve(),
        test_sequences_path=(root / args.test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        negative_samples=args.negative_samples,
        max_train_pairs=args.max_train_pairs,
        seed=args.seed,
    )

    manifest = model.run()

    report_path = (root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(manifest), encoding="utf-8")

    print("OK - Neural Model V1 addestrato")
    print(f"Pesi: {manifest['output_files']['weights']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Predizioni esempio: {manifest['output_files']['sample_predictions']}")
    print(f"Report: {report_path}")
    print(f"Vocabolario: {manifest['model_dimensions']['vocab_size']}")
    print(f"Vector dim: {manifest['model_dimensions']['vector_dim']}")
    print(f"Train pairs usate: {manifest['training_data']['train_pairs_used']}")
    print(f"Val loss finale: {manifest['evaluation']['val_loss']}")
    print(f"Test loss finale: {manifest['evaluation']['test_loss']}")


if __name__ == "__main__":
    main()
