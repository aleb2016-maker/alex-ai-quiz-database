#!/usr/bin/env python3
from pathlib import Path
import argparse
import textwrap

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"OK scritto: {path}")

ADAPTER = r"""
#!/usr/bin/env python3
# RAG Documento Studio V4.4
# Obiettivo: documento grande -> riassunto, card studio, indice Q/A.
# Non genera quiz. Riusa i controlli qualità già presenti quando disponibili.

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
GENERATED = ROOT / "dist" / "generated"

STOPWORDS = {
    "il","lo","la","i","gli","le","un","una","uno","di","a","da","in","con","su","per","tra","fra",
    "che","e","o","ma","anche","come","più","meno","molto","nel","nella","nelle","nei","del","della",
    "delle","dei","al","alla","alle","ai","si","non","sono","essere","può","possono","deve","devono",
    "usare","fare","viene","vengono","questo","questa","questi","quelle","quelli","ogni","quando",
    "dopo","prima","sul","sulla","dati","informazioni", "documento"
}

BAD_CHARS = ["þ", "ÿ", "\ufffd"]
BAD_TITLES = {"deve", "devono", "usare", "fare", "dati", "sicurezza", "account", "cosa", "parte"}

def normalizza_testo(testo: str) -> str:
    testo = testo.replace("\r\n", "\n").replace("\r", "\n")
    testo = testo.replace("“", '"').replace("”", '"').replace("’", "'")
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    testo = re.sub(r" +([,.;:!?])", r"\1", testo)
    testo = re.sub(r"([,.;:!?])([A-Za-zÀ-ÿ])", r"\1 \2", testo)
    return testo.strip()

def iter_chunks_da_file(percorso: Path, target_chars: int = 2200, max_chunks: int = 120) -> Iterable[str]:
    buffer = []
    size = 0
    count = 0
    with percorso.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = normalizza_testo(raw)
            if not line:
                continue
            buffer.append(line)
            size += len(line) + 1
            if size >= target_chars:
                chunk = normalizza_testo(" ".join(buffer))
                if chunk:
                    yield chunk
                    count += 1
                buffer, size = [], 0
                if count >= max_chunks:
                    break
    if buffer and count < max_chunks:
        yield normalizza_testo(" ".join(buffer))

def frasi(testo: str) -> list[str]:
    pezzi = re.split(r"(?<=[.!?])\s+", testo)
    pulite = []
    for p in pezzi:
        p = normalizza_testo(p)
        if len(p.split()) >= 6:
            if not p.endswith((".", "!", "?")):
                p += "."
            pulite.append(p)
    return pulite

def tokenizza(testo: str) -> list[str]:
    return [
        t.lower()
        for t in re.findall(r"[A-Za-zÀ-ÿ0-9]{3,}", testo)
        if t.lower() not in STOPWORDS and not t.isdigit()
    ]

def parole_chiave(chunks: list[str], limite: int = 18) -> list[str]:
    c = Counter()
    for chunk in chunks:
        c.update(tokenizza(chunk))
    return [w for w, _ in c.most_common(limite) if w not in BAD_TITLES]

def scegli_frasi_chiave(chunks: list[str], keywords: list[str], limite: int = 10) -> list[str]:
    tutte = []
    kw = set(keywords)
    for chunk in chunks:
        for s in frasi(chunk):
            score = sum(1 for t in tokenizza(s) if t in kw)
            if score:
                tutte.append((score, len(s), s))
    tutte.sort(key=lambda x: (-x[0], x[1]))
    viste = set()
    out = []
    for _, _, s in tutte:
        sig = s.lower()[:90]
        if sig in viste:
            continue
        viste.add(sig)
        out.append(s)
        if len(out) >= limite:
            break
    return out

def titolo_da_keyword(k: str) -> str:
    k = k.replace("_", " ").strip()
    if not k or k.lower() in BAD_TITLES:
        return ""
    return k[:1].upper() + k[1:]

def sentence_for_keyword(chunks: list[str], keyword: str) -> str:
    key = keyword.lower()
    best = ""
    for chunk in chunks:
        for s in frasi(chunk):
            if key in s.lower():
                if not best or len(s) < len(best):
                    best = s
    return best

def crea_riassunto(chunks: list[str], titolo: str) -> dict:
    keys = parole_chiave(chunks, 16)
    frasi_top = scegli_frasi_chiave(chunks, keys, 12)
    punti = frasi_top[:7]
    dettagli = frasi_top[7:12] or frasi_top[:4]
    return {
        "titolo": titolo or "Riassunto del documento",
        "panoramica": "Il documento viene sintetizzato individuando i concetti più ricorrenti e i passaggi più informativi.",
        "punti_chiave": punti,
        "dettagli_utili": dettagli,
        "parole_chiave": keys,
    }

def crea_cards(chunks: list[str], max_cards: int = 10) -> list[dict]:
    keys = parole_chiave(chunks, max_cards * 2)
    cards = []
    for key in keys:
        titolo = titolo_da_keyword(key)
        if not titolo:
            continue
        frase = sentence_for_keyword(chunks, key)
        if not frase:
            continue
        cards.append({
            "titolo": titolo,
            "fronte": f"Concetto chiave: {titolo}",
            "retro": frase,
            "spiegazione": frase,
            "uso": "Ripassa il concetto e collegalo a un esempio concreto presente nel documento.",
            "tags": [key],
            "origine": "documento",
        })
        if len(cards) >= max_cards:
            break
    return cards

def crea_indice_qa(chunks: list[str]) -> list[dict]:
    indice = []
    for i, chunk in enumerate(chunks, start=1):
        indice.append({
            "id": f"chunk-{i:03d}",
            "testo": chunk,
            "keywords": parole_chiave([chunk], 10),
        })
    return indice

def controlli_linguistici(payload: dict) -> list[str]:
    avvisi = []
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from qualita_linguistica import controlla_lingua_testo
    except Exception as exc:
        return [f"Controllo linguistico non importato: {exc}"]

    testi = []
    riassunto = payload.get("riassunto", {})
    testi.extend(riassunto.get("punti_chiave", []))
    testi.extend(riassunto.get("dettagli_utili", []))
    for c in payload.get("cards", []):
        testi.append(c.get("titolo", ""))
        testi.append(c.get("spiegazione", ""))

    for i, testo in enumerate(testi, start=1):
        try:
            risultato = controlla_lingua_testo(testo, f"rag_documento_studio_v44_{i}")
            if risultato:
                avvisi.append(f"Testo {i}: {risultato}")
        except Exception as exc:
            avvisi.append(f"Testo {i}: controllo non eseguito: {exc}")
    return avvisi

def valida_payload(payload: dict) -> list[str]:
    problemi = []
    blob = json.dumps(payload, ensure_ascii=False)
    for ch in BAD_CHARS:
        if ch in blob:
            problemi.append(f"Simbolo corrotto trovato: {ch}")
    if not payload.get("chunks"):
        problemi.append("Nessun chunk generato.")
    if len(payload.get("riassunto", {}).get("punti_chiave", [])) < 3:
        problemi.append("Riassunto troppo debole: meno di 3 punti chiave.")
    if len(payload.get("cards", [])) < 4:
        problemi.append("Troppe poche card generate.")
    for i, card in enumerate(payload.get("cards", []), start=1):
        titolo = str(card.get("titolo", "")).strip().lower()
        if not titolo or titolo in BAD_TITLES:
            problemi.append(f"Card {i}: titolo debole o generico: {titolo}")
        if len(str(card.get("spiegazione", "")).split()) < 8:
            problemi.append(f"Card {i}: spiegazione troppo corta.")
    return problemi

def main() -> None:
    parser = argparse.ArgumentParser(description="Documento grande -> riassunto, card, indice Q/A.")
    parser.add_argument("--documento", required=True, help="File TXT/MD già estratto o scritto in UTF-8.")
    parser.add_argument("--titolo", default="Documento di studio")
    parser.add_argument("--max-chunks", type=int, default=120)
    parser.add_argument("--max-cards", type=int, default=10)
    parser.add_argument("--output", default="dist/generated/rag_documento_studio_v44.json")
    args = parser.parse_args()

    documento = Path(args.documento)
    if not documento.exists():
        raise SystemExit(f"ERRORE: documento non trovato: {documento}")

    chunks = list(iter_chunks_da_file(documento, max_chunks=args.max_chunks))
    payload = {
        "versione": "rag_documento_studio_v44",
        "titolo": args.titolo,
        "documento_origine": str(documento),
        "modalita": ["riassunto", "card", "interroga_documento"],
        "chunks": chunks,
        "riassunto": crea_riassunto(chunks, args.titolo),
        "cards": crea_cards(chunks, args.max_cards),
        "qa_index": crea_indice_qa(chunks),
        "qualita": {
            "regola": "riusa_motori_qualita_esistenti",
            "avvisi_linguistici": [],
            "problemi_bloccanti": [],
        }
    }

    payload["qualita"]["avvisi_linguistici"] = controlli_linguistici(payload)
    payload["qualita"]["problemi_bloccanti"] = valida_payload(payload)

    out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORTS.mkdir(exist_ok=True)
    report = REPORTS / "rag_documento_studio_v44.md"
    report.write_text(
        "# RAG Documento Studio V4.4\n\n"
        f"- Documento: `{documento}`\n"
        f"- Output: `{out}`\n"
        f"- Chunk: {len(chunks)}\n"
        f"- Card: {len(payload['cards'])}\n"
        f"- Punti riassunto: {len(payload['riassunto']['punti_chiave'])}\n"
        f"- Avvisi linguistici: {len(payload['qualita']['avvisi_linguistici'])}\n"
        f"- Problemi bloccanti: {len(payload['qualita']['problemi_bloccanti'])}\n",
        encoding="utf-8"
    )

    if payload["qualita"]["problemi_bloccanti"]:
        print("ERRORE: problemi bloccanti nel documento studio")
        for p in payload["qualita"]["problemi_bloccanti"]:
            print("-", p)
        raise SystemExit(1)

    print("=== RAG Documento Studio V4.4 ===")
    print(f"Chunk: {len(chunks)}")
    print(f"Card: {len(payload['cards'])}")
    print(f"Output: {out}")
    print(f"Report: {report}")
    print("OK: riassunto/card/indice Q&A generati senza problemi bloccanti.")

if __name__ == "__main__":
    main()
"""

