from __future__ import annotations

import argparse
import json
import math
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple


class InferenceEngineV2Context:
    """
    Inference Engine V2 Context.

    Usa i pesi del Neural Model V2 Context per generare brevi sequenze
    considerando una finestra di contesto multi-token.

    Differenza rispetto a Inference V1:
    - V1 usa solo l'ultimo token.
    - V2 usa gli ultimi N token, con N = context_size del modello.

    Nota:
    questo è ancora un motore pratico iniziale.
    Il modello sottostante non è un Transformer, ma introduce inferenza con contesto.
    """

    BLOCKED_GENERATION_TOKENS = {"<PAD>", "<BOS>", "<UNK>"}
    STOP_TOKENS = {"<EOS>"}

    DEFAULT_PROMPTS = [
        "password",
        "password sicure",
        "sicurezza informatica",
        "backup regolari",
        "phishing",
        "dati sensibili",
        "autenticazione a due",
        "attacco ransomware",
    ]

    def __init__(
        self,
        weights_path: Path,
        manifest_path: Path,
        output_dir: Path,
        max_new_tokens: int = 28,
        top_k: int = 8,
        temperature: float = 0.80,
        seed: int = 42,
    ):
        self.weights_path = weights_path
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        self.max_new_tokens = max_new_tokens
        self.top_k = top_k
        self.temperature = max(0.05, temperature)
        self.seed = seed
        self.random = random.Random(seed)

        self.weights: Dict = {}
        self.model_manifest: Dict = {}
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.input_embeddings: List[List[float]] = []
        self.output_embeddings: List[List[float]] = []
        self.output_bias: List[float] = []
        self.vocab_size = 0
        self.vector_dim = 0
        self.context_size = 6

    def run(self, prompts: List[str]) -> Dict:
        self._load_model()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        outputs = []

        for prompt in prompts:
            outputs.append(self.generate(prompt=prompt))

        outputs_path = self.output_dir / "inference_engine_v2_context_outputs.json"
        manifest_path = self.output_dir / "inference_engine_v2_context_manifest.json"

        outputs_path.write_text(
            json.dumps(outputs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        manifest = {
            "versione": "inference_engine_v2_context",
            "status": "generated",
            "model": {
                "weights_path": str(self.weights_path),
                "manifest_path": str(self.manifest_path),
                "architecture": self.model_manifest.get("architecture", {}),
                "vocab_size": self.vocab_size,
                "vector_dim": self.vector_dim,
                "context_size": self.context_size,
            },
            "generation": {
                "max_new_tokens": self.max_new_tokens,
                "top_k": self.top_k,
                "temperature": self.temperature,
                "seed": self.seed,
                "prompts_count": len(prompts),
                "uses_context_window": True,
            },
            "output_files": {
                "outputs": str(outputs_path),
                "manifest": str(manifest_path),
            },
            "summary": {
                "total_generations": len(outputs),
                "non_empty_generations": sum(1 for item in outputs if item.get("generated_text", "").strip()),
                "average_generated_tokens": round(
                    sum(len(item.get("generated_tokens", [])) for item in outputs) / len(outputs),
                    2,
                ) if outputs else 0,
                "average_context_steps": round(
                    sum(len(item.get("steps", [])) for item in outputs) / len(outputs),
                    2,
                ) if outputs else 0,
            },
            "outputs_preview": outputs[:5],
        }

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return manifest

    def generate(self, prompt: str) -> Dict:
        clean_prompt = self._clean_text(prompt)
        prompt_tokens = self._tokenize(clean_prompt)
        prompt_token_ids = [self.token_to_id.get(token, self.token_to_id.get("<UNK>", 1)) for token in prompt_tokens]

        if not prompt_token_ids:
            prompt_token_ids = [self.token_to_id.get("<BOS>", 2)]

        context_ids = list(prompt_token_ids)[-self.context_size:]

        generated_token_ids: List[int] = []
        generated_tokens: List[str] = []
        step_debug: List[Dict] = []

        for step in range(1, self.max_new_tokens + 1):
            candidates = self.predict_next(context_ids=context_ids, top_k=max(self.top_k, 2))

            if not candidates:
                break

            selected = self._select_candidate(candidates)
            selected_token = selected["token"]
            selected_id = selected["token_id"]

            context_tokens = [self._token_from_id(token_id) for token_id in context_ids]

            step_debug.append(
                {
                    "step": step,
                    "context_tokens": context_tokens,
                    "context_ids": list(context_ids),
                    "selected_token": selected_token,
                    "selected_id": selected_id,
                    "selected_score": selected["score"],
                    "top_candidates": candidates[: min(5, len(candidates))],
                }
            )

            if selected_token in self.STOP_TOKENS:
                break

            generated_token_ids.append(selected_id)
            generated_tokens.append(selected_token)

            context_ids.append(selected_id)
            context_ids = context_ids[-self.context_size:]

        generated_text = self._detokenize(generated_tokens)

        return {
            "prompt": clean_prompt,
            "prompt_tokens": prompt_tokens,
            "prompt_token_ids": prompt_token_ids,
            "context_size": self.context_size,
            "generated_tokens": generated_tokens,
            "generated_token_ids": generated_token_ids,
            "generated_text": generated_text,
            "full_text": self._join_prompt_and_generation(clean_prompt, generated_text),
            "steps": step_debug,
        }

    def predict_next(self, context_ids: List[int], top_k: int = 10) -> List[Dict]:
        clean_context_ids = [
            token_id
            for token_id in context_ids[-self.context_size:]
            if 0 <= token_id < self.vocab_size
        ]

        if not clean_context_ids:
            clean_context_ids = [self.token_to_id.get("<UNK>", 1)]

        context_vector, context_weights = self._build_context_vector(clean_context_ids)
        scored: List[Tuple[float, int]] = []

        for candidate_id in range(self.vocab_size):
            token = self._token_from_id(candidate_id)

            if token in self.BLOCKED_GENERATION_TOKENS:
                continue

            score = self._dot(context_vector, self.output_embeddings[candidate_id]) + self.output_bias[candidate_id]
            scored.append((score, candidate_id))

        scored.sort(reverse=True, key=lambda item: item[0])

        results: List[Dict] = []

        for score, candidate_id in scored[:top_k]:
            results.append(
                {
                    "token": self._token_from_id(candidate_id),
                    "token_id": candidate_id,
                    "score": round(score, 6),
                    "probability_sigmoid": round(self._sigmoid(score), 6),
                    "context_weighted": True,
                    "context_length": len(clean_context_ids),
                }
            )

        return results

    def _build_context_vector(self, context_ids: List[int]) -> Tuple[List[float], List[float]]:
        if not context_ids:
            context_ids = [self.token_to_id.get("<UNK>", 1)]

        raw_weights = list(range(1, len(context_ids) + 1))
        weight_sum = float(sum(raw_weights))
        weights = [weight / weight_sum for weight in raw_weights]

        context_vector = [0.0 for _ in range(self.vector_dim)]

        for token_id, weight in zip(context_ids, weights):
            token_vector = self.input_embeddings[token_id]

            for index in range(self.vector_dim):
                context_vector[index] += token_vector[index] * weight

        return context_vector, weights

    def _select_candidate(self, candidates: List[Dict]) -> Dict:
        filtered = [
            candidate
            for candidate in candidates
            if candidate["token"] not in self.BLOCKED_GENERATION_TOKENS
        ]

        if not filtered:
            return candidates[0]

        if len(filtered) == 1:
            return filtered[0]

        scores = [candidate["score"] for candidate in filtered]
        max_score = max(scores)
        exp_scores = [math.exp((score - max_score) / self.temperature) for score in scores]
        total = sum(exp_scores)

        if total <= 0:
            return filtered[0]

        probabilities = [value / total for value in exp_scores]
        threshold = self.random.random()
        cumulative = 0.0

        for candidate, probability in zip(filtered, probabilities):
            cumulative += probability

            if threshold <= cumulative:
                return candidate

        return filtered[0]

    def _load_model(self) -> None:
        if not self.weights_path.exists():
            raise FileNotFoundError(f"Pesi modello V2 non trovati: {self.weights_path}")

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest modello V2 non trovato: {self.manifest_path}")

        self.weights = json.loads(self.weights_path.read_text(encoding="utf-8"))
        self.model_manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

        if self.weights.get("versione") != "neural_model_v2_context_weights":
            raise ValueError("File pesi non compatibile con Neural Model V2 Context.")

        self.token_to_id = self.weights["token_to_id"]
        self.id_to_token = self.weights["id_to_token"]
        self.input_embeddings = self.weights["input_embeddings"]
        self.output_embeddings = self.weights["output_embeddings"]
        self.output_bias = self.weights["output_bias"]
        self.vocab_size = int(self.weights["vocab_size"])
        self.vector_dim = int(self.weights["vector_dim"])
        self.context_size = int(self.weights.get("context_size", 6))

        architecture = self.model_manifest.get("architecture", {})

        if architecture.get("uses_multi_token_context") is not True:
            raise ValueError("Il manifest V2 non dichiara contesto multi-token.")

        if len(self.input_embeddings) != self.vocab_size:
            raise ValueError("Input embeddings incoerenti con vocab_size.")

        if len(self.output_embeddings) != self.vocab_size:
            raise ValueError("Output embeddings incoerenti con vocab_size.")

        if len(self.output_bias) != self.vocab_size:
            raise ValueError("Output bias incoerente con vocab_size.")

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text, flags=re.IGNORECASE)

    def _detokenize(self, tokens: List[str]) -> str:
        if not tokens:
            return ""

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

        return text.strip()

    def _join_prompt_and_generation(self, prompt: str, generated_text: str) -> str:
        if not generated_text:
            return prompt

        return f"{prompt} {generated_text}".strip()

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text).strip().split())

    def _token_from_id(self, token_id: int) -> str:
        if token_id < 0 or token_id >= len(self.id_to_token):
            return "<UNK>"

        return self.id_to_token[token_id]

    def _dot(self, left: List[float], right: List[float]) -> float:
        return sum(a * b for a, b in zip(left, right))

    def _sigmoid(self, value: float) -> float:
        if value >= 0:
            z = math.exp(-value)
            return 1 / (1 + z)

        z = math.exp(value)
        return z / (1 + z)


