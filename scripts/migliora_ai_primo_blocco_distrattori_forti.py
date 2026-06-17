import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_distrattori_forti.json")
REPORT = Path("reports/migliora_ai_primo_blocco_distrattori_forti.md")

PATCH = {
    "AI-INT-0002": {
        "opzioni": [
            "Perché fornisce più contesto e riduce le ambiguità della richiesta",
            "Perché fornisce più contesto, ma modifica anche i parametri interni del modello durante la risposta",
            "Perché chiarisce obiettivo e formato, ma rende inutile il controllo finale sulla qualità della risposta",
            "Perché riduce le ambiguità della richiesta, ma garantisce che ogni vincolo venga applicato correttamente"
        ],
        "spiegazione": (
            "Un prompt dettagliato migliora la risposta perché chiarisce contesto, obiettivo, vincoli e formato desiderato. "
            "Non modifica i parametri interni del modello, non sostituisce il controllo finale e non garantisce automaticamente "
            "che ogni vincolo venga applicato senza errori."
        )
    },

    "AI-AV-0003": {
        "opzioni": [
            "A recuperare informazioni da fonti esterne e usarle per generare risposte più fondate",
            "A recuperare informazioni esterne e usarle come contesto, ma riaddestrando il modello sui documenti a ogni richiesta",
            "A recuperare documenti esterni pertinenti, ma usarli solo per selezionare il tono della risposta",
            "A usare fonti esterne durante la generazione, ma senza distinguere tra documenti rilevanti e documenti solo simili"
        ],
        "spiegazione": (
            "Un sistema RAG recupera informazioni esterne e le usa come contesto per generare risposte più fondate. "
            "Non riaddestra il modello a ogni richiesta, non usa i documenti solo per il tono e deve distinguere tra contenuti "
            "davvero rilevanti e contenuti solo apparentemente simili."
        )
    },

    "AI-INT-0004": {
        "opzioni": [
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
            "Per fornire al modello documenti semanticamente vicini, ma senza verificare se contengono davvero informazioni utili",
            "Per recuperare informazioni aggiornate, ma lasciarle separate dal prompt usato per generare la risposta",
            "Per cercare fonti specifiche prima della risposta, ma usarle solo come elenco finale di riferimenti"
        ],
        "spiegazione": (
            "Nel RAG i documenti esterni devono fornire informazioni aggiornate o specifiche che entrano davvero nel contesto della risposta. "
            "Non basta trovare documenti semanticamente vicini, non basta recuperarli senza usarli nel prompt e non serve trattarli solo come elenco finale."
        )
    },

    "AI-INT-0005": {
        "opzioni": [
            "A rappresentare testi, immagini o dati come vettori confrontabili",
            "A rappresentare testi, immagini o dati come vettori confrontabili, ma solo quando condividono parole o caratteristiche identiche",
            "A trasformare contenuti in vettori numerici confrontabili, ma usandoli soprattutto come forma di compressione dei dati",
            "A rappresentare contenuti come vettori, ma senza mantenere relazioni di vicinanza semantica tra elementi simili"
        ],
        "spiegazione": (
            "Un embedding rappresenta contenuti come vettori confrontabili, così elementi simili possono risultare vicini anche se non usano parole identiche. "
            "Non serve solo alla compressione e non elimina le relazioni semantiche: proprio quelle relazioni sono una parte centrale della sua utilità."
        )
    },

    "AI-INT-0006": {
        "opzioni": [
            "Per verificare se il modello generalizza anche su casi nuovi",
            "Per verificare se il modello generalizza su casi nuovi, ma usando esempi scelti dal training set",
            "Per misurare la capacità di funzionare su dati non visti, ma premiando la memorizzazione degli esempi già appresi",
            "Per controllare il comportamento su casi diversi, ma senza confrontare le previsioni con il risultato atteso"
        ],
        "spiegazione": (
            "Testare un modello su esempi diversi da quelli di addestramento serve a verificare la generalizzazione su casi nuovi. "
            "Se si usano esempi già visti, si rischia di misurare memoria invece di generalizzazione; se non si confrontano le previsioni con il risultato atteso, la valutazione resta debole."
        )
    },

    "AI-INT-0007": {
        "opzioni": [
            "Specificare ruolo, obiettivo, vincoli e formato della risposta",
            "Specificare ruolo, obiettivo, vincoli e formato, ma senza dare priorità quando i vincoli entrano in conflitto",
            "Definire ruolo e formato della risposta, ma lasciando indefinito l'obiettivo principale",
            "Indicare obiettivo e vincoli della risposta, ma senza chiarire il formato richiesto"
        ],
        "spiegazione": (
            "Una risposta è più controllabile quando il prompt chiarisce ruolo, obiettivo, vincoli e formato. "
            "Se manca la priorità tra vincoli, se l'obiettivo resta indefinito o se il formato non è chiaro, il modello può produrre una risposta meno precisa."
        )
    },

    "AI-INT-0008": {
        "opzioni": [
            "Il modello può imparare a favorire quella classe nelle previsioni",
            "Il modello può assegnare maggiore importanza alla classe dominante, ma mantenere uguale sensibilità sulle classi rare",
            "Il modello può ottenere un'accuratezza apparentemente buona, ma perché riconosce meglio tutte le classi allo stesso modo",
            "Il modello può imparare lo sbilanciamento dei dati, ma compensarlo senza esempi aggiuntivi delle classi rare"
        ],
        "spiegazione": (
            "Se una classe è molto più presente delle altre, il modello può imparare a favorirla nelle previsioni. "
            "Questo non significa mantenere la stessa sensibilità sulle classi rare, né riconoscere tutte le classi allo stesso modo, né compensare lo sbilanciamento senza dati o tecniche adeguate."
        )
    },

    "AI-INT-0009": {
        "opzioni": [
            "Uno strumento esterno che l'agente può usare per compiere un'azione",
            "Uno strumento esterno che l'agente può richiamare, ma usato solo per conservare memoria della conversazione",
            "Una funzione che permette azioni fuori dal modello, ma senza restituire risultati utilizzabili nella risposta",
            "Un componente operativo dell'agente, ma coincidente con l'istruzione di sistema che ne definisce il comportamento"
        ],
        "spiegazione": (
            "In un agente AI, un tool è uno strumento esterno che può essere usato per compiere azioni, cercare dati, leggere file, chiamare API o fare calcoli. "
            "Non coincide con la memoria, non è solo una funzione senza risultati utili e non è l'istruzione di sistema."
        )
    },

    "AI-AV-0004": {
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
            "Il modello può generare una risposta ben scritta, ma il problema riguarda solo lo stile e non la qualità del contesto",
            "Il modello può usare documenti solo apparentemente rilevanti, ma correggere automaticamente il contenuto durante la generazione",
            "Il modello può sembrare fondato su fonti esterne, ma il controllo necessario riguarda solo la lunghezza del contesto"
        ],
        "spiegazione": (
            "Se il retrieval seleziona testi pertinenti solo in apparenza, il modello può produrre una risposta fluida ma fondata su un contesto debole o sbagliato. "
            "Il problema non riguarda solo lo stile, non viene corretto automaticamente durante la generazione e non si risolve controllando solo la lunghezza del contesto."
        )
    },

    "AI-AV-0005": {
        "opzioni": [
            "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
            "Perché alcune risposte richiedono giudizi su completezza e coerenza, ma la sicurezza può essere ignorata se i fatti sono corretti",
            "Perché una risposta può essere corretta nei fatti, ma il formato basta da solo a stabilire l'utilità finale",
            "Perché una risposta può essere fluida e parziale, ma va valutata solo sul numero di informazioni presenti"
        ],
        "spiegazione": (
            "Nelle risposte generate non basta sempre dire corretto o sbagliato: bisogna valutare completezza, coerenza, sicurezza e utilità. "
            "La sicurezza non può essere ignorata, il formato da solo non basta e il numero di informazioni non misura da solo la qualità della risposta."
        )
    },

    "AI-AV-0006": {
        "opzioni": [
            "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
            "Il modello può ricevere istruzioni esterne che sembrano operative, ma il rischio riguarda solo il testo generato e non i tool",
            "Il modello può confondere contenuto dell'utente e istruzioni, ma mantenere comunque invariato l'uso degli strumenti esterni",
            "Il modello può trattare informazioni recuperate come comandi, ma solo se quelle informazioni sono già presenti nel prompt di sistema"
        ],
        "spiegazione": (
            "Una prompt injection può spingere il modello a trattare contenuti esterni come istruzioni, ignorando regole originali e usando tool in modo non previsto. "
            "Il rischio non riguarda solo il testo, non garantisce un uso invariato degli strumenti e non dipende solo da ciò che è già scritto nel prompt di sistema."
        )
    },

    "AI-AV-0007": {
        "opzioni": [
            "Quando servono comportamenti stabili e specifici su molti esempi simili",
            "Quando servono comportamenti stabili su molti esempi simili, ma l'obiettivo è correggere una singola risposta isolata",
            "Quando si vuole rendere stabile uno stile o formato, ma senza avere esempi coerenti del comportamento desiderato",
            "Quando il problema si ripete in molti casi simili, ma dipende soprattutto da documenti recuperati male"
        ],
        "spiegazione": (
            "Il fine-tuning ha senso quando servono comportamenti stabili e specifici su molti esempi simili. "
            "Non è la scelta migliore per correggere una singola risposta isolata, non funziona bene senza esempi coerenti e non risolve un problema che dipende soprattutto da retrieval sbagliato."
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
        return contenuto, None

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave], chiave

    raise ValueError("Formato JSON non riconosciuto: non trovo la lista delle domande.")


def aggiorna_opzioni(domanda, nuove_opzioni):
    chiave_opzioni = None

    for chiave in ["opzioni", "options", "risposte", "answers"]:
        if chiave in domanda:
            chiave_opzioni = chiave
            break

    if chiave_opzioni is None:
        chiave_opzioni = "opzioni"

    domanda[chiave_opzioni] = nuove_opzioni


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
    domande, chiave_lista = estrai_domande(contenuto)

    aggiornate = []
    non_trovate = []

    indice_per_id = {
        str(domanda.get("id", "")).strip(): domanda
        for domanda in domande
    }

    for id_domanda, dati in PATCH.items():
        domanda = indice_per_id.get(id_domanda)

        if domanda is None:
            non_trovate.append(id_domanda)
            continue

        nuove_opzioni = dati["opzioni"]

        aggiorna_opzioni(domanda, nuove_opzioni)
        aggiorna_risposta_corretta(domanda, nuove_opzioni[0])
        domanda["spiegazione"] = dati["spiegazione"]

        # Metadati utili per ricordare la nuova regola del progetto.
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve restare nello stesso concetto della corretta "
            "e diventare sbagliata per un dettaglio tecnico, logico o pratico."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE_AI, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = []
    righe.append("# Miglioramento AI - primo blocco distrattori forti")
    righe.append("")
    righe.append("Regola applicata: 1 risposta corretta + 3 distrattori forti.")
    righe.append("")
    righe.append("Ogni distrattore ora prova a condividere la premessa corretta e a sbagliare per un dettaglio preciso.")
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

    print("===== MIGLIORAMENTO AI - PRIMO BLOCCO =====")
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
    print("OK: primo blocco AI aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