VERIFIER = r"""
#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def ok(msg: str) -> None:
    print("OK -", msg)

def err(msg: str, errors: list[str]) -> None:
    print("ERRORE -", msg)
    errors.append(msg)

def contains(path: Path, text: str) -> bool:
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")

def main() -> None:
    errors = []
    print("=== Verifica RAG Documento Studio V4.4 ===")

    files = [
        ROOT / "scripts/rag_adapter_documento_studio_v44.py",
        ROOT / "scripts/verifica_rag_documento_studio_v44.py",
        ROOT / "demo-rag/test-rag-documento-studio-v44.html",
        ROOT / "demo-rag/rag-documento-studio-v44.css",
        ROOT / "demo-rag/rag-documento-studio-v44.js",
        ROOT / "docs/RAG_DOCUMENTO_STUDIO_V44.md",
    ]
    for f in files:
        if f.exists():
            ok(f"presente {f.relative_to(ROOT)}")
        else:
            err(f"manca {f.relative_to(ROOT)}", errors)

    js = ROOT / "demo-rag/rag-documento-studio-v44.js"
    html = ROOT / "demo-rag/test-rag-documento-studio-v44.html"

    if contains(js, "window.print"):
        err("JS non deve usare window.print", errors)
    else:
        ok("nessun window.print")

    if contains(js, "AlexBrowserPdfExportV6.exportSectionsToPdf"):
        ok("PDF collegato a PDF browser V6")
    else:
        err("PDF V6 non collegato", errors)

    if contains(js, "RagCardGraphicEngine.renderGraphicCard") and contains(js, "RagCardGraphicEngine.buildCardObject"):
        ok("Card collegate al motore card esistente")
    else:
        err("motore card grafico non collegato", errors)

    if contains(html, "/runtime/web/card-graphic-engine.js"):
        ok("HTML carica runtime/web/card-graphic-engine.js")
    else:
        err("HTML non carica card engine runtime", errors)

    if contains(html, "/demo-rag/pdf-export-browser-v6.js"):
        ok("HTML carica pdf-export-browser-v6.js")
    else:
        err("HTML non carica PDF V6", errors)

    output = ROOT / "dist/generated/rag_documento_studio_v44.json"
    if output.exists():
        data = json.loads(output.read_text(encoding="utf-8"))
        for key in ["chunks", "riassunto", "cards", "qa_index", "qualita"]:
            if key in data:
                ok(f"output JSON contiene {key}")
            else:
                err(f"output JSON manca {key}", errors)
        blob = json.dumps(data, ensure_ascii=False)
        for bad in ["þ", "ÿ", "\\\\n"]:
            if bad in blob:
                err(f"output contiene simbolo/testo vietato: {bad}", errors)
        if len(data.get("cards", [])) < 4:
            err("output ha meno di 4 card", errors)
        if len(data.get("riassunto", {}).get("punti_chiave", [])) < 3:
            err("riassunto troppo povero", errors)
    else:
        print("AVVISO - output dist/generated/rag_documento_studio_v44.json non ancora generato")

    # Riusa validatori card già presenti, se disponibili.
    for validator in ["scripts/validatore_card_grafiche_completo.py", "scripts/validatore_concetti_card.py"]:
        p = ROOT / validator
        if p.exists():
            result = subprocess.run([sys.executable, str(p)], cwd=ROOT)
            if result.returncode == 0:
                ok(f"validatore esistente passato: {validator}")
            else:
                err(f"validatore esistente fallito: {validator}", errors)

    if errors:
        raise SystemExit(1)
    print("Verifica completata.")

if __name__ == "__main__":
    main()
"""

