#!/usr/bin/env python3
"""
Verifica Quality Gate Knowledge Base V3.4D.

Non verifica una pagina.
Verifica che la KB pulita sia davvero usabile prima dei generatori.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/generated/rag_quality_gate_kb_v34d"
INPUTS = BASE / "inputs"
KBS_RAW = BASE / "kb_raw"
KBS_CLEAN = BASE / "kb_clean"
REPORT = ROOT / "reports/rag_quality_gate_kb_v34d.md"

DOCUMENTI = {
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

VIETATI_TESTO_UTENTE = [
    "#",
    "scopo del documento",
    "questo documento è stato creato",
    "fonte di prova",
    "motore rag",
    "progetto quiz",
    "rag/documenti",
    "esempio di domanda",
    "risposta corretta",
    "la risposta corretta è",
    "distrattore",
    "software autorizzato allegati",
    "malware allegati pericolosi",
    "dati dispositivi account",
    "indica punti sicurezza",
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def controlla_kb_pulita(path: Path) -> list[str]:
    problemi = []

    if not path.exists():
        return [f"KB pulita mancante: {path}"]

    data = json.loads(path.read_text(encoding="utf-8"))
    gate = data.get("quality_gate_v34d", {})

    if not gate.get("ok"):
        problemi.extend(gate.get("errori", []))

    concetti = data.get("concetti", [])

    if len(concetti) < 4:
        problemi.append("meno di 4 concetti puliti")

    for index, c in enumerate(concetti, start=1):
        titolo = str(c.get("titolo_utente") or c.get("titolo") or "")
        testo = str(c.get("testo_utente") or c.get("descrizione") or "")
        combined = f"{titolo} {testo}".lower()

        if not titolo or len(titolo) < 5:
            problemi.append(f"concetto {index}: titolo utente mancante/debole")

        if not testo or len(testo) < 45:
            problemi.append(f"concetto {index}: testo utente mancante/debole")

        for banned in VIETATI_TESTO_UTENTE:
            if banned in combined:
                problemi.append(f"concetto {index}: testo utente contiene vietato: {banned}")

        if "concept_id" in combined or "chunk_id" in combined:
            problemi.append(f"concetto {index}: id tecnico nel testo utente")

    return problemi


def controlla_hardcoding() -> list[str]:
    problemi = []
    text = (ROOT / "scripts/rag_quality_gate_kb_v34d.py").read_text(encoding="utf-8", errors="ignore").lower()

    vietati = [
        "if tema ==",
        "if tipo ==",
        'if "password"',
        "if 'password'",
        'if "phishing"',
        "if 'phishing'",
        'if "malware"',
        "if 'malware'",
        'if "sport"',
        "if 'sport'",
        'if "curriculum"',
        "if 'curriculum'",
    ]

    for item in vietati:
        if item in text:
            problemi.append(f"hardcoding specifico vietato: {item}")

    return problemi


def main() -> int:
    INPUTS.mkdir(parents=True, exist_ok=True)
    KBS_RAW.mkdir(parents=True, exist_ok=True)
    KBS_CLEAN.mkdir(parents=True, exist_ok=True)

    risultati = []
    errori = []

    for nome, testo in DOCUMENTI.items():
        input_path = INPUTS / f"{nome}.txt"
        raw_path = KBS_RAW / f"{nome}_kb_raw.json"
        clean_path = KBS_CLEAN / f"{nome}_kb_clean_v34d.json"

        input_path.write_text(testo.strip() + "\n", encoding="utf-8")

        code_build, log_build = run([
            "python3",
            "scripts/rag_build_knowledge_base_v34b.py",
            "--input",
            str(input_path),
            "--output",
            str(raw_path),
        ])

        if code_build != 0:
            risultati.append(f"ERRORE: build KB fallita per {nome}")
            errori.append(log_build)
            continue

        code_gate, log_gate = run([
            "python3",
            "scripts/rag_quality_gate_kb_v34d.py",
            "--kb",
            str(raw_path),
            "--output",
            str(clean_path),
        ])

        problemi = controlla_kb_pulita(clean_path)

        if code_gate == 0 and not problemi:
            risultati.append(f"OK: quality gate KB valido per {nome}")
        else:
            risultati.append(f"ERRORE: quality gate KB non valido per {nome}")
            if log_gate.strip():
                errori.append(f"LOG {nome}:\n{log_gate.strip()}")
            for p in problemi:
                errori.append(f"{nome}: {p}")


    # Regressione obbligatoria su documento reale già presente nel progetto.
    # Serve a evitare falsi OK sui soli documenti sintetici.
    real_input = ROOT / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    if real_input.exists():
        nome = "sicurezza_reale"
        raw_path = KBS_RAW / f"{nome}_kb_raw.json"
        clean_path = KBS_CLEAN / f"{nome}_kb_clean_v34d.json"

        code_build, log_build = run([
            "python3",
            "scripts/rag_build_knowledge_base_v34b.py",
            "--input",
            str(real_input),
            "--output",
            str(raw_path),
        ])

        if code_build != 0:
            risultati.append("ERRORE: build KB fallita per sicurezza_reale")
            errori.append(log_build)
        else:
            code_gate, log_gate = run([
                "python3",
                "scripts/rag_quality_gate_kb_v34d.py",
                "--kb",
                str(raw_path),
                "--output",
                str(clean_path),
            ])

            problemi = controlla_kb_pulita(clean_path)

            if code_gate == 0 and not problemi:
                risultati.append("OK: quality gate KB valido per sicurezza_reale")
            else:
                risultati.append("ERRORE: quality gate KB non valido per sicurezza_reale")
                if log_gate.strip():
                    errori.append(f"LOG sicurezza_reale:\n{log_gate.strip()}")
                for p in problemi:
                    errori.append(f"sicurezza_reale: {p}")


    problemi_hardcoding = controlla_hardcoding()
    if problemi_hardcoding:
        risultati.append("ERRORE: hardcoding specifico trovato")
        errori.extend(problemi_hardcoding)
    else:
        risultati.append("OK: nessun hardcoding specifico vietato nel quality gate")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Quality Gate Knowledge Base RAG V3.4D",
        "",
        "Verifica della pulizia architetturale della Knowledge Base prima dei generatori.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori)}")
    lines.append("")

    if errori:
        lines.append("## Errori")
        for e in errori:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("ESITO: DA RIVEDERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA QUALITY GATE KB V3.4D ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA RIVEDERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
