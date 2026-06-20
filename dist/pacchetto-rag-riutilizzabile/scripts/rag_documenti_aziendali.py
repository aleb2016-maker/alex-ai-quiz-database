#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import csv
import re
import html
from collections import Counter
from datetime import datetime

STOPWORDS = {"della","delle","degli","dello","alla","alle","agli","allo","questo","questa","questi","queste","sono","essere","avere","come","dove","quando","perche","perché","nelle","nella","negli","nello","anche","deve","devono","puo","può","viene","vengono","dopo","prima","ogni","tutti","tutte","molto","senza","sulla","sulle","sugli","sullo","tra","fra","con","per","del","dei","nel","nei","non","una","uno","gli","che","chi","dal","dai","più","meno"}

def leggi_file(path):
    est = path.suffix.lower()
    if est in [".txt", ".md"]:
        return path.read_text(encoding="utf-8", errors="ignore")
    if est == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8", errors="ignore")), ensure_ascii=False, indent=2)
    if est == ".csv":
        righe = []
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            for row in csv.reader(f):
                righe.append(" | ".join(c.strip() for c in row if c.strip()))
        return "\n".join(righe)
    if est == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception:
            raise SystemExit("Per leggere PDF installa pypdf: pip install pypdf")
        return "\n\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    if est == ".docx":
        try:
            import docx
        except Exception:
            raise SystemExit("Per leggere DOCX installa python-docx: pip install python-docx")
        return "\n".join(p.text for p in docx.Document(str(path)).paragraphs)
    raise SystemExit(f"Formato non supportato: {est}")

def pulisci(testo):
    testo = testo.replace("\r\n", "\n").replace("\r", "\n")
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    testo = re.sub(r" +([,.!?;:])", r"\1", testo)
    testo = re.sub(r"([,.!?;:])([^\s\n])", r"\1 \2", testo)
    return testo.strip()

def frasi(testo):
    parti = re.split(r"(?<=[.!?])\s+|\n+", testo)
    return [p.strip(" -•\t") for p in parti if len(p.strip()) >= 35]

def parole(testo):
    return re.findall(r"[A-Za-zÀ-ÿ0-9]{4,}", testo.lower())

def parole_chiave(testo, n=20):
    token = [p for p in parole(testo) if p not in STOPWORDS and not p.isdigit()]
    return Counter(token).most_common(n)

def riassunto(testo, n=8):
    fs = frasi(testo)
    if not fs:
        return "- Testo insufficiente per creare un riassunto."
    pesi = dict(parole_chiave(testo, 40))
    valutate = []
    for i, f in enumerate(fs):
        score = sum(pesi.get(p, 0) for p in parole(f)) + max(0, 5 - i * 0.05)
        valutate.append((score, i, f))
    scelte = sorted(sorted(valutate, reverse=True)[:n], key=lambda x: x[1])
    return "\n".join(f"- {f}" for _, _, f in scelte)

def risposta_domanda(testo, domanda):
    if not domanda:
        return "Nessuna domanda specifica inserita."
    q = set(p for p in parole(domanda) if p not in STOPWORDS)
    risultati = []
    for f in frasi(testo):
        score = len(q & set(parole(f)))
        if score:
            risultati.append((score, f))
    if not risultati:
        return "Non ho trovato nel documento una risposta abbastanza collegata alla domanda."
    risultati.sort(reverse=True, key=lambda x: x[0])
    return "Risposta basata sui passaggi più pertinenti del documento:\n\n" + "\n".join(f"- {f}" for _, f in risultati[:5])

def report(testo, titolo):
    rischi = []
    parole_rischio = ["rischio", "errore", "problema", "sicurezza", "password", "accesso", "privacy", "phishing", "malware", "incidente"]
    for f in frasi(testo):
        if any(p in f.lower() for p in parole_rischio):
            rischi.append(f)
    if not rischi:
        rischi = ["Il documento non evidenzia rischi espliciti con parole chiave standard."]
    kw = parole_chiave(testo, 15)
    return f"""# Report aziendale - {titolo}

Generato il: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Sintesi operativa

{riassunto(testo)}

## Parole chiave principali

{chr(10).join(f"- {k}: {v}" for k, v in kw)}

## Rischi o criticità individuate

{chr(10).join(f"- {r}" for r in rischi[:8])}

## Azioni consigliate

- Trasformare i punti principali in una checklist.
- Creare un test di verifica.
- Preparare card formative.
- Usare le slide generate come base per una presentazione.
- Fare revisione umana finale prima dell'uso aziendale.
"""

def statistiche(testo):
    return {
        "caratteri": len(testo),
        "parole_stimate": len(parole(testo)),
        "frasi_utili": len(frasi(testo)),
        "parole_chiave": [{"termine": k, "occorrenze": v} for k, v in parole_chiave(testo, 20)]
    }

def grafico_svg(stats):
    dati = stats["parole_chiave"][:10]
    massimo = max([d["occorrenze"] for d in dati] or [1])
    h = 120 + len(dati) * 42
    righe = []
    y = 80
    for d in dati:
        w = int((d["occorrenze"] / massimo) * 600)
        label = html.escape(d["termine"])
        righe.append(f'<text x="30" y="{y+20}" font-size="16">{label}</text><rect x="220" y="{y}" width="{w}" height="26" rx="8"/><text x="{230+w}" y="{y+20}" font-size="14">{d["occorrenze"]}</text>')
        y += 42
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}"><style>text{{font-family:Arial;fill:#172033}} rect{{fill:#5b6cff}}</style><rect width="900" height="{h}" fill="#f5f7ff"/><text x="30" y="42" font-size="24" font-weight="700">Parole chiave principali</text>{"".join(righe)}</svg>'

