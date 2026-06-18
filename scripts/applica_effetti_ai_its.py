from pathlib import Path
import json
import re
import shutil
import tempfile
import zipfile

REPORT = Path("reports/applica_effetti_ai_its.md")

DEMO_AI_DIR = Path("demo-ai")
RUNTIME_WEB_DIR = Path("runtime/web")
CREATE_PACKAGE = Path("scripts/create_quiz_package.py")
WEB_AI_ZIP = Path("downloads/pacchetto-web-ai-its-demo.zip")
ANDROID_AI_ZIP = Path("downloads/pacchetto-android-ai-its-finale-semplice.zip")

WEB_EFFECTS_CSS = r"""
/* ===== Effetti AI ITS: coriandoli + premi finali ===== */
.alex-ai-confetti-piece {
  position: fixed;
  bottom: -36px;
  left: 50%;
  width: 14px;
  height: 22px;
  border-radius: 6px;
  pointer-events: none;
  z-index: 999999;
  opacity: 0.98;
  animation: alexAiConfettiRise 1650ms cubic-bezier(.16,.84,.33,1) forwards;
}

@keyframes alexAiConfettiRise {
  0% {
    transform: translate3d(0, 0, 0) rotate(0deg) scale(0.9);
    opacity: 0;
  }
  8% {
    opacity: 1;
  }
  74% {
    opacity: 1;
  }
  100% {
    transform: translate3d(var(--alex-ai-x), var(--alex-ai-y), 0) rotate(var(--alex-ai-rot)) scale(1.25);
    opacity: 0;
  }
}

.alex-ai-final-reward {
  margin: 24px auto;
  max-width: 760px;
  padding: 22px;
  border: 1px solid rgba(77, 208, 255, 0.42);
  border-radius: 24px;
  background:
    radial-gradient(circle at top left, rgba(77,208,255,.22), transparent 34%),
    linear-gradient(135deg, rgba(8,16,34,.96), rgba(22,10,48,.96));
  box-shadow: 0 22px 70px rgba(0, 0, 0, .42), 0 0 36px rgba(77, 208, 255, .16);
  color: #f5fbff;
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 18px;
  align-items: center;
}

.alex-ai-final-drawing {
  min-height: 108px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  font-size: 56px;
  background: linear-gradient(160deg, rgba(93,95,239,.26), rgba(18,209,255,.16));
  border: 1px solid rgba(255,255,255,.16);
}

.alex-ai-final-copy h3 {
  margin: 0 0 8px;
  font-size: 1.35rem;
  letter-spacing: .01em;
}

.alex-ai-final-copy p {
  margin: 6px 0;
  line-height: 1.5;
  color: rgba(245,251,255,.88);
}

.alex-ai-final-score {
  display: inline-flex;
  margin-top: 10px;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(77,208,255,.15);
  border: 1px solid rgba(77,208,255,.28);
  color: #9eeaff;
  font-weight: 800;
}

@media (max-width: 640px) {
  .alex-ai-final-reward {
    grid-template-columns: 1fr;
    text-align: center;
  }
}
""".strip()

