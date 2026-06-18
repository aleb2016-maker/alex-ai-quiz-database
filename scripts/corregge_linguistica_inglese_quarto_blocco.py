import json
from pathlib import Path

FILE = Path("data/inglese.json")
REPORT = Path("reports/corregge_linguistica_inglese_quarto_blocco.md")

CORREZIONI = {
    "ING-AV-0208": (
        "La frase corretta usa una struttura scissa con It was John who. "
        "Questa struttura mette in evidenza John come persona che ha risolto il problema. "
        "Which non è adatto per una persona in questa struttura. "
        "Le altre opzioni hanno un ordine delle parole scorretto. "
        "Traduzione domanda: \"Quale frase scissa mette in evidenza John come persona che ha risolto il problema?\" "
        "Traduzione risposta: \"È stato John a risolvere il problema.\""
    ),

    "ING-AV-0211": (
        "La struttura What I need is mette in evidenza ciò che serve davvero. "
        "La frase corretta è What I need is a clear plan. "
        "What I need it is aggiunge un pronome inutile. "
        "What need I inverte male le parole. "
        "What I need are non concorda con a clear plan. "
        "Traduzione domanda: \"Scegli la struttura enfatica corretta.\" "
        "Traduzione risposta: \"Quello di cui ho bisogno è un piano chiaro.\""
    )
}

contenuto = json.loads(FILE.read_text(encoding="utf-8"))

if isinstance(contenuto, list):
    domande = contenuto
else:
    domande = contenuto.get("domande", contenuto.get("questions", []))

corrette = []

for domanda in domande:
    id_domanda = domanda.get("id")

    if id_domanda in CORREZIONI:
        domanda["spiegazione"] = CORREZIONI[id_domanda]
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve essere vicina alla corretta per struttura, significato o contesto, "
            "ma sbagliata per un dettaglio preciso: verbo, tempo, articolo, preposizione, connettivo, registro o traduzione."
        )
        corrette.append(id_domanda)

mancanti = sorted(set(CORREZIONI) - set(corrette))

if mancanti:
    raise SystemExit(f"ERRORE: domande non trovate: {mancanti}")

FILE.write_text(
    json.dumps(contenuto, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

REPORT.write_text(
    "# Correzione linguistica Inglese quarto blocco\n\n"
    "Corrette spiegazioni con falso errore di spazio dopo punteggiatura.\n\n"
    "Domande corrette:\n"
    + "\n".join(f"- {id_domanda}" for id_domanda in corrette)
    + "\n",
    encoding="utf-8"
)

print("OK: corrette spiegazioni linguistiche quarto blocco Inglese.")
for id_domanda in corrette:
    print("-", id_domanda)
