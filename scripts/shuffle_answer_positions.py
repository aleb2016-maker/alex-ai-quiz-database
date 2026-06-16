import json
import random
import shutil
import tempfile
import zipfile
from pathlib import Path
from collections import Counter


OPTION_KEYS = [
    "opzioni",
    "options",
    "risposte",
    "answers",
    "choices",
]

CORRECT_KEYS = [
    "risposta_corretta",
    "correct_answer",
    "correctAnswer",
    "correct",
    "answer",
    "soluzione",
    "opzione_corretta",
    "correct_option",
    "correctOption",
    "indice_risposta_corretta",
    "correct_index",
    "correctIndex",
]

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["questions", "domande", "quiz", "items", "data"]:
            valore = dati.get(chiave)
            if isinstance(valore, list):
                return valore

    return []


def trova_chiave_opzioni(domanda):
    for chiave in OPTION_KEYS:
        valore = domanda.get(chiave)
        if isinstance(valore, list) and len(valore) >= 2:
            return chiave

    return None


def trova_risposta_corretta(domanda, opzioni):
    numero_opzioni = len(opzioni)

    for chiave in CORRECT_KEYS:
        if chiave not in domanda:
            continue

        valore = domanda[chiave]

        if isinstance(valore, int):
            if 0 <= valore < numero_opzioni:
                return chiave, valore, opzioni[valore], "indice_zero"

            if 1 <= valore <= numero_opzioni:
                return chiave, valore - 1, opzioni[valore - 1], "indice_uno"

        if isinstance(valore, str):
            testo = valore.strip()

            if testo in opzioni:
                return chiave, opzioni.index(testo), testo, "testo"

            if testo.upper() in LETTERS[:numero_opzioni]:
                indice = LETTERS.index(testo.upper())
                return chiave, indice, opzioni[indice], "lettera"

            if testo.isdigit():
                numero = int(testo)

                if 0 <= numero < numero_opzioni:
                    return chiave, numero, opzioni[numero], "indice_zero_stringa"

                if 1 <= numero <= numero_opzioni:
                    return chiave, numero - 1, opzioni[numero - 1], "indice_uno_stringa"

    return None, None, None, None


def aggiorna_campo_risposta(domanda, chiave_corretta, tipo_corretta, nuovo_indice, testo_corretta):
    if tipo_corretta == "testo":
        domanda[chiave_corretta] = testo_corretta

    elif tipo_corretta == "lettera":
        domanda[chiave_corretta] = LETTERS[nuovo_indice]

    elif tipo_corretta == "indice_zero":
        domanda[chiave_corretta] = nuovo_indice

    elif tipo_corretta == "indice_uno":
        domanda[chiave_corretta] = nuovo_indice + 1

    elif tipo_corretta == "indice_zero_stringa":
        domanda[chiave_corretta] = str(nuovo_indice)

    elif tipo_corretta == "indice_uno_stringa":
        domanda[chiave_corretta] = str(nuovo_indice + 1)


