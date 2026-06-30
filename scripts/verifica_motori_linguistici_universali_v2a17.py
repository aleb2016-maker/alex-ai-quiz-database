from pathlib import Path
import re

engine = Path("demo-rag/universal-document-learning-engine.js")
assert engine.exists(), "Manca universal-document-learning-engine.js"

txt = engine.read_text(encoding="utf-8", errors="ignore")

errors = []

required_terms = [
    "CONTRATTO_LINGUISTICO_UNIVERSALE_V2A17",
    "verificaContrattoLinguisticoUniversaleV2A17",
    "verificaQualitaTestualeBaseV2A17",
    "verificaDuplicatiPerContestoV2A17",
    "verificaTestSeparatoV2A17",
    "grammatica italiana corretta",
    "accenti corretti",
    "apostrofi corretti",
    "punteggiatura corretta",
    "frasi complete",
    "assenza frasi spezzate",
    "assenza frasi non terminate",
    "assenza finali sospetti",
    "assenza frasi riempitive",
    "assenza testo generico",
    "assenza vecchi fallback demo test",
    "domande studio naturali",
    "risposte guida specifiche",
    "spiegazioni test chiare",
    "categorie presenti",
    "sottocategorie presenti",
    "card scritte bene",
    "riassunto chiaro",
    "fonti coerenti",
    "test separato da card riassunto domande studio",
    "quattro opzioni per domanda",
    "distrattori forti",
    "duplicati esatti per tipo output",
    "ripetizioni legittime consentite",
    "compito richiesto seleziona motori giusti",
    "naturalezza anti-keyword V3.5I",
    "accordo genere",
    "correzione frasi non finite",
    "uso contesto tema",
    "uso contesto sottotema",
    "uso categorie",
    "uso sottocategorie",
    "correzione parole scritte male",
    "correzione lettere invertite",
]

for term in required_terms:
    if term not in txt:
        errors.append(f"Manca controllo/termine V2A17: {term}")

for azione in ["riassunto", "card", "test", "domande"]:
    pattern = f'verificaContrattoLinguisticoUniversaleV2A17("{azione}"'
    if pattern not in txt:
        errors.append(f"Il pulsante {azione} non chiama il contratto linguistico V2A17")

# Deve restare vietato V2A15.

# Non bloccare argomenti reali come se fossero fallback.
if '"sicurezza informatica aziendale"' in txt or "'sicurezza informatica aziendale'" in txt:
    errors.append("V2A17 non deve vietare l'argomento reale 'sicurezza informatica aziendale'")

for bad in [
    "rag-summary-topic-aware-v2a15.js",
    "rag-summary-long-quality-v2a14.js",
    "function classifyDocument",
    "classificatore interno",
]:
    if bad in txt:
        errors.append(f"Resta elemento vietato: {bad}")



# Distinzione obbligatoria V2A17:
# motore linguistico universale su tutti gli output;
# controlli strutturali quiz solo su Test.
engine_text = txt

blocchi_universali = [
    "qualita_testuale",
    "qualita_didattica",
    "card_riassunto_fonti",
    "duplicati_ripetizioni",
    "selezionatore_orchestratore",
    "naturalezza_linguistica",
    "accordo_grammaticale",
    "completamento_frasi",
    "correzione_refusi",
]

start = engine_text.find("const blocchiObbligatori = [")
end = engine_text.find("];", start)

if start == -1 or end == -1:
    errors.append("Non trovo blocchiObbligatori V2A17")
else:
    blocco_base = engine_text[start:end]
    for blocco in blocchi_universali:
        if f'"{blocco}"' not in blocco_base and f"'{blocco}'" not in blocco_base:
            errors.append(f"Motore linguistico universale non presente nei blocchi base: {blocco}")

    if '"test_separati"' in blocco_base or "'test_separati'" in blocco_base:
        errors.append("ERRORE: test_separati non deve stare nei blocchi universali base")

if 'if (azione === "test")' not in engine_text:
    errors.append("Manca distinzione azione === test per controlli quiz")

if 'blocchiObbligatori.push("test_separati")' not in engine_text:
    errors.append("test_separati deve essere aggiunto solo nel ramo Test")

if 'if (azione === "test" && dati.quiz)' not in engine_text:
    errors.append("verificaTestSeparatoV2A17 deve partire solo nel ramo Test")

for azione in ["riassunto", "card", "test", "domande"]:
    chiamata = f'verificaContrattoLinguisticoUniversaleV2A17("{azione}"'
    if chiamata not in engine_text:
        errors.append(f"Il pulsante {azione} non chiama il contratto linguistico universale")


if errors:
    print("ERRORE V2A.17:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.17:")
print("- contratto linguistico universale presente")
print("- qualità testuale collegata")
print("- qualità didattica collegata")
print("- card/riassunto/fonti collegati")
print("- test separati collegati")
print("- duplicati controllati per contesto")
print("- selezionatore/orchestratore dichiarato")
print("- naturalezza anti-keyword collegata")
print("- accordo grammaticale collegato")
print("- completatore frasi incomplete collegato come requisito")
print("- correttore refusi/parole collegate come requisito")
print("- tutti i pulsanti chiamano il contratto V2A17")
