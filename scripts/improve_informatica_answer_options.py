import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI_INFORMATICA = {
    "INF-AV-0003": {
        "opzioni": [
            "Permettere a frontend e backend di comunicare tramite richieste HTTP strutturate",
            "Permettere al frontend di leggere direttamente le tabelle del database",
            "Usare una singola pagina HTML come unico punto di elaborazione dei dati",
            "Sostituire la logica del backend con chiamate dirette dal browser"
        ],
        "risposta_corretta": "Permettere a frontend e backend di comunicare tramite richieste HTTP strutturate",
        "spiegazione": (
            "Un'API REST permette a frontend e backend di comunicare tramite richieste HTTP organizzate. "
            "Il frontend non dovrebbe leggere direttamente il database: passa dal backend, che espone endpoint controllati."
        )
    },

    "INF-AV-0004": {
        "opzioni": [
            "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
            "Perché il frontend può gestire solo la grafica mentre il backend espone dati e logica tramite API",
            "Perché il backend può cambiare alcune regole senza riscrivere tutta l'interfaccia",
            "Perché il frontend può consumare servizi diversi senza conoscere i dettagli interni del server"
        ],
        "risposta_corretta": "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
        "spiegazione": (
            "Separare frontend e backend rende il progetto più gestibile perché divide le responsabilità: "
            "interfaccia utente, logica applicativa e gestione dei dati possono evolvere in modo più ordinato. "
            "Le altre opzioni descrivono vantaggi specifici, ma la risposta corretta è quella più generale."
        )
    },

    "INF-AV-0006": {
        "opzioni": [
            "Rendere più veloci alcune ricerche su quella colonna",
            "Ridurre il numero di righe da salvare nella tabella",
            "Normalizzare automaticamente i dati duplicati",
            "Sostituire la progettazione delle relazioni tra tabelle"
        ],
        "risposta_corretta": "Rendere più veloci alcune ricerche su quella colonna",
        "spiegazione": (
            "Un indice aiuta il database a trovare più velocemente i record su certe colonne. "
            "Non riduce automaticamente le righe, non normalizza i dati e non sostituisce la progettazione corretta delle tabelle."
        )
    },

    "INF-AV-0007": {
        "opzioni": [
            "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
            "Perché possono leggere o modificare lo stesso dato nello stesso intervallo di tempo",
            "Perché possono richiedere transazioni o meccanismi di isolamento adeguati",
            "Perché possono causare aggiornamenti persi se due modifiche si sovrappongono"
        ],
        "risposta_corretta": "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
        "spiegazione": (
            "Due operazioni simultanee sullo stesso dato possono creare stati incoerenti, aggiornamenti persi o conflitti. "
            "Le altre opzioni descrivono casi specifici del problema, mentre la risposta corretta riassume il rischio principale."
        )
    },

    "INF-AV-0008": {
        "opzioni": [
            "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
            "Perché il test deve confrontare output reale e output previsto",
            "Perché il test deve verificare una condizione precisa e ripetibile",
            "Perché il test deve fallire quando il codice non rispetta il comportamento atteso"
        ],
        "risposta_corretta": "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
        "spiegazione": (
            "Un test automatico utile deve sapere cosa aspettarsi. "
            "Se il risultato atteso è chiaro, il test può confrontarlo con il risultato reale e dire se il comportamento è corretto. "
            "Le altre opzioni sono aspetti collegati, ma la risposta corretta è la formulazione più completa."
        )
    },

    "INF-AV-0009": {
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Permette di cambiare valori come URL o chiavi senza modificare i file del codice",
            "Permette di usare configurazioni diverse tra sviluppo, test e produzione",
            "Permette di evitare che credenziali e impostazioni vengano scritte direttamente nel repository"
        ],
        "risposta_corretta": "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
        "spiegazione": (
            "Le variabili d'ambiente servono soprattutto a separare configurazioni sensibili o variabili dal codice sorgente. "
            "Cambiare URL, distinguere ambienti ed evitare credenziali nel repository sono vantaggi collegati, "
            "ma la risposta corretta è quella più generale."
        )
    },

    "INF-FAC-0001": {
        "opzioni": [
            "Conservare temporaneamente i dati usati dai programmi in esecuzione",
            "Archiviare stabilmente file e programmi anche a computer spento",
            "Conservare dati molto usati dentro la CPU per accessi rapidissimi",
            "Memorizzare dati grafici usati principalmente dalla scheda video"
        ],
        "risposta_corretta": "Conservare temporaneamente i dati usati dai programmi in esecuzione",
        "spiegazione": (
            "La RAM conserva temporaneamente i dati dei programmi in esecuzione. "
            "L'archiviazione permanente è compito di SSD o hard disk, la cache è più vicina alla CPU, "
            "mentre la memoria video è legata alla scheda grafica."
        )
    },

    "INF-FAC-0008": {
        "domanda": "Quale formato è molto usato nelle API web per rappresentare oggetti e liste con coppie chiave-valore?",
        "opzioni": [
            "JSON",
            "CSV",
            "XML",
            "YAML"
        ],
        "risposta_corretta": "JSON",
        "spiegazione": (
            "JSON è molto usato nelle API web perché rappresenta bene oggetti, liste e coppie chiave-valore. "
            "CSV, XML e YAML possono rappresentare dati, ma JSON è particolarmente comune nello scambio dati tra frontend, backend e API."
        )
    },

    "INF-INT-0002": {
        "opzioni": [
            "A identificare in modo univoco ogni record di una tabella",
            "A collegare una tabella a un'altra tramite una chiave esterna",
            "A definire una colonna usata spesso per ordinare i risultati",
            "A indicare un campo facoltativo che può essere lasciato vuoto"
        ],
        "risposta_corretta": "A identificare in modo univoco ogni record di una tabella",
        "spiegazione": (
            "La chiave primaria identifica in modo univoco ogni record della tabella. "
            "Una chiave esterna collega tabelle diverse, una colonna di ordinamento serve solo a ordinare, "
            "mentre un campo facoltativo non garantisce identità univoca."
        )
    },

    "INF-INT-0005": {
        "domanda": "A cosa serve principalmente una chiave esterna in un database relazionale?",
        "opzioni": [
            "A collegare un record di una tabella a un record di un'altra tabella",
            "A identificare in modo univoco ogni record della stessa tabella",
            "A ordinare automaticamente tutti i record in base alla data",
            "A trasformare una tabella relazionale in un file JSON"
        ],
        "risposta_corretta": "A collegare un record di una tabella a un record di un'altra tabella",
        "spiegazione": (
            "Una chiave esterna serve a collegare tabelle diverse. "
            "Per esempio, un ordine può contenere l'ID del cliente a cui appartiene. "
            "La chiave primaria identifica un record nella stessa tabella, mentre ordinamento e conversione in JSON sono concetti diversi."
        )
    },

    "INF-INT-0007": {
        "opzioni": [
            "Individuare e correggere errori nel comportamento del codice",
            "Osservare il programma durante l'esecuzione per capire dove nasce un errore",
            "Controllare valori intermedi per verificare se la logica segue il flusso previsto",
            "Riprodurre un problema in modo stabile per capire quale istruzione lo provoca"
        ],
        "risposta_corretta": "Individuare e correggere errori nel comportamento del codice",
        "spiegazione": (
            "Fare debug significa individuare e correggere errori nel comportamento del codice. "
            "Osservare l'esecuzione, controllare valori intermedi e riprodurre il problema sono tecniche usate durante il debug."
        )
    },

    "INF-INT-0009": {
        "opzioni": [
            "Perché possono finire in repository, log o copie condivise del progetto",
            "Perché possono essere lette da altre persone se il codice viene pubblicato",
            "Perché rendono più difficile cambiare credenziali tra ambienti diversi",
            "Perché aumentano il rischio di esporre accessi a database o servizi esterni"
        ],
        "risposta_corretta": "Perché possono finire in repository, log o copie condivise del progetto",
        "spiegazione": (
            "Salvare password nel codice è rischioso perché possono finire in repository, log, backup o copie condivise. "
            "Le altre opzioni sono conseguenze collegate, ma il rischio principale è l'esposizione involontaria delle credenziali."
        )
    }
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, contenuto):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            contenuto,
            file,
            ensure_ascii=False,
            indent=2
        )