WEB_EFFECTS_JS = r"""
(function () {
  if (window.__alexAiItsEffectsInstalled) {
    return;
  }

  window.__alexAiItsEffectsInstalled = true;

  const rewards = {
    "10": [
      ["🚀", "Missione perfetta", "Hai chiuso il test con precisione totale. Questa è mentalità da progetto professionale."],
      ["🧠", "Prestazione eccellente", "Risposte pulite, ritmo alto e zero errori: ottimo segnale per un percorso AI ITS."],
      ["🏆", "Dominio completo", "Hai gestito il test come un sistema ben addestrato: dati chiari, decisioni corrette, risultato massimo."]
    ],
    "9": [
      ["⚡", "Quasi perfetto", "Ti manca pochissimo al massimo. La base è fortissima, ora serve solo rifinire i dettagli."],
      ["🤖", "Livello molto alto", "Hai dimostrato controllo e ragionamento. Un errore non rovina una prova così solida."],
      ["🌟", "Prestazione distinta", "Sei già in una zona alta: continua così e il 10 diventa naturale."]
    ],
    "8": [
      ["🔥", "Ottimo risultato", "Hai superato bene il test. Ora lavora sui dettagli che separano il buono dall'eccellente."],
      ["💡", "Ragionamento solido", "Il risultato mostra comprensione reale. Con un po' di revisione puoi salire ancora."],
      ["🧩", "Buona padronanza", "Le basi ci sono e si vedono. Ora punta a rendere più stabili anche le risposte difficili."]
    ],
    "7": [
      ["📈", "Buona prova", "Stai costruendo una base concreta. Rivedi gli errori e trasformali in punti forti."],
      ["🔧", "In crescita", "Il risultato è positivo. Ora serve consolidare gli argomenti dove hai esitato."],
      ["🛠️", "Base valida", "Hai materiale su cui costruire. La prossima prova può salire molto."]
    ],
    "6": [
      ["🧱", "Sufficiente", "Hai superato la soglia. Ora bisogna rendere più sicure le risposte e ridurre gli errori evitabili."],
      ["🧭", "Strada giusta", "La direzione è buona, ma serve più allenamento sui concetti chiave."],
      ["📚", "Da consolidare", "Il test è passato, ma il prossimo obiettivo è trasformare il minimo in sicurezza."]
    ],
    "low": [
      ["🔁", "Riprova strategica", "Non è una bocciatura: è una mappa degli argomenti da rinforzare."],
      ["🧪", "Test diagnostico", "Questo risultato ti dice dove intervenire. Riparti dagli errori e migliora a blocchi."],
      ["🧠", "Allenamento utile", "Ogni errore è un dato. Usalo per capire cosa rivedere prima del prossimo tentativo."]
    ]
  };

  const confettiColors = ["#4dd0ff", "#8b5cf6", "#22c55e", "#facc15", "#fb7185", "#ffffff"];

  function randomItem(items) {
    return items[Math.floor(Math.random() * items.length)];
  }

  function rewardBucket(score, total) {
    if (!total) {
      return "low";
    }

    const voto = Math.round((score / total) * 10);

    if (voto >= 10) return "10";
    if (voto >= 9) return "9";
    if (voto >= 8) return "8";
    if (voto >= 7) return "7";
    if (voto >= 6) return "6";
    return "low";
  }

  function shootConfetti() {
    const count = 46;

    for (let index = 0; index < count; index += 1) {
      const piece = document.createElement("span");
      piece.className = "alex-ai-confetti-piece";

      const spread = (Math.random() * 2 - 1) * Math.min(window.innerWidth * 0.64, 620);
      const height = -(Math.random() * 360 + 300);
      const rotation = (Math.random() * 920 - 460) + "deg";

      piece.style.left = (window.innerWidth / 2 + (Math.random() * 80 - 40)) + "px";
      piece.style.background = confettiColors[index % confettiColors.length];
      piece.style.setProperty("--alex-ai-x", spread + "px");
      piece.style.setProperty("--alex-ai-y", height + "px");
      piece.style.setProperty("--alex-ai-rot", rotation);
      piece.style.animationDelay = (Math.random() * 180) + "ms";

      document.body.appendChild(piece);

      setTimeout(function () {
        piece.remove();
      }, 2100);
    }
  }

  function extractScoreFromText(text) {
    const patterns = [
      /(?:Risultato|Punteggio|Score)[^\d]*(\d+)\s*\/\s*(\d+)/i,
      /(\d+)\s*\/\s*(\d+)\s*[-–—]\s*(?:eccellente|ottimo|distinto|buono|discreto|sufficiente|insufficiente)/i,
      /Hai totalizzato[^\d]*(\d+)\s*\/\s*(\d+)/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);

      if (match) {
        return {
          score: Number(match[1]),
          total: Number(match[2])
        };
      }
    }

    return null;
  }

  function rewardAlreadyShown(score, total) {
    const current = document.querySelector(".alex-ai-final-reward");

    if (!current) {
      return false;
    }

    return current.getAttribute("data-score") === score + "/" + total;
  }

  function renderReward(score, total) {
    if (rewardAlreadyShown(score, total)) {
      return;
    }

    document.querySelectorAll(".alex-ai-final-reward").forEach(function (node) {
      node.remove();
    });

    const bucket = rewardBucket(score, total);
    const reward = randomItem(rewards[bucket] || rewards.low);

    const card = document.createElement("section");
    card.className = "alex-ai-final-reward";
    card.setAttribute("data-score", score + "/" + total);

    card.innerHTML = [
      '<div class="alex-ai-final-drawing" aria-hidden="true">' + reward[0] + '</div>',
      '<div class="alex-ai-final-copy">',
      '<h3>' + reward[1] + '</h3>',
      '<p>' + reward[2] + '</p>',
      '<p class="alex-ai-final-score">Risultato: ' + score + '/' + total + '</p>',
      '</div>'
    ].join("");

    const target =
      document.querySelector("#result") ||
      document.querySelector(".result") ||
      document.querySelector(".results") ||
      document.querySelector(".quiz-result") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(card);
  }

  function scanForFinalReward() {
    const text = document.body ? document.body.innerText || "" : "";
    const score = extractScoreFromText(text);

    if (score && score.total > 0) {
      renderReward(score.score, score.total);
    }
  }

  function maybeConfettiFromClick(event) {
    const clicked =
      event.target.closest("button") ||
      event.target.closest(".option") ||
      event.target.closest(".answer") ||
      event.target.closest("[data-answer]");

    if (!clicked) {
      return;
    }

    setTimeout(function () {
      const classText = String(clicked.className || "").toLowerCase();
      const text = String(clicked.innerText || clicked.textContent || "").toLowerCase();

      const looksCorrect =
        classText.includes("correct") ||
        classText.includes("corretta") ||
        classText.includes("success") ||
        text.includes("corretto");

      const looksWrong =
        classText.includes("wrong") ||
        classText.includes("errore") ||
        classText.includes("sbagli") ||
        text.includes("sbagliato");

      if (looksCorrect && !looksWrong) {
        shootConfetti();
      }

      scanForFinalReward();
    }, 180);
  }

  document.addEventListener("click", maybeConfettiFromClick, true);

  const observer = new MutationObserver(function () {
    scanForFinalReward();
  });

  function start() {
    if (!document.body) {
      return;
    }

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });

    scanForFinalReward();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  window.alexAiShootConfetti = shootConfetti;
  window.alexAiShowFinalReward = renderReward;
})();
""".strip()

