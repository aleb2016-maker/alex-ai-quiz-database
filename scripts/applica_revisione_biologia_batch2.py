from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

BIOLOGIA_JSON = ROOT / "data" / "biologia.json"
BACKUP_TMP = Path("/tmp/biologia_prima_revisione_batch2.json")

REVISIONI = {
    "BIO_017": {
        "opzioni": [
            "Abbassano l’energia di attivazione e rendono più rapide le reazioni biologiche",
            "Aumentano l’energia di attivazione per bloccare reazioni non necessarie",
            "Forniscono direttamente tutta l’energia consumata durante ogni reazione cellulare",
            "Trasformano i prodotti finali in nuovi geni da usare nella sintesi proteica",
        ],
        "risposta_corretta": "Abbassano l’energia di attivazione e rendono più rapide le reazioni biologiche",
        "spiegazione": (
            "Gli enzimi sono catalizzatori biologici: abbassano l’energia di attivazione "
            "e rendono più rapide molte reazioni cellulari senza essere consumati nel processo."
        ),
    },

    "BIO_018": {
        "opzioni": [
            "La mitosi produce cellule somatiche simili, la meiosi produce gameti geneticamente variabili",
            "La mitosi produce gameti aploidi, la meiosi produce cellule somatiche diploidi identiche",
            "La mitosi separa cromosomi omologhi, la meiosi copia solo il DNA senza divisione cellulare",
            "La mitosi riduce il numero cromosomico, la meiosi lo conserva nelle cellule dei tessuti",
        ],
        "risposta_corretta": "La mitosi produce cellule somatiche simili, la meiosi produce gameti geneticamente variabili",
        "spiegazione": (
            "La mitosi serve alla crescita e al rinnovamento dei tessuti e produce cellule molto simili. "
            "La meiosi produce gameti, dimezza il numero cromosomico e aumenta la variabilità genetica."
        ),
    },

    "BIO_019": {
        "opzioni": [
            "Una sequenza di DNA viene copiata in una molecola di RNA complementare",
            "Una molecola di RNA viene tradotta direttamente in una nuova sequenza di DNA",
            "Una proteina viene copiata in RNA usando ribosomi come stampo principale",
            "Il DNA viene duplicato integralmente per preparare la divisione cellulare",
        ],
        "risposta_corretta": "Una sequenza di DNA viene copiata in una molecola di RNA complementare",
        "spiegazione": (
            "Durante la trascrizione, l’informazione contenuta in un tratto di DNA viene copiata "
            "in una molecola di RNA. La traduzione, invece, usa l’RNA per sintetizzare proteine."
        ),
    },

    "BIO_020": {
        "opzioni": [
            "Trasportano ossigeno grazie all’emoglobina presente al loro interno",
            "Producono anticorpi specifici contro virus e batteri nel plasma sanguigno",
            "Coagulano il sangue formando reti di fibrina nelle ferite aperte",
            "Distruggono cellule infette riconoscendo antigeni sulla loro membrana",
        ],
        "risposta_corretta": "Trasportano ossigeno grazie all’emoglobina presente al loro interno",
        "spiegazione": (
            "I globuli rossi sono fondamentali perché contengono emoglobina, una proteina capace "
            "di legare e trasportare ossigeno dai polmoni ai tessuti."
        ),
    },

    "BIO_022": {
        "opzioni": [
            "Può cadere in una regione non codificante o non cambiare la funzione della proteina",
            "Produce necessariamente una nuova proteina visibile in ogni cellula dell’organismo",
            "Elimina l’intero cromosoma interessato rendendo ogni effetto subito osservabile",
            "Impedisce in ogni caso la trascrizione di tutti i geni collegati a quel carattere",
        ],
        "risposta_corretta": "Può cadere in una regione non codificante o non cambiare la funzione della proteina",
        "spiegazione": (
            "Una mutazione non produce necessariamente un effetto visibile: può trovarsi in regioni "
            "non codificanti oppure non modificare in modo rilevante la proteina prodotta."
        ),
    },

    "BIO_023": {
        "opzioni": [
            "Un organismo consuma un altro organismo come fonte di energia e materia",
            "Due organismi ricavano beneficio reciproco senza perdita per nessuno dei due",
            "Un organismo vive su un altro ottenendo risorse e danneggiandolo gradualmente",
            "Due organismi competono per la stessa risorsa limitata nello stesso ambiente",
        ],
        "risposta_corretta": "Un organismo consuma un altro organismo come fonte di energia e materia",
        "spiegazione": (
            "La predazione è una relazione ecologica in cui un organismo, il predatore, "
            "si nutre di un altro organismo, la preda."
        ),
    },

    "BIO_024": {
        "opzioni": [
            "Aumenta la varietà di specie e funzioni, rendendo l’ecosistema più resistente ai cambiamenti",
            "Riduce il numero di relazioni ecologiche e rende più semplice ogni catena alimentare",
            "Concentra tutta l’energia in una sola specie dominante più adatta alle perturbazioni",
            "Elimina la competizione tra organismi usando una sola risorsa principale condivisa",
        ],
        "risposta_corretta": "Aumenta la varietà di specie e funzioni, rendendo l’ecosistema più resistente ai cambiamenti",
        "spiegazione": (
            "Un ecosistema con maggiore biodiversità contiene più specie e ruoli ecologici. "
            "Questa varietà può renderlo più stabile e più capace di reagire a cambiamenti o disturbi."
        ),
    },

    "BIO_031": {
        "opzioni": [
            "A ogni passaggio trofico molta energia viene dispersa come calore o usata nel metabolismo",
            "A ogni passaggio trofico tutta la biomassa viene trasferita integralmente al livello superiore",
            "I produttori consumano più energia dei predatori e lasciano poca materia ai consumatori",
            "I livelli superiori accumulano solo acqua, mentre la biomassa resta nei decompositori",
        ],
        "risposta_corretta": "A ogni passaggio trofico molta energia viene dispersa come calore o usata nel metabolismo",
        "spiegazione": (
            "Nelle piramidi alimentari solo una parte dell’energia passa al livello trofico successivo. "
            "Molto viene usato nel metabolismo o disperso come calore, quindi ai livelli superiori resta meno biomassa."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/biologia.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: risponde in modo preciso al concetto biologico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio biologico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not BIOLOGIA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {BIOLOGIA_JSON}")

    shutil.copy2(BIOLOGIA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(BIOLOGIA_JSON)

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

    BIOLOGIA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE BIOLOGIA BATCH 2 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/biologia.json aggiornato.")


if __name__ == "__main__":
    main()
