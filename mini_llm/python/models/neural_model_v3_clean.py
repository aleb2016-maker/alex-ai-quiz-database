from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class NeuralModelV3Clean:
    """
    Neural Model V3 Clean.

    Primo training neurale sulla catena pulita:

    Dataset V2 Clean
    -> Token Vectorizer V2 Clean
    -> Neural Model V3 Clean

    Architettura pratica iniziale:
    - legge token_vocab_v2_clean.json;
    - legge token_embeddings_v2_clean.json;
    - legge sequenze token V2 clean train/val/test;
    - usa contesto multi-token;
    - costruisce un vettore contesto come media pesata degli ultimi token;
    - addestra output embeddings e bias con negative sampling;
    - valuta con cross entropy full-softmax su validation/test;
    - salva pesi, manifest, predizioni campione e report.

    Nota:
    non è ancora un Transformer completo.
    È un modello neurale locale piccolo, controllabile e utile per avanzare
    verso inferenza V3 su dati puliti.
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

    DEFAULT_PROMPTS = [
        "password",
        "password sicure",
        "sicurezza informatica",
        "backup regolari",
        "phishing",
        "dati sensibili",
        "autenticazione a due fattori",
        "attacco ransomware",
    ]

    def __init__(
        self,
        vocab_path: Path,
        embeddings_path: Path,
        train_sequences_path: Path,
        val_sequences_path: Path,
        test_sequences_path: Path,
        output_dir: Path,
        report_path: Path,
        context_size: int = 8,
        epochs: int = 8,
        learning_rate: float = 0.045,
        negative_samples: int = 18,
        seed: int = 42,
        max_train_examples: int = 0,
    ):
        self.vocab_path = vocab_path
        self.embeddings_path = embeddings_path
        self.train_sequences_path = train_sequences_path
        self.val_sequences_path = val_sequences_path
        self.test_sequences_path = test_sequences_path
        self.output_dir = output_dir
        self.report_path = report_path
        self.context_size = context_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.negative_samples = negative_samples
        self.seed = seed
        self.max_train_examples = max_train_examples

        self.random = random.Random(seed)

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.input_embeddings: List[List[float]] = []
        self.output_embeddings: List[List[float]] = []
        self.output_bias: List[float] = []

        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3

        self.vocab_size = 0
        self.vector_dim = 0

    def run(self) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_vocab()
        self._load_embeddings()
        self._initialize_trainable_weights()

        train_sequences = self._read_jsonl(self.train_sequences_path)
        val_sequences = self._read_jsonl(self.val_sequences_path)
        test_sequences = self._read_jsonl(self.test_sequences_path)

        train_examples = self._build_examples(train_sequences, split="train")
        val_examples = self._build_examples(val_sequences, split="val")
        test_examples = self._build_examples(test_sequences, split="test")

        if self.max_train_examples and self.max_train_examples > 0:
            train_examples = train_examples[: self.max_train_examples]

        if not train_examples:
            raise ValueError("Nessun esempio train disponibile per Neural Model V3 Clean.")

        negative_pool = self._build_negative_pool(train_examples)
        epoch_history = self._train(train_examples, val_examples, negative_pool)

        train_loss_final = self._sampled_loss(train_examples[: min(1000, len(train_examples))], negative_pool)
        val_loss_final = self._full_softmax_loss(val_examples)
        test_loss_final = self._full_softmax_loss(test_examples)

        sample_predictions = self._build_sample_predictions()

        weights_path = self.output_dir / "neural_model_v3_clean_weights.json"
        manifest_path = self.output_dir / "neural_model_v3_clean_manifest.json"
        predictions_path = self.output_dir / "neural_model_v3_clean_sample_predictions.json"

        weights_payload = {
            "versione": "neural_model_v3_clean_weights",
            "description": "Pesi trainable Neural Model V3 Clean.",
            "settings": {
                "context_size": self.context_size,
                "vector_dim": self.vector_dim,
                "vocab_size": self.vocab_size,
                "negative_samples": self.negative_samples,
                "seed": self.seed,
                "source_vectorizer": "token_vectorizer_v2_clean",
                "input_embeddings_source": str(self.embeddings_path),
                "vocab_source": str(self.vocab_path),
            },
            "token_to_id": self.token_to_id,
            "id_to_token": self.id_to_token,
            "output_embeddings": self.output_embeddings,
            "output_bias": self.output_bias,
        }

        weights_path.write_text(
            json.dumps(weights_payload, ensure_ascii=False),
            encoding="utf-8",
        )

        predictions_path.write_text(
            json.dumps(sample_predictions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        manifest = {
            "versione": "neural_model_v3_clean",
            "status": "trained",
            "description": "Primo modello neurale addestrato sulla catena V2 Clean.",
            "input_files": {
                "vocab": str(self.vocab_path),
                "embeddings": str(self.embeddings_path),
                "train_sequences": str(self.train_sequences_path),
                "val_sequences": str(self.val_sequences_path),
                "test_sequences": str(self.test_sequences_path),
            },
            "output_files": {
                "weights": str(weights_path),
                "manifest": str(manifest_path),
                "sample_predictions": str(predictions_path),
                "report": str(self.report_path),
            },
            "settings": {
                "context_size": self.context_size,
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "negative_samples": self.negative_samples,
                "seed": self.seed,
                "max_train_examples": self.max_train_examples,
                "uses_vectorizer_v2_clean": True,
            },
            "model": {
                "vocab_size": self.vocab_size,
                "vector_dim": self.vector_dim,
                "trainable_output_embeddings": True,
                "trainable_output_bias": True,
                "input_embeddings_trainable": False,
                "architecture": "weighted_context_negative_sampling",
            },
            "examples": {
                "train": len(train_examples),
                "val": len(val_examples),
                "test": len(test_examples),
            },
            "loss": {
                "train_sampled_final": train_loss_final,
                "val_full_softmax_final": val_loss_final,
                "test_full_softmax_final": test_loss_final,
                "epoch_history": epoch_history,
            },
            "quality": self._quality_summary(sample_predictions),
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.report_path.write_text(
            self._build_report(manifest, sample_predictions),
            encoding="utf-8",
        )

        return manifest

    def _load_vocab(self) -> None:
        payload = json.loads(self.vocab_path.read_text(encoding="utf-8"))

        self.token_to_id = {
            str(token): int(token_id)
            for token, token_id in payload["token_to_id"].items()
        }
        self.id_to_token = [str(token) for token in payload["id_to_token"]]

        self.pad_id = self.token_to_id["<PAD>"]
        self.unk_id = self.token_to_id["<UNK>"]
        self.bos_id = self.token_to_id["<BOS>"]
        self.eos_id = self.token_to_id["<EOS>"]

        self.vocab_size = len(self.id_to_token)

    def _load_embeddings(self) -> None:
        payload = json.loads(self.embeddings_path.read_text(encoding="utf-8"))

        self.input_embeddings = [
            [float(value) for value in row]
            for row in payload["embedding_matrix"]
        ]

        self.vector_dim = int(payload["dimensione"])

        if len(self.input_embeddings) != self.vocab_size:
            raise ValueError("Embedding matrix incoerente con vocab size.")

        if self.input_embeddings and len(self.input_embeddings[0]) != self.vector_dim:
            raise ValueError("Dimensione embeddings incoerente.")

    def _initialize_trainable_weights(self) -> None:
        # Parte dagli embedding V2 puliti, poi il training li specializza come output embeddings.
        self.output_embeddings = [
            [float(value) for value in row]
            for row in self.input_embeddings
        ]

        self.output_bias = [0.0 for _ in range(self.vocab_size)]

    def _read_jsonl(self, path: Path) -> List[Dict]:
        if not path.exists():
            raise FileNotFoundError(f"Sequenze non trovate: {path}")

        records: List[Dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSONL non valido in {path}:{line_number}: {error}") from error

                if isinstance(payload, dict):
                    records.append(payload)

        return records

    def _build_examples(self, sequences: List[Dict], split: str) -> List[Dict]:
        examples: List[Dict] = []

        for sequence_index, sequence in enumerate(sequences, start=1):
            token_ids = [
                int(token_id)
                for token_id, mask in zip(sequence["token_ids"], sequence["attention_mask"])
                if int(mask) == 1
            ]

            # token_ids attivi: <BOS> ... <EOS>
            for position in range(1, len(token_ids)):
                target_id = token_ids[position]

                if target_id == self.pad_id:
                    continue

                context_start = max(0, position - self.context_size)
                context_ids = token_ids[context_start:position]

                if not context_ids:
                    continue

                examples.append(
                    {
                        "example_id": f"{split}-{sequence_index:05d}-{position:03d}",
                        "split": split,
                        "context_ids": context_ids,
                        "target_id": target_id,
                    }
                )

        return examples

    def _build_negative_pool(self, examples: List[Dict]) -> List[int]:
        counts: Dict[int, int] = {}

        for example in examples:
            target_id = int(example["target_id"])

            if target_id in {self.pad_id, self.unk_id, self.bos_id}:
                continue

            counts[target_id] = counts.get(target_id, 0) + 1

        weighted_pool: List[int] = []

        for token_id, count in counts.items():
            # Approssimazione unigram^0.75 senza librerie esterne.
            repeats = max(1, int(round(count ** 0.75)))
            weighted_pool.extend([token_id] * repeats)

        if not weighted_pool:
            weighted_pool = [
                token_id
                for token_id in range(self.vocab_size)
                if token_id not in {self.pad_id, self.unk_id, self.bos_id}
            ]

        return weighted_pool

    def _train(self, train_examples: List[Dict], val_examples: List[Dict], negative_pool: List[int]) -> List[Dict]:
        history: List[Dict] = []
        examples = list(train_examples)

        for epoch in range(1, self.epochs + 1):
            self.random.shuffle(examples)

            # Decadimento leggero per stabilizzare le ultime epoche.
            epoch_lr = self.learning_rate * (0.92 ** (epoch - 1))

            total_loss = 0.0

            for example in examples:
                total_loss += self._train_one_example(example, negative_pool, epoch_lr)

            avg_train_loss = total_loss / max(1, len(examples))
            val_loss = self._full_softmax_loss(val_examples)

            history.append(
                {
                    "epoch": epoch,
                    "learning_rate": round(epoch_lr, 8),
                    "train_sampled_loss": round(avg_train_loss, 6),
                    "val_full_softmax_loss": round(val_loss, 6),
                }
            )

            print(
                f"Epoch {epoch}/{self.epochs} "
                f"train_loss={avg_train_loss:.6f} "
                f"val_loss={val_loss:.6f}"
            )

        return history

    def _train_one_example(self, example: Dict, negative_pool: List[int], learning_rate: float) -> float:
        context_vector = self._context_vector(example["context_ids"])
        target_id = int(example["target_id"])
        negatives = self._sample_negatives(negative_pool, target_id)

        loss = 0.0

        # Positivo: massimizza sigmoid(score target).
        pos_score = self._score(context_vector, target_id)
        pos_prob = self._sigmoid(pos_score)
        pos_grad = 1.0 - pos_prob
        loss += -self._safe_log(pos_prob)

        self._update_output(token_id=target_id, context_vector=context_vector, gradient=pos_grad, learning_rate=learning_rate)

        # Negativi: massimizza sigmoid(-score negativo).
        for negative_id in negatives:
            neg_score = self._score(context_vector, negative_id)
            neg_prob = self._sigmoid(neg_score)
            neg_grad = -neg_prob
            loss += -self._safe_log(1.0 - neg_prob)

            self._update_output(token_id=negative_id, context_vector=context_vector, gradient=neg_grad, learning_rate=learning_rate)

        return loss / (1 + len(negatives))

    def _sample_negatives(self, negative_pool: List[int], target_id: int) -> List[int]:
        negatives: List[int] = []
        attempts = 0

        while len(negatives) < self.negative_samples and attempts < self.negative_samples * 12:
            candidate = self.random.choice(negative_pool)
            attempts += 1

            if candidate == target_id:
                continue

            if candidate in {self.pad_id, self.unk_id, self.bos_id}:
                continue

            negatives.append(candidate)

        if len(negatives) < self.negative_samples:
            for candidate in range(self.vocab_size):
                if candidate == target_id:
                    continue

                if candidate in {self.pad_id, self.unk_id, self.bos_id}:
                    continue

                negatives.append(candidate)

                if len(negatives) >= self.negative_samples:
                    break

        return negatives

    def _update_output(self, token_id: int, context_vector: List[float], gradient: float, learning_rate: float) -> None:
        row = self.output_embeddings[token_id]

        for index in range(self.vector_dim):
            row[index] += learning_rate * gradient * context_vector[index]

        self.output_bias[token_id] += learning_rate * gradient

    def _context_vector(self, context_ids: List[int]) -> List[float]:
        active_context = context_ids[-self.context_size :]

        if not active_context:
            return [0.0 for _ in range(self.vector_dim)]

        vector = [0.0 for _ in range(self.vector_dim)]

        # Pesa di più i token più recenti.
        weights = list(range(1, len(active_context) + 1))
        total_weight = float(sum(weights))

        for token_id, weight in zip(active_context, weights):
            embedding = self.input_embeddings[int(token_id)]
            normalized_weight = weight / total_weight

            for index in range(self.vector_dim):
                vector[index] += embedding[index] * normalized_weight

        return vector

    def _score(self, context_vector: List[float], token_id: int) -> float:
        row = self.output_embeddings[token_id]
        total = self.output_bias[token_id]

        for index in range(self.vector_dim):
            total += context_vector[index] * row[index]

        return total

    def _full_softmax_loss(self, examples: List[Dict]) -> float:
        if not examples:
            return 0.0

        total_loss = 0.0

        for example in examples:
            context_vector = self._context_vector(example["context_ids"])
            target_id = int(example["target_id"])

            scores = [
                self._score(context_vector, token_id)
                for token_id in range(self.vocab_size)
            ]

            max_score = max(scores)
            exp_sum = sum(math.exp(score - max_score) for score in scores)
            log_sum_exp = max_score + math.log(exp_sum)
            total_loss += log_sum_exp - scores[target_id]

        return round(total_loss / len(examples), 6)

    def _sampled_loss(self, examples: List[Dict], negative_pool: List[int]) -> float:
        if not examples:
            return 0.0

        total = 0.0

        # Calcola sampled loss senza aggiornare pesi.
        rng_state = self.random.getstate()

        for example in examples:
            context_vector = self._context_vector(example["context_ids"])
            target_id = int(example["target_id"])
            negatives = self._sample_negatives(negative_pool, target_id)

            pos_prob = self._sigmoid(self._score(context_vector, target_id))
            loss = -self._safe_log(pos_prob)

            for negative_id in negatives:
                neg_prob = self._sigmoid(self._score(context_vector, negative_id))
                loss += -self._safe_log(1.0 - neg_prob)

            total += loss / (1 + len(negatives))

        self.random.setstate(rng_state)

        return round(total / len(examples), 6)

    def _build_sample_predictions(self) -> List[Dict]:
        predictions: List[Dict] = []

        for prompt in self.DEFAULT_PROMPTS:
            context_ids = self._encode_prompt(prompt)

            if not context_ids:
                context_ids = [self.bos_id]

            top_predictions = self.predict_next(context_ids=context_ids, top_k=8)

            predictions.append(
                {
                    "prompt": prompt,
                    "context_tokens": [self.id_to_token[token_id] for token_id in context_ids],
                    "top_predictions": top_predictions,
                }
            )

        return predictions

    def predict_next(self, context_ids: List[int], top_k: int = 8) -> List[Dict]:
        context_vector = self._context_vector(context_ids)

        candidates: List[Tuple[int, float]] = []

        for token_id in range(self.vocab_size):
            token = self.id_to_token[token_id]

            if token_id in {self.pad_id, self.unk_id, self.bos_id}:
                continue

            if str(token).lower() in self.DIRTY_TOKENS:
                continue

            score = self._score(context_vector, token_id)
            candidates.append((token_id, score))

        candidates.sort(key=lambda item: item[1], reverse=True)

        top = candidates[:top_k]

        if not top:
            return []

        scores = [score for _token_id, score in top]
        max_score = max(scores)
        exp_scores = [math.exp(score - max_score) for score in scores]
        exp_sum = sum(exp_scores)

        result: List[Dict] = []

        for (token_id, score), exp_score in zip(top, exp_scores):
            probability = exp_score / exp_sum if exp_sum else 0.0
            result.append(
                {
                    "token_id": token_id,
                    "token": self.id_to_token[token_id],
                    "score": round(score, 6),
                    "probability_topk": round(probability, 6),
                }
            )

        return result

    def _encode_prompt(self, prompt: str) -> List[int]:
        tokens = self._tokenize(prompt)
        token_ids = [
            self.token_to_id[token]
            for token in tokens
            if token in self.token_to_id
        ]

        return token_ids[-self.context_size :]

    def _quality_summary(self, sample_predictions: List[Dict]) -> Dict:
        dirty_prediction_tokens = []
        empty_predictions = 0

        for item in sample_predictions:
            top_predictions = item.get("top_predictions", [])

            if not top_predictions:
                empty_predictions += 1

            for prediction in top_predictions:
                token = str(prediction.get("token", "")).lower()

                if token in self.DIRTY_TOKENS:
                    dirty_prediction_tokens.append(token)

        return {
            "sample_predictions": len(sample_predictions),
            "empty_predictions": empty_predictions,
            "dirty_prediction_tokens": sorted(set(dirty_prediction_tokens)),
        }

    def _build_report(self, manifest: Dict, sample_predictions: List[Dict]) -> str:
        return f"""# Report Neural Model V3 Clean

