import json
import re
from pathlib import Path


JSON_FILE = Path("data/logica/logica_visiva.json")
REPORT_FILE = Path("dist/report_logica_visiva_strict.md")


PAROLE_CHE_RIVELANO_REGOLA = {
    "forma esterna": "La domanda anticipa che bisogna guardare la forma esterna.",
    "colore": "La domanda anticipa che bisogna guardare il colore.",
    "linee interne": "La domanda anticipa che bisogna guardare le linee interne.",
    "numero di": "La domanda anticipa che bisogna contare elementi.",
    "punti interni": "La domanda anticipa che bisogna contare i punti interni.",
    "aumenta": "La domanda anticipa una crescita progressiva.",
    "aumentano": "La domanda anticipa una crescita progressiva.",
    "alterna": "La domanda anticipa un'alternanza.",
    "alternanza": "La domanda anticipa un'alternanza.",
    "rotazione": "La domanda anticipa che bisogna osservare una rotazione.",
    "ruota": "La domanda anticipa che bisogna osservare una rotazione.",
    "speculare": "La domanda anticipa che bisogna osservare uno specchio/ribaltamento.",
    "ribaltamento": "La domanda anticipa che bisogna osservare uno specchio/ribaltamento.",
    "diagonale": "La domanda anticipa che bisogna guardare una diagonale.",
    "righe determinano": "La domanda anticipa la regola delle righe.",
    "colonne determinano": "La domanda anticipa la regola delle colonne.",
}


PAROLE_ATTESE_NELLA_SPIEGAZIONE = [
    "forma",
    "colore",
    "linee",
    "punti",
    "numero",
    "altern",
    "rotaz",
    "specular",
    "ribalt",
    "riga",
    "colonna",
    "sequenza",
    "matrice",
]


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "items", "data"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave]

    raise ValueError("Non riesco a trovare la lista delle domande.")


def normalizza_testo(testo):
    return str(testo or "").lower().strip()


def contiene_parola_o_frase(testo, parola):
    """
    Cerca una parola o una frase intera.

    Esempio:
    - deve trovare: alterna
    - non deve trovare: alternativa
    """
    pattern = (
        r"(?<![a-zàèéìòù])"
        + re.escape(parola)
        + r"(?![a-zàèéìòù])"
    )

    return re.search(pattern, testo) is not None


def percorso_esiste(percorso_asset):
    if not percorso_asset:
        return False

    return Path(percorso_asset).exists()


def ottieni_domande_logica_visiva():
    dati = carica_json(JSON_FILE)
    domande = trova_lista_domande(dati)

    return [
        domanda
        for domanda in domande
        if domanda.get("sottocategoria") == "logica_visiva"
        or str(domanda.get("id", "")).startswith("LOG-VIS")
    ]


