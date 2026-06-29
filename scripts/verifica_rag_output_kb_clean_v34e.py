#!/usr/bin/env python3
"""
Verifica generatore output da KB pulita V3.4E.
Controlla riassunto, card, test e domande studio su più documenti.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/generated/rag_output_kb_clean_v34e"
INPUTS = BASE / "inputs"
KBS = BASE / "kb"
OUTPUTS = BASE / "outputs"
REPORT = ROOT / "reports/rag_output_kb_clean_v34e.md"

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

VIETATI = [
    "concept_id",
    "chunk_id",
    "origine_kb",
    "tracciabilita",
    "secondo la knowledge base",
    "risposta corretta:",
    "la risposta corretta è",
    "distrattore",
    "esempio di domanda",
    "rag/documenti",
    "scopo del documento",
    "questo documento è stato creato",
    "fonte di prova",
    "motore rag",
    "progetto quiz",
    "# documento",
    "perché «",
    "è importante nel documento",
    "che rapporto c",
]

TITOLI_BRUTTI = [
    "la sicurezza informatica è l'insieme",
    "una buona regola aziendale è attivare",
    "bisogna mantenere aggiornati anche",
    "stessa password siti rischioso",
    "mantenere aggiornati anche browser",
    "riduce rischio account venga",
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def titoli_visibili(data: dict) -> list[str]:
    titles = []

    for card in data.get("card", []):
        titles.append(str(card.get("titolo", "")))

    for test in data.get("test", []):
        titles.extend(re.findall(r"«([^»]+)»", str(test.get("domanda", ""))))

    for studio in data.get("domande_studio", []):
        titles.extend(re.findall(r"«([^»]+)»", str(studio.get("domanda", ""))))

    return titles


def campi_visibili(data: dict) -> list[str]:
    fields = []

    riassunto = data.get("riassunto", {})
    fields.append(str(riassunto.get("titolo", "")))
    fields.append(str(riassunto.get("testo_breve", "")))
    fields.append(str(riassunto.get("conclusione", "")))

    for p in riassunto.get("punti_chiave", []):
        fields.append(str(p.get("titolo", "")))
        fields.append(str(p.get("testo", "")))

    for card in data.get("card", []):
        fields.append(str(card.get("titolo", "")))
        fields.append(str(card.get("testo", "")))
        fields.append(str(card.get("messaggio_chiave", "")))
        fields.append(str(card.get("fonte_visibile", "")))

    for test in data.get("test", []):
        fields.append(str(test.get("domanda", "")))
        fields.extend(str(x) for x in test.get("opzioni", []))
        fields.append(str(test.get("spiegazione", "")))
        fields.append(str(test.get("fonte_visibile", "")))

    for studio in data.get("domande_studio", []):
        fields.append(str(studio.get("domanda", "")))
        fields.append(str(studio.get("risposta_guida", "")))
        fields.append(str(studio.get("fonte_visibile", "")))

    return fields


def controlla_output(path: Path) -> list[str]:
    problemi = []

    if not path.exists():
        return [f"output mancante: {path}"]

    data = json.loads(path.read_text(encoding="utf-8"))
    q = data.get("controlli_qualita", {})

    if not q.get("ok"):
        problemi.extend(q.get("errori", []))

    if data.get("fonte") != "knowledge_base_clean_v34d":
        problemi.append("fonte non corretta")

    if not data.get("riassunto", {}).get("testo_breve"):
        problemi.append("riassunto assente")

    if len(data.get("card", [])) < 3:
        problemi.append("card insufficienti")

    if len(data.get("test", [])) < 3:
        problemi.append("test insufficienti")

    if len(data.get("domande_studio", [])) < 3:
        problemi.append("domande studio insufficienti")

    # Lo stesso titolo può comparire correttamente in card, test e domande studio.
    # Il duplicato è un problema solo se si ripete dentro la stessa sezione.
    card_titles = [str(c.get("titolo", "")).lower() for c in data.get("card", [])]
    if len(card_titles) != len(set(card_titles)):
        problemi.append("titoli card duplicati")

    test_titles = []
    for test in data.get("test", []):
        test_titles.extend(re.findall(r"«([^»]+)»", str(test.get("domanda", ""))))
    test_titles = [t.lower() for t in test_titles]
    if len(test_titles) != len(set(test_titles)):
        problemi.append("titoli test duplicati")

    studio_titles = []
    for studio in data.get("domande_studio", []):
        studio_titles.extend(re.findall(r"«([^»]+)»", str(studio.get("domanda", ""))))
    studio_titles = [t.lower() for t in studio_titles]
    if len(studio_titles) != len(set(studio_titles)):
        problemi.append("titoli domande studio duplicati")

    titles = titoli_visibili(data)

    for title in titles:
        low_title = title.lower()

        if len(title) > 52 or len(title.split()) > 6:
            problemi.append(f"titolo visibile troppo lungo: {title}")

        for banned in TITOLI_BRUTTI:
            if banned in low_title:
                problemi.append(f"titolo visibile brutto: {banned}")

    for field in campi_visibili(data):
        low = field.lower()

        if len(field.strip()) < 8:
            problemi.append("testo visibile troppo corto")

        for banned in VIETATI:
            if banned in low:
                problemi.append(f"testo visibile contiene vietato: {banned}")

        if ". garantire" in low or ". mantenere" in low:
            problemi.append("punteggiatura lista spezzata male")

    for index, item in enumerate(data.get("test", []), start=1):
        opzioni = item.get("opzioni", [])
        corretta = item.get("risposta_corretta")

        if len(opzioni) != 4:
            problemi.append(f"test {index}: opzioni diverse da 4")

        if corretta not in opzioni:
            problemi.append(f"test {index}: corretta assente dalle opzioni")

        if len(set(opzioni)) != len(opzioni):
            problemi.append(f"test {index}: opzioni duplicate")

    return problemi


def controlla_hardcoding() -> list[str]:
    problemi = []
    text = (ROOT / "scripts/rag_genera_output_da_kb_clean_v34e.py").read_text(encoding="utf-8", errors="ignore").lower()

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


def esegui_documento(nome: str, input_path: Path, risultati: list[str], errori: list[str], numero: str = "4") -> None:
    kb_path = KBS / f"{nome}_kb.json"
    outdir = OUTPUTS / nome
    output_path = outdir / "rag_output_kb_clean_v34e.json"

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
        errori.append(log_kb)
        return

    code_gen, log_gen = run([
        "python3",
        "scripts/rag_genera_output_da_kb_clean_v34e.py",
        "--kb",
        str(kb_path),
        "--outdir",
        str(outdir),
        "--numero",
        numero,
    ])

    problemi = controlla_output(output_path)

    if code_gen == 0 and not problemi:
        risultati.append(f"OK: output V3.4E valido per {nome}")
    else:
        risultati.append(f"ERRORE: output V3.4E non valido per {nome}")
        if log_gen.strip():
            errori.append(f"LOG {nome}:\n{log_gen.strip()}")
        for p in problemi:
            errori.append(f"{nome}: {p}")


def main() -> int:
    INPUTS.mkdir(parents=True, exist_ok=True)
    KBS.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    risultati = []
    errori = []

    for nome, testo in DOCUMENTI.items():
        input_path = INPUTS / f"{nome}.txt"
        input_path.write_text(testo.strip() + "\n", encoding="utf-8")
        esegui_documento(nome, input_path, risultati, errori, "4")

    real_input = ROOT / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    if real_input.exists():
        esegui_documento("sicurezza_reale", real_input, risultati, errori, "5")

    problemi_hardcoding = controlla_hardcoding()

    if problemi_hardcoding:
        risultati.append("ERRORE: hardcoding specifico trovato nel generatore")
        errori.extend(problemi_hardcoding)
    else:
        risultati.append("OK: nessun hardcoding specifico vietato nel generatore")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Output RAG da KB pulita V3.4E",
        "",
        "Verifica generazione riassunto, card, test e domande studio da Knowledge Base pulita V3.4D.",
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

    print("=== VERIFICA OUTPUT RAG DA KB CLEAN V3.4E ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA RIVEDERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
