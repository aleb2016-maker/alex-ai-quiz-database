from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


class ModelQualityGateV1:
    """
    Model Quality Gate V1.

    Questo NON è un validatore tecnico finto.
    Questo è un cancello qualità reale.

    Deve fallire se:
    - il modello usa fallback;
    - il modello usa frasi hardcoded;
    - il modello usa sentence bank o ancore spacciate per generazione;
    - il modello genera token speciali come <BOS>, <PAD>, <UNK>;
    - il modello collassa ripetendo sempre lo stesso token;
    - il modello non produce concetti di dominio;
    - il modello produce testo troppo corto;
    - il modello produce output vuoto.

    Nota:
    il gate può essere usato su diagnostica raw o su output inferenza.
    """

    DEFAULT_RAW_OUTPUTS = Path("mini_llm/data/diagnostics/inference_raw_diagnostics_v1/inference_raw_diagnostics_v1_outputs.json")
    DEFAULT_RAW_MANIFEST = Path("mini_llm/data/diagnostics/inference_raw_diagnostics_v1/inference_raw_diagnostics_v1_manifest.json")
    DEFAULT_OUTPUT_DIR = Path("mini_llm/data/quality/model_quality_gate_v1")
    DEFAULT_REPORT = Path("mini_llm/reports/model_quality_gate_v1_report.md")

    SPECIAL_TOKENS_FORBIDDEN = {"<BOS>", "<PAD>", "<UNK>", "<bos>", "<pad>", "<unk>"}

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
        "informazioni",
        "attacco",
        "utente",
        "guasto",
        "furto",
        "servizio",
        "errore",
        "umano",
    }

    PUNCTUATION = {".", ",", ";", ":", "!", "?", "-", "(", ")", "'", "’"}

    def __init__(
        self,
        root: Path,
        outputs_path: Path,
        manifest_path: Path | None,
        output_dir: Path,
        report_path: Path,
        label: str,
        min_words: int = 6,
        max_same_token_ratio: float = 0.35,
        max_single_token_count: int = 3,
        require_domain: bool = True,
        forbid_sentence_bank: bool = True,
        forbid_anchor_retrieval: bool = True,
        forbid_fallback: bool = True,
        forbid_hardcoded: bool = True,
    ):
        self.root = root
        self.outputs_path = outputs_path
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        self.report_path = report_path
        self.label = label
        self.min_words = min_words
        self.max_same_token_ratio = max_same_token_ratio
        self.max_single_token_count = max_single_token_count
        self.require_domain = require_domain
        self.forbid_sentence_bank = forbid_sentence_bank
        self.forbid_anchor_retrieval = forbid_anchor_retrieval
        self.forbid_fallback = forbid_fallback
        self.forbid_hardcoded = forbid_hardcoded

    def run(self) -> Dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        outputs = self._load_outputs()
        manifest = self._load_manifest()

        checks = [self._check_output(index, item) for index, item in enumerate(outputs, start=1)]
        manifest_checks = self._check_manifest(manifest) if manifest else []

        all_errors = []
        all_warnings = []

        for check in checks:
            all_errors.extend(check["errors"])
            all_warnings.extend(check["warnings"])

        for check in manifest_checks:
            all_errors.extend(check["errors"])
            all_warnings.extend(check["warnings"])

        passed = not all_errors

        gate_manifest_path = self.output_dir / "model_quality_gate_v1_manifest.json"
        gate_results_path = self.output_dir / "model_quality_gate_v1_results.json"

        result = {
            "versione": "model_quality_gate_v1",
            "status": "passed" if passed else "failed",
            "label": self.label,
            "description": "Quality gate reale: fallisce se il modello usa pezze o collassa.",
            "input_files": {
                "outputs": str(self.outputs_path),
                "manifest": str(self.manifest_path) if self.manifest_path else "",
            },
            "output_files": {
                "results": str(gate_results_path),
                "manifest": str(gate_manifest_path),
                "report": str(self.report_path),
            },
            "rules": {
                "min_words": self.min_words,
                "max_same_token_ratio": self.max_same_token_ratio,
                "max_single_token_count": self.max_single_token_count,
                "require_domain": self.require_domain,
                "forbid_sentence_bank": self.forbid_sentence_bank,
                "forbid_anchor_retrieval": self.forbid_anchor_retrieval,
                "forbid_fallback": self.forbid_fallback,
                "forbid_hardcoded": self.forbid_hardcoded,
                "forbid_special_tokens": sorted(self.SPECIAL_TOKENS_FORBIDDEN),
            },
            "summary": {
                "outputs_total": len(outputs),
                "failed_outputs": sum(1 for check in checks if check["errors"]),
                "passed_outputs": sum(1 for check in checks if not check["errors"]),
                "manifest_errors": sum(len(check["errors"]) for check in manifest_checks),
                "errors_total": len(all_errors),
                "warnings_total": len(all_warnings),
            },
            "checks": checks,
            "manifest_checks": manifest_checks,
            "errors": all_errors,
            "warnings": all_warnings,
        }

        gate_results_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        gate_manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        self.report_path.write_text(self._build_report(result), encoding="utf-8")

        return result

    def _load_outputs(self) -> List[Dict]:
        if not self.outputs_path.exists():
            raise FileNotFoundError(f"Output inferenza/diagnostica non trovato: {self.outputs_path}")

        payload = json.loads(self.outputs_path.read_text(encoding="utf-8"))

        if not isinstance(payload, list):
            raise ValueError("Il file outputs deve contenere una lista JSON.")

        return payload

    def _load_manifest(self) -> Dict | None:
        if not self.manifest_path:
            return None

        if not self.manifest_path.exists():
            return None

        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))

        if not isinstance(payload, dict):
            return None

        return payload

    def _check_manifest(self, manifest: Dict) -> List[Dict]:
        checks = []

        settings = manifest.get("settings", {})
        summary = manifest.get("summary", {})

        for key in ["fallback_enabled", "hardcoded_sentences_enabled", "sentence_bank_enabled", "anchor_retrieval_enabled"]:
            value = settings.get(key)

            if value is True:
                checks.append({
                    "scope": "manifest",
                    "rule": f"{key}_must_not_be_true",
                    "errors": [f"Manifest vietato: {key}=True."],
                    "warnings": [],
                })

        if self.forbid_fallback and summary.get("fallback_used", 0):
            checks.append({
                "scope": "manifest",
                "rule": "fallback_used_must_be_zero",
                "errors": [f"Manifest segnala fallback_used={summary.get('fallback_used')}."],
                "warnings": [],
            })

        if self.forbid_hardcoded and summary.get("hardcoded_sentence_used", 0):
            checks.append({
                "scope": "manifest",
                "rule": "hardcoded_sentence_used_must_be_zero",
                "errors": [f"Manifest segnala hardcoded_sentence_used={summary.get('hardcoded_sentence_used')}."],
                "warnings": [],
            })

        if self.forbid_sentence_bank and summary.get("sentence_bank_used", 0):
            checks.append({
                "scope": "manifest",
                "rule": "sentence_bank_used_must_be_zero",
                "errors": [f"Manifest segnala sentence_bank_used={summary.get('sentence_bank_used')}."],
                "warnings": [],
            })

        if self.forbid_anchor_retrieval and summary.get("anchor_retrieval_used", 0):
            checks.append({
                "scope": "manifest",
                "rule": "anchor_retrieval_used_must_be_zero",
                "errors": [f"Manifest segnala anchor_retrieval_used={summary.get('anchor_retrieval_used')}."],
                "warnings": [],
            })

        if not checks:
            checks.append({
                "scope": "manifest",
                "rule": "manifest_quality_flags",
                "errors": [],
                "warnings": [],
            })

        return checks

    def _check_output(self, index: int, item: Dict) -> Dict:
        prompt = str(item.get("prompt", f"output-{index}"))

        tokens = self._extract_tokens(item)
        text = self._extract_text(item, tokens)
        normalized_tokens = [str(token).strip() for token in tokens if str(token).strip()]
        word_tokens = [token for token in normalized_tokens if token not in self.PUNCTUATION and token != "<EOS>"]

        errors = []
        warnings = []

        if not normalized_tokens or not text.strip():
            errors.append("Output vuoto o senza token generati.")

        if item.get("fallback_used") is True or item.get("emergency_fallback_used") is True:
            if self.forbid_fallback:
                errors.append("Output vietato: usa fallback.")

        if item.get("hardcoded_sentence_used") is True:
            if self.forbid_hardcoded:
                errors.append("Output vietato: usa frase hardcoded.")

        if item.get("sentence_bank_used") is True:
            if self.forbid_sentence_bank:
                errors.append("Output vietato: usa sentence bank.")

        if item.get("anchor_retrieval_used") is True:
            if self.forbid_anchor_retrieval:
                errors.append("Output vietato: usa anchor retrieval.")

        generation_mode = str(item.get("generation_mode", "")).lower()

        if self.forbid_sentence_bank and "sentence" in generation_mode:
            errors.append(f"Output vietato: generation_mode usa sentence bank o memoria fraseologica: {generation_mode}.")

        if self.forbid_anchor_retrieval and "anchor" in generation_mode:
            errors.append(f"Output vietato: generation_mode usa ancore: {generation_mode}.")

        if self.forbid_fallback and "fallback" in generation_mode:
            errors.append(f"Output vietato: generation_mode usa fallback: {generation_mode}.")

        special = [token for token in normalized_tokens if token in self.SPECIAL_TOKENS_FORBIDDEN]
        if special:
            errors.append(f"Token speciali vietati in output: {special}.")

        dirty = [token for token in normalized_tokens if token.lower() in self.DIRTY_TOKENS]
        if dirty:
            errors.append(f"Token sporchi vietati in output: {dirty}.")

        numeric = [token for token in normalized_tokens if self._is_numeric_code_token(token)]
        if numeric:
            errors.append(f"Codici numerici vietati in output: {numeric}.")

        metadata = [token for token in normalized_tokens if self._is_metadata_shape_token(token)]
        if metadata:
            errors.append(f"Token metadata vietati in output: {metadata}.")

        if len(word_tokens) < self.min_words:
            errors.append(f"Output troppo corto: {len(word_tokens)} parole utili, minimo {self.min_words}.")

        domain_tokens = [token for token in word_tokens if token.lower() in self.DOMAIN_TOKENS]

        if self.require_domain and not domain_tokens:
            errors.append("Output senza concetti di dominio.")

        repetition = self._repetition_stats(word_tokens)

        if repetition["max_single_token_count"] > self.max_single_token_count:
            errors.append(
                f"Collasso token: token '{repetition['most_common_token']}' ripetuto "
                f"{repetition['max_single_token_count']} volte."
            )

        if repetition["max_same_token_ratio"] > self.max_same_token_ratio:
            errors.append(
                f"Collasso ratio: token '{repetition['most_common_token']}' occupa "
                f"{repetition['max_same_token_ratio']:.2f} dell'output."
            )

        if repetition["immediate_duplicates"]:
            errors.append(f"Duplicati immediati vietati: {repetition['immediate_duplicates']}.")

        if repetition["repeated_bigrams"]:
            errors.append(f"Bigrammi ripetuti vietati: {repetition['repeated_bigrams']}.")

        if text and text[0] in ".,;:!?-":
            errors.append("Output inizia con punteggiatura.")

        if not errors and len(domain_tokens) == 1:
            warnings.append("Output passa il gate, ma contiene un solo concetto di dominio.")

        return {
            "index": index,
            "prompt": prompt,
            "passed": not errors,
            "text": text,
            "tokens": normalized_tokens,
            "word_tokens": word_tokens,
            "domain_tokens": domain_tokens,
            "repetition": repetition,
            "errors": errors,
            "warnings": warnings,
        }

    def _extract_tokens(self, item: Dict) -> List[str]:
        for key in ["generated_tokens_raw", "generated_tokens", "tokens"]:
            value = item.get(key)

            if isinstance(value, list):
                return [str(token) for token in value]

        text = self._extract_text(item, [])
        return self._tokenize(text)

    def _extract_text(self, item: Dict, tokens: List[str]) -> str:
        for key in ["generated_text_raw", "generated_text", "text"]:
            value = item.get(key)

            if isinstance(value, str):
                return value.strip()

        return " ".join(tokens).strip()

    def _repetition_stats(self, tokens: List[str]) -> Dict:
        if not tokens:
            return {
                "most_common_token": "",
                "max_single_token_count": 0,
                "max_same_token_ratio": 0.0,
                "immediate_duplicates": [],
                "repeated_bigrams": [],
            }

        lowered = [token.lower() for token in tokens]
        counts = Counter(lowered)
        most_common_token, max_count = counts.most_common(1)[0]
        ratio = max_count / max(1, len(lowered))

        immediate = []
        for left, right in zip(lowered, lowered[1:]):
            if left == right:
                immediate.append(left)

        bigrams = list(zip(lowered, lowered[1:]))
        repeated_bigrams = [" ".join(pair) for pair, count in Counter(bigrams).items() if count >= 2]

        return {
            "most_common_token": most_common_token,
            "max_single_token_count": int(max_count),
            "max_same_token_ratio": round(ratio, 4),
            "immediate_duplicates": sorted(set(immediate)),
            "repeated_bigrams": sorted(set(repeated_bigrams)),
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zàèéìòù0-9_]+|[^\s]", text.lower(), flags=re.IGNORECASE)

    def _is_numeric_code_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()
        return bool(re.fullmatch(r"0\d{2,}", normalized) or re.fullmatch(r"\d{4,}", normalized))

    def _is_metadata_shape_token(self, token: str) -> bool:
        normalized = str(token).strip().lower()
        return bool(
            "_" in normalized
            or re.fullmatch(r"[a-zàèéìòù]+v\d+", normalized)
            or re.search(r"[a-zàèéìòù]+_?[vV]?\d{1,}", normalized)
        )

    def _build_report(self, result: Dict) -> str:
        lines = [
            "# Report Model Quality Gate V1",
            "",
            "## Stato",
            result["status"].upper(),
            "",
            "## Regola",
            "Il modello fallisce se usa pezze o se collassa nella generazione.",
            "",
            "## Input",
            "```json",
            json.dumps(result["input_files"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Regole applicate",
            "```json",
            json.dumps(result["rules"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## Sintesi",
            "```json",
            json.dumps(result["summary"], ensure_ascii=False, indent=2),
            "```",
            "",
        ]

        if result["errors"]:
            lines.extend(["## Errori", ""])
            for error in result["errors"]:
                lines.append(f"- {error}")
            lines.append("")

        lines.extend(["## Controlli per output", ""])

        for check in result["checks"]:
            lines.append(f"### {check['index']}. {check['prompt']}")
            lines.append("")
            lines.append(f"Stato: {'OK' if check['passed'] else 'ERRORE'}")
            lines.append("")
            lines.append(f"Testo: {check['text']}")
            lines.append("")
            if check["errors"]:
                lines.append("Errori:")
                for error in check["errors"]:
                    lines.append(f"- {error}")
                lines.append("")
            if check["warnings"]:
                lines.append("Avvisi:")
                for warning in check["warnings"]:
                    lines.append(f"- {warning}")
                lines.append("")

        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Model Quality Gate V1")

    parser.add_argument("--outputs", default=str(ModelQualityGateV1.DEFAULT_RAW_OUTPUTS))
    parser.add_argument("--manifest", default=str(ModelQualityGateV1.DEFAULT_RAW_MANIFEST))
    parser.add_argument("--output-dir", default=str(ModelQualityGateV1.DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(ModelQualityGateV1.DEFAULT_REPORT))
    parser.add_argument("--label", default="raw_diagnostics_v1")
    parser.add_argument("--min-words", type=int, default=6)
    parser.add_argument("--max-same-token-ratio", type=float, default=0.35)
    parser.add_argument("--max-single-token-count", type=int, default=3)
    parser.add_argument("--allow-no-domain", action="store_true")
    parser.add_argument("--allow-sentence-bank", action="store_true")
    parser.add_argument("--allow-anchor-retrieval", action="store_true")
    parser.add_argument("--allow-fallback", action="store_true")
    parser.add_argument("--allow-hardcoded", action="store_true")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()

    gate = ModelQualityGateV1(
        root=root,
        outputs_path=(root / args.outputs).resolve(),
        manifest_path=(root / args.manifest).resolve() if args.manifest else None,
        output_dir=(root / args.output_dir).resolve(),
        report_path=(root / args.report).resolve(),
        label=args.label,
        min_words=args.min_words,
        max_same_token_ratio=args.max_same_token_ratio,
        max_single_token_count=args.max_single_token_count,
        require_domain=not args.allow_no_domain,
        forbid_sentence_bank=not args.allow_sentence_bank,
        forbid_anchor_retrieval=not args.allow_anchor_retrieval,
        forbid_fallback=not args.allow_fallback,
        forbid_hardcoded=not args.allow_hardcoded,
    )

    result = gate.run()

    print(f"{'OK' if result['status'] == 'passed' else 'ERRORE'} - Model Quality Gate V1: {result['status']}")
    print(f"Risultati: {result['output_files']['results']}")
    print(f"Manifest: {result['output_files']['manifest']}")
    print(f"Report: {result['output_files']['report']}")
    print(f"Output totali: {result['summary']['outputs_total']}")
    print(f"Output passati: {result['summary']['passed_outputs']}")
    print(f"Output falliti: {result['summary']['failed_outputs']}")
    print(f"Errori totali: {result['summary']['errors_total']}")
    print(f"Avvisi totali: {result['summary']['warnings_total']}")

    if result["errors"]:
        print("")
        print("ERRORI PRINCIPALI:")
        for error in result["errors"][:80]:
            print("-", error)
        if len(result["errors"]) > 80:
            print(f"... altri errori: {len(result['errors']) - 80}")

    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
