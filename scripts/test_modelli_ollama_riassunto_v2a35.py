from pathlib import Path
from datetime import datetime
import json
import time
import urllib.request
import urllib.error

ROOT = Path.cwd()
REPORT_DIR = ROOT / "reports" / "confronto_modelli_ollama_v2a35"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MODELLI = [
    "llama3.1:8b",
    "mistral:7b",
    "qwen2.5:7b",
    "llama3.2:3b",
    "phi3:mini",
]

TESTO = (
    "Il documento descrive procedure operative aziendali ripetute in più reparti. "
    "Le sezioni trattano controlli, verifiche periodiche, tracciabilità delle attività, "
    "registri operativi, responsabilità dei team, sistemi coinvolti, rischi residui "
    "e produzione di evidenze. Il problema principale è evitare passaggi informali "
    "e rendere confrontabili i risultati tra sedi, reparti e fornitori."
)

PROMPT = (
    "Sei un motore locale per riassunti di alta qualità. "
    "Scrivi SOLO in italiano naturale e professionale. "
    "Devi produrre 6 frasi complete, non di più. "
    "Non fare elenco numerato. "
    "Non inventare informazioni non presenti. "
    "Non citare normative, leggi o obblighi se non sono nel testo. "
    "Non ripetere lo stesso concetto due volte. "
    "Non copiare frasi meccaniche. "
    "Non usare parole spezzate. "
    "Fondi i concetti ripetuti in un testo fluido. "
    f"Testo da riassumere: {TESTO}"
)

PAROLE_VIETATE = [
    "normative vigenti",
    "azione quali",
    "quali sistemi",
    "aperti quale",
    "operativo conferma",
    "traccia scritta",
    "procedura richiede",
]

def chiama_ollama(modello: str) -> dict:
    payload = {
        "model": modello,
        "stream": False,
        "options": {
            "temperature": 0.15,
            "num_ctx": 4096,
            "num_predict": 450,
        },
        "prompt": PROMPT,
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.time()

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw)
    except urllib.error.URLError as exc:
        return {
            "modello": modello,
            "ok": False,
            "errore": str(exc),
            "secondi_reali": round(time.time() - start, 2),
        }
    except Exception as exc:
        return {
            "modello": modello,
            "ok": False,
            "errore": repr(exc),
            "secondi_reali": round(time.time() - start, 2),
        }

    testo = parsed.get("response", "").strip()
    lower = testo.lower()

    parole_trovate = [p for p in PAROLE_VIETATE if p in lower]
    frasi = [x.strip() for x in testo.replace("?", ".").replace("!", ".").split(".") if x.strip()]

    score = 100
    note = []

    if not testo:
        score -= 60
        note.append("Risposta vuota")

    if len(frasi) < 4:
        score -= 15
        note.append("Troppo corto")

    if len(frasi) > 7:
        score -= 10
        note.append("Troppo lungo")

    if parole_trovate:
        score -= 25
        note.append("Parole/frammenti vietati: " + ", ".join(parole_trovate))

    if "sembra" in lower:
        score -= 6
        note.append("Formula debole: sembra")

    if "è importante notare" in lower:
        score -= 6
        note.append("Riempitivo: è importante notare")

    if "normative" in lower or "leggi" in lower:
        score -= 20
        note.append("Possibile invenzione normativa")

    if len(testo) > 1400:
        score -= 10
        note.append("Risposta troppo prolissa")

    if len(testo) < 250:
        score -= 8
        note.append("Risposta un po' corta")

    return {
        "modello": modello,
        "ok": True,
        "score": max(0, score),
        "note": note,
        "risposta": testo,
        "frasi_stimate": len(frasi),
        "caratteri": len(testo),
        "secondi_reali": round(time.time() - start, 2),
        "total_duration_sec": round(parsed.get("total_duration", 0) / 1e9, 2),
        "eval_count": parsed.get("eval_count"),
        "prompt_eval_count": parsed.get("prompt_eval_count"),
    }

def main():
    risultati = []

    for modello in MODELLI:
        print(f"\n=== TEST {modello} ===")
        risultato = chiama_ollama(modello)
        risultati.append(risultato)

        if risultato.get("ok"):
            print("Score:", risultato["score"])
            print("Tempo:", risultato["secondi_reali"], "sec")
            print("Frasi:", risultato["frasi_stimate"])
            print(risultato["risposta"])
            if risultato["note"]:
                print("Note:", "; ".join(risultato["note"]))
        else:
            print("ERRORE:", risultato.get("errore"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORT_DIR / f"confronto_modelli_ollama_v2a35_{timestamp}.json"
    md_path = REPORT_DIR / f"confronto_modelli_ollama_v2a35_{timestamp}.md"

    json_path.write_text(json.dumps(risultati, ensure_ascii=False, indent=2), encoding="utf-8")

    righe = [
        "# Confronto modelli Ollama V2A35",
        "",
        "| Modello | Score | Tempo reale | Frasi | Caratteri | Note |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for r in risultati:
        if not r.get("ok"):
            righe.append(f"| {r['modello']} | 0 | {r.get('secondi_reali')} | - | - | ERRORE: {r.get('errore')} |")
            continue

        note = "; ".join(r.get("note") or [])
        righe.append(
            f"| {r['modello']} | {r['score']} | {r['secondi_reali']}s | "
            f"{r['frasi_stimate']} | {r['caratteri']} | {note} |"
        )

    righe.append("")
    righe.append("## Risposte complete")
    righe.append("")

    for r in risultati:
        righe.append(f"### {r['modello']}")
        righe.append("")
        if r.get("ok"):
            righe.append(r["risposta"])
        else:
            righe.append("ERRORE: " + r.get("errore", "errore sconosciuto"))
        righe.append("")

    md_path.write_text("\n".join(righe), encoding="utf-8")

    print("\n=== REPORT CREATI ===")
    print(json_path)
    print(md_path)

if __name__ == "__main__":
    main()
