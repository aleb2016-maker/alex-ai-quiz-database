import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "INF-INT-0006": {
        "distrattore_forte": "Definire la struttura semantica della pagina",
        "motivo_distrattore_forte": (
            "È vicino perché HTML e CSS lavorano insieme nella pagina web, "
            "ma è sbagliato perché HTML definisce la struttura, mentre CSS gestisce aspetto visivo, layout e stile."
        ),
    },
    "INF-INT-0007": {
        "opzioni": [
            "Individuare e correggere errori nel comportamento del codice",
            "Osservare il programma durante l'esecuzione per capire dove nasce un errore",
            "Controllare valori intermedi per verificare se la logica segue il flusso previsto",
            "Riprodurre un problema in modo stabile per capire quale istruzione lo provoca",
        ],
        "risposta_corretta": "Individuare e correggere errori nel comportamento del codice",
        "spiegazione": (
            "Fare debug significa individuare e correggere errori nel comportamento del codice. "
            "Osservare l'esecuzione, controllare valori intermedi e riprodurre il problema sono tecniche utili, "
            "ma non descrivono da sole l'intero processo di debug."
        ),
        "distrattore_forte": "Osservare il programma durante l'esecuzione per capire dove nasce un errore",
        "motivo_distrattore_forte": (
            "È molto vicino perché osservare l'esecuzione è una tecnica reale di debug, "
            "ma è incompleto: il debug include anche la correzione dell'errore."
        ),
    },
    "INF-INT-0008": {
        "opzioni": [
            "Una fotografia salvata dello stato del progetto nella cronologia Git",
            "Una fotografia temporanea dello stato del progetto che non entra nella cronologia Git",
            "Un ramo separato in cui sviluppare nuove modifiche",
            "Un comando per scaricare modifiche dal repository remoto",
        ],
        "risposta_corretta": "Una fotografia salvata dello stato del progetto nella cronologia Git",
        "spiegazione": (
            "Un commit salva uno stato del progetto nella cronologia Git. "
            "Non è una fotografia temporanea, non è un branch e non è il comando usato per scaricare modifiche dal remoto."
        ),
        "distrattore_forte": "Una fotografia temporanea dello stato del progetto che non entra nella cronologia Git",
        "motivo_distrattore_forte": (
            "È vicino perché parla di fotografia dello stato del progetto, "
            "ma è sbagliato perché un commit entra nella cronologia Git: non è temporaneo."
        ),
    },
    "INF-INT-0009": {
        "opzioni": [
            "Perché possono finire in repository, log o copie condivise del progetto",
            "Perché possono essere lette da altre persone se il codice viene pubblicato",
            "Perché rendono più difficile cambiare credenziali tra ambienti diversi",
            "Perché aumentano il rischio di esporre accessi a database o servizi esterni",
        ],
        "risposta_corretta": "Perché possono finire in repository, log o copie condivise del progetto",
        "spiegazione": (
            "Salvare password nel codice è rischioso perché possono finire in repository, log, backup o copie condivise. "
            "La pubblicazione del codice, la difficoltà di cambiare credenziali e l'esposizione di accessi sono conseguenze collegate."
        ),
        "distrattore_forte": "Perché possono essere lette da altre persone se il codice viene pubblicato",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive una conseguenza reale, "
            "ma è più limitato: il rischio esiste anche tramite log, backup, repository privati o copie condivise."
        ),
    },
    "INF-AV-0004": {
        "opzioni": [
            "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
            "Perché il frontend può gestire l'interfaccia mentre il backend espone dati e logica tramite API",
            "Perché il backend può cambiare alcune regole senza riscrivere tutta l'interfaccia",
            "Perché il frontend può consumare servizi diversi senza conoscere i dettagli interni del server",
        ],
        "risposta_corretta": "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
        "spiegazione": (
            "Separare frontend e backend rende il progetto più gestibile perché divide le responsabilità: "
            "interfaccia utente, logica applicativa e gestione dei dati possono evolvere in modo più ordinato. "
            "Le altre opzioni descrivono vantaggi specifici, ma la risposta corretta è quella più generale."
        ),
        "distrattore_forte": "Perché il frontend può gestire l'interfaccia mentre il backend espone dati e logica tramite API",
        "motivo_distrattore_forte": (
            "È vicino perché descrive correttamente una separazione tipica, "
            "ma è meno completo: la risposta corretta spiega il vantaggio generale sulle responsabilità del sistema."
        ),
    },
    "INF-AV-0005": {
        "opzioni": [
            "La richiesta non è autenticata correttamente",
            "La richiesta è autenticata ma l'utente non ha i permessi necessari",
            "La risorsa richiesta non esiste sul server",
            "Il server ha generato un errore interno",
        ],
        "risposta_corretta": "La richiesta non è autenticata correttamente",
        "spiegazione": (
            "HTTP 401 indica in genere un problema di autenticazione: credenziali mancanti, non valide o token scaduto. "
            "403 riguarda invece un utente autenticato ma senza permessi sufficienti; 404 indica risorsa non trovata; 500 errore interno del server."
        ),
        "distrattore_forte": "La richiesta è autenticata ma l'utente non ha i permessi necessari",
        "motivo_distrattore_forte": (
            "È molto vicino perché riguarda comunque accesso e sicurezza, "
            "ma è sbagliato perché descrive più precisamente un errore 403, non un 401."
        ),
    },
    "INF-AV-0006": {
        "opzioni": [
            "Rendere più veloci alcune ricerche su quella colonna",
            "Rendere più veloci alcune ricerche, ma senza costi su spazio o scritture",
            "Ridurre automaticamente il numero di righe salvate nella tabella",
            "Normalizzare automaticamente i dati duplicati",
        ],
        "risposta_corretta": "Rendere più veloci alcune ricerche su quella colonna",
        "spiegazione": (
            "Un indice aiuta il database a trovare più velocemente i record su certe colonne. "
            "Può però avere costi in spazio e nelle operazioni di scrittura. "
            "Non riduce automaticamente le righe e non normalizza i dati."
        ),
        "distrattore_forte": "Rendere più veloci alcune ricerche, ma senza costi su spazio o scritture",
        "motivo_distrattore_forte": (
            "È vicino perché riconosce il vantaggio sulle ricerche, "
            "ma è sbagliato perché gli indici possono avere costi di spazio e aggiornamento."
        ),
    },
    "INF-AV-0007": {
        "opzioni": [
            "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
            "Perché possono leggere o modificare lo stesso dato nello stesso intervallo di tempo",
            "Perché possono richiedere transazioni o meccanismi di isolamento adeguati",
            "Perché possono causare aggiornamenti persi se due modifiche si sovrappongono",
        ],
        "risposta_corretta": "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
        "spiegazione": (
            "Due operazioni simultanee sullo stesso dato possono creare stati incoerenti, aggiornamenti persi o conflitti. "
            "Le altre opzioni descrivono casi o soluzioni specifiche, mentre la risposta corretta riassume il rischio principale."
        ),
        "distrattore_forte": "Perché possono leggere o modificare lo stesso dato nello stesso intervallo di tempo",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive la situazione che può creare il problema, "
            "ma è incompleto: il rischio vero nasce se questa concorrenza non viene gestita correttamente."
        ),
    },
    "INF-AV-0008": {
        "opzioni": [
            "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
            "Perché il test deve confrontare output reale e output previsto",
            "Perché il test deve verificare una condizione precisa e ripetibile",
            "Perché il test deve fallire quando il codice non rispetta il comportamento atteso",
        ],
        "risposta_corretta": "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
        "spiegazione": (
            "Un test automatico utile deve sapere cosa aspettarsi. "
            "Se il risultato atteso è chiaro, il test può confrontarlo con il risultato reale e stabilire se il comportamento è corretto. "
            "Le altre opzioni sono aspetti collegati, ma meno generali."
        ),
        "distrattore_forte": "Perché il test deve confrontare output reale e output previsto",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive una tecnica tipica dei test, "
            "ma la risposta corretta è più generale: il test deve stabilire se il comportamento è corretto o no."
        ),
    },
    "INF-AV-0009": {
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Permette di cambiare URL o chiavi senza modificare i file del codice",
            "Permette di usare configurazioni diverse tra sviluppo, test e produzione",
            "Permette di evitare che credenziali e impostazioni vengano scritte direttamente nel repository",
        ],
        "risposta_corretta": "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
        "spiegazione": (
            "Le variabili d'ambiente servono soprattutto a separare configurazioni sensibili o variabili dal codice sorgente. "
            "Cambiare URL, distinguere ambienti ed evitare credenziali nel repository sono vantaggi collegati, "
            "ma la risposta corretta è quella più generale."
        ),
        "distrattore_forte": "Permette di cambiare URL o chiavi senza modificare i file del codice",
        "motivo_distrattore_forte": (
            "È vicino perché descrive un vantaggio reale delle variabili d'ambiente, "
            "ma è meno completo: il punto centrale è separare configurazioni sensibili o diverse dal codice sorgente."
        ),
    },
    "INF-FAC-0101": {
        "opzioni": [
            "Eseguire istruzioni ed elaborare operazioni",
            "Conservare temporaneamente i dati usati dai programmi",
            "Archiviare file e programmi anche a computer spento",
            "Gestire principalmente l'elaborazione grafica delle immagini",
        ],
        "risposta_corretta": "Eseguire istruzioni ed elaborare operazioni",
        "spiegazione": (
            "La CPU è il processore principale del computer: esegue istruzioni, calcoli e operazioni logiche. "
            "La RAM conserva temporaneamente i dati dei programmi, SSD o hard disk archiviano i file in modo permanente, "
            "mentre la GPU gestisce soprattutto l'elaborazione grafica."
        ),
        "distrattore_forte": "Conservare temporaneamente i dati usati dai programmi",
        "motivo_distrattore_forte": (
            "È vicino perché riguarda un componente fondamentale usato durante l'esecuzione dei programmi, "
            "ma è sbagliato perché descrive la RAM, non la CPU."
        ),
    },
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            dati,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")


