import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")

PERCORSO_SCRIPT_INGLESE = Path("scripts/add_batch_200_inglese.py")
PERCORSO_SCRIPT_MATEMATICA = Path("scripts/add_batch_200_matematica.py")
PERCORSO_SCRIPT_LOGICA = Path("scripts/add_batch_200_logica.py")


CORREZIONI = {
    "ING-AV-0102": {
        "domanda": "Quale frase usa correttamente una relative clause riferita a un server?",
        "opzioni": [
            "The server that hosts the database is offline.",
            "The server who hosts the database is offline.",
            "The server where hosts the database is offline.",
            "The server whose hosts the database is offline."
        ],
        "risposta_corretta": "The server that hosts the database is offline.",
        "spiegazione": (
            "Per riferirsi a una cosa, come 'server', si può usare 'that' o 'which'. "
            "Qui 'that hosts the database' è corretto. "
            "'Who' si usa per persone, mentre 'where' e 'whose' non funzionano in questa struttura."
        ),
        "tags": ["relative_clauses", "that", "software"]
    },

    "ING-AV-0103": {
        "domanda": "In un report tecnico, quale frase indica che il problema è stato risolto senza specificare chi lo ha risolto?",
        "opzioni": [
            "The issue has been fixed.",
            "The issue has fixed.",
            "The issue was been fixed.",
            "The issue has been fix."
        ],
        "risposta_corretta": "The issue has been fixed.",
        "spiegazione": (
            "La frase corretta usa il passivo: 'has been' + participio passato. "
            "Quindi la forma giusta è 'The issue has been fixed'. "
            "È utile quando interessa il risultato dell'azione, non chi l'ha compiuta."
        ),
        "tags": ["passive_voice", "technical_english", "software"]
    },

    "MAT-INT-0103": {
        "domanda": "Un servizio costa 6 euro di attivazione più 5 euro al mese. Se il totale è 31 euro, quanti mesi sono stati pagati?",
        "opzioni": [
            "5 mesi",
            "4 mesi",
            "6 mesi",
            "7 mesi"
        ],
        "risposta_corretta": "5 mesi",
        "spiegazione": (
            "Prima togliamo il costo fisso di attivazione: 31 - 6 = 25 euro. "
            "Ogni mese costa 5 euro, quindi 25 / 5 = 5 mesi."
        ),
        "tags": ["problemi", "equazioni", "calcolo"]
    },

    "MAT-AV-0101": {
        "domanda": "Un rettangolo ha perimetro 34 cm e base 10 cm. Qual è la sua altezza?",
        "opzioni": [
            "7 cm",
            "6 cm",
            "8 cm",
            "5 cm"
        ],
        "risposta_corretta": "7 cm",
        "spiegazione": (
            "Il perimetro del rettangolo è 2 × (base + altezza). "
            "Quindi 34 = 2 × (10 + altezza). "
            "Dividendo per 2 otteniamo 17 = 10 + altezza, quindi altezza = 7 cm."
        ),
        "tags": ["geometria", "rettangolo", "problemi"]
    },

    "MAT-AV-0104": {
        "domanda": "Da un gruppo di 5 persone bisogna scegliere presidente e vice. I ruoli sono diversi. Quante scelte possibili ci sono?",
        "opzioni": [
            "20",
            "10",
            "25",
            "15"
        ],
        "risposta_corretta": "20",
        "spiegazione": (
            "Per scegliere il presidente ci sono 5 possibilità. "
            "Dopo aver scelto il presidente, restano 4 possibilità per il vice. "
            "Poiché i ruoli sono diversi, il totale è 5 × 4 = 20."
        ),
        "tags": ["combinatoria", "ruoli", "calcolo"]
    },

    "LOG-NUM-FAC-0101": {
        "domanda": "Una macchina produce 4 pezzi al minuto. Quanti pezzi produce in 5 minuti?",
        "opzioni": [
            "20",
            "18",
            "22",
            "24"
        ],
        "risposta_corretta": "20",
        "spiegazione": (
            "La macchina produce 4 pezzi ogni minuto. "
            "In 5 minuti produce 4 × 5 = 20 pezzi."
        ),
        "tags": ["moltiplicazione", "problemi", "logica_numerica"]
    },

    "LOG-NUM-FAC-0102": {
        "domanda": "Partendo da 3, un numero viene raddoppiato quattro volte. Quale valore si ottiene?",
        "opzioni": [
            "48",
            "36",
            "42",
            "50"
        ],
        "risposta_corretta": "48",
        "spiegazione": (
            "Partiamo da 3. Primo raddoppio: 6. "
            "Secondo: 12. Terzo: 24. Quarto: 48."
        ),
        "tags": ["raddoppio", "calcolo", "logica_numerica"]
    },

    "LOG-NUM-INT-0101": {
        "domanda": "Un algoritmo parte da 2. A ogni passaggio raddoppia il valore e aggiunge 1. Dopo quattro passaggi quale valore ottiene?",
        "opzioni": [
            "47",
            "45",
            "46",
            "49"
        ],
        "risposta_corretta": "47",
        "spiegazione": (
            "Partiamo da 2. "
            "Passaggio 1: 2 × 2 + 1 = 5. "
            "Passaggio 2: 5 × 2 + 1 = 11. "
            "Passaggio 3: 11 × 2 + 1 = 23. "
            "Passaggio 4: 23 × 2 + 1 = 47."
        ),
        "tags": ["algoritmo", "pattern", "logica_numerica"]
    },

    "LOG-NUM-AV-0102": {
        "domanda": "Le differenze tra valori consecutivi sono 4, 6, 8 e 10. Se l'ultimo valore noto è 30, quale sarà il valore successivo?",
        "opzioni": [
            "42",
            "40",
            "44",
            "48"
        ],
        "risposta_corretta": "42",
        "spiegazione": (
            "Le differenze aumentano di 2: 4, 6, 8, 10. "
            "La differenza successiva è 12. "
            "Quindi 30 + 12 = 42."
        ),
        "tags": ["differenze", "pattern", "logica_numerica"]
    },

    "LOG-VER-AV-0101": {
        "domanda": "Completa l'analogia: allenamento sta a miglioramento come studio sta a ___?",
        "opzioni": [
            "apprendimento",
            "interrogazione",
            "lezione",
            "materia"
        ],
        "risposta_corretta": "apprendimento",
        "spiegazione": (
            "L'allenamento può portare a un miglioramento. "
            "Allo stesso modo, lo studio può portare ad apprendimento. "
            "Interrogazione, lezione e materia sono collegate allo studio, "
            "ma non rappresentano il risultato logico più diretto."
        ),
        "tags": ["analogie", "causa_effetto", "logica_verbale"]
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


def aggiorna_domande(domande):
    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI:
            correzione = CORREZIONI[id_domanda]

            domanda["domanda"] = correzione["domanda"]
            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]
            domanda["tags"] = correzione["tags"]

            modifiche += 1

    return modifiche


def crea_script_categoria(percorso_script, nome_lista, categoria, prefisso_id, filtro_id, titolo):
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    domande_categoria = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("categoria") == categoria
        and domanda.get("id", "").startswith(prefisso_id)
        and filtro_id in domanda.get("id", "")
    ]

    contenuto_lista = json.dumps(
        domande_categoria,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script aggiunge il blocco {titolo} della seconda espansione.
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


{nome_lista} = {contenuto_lista}


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

    nuovi_id = {{
        domanda["id"]
        for domanda in {nome_lista}
    }}

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + {nome_lista}

    salva_domande(domande_finali)

    print("Blocco {titolo} aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande {titolo}:", len({nome_lista}))
    print("Domande totali in batch_200:", len(domande_finali))


main()
'''

    percorso_script.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    modifiche = aggiorna_domande(domande_batch_200)

    salva_json(PERCORSO_BATCH_200, domande_batch_200)

    crea_script_categoria(
        PERCORSO_SCRIPT_INGLESE,
        "nuove_domande_inglese",
        "inglese",
        "ING-",
        "-01",
        "Inglese"
    )

    crea_script_categoria(
        PERCORSO_SCRIPT_MATEMATICA,
        "nuove_domande_matematica",
        "matematica",
        "MAT-",
        "-01",
        "Matematica"
    )

    crea_script_categoria(
        PERCORSO_SCRIPT_LOGICA,
        "nuove_domande_logica",
        "logica",
        "LOG-",
        "-010",
        "Logica"
    )

    print("Correzione finale qualità batch 200 completata.")
    print("Domande aggiornate:", modifiche)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_INGLESE)
    print(PERCORSO_SCRIPT_MATEMATICA)
    print(PERCORSO_SCRIPT_LOGICA)


main()