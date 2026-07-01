from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class InferenceRawDiagnosticsV1:
    """
    Inference Raw Diagnostics V1.

    Regola fondamentale:
    - nessun fallback;
    - nessuna frase hardcoded;
    - nessun recupero dal sentence bank;
    - nessuna ancora fraseologica;
    - nessuna sostituzione del testo generato.

    Questo script serve a vedere cosa genera davvero il modello.
    Se genera male, il report deve mostrarlo.
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
        "#", "input", "output", "instruction", "istruzione", "risposta", "domanda",
        "question", "answer", "completion", "prompt", "trasforma", "riscrivi",
        "collegate", "collegata", "collegato", "micro", "forma", "area",
        "operativa", "operative", "pulite", "pulita", "complete", "completa",
        "analizzato", "richiesta", "richiesto", "source_task", "source_record",
        "record", "json", "crea", "creare", "genera", "generare", "training",
        "training_originale", "knowledge_engine", "knowledge_engine_v14",
        "relazione_operativa", "relazioni_operative", "micro_informazioni",
        "frasi_rilevanti", "aree_operative", "dataset", "builder", "vectorizer",
        "manifest", "source", "clean", "clean_id", "source_split", "source_clean_id",
        "alex", "alessandro", "barbarossa", "breve", "sintesi", "template",
    }

    WEAK_TOKENS = {
        "di", "a", "da", "in", "con", "su", "per", "e", "o", "il", "lo", "la",
        "i", "gli", "le", "un", "una", "uno", "che", "del", "della", "dei",
        "degli", "delle", "questa", "voce", "è", "l", "'", "’",
    }

    DOMAIN_TOKENS = {
        "password", "manager", "sicurezza", "informatica", "backup", "ransomware",
        "phishing", "malware", "dati", "sensibili", "autenticazione", "fattori",
        "account", "codici", "temporanei", "aggiornamenti", "software", "privilegio",
        "amministrativi", "protezione", "credenziali", "dispositivi", "vulnerabilità",
        "sistemi", "accesso", "informazioni", "attacco", "utente", "guasto", "furto",
    }

    PUNCTUATION = {".", ",", ";", ":", "!", "?", "-", "(", ")", "'", "’"}

    def __init__(
        self,
        weights_path: Path,
        embeddings_path: Path,
        output_dir: Path,
        report_path: Path,
        max_new_tokens: int,
        top_k_trace: int,
        temperature: float,
    ):
        self.weights_path = weights_path
        self.embeddings_path = embeddings_path
        self.output_dir = output_dir
        self.report_path = report_path
        self.max_new_tokens = max_new_tokens
        self.top_k_trace = top_k_trace
        self.temperature = temperature

        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: List[str] = []
        self.input_embeddings: List[List[float]] = []
        self.output_embeddings: List[List[float]] = []
        self.output_bias: List[float] = []

        self.context_size = 8
        self.vocab_size = 0
        self.vector_dim = 0

        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3

    def run(self, prompts: List[str]) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_weights()
        self._load_embeddings()

        outputs = [self.generate_raw(prompt) for prompt in prompts]

        outputs_path = self.output_dir / "inference_raw_diagnostics_v1_outputs.json"
        manifest_path = self.output_dir / "inference_raw_diagnostics_v1_manifest.json"

        global_diagnostics = self._global_diagnostics(outputs)

        manifest = {
            "versione": "inference_raw_diagnostics_v1",
            "status": "diagnosed",
            "description": "Diagnostica raw del modello: nessun fallback, nessuna frase pronta, nessun recupero da sentence bank.",
            "input_files": {
                "weights": str(self.weights_path),
                "embeddings": str(self.embeddings_path),
            },
            "output_files": {
                "outputs": str(outputs_path),
                "manifest": str(manifest_path),
                "report": str(self.report_path),
            },
            "settings": {
                "generation_mode": "raw_model_only",
                "fallback_enabled": False,
                "hardcoded_sentences_enabled": False,
                "sentence_bank_enabled": False,
                "anchor_retrieval_enabled": False,
                "filters_enabled": False,
                "max_new_tokens": self.max_new_tokens,
                "top_k_trace": self.top_k_trace,
                "temperature": self.temperature,
            },
            "model": {
                "source_weights_version": "neural_model_v31_natural_weights",
                "vocab_size": self.vocab_size,
                "vector_dim": self.vector_dim,
                "context_size": self.context_size,
            },
            "summary": {
                "prompts_total": len(outputs),
                "empty_generations": global_diagnostics["empty_generations"],
                "generations_with_repetition": global_diagnostics["generations_with_repetition"],
                "generations_with_dirty_tokens": global_diagnostics["generations_with_dirty_tokens"],
                "generations_with_numeric_tokens": global_diagnostics["generations_with_numeric_tokens"],
                "generations_with_metadata_tokens": global_diagnostics["generations_with_metadata_tokens"],
                "generations_without_domain_tokens": global_diagnostics["generations_without_domain_tokens"],
                "avg_generated_tokens": global_diagnostics["avg_generated_tokens"],
            },
            "diagnostics": global_diagnostics,
        }

        outputs_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        self.report_path.write_text(self._build_report(manifest, outputs), encoding="utf-8")

        return manifest

    def _load_weights(self) -> None:
        payload = json.loads(self.weights_path.read_text(encoding="utf-8"))

        if payload.get("versione") != "neural_model_v31_natural_weights":
            raise ValueError("Questa diagnostica raw richiede neural_model_v31_natural_weights.")

        settings = payload.get("settings", {})

        self.token_to_id = {str(token): int(token_id) for token, token_id in payload["token_to_id"].items()}
        self.id_to_token = [str(token) for token in payload["id_to_token"]]
        self.output_embeddings = [[float(value) for value in row] for row in payload["output_embeddings"]]
        self.output_bias = [float(value) for value in payload["output_bias"]]

        self.context_size = int(settings.get("context_size", 8))
        self.vocab_size = int(settings.get("vocab_size", len(self.id_to_token)))
        self.vector_dim = int(settings.get("vector_dim", 0))

        self.pad_id = self.token_to_id.get("<PAD>", 0)
        self.unk_id = self.token_to_id.get("<UNK>", 1)
        self.bos_id = self.token_to_id.get("<BOS>", 2)
        self.eos_id = self.token_to_id.get("<EOS>", 3)

    def _load_embeddings(self) -> None:
        payload = json.loads(self.embeddings_path.read_text(encoding="utf-8"))

        if payload.get("versione") != "token_embeddings_v21_natural":
            raise ValueError("Questa diagnostica raw richiede token_embeddings_v21_natural.")

        self.input_embeddings = [[float(value) for value in row] for row in payload["embedding_matrix"]]

        if len(self.input_embeddings) != self.vocab_size:
            raise ValueError("Embedding matrix incoerente con vocab size.")

    def generate_raw(self, prompt: str) -> Dict:
        prompt_tokens = self._tokenize(prompt)
        context_ids = self._encode_prompt(prompt)

        if not context_ids:
            context_ids = [self.bos_id]

        generated_ids: List[int] = []
        generated_tokens: List[str] = []
        step_trace: List[Dict] = []

        for step in range(1, self.max_new_tokens + 1):
            candidates = self._top_candidates(context_ids, self.top_k_trace)
            chosen = candidates[0]
            chosen_id = int(chosen["token_id"])
            chosen_token = str(chosen["token"])

            step_trace.append(
                {
                    "step": step,
                    "context_tokens": [self.id_to_token[token_id] for token_id in context_ids],
                    "chosen_token": chosen_token,
                    "chosen_token_id": chosen_id,
                    "top_candidates": candidates,
                }
            )

            if chosen_id == self.eos_id:
                generated_ids.append(chosen_id)
                generated_tokens.append(chosen_token)
                break

            generated_ids.append(chosen_id)
            generated_tokens.append(chosen_token)
            context_ids.append(chosen_id)
            context_ids = context_ids[-self.context_size :]

        raw_text = self._detokenize_raw(generated_tokens)
        diagnostics = self._diagnose_generation(prompt, generated_tokens, step_trace)

        return {
            "prompt": prompt,
            "prompt_tokens": prompt_tokens,
            "prompt_token_ids": self._encode_prompt(prompt),
            "generated_text_raw": raw_text,
            "generated_tokens_raw": generated_tokens,
            "generated_token_ids_raw": generated_ids,
            "step_trace": step_trace,
            "diagnostics": diagnostics,
            "generation_mode": "raw_model_only",
            "fallback_used": False,
            "hardcoded_sentence_used": False,
            "sentence_bank_used": False,
            "anchor_retrieval_used": False,
            "filters_used": False,
            "model_version": "neural_model_v31_natural",
            "diagnostic_version": "inference_raw_diagnostics_v1",
        }

    def _top_candidates(self, context_ids: List[int], top_k: int) -> List[Dict]:
        context_vector = self._context_vector(context_ids)
        scored: List[Tuple[int, float]] = []

        for token_id in range(self.vocab_size):
            score = self._score(context_vector, token_id)

            if self.temperature > 0:
                score = score / self.temperature

            scored.append((token_id, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        selected = scored[:top_k]

        max_score = selected[0][1] if selected else 0.0
        exp_scores = [math.exp(score - max_score) for _token_id, score in selected]
        exp_sum = sum(exp_scores)

        result = []

        for (token_id, score), exp_score in zip(selected, exp_scores):
            token = self.id_to_token[token_id]
            probability = exp_score / exp_sum if exp_sum else 0.0
            result.append(
                {
                    "token_id": token_id,
                    "token": token,
                    "score": round(score, 6),
                    "probability_topk": round(probability, 6),
                    "is_dirty": self._is_dirty_token(token),
                    "is_numeric_code": self._is_numeric_code_token(token),
                    "is_metadata": self._is_metadata_shape_token(token),
                    "is_weak": token.lower() in self.WEAK_TOKENS,
                    "is_domain": token.lower() in self.DOMAIN_TOKENS,
                }
            )

        return result

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

        return total

    def _encode_prompt(self, prompt: str) -> List[int]:
        tokens = self._tokenize(prompt)
        ids = [self.token_to_id[token] for token in tokens if token in self.token_to_id]
        return ids[-self.context_size :]

    def _diagnose_generation(self, prompt: str, tokens: List[str], step_trace: List[Dict]) -> Dict:
        normalized_tokens = [str(token).lower() for token in tokens]

        dirty = [token for token in normalized_tokens if self._is_dirty_token(token)]
        numeric = [token for token in normalized_tokens if self._is_numeric_code_token(token)]
        metadata = [token for token in normalized_tokens if self._is_metadata_shape_token(token)]
        weak = [token for token in normalized_tokens if token in self.WEAK_TOKENS]
        domain = [token for token in normalized_tokens if token in self.DOMAIN_TOKENS]

        repeated_tokens = [token for token, count in Counter(normalized_tokens).items() if count >= 2]
        immediate_duplicates = []
        for left, right in zip(normalized_tokens, normalized_tokens[1:]):
            if left == right:
                immediate_duplicates.append(left)

        bigrams = list(zip(normalized_tokens, normalized_tokens[1:]))
        repeated_bigrams = []
        bigram_counts = Counter(bigrams)
        for bigram, count in bigram_counts.items():
            if count >= 2:
                repeated_bigrams.append(" ".join(bigram))

        punctuation_start = bool(tokens and tokens[0] in self.PUNCTUATION)
        eos_generated = bool(tokens and tokens[-1] == "<EOS>")
        empty_generation = len(tokens) == 0
        too_short = len([token for token in tokens if token not in self.PUNCTUATION]) < 6
        no_domain = len(domain) == 0

        probable_causes = []

        if empty_generation:
            probable_causes.append("Il modello non ha generato token utili.")

        if too_short:
            probable_causes.append("La generazione è troppo corta per formare una frase utile.")

        if no_domain:
            probable_causes.append("La generazione non contiene concetti di dominio.")

        if repeated_tokens or immediate_duplicates or repeated_bigrams:
            probable_causes.append("Il modello tende a ripetere token o gruppi di token.")

        if dirty or numeric or metadata:
            probable_causes.append("Il modello seleziona token contaminati o tecnici.")

        if weak and len(weak) >= max(3, len(tokens) // 2):
            probable_causes.append("La generazione è dominata da parole deboli o funzionali.")

        if punctuation_start:
            probable_causes.append("Il modello può iniziare con punteggiatura, segno di decoding instabile.")

        if not probable_causes:
            probable_causes.append("La generazione raw non mostra errori tecnici evidenti, ma va valutata semanticamente.")

        return {
            "empty_generation": empty_generation,
            "too_short": too_short,
            "eos_generated": eos_generated,
            "punctuation_start": punctuation_start,
            "dirty_tokens": dirty,
            "numeric_code_tokens": numeric,
            "metadata_tokens": metadata,
            "weak_tokens": weak,
            "domain_tokens": domain,
            "repeated_tokens": repeated_tokens,
            "immediate_duplicates": immediate_duplicates,
            "repeated_bigrams": repeated_bigrams,
            "probable_causes": probable_causes,
        }

    def _global_diagnostics(self, outputs: List[Dict]) -> Dict:
        empty = 0
        with_repetition = 0
        with_dirty = 0
        with_numeric = 0
        with_metadata = 0
        without_domain = 0
        total_tokens = 0
        all_probable_causes = Counter()

        for item in outputs:
            diagnostics = item.get("diagnostics", {})
            tokens = item.get("generated_tokens_raw", [])
            total_tokens += len(tokens)

            if diagnostics.get("empty_generation"):
                empty += 1

            if diagnostics.get("repeated_tokens") or diagnostics.get("immediate_duplicates") or diagnostics.get("repeated_bigrams"):
                with_repetition += 1

            if diagnostics.get("dirty_tokens"):
                with_dirty += 1

            if diagnostics.get("numeric_code_tokens"):
                with_numeric += 1

            if diagnostics.get("metadata_tokens"):
                with_metadata += 1

            if not diagnostics.get("domain_tokens"):
                without_domain += 1

            for cause in diagnostics.get("probable_causes", []):
                all_probable_causes[cause] += 1

        return {
            "empty_generations": empty,
            "generations_with_repetition": with_repetition,
            "generations_with_dirty_tokens": with_dirty,
            "generations_with_numeric_tokens": with_numeric,
            "generations_with_metadata_tokens": with_metadata,
            "generations_without_domain_tokens": without_domain,
            "avg_generated_tokens": round(total_tokens / max(1, len(outputs)), 2),
            "probable_causes_summary": dict(all_probable_causes),
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _detokenize_raw(self, tokens: List[str]) -> str:
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
        return re.sub(r"\s+", " ", text).strip()

    def _is_dirty_token(self, token: str) -> bool:
        return str(token).lower().strip() in self.DIRTY_TOKENS

    def _is_numeric_code_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()
        return bool(re.fullmatch(r"0\d{2,}", normalized) or re.fullmatch(r"\d{4,}", normalized))

    def _is_metadata_shape_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()
        return bool("_" in normalized or re.fullmatch(r"[a-zàèéìòù]+v\d+", normalized) or re.search(r"[a-zàèéìòù]+_?[vV]?\d{1,}", normalized))

    def _build_report(self, manifest: Dict, outputs: List[Dict]) -> str:
        lines = [
            "# Report Inference Raw Diagnostics V1",
            "",
            "## Stato",
            str(manifest["status"]),
            "",
            "## Regola",
            "Nessun fallback, nessuna frase hardcoded, nessuna ancora, nessun sentence bank.",
            "",
            "## Impostazioni",
            "```json",
            json.dumps(manifest["settings"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Sintesi",
            "```json",
            json.dumps(manifest["summary"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Diagnostica globale",
            "```json",
            json.dumps(manifest["diagnostics"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Generazioni raw",
            "",
        ]

        for item in outputs:
            lines.append(f"### Prompt: {item['prompt']}")
            lines.append("")
            lines.append(f"Output raw: {item.get('generated_text_raw', '')}")
            lines.append("")
            lines.append("Problemi rilevati:")
            for cause in item.get("diagnostics", {}).get("probable_causes", []):
                lines.append(f"- {cause}")
            lines.append("")
            lines.append("Token raw:")
            lines.append("```json")
            lines.append(json.dumps(item.get("generated_tokens_raw", []), ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inference Raw Diagnostics V1")
    parser.add_argument("--weights", default="mini_llm/data/model_v31_natural/neural_model_v31_natural_weights.json")
    parser.add_argument("--embeddings", default="mini_llm/data/vectorized_v21_natural/token_embeddings_v21_natural.json")
    parser.add_argument("--output-dir", default="mini_llm/data/diagnostics/inference_raw_diagnostics_v1")
    parser.add_argument("--report", default="mini_llm/reports/inference_raw_diagnostics_v1_report.md")
    parser.add_argument("--prompt", action="append", default=[])
    parser.add_argument("--max-new-tokens", type=int, default=20)
    parser.add_argument("--top-k-trace", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()
    prompts = args.prompt if args.prompt else InferenceRawDiagnosticsV1.DEFAULT_PROMPTS

    engine = InferenceRawDiagnosticsV1(
        weights_path=(root / args.weights).resolve(),
        embeddings_path=(root / args.embeddings).resolve(),
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        max_new_tokens=args.max_new_tokens,
        top_k_trace=args.top_k_trace,
        temperature=args.temperature,
    )

    manifest = engine.run(prompts)

    print("OK - Inference Raw Diagnostics V1 completata")
    print(f"Output diagnostica: {manifest['output_files']['outputs']}")
    print(f"Manifest: {manifest['output_files']['manifest']}")
    print(f"Report: {manifest['output_files']['report']}")
    print(f"Generazione: {manifest['settings']['generation_mode']}")
    print(f"Fallback enabled: {manifest['settings']['fallback_enabled']}")
    print(f"Hardcoded sentences enabled: {manifest['settings']['hardcoded_sentences_enabled']}")
    print(f"Sentence bank enabled: {manifest['settings']['sentence_bank_enabled']}")
    print(f"Anchor retrieval enabled: {manifest['settings']['anchor_retrieval_enabled']}")
    print(f"Filters enabled: {manifest['settings']['filters_enabled']}")
    print(f"Prompt totali: {manifest['summary']['prompts_total']}")
    print(f"Generazioni vuote: {manifest['summary']['empty_generations']}")
    print(f"Generazioni con ripetizioni: {manifest['summary']['generations_with_repetition']}")
    print(f"Generazioni con token sporchi: {manifest['summary']['generations_with_dirty_tokens']}")
    print(f"Generazioni con codici numerici: {manifest['summary']['generations_with_numeric_tokens']}")
    print(f"Generazioni con metadata: {manifest['summary']['generations_with_metadata_tokens']}")
    print(f"Generazioni senza dominio: {manifest['summary']['generations_without_domain_tokens']}")
    print(f"Media token generati: {manifest['summary']['avg_generated_tokens']}")

    outputs = json.loads(Path(manifest["output_files"]["outputs"]).read_text(encoding="utf-8"))

    for item in outputs:
        print(f"- {item['prompt']} -> {item['generated_text_raw']}")
        for cause in item["diagnostics"]["probable_causes"]:
            print(f"  CAUSA: {cause}")


if __name__ == "__main__":
    main()
