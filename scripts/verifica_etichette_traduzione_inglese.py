import json
import sys
from pathlib import Path

FILE = Path("data/inglese.json")

contenuto = json.loads(FILE.read_text(encoding="utf-8"))

if isinstance(contenuto, list):
    domande = contenuto
else:
    domande = contenuto.get("domande", contenuto.get("questions", []))

problemi = []

for domanda in domande:
    id_domanda = domanda.get("id", "SENZA_ID")
    spiegazione = domanda.get("spiegazione", "")

    if "Traduzione domanda:" not in spiegazione:
        problemi.append(f"{id_domanda}: manca Traduzione domanda:")

    if "Traduzione risposta:" not in spiegazione:
        problemi.append(f"{id_domanda}: manca Traduzione risposta:")

if problemi:
    print("CONTROLLO TRADUZIONI INGLESE: problemi trovati.")
    for problema in problemi:
        print("-", problema)
    sys.exit(1)

print("CONTROLLO TRADUZIONI INGLESE: tutte le etichette sono presenti.")
