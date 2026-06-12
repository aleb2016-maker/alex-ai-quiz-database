import json
from pathlib import Path


PERCORSO_DATABASE = Path("dist/database_quiz_finale.json")
PERCORSO_REPORT = Path("dist/report_qualita_motore.md")


CATEGORIE_MOTORE = {
    "ai",
    "informatica",
    "logica",
}


FRASI_TROPPO_DEBOLI = [
    "cambiare il colore",
    "cambia il colore",
    "cancellare il database",
    "cancella il database",
    "trasformare tutto in immagine",
    "rendere la pagina più colorata",
    "rende impossibile qualunque errore",
    "elimina sempre la necessità",
    "sostituire completamente",
]


def testo_normale(testo):
    return str(testo).strip().lower()


def carica_database():
    if not PERCORSO_DATABASE.exists():
        raise FileNotFoundError(
            "Database finale non trovato. "
            "Esegui prima: python scripts/build_database.py"
        )

    with open(PERCORSO_DATABASE, "r", encoding="utf-8") as file:
        return json.load(file)


def domanda_del_motore(domanda):
    categoria = testo_normale(domanda.get("categoria", ""))
    id_domanda = testo_normale(domanda.get("id", ""))

    if categoria in CATEGORIE_MOTORE:
        return True

    if id_domanda.startswith("log-"):
        return True

    return False


def contiene_frase_debole(opzione):
    opzione_normale = testo_normale(opzione)

    for frase in FRASI_TROPPO_DEBOLI:
        if frase in opzione_normale:
            return True

    return False


def analizza_domanda(domanda):
    problemi_rossi = []
    avvisi_gialli = []

    id_domanda = domanda.get("id", "ID_MANCANTE")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")

    if len(opzioni) != 4:
        problemi_rossi.append("La domanda non ha esattamente 4 opzioni.")
        return problemi_rossi, avvisi_gialli

    opzione_a = opzioni[0]
    opzione_b = opzioni[1]

    domanda_visiva = str(id_domanda).startswith("LOG-VIS")

    # Nelle domande visive le opzioni A/B/C/D possono essere etichette
    # collegate alle immagini. Non le spostiamo automaticamente solo
    # per mettere la risposta corretta in posizione A.
    # Le domande visive avranno un controllo dedicato quando espanderemo
    # la logica visiva.
    if not domanda_visiva:
        if opzione_a != risposta_corretta:
            problemi_rossi.append(
                "La risposta corretta non è in posizione A. "
                "Per lo standard motore, A deve essere la risposta corretta."
            )

        if opzione_b == risposta_corretta:
            problemi_rossi.append(
                "La posizione B non può essere corretta: "
                "B deve essere il distrattore forte."
            )

    for opzione in opzioni:
        if opzione != risposta_corretta and contiene_frase_debole(opzione):
            problemi_rossi.append(
                f"Distrattore troppo debole o assurdo: {opzione}"
            )

    distrattore_forte = domanda.get("distrattore_forte", "")
    motivo_distrattore_forte = domanda.get("motivo_distrattore_forte", "")

    if not distrattore_forte:
        avvisi_gialli.append(
            "Manca il campo 'distrattore_forte'. "
            "Per il motore professionale va indicato esplicitamente."
        )
    else:
        if distrattore_forte not in opzioni:
            problemi_rossi.append(
                "Il campo 'distrattore_forte' non corrisponde a nessuna opzione."
            )

        if distrattore_forte == risposta_corretta:
            problemi_rossi.append(
                "Il campo 'distrattore_forte' coincide con la risposta corretta."
            )

    if not motivo_distrattore_forte:
        avvisi_gialli.append(
            "Manca il campo 'motivo_distrattore_forte'. "
            "Serve per spiegare perché il distrattore forte è quasi giusto ma sbagliato."
        )

    return problemi_rossi, avvisi_gialli


