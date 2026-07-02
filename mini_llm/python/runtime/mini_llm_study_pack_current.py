#!/usr/bin/env python3
"""
Mini LLM Study Pack Current.

Alias stabile del miglior motore study pack disponibile.

Current attuale:
- mini_llm_study_pack_v3_quality_gate

Perché:
- genera riassunto, card, Q&A e test;
- separa test studente e answer key;
- mantiene quality gate forte;
- resta ultra rapido;
- non usa LLM locali lenti.

Questo file evita che il codice futuro dipenda da versioni sparse V1/V2/V3.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict


CURRENT_ENGINE_NAME = "mini_llm_study_pack_v3_quality_gate"
CURRENT_ENGINE_FILE = "mini_llm/python/runtime/mini_llm_study_pack_v3_quality_gate.py"
CURRENT_CLI_FILE = "scripts/mini_llm_study_pack_cli_v2.py"
CURRENT_TAG = "checkpoint-mini-llm-study-pack-cli-v2"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_current_module():
    root = repo_root()
    path = root / CURRENT_ENGINE_FILE

    if not path.exists():
        raise FileNotFoundError(f"Motore current non trovato: {path}")

    spec = importlib.util.spec_from_file_location(CURRENT_ENGINE_NAME, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare motore current: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


class MiniLLMStudyPackCurrent:
    def __init__(self, text: str, max_words_per_chunk: int = 90) -> None:
        module = load_current_module()
        self.engine = module.MiniLLMStudyPackV3QualityGate(
            text,
            max_words_per_chunk=max_words_per_chunk,
        )

    def generate_pack(
        self,
        max_summary_sentences: int = 8,
        max_cards: int = 6,
        max_qas: int = 8,
        max_test_questions: int = 6,
    ) -> Dict[str, object]:
        pack = self.engine.generate_pack(
            max_summary_sentences=max_summary_sentences,
            max_cards=max_cards,
            max_qas=max_qas,
            max_test_questions=max_test_questions,
        )

        pack["current"] = {
            "alias": "mini_llm_study_pack_current",
            "engine": CURRENT_ENGINE_NAME,
            "engine_file": CURRENT_ENGINE_FILE,
            "cli_file": CURRENT_CLI_FILE,
            "tag": CURRENT_TAG,
        }

        return pack


def generate_study_pack(text: str) -> Dict[str, object]:
    return MiniLLMStudyPackCurrent(text).generate_pack()


def main() -> int:
    sample = """
    La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
    Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
    I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
    L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
    Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
    Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
    Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
    Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
    Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.
    I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.
    La formazione del personale riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano.
    Le procedure di sicurezza aiutano a gestire incidenti, accessi, backup, dispositivi e comunicazioni interne.
    """

    pack = generate_study_pack(sample)
    print(json.dumps(pack, ensure_ascii=False, indent=2))

    return 0 if pack.get("status") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