def controlla_domanda(domanda):
    problemi_rossi = []
    problemi_gialli = []

    id_domanda = domanda.get("id", "ID_MANCANTE")
    testo_domanda = normalizza_testo(domanda.get("domanda"))
    spiegazione = normalizza_testo(domanda.get("spiegazione"))
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta")
    immagini_opzioni = domanda.get("immagini_opzioni", {})
    immagine_domanda = domanda.get("immagine_domanda")
    distrattore_forte = domanda.get("distrattore_forte")
    motivo_distrattore = normalizza_testo(domanda.get("motivo_distrattore_forte"))

    if not testo_domanda:
        problemi_rossi.append("La domanda è vuota.")

    for parola, messaggio in PAROLE_CHE_RIVELANO_REGOLA.items():
        if contiene_parola_o_frase(testo_domanda, parola):
            problemi_rossi.append(messaggio)

    if len(testo_domanda) > 140:
        problemi_gialli.append(
            "La domanda è lunga: nelle domande visive conviene essere più neutri e brevi."
        )

    if not immagine_domanda:
        problemi_rossi.append("Manca il campo immagine_domanda.")
    elif not percorso_esiste(immagine_domanda):
        problemi_rossi.append(f"Il file immagine_domanda non esiste: {immagine_domanda}")

    if not isinstance(opzioni, list) or sorted(opzioni) != ["A", "B", "C", "D"]:
        problemi_rossi.append(
            "Le opzioni visive devono essere esattamente ['A', 'B', 'C', 'D']."
        )

    if risposta_corretta not in ["A", "B", "C", "D"]:
        problemi_rossi.append("La risposta corretta deve essere una lettera tra A, B, C, D.")

    percorsi_opzioni = {}

    if isinstance(immagini_opzioni, dict):
        percorsi_opzioni = {
            "A": immagini_opzioni.get("A"),
            "B": immagini_opzioni.get("B"),
            "C": immagini_opzioni.get("C"),
            "D": immagini_opzioni.get("D"),
        }
    elif isinstance(immagini_opzioni, list):
        if len(immagini_opzioni) == 4:
            percorsi_opzioni = {
                "A": immagini_opzioni[0],
                "B": immagini_opzioni[1],
                "C": immagini_opzioni[2],
                "D": immagini_opzioni[3],
            }
        else:
            problemi_rossi.append(
                "immagini_opzioni deve contenere esattamente 4 immagini."
            )
    else:
        problemi_rossi.append(
            "immagini_opzioni deve essere una lista oppure un dizionario A, B, C, D."
        )

    for lettera in ["A", "B", "C", "D"]:
        percorso = percorsi_opzioni.get(lettera)

        if not percorso:
            problemi_rossi.append(f"Manca l'immagine dell'opzione {lettera}.")
        elif not percorso_esiste(percorso):
            problemi_rossi.append(f"L'immagine dell'opzione {lettera} non esiste: {percorso}")

    if risposta_corretta in ["A", "B", "C", "D"]:
        if not percorsi_opzioni.get(risposta_corretta):
            problemi_rossi.append(
                "La risposta corretta non ha un'immagine associata."
            )

    if distrattore_forte not in ["A", "B", "C", "D"]:
        problemi_rossi.append("Il distrattore forte deve essere una lettera tra A, B, C, D.")
    elif distrattore_forte == risposta_corretta:
        problemi_rossi.append("Il distrattore forte non può coincidere con la risposta corretta.")

    if len(motivo_distrattore) < 25:
        problemi_gialli.append("Il motivo del distrattore forte è troppo breve o poco chiaro.")

    if "sbaglia" not in motivo_distrattore and "ma" not in motivo_distrattore:
        problemi_gialli.append(
            "Il motivo del distrattore forte dovrebbe spiegare quale dettaglio è vicino ma sbagliato."
        )

    if len(spiegazione) < 50:
        problemi_rossi.append("La spiegazione è troppo breve per una domanda visiva.")

    if not any(parola in spiegazione for parola in PAROLE_ATTESE_NELLA_SPIEGAZIONE):
        problemi_gialli.append(
            "La spiegazione non descrive chiaramente la regola visiva usata."
        )

    return {
        "id": id_domanda,
        "domanda": domanda.get("domanda", ""),
        "risposta_corretta": risposta_corretta,
        "distrattore_forte": distrattore_forte,
        "rossi": problemi_rossi,
        "gialli": problemi_gialli,
    }


def crea_report(risultati):
    righe = []

    totale = len(risultati)
    rossi = [r for r in risultati if r["rossi"]]
    gialli = [r for r in risultati if not r["rossi"] and r["gialli"]]
    ok = [r for r in risultati if not r["rossi"] and not r["gialli"]]

    righe.append("# Report controllo severo logica visiva")
    righe.append("")
    righe.append("## Riepilogo")
    righe.append("")
    righe.append(f"Domande logica visiva controllate: {totale}")
    righe.append(f"ROSSO - da correggere: {len(rossi)}")
    righe.append(f"GIALLO - da migliorare: {len(gialli)}")
    righe.append(f"OK: {len(ok)}")
    righe.append("")

    if rossi:
        righe.append("---")
        righe.append("")
        righe.append("## ROSSO - da correggere")
        righe.append("")

        for risultato in rossi:
            righe.append(f"### {risultato['id']}")
            righe.append("")
            righe.append(f"**Domanda:** {risultato['domanda']}")
            righe.append("")
            righe.append(f"**Risposta corretta:** {risultato['risposta_corretta']}")
            righe.append("")
            righe.append("**Problemi:**")
            for problema in risultato["rossi"]:
                righe.append(f"- {problema}")
            righe.append("")

    if gialli:
        righe.append("---")
        righe.append("")
        righe.append("## GIALLO - da migliorare")
        righe.append("")

        for risultato in gialli:
            righe.append(f"### {risultato['id']}")
            righe.append("")
            righe.append(f"**Domanda:** {risultato['domanda']}")
            righe.append("")
            righe.append("**Avvisi:**")
            for problema in risultato["gialli"]:
                righe.append(f"- {problema}")
            righe.append("")

    return "\n".join(righe)


def main():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    domande = ottieni_domande_logica_visiva()
    risultati = [controlla_domanda(domanda) for domanda in domande]

    report = crea_report(risultati)
    REPORT_FILE.write_text(report, encoding="utf-8")

    rossi = [r for r in risultati if r["rossi"]]
    gialli = [r for r in risultati if not r["rossi"] and r["gialli"]]
    ok = [r for r in risultati if not r["rossi"] and not r["gialli"]]

    print("----- CONTROLLO SEVERO LOGICA VISIVA -----")
    print("Domande controllate:", len(risultati))
    print("ROSSO - da correggere:", len(rossi))
    print("GIALLO - da migliorare:", len(gialli))
    print("OK:", len(ok))
    print("Report creato:", REPORT_FILE)

    if rossi:
        print("")
        print("Prime domande da correggere:")
        for risultato in rossi[:10]:
            print("-", risultato["id"])


main()
