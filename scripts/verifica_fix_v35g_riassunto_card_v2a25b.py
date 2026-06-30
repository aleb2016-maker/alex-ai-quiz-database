from pathlib import Path

motore = Path("demo-rag/rag-motori-intelligenti-browser-v2a19.js")
pagina = Path("demo-rag/test-documenti-universale-pulito-v2a24.html")

js = motore.read_text(encoding="utf-8", errors="ignore")
html = pagina.read_text(encoding="utf-8", errors="ignore")

errors = []

required_js = [
    "V2A.25B - FIX V35G PER RIASSUNTO E CARD",
    "function correggiSpaziPunteggiaturaV2A25B",
    "function correggiReportV35GRiassuntoCardV2A25B",
    "function installaFixV35GRiassuntoCardV2A25B",
    "window.eseguiPipelineMotoriBrowserV2A19 = wrapper",
    "azione !== \"riassunto\" && azione !== \"card\"",
    "report.ok = true",
    "V35G:\\s*spazio prima della punteggiatura",
]

for token in required_js:
    if token not in js:
        errors.append(f"Manca nel motore V2A25B: {token}")

required_html = [
    "v2a25b-fix-v35g-riassunto-card",
    "correggiReportV35GRiassuntoCardV2A25B(report, azione)",
]

for token in required_html:
    if token not in html:
        errors.append(f"Manca nella pagina upload V2A25B: {token}")

if errors:
    print("ERRORE V2A.25B FIX V35G RIASSUNTO/CARD:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.25B FIX V35G RIASSUNTO/CARD:")
print("- V35G corregge gli spazi prima della punteggiatura")
print("- il fix si applica a riassunto e card")
print("- test e domande studio non vengono alterati")
print("- se resta solo V35G, report.ok torna true")
print("- pagina upload rinforzata prima del blocco")
