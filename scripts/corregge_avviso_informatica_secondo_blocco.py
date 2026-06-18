import json
from pathlib import Path

FILE = Path("data/informatica.json")
REPORT = Path("reports/corregge_avviso_informatica_secondo_blocco.md")

ID_DA_CORREGGERE = "INF-AV-0103"

NUOVE_OPZIONI = [
    "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
    "Perché conserva dati usati spesso, ma può restituire dati non aggiornati se la cache non viene gestita bene",
    "Perché riduce accessi ripetuti a dati frequenti, ma sposta ogni dato del database in memoria locale",
    "Perché migliora le prestazioni, ma anche quando i dati salvati non vengono riutilizzati"
]

NUOVA_SPIEGAZIONE = (
    "La cache può migliorare le prestazioni perché evita di ricalcolare o recuperare più volte dati usati spesso. "
    "Va gestita bene perché può restituire dati non aggiornati; non sposta tutto il database in memoria e non aiuta se i dati non vengono riutilizzati."
)

contenuto = json.loads(FILE.read_text(encoding="utf-8"))

if isinstance(contenuto, list):
    domande = contenuto
else:
    domande = contenuto.get("domande", contenuto.get("questions", []))

corretta = False

for domanda in domande:
    if domanda.get("id") == ID_DA_CORREGGERE:
        domanda["opzioni"] = NUOVE_OPZIONI
        domanda["risposta_corretta"] = NUOVE_OPZIONI[0]
        domanda["spiegazione"] = NUOVA_SPIEGAZIONE
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve condividere il concetto centrale della corretta "
            "e diventare sbagliata per un dettaglio tecnico, logico o pratico."
        )
        corretta = True
        break

if not corretta:
    raise SystemExit(f"ERRORE: domanda {ID_DA_CORREGGERE} non trovata.")

FILE.write_text(
    json.dumps(contenuto, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

REPORT.write_text(
    "# Correzione avviso Informatica secondo blocco\n\n"
    "- Domanda corretta: INF-AV-0103\n"
    "- Rimossa formulazione troppo assoluta: “mai vecchi”.\n",
    encoding="utf-8"
)

print("OK: corretto avviso su INF-AV-0103.")
