from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class NeuralContextModelV2:
    """
    Neural Model V2 Context.

    Secondo modello neurale del mini LLM.

    Differenza rispetto a V1:
    - V1: token corrente -> token successivo.
    - V2: finestra di più token -> token successivo.

    Architettura pratica iniziale:
    - embedding input caricati dal Token Vectorizer V1;
    - vettore contesto = media pesata degli ultimi N token;
    - output embedding addestrabile;
    - bias output addestrabile;
    - training con negative sampling;
    - salvataggio pesi, manifest, predizioni e report.

    Nota:
    non è ancora un Transformer, ma introduce il concetto fondamentale
    di contesto multi-token.
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
        context_size: int = 6,
        epochs: int = 7,
        learning_rate: float = 0.04,
        negative_samples: int = 10,
        max_train_examples: int = 10000,
        seed: int = 42,
    ):
        self.vocab_path = vocab_path
        self.embeddings_path = embeddings_path
        self.train_sequences_path = train_sequences_path
        self.val_sequences_path = val_sequences_path
        self.test_sequences_path = test_sequences_path
        self.output_dir = output_dir
        self.context_size = context_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.negative_samples = negative_samples
        self.max_train_examples = max_train_examples
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

        train_examples = self._extract_context_examples(train_records)
        val_examples = self._extract_context_examples(val_records)
        test_examples = self._extract_context_examples(test_records)

        if not train_examples:
            raise ValueError("Nessun esempio contesto->target trovato nel train set.")

        self.random.shuffle(train_examples)
        train_examples = train_examples[: self.max_train_examples]

        self._initialize_output_embeddings()
        self._build_negative_sampling_pool(train_examples)

        history = self._train(train_examples=train_examples, val_examples=val_examples)
        evaluation = self._evaluate_all(
            train_examples=train_examples,
            val_examples=val_examples,
            test_examples=test_examples,
        )

        manifest = self._save_outputs(
            train_examples=train_examples,
            val_examples=val_examples,
            test_examples=test_examples,
            history=history,
            evaluation=evaluation,
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

        if self.context_size < 2:
            raise ValueError("context_size deve essere almeno 2.")

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

    def _extract_context_examples(self, records: List[Dict]) -> List[Dict]:
        examples: List[Dict] = []
        pad_id = self.SPECIAL_TOKEN_IDS["PAD"]

        for record in records:
            token_ids = record.get("token_ids", [])
            attention_mask = record.get("attention_mask", [])

            usable_tokens = [
                int(token_id)
                for token_id, mask in zip(token_ids, attention_mask)
                if mask == 1 and int(token_id) != pad_id
            ]

            if len(usable_tokens) < 3:
                continue

            for target_index in range(1, len(usable_tokens)):
                target_id = usable_tokens[target_index]

                if target_id == pad_id:
                    continue

                start = max(0, target_index - self.context_size)
                context_ids = usable_tokens[start:target_index]

                if not context_ids:
                    continue

                examples.append(
                    {
                        "context_ids": context_ids,
                        "target_id": target_id,
                        "source_record_id": record.get("source_record_id", ""),
                        "source_task": record.get("source_task", ""),
                    }
                )

        return examples

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
        local_random = random.Random(self.seed + token_id * 104729)
        return [round(local_random.uniform(-0.018, 0.018), 8) for _ in range(self.vector_dim)]

    def _build_negative_sampling_pool(self, train_examples: List[Dict]) -> None:
        counts = Counter(example["target_id"] for example in train_examples)
        weighted_ids: List[int] = []

        for token_id, count in counts.items():
            if token_id == self.SPECIAL_TOKEN_IDS["PAD"]:
                continue

            weight = max(1, int((count ** 0.75) * 10))
            weighted_ids.extend([token_id] * weight)

        if not weighted_ids:
            weighted_ids = list(range(1, self.vocab_size))

        self.negative_sampling_pool = weighted_ids

    def _train(self, train_examples: List[Dict], val_examples: List[Dict]) -> List[Dict]:
        history: List[Dict] = []

        for epoch in range(1, self.epochs + 1):
            self.random.shuffle(train_examples)
            losses: List[float] = []

            for example in train_examples:
                context_ids = example["context_ids"]
                target_id = example["target_id"]
                loss = self._train_example(context_ids=context_ids, target_id=target_id)
                losses.append(loss)

            train_loss = round(statistics.mean(losses), 6) if losses else 0.0
            val_loss = round(self._evaluate_examples(val_examples), 6) if val_examples else 0.0

            history.append(
                {
                    "epoch": epoch,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "examples_used": len(train_examples),
                    "learning_rate": self.learning_rate,
                    "negative_samples": self.negative_samples,
                    "context_size": self.context_size,
                }
            )

            print(
                f"Epoch {epoch}/{self.epochs} - "
                f"train_loss={train_loss} - val_loss={val_loss} - examples={len(train_examples)}"
            )

        return history

    def _train_example(self, context_ids: List[int], target_id: int) -> float:
        context_vector, context_weights = self._build_context_vector(context_ids)
        positive_loss = self._update_binary_context_pair(context_vector, context_ids, context_weights, target_id, label=1.0)

        negative_losses: List[float] = []

        for _ in range(self.negative_samples):
            negative_id = self._sample_negative(exclude=target_id)
            negative_loss = self._update_binary_context_pair(
                context_vector,
                context_ids,
                context_weights,
                negative_id,
                label=0.0,
            )
            negative_losses.append(negative_loss)

        return positive_loss + sum(negative_losses)

    def _build_context_vector(self, context_ids: List[int]) -> Tuple[List[float], List[float]]:
        if not context_ids:
            unk_id = self.SPECIAL_TOKEN_IDS["UNK"]
            context_ids = [unk_id]

        # Peso maggiore ai token più recenti.
        raw_weights = list(range(1, len(context_ids) + 1))
        weight_sum = float(sum(raw_weights))
        weights = [weight / weight_sum for weight in raw_weights]

        context_vector = [0.0 for _ in range(self.vector_dim)]

        for token_id, weight in zip(context_ids, weights):
            token_vector = self.input_embeddings[token_id]

            for index in range(self.vector_dim):
                context_vector[index] += token_vector[index] * weight

        return context_vector, weights

    def _update_binary_context_pair(
        self,
        context_vector: List[float],
        context_ids: List[int],
        context_weights: List[float],
        output_id: int,
        label: float,
    ) -> float:
        output_vector = self.output_embeddings[output_id]
        bias = self.output_bias[output_id]

        score = self._dot(context_vector, output_vector) + bias
        probability = self._sigmoid(score)
        error = probability - label

        old_output_vector = list(output_vector)

        for index in range(self.vector_dim):
            output_vector[index] -= self.learning_rate * error * context_vector[index]

        self.output_bias[output_id] -= self.learning_rate * error

        # Aggiorna gli embedding input dei token di contesto.
        for token_id, context_weight in zip(context_ids, context_weights):
            token_vector = self.input_embeddings[token_id]
            update_scale = self.learning_rate * 0.08 * error * context_weight

            for index in range(self.vector_dim):
                token_vector[index] -= update_scale * old_output_vector[index]

        return self._binary_cross_entropy(probability, label)

    def _sample_negative(self, exclude: int) -> int:
        for _attempt in range(30):
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
        train_examples: List[Dict],
        val_examples: List[Dict],
        test_examples: List[Dict],
    ) -> Dict:
        return {
            "train_loss": round(self._evaluate_examples(train_examples[: min(len(train_examples), 2500)]), 6),
            "val_loss": round(self._evaluate_examples(val_examples), 6) if val_examples else 0.0,
            "test_loss": round(self._evaluate_examples(test_examples), 6) if test_examples else 0.0,
            "sample_predictions": self._sample_predictions(),
        }

    def _evaluate_examples(self, examples: List[Dict]) -> float:
        if not examples:
            return 0.0

        losses: List[float] = []
        sample = examples[: min(len(examples), 2500)]

        for example in sample:
            context_ids = example["context_ids"]
            target_id = example["target_id"]
            context_vector, _weights = self._build_context_vector(context_ids)

            positive_probability = self._score_probability(context_vector, target_id)
            positive_loss = self._binary_cross_entropy(positive_probability, 1.0)

            negative_losses: List[float] = []

            for _ in range(min(5, self.negative_samples)):
                negative_id = self._sample_negative(exclude=target_id)
                negative_probability = self._score_probability(context_vector, negative_id)
                negative_losses.append(self._binary_cross_entropy(negative_probability, 0.0))

            losses.append(positive_loss + sum(negative_losses))

        return statistics.mean(losses)

    def _score_probability(self, context_vector: List[float], output_id: int) -> float:
        score = self._dot(context_vector, self.output_embeddings[output_id]) + self.output_bias[output_id]
        return self._sigmoid(score)

    def _sample_predictions(self) -> List[Dict]:
        sample_contexts = [
            ["<BOS>", "password"],
            ["password", "sicure"],
            ["backup", "regolari"],
            ["dati", "sensibili"],
            ["autenticazione", "a", "due"],
            ["rischio", "phishing"],
            ["attacco", "ransomware"],
        ]

        predictions: List[Dict] = []

        for context_tokens in sample_contexts:
            context_ids = [self.token_to_id.get(token, self.SPECIAL_TOKEN_IDS["UNK"]) for token in context_tokens]
            top = self.predict_next_tokens(context_ids=context_ids, top_k=8)

            predictions.append(
                {
                    "context_tokens": context_tokens,
                    "context_ids": context_ids,
                    "top_predictions": top,
                }
            )

        return predictions

    def predict_next_tokens(self, context_ids: List[int], top_k: int = 10) -> List[Dict]:
        context_vector, _weights = self._build_context_vector(context_ids)
        scored: List[Tuple[float, int]] = []

        for candidate_id in range(self.vocab_size):
            if candidate_id == self.SPECIAL_TOKEN_IDS["PAD"]:
                continue

            score = self._dot(context_vector, self.output_embeddings[candidate_id]) + self.output_bias[candidate_id]
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
        train_examples: List[Dict],
        val_examples: List[Dict],
        test_examples: List[Dict],
        history: List[Dict],
        evaluation: Dict,
    ) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        weights_path = self.output_dir / "neural_model_v2_context_weights.json"
        manifest_path = self.output_dir / "neural_model_v2_context_manifest.json"
        predictions_path = self.output_dir / "neural_model_v2_context_sample_predictions.json"

        weights = {
            "versione": "neural_model_v2_context_weights",
            "architecture": "neural_context_average_negative_sampling_v2",
            "context_size": self.context_size,
            "vocab_size": self.vocab_size,
            "vector_dim": self.vector_dim,
            "token_to_id": self.token_to_id,
            "id_to_token": self.id_to_token,
            "input_embeddings": self.input_embeddings,
            "output_embeddings": self.output_embeddings,
            "output_bias": self.output_bias,
        }

        weights_path.write_text(
            json.dumps(weights, ensure_ascii=False),
            encoding="utf-8",
        )

        predictions_path.write_text(
            json.dumps(evaluation["sample_predictions"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        manifest = {
            "versione": "neural_model_v2_context",
            "status": "trained",
            "architecture": {
                "name": "neural_context_average_negative_sampling_v2",
                "description": "Media pesata degli embedding di contesto + output embedding, training contesto multi-token -> token successivo.",
                "is_transformer": False,
                "uses_multi_token_context": True,
                "context_size": self.context_size,
            },
            "input_files": {
                "vocab": str(self.vocab_path),
                "initial_embeddings": str(self.embeddings_path),
                "train_sequences": str(self.train_sequences_path),
                "val_sequences": str(self.val_sequences_path),
                "test_sequences": str(self.test_sequences_path),
            },
            "output_files": {
                "weights": str(weights_path),
                "manifest": str(manifest_path),
                "sample_predictions": str(predictions_path),
            },
            "hyperparameters": {
                "context_size": self.context_size,
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "negative_samples": self.negative_samples,
                "max_train_examples": self.max_train_examples,
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
                "train_examples_used": len(train_examples),
                "val_examples": len(val_examples),
                "test_examples": len(test_examples),
            },
            "history": history,
            "evaluation": evaluation,
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
            f"val_loss={item['val_loss']}, examples={item['examples_used']}"
        )

    history_block = "\n".join(history_lines) if history_lines else "Nessuna epoca registrata."

    predictions_block = json.dumps(
        manifest.get("evaluation", {}).get("sample_predictions", []),
        ensure_ascii=False,
        indent=2,
    )

    return f"""# Report Neural Model V2 Context

