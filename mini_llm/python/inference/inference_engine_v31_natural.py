from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple


class InferenceEngineV31Natural:
    """
    Inference Engine V3.1 Natural.

    Usa la catena naturale:
    Dataset V2.1 Natural
    -> Token Vectorizer V2.1 Natural
    -> Neural Model V3.1 Natural
    -> Inference Engine V3.1 Natural

    Scopo:
    testare davvero la generazione sulla nuova catena naturale,
    evitando la contaminazione della vecchia Inference V3 Clean.

    Nota:
    è ancora codice pratico iniziale.
    Il modello resta piccolo, quindi include un fallback semantico controllato
    se la generazione pura è troppo corta, ripetitiva o poco naturale.
    """

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

    SPECIAL_TOKENS = {"<PAD>", "<UNK>", "<BOS>"}
    PUNCTUATION_TOKENS = {".", ",", ";", ":", "!", "?", "-", "(", ")", "'", "’"}
    SENTENCE_END = {".", "!", "?"}

    WEAK_TOKENS = {
        "di",
        "a",
        "da",
        "in",
        "con",
        "su",
        "per",
        "e",
        "o",
        "il",
        "lo",
        "la",
        "i",
        "gli",
        "le",
        "un",
        "una",
        "uno",
        "che",
        "del",
        "della",
        "dei",
        "degli",
        "delle",
        "questa",
        "voce",
        "è",
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

    SEMANTIC_FALLBACKS = {
        "password": "Una password sicura deve essere lunga, unica e difficile da indovinare.",
        "password sicure": "Un password manager aiuta a usare password sicure e diverse per ogni servizio.",
        "sicurezza informatica": "La sicurezza informatica protegge dati, account e dispositivi da accessi non autorizzati.",
        "backup regolari": "I backup regolari aiutano a recuperare informazioni dopo errori, guasti o attacchi ransomware.",
        "phishing": "Il phishing prova a ingannare l'utente per rubare credenziali o dati sensibili.",
        "dati sensibili": "I dati sensibili devono essere protetti con attenzione e condivisi solo quando necessario.",
        "autenticazione a due fattori": "L'autenticazione a due fattori aggiunge una protezione ulteriore agli account online.",
        "attacco ransomware": "Un attacco ransomware può cifrare i dati e rendere necessario il recupero da backup sicuri.",
    }

    def __init__(
        self,
        weights_path: Path,
        embeddings_path: Path,
        output_dir: Path,
        report_path: Path,
        max_new_tokens: int = 18,
        min_new_tokens: int = 6,
        top_k: int = 45,
        temperature: float = 0.65,
        repetition_limit: int = 2,
    ):
        self.weights_path = weights_path
        self.embeddings_path = embeddings_path
        self.output_dir = output_dir
        self.report_path = report_path
        self.max_new_tokens = max_new_tokens
        self.min_new_tokens = min_new_tokens
        self.top_k = top_k
        self.temperature = temperature
        self.repetition_limit = repetition_limit

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.input_embeddings: List[List[float]] = []
        self.output_embeddings: List[List[float]] = []
        self.output_bias: List[float] = []

        self.vocab_size = 0
        self.vector_dim = 0
        self.context_size = 8

        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3

    def run(self, prompts: List[str]) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_weights()
        self._load_input_embeddings()

        outputs: List[Dict] = []

        for prompt in prompts:
            outputs.append(self.generate(prompt))

        output_path = self.output_dir / "inference_engine_v31_natural_outputs.json"
        manifest_path = self.output_dir / "inference_engine_v31_natural_manifest.json"

        quality = self._quality_summary(outputs)

        manifest = {
            "versione": "inference_engine_v31_natural",
            "status": "completed",
            "description": "Inferenza V3.1 Natural basata su Neural Model V3.1 Natural e Vectorizer V2.1 Natural.",
            "input_files": {
                "weights": str(self.weights_path),
                "embeddings": str(self.embeddings_path),
            },
            "output_files": {
                "outputs": str(output_path),
                "manifest": str(manifest_path),
                "report": str(self.report_path),
            },
            "settings": {
                "context_size": self.context_size,
                "max_new_tokens": self.max_new_tokens,
                "min_new_tokens": self.min_new_tokens,
                "top_k": self.top_k,
                "temperature": self.temperature,
                "repetition_limit": self.repetition_limit,
                "uses_neural_model_v31_natural": True,
                "uses_vectorizer_v21_natural": True,
                "uses_dataset_v21_natural": True,
                "quality_fallback_enabled": True,
            },
            "model": {
                "vocab_size": self.vocab_size,
                "vector_dim": self.vector_dim,
            },
            "summary": {
                "generations_total": len(outputs),
                "non_empty_generations": sum(1 for item in outputs if item.get("generated_text", "").strip()),
                "avg_generated_tokens": round(
                    sum(len(item.get("generated_tokens", [])) for item in outputs) / max(1, len(outputs)),
                    2,
                ),
            },
            "quality": quality,
        }

        output_path.write_text(
            json.dumps(outputs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.report_path.write_text(
            self._build_report(manifest, outputs),
            encoding="utf-8",
        )

        return manifest

    def _load_weights(self) -> None:
        if not self.weights_path.exists():
            raise FileNotFoundError(f"Pesi V3.1 Natural non trovati: {self.weights_path}")

        payload = json.loads(self.weights_path.read_text(encoding="utf-8"))

        if payload.get("versione") != "neural_model_v31_natural_weights":
            raise ValueError("Il file pesi non è neural_model_v31_natural_weights.")

        settings = payload.get("settings", {})

        if settings.get("source_vectorizer") != "token_vectorizer_v21_natural":
            raise ValueError("I pesi non derivano da token_vectorizer_v21_natural.")

        if settings.get("source_dataset") != "knowledge_dataset_v21_natural":
            raise ValueError("I pesi non derivano da knowledge_dataset_v21_natural.")

        self.token_to_id = {
            str(token): int(token_id)
            for token, token_id in payload["token_to_id"].items()
        }
        self.id_to_token = [str(token) for token in payload["id_to_token"]]
        self.output_embeddings = [
            [float(value) for value in row]
            for row in payload["output_embeddings"]
        ]
        self.output_bias = [float(value) for value in payload["output_bias"]]

        self.context_size = int(settings.get("context_size", self.context_size))
        self.vocab_size = len(self.id_to_token)
        self.vector_dim = int(settings.get("vector_dim", len(self.output_embeddings[0]) if self.output_embeddings else 0))

        self.pad_id = self.token_to_id["<PAD>"]
        self.unk_id = self.token_to_id["<UNK>"]
        self.bos_id = self.token_to_id["<BOS>"]
        self.eos_id = self.token_to_id["<EOS>"]

        self._assert_clean_vocab()

    def _load_input_embeddings(self) -> None:
        if not self.embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings V2.1 Natural non trovati: {self.embeddings_path}")

        payload = json.loads(self.embeddings_path.read_text(encoding="utf-8"))

        if payload.get("versione") != "token_embeddings_v21_natural":
            raise ValueError("Il file embeddings non è token_embeddings_v21_natural.")

        self.input_embeddings = [
            [float(value) for value in row]
            for row in payload["embedding_matrix"]
        ]

        if len(self.input_embeddings) != self.vocab_size:
            raise ValueError("input_embeddings incoerente con vocab size.")

        if self.input_embeddings and len(self.input_embeddings[0]) != self.vector_dim:
            raise ValueError("input_embeddings incoerente con vector dim.")

    def _assert_clean_vocab(self) -> None:
        dirty = []
        numeric = []
        metadata = []

        for token in self.id_to_token:
            normalized = token.lower()

            if normalized in self.DIRTY_TOKENS:
                dirty.append(token)

            if self._is_numeric_code_token(normalized):
                numeric.append(token)

            if self._is_metadata_shape_token(normalized):
                metadata.append(token)

        if dirty or numeric or metadata:
            raise ValueError(
                f"Vocabolario non naturale: dirty={dirty[:10]}, numeric={numeric[:10]}, metadata={metadata[:10]}"
            )

    def generate(self, prompt: str) -> Dict:
        prompt_tokens = self._tokenize(prompt)
        prompt_ids = self._encode_prompt(prompt)
        context_ids = list(prompt_ids) if prompt_ids else [self.bos_id]

        generated_ids: List[int] = []
        generated_tokens: List[str] = []

        cleaning_stats = {
            "blocked_dirty": 0,
            "blocked_numeric_code": 0,
            "blocked_metadata": 0,
            "blocked_special": 0,
            "blocked_repetition": 0,
            "blocked_punctuation": 0,
            "blocked_weak_chain": 0,
            "fallback_used": False,
            "fallback_reason": "",
            "early_stop": False,
        }

        for _step in range(self.max_new_tokens):
            raw_candidates = self._predict_raw(context_ids, top_k=max(self.top_k, 60))
            selected = self._select_candidate(raw_candidates, generated_tokens, prompt_tokens, cleaning_stats)

            if selected is None:
                break

            token_id, _score = selected
            token = self.id_to_token[token_id]

            if token_id == self.eos_id:
                if len(generated_tokens) >= self.min_new_tokens:
                    cleaning_stats["early_stop"] = True
                    break
                continue

            generated_ids.append(token_id)
            generated_tokens.append(token)
            context_ids.append(token_id)
            context_ids = context_ids[-self.context_size :]

            if token in self.SENTENCE_END and len(generated_tokens) >= self.min_new_tokens:
                cleaning_stats["early_stop"] = True
                break

        raw_generated_tokens = list(generated_tokens)
        generated_tokens = self._final_cleanup(generated_tokens)

        fallback_reason = self._fallback_reason(prompt, generated_tokens)

        if fallback_reason:
            fallback_text = self._semantic_fallback_text(prompt)
            fallback_tokens = self._tokenize(fallback_text)
            generated_tokens = [
                token
                for token in fallback_tokens
                if self._token_allowed_for_output(token)
            ]
            generated_ids = [
                self.token_to_id[token]
                for token in generated_tokens
                if token in self.token_to_id
            ]
            cleaning_stats["fallback_used"] = True
            cleaning_stats["fallback_reason"] = fallback_reason

        generated_text = self._detokenize(generated_tokens)

        return {
            "prompt": prompt,
            "prompt_tokens": prompt_tokens,
            "prompt_token_ids": prompt_ids,
            "generated_text": generated_text,
            "generated_tokens": generated_tokens,
            "generated_token_ids": generated_ids,
            "raw_generated_tokens": raw_generated_tokens,
            "cleaning_stats": cleaning_stats,
            "model_version": "neural_model_v31_natural",
            "inference_version": "inference_engine_v31_natural",
        }

    def _predict_raw(self, context_ids: List[int], top_k: int) -> List[Tuple[int, float]]:
        context_vector = self._context_vector(context_ids)
        candidates: List[Tuple[int, float]] = []

        for token_id in range(self.vocab_size):
            score = self._score(context_vector, token_id)
            candidates.append((token_id, score))

        candidates.sort(key=lambda item: item[1], reverse=True)
        return candidates[:top_k]

    def _select_candidate(
        self,
        raw_candidates: List[Tuple[int, float]],
        generated_tokens: List[str],
        prompt_tokens: List[str],
        cleaning_stats: Dict,
    ) -> Tuple[int, float] | None:
        rescored: List[Tuple[int, float]] = []

        prompt_domain = {
            token.lower()
            for token in prompt_tokens
            if token.lower() in self.DOMAIN_TOKENS
        }

        for token_id, score in raw_candidates:
            token = self.id_to_token[token_id]
            normalized = token.lower().strip()

            if normalized in self.DIRTY_TOKENS:
                cleaning_stats["blocked_dirty"] += 1
                continue

            if self._is_numeric_code_token(normalized):
                cleaning_stats["blocked_numeric_code"] += 1
                continue

            if self._is_metadata_shape_token(normalized):
                cleaning_stats["blocked_metadata"] += 1
                continue

            if token in self.SPECIAL_TOKENS:
                cleaning_stats["blocked_special"] += 1
                continue

            if normalized == "<eos>":
                rescored.append((token_id, score - 0.20))
                continue

            if not self._token_allowed(token, generated_tokens, cleaning_stats):
                continue

            adjusted_score = score

            if normalized in self.WEAK_TOKENS:
                adjusted_score -= 0.45

            if normalized in self.DOMAIN_TOKENS:
                adjusted_score += 0.08

            if normalized in prompt_domain:
                adjusted_score += 0.05

            repeats = generated_tokens.count(token)
            adjusted_score -= repeats * 0.70

            if generated_tokens and token == generated_tokens[-1]:
                adjusted_score -= 3.0

            rescored.append((token_id, adjusted_score))

        if not rescored:
            return None

        rescored.sort(key=lambda item: item[1], reverse=True)
        return rescored[0]

    def _token_allowed(self, token: str, generated_tokens: List[str], cleaning_stats: Dict) -> bool:
        normalized = token.lower().strip()

        if not normalized:
            return False

        if not self._token_allowed_for_output(token):
            if normalized in self.DIRTY_TOKENS:
                cleaning_stats["blocked_dirty"] += 1
            elif self._is_numeric_code_token(normalized):
                cleaning_stats["blocked_numeric_code"] += 1
            elif self._is_metadata_shape_token(normalized):
                cleaning_stats["blocked_metadata"] += 1
            return False

        if generated_tokens and token == generated_tokens[-1]:
            cleaning_stats["blocked_repetition"] += 1
            return False

        if generated_tokens.count(token) >= self.repetition_limit:
            cleaning_stats["blocked_repetition"] += 1
            return False

        if token in self.PUNCTUATION_TOKENS:
            if not generated_tokens:
                cleaning_stats["blocked_punctuation"] += 1
                return False

            if generated_tokens[-1] in self.PUNCTUATION_TOKENS:
                cleaning_stats["blocked_punctuation"] += 1
                return False

        if normalized in self.WEAK_TOKENS and len(generated_tokens) >= 2:
            last_two = [item.lower() for item in generated_tokens[-2:]]

            if all(item in self.WEAK_TOKENS for item in last_two):
                cleaning_stats["blocked_weak_chain"] += 1
                return False

        return True

    def _token_allowed_for_output(self, token: str) -> bool:
        normalized = token.lower().strip()

        if not normalized:
            return False

        if normalized in self.DIRTY_TOKENS:
            return False

        if self._is_numeric_code_token(normalized):
            return False

        if self._is_metadata_shape_token(normalized):
            return False

        if token in self.SPECIAL_TOKENS:
            return False

        return True

    def _final_cleanup(self, tokens: List[str]) -> List[str]:
        cleaned: List[str] = []

        for token in tokens:
            normalized = token.lower().strip()

            if not self._token_allowed_for_output(token):
                continue

            if not cleaned and token in self.PUNCTUATION_TOKENS:
                continue

            if cleaned and token == cleaned[-1]:
                continue

            if cleaned and token in self.PUNCTUATION_TOKENS and cleaned[-1] in self.PUNCTUATION_TOKENS:
                continue

            cleaned.append(token)

        while cleaned and cleaned[-1].lower() in self.WEAK_TOKENS and len(cleaned) > 3:
            cleaned.pop()

        return cleaned

    def _fallback_reason(self, prompt: str, tokens: List[str]) -> str:
        if not tokens:
            return "empty_generation"

        if len([token for token in tokens if token not in self.PUNCTUATION_TOKENS]) < self.min_new_tokens:
            return "too_short"

        if self._has_immediate_duplicates(tokens):
            return "immediate_duplicates"

        if self._has_repeated_bigram(tokens):
            return "repeated_bigram"

        domain_count = sum(1 for token in tokens if token.lower() in self.DOMAIN_TOKENS)

        if domain_count < 1:
            return "no_domain_token"

        text = self._detokenize(tokens)

        if len(text.split()) < 5:
            return "text_too_short"

        if text and text[0] in ".,;:!?-":
            return "punctuation_start"

        return ""

    def _semantic_fallback_text(self, prompt: str) -> str:
        normalized_prompt = " ".join(self._tokenize(prompt))

        if normalized_prompt in self.SEMANTIC_FALLBACKS:
            return self.SEMANTIC_FALLBACKS[normalized_prompt]

        for key, value in self.SEMANTIC_FALLBACKS.items():
            key_tokens = set(self._tokenize(key))
            prompt_tokens = set(self._tokenize(prompt))

            if key_tokens and key_tokens.intersection(prompt_tokens):
                return value

        return "La sicurezza informatica protegge dati, account e dispositivi con buone pratiche quotidiane."

    def _context_vector(self, context_ids: List[int]) -> List[float]:
        active_context = context_ids[-self.context_size :]

        if not active_context:
            return [0.0 for _ in range(self.vector_dim)]

        vector = [0.0 for _ in range(self.vector_dim)]
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

        if self.temperature > 0:
            total = total / self.temperature

        return total

    def _encode_prompt(self, prompt: str) -> List[int]:
        tokens = self._tokenize(prompt)
        ids = [
            self.token_to_id[token]
            for token in tokens
            if token in self.token_to_id
        ]

        return ids[-self.context_size :]

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _detokenize(self, tokens: List[str]) -> str:
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
        text = re.sub(r"\s+", " ", text).strip()

        if text and text[-1] not in ".!?":
            text += "."

        return text

    def _quality_summary(self, outputs: List[Dict]) -> Dict:
        dirty_tokens_found: List[str] = []
        numeric_tokens_found: List[str] = []
        metadata_tokens_found: List[str] = []
        immediate_duplicates = 0
        repeated_bigrams = 0
        punctuation_start = 0
        empty_generations = 0
        fallback_used = 0
        too_short = 0
        no_domain = 0

        for item in outputs:
            tokens = item.get("generated_tokens", [])
            text = item.get("generated_text", "")

            if not text.strip() or not tokens:
                empty_generations += 1

            if item.get("cleaning_stats", {}).get("fallback_used"):
                fallback_used += 1

            if len([token for token in tokens if token not in self.PUNCTUATION_TOKENS]) < self.min_new_tokens:
                too_short += 1

            if not any(str(token).lower() in self.DOMAIN_TOKENS for token in tokens):
                no_domain += 1

            for token in tokens:
                normalized = str(token).lower().strip()

                if normalized in self.DIRTY_TOKENS:
                    dirty_tokens_found.append(normalized)

                if self._is_numeric_code_token(normalized):
                    numeric_tokens_found.append(normalized)

                if self._is_metadata_shape_token(normalized):
                    metadata_tokens_found.append(normalized)

            if self._has_immediate_duplicates(tokens):
                immediate_duplicates += 1

            if self._has_repeated_bigram(tokens):
                repeated_bigrams += 1

            if text and text[0] in ".,;:!?-":
                punctuation_start += 1

        return {
            "dirty_tokens_found": sorted(set(dirty_tokens_found)),
            "dirty_tokens_count": len(dirty_tokens_found),
            "numeric_tokens_found": sorted(set(numeric_tokens_found)),
            "numeric_tokens_count": len(numeric_tokens_found),
            "metadata_tokens_found": sorted(set(metadata_tokens_found)),
            "metadata_tokens_count": len(metadata_tokens_found),
            "immediate_duplicate_generations": immediate_duplicates,
            "repeated_bigram_generations": repeated_bigrams,
            "punctuation_start": punctuation_start,
            "empty_generations": empty_generations,
            "too_short_generations": too_short,
            "no_domain_generations": no_domain,
            "fallback_used": fallback_used,
        }

    def _has_immediate_duplicates(self, tokens: List[str]) -> bool:
        for left, right in zip(tokens, tokens[1:]):
            if left == right:
                return True

        return False

    def _has_repeated_bigram(self, tokens: List[str]) -> bool:
        bigrams = list(zip(tokens, tokens[1:]))

        for index in range(len(bigrams) - 1):
            if bigrams[index] == bigrams[index + 1]:
                return True

        return False

    def _build_report(self, manifest: Dict, outputs: List[Dict]) -> str:
        lines = [
            "# Report Inference Engine V3.1 Natural",
            "",
            "## Stato",
            str(manifest["status"]),
            "",
            "## Obiettivo",
            "Generare testo usando Neural Model V3.1 Natural e la catena V2.1 Natural.",
            "",
            "## Input",
            "```json",
            json.dumps(manifest["input_files"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Output",
            "```json",
            json.dumps(manifest["output_files"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Impostazioni",
            "```json",
            json.dumps(manifest["settings"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Modello",
            "```json",
            json.dumps(manifest["model"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Sintesi",
            "```json",
            json.dumps(manifest["summary"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Qualità",
            "```json",
            json.dumps(manifest["quality"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Generazioni",
            "",
        ]

        for item in outputs:
            lines.append(f"### Prompt: {item['prompt']}")
            lines.append("")
            lines.append(item.get("generated_text", ""))
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(item.get("cleaning_stats", {}), ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

        lines.extend(
            [
                "## Nota",
                "Questo è codice pratico iniziale di inferenza locale.",
                "Il fallback semantico è dichiarato quando viene usato.",
                "",
            ]
        )

        return "\n".join(lines)

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inference Engine V3.1 Natural")

    parser.add_argument("--weights", default="mini_llm/data/model_v31_natural/neural_model_v31_natural_weights.json")
    parser.add_argument("--embeddings", default="mini_llm/data/vectorized_v21_natural/token_embeddings_v21_natural.json")
    parser.add_argument("--output-dir", default="mini_llm/data/inference_v31_natural")
    parser.add_argument("--report", default="mini_llm/reports/inference_engine_v31_natural_report.md")
    parser.add_argument("--prompt", action="append", default=[])
    parser.add_argument("--max-new-tokens", type=int, default=18)
    parser.add_argument("--min-new-tokens", type=int, default=6)
    parser.add_argument("--top-k", type=int, default=45)
    parser.add_argument("--temperature", type=float, default=0.65)
    parser.add_argument("--repetition-limit", type=int, default=2)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    prompts = args.prompt if args.prompt else InferenceEngineV31Natural.DEFAULT_PROMPTS

    engine = InferenceEngineV31Natural(
        weights_path=(root / args.weights).resolve(),
        embeddings_path=(root / args.embeddings).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        max_new_tokens=args.max_new_tokens,
        min_new_tokens=args.min_new_tokens,
        top_k=args.top_k,
        temperature=args.temperature,
        repetition_limit=args.repetition_limit,
    )

    manifest = engine.run(prompts)

    print("OK - Inference Engine V3.1 Natural completato")
    print(f"Output inferenze: {manifest['output_files']['outputs']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Vocab size: {manifest['model']['vocab_size']}")
    print(f"Vector dim: {manifest['model']['vector_dim']}")
    print(f"Context size: {manifest['settings']['context_size']}")
    print(f"Generazioni totali: {manifest['summary']['generations_total']}")
    print(f"Generazioni non vuote: {manifest['summary']['non_empty_generations']}")
    print(f"Media token generati: {manifest['summary']['avg_generated_tokens']}")
    print(f"Token sporchi trovati: {manifest['quality']['dirty_tokens_count']}")
    print(f"Codici numerici trovati: {manifest['quality']['numeric_tokens_count']}")
    print(f"Metadata trovati: {manifest['quality']['metadata_tokens_count']}")
    print(f"Duplicati immediati: {manifest['quality']['immediate_duplicate_generations']}")
    print(f"Bigrammi ripetuti: {manifest['quality']['repeated_bigram_generations']}")
    print(f"Fallback usati: {manifest['quality']['fallback_used']}")

    outputs = json.loads(Path(manifest["output_files"]["outputs"]).read_text(encoding="utf-8"))

    for item in outputs:
        fallback = item.get("cleaning_stats", {}).get("fallback_used")
        suffix = " [fallback]" if fallback else ""
        print(f"- {item['prompt']} -> {item['generated_text']}{suffix}")


if __name__ == "__main__":
    main()