HTML = r"""
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG Documento Studio V4.4</title>
  <link rel="stylesheet" href="/demo-rag/rag-documento-studio-v44.css">
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">RAG DOCUMENTO STUDIO V4.4</p>
      <h1>Riassunti, card e interrogazione documento</h1>
      <p class="sub">
        Motore per testi grandi: prima genera dati puliti, poi mostra riassunto, card colorate e risposte dal documento.
      </p>
    </header>

    <section class="panel controls">
      <div class="row">
        <button id="btnLoadGenerated" class="primary">Carica JSON generato</button>
        <button id="btnAnalyzeText" class="secondary">Analizza testo incollato</button>
        <button id="btnQuality" class="secondary">Controlla output</button>
        <button id="btnPdf" class="primary">Scarica PDF V6 pulito</button>
      </div>
      <label class="file-label">
        Carica TXT/MD
        <input id="fileInput" type="file" accept=".txt,.md,text/plain,text/markdown">
      </label>
      <textarea id="textInput" placeholder="Incolla qui un documento lungo oppure usa il JSON generato dallo script Python..."></textarea>
      <div id="status" class="status">Pronto.</div>
    </section>

    <section id="summarySection" class="panel pdf-export-group rag-v44-export-section">
      <h2>Riassunto strutturato</h2>
      <div id="summaryOutput" class="summary-grid muted">Nessun riassunto caricato.</div>
    </section>

    <section id="cardsSection" class="panel pdf-export-group rag-v44-export-section">
      <h2>Card studio</h2>
      <div id="cardsOutput" class="cards-grid muted">Nessuna card generata.</div>
    </section>

    <section id="askSection" class="panel no-pdf">
      <h2>Interroga il documento</h2>
      <p class="hint">Fai una domanda sul documento. Il motore cerca i passaggi più pertinenti e risponde solo con quello che trova nel testo.</p>
      <div class="ask-row">
        <input id="questionInput" type="text" placeholder="Esempio: perché sono importanti i backup?">
        <button id="btnAsk" class="primary">Rispondi</button>
      </div>
      <div id="answerOutput" class="answer-box">Nessuna domanda fatta.</div>
    </section>

    <section id="qualitySection" class="panel no-pdf">
      <h2>Controllo automatico</h2>
      <pre id="qualityOutput">Non eseguito.</pre>
    </section>
  </main>

  <script src="/runtime/web/card-graphic-engine.js"></script>
  <script src="/demo-rag/pdf-export-browser-v6.js"></script>
  <script src="/demo-rag/rag-documento-studio-v44.js"></script>
</body>
</html>
"""

