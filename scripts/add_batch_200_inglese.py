import json
from pathlib import Path


# Questo script aggiunge il blocco Inglese della seconda espansione.
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_inglese = [
    {
        "id": "ING-FAC-0101",
        "categoria": "inglese",
        "sottocategoria": "vocabolario",
        "livello": "facile",
        "domanda": "Quale parola inglese significa 'finestra'?",
        "opzioni": [
            "window",
            "wall",
            "door",
            "floor"
        ],
        "risposta_corretta": "window",
        "spiegazione": "'Window' significa finestra. 'Wall' significa muro, 'door' significa porta, mentre 'floor' significa pavimento.",
        "tags": [
            "vocabolario",
            "oggetti",
            "base"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0102",
        "categoria": "inglese",
        "sottocategoria": "pronomi",
        "livello": "facile",
        "domanda": "Completa la frase: ___ am from Italy.",
        "opzioni": [
            "I",
            "You",
            "He",
            "They"
        ],
        "risposta_corretta": "I",
        "spiegazione": "Con il verbo 'am' si usa il soggetto 'I'. La frase corretta è: 'I am from Italy'.",
        "tags": [
            "pronomi",
            "to_be",
            "base"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0103",
        "categoria": "inglese",
        "sottocategoria": "possessivi",
        "livello": "facile",
        "domanda": "Completa la frase: This is Marco. ___ phone is new.",
        "opzioni": [
            "His",
            "Her",
            "Their",
            "Our"
        ],
        "risposta_corretta": "His",
        "spiegazione": "Marco è maschile singolare, quindi il possessivo corretto è 'his'. La frase significa: Questo è Marco. Il suo telefono è nuovo.",
        "tags": [
            "possessivi",
            "pronomi",
            "base"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0104",
        "categoria": "inglese",
        "sottocategoria": "domande",
        "livello": "facile",
        "domanda": "Quale frase è una domanda corretta al presente semplice?",
        "opzioni": [
            "Do you like coffee?",
            "You like coffee?",
            "Does you like coffee?",
            "Are you like coffee?"
        ],
        "risposta_corretta": "Do you like coffee?",
        "spiegazione": "Nel present simple, con 'you' si usa l'ausiliare 'do' per formare la domanda: 'Do you like coffee?'. 'Does' si usa con he/she/it.",
        "tags": [
            "domande",
            "present_simple",
            "ausiliari"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0105",
        "categoria": "inglese",
        "sottocategoria": "preposizioni",
        "livello": "facile",
        "domanda": "Completa la frase: I go to work ___ bus.",
        "opzioni": [
            "by",
            "on",
            "at",
            "with"
        ],
        "risposta_corretta": "by",
        "spiegazione": "Per indicare il mezzo di trasporto in generale si usa 'by': by bus, by train, by car. La frase corretta è: 'I go to work by bus'.",
        "tags": [
            "preposizioni",
            "trasporti",
            "base"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0106",
        "categoria": "inglese",
        "sottocategoria": "verbi_modali",
        "livello": "facile",
        "domanda": "Completa la frase: I ___ swim, but I can't drive.",
        "opzioni": [
            "can",
            "must",
            "should",
            "will"
        ],
        "risposta_corretta": "can",
        "spiegazione": "'Can' indica capacità: 'I can swim' significa 'so nuotare'. 'Must' indica obbligo, 'should' consiglio, 'will' futuro.",
        "tags": [
            "can",
            "modali",
            "capacita"
        ],
        "difficolta": 1
    },
    {
        "id": "ING-INT-0101",
        "categoria": "inglese",
        "sottocategoria": "since_for",
        "livello": "intermedio",
        "domanda": "Completa la frase: I have lived in Rome ___ 2020.",
        "opzioni": [
            "since",
            "for",
            "during",
            "from"
        ],
        "risposta_corretta": "since",
        "spiegazione": "Con il present perfect si usa 'since' quando indichiamo il punto di inizio, come un anno preciso: 'since 2020'. 'For' si usa con una durata, per esempio 'for three years'.",
        "tags": [
            "present_perfect",
            "since",
            "for"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0102",
        "categoria": "inglese",
        "sottocategoria": "countable_uncountable",
        "livello": "intermedio",
        "domanda": "Completa la frase: There isn't ___ information on the website.",
        "opzioni": [
            "much",
            "many",
            "few",
            "several"
        ],
        "risposta_corretta": "much",
        "spiegazione": "'Information' in inglese è normalmente non numerabile. Con i nomi non numerabili si usa 'much', non 'many'.",
        "tags": [
            "much",
            "many",
            "uncountable"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0103",
        "categoria": "inglese",
        "sottocategoria": "gerundio_infinito",
        "livello": "intermedio",
        "domanda": "Completa la frase: I enjoy ___ new programming languages.",
        "opzioni": [
            "learning",
            "to learn",
            "learn",
            "learned"
        ],
        "risposta_corretta": "learning",
        "spiegazione": "Dopo il verbo 'enjoy' si usa il verbo in -ing. La frase corretta è: 'I enjoy learning new programming languages'.",
        "tags": [
            "gerundio",
            "verbi",
            "inglese_tecnico"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0104",
        "categoria": "inglese",
        "sottocategoria": "too_enough",
        "livello": "intermedio",
        "domanda": "Completa la frase: The file is too large ___ upload.",
        "opzioni": [
            "to",
            "for",
            "than",
            "that"
        ],
        "risposta_corretta": "to",
        "spiegazione": "La struttura corretta è 'too + aggettivo + to + verbo'. Quindi: 'The file is too large to upload'.",
        "tags": [
            "too",
            "strutture",
            "grammatica"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0105",
        "categoria": "inglese",
        "sottocategoria": "conditionals",
        "livello": "intermedio",
        "domanda": "Completa la frase: If I had more time, I ___ a second project.",
        "opzioni": [
            "would start",
            "will start",
            "start",
            "started"
        ],
        "risposta_corretta": "would start",
        "spiegazione": "Questa è una frase del second conditional: if + past simple, would + verbo base. Quindi: 'If I had more time, I would start a second project'.",
        "tags": [
            "second_conditional",
            "would",
            "if"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0106",
        "categoria": "inglese",
        "sottocategoria": "phrasal_verbs",
        "livello": "intermedio",
        "domanda": "Nella frase 'I need to set up the app', che cosa significa 'set up'?",
        "opzioni": [
            "configurare",
            "spegnere",
            "cercare",
            "rimandare"
        ],
        "risposta_corretta": "configurare",
        "spiegazione": "'Set up' significa configurare, preparare o impostare qualcosa. In questo caso: devo configurare l'app.",
        "tags": [
            "phrasal_verbs",
            "set_up",
            "software"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0107",
        "categoria": "inglese",
        "sottocategoria": "comparativi",
        "livello": "intermedio",
        "domanda": "Completa la frase: This laptop is ___ than my old one.",
        "opzioni": [
            "faster",
            "fastest",
            "more fast",
            "fastly"
        ],
        "risposta_corretta": "faster",
        "spiegazione": "Con un aggettivo breve come 'fast' il comparativo si forma aggiungendo -er: 'faster'. 'Fastest' è superlativo.",
        "tags": [
            "comparativo",
            "aggettivi",
            "tecnologia"
        ],
        "difficolta": 2
    },
    {
        "id": "ING-AV-0101",
        "categoria": "inglese",
        "sottocategoria": "connettivi",
        "livello": "avanzato",
        "domanda": "Completa la frase: The software is reliable; ___, it still needs regular maintenance.",
        "opzioni": [
            "nevertheless",
            "therefore",
            "because",
            "provided that"
        ],
        "risposta_corretta": "nevertheless",
        "spiegazione": "'Nevertheless' introduce un contrasto simile a 'however': il software è affidabile, tuttavia ha comunque bisogno di manutenzione.",
        "tags": [
            "connettivi",
            "contrasto",
            "inglese_avanzato"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0102",
        "categoria": "inglese",
        "sottocategoria": "relative_clauses",
        "livello": "avanzato",
        "domanda": "Quale frase usa correttamente una relative clause riferita a un server?",
        "opzioni": [
            "The server that hosts the database is offline.",
            "The server who hosts the database is offline.",
            "The server where hosts the database is offline.",
            "The server whose hosts the database is offline."
        ],
        "risposta_corretta": "The server that hosts the database is offline.",
        "spiegazione": "Per riferirsi a una cosa, come 'server', si può usare 'that' o 'which'. Qui 'that hosts the database' è corretto. 'Who' si usa per persone, mentre 'where' e 'whose' non funzionano in questa struttura.",
        "tags": [
            "relative_clauses",
            "that",
            "software"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0103",
        "categoria": "inglese",
        "sottocategoria": "passive_voice",
        "livello": "avanzato",
        "domanda": "In un report tecnico, quale frase indica che il problema è stato risolto senza specificare chi lo ha risolto?",
        "opzioni": [
            "The issue has been fixed.",
            "The issue has fixed.",
            "The issue was been fixed.",
            "The issue has been fix."
        ],
        "risposta_corretta": "The issue has been fixed.",
        "spiegazione": "La frase corretta usa il passivo: 'has been' + participio passato. Quindi la forma giusta è 'The issue has been fixed'. È utile quando interessa il risultato dell'azione, non chi l'ha compiuta.",
        "tags": [
            "passive_voice",
            "technical_english",
            "software"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0104",
        "categoria": "inglese",
        "sottocategoria": "reported_speech",
        "livello": "avanzato",
        "domanda": "Trasforma correttamente in discorso indiretto: 'We will release the update tomorrow.'",
        "opzioni": [
            "They said they would release the update the next day.",
            "They said they will release the update tomorrow.",
            "They said they released the update the next day.",
            "They said they had released the update tomorrow."
        ],
        "risposta_corretta": "They said they would release the update the next day.",
        "spiegazione": "Nel discorso indiretto, 'will' diventa spesso 'would' e 'tomorrow' diventa 'the next day', se il riferimento temporale cambia.",
        "tags": [
            "reported_speech",
            "would",
            "software"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0105",
        "categoria": "inglese",
        "sottocategoria": "modali",
        "livello": "avanzato",
        "domanda": "Completa la frase: If I had known about the error, I ___ it earlier.",
        "opzioni": [
            "would have fixed",
            "will have fixed",
            "would fix",
            "had fixed"
        ],
        "risposta_corretta": "would have fixed",
        "spiegazione": "Questa frase usa il third conditional: If + past perfect, would have + participio passato. La forma corretta è quindi: 'If I had known about the error, I would have fixed it earlier'.",
        "tags": [
            "third_conditional",
            "would_have",
            "grammar"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0106",
        "categoria": "inglese",
        "sottocategoria": "traduzione_tecnica",
        "livello": "avanzato",
        "domanda": "Nel contesto software, quale traduzione rende meglio 'The app crashed during startup'?",
        "opzioni": [
            "L'app si è bloccata durante l'avvio.",
            "L'app ha migliorato l'avvio.",
            "L'app è stata aggiornata durante l'avvio.",
            "L'app ha ignorato l'avvio."
        ],
        "risposta_corretta": "L'app si è bloccata durante l'avvio.",
        "spiegazione": "Nel contesto software, 'to crash' significa bloccarsi o andare in errore. 'During startup' significa durante l'avvio.",
        "tags": [
            "traduzione",
            "software",
            "crash"
        ],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0107",
        "categoria": "inglese",
        "sottocategoria": "registro_formale",
        "livello": "avanzato",
        "domanda": "Quale frase è più adatta in una comunicazione professionale?",
        "opzioni": [
            "Could you please send me the updated file?",
            "Send me the file now.",
            "Give me that file quickly.",
            "You send the file to me."
        ],
        "risposta_corretta": "Could you please send me the updated file?",
        "spiegazione": "'Could you please...' è una forma educata e professionale per fare una richiesta. Le altre frasi sono troppo dirette o poco naturali in un contesto formale.",
        "tags": [
            "registro_formale",
            "richieste",
            "email"
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
        for domanda in nuove_domande_inglese
    }

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_inglese

    salva_domande(domande_finali)

    print("Blocco Inglese aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Inglese:", len(nuove_domande_inglese))
    print("Domande totali in batch_200:", len(domande_finali))


main()
