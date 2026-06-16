from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FISICA_JSON = ROOT / "data" / "fisica.json"
BACKUP_TMP = Path("/tmp/fisica_prima_revisione_batch1.json")

REVISIONI = {
    "FIS_002": {
        "opzioni": [
            "Il corpo subisce un’accelerazione, cambiando velocità o direzione del moto",
            "Il corpo mantiene lo stesso moto perché la forza risultante non modifica la velocità",
            "Il corpo perde massa e per questo rallenta anche senza cambiare accelerazione",
            "Il corpo annulla la forza applicata e resta nello stato precedente di moto",
        ],
        "risposta_corretta": "Il corpo subisce un’accelerazione, cambiando velocità o direzione del moto",
        "spiegazione": (
            "Secondo la seconda legge di Newton, una forza risultante non nulla produce un’accelerazione. "
            "Questo significa che il corpo può cambiare velocità, direzione o entrambe."
        ),
    },

    "FIS_008": {
        "opzioni": [
            "La pressione aumenta perché la stessa forza è distribuita su un’area minore",
            "La pressione diminuisce perché la forza si concentra su una superficie più piccola",
            "La pressione resta invariata perché dipende solo dalla massa dell’oggetto",
            "La pressione cambia solo se cambia il materiale della superficie di appoggio",
        ],
        "risposta_corretta": "La pressione aumenta perché la stessa forza è distribuita su un’area minore",
        "spiegazione": (
            "La pressione è il rapporto tra forza e superficie. Se la forza resta la stessa "
            "ma l’area diminuisce, la pressione aumenta."
        ),
    },

    "FIS_010": {
        "opzioni": [
            "L’energia meccanica totale resta costante se non agiscono forze dissipative",
            "L’energia cinetica resta costante anche quando cambia l’energia potenziale",
            "L’energia potenziale aumenta mentre quella cinetica scompare dal sistema",
            "L’energia meccanica cresce a ogni trasformazione anche senza lavoro esterno",
        ],
        "risposta_corretta": "L’energia meccanica totale resta costante se non agiscono forze dissipative",
        "spiegazione": (
            "In assenza di attriti o altre forze dissipative, la somma tra energia cinetica "
            "ed energia potenziale resta costante. Le due forme possono trasformarsi l’una nell’altra."
        ),
    },

    "FIS_012": {
        "opzioni": [
            "La lunghezza d’onda diminuisce se la velocità di propagazione resta costante",
            "La lunghezza d’onda aumenta perché frequenza e lunghezza d’onda crescono insieme",
            "La lunghezza d’onda resta invariata perché dipende solo dall’ampiezza dell’onda",
            "La lunghezza d’onda diventa indipendente dalla frequenza nel mezzo di propagazione",
        ],
        "risposta_corretta": "La lunghezza d’onda diminuisce se la velocità di propagazione resta costante",
        "spiegazione": (
            "Per un’onda vale la relazione velocità = frequenza × lunghezza d’onda. "
            "Se la velocità resta costante e la frequenza aumenta, la lunghezza d’onda diminuisce."
        ),
    },

    "FIS_015": {
        "opzioni": [
            "Si oppone al moto relativo o alla tendenza al moto tra le superfici",
            "Aumenta il moto relativo perché agisce nella stessa direzione dello spostamento",
            "Elimina il peso del corpo quando le superfici sono a contatto",
            "Trasforma la superficie di contatto in una sorgente di forza gravitazionale",
        ],
        "risposta_corretta": "Si oppone al moto relativo o alla tendenza al moto tra le superfici",
        "spiegazione": (
            "La forza di attrito agisce tra superfici a contatto e si oppone al moto relativo "
            "o alla tendenza al moto tra esse."
        ),
    },

    "FIS_017": {
        "opzioni": [
            "Perché la pressione del fluido è maggiore in basso che in alto",
            "Perché il fluido annulla la massa del corpo quando questo viene immerso",
            "Perché il corpo immerso crea una forza di gravità opposta a quella terrestre",
            "Perché la densità del fluido diventa uguale a quella del corpo immerso",
        ],
        "risposta_corretta": "Perché la pressione del fluido è maggiore in basso che in alto",
        "spiegazione": (
            "Un corpo immerso riceve una spinta verso l’alto perché la pressione del fluido "
            "aumenta con la profondità. La pressione sulla parte inferiore è maggiore di quella sulla parte superiore."
        ),
    },

    "FIS_018": {
        "opzioni": [
            "Le particelle vibrano di più e il solido tende a dilatarsi",
            "Le particelle rallentano e il solido tende a contrarsi per il calore assorbito",
            "Le particelle perdono massa e il solido cambia elemento chimico",
            "Le particelle si fermano e il solido diventa più rigido per l’aumento di temperatura",
        ],
        "risposta_corretta": "Le particelle vibrano di più e il solido tende a dilatarsi",
        "spiegazione": (
            "Quando un solido viene riscaldato, le sue particelle aumentano l’agitazione termica. "
            "In genere questo porta a una dilatazione del materiale."
        ),
    },

    "FIS_019": {
        "opzioni": [
            "La resistenza equivalente è la somma delle singole resistenze",
            "La resistenza equivalente è minore della più piccola resistenza del circuito",
            "La resistenza equivalente coincide con la media delle resistenze presenti",
            "La resistenza equivalente dipende solo dalla tensione del generatore",
        ],
        "risposta_corretta": "La resistenza equivalente è la somma delle singole resistenze",
        "spiegazione": (
            "In un circuito con resistenze in serie, la corrente attraversa una resistenza dopo l’altra. "
            "La resistenza equivalente è quindi uguale alla somma delle resistenze."
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

    print("----- REVISIONE FISICA BATCH 1 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica.json aggiornato.")


if __name__ == "__main__":
    main()