def build_report(manifest: Dict, outputs: List[Dict]) -> str:
    sample_lines = []

    for item in outputs[:8]:
        sample_lines.append(
            f"### Prompt: {item['prompt']}\n\n"
            f"**Generato:** {item['generated_text']}\n\n"
            f"**Testo completo:** {item['full_text']}\n\n"
            f"**Context size:** {item['context_size']}\n"
        )

    sample_block = "\n---\n".join(sample_lines) if sample_lines else "Nessuna inferenza generata."

    return f"""# Report Inference Engine V2 Context

## Stato
{manifest.get("status")}

## Modello usato
- Architettura: {manifest["model"]["architecture"].get("name")}
- Usa contesto multi-token: {manifest["model"]["architecture"].get("uses_multi_token_context")}
- Context size: {manifest["model"]["context_size"]}
- Vocabolario: {manifest["model"]["vocab_size"]}
- Dimensione vettori: {manifest["model"]["vector_dim"]}

## Parametri generazione
- Max nuovi token: {manifest["generation"]["max_new_tokens"]}
- Top K: {manifest["generation"]["top_k"]}
- Temperature: {manifest["generation"]["temperature"]}
- Prompt testati: {manifest["generation"]["prompts_count"]}

## Sintesi
```json
{json.dumps(manifest["summary"], ensure_ascii=False, indent=2)}
```

## Esempi inferenza V2
{sample_block}

## Nota
Questo è il motore di inferenza V2 con contesto multi-token.
Non è ancora un Transformer, ma usa gli ultimi token per predire il token successivo.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inference Engine V2 Context")

    parser.add_argument(
        "--weights",
        default="mini_llm/data/model_v2_context/neural_model_v2_context_weights.json",
        help="Pesi Neural Model V2 Context.",
    )

    parser.add_argument(
        "--model-manifest",
        default="mini_llm/data/model_v2_context/neural_model_v2_context_manifest.json",
        help="Manifest Neural Model V2 Context.",
    )

    parser.add_argument(
        "--output-dir",
        default="mini_llm/data/inference_v2_context",
        help="Cartella output inferenze V2.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/inference_engine_v2_context_report.md",
        help="Report Markdown.",
    )

    parser.add_argument(
        "--prompt",
        action="append",
        default=None,
        help="Prompt da usare. Può essere passato più volte.",
    )

    parser.add_argument("--max-new-tokens", type=int, default=28)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.80)
    parser.add_argument("--seed", type=int, default=42)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    prompts = args.prompt if args.prompt else list(InferenceEngineV2Context.DEFAULT_PROMPTS)

    engine = InferenceEngineV2Context(
        weights_path=(root / args.weights).resolve(),
        manifest_path=(root / args.model_manifest).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        max_new_tokens=args.max_new_tokens,
        top_k=args.top_k,
        temperature=args.temperature,
        seed=args.seed,
    )

    manifest = engine.run(prompts=prompts)

    outputs_path = Path(manifest["output_files"]["outputs"])
    outputs = json.loads(outputs_path.read_text(encoding="utf-8"))

    report_path = (root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(manifest=manifest, outputs=outputs), encoding="utf-8")

    print("OK - Inference Engine V2 Context completato")
    print(f"Output inferenze: {manifest['output_files']['outputs']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {report_path}")
    print(f"Context size: {manifest['model']['context_size']}")
    print(f"Generazioni totali: {manifest['summary']['total_generations']}")
    print(f"Generazioni non vuote: {manifest['summary']['non_empty_generations']}")
    print(f"Media token generati: {manifest['summary']['average_generated_tokens']}")

    for item in outputs[:5]:
        print(f"- {item['prompt']} -> {item['generated_text']}")


if __name__ == "__main__":
    main()