CSS = r"""
:root {
  color-scheme: dark;
  --bg: #090d16;
  --panel: rgba(16, 24, 40, 0.92);
  --panel2: rgba(21, 34, 56, 0.88);
  --text: #eef6ff;
  --muted: #a9b8ce;
  --line: rgba(255,255,255,0.12);
  --accent: #49e6a1;
  --accent2: #4fb3ff;
  --danger: #ff6b6b;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background:
    radial-gradient(circle at 15% 10%, rgba(79,179,255,.22), transparent 30%),
    radial-gradient(circle at 80% 0%, rgba(73,230,161,.18), transparent 35%),
    var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.page {
  width: min(1180px, calc(100% - 28px));
  margin: 0 auto;
  padding: 28px 0 60px;
}

.hero, .panel {
  border: 1px solid var(--line);
  background: linear-gradient(145deg, rgba(20,30,52,.95), rgba(8,13,24,.94));
  border-radius: 24px;
  box-shadow: 0 22px 70px rgba(0,0,0,.28);
}

.hero {
  padding: 34px;
  margin-bottom: 18px;
}

.eyebrow {
  color: var(--accent);
  font-weight: 900;
  letter-spacing: .14em;
  font-size: .8rem;
}

h1, h2 { margin: 0 0 12px; }
h1 { font-size: clamp(2rem, 5vw, 4.2rem); line-height: .98; }
h2 { font-size: 1.55rem; }

.sub, .hint, .muted { color: var(--muted); }

.panel {
  padding: 22px;
  margin: 18px 0;
}

.row, .ask-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

button, .file-label {
  appearance: none;
  border: 0;
  color: #06111d;
  font-weight: 900;
  border-radius: 16px;
  padding: 14px 18px;
  cursor: pointer;
  transition: transform .15s ease, filter .15s ease;
}

button:hover, .file-label:hover { transform: translateY(-1px); filter: brightness(1.06); }

.primary {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
}

.secondary, .file-label {
  background: rgba(255,255,255,.11);
  color: var(--text);
  border: 1px solid var(--line);
}

.file-label input { display: none; }

textarea, input[type="text"] {
  width: 100%;
  border: 1px solid var(--line);
  background: rgba(3,7,14,.72);
  color: var(--text);
  border-radius: 18px;
  padding: 16px;
  outline: none;
  font: inherit;
}

textarea {
  min-height: 220px;
  margin-top: 14px;
  resize: vertical;
}

.ask-row input { flex: 1 1 360px; }

.status, .answer-box, pre {
  margin-top: 14px;
  padding: 14px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.06);
  border-radius: 16px;
  white-space: pre-wrap;
}

.summary-grid {
  display: grid;
  gap: 14px;
}

.summary-card {
  border: 1px solid var(--line);
  background: var(--panel2);
  padding: 18px;
  border-radius: 18px;
}

.summary-card ul {
  margin: 8px 0 0;
  padding-left: 20px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.cards-grid .rag-graphic-card,
.cards-grid .learning-card,
.cards-grid article {
  min-height: 280px;
  overflow: hidden;
}

.answer-source {
  margin-top: 10px;
  color: var(--muted);
  font-size: .92rem;
}

.error { color: var(--danger); }

@media print {
  body { background: #090d16 !important; }
  .no-pdf, .controls { display: none !important; }
  .panel { break-inside: avoid; }
}
"""

