import json
from pathlib import Path

FILE = Path("data/informatica.json")
BACKUP = Path("data/informatica.backup_prima_terzo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_informatica_terzo_blocco_distrattori_forti.md")

PATCH = {
    "INF-FAC-0201": {
        "opzioni": [
            "Una sequenza ordinata di passaggi per risolvere un problema",
            "Una sequenza di passaggi ordinati, ma usata per archiviare file senza elaborarli",
            "Un insieme di istruzioni, ma riferito a un componente fisico del processore",
            "Una procedura con passaggi, ma usata principalmente come indirizzo per aprire pagine web"
        ],
        "spiegazione": (
            "Un algoritmo è una sequenza ordinata di passaggi per risolvere un problema. "
            "Non è un archivio di file, non è un componente hardware e non coincide con un indirizzo web."
        )
    },

    "INF-FAC-0202": {
        "opzioni": [
            "Una parte del nome che aiuta a riconoscere il formato o il tipo di contenuto del file",
            "Una parte del nome che indica il formato, ma anche la cartella esatta in cui il file si trova",
            "Un'indicazione sul tipo di file, ma usata per stabilire la password necessaria ad aprirlo",
            "Un elemento del nome del file, ma riferito alla memoria RAM usata durante l'avvio"
        ],
        "spiegazione": (
            "L'estensione di un file aiuta a riconoscere il formato o il tipo di contenuto, per esempio testo, JSON o immagine. "
            "Non indica la cartella del file, non stabilisce la password e non misura la RAM usata dal sistema."
        )
    },

    "INF-FAC-0203": {
        "opzioni": [
            "Raggruppa istruzioni riutilizzabili per svolgere un compito specifico",
            "Raggruppa istruzioni riutilizzabili, ma le cancella dopo ciascuna esecuzione",
            "Organizza istruzioni del programma, ma le usa per trasformare il monitor in memoria",
            "Raccoglie codice riutilizzabile, ma sostituisce la connessione internet durante i download"
        ],
        "spiegazione": (
            "Una funzione raggruppa istruzioni riutilizzabili per svolgere un compito specifico. "
            "Non cancella il codice sorgente, non trasforma componenti hardware e non sostituisce la connessione internet."
        )
    },

    "INF-FAC-0204": {
        "opzioni": [
            "Quando bisogna ripetere più volte una o più istruzioni",
            "Quando bisogna ripetere istruzioni, ma cambiando il colore fisico della tastiera",
            "Quando si ripete un controllo sui dati, ma evitando qualunque verifica della condizione",
            "Quando si esegue più volte un'azione, ma per salvare immagini senza usare programmi"
        ],
        "spiegazione": (
            "Un ciclo è utile quando bisogna ripetere più volte una o più istruzioni. "
            "La ripetizione dipende da una condizione o da una sequenza; non riguarda il colore della tastiera o il salvataggio di immagini."
        )
    },

    "INF-FAC-0205": {
        "opzioni": [
            "Un sistema organizzato per memorizzare, cercare e gestire dati",
            "Un sistema per gestire dati, ma usato principalmente per disegnare icone",
            "Una struttura che conserva informazioni, ma coincidente con un cavo collegato allo schermo",
            "Un sistema che contiene dati, ma pensato per cancellare la cronologia del browser"
        ],
        "spiegazione": (
            "Un database è un sistema organizzato per memorizzare, cercare e gestire dati. "
            "Non è un linguaggio per icone, non è un cavo e non è un programma dedicato alla cronologia del browser."
        )
    },

    "INF-FAC-0206": {
        "opzioni": [
            "Un protocollo usato per lo scambio di informazioni tra client e server web",
            "Un protocollo del web, ma usato per comprimere file audio",
            "Una regola di scambio tra client e server, ma collocata nella memoria interna del processore",
            "Un meccanismo di comunicazione web, ma usato per spegnere database relazionali"
        ],
        "spiegazione": (
            "HTTP è un protocollo usato per lo scambio di informazioni tra client e server web. "
            "Non è un formato audio, non è memoria del processore e non è un comando per spegnere database."
        )
    },

    "INF-FAC-0207": {
        "opzioni": [
            "Il frontend riguarda l'interfaccia visibile, mentre il backend gestisce logica, dati e servizi",
            "Il frontend mostra l'interfaccia, ma conserva direttamente i dati principali su disco",
            "Il backend gestisce logica e dati, ma si occupa principalmente di colori e pulsanti visibili",
            "Frontend e backend dividono i compiti, ma il frontend funziona senza codice e il backend senza dati"
        ],
        "spiegazione": (
            "Il frontend riguarda l'interfaccia visibile con cui l'utente interagisce, mentre il backend gestisce logica, dati e servizi. "
            "Non bisogna invertire i ruoli: la parte visibile non sostituisce la gestione dati del backend."
        )
    },

    "INF-FAC-0208": {
        "opzioni": [
            "A tenere traccia delle modifiche al codice e collaborare sul progetto",
            "A tracciare modifiche del codice, ma compilando il programma senza configurazione",
            "A collaborare sul progetto, ma proteggendo il computer da tutti i virus",
            "A versionare file di progetto, ma convertendo immagini in documenti di testo modificabili"
        ],
        "spiegazione": (
            "Git serve a tenere traccia delle modifiche al codice e a collaborare sul progetto. "
            "Non è un compilatore automatico, non è un antivirus e non è uno strumento di conversione immagini-testo."
        )
    },

    "INF-FAC-0209": {
        "opzioni": [
            "Un formato testuale strutturato per rappresentare dati con coppie chiave-valore, liste e oggetti",
            "Un formato testuale strutturato, ma usato principalmente come immagine compressa per fotografie",
            "Un formato per rappresentare dati, ma collegato fisicamente al computer tramite un cavo",
            "Una struttura dati leggibile, ma installata come sistema operativo dentro il browser"
        ],
        "spiegazione": (
            "Un file JSON è un formato testuale strutturato per rappresentare dati con coppie chiave-valore, liste e oggetti. "
            "Non è un'immagine, non è un cavo e non è un sistema operativo."
        )
    },

    "INF-FAC-0210": {
        "opzioni": [
            "Un insieme di regole e punti di accesso che permette a software diversi di comunicare",
            "Un insieme di regole per software, ma usato come cartella temporanea di immagini",
            "Un punto di accesso tra programmi, ma coincidente con un tipo di tastiera per scrivere codice",
            "Un meccanismo di comunicazione software, ma riferito a un errore grafico dello schermo"
        ],
        "spiegazione": (
            "Una API è un insieme di regole e punti di accesso che permette a software diversi di comunicare. "
            "Non è una cartella temporanea, non è una tastiera e non è un errore grafico."
        )
    },

    "INF-FAC-0211": {
        "opzioni": [
            "Un valore logico che può indicare vero o falso",
            "Un valore logico a due stati, ma usato per descrivere lunghi testi di database",
            "Un valore che indica vero o falso, ma salvato principalmente come immagine trasparente",
            "Un dato logico, ma usato per assegnare indirizzi numerici alle stampanti"
        ],
        "spiegazione": (
            "Un valore booleano rappresenta un valore logico che può indicare vero o falso. "
            "Non è un testo lungo, non è un'immagine e non è un indirizzo di rete."
        )
    },

    "INF-FAC-0212": {
        "opzioni": [
            "La posizione del file dentro cartelle e sottocartelle del sistema",
            "La posizione del file nel sistema, ma indicata dal colore del nome sullo schermo",
            "Il punto in cui si trova il file, ma misurato tramite energia consumata quando viene aperto",
            "La posizione del file, ma definita dal numero di righe di codice nei programmi installati"
        ],
        "spiegazione": (
            "Il percorso di un file indica la posizione del file dentro cartelle e sottocartelle del sistema. "
            "Non dipende dal colore del nome, dal consumo elettrico o dal numero di righe di codice dei programmi."
        )
    },

    "INF-INT-0201": {
        "opzioni": [
            "Per stimare come cresce il tempo di esecuzione al crescere della quantità di dati",
            "Per valutare la crescita del tempo di esecuzione, ma scegliendo il colore dell'interfaccia",
            "Per stimare il comportamento dell'algoritmo, ma contando i file nella cartella del progetto",
            "Per misurare l'efficienza del codice, ma usando la temperatura fisica del processore"
        ],
        "spiegazione": (
            "La complessità temporale è importante perché permette di stimare come cresce il tempo di esecuzione al crescere della quantità di dati. "
            "Non riguarda colori dell'interfaccia, numero di file nella cartella o temperatura del processore."
        )
    },

    "INF-INT-0202": {
        "opzioni": [
            "A combinare righe provenienti da più tabelle in base a una relazione tra i dati",
            "A combinare dati tra tabelle, ma cancellando quelle non coinvolte nella relazione",
            "A collegare righe di più tabelle, ma cambiando il linguaggio di programmazione del progetto",
            "A unire dati relazionali, ma comprimendo immagini prima del salvataggio"
        ],
        "spiegazione": (
            "Una JOIN in SQL serve a combinare righe provenienti da più tabelle in base a una relazione tra i dati. "
            "Non cancella tabelle, non cambia linguaggio di programmazione e non comprime immagini."
        )
    },

    "INF-INT-0203": {
        "opzioni": [
            "Usa risorse identificabili, metodi HTTP coerenti e risposte comprensibili per il client",
            "Usa risorse e metodi HTTP, ma permette al browser di modificare direttamente il database",
            "Organizza risposte per il client, ma evita i codici di stato rendendo meno chiaro l'esito",
            "Espone dati tramite API, ma mescola interfaccia grafica e query SQL nella stessa risposta"
        ],
        "spiegazione": (
            "Una API REST ben progettata usa risorse identificabili, metodi HTTP coerenti e risposte comprensibili per il client. "
            "Non dovrebbe far modificare direttamente il database dal browser, ignorare i codici di stato o mescolare interfaccia grafica e query SQL."
        )
    },

    "INF-INT-0204": {
        "opzioni": [
            "Proteggere lo stato interno di un oggetto esponendo metodi controllati per interagire con esso",
            "Proteggere lo stato di un oggetto, ma unendo tutti i file del progetto in una singola immagine",
            "Limitare l'accesso interno ai dati, ma eseguendo il programma senza classi, oggetti o metodi",
            "Controllare l'interazione con l'oggetto, ma salvando ogni variabile globale in un database esterno"
        ],
        "spiegazione": (
            "L'incapsulamento significa proteggere lo stato interno di un oggetto esponendo metodi controllati per interagire con esso. "
            "Non riguarda immagini, esecuzione senza oggetti o salvataggio di variabili globali in database esterni."
        )
    },

    "INF-INT-0205": {
        "opzioni": [
            "Per separare dati, logica di presentazione e controllo del flusso dell'applicazione",
            "Per separare responsabilità dell'applicazione, ma trasformando ogni schermata in una tabella",
            "Per dividere dati e presentazione, ma impedendo l'uso di funzioni riutilizzabili",
            "Per organizzare il codice, ma sostituendo i test con nomi di file più lunghi"
        ],
        "spiegazione": (
            "Il pattern MVC è utile perché separa dati, logica di presentazione e controllo del flusso dell'applicazione. "
            "Non trasforma schermate in tabelle, non impedisce funzioni riutilizzabili e non sostituisce i test."
        )
    },

    "INF-INT-0206": {
        "opzioni": [
            "L'autenticazione verifica l'identità, mentre l'autorizzazione stabilisce cosa l'utente può fare",
            "L'autenticazione verifica l'identità, ma decide anche i permessi operativi dell'utente",
            "L'autorizzazione stabilisce i permessi, ma crea l'identità anagrafica dell'utente",
            "Autenticazione e autorizzazione gestiscono accessi, ma indicano il salvataggio dei file temporanei"
        ],
        "spiegazione": (
            "L'autenticazione verifica l'identità dell'utente, mentre l'autorizzazione stabilisce cosa quell'utente può fare. "
            "Sono concetti collegati ma distinti: prima si riconosce l'utente, poi si valutano i permessi."
        )
    },

    "INF-INT-0207": {
        "opzioni": [
            "A limitare il numero di richieste consentite in un certo periodo per proteggere servizio e risorse",
            "A controllare il numero di richieste, ma trasformandole in query SQL più lunghe",
            "A limitare richieste verso l'API, ma impedendo al server di distinguere gli utenti",
            "A proteggere il servizio da troppe richieste, ma sostituendo la validazione dei dati inseriti"
        ],
        "spiegazione": (
            "Il rate limiting serve a limitare il numero di richieste consentite in un certo periodo per proteggere servizio e risorse. "
            "Non trasforma richieste in query SQL, non elimina la distinzione tra utenti e non sostituisce la validazione dei dati."
        )
    },

    "INF-INT-0208": {
        "opzioni": [
            "Che punta a garantire atomicità, consistenza, isolamento e durabilità delle operazioni",
            "Che descrive proprietà delle transazioni, ma trasforma tabelle SQL in file HTML statici",
            "Che rende più affidabili le operazioni, ma serve a colorare query nella console del database",
            "Che regola le transazioni, ma permette di ignorare vincoli e controlli sui dati scritti"
        ],
        "spiegazione": (
            "Le proprietà ACID puntano a garantire atomicità, consistenza, isolamento e durabilità delle operazioni. "
            "Non trasformano tabelle in HTML, non riguardano colori della console e non permettono di ignorare vincoli sui dati."
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(json.dumps(contenuto, ensure_ascii=False, indent=2), encoding="utf-8")


def estrai_domande(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave]

    raise ValueError("Formato JSON non riconosciuto: non trovo la lista delle domande.")


def aggiorna_opzioni(domanda, nuove_opzioni):
    for chiave in ["opzioni", "options", "risposte", "answers"]:
        if chiave in domanda:
            domanda[chiave] = nuove_opzioni
            return

    domanda["opzioni"] = nuove_opzioni


def aggiorna_risposta_corretta(domanda, testo_corretta):
    for chiave in ["risposta_corretta", "correct_answer", "correct", "answer", "soluzione"]:
        if chiave in domanda:
            valore = str(domanda.get(chiave, "")).strip().upper()

            if valore in ["A", "B", "C", "D"]:
                domanda[chiave] = "A"
            else:
                domanda[chiave] = testo_corretta

            return

    domanda["risposta_corretta"] = testo_corretta


def main():
    if not FILE.exists():
        raise SystemExit("ERRORE: data/informatica.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

    contenuto = carica_json(FILE)
    domande = estrai_domande(contenuto)

    indice_per_id = {
        str(domanda.get("id", "")).strip(): domanda
        for domanda in domande
    }

    aggiornate = []
    non_trovate = []

    for id_domanda, dati in PATCH.items():
        domanda = indice_per_id.get(id_domanda)

        if domanda is None:
            non_trovate.append(id_domanda)
            continue

        nuove_opzioni = dati["opzioni"]

        aggiorna_opzioni(domanda, nuove_opzioni)
        aggiorna_risposta_corretta(domanda, nuove_opzioni[0])
        domanda["spiegazione"] = dati["spiegazione"]
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve condividere il concetto centrale della corretta "
            "e diventare sbagliata per un dettaglio tecnico, logico o pratico."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Informatica - terzo blocco distrattori forti",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: stesso concetto centrale, stesso contesto, piccolo dettaglio sbagliato.",
        "",
        f"Domande aggiornate: {len(aggiornate)}",
        "",
    ]

    for id_domanda in aggiornate:
        righe.append(f"- {id_domanda}")

    if non_trovate:
        righe.append("")
        righe.append("## ID non trovati")
        righe.append("")

        for id_domanda in non_trovate:
            righe.append(f"- {id_domanda}")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== MIGLIORAMENTO INFORMATICA - TERZO BLOCCO =====")
    print(f"Domande aggiornate: {len(aggiornate)}")

    for id_domanda in aggiornate:
        print(f"- {id_domanda}")

    if non_trovate:
        print()
        print("ID non trovati:")

        for id_domanda in non_trovate:
            print(f"- {id_domanda}")

    print()
    print(f"Report creato: {REPORT}")
    print("OK: terzo blocco Informatica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
