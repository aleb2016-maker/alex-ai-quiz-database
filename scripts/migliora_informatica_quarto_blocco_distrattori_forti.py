import json
from pathlib import Path

FILE = Path("data/informatica.json")
BACKUP = Path("data/informatica.backup_prima_quarto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_informatica_quarto_blocco_distrattori_forti.md")

PATCH = {
    "INF-INT-0209": {
        "opzioni": [
            "A verificare il comportamento di una piccola parte del codice in modo controllato",
            "A verificare una parte limitata del codice, ma sostituendo la documentazione tecnica del progetto",
            "A controllare una porzione di codice, ma pubblicando direttamente l'applicazione sugli store",
            "A provare il comportamento del codice, ma modificando la risoluzione delle immagini dell'interfaccia"
        ],
        "spiegazione": (
            "Un test unitario serve a verificare il comportamento di una piccola parte del codice in modo controllato. "
            "Non sostituisce la documentazione, non pubblica l'applicazione e non riguarda la risoluzione delle immagini."
        )
    },

    "INF-INT-0210": {
        "opzioni": [
            "Un ambiente isolato e riproducibile con dipendenze definite",
            "Un ambiente isolato con dipendenze definite, ma usato per disegnare icone senza codice",
            "Un ambiente riproducibile per l'applicazione, ma capace di aumentare la RAM fisica del computer",
            "Un ambiente con dipendenze controllate, ma pensato per evitare la configurazione di porte o variabili"
        ],
        "spiegazione": (
            "Docker offre un ambiente isolato e riproducibile con dipendenze definite. "
            "Non serve a disegnare icone, non aumenta la RAM fisica e non elimina la necessità di configurare porte o variabili quando servono."
        )
    },

    "INF-INT-0211": {
        "opzioni": [
            "Nel modello sincrono si attende il completamento dell'operazione, mentre nell'asincrono il programma può proseguire e gestire il risultato dopo",
            "Nel modello sincrono si attende l'operazione, ma nell'asincrono il risultato non può essere gestito dal programma",
            "Nel modello asincrono il programma può proseguire, ma questo dipende dal fatto che il codice usi immagini invece di dati",
            "Nel modello sincrono il flusso attende, ma l'esecuzione avviene senza usare il processore"
        ],
        "spiegazione": (
            "Nell'esecuzione sincrona il programma attende il completamento dell'operazione; nell'esecuzione asincrona può proseguire e gestire il risultato dopo. "
            "Il concetto riguarda il flusso di esecuzione, non immagini, assenza di processore o impossibilità di gestire risultati."
        )
    },

    "INF-INT-0212": {
        "opzioni": [
            "Tornare a una versione precedente o a uno stato stabile quando una modifica crea problemi",
            "Tornare a uno stato precedente, ma aggiungendo nuove funzionalità senza controllare il comportamento",
            "Ripristinare una versione stabile, ma duplicando i file senza sapere quale versione usare",
            "Rientrare da una modifica problematica, ma cambiando solo il nome del repository"
        ],
        "spiegazione": (
            "Un rollback significa tornare a una versione precedente o a uno stato stabile quando una modifica crea problemi. "
            "Non significa aggiungere funzionalità senza controllo, duplicare file in modo confuso o cambiare solo il nome del repository."
        )
    },

    "INF-INT-0213": {
        "opzioni": [
            "Perché aiuta il database a trovare righe senza dover scandire molti dati inutilmente",
            "Perché aiuta il database a trovare righe, ma trasformando la query in codice JavaScript",
            "Perché migliora alcune ricerche, ma sostituisce le relazioni tra tabelle con immagini",
            "Perché velocizza l'accesso ad alcuni dati, ma elimina il bisogno di progettare bene le tabelle"
        ],
        "spiegazione": (
            "Un indice può rendere più veloce una query SQL perché aiuta il database a trovare righe senza scandire molti dati inutilmente. "
            "Non trasforma SQL in JavaScript, non sostituisce relazioni con immagini e non elimina la necessità di progettare bene le tabelle."
        )
    },

    "INF-INT-0214": {
        "opzioni": [
            "Per ridurre errori, dati non coerenti e possibili vulnerabilità",
            "Per controllare i dati inseriti, ma impedendo all'utente di interagire con l'interfaccia",
            "Per migliorare sicurezza e coerenza, ma sostituendo il backend con una pagina statica",
            "Per verificare l'input dell'utente, ma rendendo il codice meno leggibile durante la manutenzione"
        ],
        "spiegazione": (
            "Validare l'input dell'utente è importante per ridurre errori, dati non coerenti e possibili vulnerabilità. "
            "Non deve impedire l'interazione, non sostituisce il backend e non dovrebbe peggiorare la manutenzione del codice."
        )
    },

    "INF-AV-0201": {
        "opzioni": [
            "Che ripetere la stessa richiesta produce lo stesso effetto sullo stato del sistema",
            "Che ripetere la stessa richiesta produce lo stesso effetto, ma solo se contiene un'immagine allegata",
            "Che la richiesta può essere ripetuta, ma il server risponde con dati casuali per aumentare la sicurezza",
            "Che l'effetto resta controllato, ma il client deve aprire una porta diversa per ogni carattere inviato"
        ],
        "spiegazione": (
            "Un'operazione HTTP idempotente produce lo stesso effetto sullo stato del sistema anche se la stessa richiesta viene ripetuta. "
            "Il concetto non dipende da immagini, risposte casuali o porte di rete aperte per carattere."
        )
    },

    "INF-AV-0202": {
        "opzioni": [
            "Un problema in cui il risultato dipende dall'ordine temporale non controllato di operazioni concorrenti",
            "Un problema di concorrenza, ma risolto ordinando alfabeticamente i file sorgente",
            "Una condizione legata all'ordine delle operazioni, ma usata per animare pulsanti in sequenza",
            "Un errore dovuto a operazioni concorrenti, ma limitato alla scelta del font dell'interfaccia"
        ],
        "spiegazione": (
            "Una race condition è un problema in cui il risultato dipende dall'ordine temporale non controllato di operazioni concorrenti. "
            "Non riguarda l'ordine alfabetico dei file, animazioni grafiche o scelta dei font."
        )
    },

    "INF-AV-0203": {
        "opzioni": [
            "Perché permette di fornire dipendenze dall'esterno e sostituirle con versioni controllate nei test",
            "Perché fornisce dipendenze dall'esterno, ma obbliga a scrivere il codice in una sola classe",
            "Perché rende sostituibili alcune dipendenze, ma impedisce l'uso di interfacce tra componenti",
            "Perché aiuta i test usando dipendenze controllate, ma elimina la separazione delle responsabilità"
        ],
        "spiegazione": (
            "La dependency injection può rendere un'applicazione più testabile perché permette di fornire dipendenze dall'esterno e sostituirle con versioni controllate nei test. "
            "Non obbliga a usare una sola classe, non impedisce le interfacce e non elimina la separazione delle responsabilità."
        )
    },

    "INF-AV-0204": {
        "opzioni": [
            "Le operazioni di lettura dei dati dalle operazioni di modifica dello stato",
            "Le operazioni di lettura e scrittura, ma separando fisicamente tastiera e monitor",
            "Query e comandi dell'applicazione, ma dividendo il codice sorgente dai commenti",
            "Letture e modifiche dello stato, ma separando immagini statiche e colori del tema grafico"
        ],
        "spiegazione": (
            "Il pattern CQRS cerca di separare le operazioni di lettura dei dati dalle operazioni di modifica dello stato. "
            "Non riguarda periferiche fisiche, commenti del codice o elementi grafici del tema."
        )
    },

    "INF-AV-0205": {
        "opzioni": [
            "Per ridurre ridondanze e anomalie organizzando i dati in tabelle coerenti",
            "Per organizzare meglio i dati, ma salvando ogni informazione in una singola colonna di testo",
            "Per ridurre anomalie nei dati, ma evitando chiavi primarie e relazioni tra tabelle",
            "Per rendere più coerente il database, ma trasformando automaticamente SQL in codice HTML"
        ],
        "spiegazione": (
            "La normalizzazione può essere utile perché riduce ridondanze e anomalie organizzando i dati in tabelle coerenti. "
            "Non significa mettere tutto in una sola colonna, evitare chiavi e relazioni o trasformare SQL in HTML."
        )
    },

    "INF-AV-0206": {
        "opzioni": [
            "Un modello in cui le repliche possono allinearsi dopo un intervallo, invece di essere aggiornate nello stesso istante",
            "Un modello di allineamento tra repliche, ma basato sul salvataggio dei dati in un unico file locale",
            "Un modello per sistemi distribuiti, ma usato per impedire la comunicazione tra servizi diversi",
            "Una forma di consistenza dei dati, ma descritta come formato grafico per schermate mobili"
        ],
        "spiegazione": (
            "La consistenza eventuale indica un modello in cui le repliche possono allinearsi dopo un intervallo invece di essere aggiornate nello stesso istante. "
            "Non significa usare un unico file locale, bloccare la comunicazione tra servizi o descrivere formati grafici."
        )
    },

    "INF-AV-0207": {
        "opzioni": [
            "A distribuire le richieste tra più istanze o server per migliorare disponibilità e gestione del carico",
            "A distribuire traffico tra server, ma correggendo automaticamente errori logici nel codice",
            "A gestire il carico tra istanze, ma sostituendo il database con memoria temporanea nel browser",
            "A smistare richieste HTTP, ma convertendole in immagini vettoriali prima dell'elaborazione"
        ],
        "spiegazione": (
            "Un load balancer serve a distribuire le richieste tra più istanze o server per migliorare disponibilità e gestione del carico. "
            "Non corregge automaticamente il codice, non sostituisce il database e non converte richieste in immagini."
        )
    },

    "INF-AV-0208": {
        "opzioni": [
            "Automatizzare integrazione, test e distribuzione del software in modo controllato",
            "Automatizzare build e test, ma disegnando anche il logo dell'applicazione",
            "Automatizzare il rilascio, ma rimuovendo la necessità di revisionare modifiche importanti",
            "Automatizzare la distribuzione, ma impedendo al team di eseguire test prima della pubblicazione"
        ],
        "spiegazione": (
            "Lo scopo principale di una pipeline CI/CD è automatizzare integrazione, test e distribuzione del software in modo controllato. "
            "Non disegna loghi, non elimina le revisioni importanti e non impedisce di eseguire test."
        )
    },

    "INF-AV-0209": {
        "opzioni": [
            "Per verificare firma, scadenza e coerenza dei dati dichiarati nel token",
            "Per controllare firma e scadenza del token, ma cambiandone il colore prima di mostrarlo",
            "Per validare i dati dichiarati nel token, ma trasformandolo in una tabella SQL permanente",
            "Per fidarsi del token in modo controllato, ma evitando di usare HTTPS nelle comunicazioni"
        ],
        "spiegazione": (
            "Un JWT deve essere validato dal server per verificare firma, scadenza e coerenza dei dati dichiarati nel token. "
            "Non va accettato sulla fiducia, e la validazione non sostituisce HTTPS né trasforma il token in una tabella SQL."
        )
    },

    "INF-AV-0210": {
        "opzioni": [
            "Per disaccoppiare servizi e gestire lavori asincroni con maggiore resilienza",
            "Per disaccoppiare servizi, ma sostituendo ogni database relazionale con un file di testo",
            "Per gestire lavori asincroni, ma obbligando i servizi a rispondere nello stesso millisecondo",
            "Per rendere più resiliente il sistema, ma eliminando la gestione di errori o ritentativi"
        ],
        "spiegazione": (
            "Una coda di messaggi può aiutare perché disaccoppia servizi e gestisce lavori asincroni con maggiore resilienza. "
            "Non sostituisce i database, non obbliga risposte simultanee e non elimina la gestione di errori o ritentativi."
        )
    },

    "INF-AV-0211": {
        "opzioni": [
            "Una situazione in cui processi o thread restano bloccati perché attendono risorse trattenute reciprocamente",
            "Una situazione di blocco tra processi, ma usata per migliorare la qualità grafica delle icone",
            "Un blocco legato a risorse trattenute, ma generato durante l'apertura del browser come file temporaneo",
            "Una condizione di attesa tra thread, ma usata come metodo per comprimere log senza perdere contenuto"
        ],
        "spiegazione": (
            "Un deadlock è una situazione in cui processi o thread restano bloccati perché attendono risorse trattenute reciprocamente. "
            "Non riguarda qualità grafica, file temporanei del browser o compressione dei log."
        )
    },

    "INF-AV-0212": {
        "opzioni": [
            "Aggiungere più istanze del servizio per distribuire il carico",
            "Aumentare la capacità del servizio, ma modificando soltanto la dimensione del monitor del server",
            "Distribuire il carico su più istanze, ma spostando tutte le funzioni in un solo metodo lungo",
            "Aggiungere istanze del servizio, ma riducendo il numero di utenti supportati dall'applicazione"
        ],
        "spiegazione": (
            "Scalare orizzontalmente un servizio significa aggiungere più istanze del servizio per distribuire il carico. "
            "Non riguarda il monitor, non significa concentrare tutto in un metodo lungo e non riduce gli utenti supportati."
        )
    },

    "INF-AV-0213": {
        "opzioni": [
            "Per capire lo stato del sistema usando log, metriche e tracce quando emergono problemi",
            "Per osservare il sistema in produzione, ma nascondendo gli errori agli sviluppatori durante il debug",
            "Per raccogliere segnali sul sistema, ma sostituendo la sicurezza applicativa con grafici dettagliati",
            "Per capire il comportamento dei servizi, ma evitando di raccogliere informazioni operative"
        ],
        "spiegazione": (
            "L'osservabilità è importante in produzione perché aiuta a capire lo stato del sistema usando log, metriche e tracce quando emergono problemi. "
            "Non serve a nascondere errori, non sostituisce la sicurezza e richiede segnali operativi utili."
        )
    },

    "INF-AV-0214": {
        "opzioni": [
            "Per introdurre cambiamenti mantenendo compatibilità e chiarezza per i client esistenti",
            "Per evolvere gli endpoint, ma impedendo ai client di sapere quale versione stanno usando",
            "Per gestire cambiamenti nelle API, ma trasformando ogni richiesta HTTP in una query non documentata",
            "Per mantenere compatibilità tra versioni, ma evitando di comunicare modifiche importanti agli sviluppatori"
        ],
        "spiegazione": (
            "Il versionamento delle API è utile per introdurre cambiamenti mantenendo compatibilità e chiarezza per i client esistenti. "
            "Non deve nascondere le versioni, creare richieste non documentate o evitare la comunicazione delle modifiche importanti."
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
        "# Miglioramento Informatica - quarto blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INFORMATICA - QUARTO BLOCCO =====")
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
    print("OK: quarto blocco Informatica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
