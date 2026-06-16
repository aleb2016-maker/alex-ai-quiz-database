from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FISICA_JSON = ROOT / "data" / "fisica.json"
BACKUP_TMP = Path("/tmp/fisica_prima_revisione_batch2.json")

REVISIONI = {
    "FIS_020": {
        "opzioni": [
            "Una grandezza vettoriale ha modulo, direzione e verso; una scalare ha solo valore numerico",
            "Una grandezza vettoriale ha solo valore numerico; una scalare richiede direzione e verso",
            "Una grandezza scalare cambia unità di misura quando viene rappresentata con una freccia",
            "Una grandezza vettoriale descrive solo masse, mentre una scalare descrive solo forze",
        ],
        "risposta_corretta": "Una grandezza vettoriale ha modulo, direzione e verso; una scalare ha solo valore numerico",
        "spiegazione": (
            "Una grandezza scalare è descritta da un valore numerico e da un’unità di misura. "
            "Una grandezza vettoriale richiede anche direzione e verso, oltre al modulo."
        ),
    },

    "FIS_021": {
        "opzioni": [
            "La forza diventa un quarto perché dipende dall’inverso del quadrato della distanza",
            "La forza diventa la metà perché dipende direttamente dalla distanza tra le cariche",
            "La forza raddoppia perché la distanza maggiore aumenta l’interazione elettrica",
            "La forza resta invariata perché dipende solo dal segno delle cariche elettriche",
        ],
        "risposta_corretta": "La forza diventa un quarto perché dipende dall’inverso del quadrato della distanza",
        "spiegazione": (
            "Secondo la legge di Coulomb, la forza elettrica è inversamente proporzionale al quadrato "
            "della distanza. Se la distanza raddoppia, la forza diventa un quarto."
        ),
    },

    "FIS_023": {
        "opzioni": [
            "Un sistema oscilla con ampiezza elevata quando è sollecitato vicino alla sua frequenza naturale",
            "Un sistema smette di oscillare quando riceve energia alla propria frequenza naturale",
            "Un sistema perde massa quando viene sollecitato da una forza periodica esterna",
            "Un sistema trasforma ogni oscillazione meccanica in corrente elettrica continua",
        ],
        "risposta_corretta": "Un sistema oscilla con ampiezza elevata quando è sollecitato vicino alla sua frequenza naturale",
        "spiegazione": (
            "La risonanza avviene quando un sistema riceve una sollecitazione periodica vicina "
            "alla sua frequenza naturale. In questa condizione l’ampiezza dell’oscillazione può aumentare molto."
        ),
    },

    "FIS_025": {
        "opzioni": [
            "Perché riflette parte della luce proveniente da una sorgente verso i nostri occhi",
            "Perché produce luce propria quando viene osservato da un osservatore vicino",
            "Perché assorbe tutta la luce incidente e la trasforma direttamente in massa",
            "Perché emette onde sonore che il cervello interpreta come immagini luminose",
        ],
        "risposta_corretta": "Perché riflette parte della luce proveniente da una sorgente verso i nostri occhi",
        "spiegazione": (
            "Vediamo un oggetto che non produce luce propria perché riflette o diffonde luce proveniente "
            "da una sorgente, come il Sole o una lampada, verso i nostri occhi."
        ),
    },

    "FIS_026": {
        "opzioni": [
            "Accumula energia potenziale elastica e tende a tornare alla forma iniziale",
            "Perde la capacità di esercitare forza appena viene allungata o compressa",
            "Trasforma la deformazione in massa aggiuntiva permanente del materiale",
            "Aumenta la propria temperatura senza poter restituire energia meccanica",
        ],
        "risposta_corretta": "Accumula energia potenziale elastica e tende a tornare alla forma iniziale",
        "spiegazione": (
            "Entro il limite elastico, una molla deformata accumula energia potenziale elastica "
            "e tende a tornare alla forma iniziale quando la forza deformante viene rimossa."
        ),
    },

    "FIS_028": {
        "opzioni": [
            "Quando la risultante delle forze e la risultante dei momenti sono nulle",
            "Quando la velocità è elevata ma le forze applicate hanno lo stesso verso",
            "Quando agisce una sola forza non bilanciata sul centro di massa",
            "Quando il corpo ruota rapidamente ma non cambia la propria posizione",
        ],
        "risposta_corretta": "Quando la risultante delle forze e la risultante dei momenti sono nulle",
        "spiegazione": (
            "Un corpo è in equilibrio statico quando non trasla e non ruota. "
            "Per questo la risultante delle forze e la risultante dei momenti devono essere nulle."
        ),
    },

    "FIS_029": {
        "opzioni": [
            "Perché il suono ha bisogno di un mezzo materiale che trasmetta le vibrazioni",
            "Perché nel vuoto il suono si trasforma in luce elettromagnetica visibile",
            "Perché nel vuoto le onde sonore aumentano frequenza fino a diventare radioonde",
            "Perché il vuoto assorbe le vibrazioni rendendole più veloci della luce",
        ],
        "risposta_corretta": "Perché il suono ha bisogno di un mezzo materiale che trasmetta le vibrazioni",
        "spiegazione": (
            "Il suono è un’onda meccanica: per propagarsi ha bisogno di particelle materiali "
            "che trasmettano la vibrazione. Nel vuoto non c’è un mezzo materiale sufficiente."
        ),
    },

    "FIS_031": {
        "opzioni": [
            "La corrente diminuisce perché, a tensione costante, è inversamente proporzionale alla resistenza",
            "La corrente aumenta perché una resistenza maggiore spinge più cariche nel circuito",
            "La corrente resta invariata perché dipende solo dalla lunghezza dei fili",
            "La corrente si annulla solo se la tensione aumenta insieme alla resistenza",
        ],
        "risposta_corretta": "La corrente diminuisce perché, a tensione costante, è inversamente proporzionale alla resistenza",
        "spiegazione": (
            "Secondo la legge di Ohm, I = V / R. Se la tensione resta costante e la resistenza aumenta, "
            "la corrente diminuisce."
        ),
    },
}


def carica_database(percorso):
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati, None, dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "quiz", "items", "data", "database"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave], chiave, dati

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/fisica.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto fisico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio fisico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not FISICA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {FISICA_JSON}")

    shutil.copy2(FISICA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(FISICA_JSON)

    domande_per_id = {
        str(domanda.get("id", "")): domanda
        for domanda in domande
        if isinstance(domanda, dict)
    }

    mancanti = [
        id_domanda
        for id_domanda in REVISIONI
        if id_domanda not in domande_per_id
    ]

    if mancanti:
        raise SystemExit(f"ERRORE: mancano queste domande nel JSON: {mancanti}")

    for id_domanda, revisione in REVISIONI.items():
        domanda = domande_per_id[id_domanda]
        domanda["opzioni"] = revisione["opzioni"]
        domanda["risposta_corretta"] = revisione["risposta_corretta"]
        domanda["spiegazione"] = revisione["spiegazione"]
        aggiorna_spiegazioni_opzioni(domanda, revisione)

    if chiave_lista is None:
        nuovo_database = domande
    else:
        dati_originali[chiave_lista] = domande
        nuovo_database = dati_originali

    FISICA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE FISICA BATCH 2 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica.json aggiornato.")


if __name__ == "__main__":
    main()
