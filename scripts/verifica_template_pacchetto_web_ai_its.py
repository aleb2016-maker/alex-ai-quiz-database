import importlib.util
import json
import shutil
from pathlib import Path

SCRIPT = Path("scripts/create_quiz_package.py")
TMP = Path("reports/_tmp_verifica_template_web_ai_its")
REPORT = Path("reports/verifica_template_pacchetto_web_ai_its.md")

HTML_VECCHIO = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Quiz Web Interattivo</title>
</head>
<body>
  <h1>Quiz Scienze</h1>
  <p>Scegli materia scientifica, numero di domande e difficoltà. Il pacchetto contiene il database completo, ma il quiz parte solo con le domande che scegli.</p>

  <label>Materia</label>
  <select id="subject">
            <option value="materie_scientifiche">Materie scientifiche - tutte</option>
            <option value="scienze_generali">Scienze generali</option>
            <option value="fisica">Fisica</option>
            <option value="chimica">Chimica</option>
            <option value="biologia">Biologia</option>
  </select>
</body>
</html>
"""


def carica_funzione():
    spec = importlib.util.spec_from_file_location("create_quiz_package_test", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    if not hasattr(modulo, "blinda_interfaccia_web_generata_ai_its"):
        raise SystemExit("ERRORE: funzione blinda_interfaccia_web_generata_ai_its non trovata.")

    return modulo.blinda_interfaccia_web_generata_ai_its


def main():
    if TMP.exists():
        shutil.rmtree(TMP)

    TMP.mkdir(parents=True, exist_ok=True)

    (TMP / "index.html").write_text(HTML_VECCHIO, encoding="utf-8")
    (TMP / "1_APRI_QUIZ.html").write_text(HTML_VECCHIO, encoding="utf-8")

    domande_ai = [
        {
            "id": f"AI-FAC-TEST-{i:04d}",
            "domanda": "Domanda AI di test",
            "opzioni": ["Corretta", "Distrattore 1", "Distrattore 2", "Distrattore 3"],
            "risposta_corretta": "Corretta",
            "spiegazione": "Spiegazione di test."
        }
        for i in range(1, 11)
    ]

    (TMP / "database_quiz.json").write_text(
        json.dumps(domande_ai, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    funzione = carica_funzione()
    funzione(TMP)

    testi = []

    for nome in ["index.html", "1_APRI_QUIZ.html"]:
        testi.append((TMP / nome).read_text(encoding="utf-8"))

    testo_unico = "\n".join(testi)

    errori = []

    richiesti = [
        "Quiz AI",
        '<option value="tutte" selected>AI</option>',
    ]

    vietati = [
        "Quiz Scienze",
        "Materie scientifiche",
        "materie_scientifiche",
        "Scienze generali",
        ">Fisica<",
        ">Chimica<",
        ">Biologia<",
    ]

    for richiesto in richiesti:
        if richiesto not in testo_unico:
            errori.append(f"Testo richiesto assente: {richiesto}")

    for vietato in vietati:
        if vietato in testo_unico:
            errori.append(f"Testo vietato ancora presente: {vietato}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    if errori:
        REPORT.write_text(
            "# Verifica template pacchetto web AI ITS\n\nESITO: ERRORE\n\n"
            + "\n".join(f"- {errore}" for errore in errori),
            encoding="utf-8",
        )

        print("ERRORE: template pacchetto web AI ITS non corretto.")
        for errore in errori:
            print("-", errore)
        raise SystemExit(1)

    REPORT.write_text(
        "# Verifica template pacchetto web AI ITS\n\n"
        "ESITO: OK\n\n"
        "- Il template AI viene rinominato in Quiz AI.\n"
        "- Il menu non mostra più materie scientifiche.\n"
        "- Il pacchetto AI simulato contiene interfaccia AI coerente.\n",
        encoding="utf-8",
    )

    print("OK: template pacchetto web AI ITS corretto.")
    print("OK: un pacchetto AI simulato non mostra più Quiz Scienze.")
    print("OK: un pacchetto AI simulato non mostra più materie scientifiche.")


if __name__ == "__main__":
    main()
