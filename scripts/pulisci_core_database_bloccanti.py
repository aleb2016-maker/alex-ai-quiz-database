from pathlib import Path
import json
import shutil
import datetime

ROOT = Path.cwd()
DATA = ROOT / "data"
BACKUPS = ROOT / "backups" / "spostati_da_data"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT = REPORTS / "pulisci_core_database_bloccanti.md"

moved_files = []

# 1. Sposta fuori da data/ i backup JSON non ufficiali.
for path in DATA.glob("*.json"):
    name_lower = path.name.lower()

    if "backup" in name_lower or ".bak" in name_lower:
        target_dir = BACKUPS / STAMP
        target_dir.mkdir(parents=True, exist_ok=True)

        target = target_dir / path.name
        shutil.move(str(path), str(target))

        moved_files.append({
            "from": str(path.relative_to(ROOT)),
            "to": str(target.relative_to(ROOT)),
        })

# 2. Diagnostica MAT-AV-0203 senza modificarla alla cieca.
math_path = DATA / "matematica.json"
math_data = json.loads(math_path.read_text(encoding="utf-8"))

target_question = None

for item in math_data:
    if item.get("id") == "MAT-AV-0203" or item.get("codice") == "MAT-AV-0203":
        target_question = item
        break

lines = [
    "# Pulizia blocchi validatore core",
    "",
    "## Backup spostati fuori da data/",
    "",
]

if moved_files:
    for item in moved_files:
        lines.append(f"- `{item['from']}` → `{item['to']}`")
else:
    lines.append("Nessun backup JSON trovato direttamente dentro `data/`.")

lines.extend([
    "",
    "## Diagnosi MAT-AV-0203",
    "",
])

if target_question is None:
    lines.append("❌ Domanda MAT-AV-0203 non trovata.")
else:
    lines.append("```json")
    lines.append(json.dumps(target_question, ensure_ascii=False, indent=2))
    lines.append("```")

REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("✅ Pulizia backup in data/ completata.")
print(f"Backup spostati: {len(moved_files)}")
print(f"Report: {REPORT}")

if target_question is None:
    print("❌ MAT-AV-0203 non trovata.")
else:
    print("")
    print("----- MAT-AV-0203 -----")
    print(json.dumps(target_question, ensure_ascii=False, indent=2))
