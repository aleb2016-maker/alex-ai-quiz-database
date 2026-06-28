from pathlib import Path

errors = []

engine = Path("demo-rag/rag-quality-summary-cards-v34a.js")

if not engine.exists():
    errors.append("Manca demo-rag/rag-quality-summary-cards-v34a.js")
else:
    text = engine.read_text(encoding="utf-8")
    required = [
        "RAGQualitySummaryCardsV34A",
        "buildSummaryData",
        "buildCardsData",
        "renderSummary",
        "renderCards",
        "enrichByContext",
        "extractKeywords",
        "bestSentences"
    ]

    for item in required:
        if item not in text:
            errors.append(f"Manca blocco/funzione: {item}")

pages = [
    Path("demo-rag/test-documenti-universale.html"),
    Path("demo-rag/test-rag-pipeline.html"),
    Path("demo-rag/index.html"),
]

linked = []

for page in pages:
    if page.exists():
        html = page.read_text(encoding="utf-8")
        if "rag-quality-summary-cards-v34a.js" in html:
            linked.append(str(page))

if not linked:
    errors.append("Il motore qualità V3.4A non è collegato a nessuna pagina RAG.")

print("\n=== VERIFICA RAG SUMMARY + CARDS V3.4A ===")

if errors:
    print("ESITO: KO")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("ESITO: OK")
print("Motore presente:", engine)
print("Pagine collegate:")
for page in linked:
    print("-", page)