def crea_card(testo):
    fs = frasi(testo)
    cards = []
    for i, (k, _) in enumerate(parole_chiave(testo, 10), 1):
        collegata = next((f for f in fs if k in f.lower()), f"Concetto collegato a {k}.")
        cards.append({
            "id": f"CARD-{i:03d}",
            "titolo": k.capitalize(),
            "spiegazione": collegata,
            "azione_pratica": "Trasforma questo concetto in una regola operativa."
        })
    return cards

def crea_slide(testo):
    fs = frasi(testo)
    slide = []
    for i, (k, _) in enumerate(parole_chiave(testo, 8), 1):
        punti = [f for f in fs if k in f.lower()][:3] or [f"Concetto principale: {k}"]
        slide.append({
            "id": f"SLIDE-{i:03d}",
            "titolo": k.capitalize(),
            "punti": punti,
            "note_relatore": f"Spiegare perché il concetto '{k}' è importante nel documento."
        })
    return slide

def html_cards(cards, titolo):
    blocchi = []
    for c in cards:
        blocchi.append(f'<article><h2>{html.escape(c["titolo"])}</h2><p>{html.escape(c["spiegazione"])}</p><strong>Azione pratica:</strong><p>{html.escape(c["azione_pratica"])}</p></article>')
    return f'<!doctype html><html lang="it"><meta charset="utf-8"><title>Card - {html.escape(titolo)}</title><style>body{{font-family:Arial;background:#f4f7fb;margin:0;padding:30px}}article{{background:white;border-radius:20px;padding:22px;margin:18px;box-shadow:0 10px 30px #0001}}</style><h1>Card formative - {html.escape(titolo)}</h1>{"".join(blocchi)}</html>'

def html_slide(slides, titolo):
    blocchi = []
    for s in slides:
        punti = "".join(f"<li>{html.escape(p)}</li>" for p in s["punti"])
        blocchi.append(f'<section><p>{s["id"]}</p><h2>{html.escape(s["titolo"])}</h2><ul>{punti}</ul><p><em>{html.escape(s["note_relatore"])}</em></p></section>')
    return f'<!doctype html><html lang="it"><meta charset="utf-8"><title>Slide - {html.escape(titolo)}</title><style>body{{font-family:Arial;background:#101628;color:white;margin:0;padding:30px}}section{{background:#172033;border-radius:28px;padding:30px;margin:22px}}</style><h1>Slide generate - {html.escape(titolo)}</h1>{"".join(blocchi)}</html>'

def crea_quiz(testo, titolo, materia, difficolta, numero):
    fs = frasi(testo)[:numero]
    quiz = []
    for i, f in enumerate(fs, 1):
        corretta = f
        opzioni = [
            corretta,
            "È corretto ignorare questo punto quando il lavoro sembra urgente.",
            "La procedura può essere applicata solo dopo che si verifica un problema.",
            "Il controllo può essere sostituito da una valutazione rapida senza verifica."
        ]
        quiz.append({
            "id": f"RAG-{i:04d}",
            "categoria": materia,
            "livello": difficolta,
            "domanda": "Secondo il documento, quale affermazione è corretta?",
            "opzioni": opzioni,
            "risposta_corretta": corretta,
            "spiegazione": "La risposta corretta riprende il contenuto del documento. Le altre opzioni cambiano un dettaglio operativo o logico.",
            "fonte": titolo
        })
    return quiz

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--titolo", default=None)
    parser.add_argument("--materia", default="documenti")
    parser.add_argument("--difficolta", default="intermedio")
    parser.add_argument("--domande", type=int, default=10)
    parser.add_argument("--tema", default="aziendale-blu")
    parser.add_argument("--domanda", default="")
    parser.add_argument("--output", default="all")
    args = parser.parse_args()

    file = Path(args.file)
    titolo = args.titolo or file.stem.replace("_", " ").replace("-", " ").title()
    slug = re.sub(r"[^a-z0-9]+", "-", titolo.lower()).strip("-") or "documento"
    out = Path("dist/rag_aziendale") / slug
    out.mkdir(parents=True, exist_ok=True)

    testo = leggi_file(file)
    corretto = pulisci(testo)

    (out / "testo_estratto.md").write_text(testo, encoding="utf-8")
    (out / "documento_corretto.md").write_text(corretto, encoding="utf-8")
    (out / "riassunto.md").write_text("# Riassunto\n\n" + riassunto(corretto), encoding="utf-8")
    (out / "report.md").write_text(report(corretto, titolo), encoding="utf-8")
    (out / "risposta_domanda.md").write_text("# Risposta domanda\n\n" + risposta_domanda(corretto, args.domanda), encoding="utf-8")

    stats = statistiche(corretto)
    (out / "statistiche.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "grafico_parole_chiave.svg").write_text(grafico_svg(stats), encoding="utf-8")

    cards = crea_card(corretto)
    slides = crea_slide(corretto)
    quiz = crea_quiz(corretto, titolo, args.materia, args.difficolta, args.domande)

    (out / "cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "cards.html").write_text(html_cards(cards, titolo), encoding="utf-8")
    (out / "slides.json").write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "slides.html").write_text(html_slide(slides, titolo), encoding="utf-8")
    (out / "quiz_rag.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")

    (out / "README_OUTPUT.md").write_text(f"# Output RAG\n\nTitolo: {titolo}\nTema: {args.tema}\n", encoding="utf-8")

    print("✅ Motore RAG documenti aziendali completato")
    print(f"📁 Output: {out}")

if __name__ == "__main__":
    main()
