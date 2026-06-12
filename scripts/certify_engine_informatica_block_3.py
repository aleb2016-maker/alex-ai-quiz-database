import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "INF-FAC-0102": {
        "opzioni": [
            "A salvare dati e programmi anche quando il computer è spento",
            "A conservare temporaneamente i dati usati dai programmi durante l'esecuzione",
            "A eseguire direttamente tutte le istruzioni della CPU",
            "A gestire principalmente i calcoli grafici della scheda video",
        ],
        "risposta_corretta": "A salvare dati e programmi anche quando il computer è spento",
        "spiegazione": (
            "Un SSD è una memoria di archiviazione permanente. Mantiene file, programmi e sistema operativo anche a computer spento. "
            "La RAM invece conserva temporaneamente dati usati dai programmi durante l'esecuzione."
        ),
        "distrattore_forte": "A conservare temporaneamente i dati usati dai programmi durante l'esecuzione",
        "motivo_distrattore_forte": (
            "È vicino perché parla comunque di memoria usata dal computer, "
            "ma è sbagliato perché descrive la RAM, non l'SSD."
        ),
    },
    "INF-FAC-0103": {
        "opzioni": [
            "Il software che gestisce risorse del computer e permette di usare programmi",
            "Un programma applicativo usato per svolgere un compito specifico",
            "Un componente hardware che aumenta lo spazio di archiviazione",
            "Una cartella che contiene file personali dell'utente",
        ],
        "risposta_corretta": "Il software che gestisce risorse del computer e permette di usare programmi",
        "spiegazione": (
            "Il sistema operativo gestisce risorse come memoria, file, periferiche e processi, "
            "e permette agli altri programmi di funzionare. Un'applicazione svolge un compito specifico, "
            "mentre un componente hardware come un SSD aumenta lo spazio di archiviazione."
        ),
        "distrattore_forte": "Un programma applicativo usato per svolgere un compito specifico",
        "motivo_distrattore_forte": (
            "È vicino perché anche un'applicazione è software, "
            "ma è sbagliato perché il sistema operativo gestisce il computer e permette alle applicazioni di funzionare."
        ),
    },
    "INF-FAC-0104": {
        "opzioni": [
            "A ripetere un blocco di istruzioni più volte",
            "A scegliere se eseguire un blocco una sola volta in base a una condizione",
            "A salvare un file in modo permanente",
            "A cancellare tutte le variabili del programma",
        ],
        "risposta_corretta": "A ripetere un blocco di istruzioni più volte",
        "spiegazione": (
            "Un ciclo permette di ripetere istruzioni finché una condizione è vera o per un numero definito di volte. "
            "Una condizione invece sceglie quale ramo di codice eseguire, ma non ripete automaticamente il blocco."
        ),
        "distrattore_forte": "A scegliere se eseguire un blocco una sola volta in base a una condizione",
        "motivo_distrattore_forte": (
            "È vicino perché anche le condizioni controllano il flusso del programma, "
            "ma è sbagliato perché un ciclo serve a ripetere istruzioni."
        ),
    },
    "INF-FAC-0105": {
        "opzioni": [
            "Un valore che può essere vero o falso",
            "Un valore numerico usato per contare due alternative",
            "Una stringa di testo composta da caratteri",
            "Un valore assente o non definito",
        ],
        "risposta_corretta": "Un valore che può essere vero o falso",
        "spiegazione": (
            "Un booleano rappresenta due stati logici: vero o falso. "
            "Un numero intero serve a contare, una stringa rappresenta testo, "
            "mentre un valore nullo o assente indica mancanza di dato."
        ),
        "distrattore_forte": "Un valore numerico usato per contare due alternative",
        "motivo_distrattore_forte": (
            "È vicino perché spesso i valori booleani vengono associati a due stati, "
            "ma è sbagliato perché il booleano rappresenta vero/falso, non un conteggio numerico."
        ),
    },
    "INF-FAC-0106": {
        "opzioni": [
            "La posizione del file dentro cartelle e sottocartelle",
            "Il nome del file senza indicare le cartelle in cui si trova",
            "La velocità con cui il file viene aperto",
            "Il numero di volte in cui il file è stato copiato",
        ],
        "risposta_corretta": "La posizione del file dentro cartelle e sottocartelle",
        "spiegazione": (
            "Il percorso indica dove si trova un file nel sistema, dentro una struttura di cartelle e sottocartelle. "
            "Il solo nome del file non basta sempre a identificarne la posizione."
        ),
        "distrattore_forte": "Il nome del file senza indicare le cartelle in cui si trova",
        "motivo_distrattore_forte": (
            "È vicino perché il nome può far parte del percorso, "
            "ma è incompleto: il percorso indica anche cartelle e sottocartelle."
        ),
    },
    "INF-INT-0101": {
        "opzioni": [
            "Permette di raggruppare istruzioni riutilizzabili con un compito chiaro",
            "Permette di raggruppare istruzioni, ma senza poter ricevere dati o restituire risultati",
            "Serve solo a rendere il codice più lungo senza motivo",
            "Sostituisce sempre la necessità di usare variabili",
        ],
        "risposta_corretta": "Permette di raggruppare istruzioni riutilizzabili con un compito chiaro",
        "spiegazione": (
            "Una funzione raccoglie istruzioni collegate a un compito. "
            "Può ricevere dati in ingresso, elaborarli e restituire un risultato, "
            "evitando ripetizioni e rendendo il codice più ordinato."
        ),
        "distrattore_forte": "Permette di raggruppare istruzioni, ma senza poter ricevere dati o restituire risultati",
        "motivo_distrattore_forte": (
            "È vicino perché parla di raggruppare istruzioni, "
            "ma è sbagliato perché una funzione può anche ricevere input e restituire output."
        ),
    },
    "INF-INT-0102": {
        "opzioni": [
            "A leggere dati da una o più tabelle",
            "A leggere dati solo da una singola tabella, senza condizioni o collegamenti",
            "A cancellare sempre l'intero database",
            "A trasformare automaticamente SQL in HTML",
        ],
        "risposta_corretta": "A leggere dati da una o più tabelle",
        "spiegazione": (
            "SELECT viene usato per interrogare il database e ottenere dati. "
            "Può leggere da una o più tabelle e può essere combinato con condizioni, ordinamenti e join."
        ),
        "distrattore_forte": "A leggere dati solo da una singola tabella, senza condizioni o collegamenti",
        "motivo_distrattore_forte": (
            "È vicino perché SELECT legge dati, "
            "ma è troppo limitato: può usare condizioni, join e più tabelle."
        ),
    },
    "INF-INT-0103": {
        "opzioni": [
            "Per combinare dati collegati provenienti da tabelle diverse",
            "Per combinare tabelle diverse creando automaticamente relazioni non definite",
            "Per rinominare automaticamente tutti i campi di una tabella",
            "Per eliminare sempre le chiavi primarie dal database",
        ],
        "risposta_corretta": "Per combinare dati collegati provenienti da tabelle diverse",
        "spiegazione": (
            "Un JOIN permette di unire informazioni distribuite in più tabelle tramite relazioni, "
            "per esempio collegando ordini e clienti attraverso un identificatore comune."
        ),
        "distrattore_forte": "Per combinare tabelle diverse creando automaticamente relazioni non definite",
        "motivo_distrattore_forte": (
            "È vicino perché parla di combinare tabelle, "
            "ma è sbagliato perché il JOIN usa relazioni o condizioni definite, non crea automaticamente relazioni corrette."
        ),
    },
    "INF-INT-0104": {
        "opzioni": [
            "La risorsa richiesta non è stata trovata sul server",
            "La richiesta non è autenticata correttamente",
            "L'utente è autenticato ma non autorizzato",
            "Il server ha generato un errore interno",
        ],
        "risposta_corretta": "La risorsa richiesta non è stata trovata sul server",
        "spiegazione": (
            "HTTP 404 indica che la risorsa richiesta non è stata trovata. "
            "401 riguarda un problema di autenticazione, 403 indica permessi insufficienti, "
            "mentre 500 segnala un errore interno del server."
        ),
        "distrattore_forte": "La richiesta non è autenticata correttamente",
        "motivo_distrattore_forte": (
            "È vicino perché anche 401 è un codice di errore HTTP molto comune, "
            "ma è sbagliato perché 401 riguarda l'autenticazione, mentre 404 riguarda una risorsa non trovata."
        ),
    },
    "INF-INT-0105": {
        "opzioni": [
            "A lavorare su una linea separata di sviluppo senza modificare subito quella principale",
            "A salvare una fotografia dello stato del progetto nella cronologia Git",
            "A scaricare automaticamente ogni libreria mancante",
            "A trasformare il repository in un database SQL",
        ],
        "risposta_corretta": "A lavorare su una linea separata di sviluppo senza modificare subito quella principale",
        "spiegazione": (
            "Un branch permette di sviluppare modifiche in parallelo. "
            "È utile per nuove funzionalità, correzioni o esperimenti, senza toccare immediatamente il ramo principale. "
            "Il commit invece salva uno stato del progetto."
        ),
        "distrattore_forte": "A salvare una fotografia dello stato del progetto nella cronologia Git",
        "motivo_distrattore_forte": (
            "È vicino perché è un concetto reale di Git, "
            "ma è sbagliato perché descrive un commit, non un branch."
        ),
    },
    "INF-INT-0106": {
        "opzioni": [
            "Per proteggere la comunicazione tra browser e server tramite cifratura",
            "Per verificare che il sito usi un certificato digitale valido, senza cifrare la comunicazione",
            "Per rendere il sito sempre più veloce indipendentemente dal server",
            "Per impedire al server di ricevere richieste dal browser",
        ],
        "risposta_corretta": "Per proteggere la comunicazione tra browser e server tramite cifratura",
        "spiegazione": (
            "HTTPS protegge la comunicazione tra browser e server tramite cifratura. "
            "I certificati sono parte importante del meccanismo, ma il punto centrale è proteggere lo scambio di dati."
        ),
        "distrattore_forte": "Per verificare che il sito usi un certificato digitale valido, senza cifrare la comunicazione",
        "motivo_distrattore_forte": (
            "È vicino perché HTTPS usa certificati digitali, "
            "ma è sbagliato perché HTTPS serve anche a cifrare la comunicazione."
        ),
    },
    "INF-INT-0107": {
        "opzioni": [
            "Far adattare layout e contenuti a schermi di dimensioni diverse",
            "Far adattare solo le immagini, lasciando invariato il layout della pagina",
            "Far rispondere il server sempre con lo stesso codice HTTP",
            "Impedire agli utenti di aprire la pagina da smartphone",
        ],
        "risposta_corretta": "Far adattare layout e contenuti a schermi di dimensioni diverse",
        "spiegazione": (
            "Una pagina responsive si adatta a desktop, tablet e smartphone. "
            "Layout, dimensioni e spaziature cambiano per restare leggibili e usabili."
        ),
        "distrattore_forte": "Far adattare solo le immagini, lasciando invariato il layout della pagina",
        "motivo_distrattore_forte": (
            "È vicino perché anche le immagini possono adattarsi negli schermi diversi, "
            "ma è incompleto: una pagina responsive adatta l'intero layout e i contenuti."
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
        print("Terzo blocco Informatica certificato correttamente.")


main()