def crea_report(domande):
    domande_motore = [
        domanda
        for domanda in domande
        if domanda_del_motore(domanda)
    ]

    rosse = []
    gialle = []
    ok = []

    for domanda in domande_motore:
        problemi_rossi, avvisi_gialli = analizza_domanda(domanda)

        if problemi_rossi:
            rosse.append((domanda, problemi_rossi, avvisi_gialli))
        elif avvisi_gialli:
            gialle.append((domanda, avvisi_gialli))
        else:
            ok.append(domanda)

    righe = []

    righe.append("# Report qualità motore quiz")
    righe.append("")
    righe.append("Categorie controllate:")
    righe.append("")
    righe.append("- AI")
    righe.append("- Informatica")
    righe.append("- Logica")
    righe.append("")
    righe.append("Significato:")
    righe.append("")
    righe.append("- ROSSO = da sistemare subito")
    righe.append("- GIALLO = da rafforzare per lo standard motore")
    righe.append("- OK MOTORE = già conforme")
    righe.append("")
    righe.append("---")
    righe.append("")
    righe.append("## Riepilogo")
    righe.append("")
    righe.append(f"Domande motore controllate: {len(domande_motore)}")
    righe.append(f"ROSSO - da sistemare subito: {len(rosse)}")
    righe.append(f"GIALLO - da rafforzare: {len(gialle)}")
    righe.append(f"OK MOTORE: {len(ok)}")
    righe.append("")
    righe.append("---")
    righe.append("")

    righe.append("## ROSSO - da sistemare subito")
    righe.append("")

    if not rosse:
        righe.append("Nessuna domanda rossa.")
        righe.append("")

    for domanda, problemi, avvisi in rosse:
        aggiungi_domanda_report(
            righe,
            domanda,
            "ROSSO",
            problemi,
            avvisi
        )

    righe.append("## GIALLO - da rafforzare")
    righe.append("")

    if not gialle:
        righe.append("Nessuna domanda gialla.")
        righe.append("")

    for domanda, avvisi in gialle:
        aggiungi_domanda_report(
            righe,
            domanda,
            "GIALLO",
            avvisi,
            []
        )

    righe.append("## OK MOTORE")
    righe.append("")

    if not ok:
        righe.append("Nessuna domanda è ancora marcata come OK MOTORE.")
        righe.append("")

    for domanda in ok:
        id_domanda = domanda.get("id", "ID_MANCANTE")
        righe.append(f"- {id_domanda}")

    PERCORSO_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PERCORSO_REPORT.write_text(
        "\n".join(righe),
        encoding="utf-8"
    )

    return len(domande_motore), len(rosse), len(gialle), len(ok)


def aggiungi_domanda_report(righe, domanda, stato, problemi, avvisi_extra):
    id_domanda = domanda.get("id", "ID_MANCANTE")
    categoria = domanda.get("categoria", "categoria_mancante")
    livello = domanda.get("livello", "livello_mancante")
    testo_domanda = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")

    righe.append(f"### {id_domanda} - {stato}")
    righe.append("")
    righe.append(f"**Categoria:** {categoria}")
    righe.append("")
    righe.append(f"**Livello:** {livello}")
    righe.append("")
    righe.append(f"**Domanda:** {testo_domanda}")
    righe.append("")
    righe.append("**Opzioni:**")

    lettere = ["A", "B", "C", "D"]

    for indice, opzione in enumerate(opzioni):
        simbolo = "✅" if opzione == risposta_corretta else "❌"
        righe.append(f"- {lettere[indice]}. {simbolo} {opzione}")

    righe.append("")
    righe.append("**Controlli:**")

    for problema in problemi:
        righe.append(f"- {problema}")

    for avviso in avvisi_extra:
        righe.append(f"- {avviso}")

    righe.append("")
    righe.append("---")
    righe.append("")


def main():
    domande = carica_database()

    totale, rosse, gialle, ok = crea_report(domande)

    print("Report qualità motore creato:")
    print(PERCORSO_REPORT)
    print("Domande motore controllate:", totale)
    print("ROSSO - da sistemare subito:", rosse)
    print("GIALLO - da rafforzare:", gialle)
    print("OK MOTORE:", ok)


main()