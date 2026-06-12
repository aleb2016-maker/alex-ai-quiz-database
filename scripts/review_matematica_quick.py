import json
import re
from pathlib import Path
from collections import Counter


DATA_DIR = Path("data")
DIST_DIR = Path("dist")
REPORT_PATH = DIST_DIR / "report_matematica_veloce.md"


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
    return str(testo).strip().lower()


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


def contiene_numero(testo):
    return bool(re.search(r"\d", str(testo)))


def contiene_operatore_matematico(testo):
    testo = str(testo)

    simboli = ["+", "-", "×", "*", "÷", "/", "=", "%", "^"]

    return any(simbolo in testo for simbolo in simboli)


def sembra_domanda_numerica(domanda):
    testo_domanda = domanda.get("domanda", "")
    spiegazione = domanda.get("spiegazione", "")
    risposta = domanda.get("risposta_corretta", "")

    testo_totale = f"{testo_domanda} {spiegazione} {risposta}".lower()

    parole_chiave = [
        "calcola",
        "equazione",
        "risolvi",
        "percentuale",
        "media",
        "successione",
        "serie",
        "valore",
        "risultato",
        "numero",
        "somma",
        "differenza",
        "prodotto",
        "divisione",
    ]

    if any(parola in testo_totale for parola in parole_chiave):
        return True

    if contiene_numero(testo_totale):
        return True

    if contiene_operatore_matematico(testo_totale):
        return True

    return False


def raccogli_domande_matematica():
    domande_matematica = []

    for percorso in DATA_DIR.rglob("*.json"):
        dati = carica_json(percorso)
        liste_domande = trova_liste_domande(dati)

        for lista_domande in liste_domande:
            for domanda in lista_domande:
                if not isinstance(domanda, dict):
                    continue

                categoria = normalizza_testo(domanda.get("categoria", ""))

                if categoria == "matematica":
                    domande_matematica.append((percorso, domanda))

    return domande_matematica


def controlla_domanda(percorso, domanda):
    problemi = []
    avvisi = []

    id_domanda = domanda.get("id", "ID_MANCANTE")
    livello = domanda.get("livello", "livello_mancante")
    testo_domanda = domanda.get("domanda", "")
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

    if sembra_domanda_numerica(domanda):
        risposta_senza_spazi = risposta.replace(" ", "")
        spiegazione_senza_spazi = spiegazione.replace(" ", "")

        if risposta and risposta_senza_spazi not in spiegazione_senza_spazi:
            avvisi.append(
                "La risposta corretta non compare chiaramente nella spiegazione"
            )

    if len(spiegazione) < 40:
        avvisi.append("Spiegazione molto breve")

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

    righe.append("# Report veloce matematica")
    righe.append("")
    righe.append(f"Domande matematica controllate: {totale}")
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

    domande_matematica = raccogli_domande_matematica()
    risultati = []
    conteggio_livelli = Counter()

    for percorso, domanda in domande_matematica:
        livello = domanda.get("livello", "livello_mancante")
        conteggio_livelli[livello] += 1

        risultato = controlla_domanda(percorso, domanda)
        risultati.append(risultato)

    report = crea_report(risultati, conteggio_livelli)
    REPORT_PATH.write_text(report, encoding="utf-8")

    totale_problemi = sum(1 for r in risultati if r["problemi"])
    totale_avvisi = sum(1 for r in risultati if r["avvisi"])

    print("----- CONTROLLO VELOCE MATEMATICA -----")
    print("Domande matematica controllate:", len(risultati))
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