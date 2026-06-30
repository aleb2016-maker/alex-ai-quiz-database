from pathlib import Path
from datetime import datetime
import json
import time
import urllib.request
import urllib.error

ROOT = Path.cwd()
REPORT_DIR = ROOT / "reports" / "confronto_top2_ollama_universale_v2a35b"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MODELLI = [
    "llama3.1:8b",
    "qwen2.5:7b",
]

TESTI = {
    "aziendale": (
        "Il documento descrive procedure operative aziendali ripetute in più reparti. "
        "Le sezioni trattano controlli, verifiche periodiche, tracciabilità delle attività, "
        "registri operativi, responsabilità dei team, sistemi coinvolti, rischi residui "
        "e produzione di evidenze. Il problema principale è evitare passaggi informali "
        "e rendere confrontabili i risultati tra sedi, reparti e fornitori."
    ),
    "scientifico": (
        "Lo studio analizza gli effetti della qualità del sonno sulla memoria a breve termine. "
        "I partecipanti sono stati divisi in gruppi con diverse ore di riposo e sottoposti a test "
        "di attenzione, richiamo di parole e velocità di risposta. I risultati mostrano che una "
        "riduzione significativa del sonno peggiora la precisione delle risposte e aumenta gli errori."
    ),
    "tecnico": (
        "Il sistema è composto da un modulo di acquisizione dati, un database locale, un servizio "
        "di elaborazione e una dashboard web. Il flusso principale prevede la ricezione degli input, "
        "la validazione dei campi, il salvataggio dei dati e la generazione di report periodici. "
        "Gli errori devono essere registrati con messaggi chiari e codici diagnostici."
    ),
    "narrativo_artistico": (
        "Il racconto segue una giovane restauratrice che entra in un teatro abbandonato per recuperare "
        "un antico fondale dipinto. Mentre osserva le figure rovinate dal tempo, scopre lettere nascoste "
        "dietro la tela e ricostruisce la storia di una compagnia scomparsa. L'atmosfera alterna mistero, "
        "nostalgia e meraviglia."
    ),
    "sportivo": (
        "La scheda di allenamento prevede tre sessioni settimanali dedicate a resistenza, forza e recupero. "
        "Ogni seduta include riscaldamento, esercizi principali, controllo della fatica e stretching finale. "
        "Il programma aumenta gradualmente il carico e richiede di annotare progressi, dolori e tempi di recupero."
    ),
}

PAROLE_VIETATE = [
    "normative vigenti",
    "azione quali",
    "quali sistemi",
    "aperti quale",
    "operativo conferma",
    "traccia scritta",
    "procedura richiede",
    "è importante notare",
    "sembra mirare",
]

def prompt_per_testo(nome: str, testo: str) -> str:
    return (
        "Sei un motore locale universale per riassunti di alta qualità. "
        "Scrivi SOLO in italiano naturale, chiaro e professionale. "
        "Devi produrre da 5 a 7 frasi complete. "
        "Non fare elenco numerato. "
        "Non inventare informazioni non presenti. "
        "Non aggiungere normative, leggi, obblighi, cause o dettagli non presenti nel testo. "
        "Non ripetere lo stesso concetto due volte. "
        "Non usare frasi riempitive come 'è importante notare'. "
        "Non usare parole spezzate o frammenti senza senso. "
        "Fondi i concetti ripetuti in un testo fluido. "
        f"Categoria del testo: {nome}. "
        f"Testo da riassumere: {testo}"
    )

