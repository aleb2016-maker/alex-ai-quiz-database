import json
from pathlib import Path


# Questo script aggiunge il blocco Informatica della seconda espansione.
# Obiettivo: portare il database da 120 a 140 domande totali.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_informatica = [
    {
        "id": "INF-FAC-0101",
        "categoria": "informatica",
        "sottocategoria": "hardware",
        "livello": "facile",
        "domanda": "Qual è il ruolo principale della CPU in un computer?",
        "opzioni": [
            "Eseguire istruzioni ed elaborare operazioni",
            "Conservare temporaneamente i dati usati dai programmi",
            "Archiviare file e programmi anche a computer spento",
            "Gestire principalmente l'elaborazione grafica delle immagini"
        ],
        "risposta_corretta": "Eseguire istruzioni ed elaborare operazioni",
        "spiegazione": "La CPU è il processore principale del computer: esegue istruzioni, calcoli e operazioni logiche. La RAM conserva temporaneamente i dati dei programmi, SSD o hard disk archiviano i file in modo permanente, mentre la GPU gestisce soprattutto l'elaborazione grafica.",
        "tags": [
            "cpu",
            "hardware",
            "processore"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0102",
        "categoria": "informatica",
        "sottocategoria": "hardware",
        "livello": "facile",
        "domanda": "A cosa serve principalmente un SSD?",
        "opzioni": [
            "A salvare dati e programmi anche quando il computer è spento",
            "A eseguire direttamente tutte le istruzioni della CPU",
            "A sostituire la memoria RAM durante ogni calcolo",
            "A trasformare il codice sorgente in immagini"
        ],
        "risposta_corretta": "A salvare dati e programmi anche quando il computer è spento",
        "spiegazione": "Un SSD è una memoria di archiviazione permanente. Mantiene file, programmi e sistema operativo anche a computer spento. La RAM invece è temporanea.",
        "tags": [
            "ssd",
            "memoria",
            "archiviazione"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0103",
        "categoria": "informatica",
        "sottocategoria": "sistema_operativo",
        "livello": "facile",
        "domanda": "Che cos'è un sistema operativo?",
        "opzioni": [
            "Il software che gestisce risorse del computer e permette di usare programmi",
            "Un programma applicativo usato per svolgere un compito specifico",
            "Un insieme di file personali salvati in una cartella",
            "Un componente hardware che aumenta lo spazio di archiviazione"
        ],
        "risposta_corretta": "Il software che gestisce risorse del computer e permette di usare programmi",
        "spiegazione": "Il sistema operativo gestisce risorse come memoria, file, periferiche e processi, e permette agli altri programmi di funzionare. Un'applicazione svolge un compito specifico, una cartella contiene file, mentre un componente hardware come un SSD aumenta lo spazio di archiviazione.",
        "tags": [
            "sistema_operativo",
            "software",
            "computer"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0104",
        "categoria": "informatica",
        "sottocategoria": "programmazione",
        "livello": "facile",
        "domanda": "A cosa serve normalmente un ciclo in programmazione?",
        "opzioni": [
            "A ripetere un blocco di istruzioni più volte",
            "A salvare un file in modo permanente",
            "A cambiare automaticamente il linguaggio del computer",
            "A cancellare tutte le variabili del programma"
        ],
        "risposta_corretta": "A ripetere un blocco di istruzioni più volte",
        "spiegazione": "Un ciclo permette di ripetere istruzioni finché una condizione è vera o per un numero definito di volte. È utile, per esempio, per scorrere una lista di elementi.",
        "tags": [
            "cicli",
            "programmazione",
            "ripetizione"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0105",
        "categoria": "informatica",
        "sottocategoria": "programmazione",
        "livello": "facile",
        "domanda": "Che cosa rappresenta normalmente un valore booleano?",
        "opzioni": [
            "Un valore che può essere vero o falso",
            "Un numero intero usato per contare elementi",
            "Una stringa di testo composta da caratteri",
            "Un valore assente o non definito"
        ],
        "risposta_corretta": "Un valore che può essere vero o falso",
        "spiegazione": "Un booleano rappresenta due stati logici: vero o falso. Un intero rappresenta numeri senza decimali, una stringa rappresenta testo, mentre un valore nullo o assente indica mancanza di dato.",
        "tags": [
            "boolean",
            "logica",
            "programmazione"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0106",
        "categoria": "informatica",
        "sottocategoria": "file",
        "livello": "facile",
        "domanda": "Che cosa indica normalmente il percorso di un file?",
        "opzioni": [
            "La posizione del file dentro cartelle e sottocartelle",
            "La velocità con cui il file viene aperto",
            "Il colore dell'icona mostrata dal sistema",
            "Il numero di volte in cui il file è stato copiato"
        ],
        "risposta_corretta": "La posizione del file dentro cartelle e sottocartelle",
        "spiegazione": "Il percorso indica dove si trova un file nel sistema. Per esempio, una cartella può contenere altre cartelle e un file può trovarsi dentro una struttura precisa.",
        "tags": [
            "file",
            "percorso",
            "cartelle"
        ],
        "difficolta": 1
    },
    {
        "id": "INF-INT-0101",
        "categoria": "informatica",
        "sottocategoria": "programmazione",
        "livello": "intermedio",
        "domanda": "Perché una funzione è utile in un programma?",
        "opzioni": [
            "Permette di raggruppare istruzioni riutilizzabili con un compito chiaro",
            "Serve solo a rendere il codice più lungo senza motivo",
            "Trasforma automaticamente ogni errore in un risultato corretto",
            "Sostituisce sempre la necessità di usare variabili"
        ],
        "risposta_corretta": "Permette di raggruppare istruzioni riutilizzabili con un compito chiaro",
        "spiegazione": "Una funzione raccoglie istruzioni collegate a un compito. Può ricevere dati in ingresso, elaborarli e restituire un risultato, evitando ripetizioni e rendendo il codice più ordinato.",
        "tags": [
            "funzioni",
            "riuso",
            "programmazione"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0102",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "intermedio",
        "domanda": "A cosa serve una query SELECT in SQL?",
        "opzioni": [
            "A leggere dati da una o più tabelle",
            "A cancellare sempre l'intero database",
            "A modificare il colore delle colonne",
            "A trasformare automaticamente SQL in HTML"
        ],
        "risposta_corretta": "A leggere dati da una o più tabelle",
        "spiegazione": "SELECT viene usato per interrogare il database e ottenere dati. Può essere combinato con condizioni, ordinamenti e join per recuperare informazioni specifiche.",
        "tags": [
            "sql",
            "select",
            "database"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0103",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "intermedio",
        "domanda": "Perché si usa un JOIN in un database relazionale?",
        "opzioni": [
            "Per combinare dati collegati provenienti da tabelle diverse",
            "Per rinominare automaticamente tutti i campi di una tabella",
            "Per eliminare sempre le chiavi primarie dal database",
            "Per convertire una query SQL in un file immagine"
        ],
        "risposta_corretta": "Per combinare dati collegati provenienti da tabelle diverse",
        "spiegazione": "Un JOIN permette di unire informazioni distribuite in più tabelle tramite relazioni, per esempio collegando ordini e clienti attraverso un identificatore comune.",
        "tags": [
            "join",
            "database",
            "relazioni"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0104",
        "categoria": "informatica",
        "sottocategoria": "web",
        "livello": "intermedio",
        "domanda": "Che cosa indica di solito una risposta HTTP 404?",
        "opzioni": [
            "La risorsa richiesta non è stata trovata sul server",
            "La richiesta non è autenticata correttamente",
            "L'utente è autenticato ma non autorizzato",
            "Il server ha generato un errore interno"
        ],
        "risposta_corretta": "La risorsa richiesta non è stata trovata sul server",
        "spiegazione": "HTTP 404 indica che la risorsa richiesta non è stata trovata. 401 riguarda un problema di autenticazione, 403 indica permessi insufficienti, mentre 500 segnala un errore interno del server.",
        "tags": [
            "http",
            "404",
            "web"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0105",
        "categoria": "informatica",
        "sottocategoria": "git",
        "livello": "intermedio",
        "domanda": "A cosa serve un branch in Git?",
        "opzioni": [
            "A lavorare su una linea separata di sviluppo senza modificare subito quella principale",
            "A cancellare definitivamente tutta la cronologia del progetto",
            "A scaricare automaticamente ogni libreria mancante",
            "A trasformare il repository in un database SQL"
        ],
        "risposta_corretta": "A lavorare su una linea separata di sviluppo senza modificare subito quella principale",
        "spiegazione": "Un branch permette di sviluppare modifiche in parallelo. È utile per nuove funzionalità, correzioni o esperimenti, senza toccare immediatamente il ramo principale.",
        "tags": [
            "git",
            "branch",
            "versionamento"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0106",
        "categoria": "informatica",
        "sottocategoria": "sicurezza",
        "livello": "intermedio",
        "domanda": "Perché HTTPS è importante per un sito web?",
        "opzioni": [
            "Per proteggere la comunicazione tra browser e server tramite cifratura",
            "Per verificare che il sito usi un certificato digitale valido",
            "Per ridurre il rischio che i dati vengano intercettati durante il trasferimento",
            "Per rendere più sicuro lo scambio di informazioni sensibili"
        ],
        "risposta_corretta": "Per proteggere la comunicazione tra browser e server tramite cifratura",
        "spiegazione": "HTTPS protegge la comunicazione tra browser e server tramite cifratura. Certificati, riduzione del rischio di intercettazione e protezione dei dati sensibili sono aspetti collegati, ma la risposta corretta è quella più completa e generale.",
        "tags": [
            "https",
            "sicurezza",
            "web"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0107",
        "categoria": "informatica",
        "sottocategoria": "frontend",
        "livello": "intermedio",
        "domanda": "Che cosa significa rendere una pagina web responsive?",
        "opzioni": [
            "Far adattare layout e contenuti a schermi di dimensioni diverse",
            "Far rispondere il server sempre con lo stesso codice HTTP",
            "Impedire agli utenti di aprire la pagina da smartphone",
            "Trasformare automaticamente ogni testo in un'immagine"
        ],
        "risposta_corretta": "Far adattare layout e contenuti a schermi di dimensioni diverse",
        "spiegazione": "Una pagina responsive si adatta a desktop, tablet e smartphone. Layout, dimensioni e spaziature cambiano per restare leggibili e usabili.",
        "tags": [
            "responsive",
            "frontend",
            "css"
        ],
        "difficolta": 2
    },
    {
        "id": "INF-AV-0101",
        "categoria": "informatica",
        "sottocategoria": "architettura",
        "livello": "avanzato",
        "domanda": "Perché la validazione dei dati dovrebbe avvenire anche lato backend?",
        "opzioni": [
            "Perché i dati inviati al server non devono essere considerati affidabili solo perché il frontend li controlla",
            "Perché il backend deve sempre ignorare tutte le richieste del frontend",
            "Perché la validazione lato backend sostituisce ogni test automatico",
            "Perché il frontend non può mai mostrare messaggi di errore"
        ],
        "risposta_corretta": "Perché i dati inviati al server non devono essere considerati affidabili solo perché il frontend li controlla",
        "spiegazione": "Il controllo lato frontend migliora l'esperienza utente, ma può essere aggirato. Il backend deve validare i dati per proteggere applicazione, database e regole di business.",
        "tags": [
            "backend",
            "validazione",
            "sicurezza"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0102",
        "categoria": "informatica",
        "sottocategoria": "sicurezza",
        "livello": "avanzato",
        "domanda": "Qual è una differenza importante tra hashing e cifratura?",
        "opzioni": [
            "L'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave",
            "L'hashing serve solo a comprimere immagini, mentre la cifratura serve solo a colorare file",
            "La cifratura elimina sempre la necessità di autenticare gli utenti",
            "Hashing e cifratura sono sempre la stessa operazione con nomi diversi"
        ],
        "risposta_corretta": "L'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave",
        "spiegazione": "Un hash è usato spesso per verificare integrità o password senza recuperare il valore originale. La cifratura invece protegge dati che devono poter essere decifrati da chi possiede la chiave.",
        "tags": [
            "hashing",
            "cifratura",
            "sicurezza"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0103",
        "categoria": "informatica",
        "sottocategoria": "performance",
        "livello": "avanzato",
        "domanda": "Perché la cache può migliorare le prestazioni di un'applicazione?",
        "opzioni": [
            "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
            "Perché cancella automaticamente ogni bug dal codice",
            "Perché sostituisce sempre il database principale",
            "Perché obbliga il server a ignorare tutte le richieste nuove"
        ],
        "risposta_corretta": "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
        "spiegazione": "La cache conserva temporaneamente risultati o dati molto richiesti. Questo può ridurre tempi di risposta e carico su database o servizi esterni.",
        "tags": [
            "cache",
            "performance",
            "applicazioni"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0104",
        "categoria": "informatica",
        "sottocategoria": "api",
        "livello": "avanzato",
        "domanda": "Perché la paginazione è utile quando un'API restituisce molti risultati?",
        "opzioni": [
            "Per dividere i risultati in blocchi più piccoli e gestibili",
            "Per impedire all'API di restituire qualsiasi dato",
            "Per trasformare ogni risposta in un errore 404",
            "Per rendere obbligatorio l'uso di un solo utente alla volta"
        ],
        "risposta_corretta": "Per dividere i risultati in blocchi più piccoli e gestibili",
        "spiegazione": "La paginazione evita di inviare troppi dati in una sola risposta. Aiuta prestazioni, consumo di rete e usabilità, soprattutto con grandi quantità di risultati.",
        "tags": [
            "api",
            "paginazione",
            "performance"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0105",
        "categoria": "informatica",
        "sottocategoria": "devops",
        "livello": "avanzato",
        "domanda": "Che vantaggio offre una pipeline CI/CD in un progetto software?",
        "opzioni": [
            "Automatizza controlli, test e rilascio riducendo errori manuali ripetitivi",
            "Sostituisce completamente la necessità di scrivere codice",
            "Trasforma automaticamente ogni bug in una nuova funzionalità",
            "Impedisce a più sviluppatori di collaborare sullo stesso progetto"
        ],
        "risposta_corretta": "Automatizza controlli, test e rilascio riducendo errori manuali ripetitivi",
        "spiegazione": "Una pipeline CI/CD può eseguire test, build e deploy in modo automatico. Questo rende più affidabile il processo di rilascio e riduce operazioni manuali ripetitive.",
        "tags": [
            "cicd",
            "devops",
            "automazione"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0106",
        "categoria": "informatica",
        "sottocategoria": "container",
        "livello": "avanzato",
        "domanda": "Perché un container può rendere più prevedibile l'esecuzione di un'applicazione?",
        "opzioni": [
            "Perché include applicazione e dipendenze in un ambiente isolato e riproducibile",
            "Perché elimina sempre la necessità di configurare qualsiasi variabile",
            "Perché trasforma il codice backend in codice frontend",
            "Perché sostituisce automaticamente ogni sistema operativo"
        ],
        "risposta_corretta": "Perché include applicazione e dipendenze in un ambiente isolato e riproducibile",
        "spiegazione": "Un container confeziona applicazione, librerie e configurazioni essenziali in un ambiente isolato. Questo riduce differenze tra sviluppo, test e produzione.",
        "tags": [
            "container",
            "docker",
            "ambiente"
        ],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0107",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "avanzato",
        "domanda": "Perché una transazione è utile quando più operazioni devono riuscire insieme?",
        "opzioni": [
            "Perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine",
            "Perché rende impossibile qualunque errore di programmazione",
            "Perché cancella automaticamente tutte le tabelle non usate",
            "Perché trasforma una query SQL in una chiamata HTTP"
        ],
        "risposta_corretta": "Perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine",
        "spiegazione": "Una transazione consente di trattare più operazioni come un'unica unità. Se qualcosa fallisce, si può annullare tutto per evitare dati parziali o incoerenti.",
        "tags": [
            "transazioni",
            "database",
            "coerenza"
        ],
        "difficolta": 3
    }
]


def carica_domande_esistenti():
    if not PERCORSO_OUTPUT.exists():
        return []

    with open(PERCORSO_OUTPUT, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_domande(domande):
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            domande,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    domande_esistenti = carica_domande_esistenti()

    nuovi_id = {
        domanda["id"]
        for domanda in nuove_domande_informatica
    }

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_informatica

    salva_domande(domande_finali)

    print("Blocco Informatica aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Informatica:", len(nuove_domande_informatica))
    print("Domande totali in batch_200:", len(domande_finali))


main()
