from pathlib import Path
import json
from datetime import datetime

ROOT = Path.cwd()


def write_file(path, text):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"OK scritto: {path.relative_to(ROOT)}")


def append_once(path, marker, text):
    path = ROOT / path
    if not path.exists():
        print(f"SKIP manca: {path.relative_to(ROOT)}")
        return
    current = path.read_text(encoding="utf-8")
    if marker in current:
        print(f"OK già presente: {marker}")
        return
    path.write_text(current.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")
    print(f"OK aggiunto blocco: {path.relative_to(ROOT)}")


def insert_before_body_once(path, marker, snippet):
    path = ROOT / path
    if not path.exists():
        print(f"SKIP manca: {path.relative_to(ROOT)}")
        return
    current = path.read_text(encoding="utf-8")
    if marker in current:
        print(f"OK pulsante già presente in {path.relative_to(ROOT)}")
        return
    if "</body>" in current:
        updated = current.replace("</body>", snippet.strip() + "\n\n</body>")
    else:
        updated = current.rstrip() + "\n\n" + snippet.strip() + "\n"
    path.write_text(updated, encoding="utf-8")
    print(f"OK aggiunto pulsante/sezione RAG in: {path.relative_to(ROOT)}")


DEMO_RAG_HTML = r'''
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Motore RAG documenti | Alex AI Quiz</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body data-theme="dark-tech">
  <main class="page-shell">
    <section class="hero-card">
      <p class="eyebrow">Motore RAG riutilizzabile</p>
      <h1>Inserisci documenti e prepara quiz, test o mini-corsi</h1>
      <p class="hero-text">
        Questa pagina è il cruscotto visivo del flusso RAG: documento → estrazione contenuti → quiz/test → revisione → pacchetto formativo scaricabile.
      </p>
      <div class="hero-actions">
        <a class="primary-action" href="../downloads/pacchetto-formazione-sicurezza-informatica-aziendale.zip">Scarica esempio aziendale</a>
        <a class="secondary-action" href="../docs/RAG_INSERIMENTO_DOCUMENTI.md">Leggi istruzioni RAG</a>
      </div>
    </section>

    <section class="grid-two">
      <article class="panel">
        <h2>1. Seleziona un documento</h2>
        <p>
          Su GitHub Pages il file resta nel tuo browser: non viene caricato su un server.
          Per usarlo davvero nella pipeline, copialo nella cartella <code>rag/documenti/</code>.
        </p>
        <label class="upload-box" for="documentInput">
          <span class="upload-icon">📄</span>
          <strong>Inserisci documento</strong>
          <small>TXT, MD, JSON, CSV, PDF o DOCX</small>
        </label>
        <input id="documentInput" type="file" accept=".txt,.md,.json,.csv,.pdf,.docx" />
        <div id="fileResult" class="result-box muted">Nessun documento selezionato.</div>
      </article>

      <article class="panel">
        <h2>2. Scegli lo stile grafico</h2>
        <p>Il motore tema permette di preparare futuri pacchetti con stili diversi senza riscrivere ogni pagina.</p>
        <select id="themeSelect">
          <option value="dark-tech">Dark tech</option>
          <option value="light-clean">Chiaro pulito</option>
          <option value="neon-purple">Neon viola</option>
          <option value="ocean-blue">Blu oceano</option>
        </select>
        <pre id="themeCommand" class="code-box">python3 scripts/applica_tema_formazione.py dark-tech</pre>
      </article>
    </section>

    <section class="pipeline-card">
      <h2>Flusso completo</h2>
      <div class="pipeline">
        <div><span>1</span><strong>Documento</strong><small>PDF, DOCX, TXT, MD</small></div>
        <div><span>2</span><strong>RAG</strong><small>chunk, indice, recupero</small></div>
        <div><span>3</span><strong>Generazione</strong><small>quiz/test/minicorso</small></div>
        <div><span>4</span><strong>Revisione</strong><small>controlli e approvazione</small></div>
        <div><span>5</span><strong>Pacchetto</strong><small>web/Android/formazione</small></div>
      </div>
    </section>

    <section class="grid-two">
      <article class="panel">
        <h2>Comandi principali</h2>
        <pre class="code-box">python3 scripts/rag_pipeline_completa_sicura.py
python3 scripts/pipeline_formazione_completa.py rag/documenti/documento_rag_sicurezza_informatica_aziendale.md --titolo "Sicurezza informatica aziendale"
python3 scripts/validatore_rag_distrattori_forti_v2.py review/rag/quiz_da_revisionare.json</pre>
      </article>

      <article class="panel">
        <h2>Cosa rende sicura la pipeline</h2>
        <ul>
          <li>Le domande generate non entrano subito nel database ufficiale.</li>
          <li>Prima passano da validazione, revisione e import controllato.</li>
          <li>I pacchetti formativi possono essere generati come esempi scaricabili.</li>
        </ul>
      </article>
    </section>
  </main>
  <script src="app.js"></script>
</body>
</html>
'''

DEMO_RAG_CSS = r'''
:root {
  --bg: #08111f;
  --panel: rgba(255, 255, 255, 0.08);
  --panel-border: rgba(255, 255, 255, 0.15);
  --text: #eef6ff;
  --muted: #a8bdd6;
  --accent: #36d6ff;
  --accent-2: #8a5cff;
  --code: rgba(0, 0, 0, 0.32);
}

body[data-theme="light-clean"] {
  --bg: #f4f7fb;
  --panel: #ffffff;
  --panel-border: #dbe5f1;
  --text: #122033;
  --muted: #516173;
  --accent: #1769ff;
  --accent-2: #00a884;
  --code: #eef3fa;
}

body[data-theme="neon-purple"] {
  --bg: #10051f;
  --panel: rgba(255, 255, 255, 0.09);
  --panel-border: rgba(212, 105, 255, 0.30);
  --text: #fff6ff;
  --muted: #d4b7e8;
  --accent: #ff4fd8;
  --accent-2: #7c5cff;
  --code: rgba(0, 0, 0, 0.35);
}

body[data-theme="ocean-blue"] {
  --bg: #061d2b;
  --panel: rgba(255, 255, 255, 0.08);
  --panel-border: rgba(80, 210, 255, 0.22);
  --text: #effbff;
  --muted: #acc9d6;
  --accent: #31d0c6;
  --accent-2: #2d8cff;
  --code: rgba(0, 0, 0, 0.32);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 28%, transparent), transparent 34rem),
    radial-gradient(circle at bottom right, color-mix(in srgb, var(--accent-2) 30%, transparent), transparent 36rem),
    var(--bg);
  color: var(--text);
}

.page-shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0;
}

.hero-card, .panel, .pipeline-card {
  border: 1px solid var(--panel-border);
  background: var(--panel);
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(18px);
}

.eyebrow {
  color: var(--accent);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .12em;
}

h1 {
  font-size: clamp(2rem, 5vw, 4.7rem);
  line-height: 1;
  margin: 0;
  max-width: 900px;
}

h2 { margin-top: 0; }

.hero-text {
  max-width: 820px;
  color: var(--muted);
  font-size: 1.12rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.primary-action, .secondary-action, .upload-box {
  border-radius: 999px;
  padding: 13px 18px;
  text-decoration: none;
  font-weight: 800;
}

.primary-action {
  color: #06111e;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
}

.secondary-action {
  color: var(--text);
  border: 1px solid var(--panel-border);
}

.grid-two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.upload-box {
  display: grid;
  place-items: center;
  min-height: 150px;
  border: 1px dashed var(--accent);
  cursor: pointer;
  text-align: center;
  color: var(--text);
}

.upload-icon { font-size: 2.2rem; }

input[type="file"] { display: none; }

.result-box, .code-box {
  margin-top: 14px;
  border-radius: 18px;
  padding: 14px;
  background: var(--code);
  color: var(--text);
  overflow: auto;
}

.muted { color: var(--muted); }

select {
  width: 100%;
  padding: 13px 14px;
  border-radius: 14px;
  border: 1px solid var(--panel-border);
  background: var(--code);
  color: var(--text);
  font-weight: 700;
}

.pipeline-card { margin-top: 18px; }

.pipeline {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.pipeline div {
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 16px;
  min-height: 130px;
}

.pipeline span {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--accent);
  color: #06111e;
  font-weight: 900;
}

.pipeline strong, .pipeline small {
  display: block;
  margin-top: 10px;
}

.pipeline small, li, p { color: var(--muted); }

code { color: var(--accent); }

@media (max-width: 850px) {
  .grid-two, .pipeline { grid-template-columns: 1fr; }
  .hero-card, .panel, .pipeline-card { padding: 20px; }
}
'''

DEMO_RAG_JS = r'''
const input = document.getElementById("documentInput");
const result = document.getElementById("fileResult");
const themeSelect = document.getElementById("themeSelect");
const themeCommand = document.getElementById("themeCommand");

const savedTheme = localStorage.getItem("alex-rag-theme") || "dark-tech";
document.body.dataset.theme = savedTheme;
themeSelect.value = savedTheme;
themeCommand.textContent = `python3 scripts/applica_tema_formazione.py ${savedTheme}`;

themeSelect.addEventListener("change", () => {
  const theme = themeSelect.value;
  document.body.dataset.theme = theme;
  localStorage.setItem("alex-rag-theme", theme);
  themeCommand.textContent = `python3 scripts/applica_tema_formazione.py ${theme}`;
});

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

input.addEventListener("change", () => {
  const file = input.files && input.files[0];

  if (!file) {
    result.textContent = "Nessun documento selezionato.";
    return;
  }

  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const title = file.name.replace(/\.[^.]+$/, "");
  const command = `cp ~/Downloads/${safeName} rag/documenti/${safeName}\npython3 scripts/pipeline_formazione_completa.py rag/documenti/${safeName} --titolo "${title}"`;

  result.innerHTML = `
    <strong>Documento selezionato:</strong> ${file.name}<br>
    <strong>Dimensione:</strong> ${formatBytes(file.size)}<br>
    <strong>Tipo:</strong> ${file.type || "non dichiarato"}<br><br>
    <strong>Comando consigliato:</strong>
    <pre class="code-box">${command}</pre>
  `;

  const lowerName = file.name.toLowerCase();
  const canPreview =
    lowerName.endsWith(".txt") ||
    lowerName.endsWith(".md") ||
    lowerName.endsWith(".json") ||
    lowerName.endsWith(".csv");

  if (canPreview) {
    const reader = new FileReader();
    reader.onload = () => {
      const preview = String(reader.result || "").slice(0, 900);
      const escaped = preview.replace(/[<>&]/g, ch => ({"<":"&lt;", ">":"&gt;", "&":"&amp;"}[ch]));
      result.innerHTML += `<strong>Anteprima locale:</strong><pre class="code-box">${escaped}</pre>`;
    };
    reader.readAsText(file);
  }
});
'''

THEME_ENGINE_CSS = r'''
:root[data-alex-theme="dark-tech"] {
  --alex-bg: #08111f;
  --alex-card: rgba(255, 255, 255, 0.08);
  --alex-text: #eef6ff;
  --alex-muted: #a8bdd6;
  --alex-accent: #36d6ff;
}

:root[data-alex-theme="light-clean"] {
  --alex-bg: #f4f7fb;
  --alex-card: #ffffff;
  --alex-text: #122033;
  --alex-muted: #516173;
  --alex-accent: #1769ff;
}

:root[data-alex-theme="neon-purple"] {
  --alex-bg: #10051f;
  --alex-card: rgba(255, 255, 255, 0.09);
  --alex-text: #fff6ff;
  --alex-muted: #d4b7e8;
  --alex-accent: #ff4fd8;
}

:root[data-alex-theme="ocean-blue"] {
  --alex-bg: #061d2b;
  --alex-card: rgba(255, 255, 255, 0.08);
  --alex-text: #effbff;
  --alex-muted: #acc9d6;
  --alex-accent: #31d0c6;
}
'''

THEME_ENGINE_JS = r'''
(function () {
  const STORAGE_KEY = "alex-theme-engine-choice";
  const root = document.documentElement;

  function applyTheme(themeName) {
    root.setAttribute("data-alex-theme", themeName || "dark-tech");
    try {
      localStorage.setItem(STORAGE_KEY, themeName || "dark-tech");
    } catch (_) {}
  }

  let saved = null;
  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch (_) {}

  applyTheme(saved || root.getAttribute("data-alex-theme") || "dark-tech");
  window.AlexThemeEngine = { applyTheme };
})();
'''

THEME_JSON = {
    "dark-tech": {
        "nome": "Dark tech",
        "sfondo": "#08111f",
        "card": "rgba(255,255,255,0.08)",
        "testo": "#eef6ff",
        "accento": "#36d6ff"
    },
    "light-clean": {
        "nome": "Chiaro pulito",
        "sfondo": "#f4f7fb",
        "card": "#ffffff",
        "testo": "#122033",
        "accento": "#1769ff"
    },
    "neon-purple": {
        "nome": "Neon viola",
        "sfondo": "#10051f",
        "card": "rgba(255,255,255,0.09)",
        "testo": "#fff6ff",
        "accento": "#ff4fd8"
    },
    "ocean-blue": {
        "nome": "Blu oceano",
        "sfondo": "#061d2b",
        "card": "rgba(255,255,255,0.08)",
        "testo": "#effbff",
        "accento": "#31d0c6"
    }
}

APPLICA_TEMA = r'''
#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "temi_grafici_formazione.json"
OUT_DIR = ROOT / "dist" / "formazione"


def main():
    tema = sys.argv[1] if len(sys.argv) > 1 else "dark-tech"
    temi = json.loads(CONFIG.read_text(encoding="utf-8"))

    if tema not in temi:
        validi = ", ".join(sorted(temi))
        raise SystemExit(f"Tema non valido: {tema}. Temi disponibili: {validi}")

    scelto = temi[tema]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "tema_selezionato.json").write_text(
        json.dumps({tema: scelto}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    css = (
        ":root {\n"
        f"  --bg: {scelto['sfondo']};\n"
        f"  --card: {scelto['card']};\n"
        f"  --text: {scelto['testo']};\n"
        f"  --accent: {scelto['accento']};\n"
        "}\n"
    )

    (OUT_DIR / "theme-selected.css").write_text(css, encoding="utf-8")
    print(f"✅ Tema formazione applicato: {scelto['nome']} ({tema})")
    print("📌 File creati: dist/formazione/tema_selezionato.json, dist/formazione/theme-selected.css")


if __name__ == "__main__":
    main()
'''

VALIDATORE_RAG_V2 = r'''
#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validatore_rag_distrattori_forti_v2.md"

STOPWORDS = {
    "che", "con", "del", "della", "dello", "dei", "degli", "delle", "per", "tra", "fra",
    "una", "uno", "gli", "alla", "alle", "allo", "sul", "sulla", "sulle", "nel", "nella",
    "nelle", "come", "cosa", "quando", "quale", "quali", "questo", "questa", "questi",
    "queste", "sono", "essere", "viene", "può", "più", "meno", "solo"
}

GENERICI = {
    "sempre", "mai", "tutto", "tutti", "nessuno", "qualsiasi", "automaticamente",
    "garantisce", "elimina completamente", "risolve sempre", "senza eccezioni",
    "in ogni caso", "al 100%"
}


def normalizza_testo(value):
    return re.sub(r"\s+", " ", str(value or "").strip())


def tokens(value):
    parole = re.findall(r"[a-zàèéìòù0-9]{4,}", normalizza_testo(value).lower())
    return {p for p in parole if p not in STOPWORDS}


def estrai_domande(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("domande", "questions", "quiz", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def estrai_opzioni(domanda):
    raw = domanda.get("opzioni") or domanda.get("risposte") or domanda.get("answers") or []
    if isinstance(raw, dict):
        return [normalizza_testo(v) for _, v in sorted(raw.items())]
    if isinstance(raw, list):
        return [normalizza_testo(v) for v in raw]
    return []


def valuta_domanda(domanda, indice):
    warnings = []
    testo_domanda = normalizza_testo(domanda.get("domanda") or domanda.get("question") or domanda.get("testo"))
    corretta = normalizza_testo(domanda.get("risposta_corretta") or domanda.get("correct_answer") or domanda.get("corretta"))
    opzioni = estrai_opzioni(domanda)
    codice = domanda.get("id") or domanda.get("codice") or f"domanda_{indice}"

    if len(opzioni) != 4:
        warnings.append("la domanda non ha esattamente 4 opzioni")

    if corretta and corretta not in opzioni:
        warnings.append("la risposta corretta non è presente tra le opzioni")

    if len(set(opzioni)) != len(opzioni):
        warnings.append("ci sono opzioni duplicate")

    distrattori = [o for o in opzioni if o != corretta]

    if len(distrattori) != 3:
        warnings.append("non risultano 3 distrattori")

    token_domanda = tokens(testo_domanda)
    token_corretta = tokens(corretta)
    ancora = token_corretta or token_domanda
    lunghezza_corretta = max(len(corretta), 1)

    for numero, distrattore in enumerate(distrattori, start=1):
        lower = distrattore.lower()
        rapporto_lunghezza = len(distrattore) / lunghezza_corretta
        overlap_core = len(tokens(distrattore) & ancora)
        overlap_domanda = len(tokens(distrattore) & token_domanda)

        if len(distrattore) < 18:
            warnings.append(f"distrattore {numero} troppo corto")

        if rapporto_lunghezza < 0.55 or rapporto_lunghezza > 1.80:
            warnings.append(f"distrattore {numero} troppo diverso per lunghezza dalla risposta corretta")

        if overlap_core == 0 and overlap_domanda == 0:
            warnings.append(f"distrattore {numero} sembra fuori tema rispetto a domanda/risposta corretta")

        if any(termine in lower for termine in GENERICI):
            warnings.append(f"distrattore {numero} contiene formulazioni troppo assolute o generiche")

    return codice, warnings


def main():
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
        if not input_path.is_absolute():
            input_path = ROOT / input_path
    else:
        possibili = [
            ROOT / "review" / "rag" / "quiz_da_revisionare.json",
            ROOT / "dist" / "generated" / "rag_quiz_generato.json",
        ]
        input_path = next((p for p in possibili if p.exists()), None)

    if not input_path or not input_path.exists():
        raise SystemExit("Nessun file RAG da validare trovato. Passa un percorso JSON come argomento.")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    domande = estrai_domande(data)

    try:
        nome_file = input_path.relative_to(ROOT)
    except ValueError:
        nome_file = input_path

    righe = [
        "# Validatore RAG distrattori forti v2",
        "",
        f"File analizzato: `{nome_file}`",
        f"Domande trovate: {len(domande)}",
        ""
    ]

    totale_warning = 0

    for i, domanda in enumerate(domande, start=1):
        codice, warnings = valuta_domanda(domanda, i)

        if warnings:
            totale_warning += len(warnings)
            righe.append(f"## {codice}")

            for warning in warnings:
                righe.append(f"- {warning}")

            righe.append("")

    if totale_warning == 0:
        righe.append("✅ Nessun avviso: i distrattori risultano tecnicamente coerenti con le regole base.")
    else:
        righe.append(f"⚠️ Avvisi totali: {totale_warning}")
        righe.append("")
        righe.append(
            "Nota: questo controllo non sostituisce la revisione umana, "
            "ma segnala le opzioni probabilmente troppo deboli, fuori tema o troppo diverse dalla risposta corretta."
        )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(righe) + "\n", encoding="utf-8")

    print(f"📌 Report: {REPORT.relative_to(ROOT)}")

    if totale_warning:
        print(f"⚠️ Avvisi trovati: {totale_warning}")
    else:
        print("✅ Distrattori RAG senza avvisi tecnici")


if __name__ == "__main__":
    main()
'''

VERIFICA_FINALI = r'''
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "demo-rag/index.html",
    "demo-rag/style.css",
    "demo-rag/app.js",
    "runtime/web/theme-engine.css",
    "runtime/web/theme-engine.js",
    "config/temi_grafici_formazione.json",
    "scripts/applica_tema_formazione.py",
    "scripts/validatore_rag_distrattori_forti_v2.py",
    "docs/RAG_INSERIMENTO_DOCUMENTI.md",
    "docs/MOTORE_GRAFICO_RIUTILIZZABILE.md",
]

ok = True

for rel in REQUIRED:
    path = ROOT / rel
    if path.exists():
        print(f"✅ {rel}")
    else:
        ok = False
        print(f"❌ manca {rel}")

readme = ROOT / "README.md"

if readme.exists():
    text = readme.read_text(encoding="utf-8").lower()
    markers = [
        "motore rag documenti",
        "pipeline materiale formativo",
        "motore grafico riutilizzabile"
    ]

    for marker in markers:
        if marker in text:
            print(f"✅ README contiene: {marker}")
        else:
            ok = False
            print(f"❌ README non contiene: {marker}")
else:
    ok = False
    print("❌ manca README.md")

if not ok:
    raise SystemExit(1)

print("\n✅ Verifica migliorie finali completata")
'''

DOC_RAG = r'''
# Inserimento documenti nel motore RAG

Il progetto ora include un cruscotto visuale in `demo-rag/index.html` per mostrare il flusso:

**documento → RAG → quiz/test/minicorso → revisione → pacchetto scaricabile**.

## Tipi di documento previsti

La pipeline è pensata per lavorare con materiali come:

- `.md`
- `.txt`
- `.json`
- `.csv`
- `.pdf`
- `.docx`

La pagina web statica può selezionare il file e mostrare il comando consigliato, ma non può caricarlo davvero su GitHub da sola.

Per usare il documento nella pipeline reale bisogna copiarlo nella cartella:

```bash
rag/documenti/
```

## Esempio

```bash
cp ~/Downloads/documento_azienda.md rag/documenti/documento_azienda.md
python3 scripts/pipeline_formazione_completa.py rag/documenti/documento_azienda.md --titolo "Documento aziendale"
```

## Sicurezza del flusso

Le domande generate dal RAG non entrano direttamente nei database ufficiali. Passano prima da:

1. generazione temporanea;
2. validazione JSON;
3. revisione;
4. controlli qualità;
5. import controllato solo se approvate.

Questo protegge il progetto da domande deboli, duplicate, troppo intuitive o non coerenti con il documento originale.
'''

DOC_THEME = r'''
# Motore grafico riutilizzabile

Il progetto ora contiene una base per scegliere lo stile grafico dei futuri pacchetti formativi.

## File principali

- `config/temi_grafici_formazione.json`
- `runtime/web/theme-engine.css`
- `runtime/web/theme-engine.js`
- `scripts/applica_tema_formazione.py`

## Temi disponibili

- `dark-tech`
- `light-clean`
- `neon-purple`
- `ocean-blue`

## Comando

```bash
python3 scripts/applica_tema_formazione.py dark-tech
```

Il comando genera:

- `dist/formazione/tema_selezionato.json`
- `dist/formazione/theme-selected.css`

Questa base serve per futuri pacchetti dove l'utente potrà scegliere colori, sfondi, stile delle card e atmosfera grafica senza riscrivere il codice del corso.
'''

README_BLOCK = r'''
<!-- ALEX-RAG-FINALE-START -->

## Motore RAG documenti e materiale formativo

Il progetto include anche una pipeline RAG riutilizzabile per trasformare documenti in contenuti formativi. Il flusso previsto è:

**documento → RAG → quiz/test/minicorso → revisione → pacchetto scaricabile**.

<p>
  <a href="demo-rag/index.html" style="display:inline-block;padding:12px 18px;border-radius:14px;background:linear-gradient(135deg,#36d6ff,#8a5cff);color:#06111e;font-weight:800;text-decoration:none;">
    📄 Apri motore RAG documenti
  </a>
</p>

La pagina `demo-rag/index.html` serve come cruscotto visuale per inserire o selezionare documenti e mostrare i comandi della pipeline. In ambiente GitHub Pages il file resta nel browser: per elaborarlo davvero va copiato nella cartella `rag/documenti/` del progetto locale.

### Pipeline materiale formativo

La pipeline può generare:

- testo estratto/corretto;
- mini-corso interattivo JSON;
- mini-corso HTML;
- pacchetto ZIP scaricabile;
- report di controllo.

Esempio:

```bash
python3 scripts/pipeline_formazione_completa.py rag/documenti/documento_rag_sicurezza_informatica_aziendale.md --titolo "Sicurezza informatica aziendale"
```

### Revisione sicura dei quiz generati da RAG

Le domande generate dal RAG non vengono inserite automaticamente nei database ufficiali. Prima passano da validazione, revisione e import controllato. Per un controllo aggiuntivo sui distrattori:

```bash
python3 scripts/validatore_rag_distrattori_forti_v2.py review/rag/quiz_da_revisionare.json
```

### Motore grafico riutilizzabile

Sono disponibili preset grafici riutilizzabili per futuri pacchetti formativi:

```bash
python3 scripts/applica_tema_formazione.py dark-tech
```

Temi iniziali: `dark-tech`, `light-clean`, `neon-purple`, `ocean-blue`.

<!-- ALEX-RAG-FINALE-END -->
'''

DEMO_BUTTON = r'''
<!-- ALEX-RAG-BUTTON-START -->
<section class="rag-documenti-card" aria-label="Motore RAG documenti">
  <div>
    <p class="rag-documenti-label">Nuovo motore riutilizzabile</p>
    <h2>RAG documenti</h2>
    <p>Inserisci documenti e prepara quiz, test, mini-corsi e pacchetti formativi scaricabili.</p>
  </div>
  <a class="rag-documenti-button" href="../demo-rag/index.html">📄 Apri motore RAG</a>
</section>
<!-- ALEX-RAG-BUTTON-END -->
'''

DEMO_BUTTON_CSS = r'''
/* ALEX-RAG-BUTTON-START: aggiunta non distruttiva, non modifica i pulsanti colorati esistenti */
.rag-documenti-card {
  margin: 32px auto;
  width: min(1080px, calc(100% - 32px));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(54, 214, 255, 0.28);
  background: linear-gradient(135deg, rgba(54, 214, 255, 0.14), rgba(138, 92, 255, 0.16));
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.20);
}

.rag-documenti-card h2 {
  margin: 0 0 8px;
}

.rag-documenti-card p {
  margin: 0;
}

.rag-documenti-label {
  color: #36d6ff;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: .8rem;
}

.rag-documenti-button {
  flex: 0 0 auto;
  display: inline-block;
  padding: 13px 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #36d6ff, #8a5cff);
  color: #06111e;
  font-weight: 900;
  text-decoration: none;
}

@media (max-width: 760px) {
  .rag-documenti-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
/* ALEX-RAG-BUTTON-END */
'''

REPORT_TEXT = f'''
# Migliorie finali RAG e formazione

Data generazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Sono stati aggiunti i blocchi finali per rendere il progetto più presentabile e riutilizzabile:

- cruscotto `demo-rag/` per documenti e pipeline RAG;
- pulsante RAG nella demo principale senza modificare i pulsanti colorati esistenti;
- documentazione per inserimento documenti;
- motore tema grafico riutilizzabile;
- validatore RAG distrattori forti v2;
- aggiornamento README tramite blocco aggiunto, senza riscrittura completa.
'''


def main():
    write_file("demo-rag/index.html", DEMO_RAG_HTML)
    write_file("demo-rag/style.css", DEMO_RAG_CSS)
    write_file("demo-rag/app.js", DEMO_RAG_JS)

    write_file("runtime/web/theme-engine.css", THEME_ENGINE_CSS)
    write_file("runtime/web/theme-engine.js", THEME_ENGINE_JS)

    write_file("config/temi_grafici_formazione.json", json.dumps(THEME_JSON, ensure_ascii=False, indent=2))

    write_file("scripts/applica_tema_formazione.py", APPLICA_TEMA)
    write_file("scripts/validatore_rag_distrattori_forti_v2.py", VALIDATORE_RAG_V2)
    write_file("scripts/verifica_migliorie_finali_rag.py", VERIFICA_FINALI)

    write_file("docs/RAG_INSERIMENTO_DOCUMENTI.md", DOC_RAG)
    write_file("docs/MOTORE_GRAFICO_RIUTILIZZABILE.md", DOC_THEME)

    write_file("reports/migliorie_finali_rag_formazione.md", REPORT_TEXT)

    insert_before_body_once("demo/index.html", "ALEX-RAG-BUTTON-START", DEMO_BUTTON)
    append_once("demo/style.css", "ALEX-RAG-BUTTON-START", DEMO_BUTTON_CSS)
    append_once("README.md", "ALEX-RAG-FINALE-START", README_BLOCK)

    print("\n✅ Migliorie finali RAG/formazione applicate")


if __name__ == "__main__":
    main()