## Stato
{manifest["status"]}

## Obiettivo
Addestrare il primo modello neurale sulla catena pulita V2.

## Input
```json
{json.dumps(manifest["input_files"], ensure_ascii=False, indent=2)}
```

## Output
```json
{json.dumps(manifest["output_files"], ensure_ascii=False, indent=2)}
```

## Impostazioni
```json
{json.dumps(manifest["settings"], ensure_ascii=False, indent=2)}
```

## Modello
```json
{json.dumps(manifest["model"], ensure_ascii=False, indent=2)}
```

## Esempi
```json
{json.dumps(manifest["examples"], ensure_ascii=False, indent=2)}
```

## Loss
```json
{json.dumps(manifest["loss"], ensure_ascii=False, indent=2)}
```

## Qualità
```json
{json.dumps(manifest["quality"], ensure_ascii=False, indent=2)}
```

## Predizioni campione
```json
{json.dumps(sample_predictions, ensure_ascii=False, indent=2)}
```

## Nota
Questo è un modello neurale pratico iniziale, non ancora un Transformer.
Serve come passaggio controllato verso Inference Engine V3 Clean.
"""

    def _tokenize(self, text: str) -> List[str]:
        import re

        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _sigmoid(self, value: float) -> float:
        if value >= 0:
            z = math.exp(-value)
            return 1.0 / (1.0 + z)

        z = math.exp(value)
        return z / (1.0 + z)

    def _safe_log(self, value: float) -> float:
        return math.log(max(value, 1e-12))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Neural Model V3 Clean")

    parser.add_argument("--vocab", default="mini_llm/data/vectorized_v2/token_vocab_v2_clean.json")
    parser.add_argument("--embeddings", default="mini_llm/data/vectorized_v2/token_embeddings_v2_clean.json")
    parser.add_argument("--train", default="mini_llm/data/vectorized_v2/token_sequences_v2_clean_train.jsonl")
    parser.add_argument("--val", default="mini_llm/data/vectorized_v2/token_sequences_v2_clean_val.jsonl")
    parser.add_argument("--test", default="mini_llm/data/vectorized_v2/token_sequences_v2_clean_test.jsonl")
    parser.add_argument("--output-dir", default="mini_llm/data/model_v3_clean")
    parser.add_argument("--report", default="mini_llm/reports/neural_model_v3_clean_report.md")
    parser.add_argument("--context-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.045)
    parser.add_argument("--negative-samples", type=int, default=18)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-train-examples", type=int, default=0)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    model = NeuralModelV3Clean(
        vocab_path=(root / args.vocab).resolve(),
        embeddings_path=(root / args.embeddings).resolve(),
        train_sequences_path=(root / args.train).resolve(),
        val_sequences_path=(root / args.val).resolve(),
        test_sequences_path=(root / args.test).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        context_size=args.context_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        negative_samples=args.negative_samples,
        seed=args.seed,
        max_train_examples=args.max_train_examples,
    )

    manifest = model.run()

    print("OK - Neural Model V3 Clean addestrato")
    print(f"Pesi: {manifest['output_files']['weights']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Predizioni campione: {manifest['output_files']['sample_predictions']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Vocab size: {manifest['model']['vocab_size']}")
    print(f"Vector dim: {manifest['model']['vector_dim']}")
    print(f"Context size: {manifest['settings']['context_size']}")
    print(f"Train examples: {manifest['examples']['train']}")
    print(f"Val loss finale: {manifest['loss']['val_full_softmax_final']}")
    print(f"Test loss finale: {manifest['loss']['test_full_softmax_final']}")
    print(f"Dirty prediction tokens: {manifest['quality']['dirty_prediction_tokens']}")
    print(f"Empty predictions: {manifest['quality']['empty_predictions']}")


if __name__ == "__main__":
    main()
