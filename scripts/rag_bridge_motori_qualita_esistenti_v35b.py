#!/usr/bin/env python3
"""
RAG Bridge Motori Qualità Esistenti V3.5B

Questo script NON crea un nuovo motore qualità.
Collega l'output RAG V3.4E ai motori qualità già presenti nel progetto.

Motori collegati:
- scripts/motore_qualita_generale.py
- scripts/motore_distrattori_ai.py

Se i motori non vengono importati e usati, il bridge fallisce.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


MOTORE_QUALITA_GENERALE = ROOT / "scripts/motore_qualita_generale.py"
MOTORE_DISTRATTORI_AI = ROOT / "scripts/motore_distrattori_ai.py"


FINALI_MOZZATI = {
    "e", "di", "da", "con", "per", "su", "tra", "fra",
    "della", "delle", "degli", "dello", "alla", "alle",
    "agli", "nella", "nelle", "negli", "sulla", "sulle",
    "dei", "del", "nel", "nei", "al", "ai",
}


def importa_modulo(path: Path, nome: str):
    if not path.exists():
        raise FileNotFoundError(f"Motore mancante: {path}")

    spec = importlib.util.spec_from_file_location(nome, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalizza_fallback(value: str) -> str:
    text = " ".join(str(value or "").split()).strip().lower()
    text = re.sub(r"[^\wàèéìòùç]+", " ", text)
    return " ".join(text.split())


class MotoriEsistenti:
    def __init__(self) -> None:
        self.qualita = importa_modulo(MOTORE_QUALITA_GENERALE, "motore_qualita_generale_v35b")
        self.distrattori = importa_modulo(MOTORE_DISTRATTORI_AI, "motore_distrattori_ai_v35b")
        self.funzioni_usate = []

    def normalizza(self, value: str) -> str:
        if hasattr(self.qualita, "normalizza_testo"):
            self.funzioni_usate.append("motore_qualita_generale.normalizza_testo")
            return self.qualita.normalizza_testo(value)

        if hasattr(self.qualita, "normalizza_per_confronto"):
            self.funzioni_usate.append("motore_qualita_generale.normalizza_per_confronto")
            return self.qualita.normalizza_per_confronto(value)

        if hasattr(self.distrattori, "pulisci_testo"):
            self.funzioni_usate.append("motore_distrattori_ai.pulisci_testo")
            return self.distrattori.pulisci_testo(value)

        return normalizza_fallback(value)

    def similarita(self, a: str, b: str) -> float:
        if hasattr(self.qualita, "rapporto_similarita"):
            self.funzioni_usate.append("motore_qualita_generale.rapporto_similarita")
            try:
                return float(self.qualita.rapporto_similarita(a, b))
            except Exception:
                pass

        if hasattr(self.distrattori, "similarita"):
            self.funzioni_usate.append("motore_distrattori_ai.similarita")
            try:
                return float(self.distrattori.similarita(a, b))
            except Exception:
                pass

        na = set(self.normalizza(a).split())
        nb = set(self.normalizza(b).split())

        if not na or not nb:
            return 0.0

        return len(na & nb) / len(na | nb)

    def analizza_domanda_se_possibile(self, domanda: dict[str, Any]) -> Any:
        if hasattr(self.qualita, "analizza_domanda"):
            self.funzioni_usate.append("motore_qualita_generale.analizza_domanda")
            try:
                return self.qualita.analizza_domanda(domanda)
            except TypeError:
                pass
            except Exception as exc:
                return {"errore_motore_qualita_generale": str(exc)}

        if hasattr(self.distrattori, "analizza_domanda"):
            self.funzioni_usate.append("motore_distrattori_ai.analizza_domanda")
            try:
                return self.distrattori.analizza_domanda(domanda)
            except TypeError:
                pass
            except Exception as exc:
                return {"errore_motore_distrattori_ai": str(exc)}

        return None


def carica_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def testo_visibile(output: dict[str, Any]) -> list[str]:
    testi = []

    r = output.get("riassunto", {})
    testi.extend([
        r.get("titolo", ""),
        r.get("testo_breve", ""),
        r.get("conclusione", ""),
    ])

    for p in r.get("punti_chiave", []) or []:
        testi.extend([p.get("titolo", ""), p.get("testo", "")])

    for c in output.get("card", []) or []:
        testi.extend([
            c.get("titolo", ""),
            c.get("testo", ""),
            c.get("messaggio_chiave", ""),
            c.get("fonte_visibile", ""),
        ])

    for t in output.get("test", []) or []:
        testi.append(t.get("domanda", ""))
        testi.extend(t.get("opzioni", []) or [])
        testi.append(t.get("risposta_corretta", ""))
        testi.append(t.get("spiegazione", ""))
        testi.append(t.get("fonte_visibile", ""))

    for s in output.get("domande_studio", []) or []:
        testi.extend([
            s.get("domanda", ""),
            s.get("risposta_guida", ""),
            s.get("fonte_visibile", ""),
        ])

    return [" ".join(str(t or "").split()).strip() for t in testi if str(t or "").strip()]


def finisce_male(value: str) -> bool:
    text = " ".join(str(value or "").split()).strip(" .!?;:,")
    if not text:
        return True

    last = text.split()[-1].lower().strip(" .!?;:,")
    return last in FINALI_MOZZATI


def domande_quiz_da_rag(output: dict[str, Any]) -> list[dict[str, Any]]:
    domande = []

    for item in output.get("test", []) or []:
        domande.append({
            "domanda": item.get("domanda", ""),
            "opzioni": item.get("opzioni", []),
            "risposta_corretta": item.get("risposta_corretta", ""),
            "spiegazione": item.get("spiegazione", ""),
        })

    return domande


def controlla_test_con_motori(domande: list[dict[str, Any]], motori: MotoriEsistenti) -> list[str]:
    errori = []
    opzioni_globali = []

    for index, domanda in enumerate(domande, start=1):
        testo_domanda = domanda.get("domanda", "")
        opzioni = domanda.get("opzioni", []) or []
        corretta = domanda.get("risposta_corretta", "")

        motori.analizza_domanda_se_possibile(domanda)

        if len(opzioni) != 4:
            errori.append(f"test {index}: numero opzioni diverso da 4")

        if corretta not in opzioni:
            errori.append(f"test {index}: risposta corretta assente dalle opzioni")

        normalizzate = [motori.normalizza(o) for o in opzioni]

        if len(normalizzate) != len(set(normalizzate)):
            errori.append(f"test {index}: opzioni duplicate secondo motore esistente")

        for a_i, a in enumerate(opzioni):
            for b_i, b in enumerate(opzioni):
                if b_i <= a_i:
                    continue

                sim = motori.similarita(a, b)
                if sim >= 0.92:
                    errori.append(f"test {index}: opzioni troppo simili secondo motore esistente")

        if not testo_domanda or len(testo_domanda) < 12:
            errori.append(f"test {index}: domanda troppo debole")

        for opt in opzioni:
            opzioni_globali.append(motori.normalizza(opt))

    counts = Counter(opzioni_globali)

    for opt, count in counts.items():
        if count > 2:
            errori.append(f"opzione ripetuta troppe volte tra domande diverse: {count} volte")

    return errori


def controlla_testi_visibili(output: dict[str, Any], motori: MotoriEsistenti) -> list[str]:
    errori = []

    marcatori_tecnici = [
        "concept_id",
        "chunk_id",
        "knowledge_base_json",
        "origine_kb",
        "tracciabilita",
        "rag/documenti",
        "documento rag di test",
        "scopo del documento",
        "fonte di prova",
        "motore rag",
        "progetto quiz",
    ]

    for text in testo_visibile(output):
        low = motori.normalizza(text)

        for marker in marcatori_tecnici:
            if marker in low:
                errori.append(f"testo tecnico visibile: {marker}")

        if finisce_male(text):
            errori.append(f"frase visibile troncata male: {text}")

    return errori


def valuta_output(output: dict[str, Any]) -> dict[str, Any]:
    motori = MotoriEsistenti()

    domande = domande_quiz_da_rag(output)

    errori = []
    errori.extend(controlla_test_con_motori(domande, motori))
    errori.extend(controlla_testi_visibili(output, motori))

    funzioni_distinte = sorted(set(motori.funzioni_usate))

    if not any(f.startswith("motore_qualita_generale.") for f in funzioni_distinte):
        errori.append("motore_qualita_generale non usato realmente")

    if not any(f.startswith("motore_distrattori_ai.") for f in funzioni_distinte):
        errori.append("motore_distrattori_ai non usato realmente")

    return {
        "ok": not errori,
        "errori": errori,
        "motori_importati": [
            str(MOTORE_QUALITA_GENERALE.relative_to(ROOT)),
            str(MOTORE_DISTRATTORI_AI.relative_to(ROOT)),
        ],
        "funzioni_usate": funzioni_distinte,
        "domande_test_controllate": len(domande),
        "testi_visibili_controllati": len(testo_visibile(output)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-report-json", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    report_path = Path(args.output_report_json)

    output = carica_json(input_path)
    report = valuta_output(output)

    salva_json(report_path, report)

    print("=== RAG BRIDGE MOTORI QUALITÀ ESISTENTI V3.5B ===")
    print("Input:", input_path)
    print("Report JSON:", report_path)
    print("Qualità OK:", report["ok"])
    print("Domande test controllate:", report["domande_test_controllate"])
    print("Testi visibili controllati:", report["testi_visibili_controllati"])
    print("Motori importati:")
    for m in report["motori_importati"]:
        print("-", m)
    print("Funzioni usate:")
    for f in report["funzioni_usate"]:
        print("-", f)

    if report["errori"]:
        print("ERRORI:")
        for e in report["errori"]:
            print("-", e)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
