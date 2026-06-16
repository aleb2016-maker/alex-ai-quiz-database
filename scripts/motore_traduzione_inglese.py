from pathlib import Path
import json
import re


FILE_INGLESE = Path("data/inglese.json")
FILE_TRADUZIONI = Path("data/traduzioni/inglese_it_approvate.json")
REPORT_FILE = Path("reports/traduzioni_inglese.md")


def leggi_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def scrivi_json(path, dati):
    path.write_text(
        json.dumps(dati, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


def pulisci_testo(testo):
    testo = str(testo or "")
    testo = testo.replace("\n", " ")
    testo = re.sub(r"\s+", " ", testo)
    testo = re.sub(r"\s+([,.;:!?])", r"\1", testo)
    testo = re.sub(r"([,;:!?])([^\s])", r"\1 \2", testo)
    testo = re.sub(r"(?<!\d)\.([^\s\d])", r". \1", testo)
    testo = re.sub(r" {2,}", " ", testo)
    return testo.strip()


def rimuovi_vecchie_traduzioni(spiegazione):
    spiegazione = pulisci_testo(spiegazione)

    spiegazione = re.sub(
        r'\s*Traduzione in italiano della risposta corretta:\s*".*?"\.?',
        "",
        spiegazione
    )

    spiegazione = re.sub(
        r'\s*Traduzione domanda:\s*".*?"\.?',
        "",
        spiegazione
    )

    spiegazione = re.sub(
        r'\s*Traduzione risposta:\s*".*?"\.?',
        "",
        spiegazione
    )

    return pulisci_testo(spiegazione)


def aggiorna_spiegazione(spiegazione, traduzione_domanda, traduzione_risposta):
    base = rimuovi_vecchie_traduzioni(spiegazione)

    riga_domanda = f'Traduzione domanda: "{traduzione_domanda}"'
    riga_risposta = f'Traduzione risposta: "{traduzione_risposta}"'

    if base:
        return f"{base} {riga_domanda} {riga_risposta}"

    return f"{riga_domanda} {riga_risposta}"


def main():
    if not FILE_INGLESE.exists():
        raise SystemExit(f"File non trovato: {FILE_INGLESE}")

    if not FILE_TRADUZIONI.exists():
        raise SystemExit(f"File traduzioni non trovato: {FILE_TRADUZIONI}")

    domande = leggi_json(FILE_INGLESE)
    traduzioni = leggi_json(FILE_TRADUZIONI)

    problemi = []
    righe_report = ["# Report motore traduzione inglese", ""]

    inglese = [
        domanda
        for domanda in domande
        if str(domanda.get("categoria", "")).lower() == "inglese"
    ]

    if len(inglese) != 40:
        problemi.append(f"Attese 40 domande inglesi, trovate {len(inglese)}")

    for domanda in inglese:
        id_domanda = domanda.get("id")
        domanda_originale = domanda.get("domanda", "")
        voce = traduzioni.get(id_domanda)

        if not voce:
            problemi.append(f"{id_domanda}: manca voce nel file traduzioni")
            continue

        traduzione_domanda = pulisci_testo(voce.get("traduzione_domanda", ""))
        traduzione_risposta = pulisci_testo(voce.get("traduzione_risposta", ""))

        if not traduzione_domanda:
            problemi.append(f"{id_domanda}: manca traduzione_domanda")

        if not traduzione_risposta:
            problemi.append(f"{id_domanda}: manca traduzione_risposta")

        if domanda_originale.count("___") != traduzione_domanda.count("___"):
            problemi.append(
                f"{id_domanda}: numero di ___ diverso tra domanda originale e traduzione"
            )

        if ". .." in traduzione_domanda or ". .." in traduzione_risposta:
            problemi.append(f"{id_domanda}: traduzione contiene '. ..'")

    if problemi:
        print("ERRORE: traduzioni non approvate o non valide")
        for problema in problemi:
            print("-", problema)
        raise SystemExit(1)

    for domanda in inglese:
        id_domanda = domanda["id"]
        voce = traduzioni[id_domanda]

        traduzione_domanda = pulisci_testo(voce["traduzione_domanda"])
        traduzione_risposta = pulisci_testo(voce["traduzione_risposta"])

        domanda["traduzione_italiana_domanda"] = traduzione_domanda
        domanda["traduzione_italiana_risposta_corretta"] = traduzione_risposta

        domanda["spiegazione"] = aggiorna_spiegazione(
            domanda.get("spiegazione", ""),
            traduzione_domanda,
            traduzione_risposta
        )

        righe_report.append(f"## {id_domanda}")
        righe_report.append("")
        righe_report.append(f"- Domanda originale: `{domanda.get('domanda', '')}`")
        righe_report.append(f"- Traduzione domanda: `{traduzione_domanda}`")
        righe_report.append(f"- Risposta corretta: `{domanda.get('risposta_corretta', '')}`")
        righe_report.append(f"- Traduzione risposta: `{traduzione_risposta}`")
        righe_report.append("")

    scrivi_json(FILE_INGLESE, domande)
    REPORT_FILE.write_text("\n".join(righe_report) + "\n", encoding="utf-8")

    print("OK: traduzioni approvate applicate.")
    print("File aggiornato:", FILE_INGLESE)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
    main()
