import json
from pathlib import Path


# Questo script aggiunge il blocco AI della seconda espansione.
# Obiettivo: portare il database da 100 a 200 domande totali.
# Questo primo blocco aggiunge 20 nuove domande AI.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_ai = [
    {
        "id": "AI-FAC-0101",
        "categoria": "ai",
        "sottocategoria": "fondamenti",
        "livello": "facile",
        "domanda": "Quale attività descrive meglio un modello di intelligenza artificiale?",
        "opzioni": [
            "Riconoscere schemi nei dati e usare questi schemi per produrre risposte o previsioni",
            "Memorizzare ogni file del computer senza modificarlo",
            "Sostituire automaticamente ogni programma installato sul dispositivo",
            "Collegare fisicamente due computer tramite un cavo"
        ],
        "risposta_corretta": "Riconoscere schemi nei dati e usare questi schemi per produrre risposte o previsioni",
        "spiegazione": "Un modello di intelligenza artificiale impara schemi dai dati e li usa per classificare, prevedere, generare testo o prendere decisioni. Non è semplicemente un archivio di file o un collegamento fisico tra dispositivi.",
        "tags": [
            "ai",
            "modelli",
            "fondamenti"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0102",
        "categoria": "ai",
        "sottocategoria": "prompting",
        "livello": "facile",
        "domanda": "Quale prompt è più chiaro per chiedere un riassunto?",
        "opzioni": [
            "Riassumi questo testo in 5 righe indicando le idee principali.",
            "Fammi una cosa su questo testo.",
            "Sistema tutto nel modo migliore possibile.",
            "Usa l'intelligenza artificiale sul contenuto."
        ],
        "risposta_corretta": "Riassumi questo testo in 5 righe indicando le idee principali.",
        "spiegazione": "Un prompt chiaro specifica cosa fare e con quale formato. Dire 'in 5 righe' e 'idee principali' rende il compito più controllabile.",
        "tags": [
            "prompt",
            "riassunto",
            "chiarezza"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0103",
        "categoria": "ai",
        "sottocategoria": "dati",
        "livello": "facile",
        "domanda": "Perché i dati di addestramento sono importanti per un modello AI?",
        "opzioni": [
            "Perché influenzano ciò che il modello impara e come risponde",
            "Perché rendono inutile controllare le risposte generate",
            "Perché impediscono al modello di commettere errori",
            "Perché sostituiscono sempre il codice dell'applicazione"
        ],
        "risposta_corretta": "Perché influenzano ciò che il modello impara e come risponde",
        "spiegazione": "Il modello impara dai dati disponibili durante l'addestramento. Se i dati sono incompleti, distorti o poco adatti, anche le risposte possono risentirne.",
        "tags": [
            "dataset",
            "addestramento",
            "qualita"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0104",
        "categoria": "ai",
        "sottocategoria": "classificazione",
        "livello": "facile",
        "domanda": "Quale esempio rappresenta meglio un compito di classificazione?",
        "opzioni": [
            "Stabilire se un messaggio è spam o non spam",
            "Scrivere una poesia partendo da un tema",
            "Disegnare un'icona per una nuova app",
            "Tradurre liberamente un romanzo completo"
        ],
        "risposta_corretta": "Stabilire se un messaggio è spam o non spam",
        "spiegazione": "La classificazione assegna un'etichetta a un input. Spam/non spam è un esempio classico perché il modello sceglie una categoria tra alternative definite.",
        "tags": [
            "classificazione",
            "spam",
            "categorie"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0105",
        "categoria": "ai",
        "sottocategoria": "generazione",
        "livello": "facile",
        "domanda": "Che cosa significa dire che un modello generativo produce testo?",
        "opzioni": [
            "Che crea una risposta nuova seguendo il contesto ricevuto",
            "Che copia sempre una frase identica dal database",
            "Che salva il testo solo in formato immagine",
            "Che cancella automaticamente il contenuto originale"
        ],
        "risposta_corretta": "Che crea una risposta nuova seguendo il contesto ricevuto",
        "spiegazione": "Un modello generativo produce una continuazione o una risposta in base al contesto. Non si limita necessariamente a copiare una frase identica.",
        "tags": [
            "generativa",
            "testo",
            "llm"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0106",
        "categoria": "ai",
        "sottocategoria": "allucinazioni",
        "livello": "facile",
        "domanda": "Quando si parla di allucinazione in AI, a cosa ci si riferisce?",
        "opzioni": [
            "A una risposta plausibile ma falsa o non verificata",
            "A una risposta corretta ma troppo breve per essere utile",
            "A una risposta basata solo su fonti citate e controllabili",
            "A una risposta incompleta ma dichiarata come incerta"
        ],
        "risposta_corretta": "A una risposta plausibile ma falsa o non verificata",
        "spiegazione": "Un'allucinazione in AI è una risposta che può sembrare credibile, ma contiene informazioni false, inventate o non verificate. Una risposta breve, incompleta o prudente può essere migliorabile, ma non è necessariamente un'allucinazione.",
        "tags": [
            "allucinazioni",
            "affidabilita",
            "verifica"
        ],
        "difficolta": 1
    },
    {
        "id": "AI-INT-0101",
        "categoria": "ai",
        "sottocategoria": "rag",
        "livello": "intermedio",
        "domanda": "In un sistema RAG, perché la scelta dei chunk del documento è importante?",
        "opzioni": [
            "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
            "Perché i chunk servono solo a cambiare il colore del testo recuperato",
            "Perché ogni chunk deve contenere sempre l'intero database",
            "Perché i chunk eliminano automaticamente tutte le risposte sbagliate"
        ],
        "risposta_corretta": "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
        "spiegazione": "Nei sistemi RAG i documenti vengono spesso divisi in parti più piccole, chiamate chunk. Se i chunk sono troppo grandi, possono contenere troppe informazioni non pertinenti. Se sono troppo piccoli, possono perdere contesto utile. La dimensione dei chunk influenza quindi la qualità del recupero.",
        "tags": [
            "rag",
            "chunking",
            "retrieval"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0102",
        "categoria": "ai",
        "sottocategoria": "embedding",
        "livello": "intermedio",
        "domanda": "Quale differenza c'è tra ricerca per parole esatte e ricerca semantica?",
        "opzioni": [
            "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
            "La ricerca semantica funziona solo se la frase contiene le stesse parole identiche",
            "La ricerca per parole esatte interpreta sempre il significato profondo della domanda",
            "La ricerca semantica elimina la necessità di controllare i risultati trovati"
        ],
        "risposta_corretta": "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
        "spiegazione": "La ricerca per parole esatte cerca corrispondenze letterali. La ricerca semantica invece prova a confrontare il significato dei contenuti, quindi può trovare testi pertinenti anche se usano parole diverse dalla domanda.",
        "tags": [
            "ricerca_semantica",
            "similarita",
            "retrieval"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0103",
        "categoria": "ai",
        "sottocategoria": "valutazione",
        "livello": "intermedio",
        "domanda": "Perché è utile testare un modello su esempi che non ha visto durante lo sviluppo?",
        "opzioni": [
            "Per misurare se generalizza oltre i casi usati per costruirlo",
            "Per assicurarsi che memorizzi esattamente tutte le risposte",
            "Per ridurre sempre a zero il costo di esecuzione",
            "Per eliminare la necessità di dati di validazione"
        ],
        "risposta_corretta": "Per misurare se generalizza oltre i casi usati per costruirlo",
        "spiegazione": "Un modello deve funzionare anche su casi nuovi. Testarlo solo su esempi già visti rischia di misurare la memoria, non la capacità di generalizzare.",
        "tags": [
            "valutazione",
            "generalizzazione",
            "test"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0104",
        "categoria": "ai",
        "sottocategoria": "prompting",
        "livello": "intermedio",
        "domanda": "Quale indicazione rende un prompt più controllabile?",
        "opzioni": [
            "Specificare ruolo, obiettivo, formato di risposta e vincoli",
            "Chiedere al modello di fare semplicemente il meglio possibile",
            "Evitare qualsiasi contesto per lasciare più libertà",
            "Usare solo una parola senza spiegare il compito"
        ],
        "risposta_corretta": "Specificare ruolo, obiettivo, formato di risposta e vincoli",
        "spiegazione": "Ruolo, obiettivo, formato e vincoli aiutano il modello a produrre una risposta più coerente con ciò che serve davvero.",
        "tags": [
            "prompt",
            "controllo",
            "istruzioni"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0105",
        "categoria": "ai",
        "sottocategoria": "bias",
        "livello": "intermedio",
        "domanda": "Che cosa può succedere se un dataset è molto sbilanciato?",
        "opzioni": [
            "Il modello può funzionare bene su alcuni casi e male su altri meno rappresentati",
            "Il modello diventa automaticamente più equo in ogni situazione",
            "Il modello smette sempre di produrre risposte",
            "Il modello cancella da solo gli esempi in eccesso"
        ],
        "risposta_corretta": "Il modello può funzionare bene su alcuni casi e male su altri meno rappresentati",
        "spiegazione": "Se alcune classi o situazioni sono poco rappresentate, il modello può imparare soprattutto i casi più frequenti e commettere più errori sui casi rari.",
        "tags": [
            "bias",
            "dataset",
            "sbilanciamento"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0106",
        "categoria": "ai",
        "sottocategoria": "agenti",
        "livello": "intermedio",
        "domanda": "Perché un agente AI può usare una fase di pianificazione prima di agire?",
        "opzioni": [
            "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
            "Per impedire sempre all'utente di modificare la richiesta",
            "Per trasformare ogni risposta in una lista casuale di operazioni",
            "Per saltare completamente il controllo del risultato finale"
        ],
        "risposta_corretta": "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
        "spiegazione": "Un agente AI può pianificare prima di agire per decidere quali passaggi seguire, quali strumenti usare e in quale ordine. Questo riduce il rischio di azioni impulsive o poco coerenti con l'obiettivo.",
        "tags": [
            "agenti",
            "pianificazione",
            "tool_use"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0107",
        "categoria": "ai",
        "sottocategoria": "sicurezza",
        "livello": "intermedio",
        "domanda": "Perché conviene limitare le azioni che un agente AI può eseguire automaticamente?",
        "opzioni": [
            "Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose",
            "Per impedire al modello di leggere qualsiasi istruzione dell'utente",
            "Per rendere impossibile ogni controllo umano",
            "Per aumentare sempre la lunghezza delle risposte"
        ],
        "risposta_corretta": "Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose",
        "spiegazione": "Un agente con troppi permessi può fare danni se interpreta male un comando o subisce prompt injection. Limitare permessi e richiedere conferme rende il sistema più sicuro.",
        "tags": [
            "sicurezza",
            "agenti",
            "permessi"
        ],
        "difficolta": 2
    },
    {
        "id": "AI-AV-0101",
        "categoria": "ai",
        "sottocategoria": "rag",
        "livello": "avanzato",
        "domanda": "Qual è un rischio importante se il retrieval di un sistema RAG recupera documenti solo apparentemente pertinenti?",
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto fuorviante",
            "Il modello smette automaticamente di generare testo",
            "Il database vettoriale elimina tutti i documenti non usati",
            "Il prompt dell'utente viene sempre ignorato completamente"
        ],
        "risposta_corretta": "Il modello può generare una risposta ben scritta ma basata su contesto fuorviante",
        "spiegazione": "Se i documenti recuperati sembrano pertinenti ma non rispondono davvero alla domanda, il modello può appoggiarsi a informazioni sbagliate o parziali e produrre una risposta convincente ma non affidabile.",
        "tags": [
            "rag",
            "retrieval",
            "qualita"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0102",
        "categoria": "ai",
        "sottocategoria": "fine_tuning",
        "livello": "avanzato",
        "domanda": "Quando il fine-tuning è più adatto del solo prompt engineering?",
        "opzioni": [
            "Quando serve modificare stabilmente il comportamento del modello su molti esempi simili",
            "Quando bisogna correggere una singola risposta occasionale",
            "Quando si vuole evitare qualunque raccolta di esempi",
            "Quando basta cambiare il tono di una frase una sola volta"
        ],
        "risposta_corretta": "Quando serve modificare stabilmente il comportamento del modello su molti esempi simili",
        "spiegazione": "Il fine-tuning è utile se si hanno esempi di qualità e si vuole rendere stabile un comportamento su una famiglia di compiti. Per modifiche leggere o occasionali spesso basta il prompt.",
        "tags": [
            "fine_tuning",
            "prompting",
            "addestramento"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0103",
        "categoria": "ai",
        "sottocategoria": "valutazione",
        "livello": "avanzato",
        "domanda": "Perché valutare un sistema AI solo con risposta corretta o sbagliata può essere insufficiente?",
        "opzioni": [
            "Perché possono contare anche completezza, fonti, robustezza, sicurezza e chiarezza",
            "Perché una metrica binaria misura sempre anche il costo computazionale",
            "Perché ogni risposta generata è sempre corretta se è scritta bene",
            "Perché la valutazione deve ignorare il contesto della domanda"
        ],
        "risposta_corretta": "Perché possono contare anche completezza, fonti, robustezza, sicurezza e chiarezza",
        "spiegazione": "Molti sistemi AI non producono solo una risposta secca. Serve valutare qualità, affidabilità, aderenza al contesto, sicurezza e capacità di gestire casi difficili.",
        "tags": [
            "valutazione",
            "metriche",
            "qualita"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0104",
        "categoria": "ai",
        "sottocategoria": "prompt_injection",
        "livello": "avanzato",
        "domanda": "Qual è un esempio realistico di prompt injection in un'app che legge documenti esterni?",
        "opzioni": [
            "Un documento contiene istruzioni nascoste che provano a far ignorare le regole del sistema",
            "Un utente scrive una domanda troppo breve per essere capita",
            "Un file viene salvato in una cartella con un nome lungo",
            "Una risposta contiene una parola inglese invece di una italiana"
        ],
        "risposta_corretta": "Un documento contiene istruzioni nascoste che provano a far ignorare le regole del sistema",
        "spiegazione": "La prompt injection può arrivare anche da contenuti esterni. Un documento può contenere istruzioni malevole che cercano di far cambiare comportamento al modello o ai tool collegati.",
        "tags": [
            "prompt_injection",
            "sicurezza",
            "documenti"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0105",
        "categoria": "ai",
        "sottocategoria": "architettura",
        "livello": "avanzato",
        "domanda": "Perché in un'app AI conviene separare recupero dei dati, generazione e controllo finale?",
        "opzioni": [
            "Per rendere più chiaro dove nasce un errore e migliorare ogni fase separatamente",
            "Per fare in modo che il modello non riceva mai alcun contesto",
            "Per impedire all'app di usare database o API",
            "Per obbligare l'utente a scrivere tre domande diverse"
        ],
        "risposta_corretta": "Per rendere più chiaro dove nasce un errore e migliorare ogni fase separatamente",
        "spiegazione": "Separare le fasi aiuta a capire se il problema nasce dal retrieval, dal prompt, dalla generazione o dal controllo finale. Questo rende debug e miglioramento molto più ordinati.",
        "tags": [
            "architettura",
            "debug",
            "pipeline"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0106",
        "categoria": "ai",
        "sottocategoria": "memoria",
        "livello": "avanzato",
        "domanda": "Quale rischio nasce se un agente salva memoria personale senza criteri chiari?",
        "opzioni": [
            "Può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto",
            "Diventa automaticamente incapace di rispondere a domande generali",
            "Non può più usare alcun prompt dell'utente",
            "Trasforma ogni informazione salvata in codice eseguibile"
        ],
        "risposta_corretta": "Può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto",
        "spiegazione": "La memoria può migliorare la personalizzazione, ma va gestita con criteri: cosa salvare, cosa evitare, quando aggiornare e come rispettare privacy e pertinenza.",
        "tags": [
            "memoria",
            "privacy",
            "agenti"
        ],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0107",
        "categoria": "ai",
        "sottocategoria": "monitoraggio",
        "livello": "avanzato",
        "domanda": "Perché un'app AI in produzione dovrebbe registrare errori e feedback degli utenti?",
        "opzioni": [
            "Per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità",
            "Per dimostrare che il modello non sbaglia mai",
            "Per sostituire ogni test prima del rilascio",
            "Per evitare qualsiasi aggiornamento futuro del sistema"
        ],
        "risposta_corretta": "Per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità",
        "spiegazione": "I test iniziali non coprono tutti gli scenari. Log e feedback aiutano a scoprire errori ricorrenti, casi limite e problemi di sicurezza emersi nell'uso reale.",
        "tags": [
            "monitoraggio",
            "feedback",
            "produzione"
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
        for domanda in nuove_domande_ai
    }

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_ai

    salva_domande(domande_finali)

    print("Blocco AI aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande AI:", len(nuove_domande_ai))
    print("Domande totali in batch_200:", len(domande_finali))


main()
