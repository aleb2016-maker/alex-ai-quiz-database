import json
from pathlib import Path


PERCORSO_DATABASE = Path("dist/database_quiz_finale.json")
PERCORSO_OUTPUT = Path("dist/domande_gialle_motore")


CATEGORIE_MOTORE = {
    "ai",
    "informatica",
    "logica",
}


def carica_database():
    with open(PERCORSO_DATABASE, "r", encoding="utf-8") as file:
        return json.load(file)


def manca_certificazione_motore(domanda):
    distrattore_forte = domanda.get("distrattore_forte", "")
    motivo = domanda.get("motivo_distrattore_forte", "")

    return not distrattore_forte or not motivo


def crea_blocco_domanda(domanda):
    id_domanda = domanda.get("id", "ID_MANCANTE")
    categoria = domanda.get("categoria", "categoria_mancante")
    livello = domanda.get("livello", "livello_mancante")
    testo = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")
    spiegazione = domanda.get("spiegazione", "")

    righe = []

    righe.append(f"### {id_domanda}")
    righe.append("")
    righe.append(f"**Categoria:** {categoria}")
    righe.append("")
    righe.append(f"**Livello:** {livello}")
    righe.append("")
    righe.append(f"**Domanda:** {testo}")
    righe.append("")
    righe.append("**Opzioni:**")

    lettere = ["A", "B", "C", "D"]

    for indice, opzione in enumerate(opzioni):
        simbolo = "✅" if opzione == risposta_corretta else "❌"
        righe.append(f"- {lettere[indice]}. {simbolo} {opzione}")

    righe.append("")
    righe.append(f"**Risposta corretta:** {risposta_corretta}")
    righe.append("")
    righe.append(f"**Spiegazione:** {spiegazione}")
    righe.append("")
    righe.append("**Da aggiungere:**")
    righe.append("")
    righe.append("- distrattore_forte:")
    righe.append("- motivo_distrattore_forte:")
    righe.append("")
    righe.append("---")
    righe.append("")

    return "\n".join(righe)


def main():
    domande = carica_database()

    PERCORSO_OUTPUT.mkdir(parents=True, exist_ok=True)

    domande_per_categoria = {
        "ai": [],
        "informatica": [],
        "logica": [],
    }

    for domanda in domande:
        categoria = domanda.get("categoria", "")

        if categoria not in CATEGORIE_MOTORE:
            continue

        if manca_certificazione_motore(domanda):
            domande_per_categoria[categoria].append(domanda)

    for categoria, lista_domande in domande_per_categoria.items():
        righe = []

        righe.append(f"# Domande gialle motore - {categoria}")
        righe.append("")
        righe.append(f"Totale domande da certificare: {len(lista_domande)}")
        righe.append("")
        righe.append("---")
        righe.append("")

        for domanda in lista_domande:
            righe.append(crea_blocco_domanda(domanda))

        percorso_file = PERCORSO_OUTPUT / f"{categoria}.md"

        percorso_file.write_text(
            "\n".join(righe),
            encoding="utf-8"
        )

        print(f"{categoria}: {len(lista_domande)} domande esportate in {percorso_file}")


main()