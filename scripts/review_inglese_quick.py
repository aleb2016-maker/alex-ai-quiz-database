import json
from pathlib import Path
from collections import Counter


DATA_DIR = Path("data")
DIST_DIR = Path("dist")
REPORT_PATH = DIST_DIR / "report_inglese_veloce.md"


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def trova_liste_domande(dati):
    liste = []

    if isinstance(dati, list):
        liste.append(dati)

    elif isinstance(dati, dict):
        for valore in dati.values():
            if isinstance(valore, list):
                liste.append(valore)

    return liste


def normalizza_testo(testo):
    testo = str(testo).strip().lower()
    testo = " ".join(testo.split())
    return testo


def estrai_opzioni(domanda):
    opzioni = domanda.get("opzioni", [])

    if not isinstance(opzioni, list):
        return []

    opzioni_pulite = []

    for opzione in opzioni:
        if isinstance(opzione, str):
            opzioni_pulite.append(opzione.strip())

        elif isinstance(opzione, dict):
            testo = (
                opzione.get("testo")
                or opzione.get("text")
                or opzione.get("answer")
                or ""
            )
            opzioni_pulite.append(str(testo).strip())

    return opzioni_pulite


def raccogli_domande_inglese():
    domande_inglese = []

    for percorso in DATA_DIR.rglob("*.json"):
        dati = carica_json(percorso)
        liste_domande = trova_liste_domande(dati)

        for lista_domande in liste_domande:
            for domanda in lista_domande:
                if not isinstance(domanda, dict):
                    continue

                categoria = normalizza_testo(domanda.get("categoria", ""))

                if categoria == "inglese":
                    domande_inglese.append((percorso, domanda))

    return domande_inglese


def risposta_corta_accettata(risposta):
    risposte_corte_accettate = {
        "i",
        "a",
    }

    risposta_normalizzata = normalizza_testo(risposta)

    return risposta_normalizzata in risposte_corte_accettate


def controlla_domanda(percorso, domanda):
    problemi = []
    avvisi = []

    id_domanda = domanda.get("id", "ID_MANCANTE")
    livello = domanda.get("livello", "livello_mancante")
    testo_domanda = str(domanda.get("domanda", "")).strip()
    risposta = str(domanda.get("risposta_corretta", "")).strip()
    spiegazione = str(domanda.get("spiegazione", "")).strip()
    opzioni = estrai_opzioni(domanda)

    if not id_domanda:
        problemi.append("ID mancante")

    if not testo_domanda:
        problemi.append("Testo domanda mancante")

    if not risposta:
        problemi.append("Risposta corretta mancante")

    if not spiegazione:
        problemi.append("Spiegazione mancante")

    if len(opzioni) != 4:
        problemi.append(f"Numero opzioni diverso da 4: {len(opzioni)}")

    opzioni_normalizzate = [normalizza_testo(opzione) for opzione in opzioni]

    if len(opzioni_normalizzate) != len(set(opzioni_normalizzate)):
        problemi.append("Opzioni duplicate nella stessa domanda")

    if risposta and normalizza_testo(risposta) not in opzioni_normalizzate:
        problemi.append("Risposta corretta non presente tra le opzioni")

    if len(spiegazione) < 35:
        avvisi.append("Spiegazione molto breve")

    if len(testo_domanda) < 15:
        avvisi.append("Domanda molto breve")

    if risposta and len(risposta) <= 1:
        if not risposta_corta_accettata(risposta):
            avvisi.append("Risposta corretta molto corta: controllare se è voluto")

    return {
        "id": id_domanda,
        "livello": livello,
        "file": str(percorso),
        "domanda": testo_domanda,
        "problemi": problemi,
        "avvisi": avvisi,
    }


def crea_report(risultati, conteggio_livelli):
    righe = []

    totale = len(risultati)
    totale_problemi = sum(1 for r in risultati if r["problemi"])
    totale_avvisi = sum(1 for r in risultati if r["avvisi"])

    righe.append("# Report veloce inglese")
    righe.append("")
    righe.append(f"Domande inglese controllate: {totale}")
    righe.append(f"Domande con problemi gravi: {totale_problemi}")
    righe.append(f"Domande con avvisi: {totale_avvisi}")
    righe.append("")
    righe.append("## Distribuzione livelli")
    righe.append("")

    for livello, totale_livello in sorted(conteggio_livelli.items()):
        righe.append(f"- {livello}: {totale_livello}")

    righe.append("")
    righe.append("## Problemi gravi")
    righe.append("")

    problemi_presenti = False

    for risultato in risultati:
        if risultato["problemi"]:
            problemi_presenti = True
            righe.append(f"### {risultato['id']}")
            righe.append("")
            righe.append(f"File: `{risultato['file']}`")
            righe.append("")
            righe.append(f"Domanda: {risultato['domanda']}")
            righe.append("")

            for problema in risultato["problemi"]:
                righe.append(f"- {problema}")

            righe.append("")

    if not problemi_presenti:
        righe.append("Nessun problema grave trovato.")
        righe.append("")

    righe.append("## Avvisi da controllare velocemente")
    righe.append("")

    avvisi_presenti = False

    for risultato in risultati:
        if risultato["avvisi"] and not risultato["problemi"]:
            avvisi_presenti = True
            righe.append(f"### {risultato['id']}")
            righe.append("")
            righe.append(f"File: `{risultato['file']}`")
            righe.append("")
            righe.append(f"Domanda: {risultato['domanda']}")
            righe.append("")

            for avviso in risultato["avvisi"]:
                righe.append(f"- {avviso}")

            righe.append("")

    if not avvisi_presenti:
        righe.append("Nessun avviso trovato.")
        righe.append("")

    return "\n".join(righe)


def main():
    DIST_DIR.mkdir(exist_ok=True)

    domande_inglese = raccogli_domande_inglese()
    risultati = []
    conteggio_livelli = Counter()

    for percorso, domanda in domande_inglese:
        livello = domanda.get("livello", "livello_mancante")
        conteggio_livelli[livello] += 1

        risultato = controlla_domanda(percorso, domanda)
        risultati.append(risultato)

    report = crea_report(risultati, conteggio_livelli)
    REPORT_PATH.write_text(report, encoding="utf-8")

    totale_problemi = sum(1 for r in risultati if r["problemi"])
    totale_avvisi = sum(1 for r in risultati if r["avvisi"])

    print("----- CONTROLLO VELOCE INGLESE -----")
    print("Domande inglese controllate:", len(risultati))
    print("Problemi gravi:", totale_problemi)
    print("Avvisi:", totale_avvisi)
    print("Report creato in:", REPORT_PATH)

    if totale_problemi == 0:
        print("")
        print("Risultato: nessun problema grave trovato.")
    else:
        print("")
        print("ATTENZIONE: ci sono problemi gravi da correggere.")


main()