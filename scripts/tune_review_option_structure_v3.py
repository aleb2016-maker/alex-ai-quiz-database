from pathlib import Path


PERCORSO_SCRIPT = Path("scripts/review_option_structure.py")


vecchio_blocco = '''    id_domanda = domanda.get("id", "ID_MANCANTE")
    testo_domanda = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")

    if len(opzioni) != 4:
        problemi.append("La domanda non ha esattamente 4 opzioni.")
        return problemi

    opzione_a = opzioni[0]
'''


nuovo_blocco = '''    id_domanda = domanda.get("id", "ID_MANCANTE")
    categoria = domanda.get("categoria", "")
    testo_domanda = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")

    if len(opzioni) != 4:
        problemi.append("La domanda non ha esattamente 4 opzioni.")
        return problemi

    # Per la matematica non applichiamo il controllo A/B/C/D forte.
    # Le risposte numeriche vicine sono spesso già valide anche se non sono ordinate
    # esattamente come A corretta, B più vicina, C e D vicine tra loro.
    # La matematica resta controllata dagli altri script:
    # validazione, duplicati, somiglianze e opzioni duplicate.
    if categoria == "matematica":
        return problemi

    opzione_a = opzioni[0]
'''


def main():
    contenuto = PERCORSO_SCRIPT.read_text(encoding="utf-8")

    if vecchio_blocco not in contenuto:
        print("Blocco da sostituire non trovato.")
        print("Forse la V3 è già stata applicata oppure il file è cambiato.")
        return

    nuovo_contenuto = contenuto.replace(
        vecchio_blocco,
        nuovo_blocco
    )

    PERCORSO_SCRIPT.write_text(
        nuovo_contenuto,
        encoding="utf-8"
    )

    print("Controllo struttura opzioni aggiornato alla versione V3.")
    print("Matematica esclusa dal controllo A/B/C/D forte.")
    print("File modificato:")
    print(PERCORSO_SCRIPT)


main()