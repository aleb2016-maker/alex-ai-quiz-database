from pathlib import Path

ROOT = Path.cwd()
VALIDATOR = ROOT / "scripts/validatore_duplicati_database.py"
REPORT = ROOT / "reports/correggi_duplicati_logica_visiva.md"

text = VALIDATOR.read_text(encoding="utf-8")

old = '''        if question_text:
            if question_text in question_texts:
                problems.append({
                    "file": relative_path,
                    "id": question_id,
                    "messaggio": f"Domanda identica a {question_texts[question_text]}",
                })
            else:
                question_texts[question_text] = question_id
'''

new = '''        # Per LOG-VIS il testo della domanda può essere volutamente neutro e identico.
        # La distinzione reale sta nelle immagini, nelle opzioni e nel visual_logic.
        # Quindi non blocchiamo i duplicati testuali delle domande visive.
        if question_text and not question_id.startswith("LOG-VIS"):
            if question_text in question_texts:
                problems.append({
                    "file": relative_path,
                    "id": question_id,
                    "messaggio": f"Domanda identica a {question_texts[question_text]}",
                })
            else:
                question_texts[question_text] = question_id
'''

if old not in text:
    raise RuntimeError("Blocco duplicati domanda non trovato nel validatore.")

text = text.replace(old, new)
VALIDATOR.write_text(text, encoding="utf-8")

REPORT.write_text(
    "\n".join([
        "# Correzione duplicati Logica visiva",
        "",
        "Aggiornato `scripts/validatore_duplicati_database.py`.",
        "",
        "Le domande `LOG-VIS` possono avere testo neutro identico, perché la distinzione reale è visuale:",
        "",
        "- immagini;",
        "- opzioni;",
        "- risposta corretta;",
        "- visual_logic.",
        "",
        "Il validatore continua invece a bloccare:",
        "",
        "- ID duplicati;",
        "- opzioni duplicate nella stessa domanda;",
        "- domande testuali identiche non visuali.",
        "",
    ])
    + "\n",
    encoding="utf-8",
)

print("✅ Validatore duplicati corretto per Logica visiva.")
print(f"Report: {REPORT}")
