import re
from collections import Counter
from pathlib import Path


PERCORSO_REPORT = Path("dist/report_qualita_motore.md")


def main():
    testo = PERCORSO_REPORT.read_text(encoding="utf-8")

    blocco_giallo = testo.split("## GIALLO - da rafforzare", 1)[1]
    blocco_giallo = blocco_giallo.split("## OK MOTORE", 1)[0]

    categorie = re.findall(r"\*\*Categoria:\*\* ([^\n]+)", blocco_giallo)
    conteggio = Counter(categorie)

    print("----- GIALLE PER CATEGORIA -----")

    for categoria, totale in sorted(conteggio.items()):
        print(f"{categoria}: {totale}")


main()