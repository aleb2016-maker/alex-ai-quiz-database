import json
from pathlib import Path


# Questo script controlla tutte le domande del database finale
# e crea un report leggibile per revisionare la qualità delle 4 risposte.
#
# Obiettivo:
# - evitare risposte sbagliate troppo assurde
# - evitare che la risposta corretta si capisca per esclusione
# - controllare se i distrattori sono concettualmente plausibili
#
# Output:
# dist/report_revisione_risposte.md


PERCORSO_DATABASE = Path("dist/database_quiz_finale.json")
PERCORSO_REPORT = Path("dist/report_revisione_risposte.md")


PAROLE_TROPPO_ASSURDE = [
    "banana",
    "bicicletta",
    "telefono",
    "password",
    "cavo di rete",
    "colore dello schermo",
    "ventola",
    "immagine compressa",
    "videogioco",
    "file audio",
    "lavare",
    "friggere",
    "macchina",
    "pubblicità",
    "batteria",
    "monitor",
    "uovo",
    "automobile"
]


def carica_database():
    with open(PERCORSO_DATABASE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalizza_testo(testo):
    return testo.lower().strip()


def trova_opzioni_sospette(domanda):
    opzioni_sospette = []

    risposta_corretta = normalizza_testo(domanda["risposta_corretta"])

    for opzione in domanda["opzioni"]:
        opzione_normale = normalizza_testo(opzione)

        if opzione_normale == risposta_corretta:
            continue

        for parola in PAROLE_TROPPO_ASSURDE:
            if parola in opzione_normale:
                opzioni_sospette.append(opzione)
                break

    return opzioni_sospette


def valuta_domanda(domanda):
    opzioni = domanda["opzioni"]
    risposta_corretta = domanda["risposta_corretta"]
    opzioni_sospette = trova_opzioni_sospette(domanda)

    problemi = []

    if len(opzioni) != 4:
        problemi.append("La domanda non ha 4 opzioni.")

    if risposta_corretta not in opzioni:
        problemi.append("La risposta corretta non è presente tra le opzioni.")

    if len(set(opzioni)) != len(opzioni):
        problemi.append("Ci sono opzioni duplicate.")

    if opzioni_sospette:
        problemi.append(
            "Possibili distrattori troppo deboli o concettualmente lontani: "
            + ", ".join(opzioni_sospette)
        )

    return problemi


def crea_report(domande):
    righe = []

    righe.append("# Report revisione risposte")
    righe.append("")
    righe.append(
        "Questo report serve a controllare se le 4 risposte sono davvero "
        "plausibili oppure se la risposta corretta si capisce troppo facilmente."
    )
    righe.append("")
    righe.append(f"Domande controllate: {len(domande)}")
    righe.append("")

    domande_con_problemi = 0

    categorie = sorted(set(domanda["categoria"] for domanda in domande))

    for categoria in categorie:
        righe.append(f"## Categoria: {categoria}")
        righe.append("")

        domande_categoria = [
            domanda for domanda in domande
            if domanda["categoria"] == categoria
        ]

        domande_categoria.sort(
            key=lambda domanda: (
                domanda.get("livello", ""),
                domanda.get("id", "")
            )
        )

        for domanda in domande_categoria:
            problemi = valuta_domanda(domanda)

            if problemi:
                domande_con_problemi += 1
                stato = "DA RIVEDERE"
            else:
                stato = "OK DA CONTROLLARE A OCCHIO"
            
            righe.append(f"### {domanda['id']} - {stato}")
            righe.append("")
            righe.append(f"**Livello:** {domanda.get('livello', '')}")
            righe.append("")
            righe.append(f"**Domanda:** {domanda['domanda']}")
            righe.append("")
            righe.append("**Opzioni:**")

            for opzione in domanda["opzioni"]:
                if opzione == domanda["risposta_corretta"]:
                    righe.append(f"- ✅ {opzione}")
                else:
                    righe.append(f"- ❌ {opzione}")

            righe.append("")
            righe.append(f"**Spiegazione:** {domanda.get('spiegazione', '')}")
            righe.append("")

            if problemi:
                righe.append("**Problemi trovati automaticamente:**")
                for problema in problemi:
                    righe.append(f"- {problema}")
                righe.append("")
            else:
                righe.append(
                    "**Nota:** nessun problema tecnico automatico, "
                    "ma va comunque controllata la somiglianza concettuale delle risposte."
                )
                righe.append("")

            righe.append("---")
            righe.append("")

    righe.insert(
        5,
        f"Domande segnalate automaticamente: {domande_con_problemi}"
    )
    righe.insert(6, "")

    return "\n".join(righe)


def main():
    domande = carica_database()
    report = crea_report(domande)

    PERCORSO_REPORT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_REPORT, "w", encoding="utf-8") as file:
        file.write(report)

    print("Report creato correttamente:")
    print(PERCORSO_REPORT)
    print(f"Domande controllate: {len(domande)}")


main()