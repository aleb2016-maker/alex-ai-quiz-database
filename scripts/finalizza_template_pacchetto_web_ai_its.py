from pathlib import Path
import re

TARGET = Path("scripts/create_quiz_package.py")
REPORT = Path("reports/finalizza_template_pacchetto_web_ai_its.md")

def main():
    testo = TARGET.read_text(encoding="utf-8")
    originale = testo

    if "def blinda_interfaccia_web_generata_ai_its(output_dir):" not in testo:
        raise SystemExit("ERRORE: funzione blinda_interfaccia_web_generata_ai_its non trovata.")

    righe = testo.splitlines()
    nuove = []
    inserita = False

    for i, riga in enumerate(righe):
        if "zip_path = output_dir.with_suffix" in riga:
            precedenti = "\n".join(nuove[-8:])

            if "blinda_interfaccia_web_generata_ai_its(output_dir)" not in precedenti:
                indent = re.match(r"^(\s*)", riga).group(1)
                nuove.append(indent + "blinda_interfaccia_web_generata_ai_its(output_dir)")
                inserita = True

        nuove.append(riga)

    testo = "\n".join(nuove) + "\n"
    TARGET.write_text(testo, encoding="utf-8")

    controllo = TARGET.read_text(encoding="utf-8")

    chiamate_reali = [
        line.strip()
        for line in controllo.splitlines()
        if line.strip() == "blinda_interfaccia_web_generata_ai_its(output_dir)"
    ]

    if not chiamate_reali:
        raise SystemExit("ERRORE: chiamata reale alla blindatura non inserita.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join([
            "# Finalizzazione template pacchetto web AI ITS",
            "",
            f"File controllato: `{TARGET}`",
            "",
            f"Chiamata inserita ora: {inserita}",
            f"Chiamate reali trovate: {len(chiamate_reali)}",
            f"File modificato: {testo != originale}",
            "",
            "Esito: OK. La funzione di blindatura viene chiamata prima della creazione dello ZIP.",
            "",
        ]),
        encoding="utf-8",
    )

    print("===== FINALIZZAZIONE TEMPLATE WEB AI ITS =====")
    print(f"Chiamata inserita ora: {inserita}")
    print(f"Chiamate reali trovate: {len(chiamate_reali)}")
    print(f"File modificato: {testo != originale}")
    print(f"Report: {REPORT}")
    print("OK: la blindatura viene chiamata prima della creazione dello ZIP.")

if __name__ == "__main__":
    main()