def chiama_ollama(modello: str, categoria: str, testo: str) -> dict:
    payload = {
        "model": modello,
        "stream": False,
        "options": {
            "temperature": 0.12,
            "num_ctx": 4096,
            "num_predict": 420,
        },
        "prompt": prompt_per_testo(categoria, testo),
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
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return {
            "modello": modello,
            "categoria": categoria,
            "ok": False,
            "errore": str(exc),
            "secondi_reali": round(time.time() - start, 2),
        }
    except Exception as exc:
        return {
            "modello": modello,
            "categoria": categoria,
            "ok": False,
            "errore": repr(exc),
            "secondi_reali": round(time.time() - start, 2),
        }

    risposta = parsed.get("response", "").strip()
    lower = risposta.lower()
    frasi = [x.strip() for x in risposta.replace("?", ".").replace("!", ".").split(".") if x.strip()]
    vietate = [p for p in PAROLE_VIETATE if p in lower]

    score = 100
    note = []

    if not risposta:
        score -= 70
        note.append("Risposta vuota")

    if len(frasi) < 5:
        score -= 15
        note.append("Troppo corto")

    if len(frasi) > 7:
        score -= 12
        note.append("Troppo lungo")

    if vietate:
        score -= 25
        note.append("Frasi/parole vietate: " + ", ".join(vietate))

    if len(risposta) < 300:
        score -= 8
        note.append("Un po' corto")

    if len(risposta) > 1400:
        score -= 10
        note.append("Troppo prolisso")

    if risposta.strip().startswith(("1.", "1)", "- ")):
        score -= 15
        note.append("Ha fatto elenco invece di paragrafo")

    return {
        "modello": modello,
        "categoria": categoria,
        "ok": True,
        "score": max(0, score),
        "note": note,
        "risposta": risposta,
        "frasi_stimate": len(frasi),
        "caratteri": len(risposta),
        "secondi_reali": round(time.time() - start, 2),
        "total_duration_sec": round(parsed.get("total_duration", 0) / 1e9, 2),
        "eval_count": parsed.get("eval_count"),
        "prompt_eval_count": parsed.get("prompt_eval_count"),
    }

def main():
    risultati = []

    for modello in MODELLI:
        for categoria, testo in TESTI.items():
            print(f"\n=== TEST {modello} / {categoria} ===")
            risultato = chiama_ollama(modello, categoria, testo)
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

    riepilogo = {}
    for r in risultati:
        modello = r["modello"]
        riepilogo.setdefault(modello, {"score": 0, "tempo": 0, "test": 0, "errori": 0})
        riepilogo[modello]["test"] += 1

        if r.get("ok"):
            riepilogo[modello]["score"] += r.get("score", 0)
            riepilogo[modello]["tempo"] += r.get("secondi_reali", 0)
        else:
            riepilogo[modello]["errori"] += 1

    for modello, dati in riepilogo.items():
        test_validi = max(1, dati["test"] - dati["errori"])
        dati["score_medio"] = round(dati["score"] / test_validi, 2)
        dati["tempo_medio"] = round(dati["tempo"] / test_validi, 2)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORT_DIR / f"top2_ollama_universale_v2a35b_{timestamp}.json"
    md_path = REPORT_DIR / f"top2_ollama_universale_v2a35b_{timestamp}.md"

    json_path.write_text(
        json.dumps({"riepilogo": riepilogo, "risultati": risultati}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    righe = [
        "# Confronto top 2 modelli Ollama universali V2A35B",
        "",
        "## Riepilogo",
        "",
        "| Modello | Score medio | Tempo medio | Test | Errori |",
        "|---|---:|---:|---:|---:|",
    ]

    for modello, dati in sorted(riepilogo.items(), key=lambda x: x[1]["score_medio"], reverse=True):
        righe.append(
            f"| {modello} | {dati['score_medio']} | {dati['tempo_medio']}s | {dati['test']} | {dati['errori']} |"
        )

    righe.append("")
    righe.append("## Risposte complete")
    righe.append("")

    for r in risultati:
        righe.append(f"### {r['modello']} / {r['categoria']}")
        righe.append("")
        if r.get("ok"):
            righe.append(f"Score: {r['score']} - Tempo: {r['secondi_reali']}s - Frasi: {r['frasi_stimate']}")
            if r["note"]:
                righe.append("Note: " + "; ".join(r["note"]))
            righe.append("")
            righe.append(r["risposta"])
        else:
            righe.append("ERRORE: " + r.get("errore", "errore sconosciuto"))
        righe.append("")

    md_path.write_text("\n".join(righe), encoding="utf-8")

    print("\n=== RIEPILOGO ===")
    for modello, dati in sorted(riepilogo.items(), key=lambda x: x[1]["score_medio"], reverse=True):
        print(f"{modello}: score medio {dati['score_medio']} - tempo medio {dati['tempo_medio']}s")

    print("\n=== REPORT CREATI ===")
    print(json_path)
    print(md_path)

if __name__ == "__main__":
    main()