ANDROID_REWARD_ENGINE = r"""
package com.alex.quizengine

import kotlin.random.Random

data class FinalReward(
    val title: String,
    val message: String,
    val drawing: String,
    val score: Int,
    val total: Int
)

data class ConfettiSpec(
    val pieces: Int = 46,
    val startsFromBottom: Boolean = true,
    val wideSpread: Boolean = true,
    val softMotion: Boolean = true
)

object FinalRewardEngine {
    private val perfect = listOf(
        Triple("Missione perfetta", "Hai chiuso il test con precisione totale. Questa è mentalità da progetto professionale.", "🚀"),
        Triple("Prestazione eccellente", "Risposte pulite, ritmo alto e zero errori: ottimo segnale per un percorso AI ITS.", "🧠"),
        Triple("Dominio completo", "Hai gestito il test come un sistema ben addestrato: dati chiari, decisioni corrette, risultato massimo.", "🏆")
    )

    private val excellent = listOf(
        Triple("Quasi perfetto", "Ti manca pochissimo al massimo. La base è fortissima, ora serve solo rifinire i dettagli.", "⚡"),
        Triple("Livello molto alto", "Hai dimostrato controllo e ragionamento. Un errore non rovina una prova così solida.", "🤖"),
        Triple("Prestazione distinta", "Sei già in una zona alta: continua così e il 10 diventa naturale.", "🌟")
    )

    private val good = listOf(
        Triple("Ottimo risultato", "Hai superato bene il test. Ora lavora sui dettagli che separano il buono dall'eccellente.", "🔥"),
        Triple("Ragionamento solido", "Il risultato mostra comprensione reale. Con un po' di revisione puoi salire ancora.", "💡"),
        Triple("Buona padronanza", "Le basi ci sono e si vedono. Ora punta a rendere più stabili anche le risposte difficili.", "🧩")
    )

    private val medium = listOf(
        Triple("Buona prova", "Stai costruendo una base concreta. Rivedi gli errori e trasformali in punti forti.", "📈"),
        Triple("In crescita", "Il risultato è positivo. Ora serve consolidare gli argomenti dove hai esitato.", "🔧"),
        Triple("Base valida", "Hai materiale su cui costruire. La prossima prova può salire molto.", "🛠️")
    )

    private val minimum = listOf(
        Triple("Sufficiente", "Hai superato la soglia. Ora bisogna rendere più sicure le risposte e ridurre gli errori evitabili.", "🧱"),
        Triple("Strada giusta", "La direzione è buona, ma serve più allenamento sui concetti chiave.", "🧭"),
        Triple("Da consolidare", "Il test è passato, ma il prossimo obiettivo è trasformare il minimo in sicurezza.", "📚")
    )

    private val low = listOf(
        Triple("Riprova strategica", "Non è una bocciatura: è una mappa degli argomenti da rinforzare.", "🔁"),
        Triple("Test diagnostico", "Questo risultato ti dice dove intervenire. Riparti dagli errori e migliora a blocchi.", "🧪"),
        Triple("Allenamento utile", "Ogni errore è un dato. Usalo per capire cosa rivedere prima del prossimo tentativo.", "🧠")
    )

    fun rewardFor(score: Int, total: Int): FinalReward {
        val safeTotal = total.coerceAtLeast(1)
        val voto = ((score.toDouble() / safeTotal.toDouble()) * 10.0).toInt()

        val bucket = when {
            voto >= 10 -> perfect
            voto >= 9 -> excellent
            voto >= 8 -> good
            voto >= 7 -> medium
            voto >= 6 -> minimum
            else -> low
        }

        val selected = bucket[Random.nextInt(bucket.size)]

        return FinalReward(
            title = selected.first,
            message = selected.second,
            drawing = selected.third,
            score = score,
            total = total
        )
    }

    fun confettiForCorrectAnswer(): ConfettiSpec {
        return ConfettiSpec(
            pieces = 46,
            startsFromBottom = true,
            wideSpread = true,
            softMotion = true
        )
    }
}
""".strip()


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def ensure_link(html_path, css_name="ai-effects.css", js_name="ai-effects.js"):
    if not html_path.exists():
        return False

    text = html_path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if css_name not in text:
        text = text.replace(
            "</head>",
            f'  <link rel="stylesheet" href="{css_name}">\n</head>'
        )

    if js_name not in text:
        text = text.replace(
            "</body>",
            f'  <script src="{js_name}"></script>\n</body>'
        )

    if text != original:
        html_path.write_text(text, encoding="utf-8")

    return text != original