def mescola_domande_file(json_path, seed_base=20260616):
    try:
        dati = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return 0, Counter()

    domande = trova_lista_domande(dati)

    if not domande:
        return 0, Counter()

    rng = random.Random(seed_base + abs(hash(str(json_path))) % 100000)

    domande_valide = []

    for domanda in domande:
        if not isinstance(domanda, dict):
            continue

        chiave_opzioni = trova_chiave_opzioni(domanda)

        if not chiave_opzioni:
            continue

        opzioni = domanda[chiave_opzioni]

        if not all(isinstance(opzione, str) for opzione in opzioni):
            continue

        chiave_corretta, indice_corretta, testo_corretta, tipo_corretta = trova_risposta_corretta(
            domanda,
            opzioni,
        )

        if chiave_corretta is None:
            continue

        domande_valide.append(
            {
                "domanda": domanda,
                "chiave_opzioni": chiave_opzioni,
                "chiave_corretta": chiave_corretta,
                "testo_corretta": testo_corretta,
                "tipo_corretta": tipo_corretta,
            }
        )

    if not domande_valide:
        return 0, Counter()

    # Distribuisce le risposte corrette in modo bilanciato tra A, B, C, D.
    posizioni = []
    for indice in range(len(domande_valide)):
        posizioni.append(indice % 4)

    rng.shuffle(posizioni)

    distribuzione = Counter()

    for info, posizione_target in zip(domande_valide, posizioni):
        domanda = info["domanda"]
        chiave_opzioni = info["chiave_opzioni"]
        chiave_corretta = info["chiave_corretta"]
        testo_corretta = info["testo_corretta"]
        tipo_corretta = info["tipo_corretta"]

        opzioni_originali = list(domanda[chiave_opzioni])

        opzioni_sbagliate = []
        corretta_rimossa = False

        for opzione in opzioni_originali:
            if opzione == testo_corretta and not corretta_rimossa:
                corretta_rimossa = True
                continue

            opzioni_sbagliate.append(opzione)

        rng.shuffle(opzioni_sbagliate)

        posizione_target = min(posizione_target, len(opzioni_originali) - 1)

        nuove_opzioni = list(opzioni_sbagliate)
        nuove_opzioni.insert(posizione_target, testo_corretta)

        domanda[chiave_opzioni] = nuove_opzioni

        nuovo_indice = nuove_opzioni.index(testo_corretta)

        aggiorna_campo_risposta(
            domanda,
            chiave_corretta,
            tipo_corretta,
            nuovo_indice,
            testo_corretta,
        )

        distribuzione[LETTERS[nuovo_indice]] += 1

    json_path.write_text(
        json.dumps(dati, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return len(domande_valide), distribuzione


def mescola_zip(zip_path):
    modifiche_totali = 0
    distribuzione_totale = Counter()

    with tempfile.TemporaryDirectory() as tmp_nome:
        tmp = Path(tmp_nome)
        estratta = tmp / "estratta"
        nuova = tmp / "nuova.zip"

        estratta.mkdir()

        with zipfile.ZipFile(zip_path, "r") as archivio:
            archivio.extractall(estratta)

        for json_path in estratta.rglob("database_quiz.json"):
            modifiche, distribuzione = mescola_domande_file(json_path)
            modifiche_totali += modifiche
            distribuzione_totale.update(distribuzione)

        if modifiche_totali == 0:
            return 0, distribuzione_totale

        with zipfile.ZipFile(nuova, "w", zipfile.ZIP_DEFLATED) as archivio:
            for file in estratta.rglob("*"):
                if file.is_file():
                    archivio.write(file, file.relative_to(estratta))

        shutil.copy2(nuova, zip_path)

    return modifiche_totali, distribuzione_totale


def percorsi_da_processare(args):
    if args:
        return [Path(arg) for arg in args]

    return [
        Path("data"),
        Path("demo"),
        Path("demo-scienze"),
        Path("downloads"),
    ]


def main():
    import sys

    totale_modifiche = 0
    distribuzione_finale = Counter()

    for percorso in percorsi_da_processare(sys.argv[1:]):
        if not percorso.exists():
            continue

        if percorso.is_file() and percorso.suffix == ".zip":
            modifiche, distribuzione = mescola_zip(percorso)
            totale_modifiche += modifiche
            distribuzione_finale.update(distribuzione)

            if modifiche:
                print(f"Mescolato ZIP: {percorso}")

        elif percorso.is_file() and percorso.suffix == ".json":
            modifiche, distribuzione = mescola_domande_file(percorso)
            totale_modifiche += modifiche
            distribuzione_finale.update(distribuzione)

            if modifiche:
                print(f"Mescolato JSON: {percorso}")

        elif percorso.is_dir():
            for json_path in percorso.rglob("*.json"):
                if ".venv" in json_path.parts:
                    continue

                modifiche, distribuzione = mescola_domande_file(json_path)
                totale_modifiche += modifiche
                distribuzione_finale.update(distribuzione)

                if modifiche:
                    print(f"Mescolato JSON: {json_path}")

            for zip_path in percorso.rglob("*.zip"):
                modifiche, distribuzione = mescola_zip(zip_path)
                totale_modifiche += modifiche
                distribuzione_finale.update(distribuzione)

                if modifiche:
                    print(f"Mescolato ZIP: {zip_path}")

    print()
    print("Totale domande con risposte mescolate:", totale_modifiche)
    print("Distribuzione risposte corrette:", dict(distribuzione_finale))


if __name__ == "__main__":
    main()
