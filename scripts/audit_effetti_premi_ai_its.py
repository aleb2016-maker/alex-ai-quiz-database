from pathlib import Path
import zipfile

REPORT = Path("reports/audit_effetti_premi_ai_its.md")

KEYWORDS = [
    "confetti",
    "coriandoli",
    "premio",
    "premi",
    "reward",
    "rewards",
    "giudizio",
    "giudizi",
    "motivaz",
    "frase",
    "frasi",
    "finale",
    "risultato",
    "risultati",
    "voto",
    "stelle",
    "badge",
    "achievement",
    "celebration",
    "corretta",
    "risposta corretta",
    "success",
    "green",
    "verde",
]

TEXT_EXT = {
    ".html",
    ".js",
    ".css",
    ".json",
    ".md",
    ".kt",
    ".xml",
    ".py",
}

SCAN_DIRS = [
    Path("demo"),
    Path("demo-ai"),
    Path("demo-scienze"),
    Path("runtime"),
    Path("scripts"),
    Path(".github/workflows"),
]

SCAN_FILES = [
    Path("README.md"),
    Path("START_HERE.md"),
]

SCAN_ZIPS = [
    Path("downloads/pacchetto-web-ai-its-demo.zip"),
    Path("downloads/pacchetto-android-ai-its-finale-semplice.zip"),
    Path("downloads/pacchetto-web-scienze-demo.zip"),
    Path("downloads/pacchetto-android-scienze-finale-semplice.zip"),
]


def contiene_keyword(testo):
    testo_basso = testo.lower()
    trovate = []

    for keyword in KEYWORDS:
        if keyword.lower() in testo_basso:
            trovate.append(keyword)

    return trovate


def righe_interessanti(testo):
    risultati = []

    for numero, riga in enumerate(testo.splitlines(), 1):
        riga_bassa = riga.lower()

        if any(keyword.lower() in riga_bassa for keyword in KEYWORDS):
            risultati.append((numero, riga.strip()))

    return risultati


def file_da_scansionare():
    paths = []

    for cartella in SCAN_DIRS:
        if not cartella.exists():
            continue

        for path in cartella.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_EXT:
                if ".git" in path.parts:
                    continue
                if ".venv" in path.parts:
                    continue
                if "node_modules" in path.parts:
                    continue
                paths.append(path)

    for path in SCAN_FILES:
        if path.exists():
            paths.append(path)

    return sorted(set(paths))


def analizza_file(path):
    testo = path.read_text(encoding="utf-8", errors="ignore")
    keywords = contiene_keyword(testo)

    if not keywords:
        return None

    return {
        "path": str(path),
        "keywords": keywords,
        "righe": righe_interessanti(testo)[:40],
    }


def analizza_zip(path):
    if not path.exists():
        return {
            "path": str(path),
            "esiste": False,
            "matches": [],
        }

    matches = []

    with zipfile.ZipFile(path, "r") as archive:
        for name in archive.namelist():
            suffix = Path(name).suffix.lower()

            if suffix not in TEXT_EXT:
                continue

            try:
                testo = archive.read(name).decode("utf-8", errors="ignore")
            except Exception:
                continue

            keywords = contiene_keyword(testo)

            if keywords:
                matches.append({
                    "file": name,
                    "keywords": keywords,
                    "righe": righe_interessanti(testo)[:25],
                })

    return {
        "path": str(path),
        "esiste": True,
        "matches": matches,
    }


def stampa_file_match(match):
    print()
    print(match["path"])
    print("keyword:", ", ".join(match["keywords"]))

    for numero, riga in match["righe"][:20]:
        print(f"  {numero}: {riga}")


def stampa_zip_match(match):
    print()
    print(match["path"])

    if not match["esiste"]:
        print("  ZIP NON TROVATO")
        return

    if not match["matches"]:
        print("  nessun effetto/premio trovato")
        return

    for item in match["matches"][:20]:
        print()
        print("  file:", item["file"])
        print("  keyword:", ", ".join(item["keywords"]))

        for numero, riga in item["righe"][:12]:
            print(f"    {numero}: {riga}")


def main():
    print("===== AUDIT EFFETTI / PREMI / CORIANDOLI AI ITS =====")

    matches_file = []

    for path in file_da_scansionare():
        match = analizza_file(path)

        if match:
            matches_file.append(match)

    matches_zip = [analizza_zip(path) for path in SCAN_ZIPS]

    print()
    print("===== FILE LOCALI CON EFFETTI / PREMI =====")

    if not matches_file:
        print("Nessun file locale trovato con keyword effetti/premi.")
    else:
        for match in matches_file:
            stampa_file_match(match)

    print()
    print("===== ZIP CON EFFETTI / PREMI =====")

    for match in matches_zip:
        stampa_zip_match(match)

    righe = [
        "# Audit effetti / premi / coriandoli AI ITS",
        "",
        "Obiettivo: trovare dove sono già presenti effetti, premi finali, frasi motivazionali, giudizi variabili e coriandoli.",
        "",
        "## File locali",
        "",
    ]

    if not matches_file:
        righe.append("- Nessun file locale trovato con keyword effetti/premi.")
    else:
        for match in matches_file:
            righe.append(f"### `{match['path']}`")
            righe.append("")
            righe.append(f"Keyword: {', '.join(match['keywords'])}")
            righe.append("")
            for numero, riga in match["righe"][:30]:
                righe.append(f"- L{numero}: `{riga}`")
            righe.append("")

    righe.append("")
    righe.append("## ZIP")
    righe.append("")

    for match in matches_zip:
        righe.append(f"### `{match['path']}`")
        righe.append("")

        if not match["esiste"]:
            righe.append("- ZIP non trovato.")
            righe.append("")
            continue

        if not match["matches"]:
            righe.append("- Nessun effetto/premio trovato.")
            righe.append("")
            continue

        for item in match["matches"][:20]:
            righe.append(f"- `{item['file']}` — keyword: {', '.join(item['keywords'])}")
            for numero, riga in item["righe"][:12]:
                righe.append(f"  - L{numero}: `{riga}`")
            righe.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print()
    print("Report creato:", REPORT)


if __name__ == "__main__":
    main()