JS = r"""
(function () {
  let currentData = null;

  const $ = (id) => document.getElementById(id);

  function setStatus(message, isError = false) {
    $("status").textContent = message;
    $("status").classList.toggle("error", !!isError);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function normalizeText(text) {
    return String(text || "")
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .replace(/ +([,.;:!?])/g, "$1")
      .replace(/([,.;:!?])([A-Za-zÀ-ÿ])/g, "$1 $2")
      .trim();
  }

  const stopwords = new Set([
    "il","lo","la","gli","le","una","uno","con","per","tra","fra","che","non","sono","essere",
    "deve","devono","usare","fare","dati","documento","questo","questa","anche","come","della",
    "delle","degli","nelle","nella","sulla","sugli","più","meno","molto","quando"
  ]);

  function tokens(text) {
    return (String(text || "").toLowerCase().match(/[a-zà-ÿ0-9]{3,}/g) || [])
      .filter((t) => !stopwords.has(t) && !/^\d+$/.test(t));
  }

  function splitChunks(text, size = 2200) {
    const clean = normalizeText(text);
    const paragraphs = clean.split(/\n+/).filter(Boolean);
    const chunks = [];
    let buffer = "";
    for (const p of paragraphs) {
      if ((buffer + " " + p).length > size && buffer) {
        chunks.push(buffer.trim());
        buffer = p;
      } else {
        buffer += (buffer ? " " : "") + p;
      }
    }
    if (buffer.trim()) chunks.push(buffer.trim());
    return chunks.slice(0, 120);
  }

  function sentences(text) {
    return normalizeText(text)
      .split(/(?<=[.!?])\s+/)
      .map((s) => s.trim())
      .filter((s) => s.split(/\s+/).length >= 6);
  }

  function topKeywords(chunks, limit = 16) {
    const count = new Map();
    chunks.forEach((chunk) => {
      tokens(chunk).forEach((t) => count.set(t, (count.get(t) || 0) + 1));
    });
    return [...count.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([k]) => k)
      .filter((k) => !["deve", "devono", "usare", "fare", "dati", "account"].includes(k))
      .slice(0, limit);
  }

  function sentenceForKeyword(chunks, keyword) {
    const key = keyword.toLowerCase();
    let best = "";
    chunks.forEach((chunk) => {
      sentences(chunk).forEach((s) => {
        if (s.toLowerCase().includes(key) && (!best || s.length < best.length)) best = s;
      });
    });
    return best;
  }

  function buildDataFromText(text, title = "Documento di studio") {
    const chunks = splitChunks(text);
    const keywords = topKeywords(chunks, 16);
    const keySet = new Set(keywords);
    const scored = [];
    chunks.forEach((chunk) => {
      sentences(chunk).forEach((s) => {
        const score = tokens(s).filter((t) => keySet.has(t)).length;
        if (score > 0) scored.push({ score, text: s });
      });
    });
    scored.sort((a, b) => b.score - a.score || a.text.length - b.text.length);
    const seen = new Set();
    const selected = [];
    for (const item of scored) {
      const sig = item.text.toLowerCase().slice(0, 90);
      if (seen.has(sig)) continue;
      seen.add(sig);
      selected.push(item.text);
      if (selected.length >= 10) break;
    }

    const cards = [];
    for (const keyword of keywords) {
      const phrase = sentenceForKeyword(chunks, keyword);
      if (!phrase) continue;
      const titleCard = keyword.charAt(0).toUpperCase() + keyword.slice(1);
      cards.push({
        titolo: titleCard,
        fronte: "Concetto chiave: " + titleCard,
        retro: phrase,
        spiegazione: phrase,
        uso: "Collega questo concetto a un esempio concreto del documento.",
        tags: [keyword],
        origine: "documento"
      });
      if (cards.length >= 10) break;
    }

    return {
      versione: "rag_documento_studio_v44_browser",
      titolo: title,
      modalita: ["riassunto", "card", "interroga_documento"],
      chunks,
      riassunto: {
        titolo: title,
        panoramica: "Riassunto generato dai passaggi più informativi del documento.",
        punti_chiave: selected.slice(0, 7),
        dettagli_utili: selected.slice(7, 10),
        parole_chiave: keywords
      },
      cards,
      qa_index: chunks.map((chunk, i) => ({ id: "chunk-" + String(i + 1).padStart(3, "0"), testo: chunk, keywords: topKeywords([chunk], 8) })),
      qualita: { avvisi_linguistici: [], problemi_bloccanti: [] }
    };
  }

  function renderSummary(data) {
    const r = data.riassunto || {};
    $("summaryOutput").classList.remove("muted");
    $("summaryOutput").innerHTML = `
      <div class="summary-card">
        <h3>${escapeHtml(r.titolo || data.titolo || "Riassunto")}</h3>
        <p>${escapeHtml(r.panoramica || "")}</p>
      </div>
      <div class="summary-card">
        <h3>Punti chiave</h3>
        <ul>${(r.punti_chiave || []).map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
      </div>
      <div class="summary-card">
        <h3>Dettagli utili</h3>
        <ul>${(r.dettagli_utili || []).map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
      </div>
    `;
  }

  function renderCards(data) {
    if (!window.RagCardGraphicEngine) {
      throw new Error("Motore card grafico non caricato: runtime/web/card-graphic-engine.js");
    }
    const cards = data.cards || [];
    $("cardsOutput").classList.remove("muted");
    $("cardsOutput").innerHTML = cards.map((card, index) => {
      const row = {
        domanda: card.fronte || card.titolo,
        risposta_corretta: card.titolo,
        spiegazione: card.spiegazione || card.retro,
        tags: card.tags || [],
        categoria: "documento",
        sottocategoria: "studio"
      };
      const graphicCard = window.RagCardGraphicEngine.buildCardObject(row, index);
      graphicCard.titolo = card.titolo || graphicCard.titolo;
      graphicCard.fronte = card.fronte || graphicCard.fronte;
      graphicCard.retro = card.retro || card.spiegazione || graphicCard.retro;
      return window.RagCardGraphicEngine.renderGraphicCard(graphicCard, index);
    }).join("");
  }

  function runQuality(data) {
    const problems = [];
    const blob = JSON.stringify(data || {});
    ["þ", "ÿ", "\\n"].forEach((bad) => {
      if (blob.includes(bad)) problems.push("Simbolo/testo vietato trovato: " + bad);
    });
    if (!window.RagCardGraphicEngine) problems.push("Motore card grafico non caricato.");
    if (!window.AlexBrowserPdfExportV6) problems.push("Motore PDF V6 non caricato.");
    if (!data || !Array.isArray(data.chunks) || data.chunks.length === 0) problems.push("Nessun chunk documento.");
    if (!data.riassunto || (data.riassunto.punti_chiave || []).length < 3) problems.push("Riassunto troppo povero.");
    if (!Array.isArray(data.cards) || data.cards.length < 4) problems.push("Meno di 4 card.");
    (data.cards || []).forEach((card, i) => {
      const title = String(card.titolo || "").toLowerCase().trim();
      if (["deve", "devono", "usare", "fare", "dati", "account"].includes(title)) {
        problems.push(`Card ${i + 1}: titolo generico o sporco: ${title}`);
      }
      if (String(card.spiegazione || card.retro || "").split(/\s+/).length < 8) {
        problems.push(`Card ${i + 1}: testo troppo corto.`);
      }
    });

    $("qualityOutput").textContent = problems.length
      ? "ERRORE:\n- " + problems.join("\n- ")
      : "OK: output controllato.\n- testo senza simboli strani\n- riassunto presente\n- card presenti\n- motore card collegato\n- PDF V6 collegato";
    return problems;
  }

  function renderAll(data) {
    currentData = data;
    renderSummary(data);
    renderCards(data);
    runQuality(data);
    setStatus("Documento caricato: riassunto, card e indice Q/A pronti.");
  }

  async function loadGeneratedJson() {
    try {
      setStatus("Carico /dist/generated/rag_documento_studio_v44.json ...");
      const res = await fetch("/dist/generated/rag_documento_studio_v44.json?ts=" + Date.now());
      if (!res.ok) throw new Error("JSON non trovato. Prima esegui lo script Python adapter.");
      const data = await res.json();
      renderAll(data);
    } catch (err) {
      setStatus(err.message || String(err), true);
    }
  }

  function analyzeText() {
    const text = $("textInput").value;
    if (!normalizeText(text)) {
      setStatus("Incolla un testo o carica un file.", true);
      return;
    }
    renderAll(buildDataFromText(text));
  }

  function askDocument() {
    if (!currentData) {
      $("answerOutput").textContent = "Prima carica o analizza un documento.";
      return;
    }
    const question = $("questionInput").value.trim();
    if (!question) {
      $("answerOutput").textContent = "Scrivi una domanda.";
      return;
    }
    const qTokens = new Set(tokens(question));
    const scored = (currentData.qa_index || []).map((chunk) => {
      const chunkTokens = new Set([...(chunk.keywords || []), ...tokens(chunk.testo || "")]);
      let score = 0;
      qTokens.forEach((t) => { if (chunkTokens.has(t)) score += 1; });
      return { score, chunk };
    }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score);

    if (!scored.length) {
      $("answerOutput").innerHTML = "Non ho trovato nel documento un passaggio abbastanza pertinente per rispondere con sicurezza.";
      return;
    }

    const best = scored.slice(0, 2).map((x) => x.chunk);
    const answerSentences = [];
    best.forEach((chunk) => {
      sentences(chunk.testo).forEach((s) => {
        const score = tokens(s).filter((t) => qTokens.has(t)).length;
        if (score > 0) answerSentences.push({ score, text: s, id: chunk.id });
      });
    });
    answerSentences.sort((a, b) => b.score - a.score || a.text.length - b.text.length);
    const chosen = answerSentences.slice(0, 3);

    $("answerOutput").innerHTML = `
      <strong>Risposta dal documento:</strong>
      <p>${escapeHtml(chosen.map((x) => x.text).join(" "))}</p>
      <div class="answer-source">Fonti interne: ${best.map((x) => escapeHtml(x.id)).join(", ")}</div>
    `;
  }

  async function exportPdf() {
    if (!currentData) {
      setStatus("Prima carica o analizza un documento.", true);
      return;
    }
    const problems = runQuality(currentData);
    if (problems.length) {
      setStatus("PDF bloccato: correggi prima gli errori del controllo output.", true);
      return;
    }
    if (!window.AlexBrowserPdfExportV6 || !window.AlexBrowserPdfExportV6.exportSectionsToPdf) {
      setStatus("Motore PDF V6 non disponibile.", true);
      return;
    }
    setStatus("Genero PDF V6 pulito...");
    await window.AlexBrowserPdfExportV6.exportSectionsToPdf({
      title: currentData.titolo || "RAG Documento Studio V4.4",
      filename: "rag-documento-studio-v44.pdf"
    });
    setStatus("PDF richiesto al motore V6.");
  }

  $("btnLoadGenerated").addEventListener("click", loadGeneratedJson);
  $("btnAnalyzeText").addEventListener("click", analyzeText);
  $("btnQuality").addEventListener("click", () => currentData ? runQuality(currentData) : setStatus("Nessun documento da controllare.", true));
  $("btnAsk").addEventListener("click", askDocument);
  $("btnPdf").addEventListener("click", exportPdf);

  $("fileInput").addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    const text = await file.text();
    $("textInput").value = text;
    setStatus("File caricato. Clicca Analizza testo incollato oppure usa l'adapter Python per output controllato.");
  });
})();
"""

