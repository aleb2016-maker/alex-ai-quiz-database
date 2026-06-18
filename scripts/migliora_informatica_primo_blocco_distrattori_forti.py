import json
from pathlib import Path

FILE = Path("data/informatica.json")
BACKUP = Path("data/informatica.backup_prima_primo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_informatica_primo_blocco_distrattori_forti.md")

PATCH = {
    "INF-FAC-0001": {
        "opzioni": [
            "Conservare temporaneamente i dati usati dai programmi in esecuzione",
            "Conservare dati durante l'esecuzione, ma mantenerli disponibili anche a computer spento",
            "Memorizzare dati usati spesso dalla CPU, ma solo nella memoria interna del processore",
            "Gestire dati temporanei dei programmi, ma principalmente per elaborarli nella scheda video"
        ],
        "spiegazione": (
            "La RAM conserva temporaneamente i dati usati dai programmi in esecuzione. "
            "Non è memoria permanente come SSD o hard disk, non coincide con la cache della CPU e non è la memoria video della scheda grafica."
        )
    },

    "INF-INT-0002": {
        "opzioni": [
            "A identificare in modo univoco ogni record di una tabella",
            "A identificare i record, ma solo quando una tabella viene collegata a un'altra tramite chiave esterna",
            "A rendere riconoscibile una riga, ma senza impedire che due record abbiano lo stesso valore",
            "A definire un campo importante della tabella, ma lasciandolo facoltativo nei record"
        ],
        "spiegazione": (
            "Una chiave primaria serve a identificare in modo univoco ogni record di una tabella. "
            "Non è una chiave esterna, non può permettere duplicati sull'identità del record e non dovrebbe essere un campo facoltativo."
        )
    },

    "INF-AV-0003": {
        "opzioni": [
            "Permettere a frontend e backend di comunicare tramite richieste HTTP strutturate",
            "Permettere al frontend di comunicare con il backend, ma leggendo direttamente le tabelle del database",
            "Organizzare richieste HTTP tra client e server, ma lasciando la logica applicativa nel browser",
            "Esporre dati e operazioni al frontend, ma sostituendo completamente il controllo del backend"
        ],
        "spiegazione": (
            "Un'API REST permette a frontend e backend di comunicare tramite richieste HTTP strutturate. "
            "Il frontend non dovrebbe leggere direttamente il database, la logica applicativa resta controllata dal backend e l'API non elimina i controlli server."
        )
    },

    "INF-FAC-0004": {
        "opzioni": [
            "HTML",
            "CSS",
            "JavaScript",
            "SQL"
        ],
        "spiegazione": (
            "HTML è il linguaggio usato principalmente per definire la struttura di una pagina web. "
            "CSS gestisce l'aspetto grafico, JavaScript aggiunge comportamento e interattività, SQL serve per lavorare con database."
        )
    },

    "INF-INT-0004": {
        "opzioni": [
            "GET",
            "POST",
            "PUT",
            "PATCH"
        ],
        "spiegazione": (
            "GET viene usato di solito per ottenere dati senza modificarli. "
            "POST invia o crea dati, PUT sostituisce una risorsa e PATCH aggiorna parzialmente una risorsa."
        )
    },

    "INF-AV-0004": {
        "opzioni": [
            "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
            "Perché il frontend può cambiare, ma solo se il backend espone direttamente le tabelle interne",
            "Perché backend e frontend hanno responsabilità distinte, ma devono essere modificati sempre insieme",
            "Perché l'interfaccia può usare API, ma la logica applicativa viene spostata interamente nel browser"
        ],
        "spiegazione": (
            "Separare frontend e backend rende un'applicazione più gestibile perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare. "
            "Non significa esporre tabelle interne, non obbliga a modificare tutto insieme e non sposta tutta la logica nel browser."
        )
    },

    "INF-FAC-0005": {
        "opzioni": [
            "Un insieme organizzato di righe e colonne",
            "Un insieme di dati organizzati, ma formato da una sola riga della base dati",
            "Una struttura con righe e colonne, ma usata solo per collegare due database diversi",
            "Una raccolta ordinata di dati, ma coincidente con una query di filtro"
        ],
        "spiegazione": (
            "In un database, una tabella rappresenta normalmente un insieme organizzato di righe e colonne. "
            "Una singola riga è un record, una relazione collega tabelle diverse e una query serve a leggere o filtrare dati."
        )
    },

    "INF-INT-0005": {
        "opzioni": [
            "A collegare un record di una tabella a un record di un'altra tabella",
            "A collegare tabelle diverse, ma identificando in modo univoco i record della tabella corrente",
            "A creare una relazione tra tabelle, ma senza riferirsi a una chiave presente nell'altra tabella",
            "A collegare dati tra tabelle, ma trasformando automaticamente il risultato in formato JSON"
        ],
        "spiegazione": (
            "Una chiave esterna serve a collegare un record di una tabella a un record di un'altra tabella. "
            "La chiave primaria identifica i record della tabella corrente, mentre una chiave esterna richiama un riferimento presente altrove."
        )
    },

    "INF-AV-0005": {
        "opzioni": [
            "La richiesta non è autenticata correttamente",
            "La richiesta è autenticata, ma l'utente non ha i permessi necessari",
            "La richiesta è valida, ma la risorsa indicata non è stata trovata",
            "La richiesta arriva al server, ma produce un errore interno non legato all'autenticazione"
        ],
        "spiegazione": (
            "Una risposta HTTP 401 indica di solito che la richiesta non è autenticata correttamente. "
            "403 riguarda permessi insufficienti dopo l'autenticazione, 404 una risorsa non trovata e 500 un errore interno del server."
        )
    },

    "INF-FAC-0006": {
        "opzioni": [
            "A conservare un valore che può essere usato o modificato",
            "A conservare un valore nel programma, ma senza poterlo leggere in istruzioni successive",
            "A dare un nome a un valore, ma solo per definire una funzione riutilizzabile",
            "A memorizzare un valore, ma principalmente per ripetere automaticamente un blocco di codice"
        ],
        "spiegazione": (
            "Una variabile serve a conservare un valore che può essere usato o modificato durante il programma. "
            "Non è una funzione, non è un ciclo e non serve solo a dichiarare qualcosa senza poterlo riutilizzare."
        )
    },

    "INF-INT-0006": {
        "opzioni": [
            "Gestire l'aspetto visivo degli elementi",
            "Definire la struttura della pagina, ma occupandosi anche di colori e spaziature",
            "Gestire lo stile degli elementi, ma eseguendo la logica interattiva nel browser",
            "Controllare layout e colori, ma recuperando direttamente i dati dal database"
        ],
        "spiegazione": (
            "Il ruolo principale del CSS è gestire l'aspetto visivo degli elementi: stile, colori, layout e spaziature. "
            "HTML definisce la struttura, JavaScript gestisce l'interattività e l'accesso al database appartiene di solito al backend."
        )
    },

    "INF-AV-0006": {
        "opzioni": [
            "Rendere più veloci alcune ricerche su quella colonna",
            "Rendere più veloci alcune ricerche, ma senza aumentare spazio usato o costo delle scritture",
            "Velocizzare le ricerche sulla colonna, ma eliminando automaticamente le righe duplicate",
            "Migliorare l'accesso ai dati, ma normalizzando da solo la struttura della tabella"
        ],
        "spiegazione": (
            "Un indice su una colonna molto cercata può rendere più veloci alcune ricerche su quella colonna. "
            "Può però aumentare lo spazio usato e rendere più costose alcune scritture; non elimina duplicati e non normalizza automaticamente i dati."
        )
    },

    "INF-FAC-0007": {
        "opzioni": [
            "L'indirizzo di una risorsa sul web",
            "La parte dell'indirizzo che indica solo il protocollo di comunicazione",
            "Il nome del dominio, ma senza percorso, parametri o risorsa specifica",
            "Il codice numerico che il server restituisce dopo aver ricevuto una richiesta"
        ],
        "spiegazione": (
            "Un URL indica l'indirizzo di una risorsa sul web. "
            "Può includere protocollo, dominio, percorso e parametri; il codice di stato invece appartiene alla risposta del server."
        )
    },

    "INF-INT-0007": {
        "opzioni": [
            "Individuare e correggere errori nel comportamento del codice",
            "Osservare l'esecuzione del programma, ma senza modificare il codice che causa l'errore",
            "Controllare valori intermedi del programma, ma senza collegarli alla correzione finale",
            "Riprodurre un problema in modo stabile, ma fermandosi prima di capire quale istruzione lo provoca"
        ],
        "spiegazione": (
            "Fare debug significa individuare e correggere errori nel comportamento del codice. "
            "Osservare l'esecuzione, controllare valori e riprodurre il problema sono tecniche utili, ma il debug include anche la correzione."
        )
    },

    "INF-AV-0007": {
        "opzioni": [
            "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
            "Perché possono agire sullo stesso dato nello stesso momento, ma senza rischiare aggiornamenti persi",
            "Perché possono creare conflitti sui dati, ma vengono risolte senza transazioni o isolamento",
            "Perché possono sovrapporsi sullo stesso dato, ma il risultato resta coerente anche senza controllo"
        ],
        "spiegazione": (
            "Due operazioni simultanee sullo stesso dato possono creare problemi perché possono produrre risultati incoerenti se non vengono gestite correttamente. "
            "Servono meccanismi come transazioni, isolamento o controlli di concorrenza per evitare conflitti e aggiornamenti persi."
        )
    },

    "INF-FAC-0008": {
        "opzioni": [
            "JSON",
            "XML",
            "YAML",
            "CSV"
        ],
        "spiegazione": (
            "JSON è molto usato nelle API web per rappresentare oggetti, liste e coppie chiave-valore. "
            "XML e YAML possono rappresentare dati strutturati, mentre CSV è più adatto a dati tabellari semplici."
        )
    },

    "INF-INT-0008": {
        "opzioni": [
            "Una fotografia salvata dello stato del progetto nella cronologia Git",
            "Una fotografia dello stato del progetto, ma temporanea e non inserita nella cronologia",
            "Un punto salvato nella cronologia, ma usato principalmente per creare un ramo separato",
            "Una versione del progetto, ma scaricata dal repository remoto invece che registrata localmente"
        ],
        "spiegazione": (
            "In Git, un commit è una fotografia salvata dello stato del progetto nella cronologia. "
            "Non è un salvataggio temporaneo, non coincide con un branch e non è il comando per scaricare modifiche dal remoto."
        )
    },

    "INF-AV-0008": {
        "opzioni": [
            "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
            "Perché il test confronta il risultato reale con quello atteso, ma senza condizioni ripetibili",
            "Perché il test deve sapere cosa aspettarsi, ma può ignorare se il comportamento è corretto",
            "Perché il test deve fallire in caso di errore, ma senza definire prima il risultato previsto"
        ],
        "spiegazione": (
            "Un test automatico utile deve avere un risultato atteso ben definito perché deve poter stabilire se il comportamento ottenuto è corretto o no. "
            "Senza risultato atteso, il test non può confrontare in modo affidabile ciò che accade con ciò che dovrebbe accadere."
        )
    },

    "INF-INT-0009": {
        "opzioni": [
            "Perché possono finire in repository, log o copie condivise del progetto",
            "Perché possono essere lette se il codice viene pubblicato, ma non se resta in un repository privato",
            "Perché rendono difficile cambiare credenziali tra ambienti, ma senza rischi di esposizione",
            "Perché possono esporre accessi a servizi esterni, ma solo quando il progetto è già in produzione"
        ],
        "spiegazione": (
            "Salvare password direttamente nel codice è rischioso perché possono finire in repository, log, backup o copie condivise del progetto. "
            "Anche repository privati, ambienti di test e copie locali possono diventare punti di esposizione."
        )
    },

    "INF-AV-0009": {
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Permette di separare configurazioni dal codice, ma salvandole comunque nel repository",
            "Permette di cambiare configurazioni tra ambienti, ma richiede di modificare i file sorgente",
            "Permette di nascondere credenziali nel codice, ma lasciandole leggibili durante il commit"
        ],
        "spiegazione": (
            "Una variabile d'ambiente è utile perché permette di separare configurazioni sensibili o diverse dal codice sorgente. "
            "Aiuta a gestire ambienti diversi e credenziali senza scriverle direttamente nei file del progetto."
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
        "# Miglioramento Informatica - primo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INFORMATICA - PRIMO BLOCCO =====")
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
    print("OK: primo blocco Informatica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