## Stato
{manifest.get("status")}

## Architettura
- Nome: {manifest["architecture"]["name"]}
- Usa contesto multi-token: {manifest["architecture"]["uses_multi_token_context"]}
- Context size: {manifest["architecture"]["context_size"]}
- Transformer: {manifest["architecture"]["is_transformer"]}

## Dimensioni modello
- Vocabolario: {manifest["model_dimensions"]["vocab_size"]}
- Dimensione vettori: {manifest["model_dimensions"]["vector_dim"]}
- Righe embedding input: {manifest["model_dimensions"]["input_embedding_rows"]}
- Righe embedding output: {manifest["model_dimensions"]["output_embedding_rows"]}

## Dati training
- Train examples usati: {manifest["training_data"]["train_examples_used"]}
- Validation examples: {manifest["training_data"]["val_examples"]}
- Test examples: {manifest["training_data"]["test_examples"]}

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

## Predizioni di esempio
```json
{predictions_block}
```

## Nota
Questo è Neural Model V2: introduce contesto multi-token.
Non è ancora un Transformer, ma supera il limite principale del V1 bigram.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Neural Model V2 Context")

    parser.add_argument("--vocab", default="mini_llm/data/vectorized/token_vocab_v1.json")
    parser.add_argument("--embeddings", default="mini_llm/data/vectorized/token_embeddings_v1.json")
    parser.add_argument("--train", default="mini_llm/data/vectorized/token_sequences_v1_train.jsonl")
    parser.add_argument("--val", default="mini_llm/data/vectorized/token_sequences_v1_val.jsonl")
    parser.add_argument("--test", default="mini_llm/data/vectorized/token_sequences_v1_test.jsonl")
    parser.add_argument("--output-dir", default="mini_llm/data/model_v2_context")
    parser.add_argument("--report", default="mini_llm/reports/neural_model_v2_context_report.md")

    parser.add_argument("--context-size", type=int, default=6)
    parser.add_argument("--epochs", type=int, default=7)
    parser.add_argument("--learning-rate", type=float, default=0.04)
    parser.add_argument("--negative-samples", type=int, default=10)
    parser.add_argument("--max-train-examples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    model = NeuralContextModelV2(
        vocab_path=(root / args.vocab).resolve(),
        embeddings_path=(root / args.embeddings).resolve(),
        train_sequences_path=(root / args.train).resolve(),
        val_sequences_path=(root / args.val).resolve(),
        test_sequences_path=(root / args.test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        context_size=args.context_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        negative_samples=args.negative_samples,
        max_train_examples=args.max_train_examples,
        seed=args.seed,
    )

    manifest = model.run()

    report_path = (root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(manifest), encoding="utf-8")

    print("OK - Neural Model V2 Context addestrato")
    print(f"Pesi: {manifest['output_files']['weights']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Predizioni esempio: {manifest['output_files']['sample_predictions']}")
    print(f"Report: {report_path}")
    print(f"Vocabolario: {manifest['model_dimensions']['vocab_size']}")
    print(f"Vector dim: {manifest['model_dimensions']['vector_dim']}")
    print(f"Context size: {manifest['architecture']['context_size']}")
    print(f"Train examples usati: {manifest['training_data']['train_examples_used']}")
    print(f"Val loss finale: {manifest['evaluation']['val_loss']}")
    print(f"Test loss finale: {manifest['evaluation']['test_loss']}")


if __name__ == "__main__":
    main()
