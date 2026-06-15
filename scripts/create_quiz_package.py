import argparse
import json
import random
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "dist" / "database_quiz_finale.json"
OUTPUT_ROOT = ROOT / "dist" / "generated"

def slug(testo):
    return (
        str(testo or "")
        .strip()
        .lower()
        .replace("à", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
        .replace(" ", "_")
        .replace("-", "_")
    )

def carica_database():
    dati = json.loads(DATABASE_PATH.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        if isinstance(dati.get("quiz"), list):
            return dati["quiz"]
        if isinstance(dati.get("domande"), list):
            return dati["domande"]

    raise ValueError("Formato database non riconosciuto.")

def materia_ok(domanda, materia):
    if materia == "tutte":
        return True

    materia = slug(materia)
    categoria = slug(domanda.get("categoria", ""))
    sottocategoria = slug(domanda.get("sottocategoria", ""))
    tags = domanda.get("tags", [])

    if isinstance(tags, list):
        tags = [slug(tag) for tag in tags]
    else:
        tags = []

    if materia in [categoria, sottocategoria] or materia in tags:
        return True

    if materia == "fisica":
        return "fisica" in sottocategoria or any("fisica" in tag for tag in tags)

    if materia == "chimica":
        return "chimica" in sottocategoria or any("chimica" in tag for tag in tags)

    if materia == "biologia":
        return "biologia" in sottocategoria or any("biologia" in tag for tag in tags)

    return False

def prepara_domande(materia, livello, numero):
    database = carica_database()

    domande = [
        domanda for domanda in database
        if materia_ok(domanda, materia)
        and (livello == "tutti" or domanda.get("livello") == livello)
    ]

    if not domande:
        raise ValueError("Nessuna domanda trovata con questi filtri.")

    random.shuffle(domande)

    if numero != "all":
        domande = domande[:int(numero)]

    return domande

def crea_demo_web(percorso, domande):
    dati_json = json.dumps(domande, ensure_ascii=False)

    html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Apri quiz generato</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      margin: 0;
      font-family: system-ui, sans-serif;
      background: radial-gradient(circle at top left, #155e75, #020617 45%, #111827);
      color: #f8fafc;
    }
    .page {
      max-width: 980px;
      margin: 0 auto;
      padding: 36px 20px;
    }
    .hero, .quiz {
      background: rgba(15, 23, 42, 0.94);
      border: 1px solid rgba(148, 163, 184, 0.32);
      border-radius: 28px;
      padding: 30px;
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
    }
    h1 {
      font-size: clamp(2rem, 5vw, 3.3rem);
      margin: 0 0 12px;
    }
    p {
      color: #cbd5e1;
      line-height: 1.6;
    }
    .start {
      margin-top: 20px;
      padding: 18px 28px;
      border: 0;
      border-radius: 20px;
      background: linear-gradient(135deg, #5eead4, #f0f9a8);
      color: #020617;
      font-size: 1.08rem;
      font-weight: 1000;
      cursor: pointer;
    }
    .quiz {
      margin-top: 28px;
      display: none;
    }
    .top {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      color: #cbd5e1;
      font-weight: 800;
      margin-bottom: 18px;
    }
    .score {
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(34, 197, 94, 0.16);
      color: #bbf7d0;
      white-space: nowrap;
    }
    .question {
      font-size: 1.35rem;
      font-weight: 950;
      line-height: 1.45;
      margin-bottom: 20px;
    }
    .option {
      width: 100%;
      margin: 8px 0;
      padding: 16px 18px;
      border-radius: 18px;
      border: 1px solid rgba(148, 163, 184, 0.35);
      background: rgba(30, 41, 59, 0.96);
      color: #f8fafc;
      text-align: left;
      font-size: 1rem;
      font-weight: 750;
      cursor: pointer;
    }
    .correct { background: rgba(22, 163, 74, 0.9); }
    .wrong { background: rgba(220, 38, 38, 0.9); }
    .disabled { opacity: 0.5; }
    .feedback {
      margin-top: 20px;
      padding: 18px;
      border-radius: 18px;
      background: rgba(2, 6, 23, 0.65);
      display: none;
    }
    .next {
      margin-top: 14px;
      padding: 14px 20px;
      border: 0;
      border-radius: 16px;
      background: linear-gradient(135deg, #5eead4, #f0f9a8);
      color: #020617;
      font-weight: 950;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>Prova subito il tuo test</h1>
      <p>
        Questo è il pacchetto web già pronto. Premi il pulsante e il quiz parte direttamente nel browser.
      </p>
      <button class="start" onclick="startQuiz()">▶ PROVA IL TEST ADESSO</button>
      <p>
        File inclusi: <strong>1_APRI_QUIZ.html</strong>, <strong>README_LEGGIMI.html</strong>, <strong>database_quiz.json</strong>.
      </p>
    </section>

    <section id="quizBox" class="quiz"></section>
  </main>

  <script>
    const quizDatabase = __QUIZ_JSON__;
    let quiz = [];
    let indice = 0;
    let punteggio = 0;
    let bloccato = false;

    function startQuiz() {
      quiz = [...quizDatabase];
      indice = 0;
      punteggio = 0;
      mescola(quiz);
      document.getElementById("quizBox").style.display = "block";
      mostraDomanda();
      document.getElementById("quizBox").scrollIntoView({ behavior: "smooth" });
    }

    function mostraDomanda() {
      bloccato = false;
      const box = document.getElementById("quizBox");
      const domanda = quiz[indice];

      if (!domanda) {
        const percentuale = Math.round((punteggio / quiz.length) * 100);
        box.innerHTML = `
          <h2>Risultato finale</h2>
          <p>Hai risposto correttamente a <strong>${punteggio}</strong> domande su <strong>${quiz.length}</strong>.</p>
          <p>Percentuale: <strong>${percentuale}%</strong></p>
          <button class="next" onclick="startQuiz()">Rifai il test</button>
        `;
        return;
      }

      box.innerHTML = `
        <div class="top">
          <div>Domanda ${indice + 1}/${quiz.length} · ${escapeHtml(domanda.categoria)} · ${escapeHtml(domanda.livello)}</div>
          <div class="score">Punteggio: ${punteggio}</div>
        </div>
        <div class="question">${escapeHtml(domanda.domanda)}</div>
        <div>
          ${(domanda.opzioni || []).map((opzione, i) => `
            <button class="option" data-index="${i}">
              <strong>${String.fromCharCode(65 + i)})</strong> ${escapeHtml(opzione)}
            </button>
          `).join("")}
        </div>
        <div id="feedback" class="feedback"></div>
      `;

      document.querySelectorAll(".option").forEach(button => {
        button.addEventListener("click", () => {
          rispondi(Number(button.dataset.index));
        });
      });
    }

    function rispondi(indiceRisposta) {
      if (bloccato) return;
      bloccato = true;

      const domanda = quiz[indice];
      const risposta = domanda.opzioni[indiceRisposta];
      const corretta = risposta === domanda.risposta_corretta;

      if (corretta) punteggio++;

      document.querySelectorAll(".option").forEach((button, i) => {
        const valore = domanda.opzioni[i];

        if (valore === domanda.risposta_corretta) {
          button.classList.add("correct");
        } else if (i === indiceRisposta) {
          button.classList.add("wrong");
        } else {
          button.classList.add("disabled");
        }
      });

      const feedback = document.getElementById("feedback");
      feedback.style.display = "block";
      feedback.innerHTML = `
        <p><strong>${corretta ? "Corretto." : "Sbagliato."}</strong></p>
        <p>Risposta corretta: <strong>${escapeHtml(domanda.risposta_corretta)}</strong></p>
        <p>${escapeHtml(domanda.spiegazione || "Spiegazione non disponibile.")}</p>
        <button class="next" onclick="indice++; mostraDomanda()">
          ${indice === quiz.length - 1 ? "Vedi risultato finale" : "Domanda successiva"}
        </button>
      `;
    }

    function mescola(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
    }

    function escapeHtml(text) {
      return String(text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }
  </script>
</body>
</html>
""".replace("__QUIZ_JSON__", dati_json)

    leggimi = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Leggimi pacchetto quiz</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 850px; margin: 40px auto; padding: 24px; line-height: 1.6; }
    a { display: inline-block; padding: 18px 24px; border-radius: 14px; background: #16a34a; color: white; font-weight: 900; text-decoration: none; }
  </style>
</head>
<body>
  <h1>Pacchetto quiz web</h1>
  <p>Per provare subito il test apri il file:</p>
  <h2>1_APRI_QUIZ.html</h2>
  <a href="./1_APRI_QUIZ.html">▶ APRI E PROVA IL TEST</a>
</body>
</html>
"""

    (percorso / "1_APRI_QUIZ.html").write_text(html, encoding="utf-8")
    (percorso / "index.html").write_text(html, encoding="utf-8")
    (percorso / "README_LEGGIMI.html").write_text(leggimi, encoding="utf-8")

def crea_readme_pacchetto(percorso, piattaforma, materia, livello, numero):
    testo = f"""# Pacchetto quiz generato

Piattaforma: {piattaforma}
Materia: {materia}
Livello: {livello}
Domande: {numero}

## Web

Apri:

1_APRI_QUIZ.html

## Android

Copia:

app/src/main/assets/database_quiz.json
"""
    (percorso / "README.md").write_text(testo, encoding="utf-8")

def crea_pacchetto(piattaforma, materia, livello, numero):
    domande = prepara_domande(materia, livello, numero)

    nome = f"{piattaforma}_{slug(materia)}_{slug(livello)}_{len(domande)}_domande"
    output_dir = OUTPUT_ROOT / nome

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if piattaforma == "android":
        assets = output_dir / "app" / "src" / "main" / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        (assets / "database_quiz.json").write_text(json.dumps(domande, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        (output_dir / "database_quiz.json").write_text(json.dumps(domande, ensure_ascii=False, indent=2), encoding="utf-8")
        crea_demo_web(output_dir, domande)

    crea_readme_pacchetto(output_dir, piattaforma, materia, livello, len(domande))

    zip_path = output_dir.with_suffix(".zip")

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archivio:
        for file_path in output_dir.rglob("*"):
            archivio.write(file_path, file_path.relative_to(output_dir.parent))

    print(f"Pacchetto creato: {zip_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["android", "web", "demo"], required=True)
    parser.add_argument("--subject", default="scienze")
    parser.add_argument("--level", default="tutti")
    parser.add_argument("--number", default="10")
    args = parser.parse_args()

    crea_pacchetto(args.platform, args.subject, args.level, args.number)

if __name__ == "__main__":
    main()
