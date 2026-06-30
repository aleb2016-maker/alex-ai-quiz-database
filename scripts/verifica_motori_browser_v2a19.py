from pathlib import Path
import re

errors = []

js = Path("demo-rag/rag-motori-intelligenti-browser-v2a19.js")
engine = Path("demo-rag/universal-document-learning-engine.js")
pagina = Path("demo-rag/test-documenti-universale.html")

if not js.exists():
    errors.append("Manca demo-rag/rag-motori-intelligenti-browser-v2a19.js")

txt = js.read_text(encoding="utf-8", errors="ignore") if js.exists() else ""
engine_txt = engine.read_text(encoding="utf-8", errors="ignore")
pagina_txt = pagina.read_text(encoding="utf-8", errors="ignore")

required_js = [
    "RAG_MOTORI_INTELLIGENTI_BROWSER_V2A19",
    "eseguiPipelineMotoriBrowserV2A19",
    "renderizzaOutputMotoriBrowserV2A19",
    "mostraOutputMotoriBrowserV2A19",
    "AZIONI_MOTORI_BROWSER_V2A19",
    "MOTORI_BROWSER_V2A19",
    "V35B",
    "V35C",
    "V35D",
    "V35E",
    "V35F",
    "V35G",
    "V35I",
    "V35J",
    "V35K",
    "V35M",
    "V35N",
    "V35O",
    "creaRiassuntoReale",
    "creaCardBrowser",
    "creaTestBrowser",
    "creaDomandeStudioBrowser",
    "targetPercento",
    "minPercento",
    "maxPercento",
    "Nessuna API a pagamento",
]

for r in required_js:
    if r not in txt:
        errors.append(f"Manca nel motore browser V2A19: {r}")

if "rag-motori-intelligenti-browser-v2a19.js" not in pagina_txt:
    errors.append("La pagina universale non carica rag-motori-intelligenti-browser-v2a19.js")

if "rag-motori-intelligenti-browser-v2a19.js" in pagina_txt and "universal-document-learning-engine.js" in pagina_txt:
    pos_v2a19 = pagina_txt.find("rag-motori-intelligenti-browser-v2a19.js")
    pos_engine = pagina_txt.find("universal-document-learning-engine.js")
    if pos_v2a19 > pos_engine:
        errors.append("V2A19 viene caricato dopo universal-document-learning-engine.js: deve essere prima")

required_engine = [
    "BLOCCO V2A.19: motore browser reale non caricato",
    "window.eseguiPipelineMotoriBrowserV2A19",
    'eseguiMotoriIntelligentiUniversaliV35V2A18("riassunto"',
    'eseguiMotoriIntelligentiUniversaliV35V2A18("card"',
    'eseguiMotoriIntelligentiUniversaliV35V2A18("test"',
    'eseguiMotoriIntelligentiUniversaliV35V2A18("domande"',
    'window.mostraOutputMotoriBrowserV2A19("riassunto"',
    'window.mostraOutputMotoriBrowserV2A19("card"',
    'window.mostraOutputMotoriBrowserV2A19("test"',
    'window.mostraOutputMotoriBrowserV2A19("domande"',
]

for r in required_engine:
    if r not in engine_txt:
        errors.append(f"Manca nel motore universale: {r}")

vietati = [
    "api.openai.com",
    "OPENAI_API_KEY",
    "fetch(\"https://",
    "fetch('https://",
    "axios",
]

for v in vietati:
    if v in txt:
        errors.append(f"Il motore browser contiene chiamata/API vietata: {v}")

for azione in ["riassunto", "card", "test", "domande"]:
    if azione not in txt:
        errors.append(f"Manca azione browser V2A19: {azione}")

if errors:
    print("ERRORE V2A.19 MOTORI BROWSER:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.19 MOTORI BROWSER:")
print("- motore browser-only creato")
print("- nessuna API a pagamento")
print("- pagina universale carica V2A19 prima del motore universale")
print("- V2A18 blocca se V2A19 non è caricato")
print("- i 4 pulsanti generano output tramite V2A19")
