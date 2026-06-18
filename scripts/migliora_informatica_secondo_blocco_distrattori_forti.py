import json
from pathlib import Path

FILE = Path("data/informatica.json")
BACKUP = Path("data/informatica.backup_prima_secondo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_informatica_secondo_blocco_distrattori_forti.md")

PATCH = {
    "INF-FAC-0101": {
        "opzioni": [
            "Eseguire istruzioni ed elaborare operazioni",
            "Elaborare operazioni del computer, ma conservando temporaneamente i dati dei programmi",
            "Gestire istruzioni e calcoli, ma archiviando file e programmi anche a computer spento",
            "Eseguire operazioni principali, ma occupandosi soprattutto dei calcoli grafici delle immagini"
        ],
        "spiegazione": (
            "La CPU è il processore principale: esegue istruzioni ed elabora operazioni. "
            "La RAM conserva dati temporanei, SSD e hard disk archiviano file in modo permanente, mentre la GPU è specializzata soprattutto nell'elaborazione grafica."
        )
    },

    "INF-INT-0101": {
        "opzioni": [
            "Permette di raggruppare istruzioni riutilizzabili con un compito chiaro",
            "Permette di raggruppare istruzioni, ma senza ricevere dati o restituire risultati",
            "Rende il codice più ordinato, ma serve principalmente ad allungare il programma",
            "Raggruppa istruzioni riutilizzabili, ma sostituisce la necessità di usare variabili"
        ],
        "spiegazione": (
            "Una funzione è utile perché raggruppa istruzioni riutilizzabili con un compito chiaro. "
            "Può ricevere dati, restituire risultati e ridurre ripetizioni; non serve ad allungare il codice e non sostituisce le variabili."
        )
    },

    "INF-AV-0101": {
        "opzioni": [
            "Perché i dati inviati al server non devono essere considerati affidabili solo perché il frontend li controlla",
            "Perché il frontend può controllare i dati, ma quei controlli possono essere aggirati prima dell'invio",
            "Perché il backend deve validare i dati, ma questo sostituisce i test automatici dell'applicazione",
            "Perché il frontend può mostrare errori all'utente, ma il server deve ignorare i dati già controllati"
        ],
        "spiegazione": (
            "La validazione deve avvenire anche lato backend perché i dati inviati al server non sono affidabili solo perché il frontend li controlla. "
            "I controlli frontend migliorano l'esperienza utente, ma possono essere aggirati; il backend protegge regole, applicazione e database."
        )
    },

    "INF-FAC-0102": {
        "opzioni": [
            "A salvare dati e programmi anche quando il computer è spento",
            "A conservare dati del computer in modo stabile, ma solo finché i programmi restano aperti",
            "A salvare file e programmi, ma eseguendo direttamente le istruzioni principali della CPU",
            "A mantenere dati anche a computer spento, ma principalmente per i calcoli grafici della scheda video"
        ],
        "spiegazione": (
            "Un SSD serve principalmente a salvare dati e programmi anche quando il computer è spento. "
            "Non è memoria temporanea come la RAM, non esegue le istruzioni della CPU e non è la memoria usata soprattutto dalla scheda video."
        )
    },

    "INF-INT-0102": {
        "opzioni": [
            "A leggere dati da una o più tabelle",
            "A leggere dati da tabelle, ma solo se non vengono usate condizioni o collegamenti",
            "A interrogare il database, ma cancellando i record che non rispettano la condizione",
            "A ottenere dati con SQL, ma trasformando direttamente il risultato in struttura HTML"
        ],
        "spiegazione": (
            "SELECT serve a leggere dati da una o più tabelle. "
            "Può usare condizioni, ordinamenti e join; non cancella dati e non trasforma direttamente SQL in HTML."
        )
    },

    "INF-AV-0102": {
        "opzioni": [
            "L'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave",
            "L'hashing protegge dati, ma può essere riportato al valore originale usando una chiave corretta",
            "La cifratura protegge dati, ma serve solo a confrontare se due valori producono la stessa impronta",
            "Hashing e cifratura proteggono dati, ma entrambi permettono di recuperare il testo originale con una chiave"
        ],
        "spiegazione": (
            "La differenza importante è che l'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave. "
            "Gli hash sono utili per impronte e verifiche, la cifratura per proteggere dati che devono poter essere recuperati."
        )
    },

    "INF-FAC-0103": {
        "opzioni": [
            "Il software che gestisce risorse del computer e permette di usare programmi",
            "Un programma che gestisce alcune risorse, ma svolge un solo compito specifico dell'utente",
            "Un software di base del computer, ma coincidente con un componente hardware di archiviazione",
            "Un ambiente che permette di usare programmi, ma rappresentato solo da una cartella di file personali"
        ],
        "spiegazione": (
            "Un sistema operativo è il software che gestisce risorse del computer e permette di usare programmi. "
            "Non è una singola applicazione, non è un componente hardware e non coincide con una cartella di file personali."
        )
    },

    "INF-INT-0103": {
        "opzioni": [
            "Per combinare dati collegati provenienti da tabelle diverse",
            "Per combinare dati di tabelle diverse, ma creando relazioni anche quando non esiste alcun collegamento",
            "Per unire informazioni tra tabelle, ma rinominando automaticamente tutti i campi coinvolti",
            "Per collegare tabelle relazionali, ma eliminando il bisogno di chiavi primarie o esterne"
        ],
        "spiegazione": (
            "Un JOIN si usa per combinare dati collegati provenienti da tabelle diverse. "
            "Non crea relazioni senza collegamenti logici, non rinomina automaticamente i campi e non elimina il ruolo delle chiavi."
        )
    },

    "INF-AV-0103": {
        "opzioni": [
            "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
            "Perché conserva dati usati spesso, ma garantisce che non diventino mai vecchi",
            "Perché riduce accessi ripetuti a dati frequenti, ma sposta ogni dato del database in memoria locale",
            "Perché migliora le prestazioni, ma anche quando i dati salvati non vengono riutilizzati"
        ],
        "spiegazione": (
            "La cache può migliorare le prestazioni perché evita di ricalcolare o recuperare più volte dati usati spesso. "
            "Va gestita bene perché può diventare non aggiornata; non sposta tutto il database in memoria e non aiuta se i dati non vengono riutilizzati."
        )
    },

    "INF-FAC-0104": {
        "opzioni": [
            "A ripetere un blocco di istruzioni più volte",
            "A scegliere tra due rami di codice, ma senza ripetere automaticamente le istruzioni",
            "A ripetere istruzioni, ma salvando prima un file in modo permanente",
            "A controllare una condizione, ma cancellando tutte le variabili a ogni passaggio"
        ],
        "spiegazione": (
            "Un ciclo serve normalmente a ripetere un blocco di istruzioni più volte. "
            "Una condizione sceglie quale ramo eseguire, ma non ripete da sola il blocco; salvare file o cancellare variabili sono operazioni diverse."
        )
    },

    "INF-INT-0104": {
        "opzioni": [
            "La risorsa richiesta non è stata trovata sul server",
            "La richiesta non è autenticata correttamente, quindi il server non identifica l'utente",
            "L'utente è riconosciuto, ma non ha i permessi per accedere alla risorsa",
            "Il server ha ricevuto la richiesta, ma ha generato un errore interno"
        ],
        "spiegazione": (
            "Una risposta HTTP 404 indica di solito che la risorsa richiesta non è stata trovata sul server. "
            "401 riguarda l'autenticazione, 403 i permessi insufficienti e 500 un errore interno del server."
        )
    },

    "INF-AV-0104": {
        "opzioni": [
            "Per dividere i risultati in blocchi più piccoli e gestibili",
            "Per restituire meno dati per risposta, ma mantenendo accessibili anche gli altri risultati",
            "Per organizzare molti risultati in pagine, ma impedendo all'API di restituire dati successivi",
            "Per ridurre la dimensione della risposta, ma trasformando i risultati mancanti in errore 404"
        ],
        "spiegazione": (
            "La paginazione è utile perché divide molti risultati in blocchi più piccoli e gestibili. "
            "Riduce il carico della risposta, migliora prestazioni e usabilità, ma non impedisce di accedere alle pagine successive."
        )
    },

    "INF-FAC-0105": {
        "opzioni": [
            "Un valore che può essere vero o falso",
            "Un valore con due stati logici, ma usato principalmente per contare alternative numeriche",
            "Un dato che rappresenta vero o falso, ma salvato come stringa di testo generica",
            "Un valore logico, ma usato per indicare assenza completa di informazione"
        ],
        "spiegazione": (
            "Un valore booleano rappresenta normalmente un valore che può essere vero o falso. "
            "Non è un numero usato per contare, non è una stringa generica e non coincide con un valore nullo o assente."
        )
    },

    "INF-INT-0105": {
        "opzioni": [
            "A lavorare su una linea separata di sviluppo senza modificare subito quella principale",
            "A salvare una fotografia del progetto nella cronologia, ma senza creare una linea separata",
            "A creare una linea separata, ma solo per scaricare librerie mancanti dal repository remoto",
            "A separare modifiche del progetto, ma trasformando il repository in una tabella SQL"
        ],
        "spiegazione": (
            "Un branch in Git serve a lavorare su una linea separata di sviluppo senza modificare subito quella principale. "
            "Un commit salva uno stato nella cronologia, mentre scaricare librerie o trasformare il repository in SQL non riguarda i branch."
        )
    },

    "INF-AV-0105": {
        "opzioni": [
            "Automatizza controlli, test e rilascio riducendo errori manuali ripetitivi",
            "Automatizza test e build, ma sostituisce anche la necessità di progettare bene il codice",
            "Riduce passaggi manuali nel rilascio, ma impedisce a più sviluppatori di collaborare",
            "Esegue controlli automatici, ma elimina il bisogno di verificare i risultati dei test"
        ],
        "spiegazione": (
            "Una pipeline CI/CD automatizza controlli, test e rilascio riducendo errori manuali ripetitivi. "
            "Non sostituisce la progettazione o la scrittura del codice, non blocca la collaborazione e non elimina la necessità di interpretare i risultati dei test."
        )
    },

    "INF-FAC-0106": {
        "opzioni": [
            "La posizione del file dentro cartelle e sottocartelle",
            "Il nome del file, ma senza indicare in quali cartelle si trova",
            "L'indicazione di dove si trova il file, ma riferita solo alla velocità di apertura",
            "La posizione del file, ma calcolata dal numero di volte in cui è stato copiato"
        ],
        "spiegazione": (
            "Il percorso di un file indica la sua posizione dentro cartelle e sottocartelle. "
            "Il solo nome non basta a indicare dove si trova; velocità di apertura e numero di copie non definiscono il percorso."
        )
    },

    "INF-INT-0106": {
        "opzioni": [
            "Per proteggere la comunicazione tra browser e server tramite cifratura",
            "Per usare un certificato digitale, ma senza cifrare davvero lo scambio dei dati",
            "Per migliorare la sicurezza della comunicazione, ma rendendo il sito indipendente dal server",
            "Per proteggere i dati in transito, ma impedendo al server di ricevere richieste dal browser"
        ],
        "spiegazione": (
            "HTTPS è importante perché protegge la comunicazione tra browser e server tramite cifratura. "
            "I certificati aiutano a stabilire fiducia, ma il punto centrale è proteggere i dati in transito."
        )
    },

    "INF-AV-0106": {
        "opzioni": [
            "Perché include applicazione e dipendenze in un ambiente isolato e riproducibile",
            "Perché include applicazione e dipendenze, ma aggiorna le librerie a ogni avvio",
            "Perché rende l'ambiente più prevedibile, ma installa da solo ogni libreria mancante durante l'esecuzione",
            "Perché isola l'applicazione, ma modifica l'ambiente del computer host per uniformarlo al container"
        ],
        "spiegazione": (
            "Un container rende più prevedibile l'esecuzione perché include applicazione e dipendenze in un ambiente isolato e riproducibile. "
            "Non aggiorna automaticamente tutte le librerie, non installa dipendenze mancanti a ogni avvio e non deve modificare l'host per funzionare."
        )
    },

    "INF-INT-0107": {
        "opzioni": [
            "Far adattare layout e contenuti a schermi di dimensioni diverse",
            "Adattare la pagina agli schermi, ma cambiando solo le immagini e non il layout",
            "Rendere la pagina adatta a dispositivi diversi, ma restituendo lo stesso codice HTTP in ogni caso",
            "Migliorare l'uso su smartphone, ma impedendo l'apertura da desktop o tablet"
        ],
        "spiegazione": (
            "Rendere una pagina responsive significa far adattare layout e contenuti a schermi di dimensioni diverse. "
            "Non riguarda solo le immagini, non dipende dai codici HTTP e non impedisce l'uso da altri dispositivi."
        )
    },

    "INF-AV-0107": {
        "opzioni": [
            "Perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine",
            "Perché conferma ogni modifica appena viene eseguita, anche se una fase successiva fallisce",
            "Perché raggruppa più operazioni, ma non consente di annullarle se una parte non riesce",
            "Perché controlla il risultato complessivo, ma corregge da sola query scritte con logica sbagliata"
        ],
        "spiegazione": (
            "Una transazione è utile perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine. "
            "Se una parte fallisce, si può annullare il gruppo di operazioni per evitare dati parziali o incoerenti."
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
        "# Miglioramento Informatica - secondo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INFORMATICA - SECONDO BLOCCO =====")
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
    print("OK: secondo blocco Informatica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