def install_web_effects_in_folder(folder):
    if not folder.exists():
        return {"folder": str(folder), "exists": False, "changed_html": 0}

    write_text(folder / "ai-effects.css", WEB_EFFECTS_CSS)
    write_text(folder / "ai-effects.js", WEB_EFFECTS_JS)

    changed_html = 0

    for html_name in ["index.html", "1_APRI_QUIZ.html"]:
        html = folder / html_name
        if ensure_link(html):
            changed_html += 1

    return {
        "folder": str(folder),
        "exists": True,
        "changed_html": changed_html,
    }


def patch_create_quiz_package():
    if not CREATE_PACKAGE.exists():
        raise SystemExit(f"ERRORE: non trovo {CREATE_PACKAGE}")

    text = CREATE_PACKAGE.read_text(encoding="utf-8")
    original = text

    marker = "# === EFFETTI WEB AI ITS PACCHETTI PERSONALIZZATI ==="

    helper = f'''
# === EFFETTI WEB AI ITS PACCHETTI PERSONALIZZATI ===
ALEX_AI_EFFECTS_CSS = {WEB_EFFECTS_CSS!r}
ALEX_AI_EFFECTS_JS = {WEB_EFFECTS_JS!r}

def scrivi_effetti_web_ai_its(output_dir):
    from pathlib import Path as _Path
    import json as _json

    output_dir = _Path(output_dir)

    possibili_database = [
        output_dir / "database_quiz.json",
        output_dir / "SOLO_FILE_DA_COPIARE_WEB" / "database_quiz.json",
    ]

    database_path = None

    for candidato in possibili_database:
        if candidato.exists():
            database_path = candidato
            break

    if database_path is None:
        return

    try:
        dati = _json.loads(database_path.read_text(encoding="utf-8"))
    except Exception:
        return

    if isinstance(dati, list):
        domande = dati
    elif isinstance(dati, dict):
        domande = []
        for chiave in ["domande", "questions", "quiz", "items", "data"]:
            valore = dati.get(chiave)
            if isinstance(valore, list):
                domande = valore
                break
    else:
        domande = []

    if not domande:
        return

    def categoria_da_id(domanda):
        qid = str(domanda.get("id", "")).upper()

        if qid.startswith("AI-"):
            return "ai"
        if qid.startswith("INF-"):
            return "informatica"
        if qid.startswith("ING-"):
            return "inglese"
        if qid.startswith("MAT-"):
            return "matematica"
        if qid.startswith("LOG-VIS-"):
            return "logica_visiva"
        if qid.startswith(("LOG-NUM-", "LOG-VER-", "LOG-AST-", "LOG-CRI-")):
            return "logica"
        if qid.startswith(("SCI-", "BIO-", "CHI-", "FIS-", "FQ-")):
            return "scienze"

        return "altro"

    categorie = {{categoria_da_id(domanda) for domanda in domande}}
    categorie.discard("altro")

    categorie_ai_its = {{
        "ai",
        "informatica",
        "matematica",
        "inglese",
        "logica",
        "logica_visiva",
    }}

    if not categorie or "scienze" in categorie or not categorie.issubset(categorie_ai_its):
        return

    for html_file in sorted(set(output_dir.rglob("index.html")) | set(output_dir.rglob("1_APRI_QUIZ.html"))):
        cartella = html_file.parent
        (cartella / "ai-effects.css").write_text(ALEX_AI_EFFECTS_CSS.strip() + "\\n", encoding="utf-8")
        (cartella / "ai-effects.js").write_text(ALEX_AI_EFFECTS_JS.strip() + "\\n", encoding="utf-8")

        testo = html_file.read_text(encoding="utf-8", errors="ignore")

        if "ai-effects.css" not in testo:
            testo = testo.replace("</head>", '  <link rel="stylesheet" href="ai-effects.css">\\n</head>')

        if "ai-effects.js" not in testo:
            testo = testo.replace("</body>", '  <script src="ai-effects.js"></script>\\n</body>')

        html_file.write_text(testo, encoding="utf-8")
'''.rstrip()

    if marker not in text:
        insert_at = text.find("\ndef ")

        if insert_at == -1:
            raise SystemExit("ERRORE: non trovo un punto sicuro dove inserire helper effetti AI ITS.")

        text = text[:insert_at] + "\n\n" + helper + "\n" + text[insert_at:]

    if "scrivi_effetti_web_ai_its(output_dir)" not in text:
        lines = text.splitlines()
        new_lines = []

        for line in lines:
            if "zip_path = output_dir.with_suffix" in line:
                indent = re.match(r"^(\s*)", line).group(1)
                previous = "\n".join(new_lines[-8:])

                if "scrivi_effetti_web_ai_its(output_dir)" not in previous:
                    new_lines.append(indent + "scrivi_effetti_web_ai_its(output_dir)")

            new_lines.append(line)

        text = "\n".join(new_lines) + "\n"

    CREATE_PACKAGE.write_text(text, encoding="utf-8")

    return {
        "changed": text != original,
        "has_helper": marker in text,
        "has_call": "scrivi_effetti_web_ai_its(output_dir)" in text,
    }


