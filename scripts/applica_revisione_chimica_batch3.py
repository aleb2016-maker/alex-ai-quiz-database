from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

CHIMICA_JSON = ROOT / "data" / "chimica.json"
BACKUP_TMP = Path("/tmp/chimica_prima_revisione_batch3.json")

REVISIONI = {
    "CHE_032": {
        "opzioni": [
            "Il prodotto tra le concentrazioni di H⁺ e OH⁻ a una data temperatura",
            "La somma tra le concentrazioni di H⁺ e OH⁻ presenti nella soluzione",
            "Il rapporto tra la concentrazione di H⁺ e quella di OH⁻ in acqua",
            "La quantità totale di molecole d’acqua dissociate in un litro di soluzione",
        ],
        "risposta_corretta": "Il prodotto tra le concentrazioni di H⁺ e OH⁻ a una data temperatura",
        "spiegazione": (
            "Il prodotto ionico dell’acqua indica il prodotto tra le concentrazioni di ioni H⁺ e OH⁻. "
            "A temperatura costante questo valore resta caratteristico dell’acqua."
        ),
    },

    "CHE_033": {
        "opzioni": [
            "Molecole con energia sufficiente passano dalla superficie del liquido al vapore",
            "Molecole con energia minore si legano più stabilmente formando un solido",
            "Le particelle del liquido perdono carica elettrica e diventano atomi isolati",
            "Le molecole del liquido si trasformano chimicamente in nuovi composti gassosi",
        ],
        "risposta_corretta": "Molecole con energia sufficiente passano dalla superficie del liquido al vapore",
        "spiegazione": (
            "Durante l’evaporazione, alcune molecole alla superficie del liquido hanno energia sufficiente "
            "per vincere le attrazioni intermolecolari e passare allo stato di vapore."
        ),
    },

    "CHE_034": {
        "opzioni": [
            "Una sostanza formata da elementi diversi uniti chimicamente in proporzioni definite",
            "Una sostanza ottenuta mescolando elementi diversi senza legami chimici stabili",
            "Un materiale composto da particelle separate con composizione variabile",
            "Un insieme di atomi dello stesso elemento non uniti da legami chimici",
        ],
        "risposta_corretta": "Una sostanza formata da elementi diversi uniti chimicamente in proporzioni definite",
        "spiegazione": (
            "Un composto chimico è formato da atomi di elementi diversi legati chimicamente "
            "in proporzioni definite. Una miscela, invece, può avere composizione variabile."
        ),
    },

    "CHE_035": {
        "opzioni": [
            "Perché assume forme chimiche diverse in ambiente acido o basico, con colori diversi",
            "Perché misura direttamente la massa degli ioni presenti nella soluzione",
            "Perché trasforma l’acido in base e la base in acido durante la reazione",
            "Perché precipita in modo diverso quando aumenta la quantità di solvente",
        ],
        "risposta_corretta": "Perché assume forme chimiche diverse in ambiente acido o basico, con colori diversi",
        "spiegazione": (
            "Un indicatore acido-base cambia colore perché può trovarsi in forme chimiche diverse "
            "a seconda del pH. Queste forme assorbono la luce in modo diverso e quindi mostrano colori diversi."
        ),
    },

    "CHE_036": {
        "opzioni": [
            "Aumenta la frequenza degli urti efficaci tra le particelle reagenti",
            "Riduce il numero di particelle disponibili per reagire nello stesso volume",
            "Aumenta la massa degli atomi senza modificare gli urti tra particelle",
            "Blocca il movimento delle particelle rendendo più stabile ogni reagente",
        ],
        "risposta_corretta": "Aumenta la frequenza degli urti efficaci tra le particelle reagenti",
        "spiegazione": (
            "Se aumenta la concentrazione dei reagenti, ci sono più particelle nello stesso volume. "
            "Questo rende più frequenti gli urti efficaci e può aumentare la velocità della reazione."
        ),
    },

    "CHE_038": {
        "opzioni": [
            "Si sposta nella direzione che tende a contrastare la perturbazione subita",
            "Si sposta nella direzione che amplifica la perturbazione fino a consumare i reagenti",
            "Interrompe la reazione diretta e lascia procedere solo quella inversa",
            "Mantiene invariate le concentrazioni ignorando variazioni di pressione o temperatura",
        ],
        "risposta_corretta": "Si sposta nella direzione che tende a contrastare la perturbazione subita",
        "spiegazione": (
            "Secondo il principio di Le Châtelier, un sistema all’equilibrio reagisce a una perturbazione "
            "spostandosi nella direzione che tende a ridurne l’effetto."
        ),
    },

    "CHE_039": {
        "opzioni": [
            "Resiste a variazioni moderate di pH grazie a una coppia acido debole/base coniugata",
            "Trasforma ogni acido forte in acqua pura eliminando tutti gli ioni presenti",
            "Mantiene il pH usando soltanto un sale neutro privo di componenti acide o basiche",
            "Aumenta rapidamente il pH quando viene aggiunta una piccola quantità di acido",
        ],
        "risposta_corretta": "Resiste a variazioni moderate di pH grazie a una coppia acido debole/base coniugata",
        "spiegazione": (
            "Una soluzione tampone resiste a variazioni moderate di pH perché contiene una coppia "
            "acido debole/base coniugata, capace di assorbire piccole aggiunte di acido o base."
        ),
    },

    "CHE_040": {
        "opzioni": [
            "Per individuare il punto finale tramite un cambiamento di colore vicino all’equivalenza",
            "Per aumentare la concentrazione dell’acido fino a rendere la reazione più rapida",
            "Per trasformare direttamente la base in sale prima dell’aggiunta del titolante",
            "Per misurare la massa del solvente senza seguire il cambiamento di pH",
        ],
        "risposta_corretta": "Per individuare il punto finale tramite un cambiamento di colore vicino all’equivalenza",
        "spiegazione": (
            "In una titolazione acido-base si usa spesso un indicatore perché cambia colore vicino "
            "al punto finale, aiutando a capire quando la neutralizzazione è praticamente completata."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/chimica.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto chimico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio chimico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not CHIMICA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {CHIMICA_JSON}")

    shutil.copy2(CHIMICA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(CHIMICA_JSON)

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

    CHIMICA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE CHIMICA BATCH 3 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/chimica.json aggiornato.")


if __name__ == "__main__":
    main()
