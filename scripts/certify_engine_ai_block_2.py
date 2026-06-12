import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "AI-INT-0004": {
        "opzioni": [
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
            "Per trovare testi semanticamente simili alla domanda, anche se poi non vengono usati come contesto",
            "Per archiviare i documenti recuperati senza inserirli nel prompt",
            "Per confrontare la domanda con esempi simili senza generare una risposta",
        ],
        "risposta_corretta": "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
        "spiegazione": (
            "Nel RAG il sistema recupera documenti rilevanti e li passa al modello come contesto. "
            "Il punto non è solo trovare testi simili, ma fornire informazioni utili su cui costruire la risposta. "
            "Se i documenti vengono trovati ma non usati nel prompt, oppure sono solo simili in apparenza, "
            "la risposta può restare generica o poco affidabile."
        ),
        "distrattore_forte": "Per trovare testi semanticamente simili alla domanda, anche se poi non vengono usati come contesto",
        "motivo_distrattore_forte": (
            "È vicino perché parla di ricerca semantica e documenti simili, "
            "ma è sbagliato perché nel RAG i documenti devono essere usati come contesto della generazione."
        ),
    },
    "AI-INT-0005": {
        "opzioni": [
            "A rappresentare testi, immagini o dati come vettori confrontabili",
            "A trasformare contenuti in vettori numerici solo per conservarli come testo compresso",
            "A confrontare contenuti solo quando usano le stesse parole identiche",
            "A cercare parole uguali senza rappresentare il significato dei contenuti",
        ],
        "risposta_corretta": "A rappresentare testi, immagini o dati come vettori confrontabili",
        "spiegazione": (
            "Un embedding trasforma un contenuto in un vettore numerico, così contenuti simili possono essere confrontati "
            "anche se usano parole diverse. Non è una compressione del testo originale e non è una semplice ricerca per parole identiche."
        ),
        "distrattore_forte": "A trasformare contenuti in vettori numerici solo per conservarli come testo compresso",
        "motivo_distrattore_forte": (
            "È vicino perché parla di trasformazione in vettori numerici, "
            "ma è sbagliato perché un embedding non serve principalmente a comprimere il testo originale."
        ),
    },
    "AI-INT-0006": {
        "opzioni": [
            "Per verificare se il modello generalizza anche su casi nuovi",
            "Per confermare che il modello ricorda con precisione gli esempi usati in addestramento",
            "Per scegliere automaticamente nuovi esempi da aggiungere al training set",
            "Per aumentare il numero di esempi nel dataset senza controllare le prestazioni",
        ],
        "risposta_corretta": "Per verificare se il modello generalizza anche su casi nuovi",
        "spiegazione": (
            "Testare un modello su esempi diversi da quelli usati in addestramento serve a capire se generalizza su casi nuovi. "
            "Se funziona bene solo sui dati già visti, potrebbe aver memorizzato troppo il training set invece di imparare regole utili."
        ),
        "distrattore_forte": "Per confermare che il modello ricorda con precisione gli esempi usati in addestramento",
        "motivo_distrattore_forte": (
            "È vicino perché parla del rapporto tra test e dati di addestramento, "
            "ma è sbagliato perché il test deve misurare la generalizzazione, non la memoria degli esempi già visti."
        ),
    },
    "AI-INT-0007": {
        "opzioni": [
            "Specificare ruolo, obiettivo, vincoli e formato della risposta",
            "Specificare solo il ruolo del modello, senza indicare vincoli, obiettivo e formato",
            "Fornire molti obiettivi diversi senza indicare priorità",
            "Chiedere una risposta generica lasciando formato e criteri aperti",
        ],
        "risposta_corretta": "Specificare ruolo, obiettivo, vincoli e formato della risposta",
        "spiegazione": (
            "Un prompt controllabile chiarisce cosa deve fare il modello, con quali vincoli e in quale formato. "
            "Specificare solo il ruolo può aiutare, ma non basta se mancano obiettivo, vincoli e formato. "
            "Richieste vaghe o con obiettivi confusi aumentano il rischio di risposte generiche."
        ),
        "distrattore_forte": "Specificare solo il ruolo del modello, senza indicare vincoli, obiettivo e formato",
        "motivo_distrattore_forte": (
            "È vicino perché il ruolo è un elemento utile del prompt, "
            "ma è incompleto: per controllare davvero la risposta servono anche obiettivo, vincoli e formato."
        ),
    },
    "AI-INT-0008": {
        "opzioni": [
            "Il modello può imparare a favorire quella classe nelle previsioni",
            "Il modello può imparare a favorire la classe meno presente per compensare automaticamente lo sbilanciamento",
            "Il modello può migliorare sulle classi rare anche senza esempi sufficienti",
            "Il modello può rendere inutile ogni metrica diversa dall'accuratezza",
        ],
        "risposta_corretta": "Il modello può imparare a favorire quella classe nelle previsioni",
        "spiegazione": (
            "Se una classe è molto più presente delle altre, il modello può imparare a prevederla troppo spesso. "
            "Questo può dare un risultato apparentemente buono, ma peggiorare il riconoscimento delle classi meno rappresentate. "
            "Per questo l'accuratezza da sola può non bastare."
        ),
        "distrattore_forte": "Il modello può imparare a favorire la classe meno presente per compensare automaticamente lo sbilanciamento",
        "motivo_distrattore_forte": (
            "È vicino perché parla dello sbilanciamento tra classi, "
            "ma è sbagliato perché normalmente il modello tende a favorire la classe più presente, non quella rara."
        ),
    },
    "AI-INT-0009": {
        "opzioni": [
            "Uno strumento esterno che l'agente può usare per compiere un'azione",
            "Uno strumento esterno che l'agente può consultare, ma che non può mai eseguire azioni",
            "Una memoria conversazionale che conserva informazioni tra più messaggi",
            "Un'istruzione di sistema che definisce il comportamento dell'agente",
        ],
        "risposta_corretta": "Uno strumento esterno che l'agente può usare per compiere un'azione",
        "spiegazione": (
            "In un agente AI, un tool è uno strumento esterno che permette di compiere azioni, per esempio cercare dati, "
            "leggere file, chiamare API o fare calcoli. Memoria e istruzioni di sistema sono componenti importanti, "
            "ma non sono tool."
        ),
        "distrattore_forte": "Uno strumento esterno che l'agente può consultare, ma che non può mai eseguire azioni",
        "motivo_distrattore_forte": (
            "È vicino perché parla comunque di uno strumento esterno usato dall'agente, "
            "ma è sbagliato perché un tool può anche eseguire azioni, non solo essere consultato."
        ),
    },
    "AI-AV-0004": {
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
            "Il modello può generare una risposta sempre corretta, anche se il contesto recuperato è solo apparentemente pertinente",
            "Il modello può rifiutare automaticamente tutti i documenti recuperati",
            "Il modello può bloccare la generazione ogni volta che il retrieval non è perfetto",
        ],
        "risposta_corretta": "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
        "spiegazione": (
            "Se il retrieval recupera documenti solo apparentemente pertinenti, il modello può costruire una risposta fluida "
            "ma fondata su contesto sbagliato. È un problema delicato perché la forma della risposta può sembrare convincente "
            "anche quando la base informativa è debole."
        ),
        "distrattore_forte": "Il modello può generare una risposta sempre corretta, anche se il contesto recuperato è solo apparentemente pertinente",
        "motivo_distrattore_forte": (
            "È vicino perché collega risposta e contesto recuperato, "
            "ma è sbagliato perché un contesto solo apparentemente pertinente non garantisce una risposta corretta."
        ),
    },
    "AI-AV-0005": {
        "opzioni": [
            "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
            "Perché basta valutare la completezza, senza considerare coerenza, sicurezza e utilità",
            "Perché una risposta va valutata solo in base al formato richiesto",
            "Perché una risposta va valutata solo in base alla fluidità del testo",
        ],
        "risposta_corretta": "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
        "spiegazione": (
            "Nei compiti generativi non basta sempre distinguere tra corretto e sbagliato. "
            "Una risposta può essere parzialmente corretta, incompleta, poco sicura, fuori contesto o poco utile. "
            "Per questo servono criteri più ricchi, come completezza, coerenza, sicurezza e utilità."
        ),
        "distrattore_forte": "Perché basta valutare la completezza, senza considerare coerenza, sicurezza e utilità",
        "motivo_distrattore_forte": (
            "È vicino perché la completezza è davvero un criterio utile, "
            "ma è sbagliato perché da sola non basta: servono anche coerenza, sicurezza e utilità."
        ),
    },
    "AI-AV-0006": {
        "opzioni": [
            "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
            "Il modello può ricevere istruzioni esterne, ma queste possono influenzare solo lo stile della risposta",
            "Il modello può confondere contenuto dell'utente e istruzioni operative solo senza tool collegati",
            "Il modello può trattare informazioni recuperate come testo da copiare, ma non come comandi",
        ],
        "risposta_corretta": "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
        "spiegazione": (
            "Una prompt injection tenta di manipolare il comportamento del modello, facendogli trattare contenuti esterni come istruzioni. "
            "Il rischio principale, soprattutto con tool esterni, è che il modello ignori le istruzioni originali e compia azioni non previste."
        ),
        "distrattore_forte": "Il modello può ricevere istruzioni esterne, ma queste possono influenzare solo lo stile della risposta",
        "motivo_distrattore_forte": (
            "È vicino perché parla di istruzioni esterne, "
            "ma è sbagliato perché una prompt injection può influenzare anche comportamento e uso dei tool, non solo lo stile."
        ),
    },
    "AI-AV-0007": {
        "opzioni": [
            "Quando servono comportamenti stabili e specifici su molti esempi simili",
            "Quando serve un comportamento stabile, ma si dispone di un solo esempio isolato",
            "Quando il problema dipende soprattutto da documenti recuperati male",
            "Quando basta cambiare il prompt per correggere una risposta singola",
        ],
        "risposta_corretta": "Quando servono comportamenti stabili e specifici su molti esempi simili",
        "spiegazione": (
            "Il fine-tuning ha senso quando si vuole rendere stabile uno stile, un formato o un comportamento su molti casi simili. "
            "Per problemi singoli o istruzioni semplici può bastare il prompt engineering; se il retrieval è sbagliato, "
            "invece, va corretta la pipeline di recupero."
        ),
        "distrattore_forte": "Quando serve un comportamento stabile, ma si dispone di un solo esempio isolato",
        "motivo_distrattore_forte": (
            "È vicino perché parla di comportamento stabile, "
            "ma è sbagliato perché il fine-tuning richiede esempi coerenti e numerosi, non un solo caso isolato."
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
    print("Domande AI certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Secondo blocco AI certificato correttamente.")


main()