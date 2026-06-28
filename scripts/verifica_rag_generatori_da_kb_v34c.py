#!/usr/bin/env python3
"""
Verifica generatori Test + Domande Studio da KB V3.4C.

La verifica costruisce KB su più documenti e poi genera output SOLO dalla KB.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/generated/rag_generatori_da_kb_v34c"
INPUTS = BASE / "test_inputs"
KBS = BASE / "test_kb"
OUTPUTS = BASE / "test_outputs"
REPORT = ROOT / "reports/rag_generatori_da_kb_v34c.md"

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


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def controlla_output(path: Path) -> list[str]:
    problemi = []

    if not path.exists():
        return [f"output mancante: {path}"]

    data = json.loads(path.read_text(encoding="utf-8"))

    test = data.get("test", [])
    studio = data.get("domande_studio", [])
    qualita = data.get("controlli_qualita", {})

    if data.get("fonte") != "knowledge_base_json":
        problemi.append("fonte output diversa da knowledge_base_json")

    if len(test) < 3:
        problemi.append("meno di 3 test generati")

    if len(studio) < 3:
        problemi.append("meno di 3 domande studio generate")

    if not qualita.get("ok"):
        problemi.extend(qualita.get("errori", []))

    for index, item in enumerate(test, start=1):
        if not item.get("origine_kb", {}).get("concept_id"):
            problemi.append(f"test {index}: origine concept_id mancante")
        if not item.get("origine_kb", {}).get("chunk_id"):
            problemi.append(f"test {index}: origine chunk_id mancante")
        if item.get("risposta_corretta") not in item.get("opzioni", []):
            problemi.append(f"test {index}: risposta corretta non presente nelle opzioni")
        if len(item.get("opzioni", [])) != 4:
            problemi.append(f"test {index}: numero opzioni diverso da 4")

    for index, item in enumerate(studio, start=1):
        if not item.get("origine_kb", {}).get("concept_id"):
            problemi.append(f"studio {index}: origine concept_id mancante")
        if not item.get("origine_kb", {}).get("chunk_id"):
            problemi.append(f"studio {index}: origine chunk_id mancante")

        domanda = str(item.get("domanda", "")).lower()
        vietate = [
            "spiega il punto principale collegato a",
            "che cosa bisogna ricordare su documento",
            "concetto di documento",
        ]

        for v in vietate:
            if v in domanda:
                problemi.append(f"studio {index}: frase vietata: {v}")

    return problemi


def controlla_hardcoding_generatore() -> list[str]:
    problemi = []
    path = ROOT / "scripts/rag_genera_test_domande_da_kb_v34c.py"
    text = path.read_text(encoding="utf-8", errors="ignore").lower()

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
            problemi.append(f"hardcoding vietato nel generatore: {item}")

    return problemi


def main() -> int:
    INPUTS.mkdir(parents=True, exist_ok=True)
    KBS.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    risultati = []
    errori = []

    for nome, testo in DOCUMENTI_TEST.items():
        input_path = INPUTS / f"{nome}.txt"
        kb_path = KBS / f"{nome}_kb.json"
        outdir = OUTPUTS / nome
        output_path = outdir / "rag_test_domande_studio_da_kb_v34c.json"

        input_path.write_text(testo.strip() + "\n", encoding="utf-8")

        code_kb, log_kb = run([
            "python3",
            "scripts/rag_build_knowledge_base_v34b.py",
            "--input",
            str(input_path),
            "--output",
            str(kb_path),
        ])

        if code_kb != 0:
            risultati.append(f"ERRORE: build KB fallita per {nome}")
            errori.append(f"LOG build KB {nome}:\n{log_kb}")
            continue

        code_gen, log_gen = run([
            "python3",
            "scripts/rag_genera_test_domande_da_kb_v34c.py",
            "--kb",
            str(kb_path),
            "--outdir",
            str(outdir),
            "--numero",
            "4",
        ])

        problemi_output = controlla_output(output_path)

        if code_gen == 0 and not problemi_output:
            risultati.append(f"OK: generatori da KB validi per {nome}")
        else:
            risultati.append(f"ERRORE: generatori da KB non validi per {nome}")
            if log_gen.strip():
                errori.append(f"LOG generatore {nome}:\n{log_gen.strip()}")
            for p in problemi_output:
                errori.append(f"{nome}: {p}")

    problemi_hardcoding = controlla_hardcoding_generatore()

    if problemi_hardcoding:
        risultati.append("ERRORE: hardcoding vietato trovato nel generatore")
        errori.extend(problemi_hardcoding)
    else:
        risultati.append("OK: nessun hardcoding specifico vietato nel generatore")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Generatori RAG da Knowledge Base V3.4C",
        "",
        "Verifica su più documenti. Il generatore deve leggere dalla KB e non da toppe per argomento.",
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

    print("=== VERIFICA GENERATORI RAG DA KB V3.4C ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA RIVEDERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