DOC = r"""
# RAG Documento Studio V4.4

Questo blocco torna all'obiettivo corretto del motore RAG:

- testi grandi
- riassunti strutturati
- card colorate con disegni usando il motore card già creato
- sezione "Interroga il documento"
- PDF tramite `demo-rag/pdf-export-browser-v6.js`
- controlli automatici prima dell'output

Non è un blocco quiz. I motori quiz/qualità servono come qualità testuale e controllo, non come obiettivo principale.
"""

REPORT = r"""
# Report RAG Documento Studio V4.4

Stato installazione: pronto.

Motori riutilizzati:

- `scripts/qualita_linguistica.py`
- `runtime/web/card-graphic-engine.js`
- `demo-rag/pdf-export-browser-v6.js`
- `scripts/validatore_card_grafiche_completo.py`
- `scripts/validatore_concetti_card.py`

Output principale:

- `dist/generated/rag_documento_studio_v44.json`
"""

README = r"""
# Pacchetto RAG Documento Studio V4.4

Questo pacchetto NON aggiunge un nuovo motore quiz.

Aggiunge un blocco per:

- prendere testi grandi già estratti in TXT/MD
- generare riassunto
- generare card studio
- creare indice per "Interroga il documento"
- riusare card engine già creato
- riusare PDF browser V6 già creato
- usare controlli qualità già presenti dove possibile

## Installazione

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source backend/.venv/bin/activate

unzip ~/Downloads/rag_documento_studio_v44_pack.zip -d .

python3 scripts/installa_rag_documento_studio_v44.py --root .
```

## Genera JSON controllato

```bash
python3 scripts/rag_adapter_documento_studio_v44.py \
  --documento rag/documenti/documento_rag_sicurezza_informatica_aziendale.md \
  --titolo "Sicurezza informatica aziendale" \
  --max-cards 10 \
  --output dist/generated/rag_documento_studio_v44.json
```

## Verifica

```bash
python3 scripts/verifica_rag_documento_studio_v44.py
```

## Avvio pagina

```bash
python3 -m http.server 8000
```

URL:

```text
http://localhost:8000/demo-rag/test-rag-documento-studio-v44.html
```
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    write(root / "scripts/rag_adapter_documento_studio_v44.py", ADAPTER)
    write(root / "scripts/verifica_rag_documento_studio_v44.py", VERIFIER)
    write(root / "demo-rag/test-rag-documento-studio-v44.html", HTML)
    write(root / "demo-rag/rag-documento-studio-v44.css", CSS)
    write(root / "demo-rag/rag-documento-studio-v44.js", JS)
    write(root / "docs/RAG_DOCUMENTO_STUDIO_V44.md", DOC)
    write(root / "reports/rag_documento_studio_v44.md", REPORT)

    print()
    print("✅ RAG Documento Studio V4.4 installato")
    print("📌 Genera JSON:")
    print("   python3 scripts/rag_adapter_documento_studio_v44.py --documento rag/documenti/documento_rag_sicurezza_informatica_aziendale.md --titolo \"Sicurezza informatica aziendale\" --max-cards 10 --output dist/generated/rag_documento_studio_v44.json")
    print("🧪 Verifica:")
    print("   python3 scripts/verifica_rag_documento_studio_v44.py")
    print("🌐 URL:")
    print("   http://localhost:8000/demo-rag/test-rag-documento-studio-v44.html")

if __name__ == "__main__":
    main()
