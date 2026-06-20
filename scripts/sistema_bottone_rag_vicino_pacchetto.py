from pathlib import Path
import re

index_path = Path("demo/index.html")
style_path = Path("demo/style.css")
rag_page_path = Path("demo-rag/index.html")

for file_path in [index_path, style_path, rag_page_path]:
    if not file_path.exists():
        raise SystemExit(f"❌ File mancante: {file_path}")

index_html = index_path.read_text(encoding="utf-8")
style_css = style_path.read_text(encoding="utf-8")

rag_button = """
<!-- RAG_PACKAGE_BUTTON_START -->
<a class="rag-package-button" href="../demo-rag/index.html" aria-label="Apri pacchetto RAG documenti">
  <span class="rag-package-icon">🧠</span>
  <span class="rag-package-text">
    <strong>Pacchetto RAG documenti</strong>
    <small>Riassunti · quiz · report · tabelle · card</small>
  </span>
</a>
<!-- RAG_PACKAGE_BUTTON_END -->
"""

# Rimuove eventuali versioni precedenti del bottone RAG marcato.
index_html = re.sub(
    r"\n?\s*<!-- RAG_PACKAGE_BUTTON_START -->.*?<!-- RAG_PACKAGE_BUTTON_END -->\s*\n?",
    "\n",
    index_html,
    flags=re.S,
)

# Rimuove il vecchio link semplice/azzurro verso demo-rag, se presente.
index_html = re.sub(
    r"\n\s*<p[^>]*>\s*<a[^>]*href=[\"'][^\"']*demo-rag[^\"']*[\"'][^>]*>.*?RAG.*?</a>\s*</p>\s*",
    "\n",
    index_html,
    flags=re.I | re.S,
)

index_html = re.sub(
    r"\n\s*<a[^>]*href=[\"'][^\"']*demo-rag[^\"']*[\"'][^>]*>.*?RAG.*?</a>\s*",
    "\n",
    index_html,
    flags=re.I | re.S,
)

# Cerca il bottone/link del pacchetto personalizzato e inserisce subito dopo il bottone RAG.
pattern_personalizzato = re.compile(
    r"(<a\b[^>]*>[\s\S]{0,900}?(?:pacchetto\s+personalizzato|personalizzato)[\s\S]{0,900}?</a>)",
    flags=re.I,
)

match = pattern_personalizzato.search(index_html)

if not match:
    raise SystemExit(
        "❌ Non ho trovato il bottone/link del pacchetto personalizzato in demo/index.html. "
        "Controlla il testo del bottone rosso."
    )

index_html = (
    index_html[:match.end()]
    + "\n"
    + rag_button
    + index_html[match.end():]
)

index_path.write_text(index_html, encoding="utf-8")

# Aggiorna lo stile del bottone senza toccare i pulsanti già esistenti.
style_css = re.sub(
    r"\n?/\* RAG_PACKAGE_BUTTON_STYLE_START \*/.*?/\* RAG_PACKAGE_BUTTON_STYLE_END \*/\s*\n?",
    "\n",
    style_css,
    flags=re.S,
)

style_css += """
/* RAG_PACKAGE_BUTTON_STYLE_START */

.rag-package-button {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-height: 58px;
  padding: 14px 20px;
  margin: 10px 8px;
  border-radius: 18px;
  text-decoration: none;
  color: #ffffff;
  background:
    radial-gradient(circle at top left, rgba(255,255,255,0.35), transparent 34%),
    linear-gradient(135deg, #00d4ff 0%, #7c3cff 48%, #00c875 100%);
  box-shadow: 0 14px 34px rgba(0, 212, 255, 0.22),
              0 10px 28px rgba(124, 60, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.28);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
  vertical-align: middle;
}

.rag-package-button:hover {
  transform: translateY(-3px) scale(1.02);
  filter: brightness(1.08);
  box-shadow: 0 18px 42px rgba(0, 212, 255, 0.32),
              0 14px 34px rgba(124, 60, 255, 0.35);
}

.rag-package-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  font-size: 25px;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: inset 0 0 18px rgba(255, 255, 255, 0.12);
}

.rag-package-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.rag-package-text strong {
  font-size: 1rem;
  letter-spacing: 0.02em;
}

.rag-package-text small {
  margin-top: 4px;
  font-size: 0.76rem;
  opacity: 0.9;
}

/* RAG_PACKAGE_BUTTON_STYLE_END */
"""

