import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_terzo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_ai_terzo_blocco_distrattori_forti.md")

PATCH = {
    "AI-INT-0211": {
        "opzioni": [
            "Collegare la risposta a informazioni verificabili o a fonti fornite al sistema",
            "Collegare la risposta a fonti fornite, ma usarle solo come riferimento finale senza influenzare il contenuto generato",
            "Ancorare la risposta a dati verificabili, ma senza distinguere tra fonti pertinenti e fonti solo semanticamente simili",
            "Usare informazioni disponibili per rendere la risposta più credibile, ma senza verificare se supportano davvero l'affermazione"
        ],
        "spiegazione": (
            "Il grounding collega la risposta a informazioni verificabili o a fonti fornite al sistema. "
            "Non basta citare fonti alla fine, non basta usare contenuti solo simili e non basta rendere la risposta credibile se le informazioni non supportano davvero ciò che viene affermato."
        )
    },

    "AI-INT-0212": {
        "opzioni": [
            "Per ridurre la precisione numerica dei pesi e diminuire memoria o costo computazionale",
            "Per ridurre la precisione numerica dei pesi, ma aumentando il numero totale di parametri del modello",
            "Per rendere più leggero il modello, ma senza modificare il modo in cui i pesi vengono rappresentati numericamente",
            "Per diminuire memoria e costo computazionale, ma garantendo la stessa precisione di calcolo in ogni passaggio"
        ],
        "spiegazione": (
            "La quantizzazione riduce la precisione numerica con cui sono rappresentati i pesi o alcune operazioni, diminuendo memoria e costo computazionale. "
            "Non aumenta i parametri, non lascia invariata la rappresentazione numerica e non garantisce sempre la stessa precisione di calcolo."
        )
    },

    "AI-AV-0205": {
        "opzioni": [
            "La perdita di prestazioni su conoscenze o compiti precedenti dopo un nuovo addestramento",
            "La perdita di prestazioni su compiti precedenti, ma dovuta solo alla cancellazione manuale del dataset originale",
            "Il peggioramento su conoscenze già apprese, ma senza che il nuovo addestramento abbia influenzato i pesi del modello",
            "La riduzione della capacità su compiti vecchi, ma compensata automaticamente dalla maggiore accuratezza sul nuovo compito"
        ],
        "spiegazione": (
            "Il catastrophic forgetting è la perdita di prestazioni su conoscenze o compiti precedenti dopo un nuovo addestramento. "
            "Non dipende solo dalla cancellazione manuale del dataset, riguarda cambiamenti nel comportamento del modello e non viene compensato automaticamente dal miglioramento sul nuovo compito."
        )
    },

    "AI-AV-0208": {
        "opzioni": [
            "Per collegare correttamente elementi visivi e descrizioni linguistiche durante il ragionamento o la generazione",
            "Per collegare testo e immagini, ma usando il testo solo come etichetta esterna senza influenzare il ragionamento visivo",
            "Per mettere in relazione descrizioni e contenuti visivi, ma trattando ogni modalità come indipendente nella risposta finale",
            "Per usare testo e immagini nello stesso sistema, ma convertendo tutto in una sola modalità prima di ogni confronto"
        ],
        "spiegazione": (
            "Un sistema multimodale deve allineare testo e immagini per collegare elementi visivi e descrizioni linguistiche durante ragionamento o generazione. "
            "Non basta usare il testo come etichetta, non si devono trattare le modalità come indipendenti e non è sempre corretto ridurre tutto a una sola modalità prima del confronto."
        )
    },

    "AI-AV-0209": {
        "opzioni": [
            "Bilanciare qualità delle risposte, latenza, costo computazionale e risorse disponibili",
            "Bilanciare qualità e latenza, ma scegliendo comunque il modello più grande quando produce risposte più complete",
            "Valutare costo e risorse disponibili, ma considerare la latenza solo dopo il rilascio dell'applicazione",
            "Scegliere un modello con buone risposte, ma separando la qualità dai vincoli pratici di esecuzione"
        ],
        "spiegazione": (
            "In un'app reale bisogna bilanciare qualità, latenza, costo computazionale e risorse disponibili. "
            "Il modello più grande non è sempre la scelta migliore, la latenza va valutata prima del rilascio e la qualità non può essere separata dai vincoli pratici."
        )
    },

    "AI-INT-0107": {
        "opzioni": [
            "Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose",
            "Per ridurre i rischi operativi, ma lasciando all'agente la possibilità di confermare da solo le azioni delicate",
            "Per limitare le azioni automatiche, ma senza distinguere tra operazioni reversibili e operazioni rischiose",
            "Per controllare meglio l'agente, ma concedendo permessi ampi quando il prompt sembra scritto in modo chiaro"
        ],
        "spiegazione": (
            "Limitare le azioni automatiche riduce il rischio che errori, ambiguità o prompt malevoli producano azioni dannose. "
            "L'agente non dovrebbe confermare da solo azioni delicate, i permessi vanno graduati in base al rischio e un prompt chiaro non elimina la necessità di controlli."
        )
    },

    "AI-AV-0204": {
        "opzioni": [
            "RLHF usa un processo con modello di ricompensa e ottimizzazione tramite rinforzo, mentre DPO ottimizza direttamente su preferenze confrontate",
            "RLHF usa preferenze e ricompensa, mentre DPO richiede comunque un modello di ricompensa separato per ogni confronto",
            "DPO ottimizza su preferenze confrontate, ma usa rinforzo esplicito nello stesso modo centrale di RLHF",
            "RLHF e DPO usano preferenze, ma differiscono solo per il formato dei dati e non per il modo di ottimizzare"
        ],
        "spiegazione": (
            "RLHF usa tipicamente un modello di ricompensa e ottimizzazione tramite rinforzo, mentre DPO ottimizza direttamente su preferenze confrontate. "
            "DPO non richiede lo stesso modello di ricompensa separato, non usa il rinforzo nello stesso modo centrale di RLHF e la differenza non riguarda solo il formato dei dati."
        )
    },

    "AI-AV-0207": {
        "opzioni": [
            "L'inserimento nel contesto di informazioni fuorvianti che influenzano negativamente le risposte successive",
            "L'inserimento di informazioni nel contesto, ma con effetti limitati solo alla formattazione della risposta",
            "La presenza di dati fuorvianti nel contesto, ma senza impatto sulle risposte successive del modello",
            "La contaminazione del contesto con contenuti ingannevoli, ma corretta automaticamente dal modello prima della generazione"
        ],
        "spiegazione": (
            "Il context poisoning avviene quando informazioni fuorvianti entrano nel contesto e influenzano negativamente risposte successive. "
            "Non riguarda solo la formattazione, può avere impatto sul comportamento del modello e non viene sempre corretto automaticamente."
        )
    },

    "AI-FAC-0006": {
        "opzioni": [
            "Classificazione",
            "Classificazione binaria, ma senza assegnare l'email a una classe finale",
            "Clustering di email simili, ma usando categorie spam e non spam già definite",
            "Regressione, ma applicata per scegliere tra due categorie invece di stimare un valore numerico"
        ],
        "spiegazione": (
            "Decidere se una email è spam oppure no è un problema di classificazione, perché l'input viene assegnato a una categoria. "
            "Non è clustering se le categorie sono già definite e non è regressione, perché non si sta stimando un valore numerico continuo."
        )
    },

    "AI-FAC-0008": {
        "opzioni": [
            "Allucinazione",
            "Errore di grounding, ma con risposta comunque supportata dai dati disponibili",
            "Bias del dataset, ma senza una distorsione sistematica nei risultati",
            "Overfitting della risposta, ma riferito a un contenuto inventato durante l'inferenza"
        ],
        "spiegazione": (
            "Quando un modello inventa una risposta falsa e la presenta come sicura si parla normalmente di allucinazione. "
            "Un errore di grounding è collegato ma non coincide sempre con il nome del fenomeno; bias e overfitting descrivono problemi diversi."
        )
    },

    "AI-FAC-0207": {
        "opzioni": [
            "Usare il modello per produrre una previsione o una risposta su un nuovo input",
            "Usare il modello su un nuovo input, ma aggiornando i pesi durante ogni risposta",
            "Produrre una risposta dopo l'addestramento, ma solo su esempi già presenti nel training set",
            "Applicare il modello a un input, ma completando prima una nuova fase di addestramento"
        ],
        "spiegazione": (
            "L'inferenza è l'uso di un modello già addestrato per produrre una previsione o una risposta su un nuovo input. "
            "Non aggiorna i pesi durante ogni risposta, non riguarda solo esempi già visti e non richiede una nuova fase di addestramento prima di ogni utilizzo."
        )
    },

    "AI-FAC-0208": {
        "opzioni": [
            "Una risposta plausibile nella forma ma non corretta o non supportata dai dati",
            "Una risposta fluida e sicura, ma sempre verificata da fonti esterne fornite al modello",
            "Una risposta non supportata dai dati, ma corretta perché coerente con il tono della conversazione",
            "Una risposta plausibile ma imprecisa, corretta automaticamente quando viene generata con un prompt più lungo"
        ],
        "spiegazione": (
            "Un'allucinazione è una risposta plausibile nella forma ma non corretta o non supportata dai dati. "
            "Non è verificata solo perché suona sicura, il tono coerente non garantisce correttezza e un prompt più lungo non corregge automaticamente il problema."
        )
    },

    "AI-FAC-0212": {
        "opzioni": [
            "Nel supervisionato gli esempi di addestramento hanno etichette o risposte corrette associate",
            "Nel supervisionato gli esempi hanno etichette, ma il modello non le usa per imparare la relazione input-risposta",
            "Nel non supervisionato il modello cerca strutture nei dati, ma usando etichette corrette fornite per ogni esempio",
            "Nel supervisionato e nel non supervisionato i dati sono uguali, cambia solo il numero di esempi usati"
        ],
        "spiegazione": (
            "Nell'apprendimento supervisionato gli esempi hanno etichette o risposte corrette associate. "
            "Nel non supervisionato il modello cerca strutture senza etichette esplicite; la differenza non riguarda solo il numero di esempi."
        )
    },

    "AI-INT-0202": {
        "opzioni": [
            "Per cercare elementi semanticamente simili usando vettori numerici",
            "Per cercare elementi simili usando vettori, ma confrontando solo parole identiche presenti nei testi",
            "Per conservare embedding numerici, ma senza permettere ricerche di vicinanza tra contenuti",
            "Per trovare contenuti semanticamente vicini, ma sostituendo il modello linguistico con una tabella statica"
        ],
        "spiegazione": (
            "Un database vettoriale è utile perché permette di cercare elementi semanticamente simili usando vettori numerici. "
            "Non si limita a parole identiche, non conserva vettori senza ricerca di vicinanza e non sostituisce da solo il modello linguistico."
        )
    },

    "AI-INT-0206": {
        "opzioni": [
            "Un tentativo di inserire istruzioni malevole o fuorvianti nel testo dato al modello",
            "Un tentativo di inserire istruzioni nel testo, ma limitato a cambiare solo il tono della risposta",
            "Una manipolazione del prompt, ma innocua se l'istruzione appare dentro un documento recuperato",
            "Un attacco tramite testo, ma possibile solo quando il modello non ha istruzioni di sistema"
        ],
        "spiegazione": (
            "La prompt injection è un tentativo di inserire istruzioni malevole o fuorvianti nel testo dato al modello. "
            "Non riguarda solo il tono, può arrivare anche da documenti recuperati e può essere rischiosa anche se esistono istruzioni di sistema."
        )
    },

    "AI-INT-0207": {
        "opzioni": [
            "A permettere al modello di richiedere l'uso di strumenti esterni, come API, calcoli o ricerche",
            "A permettere l'uso di strumenti esterni, ma senza definire permessi, limiti o controlli sulle azioni",
            "A collegare il modello a funzioni esterne, ma solo per leggere risultati senza usarli nella risposta",
            "A far scegliere strumenti al modello, ma sostituendo la verifica del risultato con la chiamata del tool"
        ],
        "spiegazione": (
            "Il tool calling permette al modello di richiedere strumenti esterni, come API, calcoli o ricerche. "
            "Servono comunque permessi e controlli, i risultati devono essere usati e verificati correttamente, e chiamare un tool non sostituisce la validazione."
        )
    },

    "AI-INT-0208": {
        "opzioni": [
            "Per controllare meglio quando l'agente deve pensare, chiamare strumenti, verificare risultati o fermarsi",
            "Per separare ragionamento e azioni, ma permettere comunque all'agente di eseguire strumenti senza verifica finale",
            "Per controllare le fasi dell'agente, ma trattare la chiamata agli strumenti come sempre sicura se il ragionamento sembra coerente",
            "Per distinguere pensiero e azione, ma eliminando log e controlli quando l'agente produce una risposta fluida"
        ],
        "spiegazione": (
            "Separare ragionamento e azioni rende l'agente più controllabile: si può decidere quando pensare, chiamare strumenti, verificare risultati o fermarsi. "
            "Non basta che il ragionamento sembri coerente, la verifica finale resta utile e log e controlli non vanno eliminati."
        )
    },

    "AI-INT-0210": {
        "opzioni": [
            "Una tendenza sistematica del modello a favorire o penalizzare certi risultati o gruppi",
            "Una tendenza del modello verso certi risultati, ma dovuta soltanto a errori casuali non ripetibili",
            "Una distorsione sistematica nei risultati, ma sempre intenzionale e progettata manualmente dagli sviluppatori",
            "Una preferenza del modello per alcuni output, ma senza effetti misurabili su gruppi, decisioni o risultati"
        ],
        "spiegazione": (
            "Il bias indica una tendenza sistematica del modello a favorire o penalizzare certi risultati o gruppi. "
            "Non è solo rumore casuale, non deve essere per forza intenzionale e può avere effetti misurabili sui risultati."
        )
    },

    "AI-INT-0213": {
        "opzioni": [
            "Molti elementi previsti come positivi dal modello sono in realtà negativi",
            "Molti positivi previsti sono errati, ma il modello ha comunque pochi falsi positivi",
            "Il modello produce pochi risultati positivi, ma quelli previsti come positivi sono quasi tutti corretti",
            "Il classificatore sbaglia molte predizioni negative, ma mantiene affidabili le predizioni positive"
        ],
        "spiegazione": (
            "Una bassa precisione indica che molti elementi previsti come positivi sono in realtà negativi, quindi ci sono molti falsi positivi. "
            "Non significa semplicemente produrre pochi positivi e non riguarda in modo diretto l'affidabilità delle predizioni negative."
        )
    },

    "AI-INT-0214": {
        "opzioni": [
            "Per capire quali input causano errori, risposte deboli o comportamenti inattesi",
            "Per registrare input e risultati, ma senza collegarli agli errori osservati durante i test",
            "Per capire i comportamenti inattesi, ma usando i log solo come archivio e non come base di analisi",
            "Per conservare risultati dei test, ma sostituendo con i log la revisione qualitativa delle risposte"
        ],
        "spiegazione": (
            "Registrare log e risultati durante i test aiuta a capire quali input causano errori, risposte deboli o comportamenti inattesi. "
            "I log devono essere collegati all'analisi degli errori e non sostituiscono la revisione qualitativa."
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(
        json.dumps(contenuto, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


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
    if not FILE_AI.exists():
        raise SystemExit("ERRORE: data/ai.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE_AI.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

    contenuto = carica_json(FILE_AI)
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

    salva_json(FILE_AI, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = []
    righe.append("# Miglioramento AI - terzo blocco distrattori forti")
    righe.append("")
    righe.append("Regola applicata: 1 risposta corretta + 3 distrattori forti.")
    righe.append("")
    righe.append("Metodo: stesso concetto centrale, stesso contesto, piccolo dettaglio sbagliato.")
    righe.append("")
    righe.append(f"Domande aggiornate: {len(aggiornate)}")
    righe.append("")

    for id_domanda in aggiornate:
        righe.append(f"- {id_domanda}")

    if non_trovate:
        righe.append("")
        righe.append("## ID non trovati")
        righe.append("")
        for id_domanda in non_trovate:
            righe.append(f"- {id_domanda}")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== MIGLIORAMENTO AI - TERZO BLOCCO =====")
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
    print("OK: terzo blocco AI aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