def trova_liste_domande(dati):
    liste = []

    if isinstance(dati, list):
        liste.append(dati)

    elif isinstance(dati, dict):
        for valore in dati.values():
            if isinstance(valore, list):
                liste.append(valore)

    return liste


def aggiorna_file(percorso):
    dati = carica_json(percorso)
    liste_domande = trova_liste_domande(dati)

    modificato = False
    id_modificati = []

    for lista_domande in liste_domande:
        for domanda in lista_domande:
            if not isinstance(domanda, dict):
                continue

            id_domanda = domanda.get("id")

            if id_domanda in AGGIORNAMENTI:
                domanda.update(AGGIORNAMENTI[id_domanda])
                modificato = True
                id_modificati.append(id_domanda)

    if modificato:
        salva_json(percorso, dati)

    return id_modificati


def main():
    tutti_modificati = []

    for percorso in DATA_DIR.rglob("*.json"):
        id_modificati = aggiorna_file(percorso)

        if id_modificati:
            print("File aggiornato:", percorso)

            for id_domanda in id_modificati:
                print(" -", id_domanda)

            tutti_modificati.extend(id_modificati)

    mancanti = sorted(
        set(AGGIORNAMENTI.keys()) - set(tutti_modificati)
    )

    print("")
    print("Domande Informatica certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Secondo blocco Informatica certificato correttamente.")


main()