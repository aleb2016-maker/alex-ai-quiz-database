import json
from pathlib import Path


PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


MIGLIORAMENTI = {
    # =========================
    # AI - distrattori più plausibili
    # =========================

    "AI-FAC-0004": {
        "opzioni": [
            "Esempi usati dal modello per imparare schemi e relazioni",
            "Esempi usati solo per verificare il modello dopo l'addestramento",
            "Regole scritte manualmente per ogni singola risposta possibile",
            "Parametri finali già imparati dal modello dopo il training"
        ],
        "risposta_corretta": "Esempi usati dal modello per imparare schemi e relazioni",
        "spiegazione": (
            "I dati di addestramento sono esempi usati dal modello per imparare schemi e relazioni. "
            "I dati di test servono invece a verificare il modello dopo l'addestramento. "
            "Le regole manuali appartengono più ai sistemi esperti tradizionali, mentre i parametri sono il risultato dell'apprendimento."
        )
    },

    "AI-FAC-0005": {
        "opzioni": [
            "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
            "Analizza questo testo e produci un commento libero.",
            "Riscrivi questo testo mantenendo tutti i dettagli.",
            "Estrai tutte le parole chiave senza fare un riassunto."
        ],
        "risposta_corretta": "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
        "spiegazione": (
            "Il prompt corretto specifica chiaramente il compito, la lunghezza e lo stile: un riassunto in 5 righe con linguaggio semplice. "
            "Le altre opzioni sono attività plausibili sul testo, ma non chiedono esattamente un riassunto breve."
        )
    },

    "AI-FAC-0006": {
        "opzioni": [
            "Classificazione",
            "Regressione",
            "Clustering",
            "Generazione"
        ],
        "risposta_corretta": "Classificazione",
        "spiegazione": (
            "La classificazione assegna un elemento a una categoria, per esempio spam o non spam. "
            "La regressione predice un valore numerico, il clustering raggruppa dati simili senza etichette, "
            "mentre la generazione produce nuovi contenuti."
        )
    },

    "AI-FAC-0007": {
        "opzioni": [
            "Lavora con il linguaggio per comprendere o generare testo",
            "Classifica esclusivamente immagini senza usare testo",
            "Memorizza pagine web senza elaborarne il significato",
            "Esegue soltanto calcoli numerici senza usare parole"
        ],
        "risposta_corretta": "Lavora con il linguaggio per comprendere o generare testo",
        "spiegazione": (
            "Un modello linguistico lavora principalmente con testo e linguaggio naturale. "
            "Può comprendere, completare, riassumere o generare frasi. Le altre risposte descrivono attività possibili in informatica o AI, "
            "ma non rappresentano il ruolo principale di un modello linguistico."
        )
    },

    "AI-FAC-0008": {
        "opzioni": [
            "Allucinazione",
            "Bias del dataset",
            "Overfitting",
            "Errore di classificazione"
        ],
        "risposta_corretta": "Allucinazione",
        "spiegazione": (
            "Un'allucinazione avviene quando un modello genera una risposta falsa o inventata presentandola come sicura. "
            "Il bias riguarda distorsioni nei dati o nei risultati, l'overfitting indica un modello troppo adattato ai dati di addestramento, "
            "mentre un errore di classificazione è una previsione di classe sbagliata."
        )
    },

    "AI-INT-0004": {
        "opzioni": [
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
            "Per addestrare di nuovo il modello ogni volta che riceve una domanda",
            "Per sostituire la generazione con una semplice ricerca di parole uguali",
            "Per impedire al modello di usare il contesto recuperato"
        ],
        "risposta_corretta": "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
        "spiegazione": (
            "Nel RAG il sistema recupera documenti utili e li passa al modello come contesto. "
            "Non significa riaddestrare il modello a ogni domanda, né fare solo una ricerca letterale. "
            "Il recupero serve proprio a dare al modello informazioni più pertinenti."
        )
    },

    "AI-INT-0005": {
        "opzioni": [
            "A rappresentare testi, immagini o dati come vettori confrontabili",
            "A trasformare direttamente ogni testo in una risposta finale",
            "A classificare i dati senza creare alcuna rappresentazione numerica",
            "A salvare il testo originale senza permettere confronti semantici"
        ],
        "risposta_corretta": "A rappresentare testi, immagini o dati come vettori confrontabili",
        "spiegazione": (
            "Un embedding rappresenta un contenuto come vettore numerico. Questo permette confronti di somiglianza semantica. "
            "Non è una risposta finale e non sostituisce da solo classificazione, retrieval o generazione."
        )
    },

    "AI-INT-0006": {
        "opzioni": [
            "Per verificare se il modello generalizza anche su casi nuovi",
            "Per controllare se il modello ricorda perfettamente i dati di training",
            "Per aumentare il numero di parametri durante il test",
            "Per evitare qualunque confronto con risultati attesi"
        ],
        "risposta_corretta": "Per verificare se il modello generalizza anche su casi nuovi",
        "spiegazione": (
            "Il test su esempi non visti serve a capire se il modello generalizza. "
            "Ricordare perfettamente i dati di training può invece indicare overfitting. "
            "Durante il test non si aumentano i parametri e il confronto con risultati attesi è spesso fondamentale."
        )
    },

    "AI-INT-0007": {
        "opzioni": [
            "Specificare ruolo, obiettivo, vincoli e formato della risposta",
            "Scrivere una richiesta breve senza contesto per lasciare libertà totale",
            "Fornire molti obiettivi diversi senza indicare priorità",
            "Chiedere una risposta generica senza definire il formato"
        ],
        "risposta_corretta": "Specificare ruolo, obiettivo, vincoli e formato della risposta",
        "spiegazione": (
            "Un prompt controllabile chiarisce cosa deve fare il modello, con quali vincoli e in quale formato. "
            "Una richiesta vaga o con obiettivi confusi aumenta il rischio di risposte generiche o incoerenti."
        )
    },

    "AI-INT-0008": {
        "opzioni": [
            "Il modello può imparare a favorire quella classe nelle previsioni",
            "Il modello impara automaticamente a bilanciare tutte le classi",
            "Il modello ignora sempre la classe più frequente",
            "Il modello produce solo risultati casuali senza seguire i dati"
        ],
        "risposta_corretta": "Il modello può imparare a favorire quella classe nelle previsioni",
        "spiegazione": (
            "Se una classe è molto più presente delle altre, il modello può prevederla troppo spesso. "
            "Il bilanciamento non avviene automaticamente: spesso servono tecniche specifiche, metriche adatte o dati più equilibrati."
        )
    },

    "AI-INT-0009": {
        "opzioni": [
            "Uno strumento esterno che l'agente può usare per compiere un'azione",
            "Una memoria interna che conserva solo la conversazione precedente",
            "Un prompt fisso che descrive il comportamento dell'agente",
            "Un modello separato usato soltanto per generare testo"
        ],
        "risposta_corretta": "Uno strumento esterno che l'agente può usare per compiere un'azione",
        "spiegazione": (
            "In un agente AI, un tool è una funzione o risorsa esterna che permette di fare qualcosa, "
            "per esempio cercare dati, leggere file, chiamare API o fare calcoli. "
            "Memoria, prompt e modello sono componenti diversi."
        )
    },

    "AI-AV-0004": {
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
            "Il modello può rifiutare una risposta corretta perché il contesto è troppo breve",
            "Il modello può usare solo la memoria interna ignorando i documenti recuperati",
            "Il modello può confondere la domanda con una valutazione del retrieval"
        ],
        "risposta_corretta": "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
        "spiegazione": (
            "Se il retrieval recupera documenti solo apparentemente pertinenti, il modello può costruire una risposta fluida ma fondata su contesto sbagliato. "
            "È un problema delicato perché la forma della risposta può sembrare convincente anche quando la base informativa è debole."
        )
    },

    "AI-AV-0005": {
        "opzioni": [
            "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
            "Perché una risposta lunga deve essere sempre considerata migliore di una breve",
            "Perché la valutazione automatica deve ignorare il contesto della richiesta",
            "Perché nei compiti generativi esiste sempre una sola risposta identica da confrontare"
        ],
        "risposta_corretta": "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
        "spiegazione": (
            "Nei compiti generativi spesso non basta dire corretto o sbagliato. "
            "Una risposta può essere parzialmente corretta ma incompleta, poco sicura, fuori formato o poco utile. "
            "Per questo servono criteri di valutazione più ricchi."
        )
    },

    "AI-AV-0006": {
        "opzioni": [
            "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
            "Il modello può ricevere un contesto lungo ma rimanere comunque dentro le istruzioni di sistema",
            "Il modello può rispondere con informazioni incomplete senza usare tool esterni",
            "Il modello può ridurre la qualità della risposta senza violare alcuna istruzione"
        ],
        "risposta_corretta": "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
        "spiegazione": (
            "Una prompt injection tenta di manipolare il modello facendogli ignorare istruzioni prioritarie. "
            "Il rischio è maggiore se il modello può usare tool esterni, perché potrebbe compiere azioni non previste dall'applicazione."
        )
    },

    "AI-AV-0007": {
        "opzioni": [
            "Quando servono comportamenti stabili e specifici su molti esempi simili",
            "Quando basta correggere una singola risposta con un prompt più preciso",
            "Quando non sono disponibili esempi coerenti del comportamento desiderato",
            "Quando il problema dipende solo dal recupero di documenti sbagliati"
        ],
        "risposta_corretta": "Quando servono comportamenti stabili e specifici su molti esempi simili",
        "spiegazione": (
            "Il fine-tuning ha senso quando si vuole rendere stabile uno stile, un formato o un comportamento su molti casi simili. "
            "Per problemi singoli o istruzioni semplici può bastare il prompt engineering; se il retrieval è sbagliato, invece, va corretta la pipeline di recupero."
        )
    },

    "AI-AV-0008": {
        "opzioni": [
            "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
            "Per aumentare la complessità senza poter capire quale modulo sbaglia",
            "Per impedire al controllo finale di valutare la risposta generata",
            "Per usare sempre un solo modello anche quando servono funzioni diverse"
        ],
        "risposta_corretta": "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
        "spiegazione": (
            "Separare recupero, generazione e controllo finale rende la pipeline più osservabile. "
            "Se qualcosa va male, si può capire se l'errore nasce dai documenti recuperati, dalla generazione o dalla verifica finale."
        )
    },

    "AI-AV-0009": {
        "opzioni": [
            "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
            "Perché un modello corretto dal punto di vista tecnico elimina automaticamente ogni bias",
            "Perché i bias compaiono solo se il codice contiene errori di sintassi",
            "Perché le metriche di valutazione non possono mai influenzare il comportamento del modello"
        ],
        "risposta_corretta": "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
        "spiegazione": (
            "Un modello può essere implementato correttamente ma imparare distorsioni presenti nei dati o negli obiettivi di addestramento. "
            "Anche le metriche scelte possono favorire certi comportamenti rispetto ad altri."
        )
    },

    # =========================
    # INFORMATICA - distrattori più plausibili
    # =========================

    "INF-FAC-0004": {
        "opzioni": ["HTML", "CSS", "JavaScript", "SQL"],
        "risposta_corretta": "HTML",
        "spiegazione": (
            "HTML definisce la struttura della pagina web. CSS gestisce lo stile grafico, JavaScript aggiunge interattività, "
            "mentre SQL serve a interrogare database. Tutte sono tecnologie reali, ma hanno ruoli diversi."
        )
    },

    "INF-FAC-0005": {
        "opzioni": [
            "Un insieme organizzato di righe e colonne",
            "Una relazione tra due tabelle tramite chiavi",
            "Una singola riga che rappresenta un record",
            "Una query usata per filtrare i dati"
        ],
        "risposta_corretta": "Un insieme organizzato di righe e colonne",
        "spiegazione": (
            "Una tabella contiene dati organizzati in righe e colonne. Una riga è un record, una query serve a leggere o modificare dati, "
            "e una relazione collega tabelle diverse."
        )
    },

    "INF-FAC-0006": {
        "opzioni": [
            "A conservare un valore che può essere usato o modificato",
            "A definire una funzione riutilizzabile",
            "A ripetere un blocco di istruzioni",
            "A controllare una condizione vera o falsa"
        ],
        "risposta_corretta": "A conservare un valore che può essere usato o modificato",
        "spiegazione": (
            "Una variabile conserva un valore. Una funzione raggruppa codice riutilizzabile, un ciclo ripete istruzioni, "
            "mentre una condizione controlla quale ramo di codice eseguire."
        )
    },

    "INF-FAC-0007": {
        "opzioni": [
            "L'indirizzo di una risorsa sul web",
            "Il protocollo usato per trasferire una pagina",
            "Il nome del dominio senza percorso della risorsa",
            "Il codice di stato restituito dal server"
        ],
        "risposta_corretta": "L'indirizzo di una risorsa sul web",
        "spiegazione": (
            "Un URL identifica l'indirizzo completo di una risorsa web. Può includere protocollo, dominio, percorso e parametri. "
            "Il protocollo e il dominio sono solo parti dell'URL, mentre il codice di stato è la risposta del server."
        )
    },

    "INF-FAC-0008": {
        "opzioni": ["JSON", "CSV", "XML", "YAML"],
        "risposta_corretta": "JSON",
        "spiegazione": (
            "JSON è molto usato per rappresentare dati strutturati in applicazioni web e API. "
            "Anche CSV, XML e YAML rappresentano dati, ma JSON è particolarmente comune per oggetti e liste scambiati tra sistemi."
        )
    },

    "INF-INT-0004": {
        "opzioni": ["GET", "POST", "PUT", "PATCH"],
        "risposta_corretta": "GET",
        "spiegazione": (
            "GET viene usato normalmente per leggere dati senza modificarli. POST crea o invia dati, PUT sostituisce una risorsa, "
            "PATCH aggiorna parzialmente una risorsa."
        )
    },

    "INF-INT-0005": {
        "opzioni": [
            "Per identificare in modo univoco ogni record",
            "Per collegare una tabella a un'altra come chiave esterna",
            "Per ordinare sempre i record in ordine alfabetico",
            "Per rendere più leggibile il nome delle colonne"
        ],
        "risposta_corretta": "Per identificare in modo univoco ogni record",
        "spiegazione": (
            "La chiave primaria identifica una riga in modo univoco. La chiave esterna collega tabelle diverse. "
            "Ordinamento e leggibilità dei nomi non sono lo scopo principale della chiave primaria."
        )
    },

    "INF-INT-0006": {
        "opzioni": [
            "Gestire l'aspetto visivo degli elementi",
            "Definire la struttura semantica della pagina",
            "Gestire la logica interattiva nel browser",
            "Recuperare dati da un database con query"
        ],
        "risposta_corretta": "Gestire l'aspetto visivo degli elementi",
        "spiegazione": (
            "CSS gestisce stile, layout, colori, spaziature e responsive design. HTML definisce la struttura, JavaScript gestisce l'interattività, "
            "mentre le query al database sono tipiche del backend."
        )
    },

    "INF-INT-0007": {
        "opzioni": [
            "Individuare e correggere errori nel comportamento del codice",
            "Scrivere test automatici prima di creare una funzione",
            "Ottimizzare il codice senza verificare errori funzionali",
            "Pubblicare il progetto su un server remoto"
        ],
        "risposta_corretta": "Individuare e correggere errori nel comportamento del codice",
        "spiegazione": (
            "Il debug serve a trovare e correggere errori. I test aiutano a verificarli, l'ottimizzazione migliora prestazioni o struttura, "
            "mentre il deploy pubblica il progetto."
        )
    },

    "INF-INT-0008": {
        "opzioni": [
            "Una fotografia salvata dello stato del progetto",
            "Un ramo separato in cui sviluppare nuove modifiche",
            "Un comando per scaricare modifiche dal repository remoto",
            "Un file temporaneo ignorato dal controllo versione"
        ],
        "risposta_corretta": "Una fotografia salvata dello stato del progetto",
        "spiegazione": (
            "Un commit salva uno stato del progetto. Un branch è un ramo di sviluppo, pull scarica modifiche dal remoto, "
            "mentre un file ignorato non viene tracciato da Git."
        )
    },

    "INF-INT-0009": {
        "opzioni": [
            "Perché possono finire in repository, log o copie condivise del progetto",
            "Perché impediscono al codice di collegarsi a un database",
            "Perché rendono impossibile usare variabili d'ambiente",
            "Perché vengono sempre cifrate automaticamente da Git"
        ],
        "risposta_corretta": "Perché possono finire in repository, log o copie condivise del progetto",
        "spiegazione": (
            "Salvare password nel codice è rischioso perché possono essere condivise per errore nel repository o nei log. "
            "Le variabili d'ambiente servono proprio a separare questi dati dal codice."
        )
    },

    "INF-AV-0004": {
        "opzioni": [
            "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
            "Perché il frontend può sostituire completamente database e API",
            "Perché il backend deve contenere anche tutta la grafica dell'utente",
            "Perché separare i livelli elimina automaticamente ogni bug"
        ],
        "risposta_corretta": "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
        "spiegazione": (
            "Separare frontend e backend aiuta a distinguere responsabilità diverse. "
            "Non elimina automaticamente i bug e non significa che il frontend sostituisca database o API."
        )
    },

    "INF-AV-0005": {
        "opzioni": [
            "La richiesta non è autenticata correttamente",
            "La richiesta è valida ma l'utente non ha i permessi necessari",
            "La risorsa richiesta non esiste sul server",
            "Il server ha generato un errore interno"
        ],
        "risposta_corretta": "La richiesta non è autenticata correttamente",
        "spiegazione": (
            "HTTP 401 indica in genere un problema di autenticazione. "
            "403 riguarda permessi insufficienti, 404 risorsa non trovata, 500 errore interno del server."
        )
    },

    "INF-AV-0006": {
        "opzioni": [
            "Rendere più veloci alcune ricerche su quella colonna",
            "Ridurre sempre lo spazio occupato dalla tabella",
            "Evitare automaticamente ogni duplicato nei dati",
            "Sostituire la chiave primaria della tabella"
        ],
        "risposta_corretta": "Rendere più veloci alcune ricerche su quella colonna",
        "spiegazione": (
            "Un indice può velocizzare ricerche e ordinamenti su una colonna, ma occupa spazio e può rallentare alcune scritture. "
            "Non elimina automaticamente duplicati e non sostituisce necessariamente una chiave primaria."
        )
    },

    "INF-AV-0007": {
        "opzioni": [
            "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
            "Perché impediscono sempre l'accesso simultaneo al database",
            "Perché trasformano ogni operazione in una transazione sicura",
            "Perché eliminano automaticamente il rischio di aggiornamenti persi"
        ],
        "risposta_corretta": "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
        "spiegazione": (
            "Operazioni simultanee sullo stesso dato possono causare conflitti, aggiornamenti persi o stati incoerenti. "
            "Transazioni e meccanismi di isolamento servono proprio a ridurre questi rischi."
        )
    },

    "INF-AV-0008": {
        "opzioni": [
            "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
            "Perché un test utile deve cambiare risultato a ogni esecuzione",
            "Perché il test deve controllare solo che il programma si avvii",
            "Perché il risultato atteso serve solo nei test manuali"
        ],
        "risposta_corretta": "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
        "spiegazione": (
            "Un test automatico confronta risultato ottenuto e risultato atteso. "
            "Se il risultato atteso non è chiaro, il test non può stabilire se il codice funziona davvero."
        )
    },

    "INF-AV-0009": {
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Permette di salvare password nel codice in modo più visibile",
            "Permette di evitare qualunque configurazione tra ambienti diversi",
            "Permette di compilare il frontend senza usare file statici"
        ],
        "risposta_corretta": "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
        "spiegazione": (
            "Le variabili d'ambiente permettono di tenere configurazioni, chiavi e URL fuori dal codice. "
            "Sono utili quando sviluppo, test e produzione usano valori diversi."
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


def applica_miglioramenti(domande):
    domande_modificate = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in MIGLIORAMENTI:
            miglioramento = MIGLIORAMENTI[id_domanda]

            domanda["opzioni"] = miglioramento["opzioni"]
            domanda["risposta_corretta"] = miglioramento["risposta_corretta"]
            domanda["spiegazione"] = miglioramento["spiegazione"]

            domande_modificate += 1

    return domande_modificate


def aggiorna_script_create_batch(domande):
    contenuto_lista = json.dumps(
        domande,
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
    domande = carica_json(PERCORSO_BATCH)

    domande_modificate = applica_miglioramenti(domande)

    salva_json(PERCORSO_BATCH, domande)
    aggiorna_script_create_batch(domande)

    print("Miglioramento risposte completato.")
    print(f"Domande modificate: {domande_modificate}")
    print("File aggiornati:")
    print(PERCORSO_BATCH)
    print(PERCORSO_SCRIPT_BATCH)


main()