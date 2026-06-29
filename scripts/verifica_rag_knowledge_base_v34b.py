#!/usr/bin/env python3
"""
Verifica Knowledge Base RAG V3.4B

Controlla che la KB sia generale e funzioni su più argomenti.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "dist/generated/rag_knowledge_base_v34b/test_inputs"
OUT = ROOT / "dist/generated/rag_knowledge_base_v34b/test_outputs"
REPORT = ROOT / "reports/rag_knowledge_base_v34b.md"

DOCUMENTI_TEST = {
    "sicurezza": """
    Documento di formazione sulla protezione degli account aziendali.
    Le credenziali devono essere gestite con attenzione e non devono essere riutilizzate su servizi diversi.
    Un secondo controllo di accesso riduce il rischio quando una credenziale viene scoperta.
    I messaggi sospetti devono essere verificati controllando mittente, collegamenti e richieste insolite.
    Gli aggiornamenti e gli strumenti di protezione aiutano a ridurre i rischi collegati al software dannoso.
    """,
    "sport": """
    Scheda di allenamento per migliorare forza e resistenza.
    Il riscaldamento prepara muscoli e articolazioni allo sforzo e riduce il rischio di fastidi.
    La progressione dei carichi deve essere graduale per evitare sovraccarichi.
    Il recupero è parte del programma perché permette al corpo di adattarsi allo stimolo allenante.
    Gli esercizi devono essere scelti in base all'obiettivo e al livello della persona.
    """,
    "curriculum": """
    Profilo professionale di un candidato per un ruolo tecnico.
    Il curriculum deve presentare esperienze, competenze e risultati in modo chiaro.
    Le competenze tecniche sono più efficaci quando sono collegate ad attività concrete.
    La sintesi iniziale aiuta il selezionatore a capire rapidamente il valore del profilo.
    Le esperienze devono essere ordinate e descritte con responsabilità, strumenti usati e risultati raggiunti.
    """,
    "poesia": """
    Testo poetico dedicato al viaggio e alla memoria.
    Le immagini del mare e della luce creano un tono malinconico ma aperto alla speranza.
    Il ritmo dei versi accompagna il passaggio dal ricordo alla consapevolezza.
    Le metafore collegano il paesaggio esterno allo stato interiore della voce poetica.
    Il significato nasce dal rapporto tra parole, pause, immagini e atmosfera.
    """,
    "aziendale": """
    Procedura aziendale per la gestione delle richieste interne.
    Ogni richiesta deve essere registrata con descrizione, priorità e reparto responsabile.
    La tracciabilità consente di capire chi ha gestito l'attività e quali passaggi sono stati completati.
    Le scadenze aiutano a distinguere attività urgenti e attività programmabili.
    Il controllo finale verifica che la richiesta sia stata chiusa correttamente e comunicata al referente.
    """,
}


CAMPI_OBBLIGATORI = [
    "titolo_documento",
    "tipo_documento",
    "input_reale_usato",
    "chunk",
    "concetti",
    "parole_chiave",
    "frasi_importanti",
    "relazioni_tra_concetti",
    "fonti_pagine_sezioni",
    "output_generati",
    "controlli_qualita",
]


def run_builder(nome: str, testo: str) -> tuple[bool, Path, str]:
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    input_path = TMP / f"{nome}.txt"
    output_path = OUT / f"{nome}_knowledge_base.json"

    input_path.write_text(testo.strip() + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            "scripts/rag_build_knowledge_base_v34b.py",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    return result.returncode == 0, output_path, result.stdout + result.stderr


def valida_kb(path: Path) -> list[str]:
    problemi = []

    if not path.exists():
        return [f"file output mancante: {path}"]

    kb = json.loads(path.read_text(encoding="utf-8"))

    for campo in CAMPI_OBBLIGATORI:
        if campo not in kb:
            problemi.append(f"campo obbligatorio mancante: {campo}")

    if not kb.get("input_reale_usato"):
        problemi.append("input_reale_usato non confermato")

    if len(kb.get("chunk", [])) < 1:
        problemi.append("nessun chunk")

    if len(kb.get("concetti", [])) < 3:
        problemi.append("meno di 3 concetti")

    if len(kb.get("parole_chiave", [])) < 8:
        problemi.append("meno di 8 parole chiave")

    for concept in kb.get("concetti", []):
        if not concept.get("titolo"):
            problemi.append("concetto senza titolo")
        if not concept.get("descrizione"):
            problemi.append(f"concetto senza descrizione: {concept.get('id')}")
        if not concept.get("frasi_origine"):
            problemi.append(f"concetto senza frasi origine: {concept.get('id')}")
        if not concept.get("chunk_origine"):
            problemi.append(f"concetto senza chunk origine: {concept.get('id')}")

    quality = kb.get("controlli_qualita", {})
    if not quality.get("ok"):
        problemi.extend(quality.get("errori", []))

    return problemi


def controlla_hardcoding_builder() -> list[str]:
    problemi = []
    path = ROOT / "scripts/rag_build_knowledge_base_v34b.py"
    text = path.read_text(encoding="utf-8", errors="ignore").lower()

    vietati = [
        'if tema ==',
        'if tipo == "password"',
        "if tipo == 'password'",
        'if "phishing" in',
        "if 'phishing' in",
        'if "malware" in',
        "if 'malware' in",
    ]

    for item in vietati:
        if item in text:
            problemi.append(f"hardcoding vietato trovato nel builder: {item}")

    return problemi


def main() -> int:
    risultati = []
    errori_totali = []

    for nome, testo in DOCUMENTI_TEST.items():
        ok_run, output_path, log = run_builder(nome, testo)
        problemi = valida_kb(output_path)

        if ok_run and not problemi:
            risultati.append(f"OK: KB valida per {nome}")
        else:
            risultati.append(f"ERRORE: KB non valida per {nome}")
            if log.strip():
                errori_totali.append(f"LOG {nome}:\n{log.strip()}")
            for p in problemi:
                errori_totali.append(f"{nome}: {p}")

    problemi_hardcoding = controlla_hardcoding_builder()
    for p in problemi_hardcoding:
        errori_totali.append(p)

    if problemi_hardcoding:
        risultati.append("ERRORE: hardcoding vietato trovato")
    else:
        risultati.append("OK: nessun hardcoding specifico vietato nel builder")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Knowledge Base RAG V3.4B",
        "",
        "Verifica generale su più tipi di documento.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori_totali)}")
    lines.append("")

    if errori_totali:
        lines.append("## Errori")
        for err in errori_totali:
            lines.append(f"- {err}")
        lines.append("")
        lines.append("ESITO: DA RIVEDERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA KNOWLEDGE BASE RAG V3.4B ===")
    for r in risultati:
        print(r)
    print("")
    print("Errori totali:", len(errori_totali))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori_totali else "DA RIVEDERE")

    return 0 if not errori_totali else 1


if __name__ == "__main__":
    raise SystemExit(main())
