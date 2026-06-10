import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# Modello locale Ollama da usare come revisore linguistico.
MODELLO_AI = "gemma4:12b"


# Endpoint locale di Ollama.
OLLAMA_URL = "http://localhost:11434/api/generate"


# Cartella dove si trovano i JSON delle domande.
CARTELLA_DOMANDE = Path("data")


# File report finale.
FILE_REPORT = Path("dist/text_quality_ai_report.md")


def trova_file_json():
    # Cerca tutti i file JSON dentro data e sottocartelle.
    file_json = list(CARTELLA_DOMANDE.rglob("*.json"))

    return file_json


def carica_domande_da_file(percorso_file):
    # Legge un file JSON e restituisce la lista delle domande.
    with open(percorso_file, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def crea_testo_da_revisionare(domanda):
    # Prepara il testo della domanda da far controllare a Gemma.
    id_domanda = domanda.get("id", "ID_MANCANTE")
    categoria = domanda.get("categoria", "")
    sottocategoria = domanda.get("sottocategoria", "")
    livello = domanda.get("livello", "")
    testo_domanda = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")
    spiegazione = domanda.get("spiegazione", "")

    righe_opzioni = []

    for indice, opzione in enumerate(opzioni, start=1):
        righe_opzioni.append(f"{indice}. {opzione}")

    testo_opzioni = "\n".join(righe_opzioni)

    testo = f"""
ID domanda: {id_domanda}
Categoria: {categoria}
Sottocategoria: {sottocategoria}
Livello: {livello}

Domanda:
{testo_domanda}

Opzioni:
{testo_opzioni}

Risposta corretta:
{risposta_corretta}

Spiegazione:
{spiegazione}
"""

    return testo.strip()


def crea_prompt_revisione(domanda):
    # Crea il prompt per il revisore AI.
    testo_da_revisionare = crea_testo_da_revisionare(domanda)

    prompt = f"""
Sei un revisore linguistico per un database di quiz.

Devi controllare SOLO:
- grammatica
- costruzione della frase
- punteggiatura
- accenti
- chiarezza della spiegazione
- naturalezza delle opzioni di risposta

Non devi cambiare il significato tecnico della domanda.
Non devi inventare nuove domande.
Non devi allungare inutilmente.
Se il testo va bene, dillo chiaramente.

Se la categoria è "inglese", controlla anche se la frase inglese è grammaticalmente corretta.

Rispondi sempre con questo formato:

ESITO: OK oppure DA RIVEDERE

PROBLEMI:
- elenco breve dei problemi trovati, oppure "Nessun problema evidente"

SUGGERIMENTI:
- eventuali correzioni consigliate, oppure "Nessuna correzione necessaria"

TESTO DA CONTROLLARE:
{testo_da_revisionare}
"""

    return prompt.strip()


def chiedi_a_ollama(prompt):
    # Invia il prompt a Ollama usando l'API locale.
    dati = {
        "model": MODELLO_AI,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    dati_json = json.dumps(dati).encode("utf-8")

    richiesta = urllib.request.Request(
        OLLAMA_URL,
        data=dati_json,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(richiesta, timeout=180) as risposta:
            contenuto = risposta.read().decode("utf-8")
            dati_risposta = json.loads(contenuto)

            return dati_risposta.get("response", "").strip()

    except urllib.error.URLError as errore:
        return f"ERRORE OLLAMA: {errore}"

    except TimeoutError:
        return "ERRORE OLLAMA: tempo massimo superato"


def carica_tutte_le_domande():
    # Carica tutte le domande da tutti i file JSON.
    tutte_le_domande = []

    file_json = trova_file_json()

    for percorso_file in file_json:
        domande_del_file = carica_domande_da_file(percorso_file)

        for domanda in domande_del_file:
            domanda_con_file = dict(domanda)
            domanda_con_file["_file_origine"] = str(percorso_file)

            tutte_le_domande.append(domanda_con_file)

    return tutte_le_domande


def salva_report(risultati):
    # Salva il report finale in Markdown.
    FILE_REPORT.parent.mkdir(exist_ok=True)

    with open(FILE_REPORT, "w", encoding="utf-8") as file:
        file.write("# Report controllo qualità testi con Gemma 4 12B\n\n")
        file.write(f"Data controllo: {datetime.now()}\n\n")
        file.write(f"Modello usato: `{MODELLO_AI}`\n\n")
        file.write(f"Domande controllate: {len(risultati)}\n\n")
        file.write("---\n\n")

        for risultato in risultati:
            file.write(f"## {risultato['id_domanda']}\n\n")
            file.write(f"File: `{risultato['file_origine']}`\n\n")
            file.write("### Risultato revisione\n\n")
            file.write(risultato["risposta_ai"])
            file.write("\n\n---\n\n")


def main():
    print("----- CONTROLLO QUALITÀ TESTI CON GEMMA 4 12B -----")
    print(f"Modello usato: {MODELLO_AI}")

    tutte_le_domande = carica_tutte_le_domande()

    print(f"Domande trovate: {len(tutte_le_domande)}")
    print("Avvio revisione AI...\n")

    risultati = []

    for numero, domanda in enumerate(tutte_le_domande, start=1):
        id_domanda = domanda.get("id", "ID_MANCANTE")
        file_origine = domanda.get("_file_origine", "FILE_SCONOSCIUTO")

        print(f"[{numero}/{len(tutte_le_domande)}] Controllo: {id_domanda}")

        prompt = crea_prompt_revisione(domanda)
        risposta_ai = chiedi_a_ollama(prompt)

        risultati.append(
            {
                "id_domanda": id_domanda,
                "file_origine": file_origine,
                "risposta_ai": risposta_ai,
            }
        )

    salva_report(risultati)

    print("\n----- RISULTATO FINALE -----")
    print(f"Report creato in: {FILE_REPORT}")
    print("Controllo AI completato.")


main()