style_path.write_text(style_css, encoding="utf-8")

# Ricrea la pagina demo-rag con le opzioni chiare del pacchetto.
rag_page_html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pacchetto RAG documenti</title>
  <style>
    :root {
      --bg: #07111f;
      --panel: rgba(255,255,255,0.08);
      --panel2: rgba(255,255,255,0.12);
      --text: #f3f7ff;
      --muted: #b8c7dd;
      --cyan: #00d4ff;
      --violet: #7c3cff;
      --green: #00c875;
      --orange: #ff8a3d;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(0,212,255,0.22), transparent 32%),
        radial-gradient(circle at top right, rgba(124,60,255,0.22), transparent 34%),
        linear-gradient(180deg, #07111f 0%, #0b1020 100%);
      min-height: 100vh;
    }

    .page {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 56px;
    }

    .top-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 28px;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      min-height: 48px;
      padding: 12px 18px;
      border-radius: 15px;
      color: white;
      text-decoration: none;
      font-weight: 800;
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(255,255,255,0.1);
    }

    .btn-download {
      background: linear-gradient(135deg, var(--cyan), var(--violet), var(--green));
      box-shadow: 0 15px 32px rgba(0, 212, 255, 0.22);
    }

    .btn-back {
      background: rgba(255,255,255,0.1);
    }

    .hero {
      padding: 34px;
      border-radius: 30px;
      background:
        linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,60,255,0.16)),
        rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.16);
      box-shadow: 0 24px 60px rgba(0,0,0,0.32);
    }

    .badge {
      display: inline-flex;
      padding: 8px 13px;
      border-radius: 999px;
      font-size: 0.83rem;
      font-weight: 900;
      color: #06111f;
      background: linear-gradient(135deg, var(--cyan), var(--green));
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.2rem, 6vw, 4.4rem);
      line-height: 0.95;
      letter-spacing: -0.06em;
    }

    .subtitle {
      max-width: 860px;
      color: var(--muted);
      font-size: 1.12rem;
      line-height: 1.7;
      margin: 18px 0 0;
    }

    .section-title {
      margin: 38px 0 16px;
      font-size: 1.7rem;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }

    .card {
      min-height: 190px;
      padding: 22px;
      border-radius: 24px;
      background: var(--panel);
      border: 1px solid rgba(255,255,255,0.14);
      box-shadow: 0 14px 35px rgba(0,0,0,0.22);
    }

    .card strong {
      display: block;
      font-size: 1.13rem;
      margin: 12px 0 9px;
    }

    .card p {
      color: var(--muted);
      line-height: 1.55;
      margin: 0;
    }

    .icon {
      display: inline-flex;
      width: 44px;
      height: 44px;
      align-items: center;
      justify-content: center;
      border-radius: 16px;
      font-size: 1.45rem;
      background: linear-gradient(135deg, rgba(0,212,255,0.24), rgba(124,60,255,0.28));
    }

    .workflow {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
    }

    .step {
      padding: 18px;
      border-radius: 20px;
      background: var(--panel2);
      border: 1px solid rgba(255,255,255,0.12);
      color: var(--muted);
      line-height: 1.5;
    }

    .step b {
      display: block;
      color: white;
      margin-bottom: 6px;
    }

    .command {
      margin-top: 18px;
      padding: 18px;
      border-radius: 18px;
      overflow-x: auto;
      background: rgba(0,0,0,0.38);
      border: 1px solid rgba(255,255,255,0.12);
      color: #dffaff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.9rem;
      line-height: 1.6;
    }

    @media (max-width: 900px) {
      .grid,
      .workflow {
        grid-template-columns: 1fr;
      }

      .hero {
        padding: 24px;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <div class="top-actions">
      <a class="btn btn-back" href="../demo/index.html">← Torna alla demo principale</a>
      <a class="btn btn-download" href="../downloads/pacchetto-rag-riutilizzabile.zip">⬇️ Scarica pacchetto RAG riutilizzabile</a>
    </div>

    <section class="hero">
      <span class="badge">Motore RAG riutilizzabile</span>
      <h1>Pacchetto RAG documenti</h1>
      <p class="subtitle">
        Inserisci documenti aziendali, dispense, PDF convertiti in testo, appunti o materiale formativo.
        Il motore può pulire il contenuto, riassumerlo, trasformarlo in quiz, report, tabelle, card,
        slide e mini-corsi riutilizzabili per nuovi progetti.
      </p>
    </section>

    <h2 class="section-title">Scegli cosa generare</h2>

    <section class="grid">
      <article class="card">
        <span class="icon">🧹</span>
        <strong>Correggi e pulisci documento</strong>
        <p>Rende il testo più ordinato, leggibile e pronto per essere trasformato in materiale formativo.</p>
      </article>

      <article class="card">
        <span class="icon">📝</span>
        <strong>Genera riassunti</strong>
        <p>Crea sintesi chiare del documento, utili per studio, formazione o presentazione rapida.</p>
      </article>

      <article class="card">
        <span class="icon">❓</span>
        <strong>Genera quiz</strong>
        <p>Trasforma il contenuto in domande con risposte, spiegazioni e struttura compatibile con il motore quiz.</p>
      </article>

      <article class="card">
        <span class="icon">📊</span>
        <strong>Genera report</strong>
        <p>Produce un report aziendale o didattico con punti chiave, struttura, osservazioni e contenuti principali.</p>
      </article>

      <article class="card">
        <span class="icon">📈</span>
        <strong>Genera tabelle e statistiche</strong>
        <p>Estrae dati, parole chiave, conteggi, sezioni e indicatori utili per analizzare il documento.</p>
      </article>

      <article class="card">
        <span class="icon">🃏</span>
        <strong>Genera card formative</strong>
        <p>Crea card interattive per spiegare concetti, passaggi, regole, procedure o mini-lezioni.</p>
      </article>

      <article class="card">
        <span class="icon">🎞️</span>
        <strong>Genera slide</strong>
        <p>Prepara una struttura a slide per trasformare il documento in una presentazione semplice.</p>
      </article>

      <article class="card">
        <span class="icon">💬</span>
        <strong>Genera Q&amp;A</strong>
        <p>Crea domande e risposte rapide per consultare il documento come base di conoscenza.</p>
      </article>

      <article class="card">
        <span class="icon">🎓</span>
        <strong>Genera mini-corso</strong>
        <p>Organizza il materiale in un percorso formativo con spiegazioni, card e contenuti progressivi.</p>
      </article>
    </section>

    <h2 class="section-title">Flusso del pacchetto</h2>

    <section class="workflow">
      <div class="step">
        <b>1. Inserisci documento</b>
        Carichi o copi il materiale dentro la cartella documenti del pacchetto.
      </div>

      <div class="step">
        <b>2. Avvii il motore RAG</b>
        Il sistema legge il testo, lo pulisce e prepara i contenuti.
      </div>

      <div class="step">
        <b>3. Generi gli output</b>
        Ottieni riassunti, quiz, report, tabelle, card, slide e Q&amp;A.
      </div>

      <div class="step">
        <b>4. Riusi il risultato</b>
        Puoi usare gli output per demo, corsi, app web, app Android o nuovi progetti.
      </div>
    </section>

    <div class="command">Comando base:
python3 scripts/rag_documenti_aziendali.py rag/documenti/esempio_documento_aziendale_formazione.md --titolo "Formazione aziendale"</div>
  </main>
</body>
</html>
"""

rag_page_path.write_text(rag_page_html, encoding="utf-8")

print("✅ Bottone RAG inserito vicino al pacchetto personalizzato")
print("✅ Vecchio link RAG semplice rimosso se presente")
print("✅ Pagina demo-rag aggiornata con opzioni: riassunti, quiz, report, tabelle, card, slide, Q&A")
