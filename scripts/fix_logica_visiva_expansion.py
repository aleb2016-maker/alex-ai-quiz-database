import json
from pathlib import Path


LOGICA_VISIVA_FILE = Path("data/logica/logica_visiva.json")
EXPANSION_SCRIPT = Path("scripts/expand_logica_visiva_levels.py")


LIVELLO_TO_DIFFICOLTA = {
    "facile": 1,
    "intermedio": 2,
    "avanzato": 3,
}


DOMANDE_RISCRITTE = {
    "LOG-VIS-FAC-0004": (
        "Guarda la serie alternata di forme e colori. "
        "Quale simbolo deve apparire nella casella vuota?"
    ),
    "LOG-VIS-INT-0004": (
        "La figura esterna cresce e gli elementi interni aumentano. "
        "Quale opzione continua correttamente la progressione?"
    ),
    "LOG-VIS-AV-0004": (
        "Nella griglia cambiano insieme forma esterna, colore e linee interne. "
        "Quale casella completa lo schema?"
    ),
    "LOG-VIS-AV-0008": (
        "Completa la griglia ciclica osservando forma, colore e barre diagonali."
    ),
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "items", "data"]:
            valore = dati.get(chiave)

            if isinstance(valore, list):
                return valore

    raise ValueError("Non riesco a trovare la lista delle domande.")


def crea_tags(domanda):
    livello = domanda.get("livello", "livello_mancante")
    tipo = domanda.get("tipo", "visiva")
    sottocategoria = domanda.get("sottocategoria", "logica_visiva")

    tags = [
        "logica",
        "logica_visiva",
        "visuale",
        livello,
        tipo,
        sottocategoria,
    ]

    tags_puliti = []

    for tag in tags:
        tag = str(tag).strip()

        if tag and tag not in tags_puliti:
            tags_puliti.append(tag)

    return tags_puliti


def sistema_domanda(domanda):
    id_domanda = domanda.get("id", "")

    if not id_domanda.startswith("LOG-VIS-"):
        return False

    livello = domanda.get("livello", "")

    if livello not in LIVELLO_TO_DIFFICOLTA:
        print("Livello non riconosciuto:", id_domanda, livello)
        return False

    domanda["categoria"] = "logica"
    domanda["sottocategoria"] = "logica_visiva"
    domanda["tipo"] = "visiva"

    domanda["difficolta"] = LIVELLO_TO_DIFFICOLTA[livello]
    domanda["tags"] = crea_tags(domanda)

    if id_domanda in DOMANDE_RISCRITTE:
        domanda["domanda"] = DOMANDE_RISCRITTE[id_domanda]

    if "distrattore_forte" not in domanda:
        domanda["distrattore_forte"] = (
            "Una delle opzioni sbagliate mantiene quasi tutta la regola visiva, "
            "ma cambia un dettaglio importante."
        )

    if "motivo_distrattore_forte" not in domanda:
        domanda["motivo_distrattore_forte"] = (
            "È plausibile perché somiglia alla risposta corretta, ma sbaglia almeno "
            "un elemento tra forma, colore, quantità, orientamento o riempimento."
        )

    return True


def sistema_script_espansione():
    if not EXPANSION_SCRIPT.exists():
        print("Script espansione non trovato:", EXPANSION_SCRIPT)
        return

    testo = EXPANSION_SCRIPT.read_text(encoding="utf-8")

    testo_vecchio = 'BACKUP_FILE = Path("data/logica/logica_visiva.backup.json")'
    testo_nuovo = 'BACKUP_FILE = Path("backups/logica_visiva.backup.json")'

    if testo_vecchio in testo:
        testo = testo.replace(testo_vecchio, testo_nuovo)
        EXPANSION_SCRIPT.write_text(testo, encoding="utf-8")
        print("Aggiornato backup nello script:", EXPANSION_SCRIPT)
    else:
        print("Backup script già corretto oppure riga non trovata.")


def main():
    if not LOGICA_VISIVA_FILE.exists():
        raise FileNotFoundError(f"File non trovato: {LOGICA_VISIVA_FILE}")

    dati = carica_json(LOGICA_VISIVA_FILE)
    lista_domande = trova_lista_domande(dati)

    domande_sistemate = 0

    for domanda in lista_domande:
        if not isinstance(domanda, dict):
            continue

        if sistema_domanda(domanda):
            domande_sistemate += 1

    salva_json(LOGICA_VISIVA_FILE, dati)
    sistema_script_espansione()

    print("")
    print("----- CORREZIONE LOGICA VISIVA COMPLETATA -----")
    print("Domande LOG-VIS sistemate:", domande_sistemate)
    print("File aggiornato:", LOGICA_VISIVA_FILE)
    print("Script espansione aggiornato:", EXPANSION_SCRIPT)


main()