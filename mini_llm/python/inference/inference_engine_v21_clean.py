from __future__ import annotations

import argparse
import json
import math
import random
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class InferenceEngineV21Clean:
    """
    Inference Engine V2.1 Clean.

    Usa i pesi del Neural Model V2 Context, ma aggiunge un livello di pulizia
    sopra la generazione:

    - filtro token tecnici del dataset: #, input, output, risposta, istruzione;
    - filtro parole di servizio contaminate: pulite, complete, trasforma, riscrivi;
    - blocco ripetizioni immediate;
    - blocco ripetizioni eccessive nello stesso output;
    - blocco punteggiatura come primo token;
    - stop anticipato su frase breve conclusa;
    - max token più corto rispetto a V2;
    - fallback pulito obbligatorio se i filtri eliminano tutti i candidati;
    - report e manifest dedicati.

    Nota:
    questo non cambia il training e non falsifica il modello.
    Pulisce il decoding, cioè il modo in cui scegliamo i token dai pesi V2.
    """

    BLOCKED_GENERATION_TOKENS = {"<PAD>", "<BOS>", "<UNK>"}
    STOP_TOKENS = {"<EOS>"}

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

    SOFT_DIRTY_TOKENS = {
        "riassunto",
        "frase",
        "utile",
        "chiara",
        "chiare",
    }

    WEAK_TOKENS = {
        "un",
        "una",
        "il",
        "lo",
        "la",
        "gli",
        "le",
        "di",
        "a",
        "da",
        "per",
        "con",
        "e",
        "o",
        "in",
        "su",
        "tra",
        "fra",
        "che",
        "l",
    }

    PUNCTUATION_TOKENS = {".", ",", ";", ":", "!", "?", "-", "(", ")", "’", "'"}

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

    SAFE_FALLBACK_BY_KEYWORD = {
        "password": ["manager", "password", "lunghe", "account", "sicure"],
        "sicure": ["password", "manager", "account", "servizio"],
        "sicurezza": ["sicurezza", "informatica", "dati", "account", "sistemi"],
        "informatica": ["sicurezza", "dati", "dispositivi", "account", "sistemi"],
        "backup": ["backup", "dati", "ransomware", "informazioni"],
        "regolari": ["backup", "dati", "informazioni", "ransomware"],
        "phishing": ["phishing", "dati", "sensibili", "credenziali"],
        "dati": ["dati", "sensibili", "account", "protezione"],
        "sensibili": ["dati", "sensibili", "account", "attenzione"],
        "autenticazione": ["autenticazione", "due", "fattori", "password"],
        "fattori": ["autenticazione", "due", "fattori", "password"],
        "ransomware": ["ransomware", "dati", "backup", "malware"],
        "attacco": ["ransomware", "malware", "dati", "backup"],
    }

    GLOBAL_SAFE_FALLBACK = [
        "sicurezza",
        "dati",
        "account",
        "password",
        "backup",
        "ransomware",
        "phishing",
        "malware",
    ]

    def __init__(
        self,
        weights_path: Path,
        manifest_path: Path,
        output_dir: Path,
        max_new_tokens: int = 16,
        top_k: int = 40,
        temperature: float = 0.50,
        min_new_tokens: int = 3,
        seed: int = 42,
    ):
        self.weights_path = weights_path
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        self.max_new_tokens = max_new_tokens
        self.top_k = top_k
        self.temperature = max(0.05, temperature)
        self.min_new_tokens = min_new_tokens
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

        outputs = [self.generate(prompt=prompt) for prompt in prompts]

        outputs_path = self.output_dir / "inference_engine_v21_clean_outputs.json"
        manifest_path = self.output_dir / "inference_engine_v21_clean_manifest.json"

        outputs_path.write_text(
            json.dumps(outputs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        quality_summary = self._build_quality_summary(outputs)

        manifest = {
            "versione": "inference_engine_v21_clean",
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
                "min_new_tokens": self.min_new_tokens,
                "top_k": self.top_k,
                "temperature": self.temperature,
                "seed": self.seed,
                "prompts_count": len(prompts),
                "uses_context_window": True,
                "uses_clean_decoding": True,
            },
            "filters": {
                "blocked_generation_tokens": sorted(self.BLOCKED_GENERATION_TOKENS),
                "dirty_tokens": sorted(self.DIRTY_TOKENS),
                "soft_dirty_tokens": sorted(self.SOFT_DIRTY_TOKENS),
                "punctuation_tokens": sorted(self.PUNCTUATION_TOKENS),
                "rules": [
                    "no dirty tokens",
                    "no immediate duplicate tokens",
                    "no punctuation as first generated token",
                    "no excessive punctuation",
                    "early stop after useful sentence end",
                    "shorter generation than raw V2",
                ],
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
                "average_removed_candidates": round(
                    sum(item.get("cleaning_stats", {}).get("removed_candidates", 0) for item in outputs) / len(outputs),
                    2,
                ) if outputs else 0,
                "quality": quality_summary,
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

        cleaning_stats = {
            "removed_candidates": 0,
            "blocked_dirty": 0,
            "blocked_repetition": 0,
            "blocked_punctuation": 0,
            "blocked_weak_sequence": 0,
            "early_stop": False,
            "fallback_used": False,
            "semantic_fallback_used": False,
        }

        for step in range(1, self.max_new_tokens + 1):
            raw_candidates = self.predict_next_raw(context_ids=context_ids, top_k=max(self.top_k, 60))
            selected = self._select_clean_candidate(
                raw_candidates=raw_candidates,
                generated_tokens=generated_tokens,
                step=step,
                cleaning_stats=cleaning_stats,
            )

            context_tokens = [self._token_from_id(token_id) for token_id in context_ids]

            if selected is None:
                step_debug.append(
                    {
                        "step": step,
                        "context_tokens": context_tokens,
                        "context_ids": list(context_ids),
                        "selected_token": None,
                        "reason": "no_clean_candidate",
                        "top_candidates": raw_candidates[: min(8, len(raw_candidates))],
                    }
                )
                break

            selected_token = selected["token"]
            selected_id = selected["token_id"]

            step_debug.append(
                {
                    "step": step,
                    "context_tokens": context_tokens,
                    "context_ids": list(context_ids),
                    "selected_token": selected_token,
                    "selected_id": selected_id,
                    "selected_score": selected["score"],
                    "top_candidates": raw_candidates[: min(8, len(raw_candidates))],
                    "clean_candidate": True,
                }
            )

            if selected_token in self.STOP_TOKENS:
                cleaning_stats["early_stop"] = True
                break

            generated_token_ids.append(selected_id)
            generated_tokens.append(selected_token)

            context_ids.append(selected_id)
            context_ids = context_ids[-self.context_size:]

            if self._should_stop_early(generated_tokens):
                cleaning_stats["early_stop"] = True
                break

        generated_tokens = self._final_token_cleanup(generated_tokens)

        if not generated_tokens:
            fallback_tokens = self._safe_non_empty_fallback(prompt_tokens=prompt_tokens)
            generated_tokens = fallback_tokens
            generated_token_ids = [
                self.token_to_id[token]
                for token in fallback_tokens
                if token in self.token_to_id
            ]
            cleaning_stats["semantic_fallback_used"] = True
            cleaning_stats["fallback_used"] = True

        generated_text = self._detokenize(generated_tokens)

        return {
            "prompt": clean_prompt,
            "prompt_tokens": prompt_tokens,
            "prompt_token_ids": prompt_token_ids,
            "context_size": self.context_size,
            "generated_tokens": generated_tokens,
            "generated_token_ids": generated_token_ids[: len(generated_tokens)],
            "generated_text": generated_text,
            "full_text": self._join_prompt_and_generation(clean_prompt, generated_text),
            "cleaning_stats": cleaning_stats,
            "steps": step_debug,
        }

    def predict_next_raw(self, context_ids: List[int], top_k: int = 20) -> List[Dict]:
        clean_context_ids = [
            token_id
            for token_id in context_ids[-self.context_size:]
            if 0 <= token_id < self.vocab_size
        ]

        if not clean_context_ids:
            clean_context_ids = [self.token_to_id.get("<UNK>", 1)]

        context_vector, _weights = self._build_context_vector(clean_context_ids)
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

    def _select_clean_candidate(
        self,
        raw_candidates: List[Dict],
        generated_tokens: List[str],
        step: int,
        cleaning_stats: Dict,
    ) -> Optional[Dict]:
        clean_candidates: List[Dict] = []

        for candidate in raw_candidates:
            token = str(candidate["token"]).strip()

            if self._is_blocked_candidate(token, generated_tokens, step, cleaning_stats):
                cleaning_stats["removed_candidates"] += 1
                continue

            adjusted = dict(candidate)
            adjusted["score"] = self._adjust_score_for_quality(candidate["score"], token, generated_tokens)
            clean_candidates.append(adjusted)

        if not clean_candidates:
            fallback = self._fallback_candidate(raw_candidates, generated_tokens, step, cleaning_stats)

            if fallback:
                cleaning_stats["fallback_used"] = True
                return fallback

            return None

        clean_candidates.sort(reverse=True, key=lambda item: item["score"])

        # Deterministico e più pulito: nelle prime posizioni scegli quasi sempre il migliore.
        if step <= 2:
            return clean_candidates[0]

        top = clean_candidates[: min(6, len(clean_candidates))]
        scores = [candidate["score"] for candidate in top]
        max_score = max(scores)
        exp_scores = [math.exp((score - max_score) / self.temperature) for score in scores]
        total = sum(exp_scores)

        if total <= 0:
            return top[0]

        threshold = self.random.random()
        cumulative = 0.0

        for candidate, exp_score in zip(top, exp_scores):
            cumulative += exp_score / total

            if threshold <= cumulative:
                return candidate

        return top[0]

    def _is_blocked_candidate(
        self,
        token: str,
        generated_tokens: List[str],
        step: int,
        cleaning_stats: Dict,
    ) -> bool:
        normalized = token.lower().strip()

        if normalized in self.BLOCKED_GENERATION_TOKENS:
            cleaning_stats["blocked_dirty"] += 1
            return True

        if normalized in self.DIRTY_TOKENS:
            cleaning_stats["blocked_dirty"] += 1
            return True

        # I token soft-dirty non vengono bloccati qui:
        # vengono penalizzati nel punteggio, così non causano output vuoti.

        if step == 1 and normalized in self.PUNCTUATION_TOKENS:
            cleaning_stats["blocked_punctuation"] += 1
            return True

        if generated_tokens:
            previous = generated_tokens[-1].lower()

            if normalized == previous:
                cleaning_stats["blocked_repetition"] += 1
                return True

            if normalized in self.PUNCTUATION_TOKENS and previous in self.PUNCTUATION_TOKENS:
                cleaning_stats["blocked_punctuation"] += 1
                return True

        if generated_tokens.count(normalized) >= 2:
            cleaning_stats["blocked_repetition"] += 1
            return True

        if len(generated_tokens) >= 2:
            last_two = [item.lower() for item in generated_tokens[-2:]]

            if normalized in self.WEAK_TOKENS and all(item in self.WEAK_TOKENS for item in last_two):
                cleaning_stats["blocked_weak_sequence"] += 1
                return True

        if len(generated_tokens) < self.min_new_tokens and normalized in {".", "!", "?", ";"}:
            cleaning_stats["blocked_punctuation"] += 1
            return True

        return False

    def _adjust_score_for_quality(self, score: float, token: str, generated_tokens: List[str]) -> float:
        normalized = token.lower().strip()
        adjusted = float(score)

        if normalized in self.SOFT_DIRTY_TOKENS:
            adjusted -= 1.2

        if normalized in self.WEAK_TOKENS:
            adjusted -= 0.35

        if normalized in self.PUNCTUATION_TOKENS:
            adjusted -= 0.25

        if generated_tokens and normalized in [item.lower() for item in generated_tokens[-4:]]:
            adjusted -= 0.9

        return adjusted

    def _fallback_candidate(
        self,
        raw_candidates: List[Dict],
        generated_tokens: List[str],
        step: int,
        cleaning_stats: Dict,
    ) -> Optional[Dict]:
        for candidate in raw_candidates:
            token = str(candidate["token"]).lower().strip()

            if token in self.BLOCKED_GENERATION_TOKENS:
                continue

            if token in self.DIRTY_TOKENS:
                continue

            if step == 1 and token in self.PUNCTUATION_TOKENS:
                continue

            if generated_tokens and token == generated_tokens[-1].lower():
                continue

            return candidate

        return None

    def _should_stop_early(self, generated_tokens: List[str]) -> bool:
        if len(generated_tokens) < self.min_new_tokens:
            return False

        last = generated_tokens[-1]

        if last in {".", "!", "?"}:
            return True

        if len(generated_tokens) >= self.max_new_tokens:
            return True

        return False

    def _final_token_cleanup(self, tokens: List[str]) -> List[str]:
        cleaned: List[str] = []

        for token in tokens:
            normalized = token.lower().strip()

            if normalized in self.DIRTY_TOKENS:
                continue

            if normalized in self.BLOCKED_GENERATION_TOKENS:
                continue

            if not cleaned and normalized in self.PUNCTUATION_TOKENS:
                continue

            if cleaned and normalized == cleaned[-1].lower():
                continue

            if cleaned and normalized in self.PUNCTUATION_TOKENS and cleaned[-1] in self.PUNCTUATION_TOKENS:
                continue

            cleaned.append(token)

        # Rimuove punteggiatura finale isolata ripetuta o inutile.
        while cleaned and cleaned[-1] in {",", ";", ":", "-", "’", "'"}:
            cleaned.pop()

        return cleaned

    def _safe_non_empty_fallback(self, prompt_tokens: List[str]) -> List[str]:
        """
        Fallback finale di sicurezza.

        Entra solo quando il decoding pulito non produce nessun token.
        Usa solo token presenti nel vocabolario e non presenti nella lista sporca.
        Non inventa nuovi token fuori vocabolario.
        """
        prompt_norm = [str(token).lower().strip() for token in prompt_tokens]
        candidates: List[str] = []

        for prompt_token in prompt_norm:
            candidates.extend(self.SAFE_FALLBACK_BY_KEYWORD.get(prompt_token, []))

        candidates.extend(self.GLOBAL_SAFE_FALLBACK)

        clean_tokens: List[str] = []

        for token in candidates:
            normalized = token.lower().strip()

            if normalized in self.DIRTY_TOKENS:
                continue

            if normalized in self.BLOCKED_GENERATION_TOKENS:
                continue

            if normalized in self.PUNCTUATION_TOKENS:
                continue

            if normalized not in self.token_to_id:
                continue

            if clean_tokens and normalized == clean_tokens[-1]:
                continue

            if normalized in clean_tokens:
                continue

            clean_tokens.append(normalized)

            if len(clean_tokens) >= 4:
                break

        if clean_tokens:
            return clean_tokens

        # Ultima protezione: cerca nel vocabolario i primi token puliti disponibili.
        for token in self.id_to_token:
            normalized = str(token).lower().strip()

            if normalized in self.DIRTY_TOKENS:
                continue

            if normalized in self.BLOCKED_GENERATION_TOKENS:
                continue

            if normalized in self.PUNCTUATION_TOKENS:
                continue

            if len(normalized) <= 1:
                continue

            if normalized in clean_tokens:
                continue

            clean_tokens.append(normalized)

            if len(clean_tokens) >= 3:
                break

        return clean_tokens

    def _build_quality_summary(self, outputs: List[Dict]) -> Dict:
        dirty_count = 0
        duplicate_count = 0
        punctuation_start_count = 0

        for item in outputs:
            tokens = [str(token).lower() for token in item.get("generated_tokens", [])]

            dirty_count += sum(1 for token in tokens if token in self.DIRTY_TOKENS)

            for left, right in zip(tokens, tokens[1:]):
                if left == right:
                    duplicate_count += 1

            if tokens and tokens[0] in self.PUNCTUATION_TOKENS:
                punctuation_start_count += 1

        return {
            "dirty_tokens_found": dirty_count,
            "immediate_duplicates_found": duplicate_count,
            "punctuation_start_found": punctuation_start_count,
        }

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

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"([,.;:!?])\1+", r"\1", text)

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
        stats = item.get("cleaning_stats", {})
        sample_lines.append(
            f"### Prompt: {item['prompt']}\n\n"
            f"**Generato pulito:** {item['generated_text']}\n\n"
            f"**Testo completo:** {item['full_text']}\n\n"
            f"**Context size:** {item['context_size']}\n\n"
            f"**Filtri applicati:** removed={stats.get('removed_candidates', 0)}, "
            f"dirty={stats.get('blocked_dirty', 0)}, "
            f"repeat={stats.get('blocked_repetition', 0)}, "
            f"punct={stats.get('blocked_punctuation', 0)}, "
            f"semantic_fallback={stats.get('semantic_fallback_used', False)}\n"
        )

    sample_block = "\n---\n".join(sample_lines) if sample_lines else "Nessuna inferenza generata."

    return f"""# Report Inference Engine V2.1 Clean

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
- Min nuovi token: {manifest["generation"]["min_new_tokens"]}
- Top K: {manifest["generation"]["top_k"]}
- Temperature: {manifest["generation"]["temperature"]}
- Clean decoding: {manifest["generation"]["uses_clean_decoding"]}

## Sintesi
```json
{json.dumps(manifest["summary"], ensure_ascii=False, indent=2)}
```

## Filtri attivi
```json
{json.dumps(manifest["filters"], ensure_ascii=False, indent=2)}
```

## Esempi inferenza pulita
{sample_block}

## Nota
Questo blocco non riaddestra il modello.
Migliora il decoding dei pesi V2 con filtri qualità e stop anticipato.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inference Engine V2.1 Clean")

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
        default="mini_llm/data/inference_v21_clean",
        help="Cartella output inferenze V2.1 Clean.",
    )

    parser.add_argument(
        "--report",
        default="mini_llm/reports/inference_engine_v21_clean_report.md",
        help="Report Markdown.",
    )

    parser.add_argument(
        "--prompt",
        action="append",
        default=None,
        help="Prompt da usare. Può essere passato più volte.",
    )

    parser.add_argument("--max-new-tokens", type=int, default=16)
    parser.add_argument("--min-new-tokens", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=42)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    prompts = args.prompt if args.prompt else list(InferenceEngineV21Clean.DEFAULT_PROMPTS)

    engine = InferenceEngineV21Clean(
        weights_path=(root / args.weights).resolve(),
        manifest_path=(root / args.model_manifest).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        max_new_tokens=args.max_new_tokens,
        min_new_tokens=args.min_new_tokens,
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

    print("OK - Inference Engine V2.1 Clean completato")
    print(f"Output inferenze: {manifest['output_files']['outputs']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {report_path}")
    print(f"Context size: {manifest['model']['context_size']}")
    print(f"Generazioni totali: {manifest['summary']['total_generations']}")
    print(f"Generazioni non vuote: {manifest['summary']['non_empty_generations']}")
    print(f"Media token generati: {manifest['summary']['average_generated_tokens']}")
    print(f"Token sporchi trovati: {manifest['summary']['quality']['dirty_tokens_found']}")
    print(f"Duplicati immediati trovati: {manifest['summary']['quality']['immediate_duplicates_found']}")

    for item in outputs[:5]:
        print(f"- {item['prompt']} -> {item['generated_text']}")


if __name__ == "__main__":
    main()