def patch_android_zip():
    if not ANDROID_AI_ZIP.exists():
        return {
            "zip": str(ANDROID_AI_ZIP),
            "exists": False,
            "updated": False,
        }

    targets = [
        "quizengine/FinalRewardEngine.kt",
        "2_FILE_DA_COPIARE/app/src/main/java/com/alex/quizengine/FinalRewardEngine.kt",
        "app/src/main/java/com/alex/quizengine/FinalRewardEngine.kt",
    ]

    with tempfile.TemporaryDirectory() as tmp:
        temp_zip = Path(tmp) / "android-ai.tmp.zip"

        with zipfile.ZipFile(ANDROID_AI_ZIP, "r") as old:
            with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as new:
                existing = set()

                for item in old.infolist():
                    name = item.filename.replace("\\", "/")
                    existing.add(name)

                    if name in targets:
                        continue

                    new.writestr(item, old.read(item.filename))

                for target in targets:
                    new.writestr(target, ANDROID_REWARD_ENGINE + "\n")

        shutil.move(str(temp_zip), ANDROID_AI_ZIP)

    return {
        "zip": str(ANDROID_AI_ZIP),
        "exists": True,
        "updated": True,
        "targets": targets,
    }


def main():
    results = []

    RUNTIME_WEB_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUNTIME_WEB_DIR / "ai-effects.css", WEB_EFFECTS_CSS)
    write_text(RUNTIME_WEB_DIR / "ai-effects.js", WEB_EFFECTS_JS)

    results.append(install_web_effects_in_folder(DEMO_AI_DIR))
    create_result = patch_create_quiz_package()
    android_result = patch_android_zip()

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Applicazione effetti AI ITS",
        "",
        "Effetti applicati:",
        "",
        "- coriandoli su risposta corretta per web;",
        "- premi finali variabili anche con lo stesso voto;",
        "- frasi motivazionali;",
        "- disegno/emoji premio;",
        "- runtime web riutilizzabile;",
        "- motore Kotlin Android riutilizzabile.",
        "",
        "## Demo AI",
        "",
    ]

    for result in results:
        lines.append(f"- `{result['folder']}` — esiste: {result['exists']}, HTML modificati: {result.get('changed_html', 0)}")

    lines.extend([
        "",
        "## Pacchetto personalizzato",
        "",
        f"- Helper in `scripts/create_quiz_package.py`: {create_result['has_helper']}",
        f"- Chiamata prima dello ZIP: {create_result['has_call']}",
        f"- File modificato: {create_result['changed']}",
        "",
        "## Android AI",
        "",
        f"- Zip esiste: {android_result['exists']}",
        f"- Zip aggiornato: {android_result['updated']}",
    ])

    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("===== APPLICA EFFETTI AI ITS =====")
    print("OK: runtime web AI ITS scritto in runtime/web.")
    print("OK: demo-ai aggiornata con ai-effects.css/js.")
    print("OK: create_quiz_package.py aggiornato per pacchetti personalizzati AI ITS.")
    print("OK: Android AI zip aggiornato con FinalRewardEngine.kt." if android_result["updated"] else "ATTENZIONE: Android AI zip non trovato.")
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