def aggiorna_file_json(percorso):
    domande = carica_json(percorso)
    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI_INFORMATICA:
            correzione = CORREZIONI_INFORMATICA[id_domanda]

            if "domanda" in correzione:
                domanda["domanda"] = correzione["domanda"]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    if modifiche > 0:
        salva_json(percorso, domande)

    return modifiche


def aggiorna_script_create_batch():
    if not PERCORSO_BATCH.exists():
        return

    domande_batch = carica_json(PERCORSO_BATCH)

    contenuto_lista = json.dumps(
        domande_batch,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script crea il primo batch di espansione.
# Obiettivo: portare il database da 27 a 100 domande totali.
# Le nuove domande vengono salvate in data/espansione/batch_100.json


PERCORSO_OUTPUT = Path("data/espansione/batch_100.json")


nuove_domande = {contenuto_lista}


def main():
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            nuove_domande,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("File creato correttamente:")
    print(PERCORSO_OUTPUT)
    print(f"Domande create: {{len(nuove_domande)}}")


main()
'''

    PERCORSO_SCRIPT_BATCH.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    modifiche_totali = 0

    for percorso in sorted(PERCORSO_DATA.rglob("*.json")):
        modifiche_file = aggiorna_file_json(percorso)

        if modifiche_file > 0:
            modifiche_totali += modifiche_file
            print(f"Aggiornato {percorso}: {modifiche_file} domande")

    aggiorna_script_create_batch()

    print()
    print("Revisione Informatica completata.")
    print(f"Domande Informatica aggiornate: {modifiche_totali}")


main()