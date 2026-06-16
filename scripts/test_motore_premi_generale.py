from pathlib import Path

root = Path(__file__).resolve().parents[1]

runtime_reward = root / "runtime" / "web" / "final-reward-engine.js"
demo_app = root / "demo" / "app.js"
demo_style = root / "demo" / "style.css"

for file in [runtime_reward, demo_app, demo_style]:
    if not file.exists():
        raise SystemExit(f"ERRORE: file mancante: {file}")

testo_runtime = runtime_reward.read_text(encoding="utf-8")
testo_demo = demo_app.read_text(encoding="utf-8")
testo_css = demo_style.read_text(encoding="utf-8")

controlli_runtime = [
    "window.AlexFinalRewardEngine",
    "creaPremioFinale",
    "mostraPremioFinale",
    "perfetto",
    "eccellente",
    "ottimo",
    "buono",
    "sufficiente",
    "allenamento",
]

controlli_demo = [
    "alexMostraPremioFinaleGenerale",
    "alexLeggiTotaleDomandePremioGenerale",
    "AlexFinalRewardEngine.mostraPremioFinale",
]

controlli_css = [
    ".alex-final-reward-card",
    ".alex-final-reward-drawing",
    ".alex-final-reward-motivation",
]

for controllo in controlli_runtime:
    if controllo not in testo_runtime:
        raise SystemExit(f"ERRORE runtime: manca {controllo}")

for controllo in controlli_demo:
    if controllo not in testo_demo:
        raise SystemExit(f"ERRORE demo: manca {controllo}")

for controllo in controlli_css:
    if controllo not in testo_css:
        raise SystemExit(f"ERRORE CSS: manca {controllo}")

print("OK: motore premi generale presente e collegato alla demo.")
