from pathlib import Path
import re
import sys

report_generale = Path("reports/motore_qualita_generale.md")
report_visivo = Path("reports/motore_qualita_logica_visiva.md")

problemi = []

def controlla_report(path, pattern):
    if not path.exists():
        problemi.append(f"Report mancante: {path}")
        return

    testo = path.read_text(encoding="utf-8")

    for nome, regex in pattern:
        trovati = re.findall(regex, testo)
        for valore in trovati:
            numero = int(valore)
            if numero > 0:
                problemi.append(f"{path}: {nome} = {numero}")

controlla_report(
    report_generale,
    [
        ("Problemi tecnici", r"Problemi tecnici:\s+\*\*(\d+)\*\*"),
        ("Avvisi qualità reali", r"Avvisi qualità reali:\s+\*\*(\d+)\*\*"),
        ("Errori linguistici", r"Errori linguistici:\s+\*\*(\d+)\*\*"),
        ("Duplicati identici", r"Duplicati identici:\s+\*\*(\d+)\*\*"),
        ("Domande molto simili", r"Domande molto simili:\s+\*\*(\d+)\*\*"),
    ],
)

controlla_report(
    report_visivo,
    [
        ("Problemi tecnici", r"Problemi tecnici:\s+\*\*(\d+)\*\*"),
        ("Avvisi qualità", r"Avvisi qualità:\s+\*\*(\d+)\*\*"),
        ("Errori linguistici", r"Errori linguistici:\s+\*\*(\d+)\*\*"),
        ("Immagini mancanti", r"Immagini mancanti:\s+\*\*(\d+)\*\*"),
    ],
)

if problemi:
    print("CONTROLLO EXTRA: report NON puliti.")
    for problema in problemi:
        print("-", problema)
    sys.exit(1)

print("CONTROLLO EXTRA: report puliti, nessun problema reale trovato.")
