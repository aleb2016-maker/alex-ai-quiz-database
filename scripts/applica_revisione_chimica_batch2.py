from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

CHIMICA_JSON = ROOT / "data" / "chimica.json"
BACKUP_TMP = Path("/tmp/chimica_prima_revisione_batch2.json")

REVISIONI = {
    "CHE_021": {
        "opzioni": [
            "Le velocità della reazione diretta e inversa diventano uguali",
            "La reazione diretta si ferma mentre quella inversa continua da sola",
            "La concentrazione dei prodotti aumenta senza limite nel tempo",
            "I reagenti vengono consumati del tutto e non possono riformarsi",
        ],
        "risposta_corretta": "Le velocità della reazione diretta e inversa diventano uguali",
        "spiegazione": (
            "In un equilibrio chimico dinamico, la reazione diretta e quella inversa continuano ad avvenire, "
            "ma con la stessa velocità. Per questo le concentrazioni macroscopiche restano costanti."
        ),
    },

    "CHE_022": {
        "opzioni": [
            "Il pH diminuisce perché la soluzione diventa più acida",
            "Il pH aumenta perché gli ioni H⁺ rendono la soluzione più basica",
            "Il pH resta invariato perché dipende solo dalla quantità di solvente",
            "Il pH misura soltanto gli ioni OH⁻ e non dipende dagli ioni H⁺",
        ],
        "risposta_corretta": "Il pH diminuisce perché la soluzione diventa più acida",
        "spiegazione": (
            "Il pH è collegato alla concentrazione di ioni H⁺: quando la concentrazione di H⁺ aumenta, "
            "il pH diminuisce e la soluzione diventa più acida."
        ),
    },

    "CHE_023": {
        "opzioni": [
            "La geometria simmetrica può annullare il momento dipolare complessivo",
            "La presenza di legami polari rende la molecola polare indipendentemente dalla forma",
            "La molecola diventa apolare perché i legami polari perdono gli elettroni condivisi",
            "L’apolarità dipende solo dalla massa molecolare e non dalla distribuzione di carica",
        ],
        "risposta_corretta": "La geometria simmetrica può annullare il momento dipolare complessivo",
        "spiegazione": (
            "Una molecola può contenere legami polari ma risultare apolare se la sua geometria è simmetrica "
            "e i dipoli dei legami si compensano tra loro."
        ),
    },

    "CHE_024": {
        "opzioni": [
            "L’energia minima necessaria perché i reagenti possano trasformarsi in prodotti",
            "L’energia totale liberata quando tutti i prodotti sono già formati",
            "L’energia conservata nei prodotti dopo il completamento della reazione",
            "L’energia che misura solo la massa dei reagenti prima dell’urto efficace",
        ],
        "risposta_corretta": "L’energia minima necessaria perché i reagenti possano trasformarsi in prodotti",
        "spiegazione": (
            "L’energia di attivazione è la barriera energetica minima che i reagenti devono superare "
            "per raggiungere lo stato di transizione e trasformarsi in prodotti."
        ),
    },

    "CHE_026": {
        "opzioni": [
            "Il componente che scioglie il soluto ed è spesso presente in quantità maggiore",
            "Il componente disciolto nel liquido e presente in quantità minore rispetto al solvente",
            "La sostanza che precipita dal fondo quando la soluzione diventa omogenea",
            "Il composto che reagisce con ogni soluto trasformandolo in gas",
        ],
        "risposta_corretta": "Il componente che scioglie il soluto ed è spesso presente in quantità maggiore",
        "spiegazione": (
            "Il solvente è il componente della soluzione che scioglie il soluto. "
            "Di solito è presente in quantità maggiore, anche se la definizione dipende dal ruolo nella soluzione."
        ),
    },

    "CHE_027": {
        "opzioni": [
            "Hanno lo stesso numero di elettroni di valenza e reagiscono in modo simile",
            "Hanno lo stesso numero totale di protoni e quindi identica massa atomica",
            "Hanno lo stesso numero di neutroni e formano gli stessi isotopi stabili",
            "Hanno configurazioni interne identiche ma diverso strato elettronico esterno",
        ],
        "risposta_corretta": "Hanno lo stesso numero di elettroni di valenza e reagiscono in modo simile",
        "spiegazione": (
            "Gli elementi dello stesso gruppo della tavola periodica hanno lo stesso numero di elettroni di valenza. "
            "Questo spiega perché presentano proprietà chimiche simili."
        ),
    },

    "CHE_028": {
        "opzioni": [
            "Gli ioni H⁺ dell’acido reagiscono con gli ioni OH⁻ della base formando acqua",
            "Gli ioni H⁺ dell’acido si trasformano direttamente in elettroni liberi",
            "La base aumenta l’acidità della soluzione producendo nuovi ioni H⁺",
            "L’acido e la base scompaiono senza formare nuove specie chimiche",
        ],
        "risposta_corretta": "Gli ioni H⁺ dell’acido reagiscono con gli ioni OH⁻ della base formando acqua",
        "spiegazione": (
            "In una neutralizzazione, un acido e una base reagiscono: gli ioni H⁺ e OH⁻ formano acqua, "
            "mentre gli altri ioni possono formare un sale."
        ),
    },

    "CHE_031": {
        "opzioni": [
            "Un acido forte si ionizza quasi completamente, un acido debole solo parzialmente",
            "Un acido forte ha pH alto, un acido debole ha pH basso alla stessa concentrazione",
            "Un acido forte contiene più atomi, un acido debole contiene meno legami chimici",
            "Un acido forte non produce ioni H⁺, un acido debole li produce in grande quantità",
        ],
        "risposta_corretta": "Un acido forte si ionizza quasi completamente, un acido debole solo parzialmente",
        "spiegazione": (
            "Un acido forte in acqua si ionizza quasi completamente, liberando molti ioni H⁺. "
            "Un acido debole invece si ionizza solo in parte e mantiene un equilibrio tra forma ionizzata e non ionizzata."
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

    print("----- REVISIONE CHIMICA BATCH 2 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/chimica.json aggiornato.")


if __name__ == "__main__":
    main()
