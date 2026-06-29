#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_lucidatore_linguistico_universale_v35m.md"

CONTROL_KEY = "lucidatore_linguistico_universale_v35m"
CONTROL_NAME = "Lucidatore linguistico universale V35M"

VISIBLE_KEYS = {
    "titolo", "title", "sottotitolo", "subtitle",
    "testo", "text", "contenuto", "content", "descrizione", "description",
    "riassunto", "summary", "paragrafo", "paragraph",
    "domanda", "question", "risposta", "answer", "risposta_guida",
    "spiegazione", "explanation", "feedback",
    "opzione", "opzioni", "options", "opzioni_visibili", "risposte", "choices",
    "conclusione", "messaggio_chiave", "fonte_visibile",
    "categoria", "categorie", "categoria_didattica", "sottocategoria",
    "badge", "label", "etichette", "note", "nota",
}

TECHNICAL_KEYS = {
    "id", "slug", "key", "chiave", "codice", "code",
    "path", "file", "source_file", "engine", "motore", "script",
    "mappa", "mappa_opzioni", "mappa_opzioni_v35d",
    "controlli", "controlli_qualita", "checks", "quality", "qualita",
    "debug", "metadata", "meta", "hash", "score", "ok",
    "valid", "errore", "errori", "warnings", "versione",
    "creato_il", "pipeline",
}

ACCENT_REPLACEMENTS = [
    (r"\bperche\b", "perché"),
    (r"\bpoiche\b", "poiché"),
    (r"\baffinche\b", "affinché"),
    (r"\bfinche\b", "finché"),
    (r"\bpuo\b", "può"),
    (r"\bpiu\b", "più"),
    (r"\bgia\b", "già"),
    (r"\bcioe\b", "cioè"),
    (r"\bcosi\b", "così"),
    (r"\bpero\b", "però"),
    (r"\bsara\b", "sarà"),
    (r"\bavra\b", "avrà"),
    (r"\bdovra\b", "dovrà"),
    (r"\bverra\b", "verrà"),
    (r"\bqual e\b", "qual è"),
]

CONTRACTIONS = [
    (r"\bdi\s+il\b", "del"),
    (r"\bdi\s+lo\b", "dello"),
    (r"\bdi\s+la\b", "della"),
    (r"\bdi\s+i\b", "dei"),
    (r"\bdi\s+gli\b", "degli"),
    (r"\bdi\s+le\b", "delle"),
    (r"\ba\s+il\b", "al"),
    (r"\ba\s+lo\b", "allo"),
    (r"\ba\s+la\b", "alla"),
    (r"\ba\s+i\b", "ai"),
    (r"\ba\s+gli\b", "agli"),
    (r"\ba\s+le\b", "alle"),
    (r"\bda\s+il\b", "dal"),
    (r"\bda\s+lo\b", "dallo"),
    (r"\bda\s+la\b", "dalla"),
    (r"\bda\s+i\b", "dai"),
    (r"\bda\s+gli\b", "dagli"),
    (r"\bda\s+le\b", "dalle"),
    (r"\bin\s+il\b", "nel"),
    (r"\bin\s+lo\b", "nello"),
    (r"\bin\s+la\b", "nella"),
    (r"\bin\s+i\b", "nei"),
    (r"\bin\s+gli\b", "negli"),
    (r"\bin\s+le\b", "nelle"),
    (r"\bsu\s+il\b", "sul"),
    (r"\bsu\s+lo\b", "sullo"),
    (r"\bsu\s+la\b", "sulla"),
    (r"\bsu\s+i\b", "sui"),
    (r"\bsu\s+gli\b", "sugli"),
    (r"\bsu\s+le\b", "sulle"),
]

TEXT_ENDING_KEYS = {
    "testo", "text", "contenuto", "content", "descrizione", "description",
    "riassunto", "summary", "paragrafo", "paragraph",
    "risposta", "answer", "risposta_guida",
    "spiegazione", "explanation", "feedback",
    "conclusione", "messaggio_chiave", "note", "nota",
}

QUESTION_KEYS = {"domanda", "question", "domanda_visibile"}


def key_name(key: str | None) -> str:
    return str(key or "").lower()


def is_visible_key(key: str | None) -> bool:
    k = key_name(key)
    if not k:
        return False
    if k in TECHNICAL_KEYS:
        return False
    if k in VISIBLE_KEYS:
        return True
    return any(part in VISIBLE_KEYS for part in re.split(r"[_\-.]+", k))


def normalize_spaces(text: str) -> str:
    text = str(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = re.sub(r"\s+", " ", text).strip()

    # Fonte:Il -> Fonte: Il, Nota:Testo -> Nota: Testo
    text = re.sub(r"\b(Fonte|Nota|Esempio|Risposta|Domanda|Spiegazione):(?=\S)", r"\1: ", text, flags=re.IGNORECASE)

    # Spazio dopo punteggiatura quando manca.
    text = re.sub(r"([,;:!?])(?=[^\s»”\")\]\}])", r"\1 ", text)

    # Non lascia spazio prima della punteggiatura.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Pulisce punteggiatura duplicata.
    text = re.sub(r"\?\s*\?+", "?", text)
    text = re.sub(r"!\s*!+", "!", text)
    text = re.sub(r"\.\s*\.\s*\.+", ".", text)

    # Evita finali tipo ,.
    text = text.replace(",.", ".").replace(";.", ".").replace(":.", ".")
    text = text.replace(",?", "?").replace(";?", "?").replace(":?", "?")
    text = text.replace(".?", "?").replace("?.", "?").replace(".!", "!").replace("!.", "!")

    text = re.sub(r"[,;:]\s*$", ".", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def apply_accents(text: str) -> str:
    for pattern, replacement in ACCENT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def apply_contractions(text: str) -> str:
    for pattern, replacement in CONTRACTIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def apply_apostrophes(text: str) -> str:
    replacements = [
        (r"\bl utente\b", "l'utente"),
        (r"\bd accordo\b", "d'accordo"),
        (r"\bun altra\b", "un'altra"),
        (r"\bun applicazione\b", "un'applicazione"),
        (r"\buna informazione\b", "un'informazione"),
        (r"\buna esperienza\b", "un'esperienza"),
        (r"\buna azione\b", "un'azione"),
        (r"\buna idea\b", "un'idea"),
        (r"\bun po\b", "un po'"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def remove_duplicate_words(text: str) -> str:
    # Rimuove parole duplicate consecutive: "il il", "test test".
    return re.sub(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ0-9']{2,})\s+\1\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )


def remove_duplicate_sentences(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text)
    cleaned: list[str] = []
    last_norm = ""
    for part in parts:
        norm = re.sub(r"[^a-z0-9àèéìòù]+", " ", part.lower()).strip()
        if norm and norm == last_norm:
            continue
        cleaned.append(part)
        if norm:
            last_norm = norm
    return " ".join(cleaned).strip()


def ensure_final_punctuation(text: str, key: str | None) -> str:
    k = key_name(key)

    if not text:
        return text

    if k in QUESTION_KEYS or "domanda" in k or "question" in k:
        return text.rstrip(".!") + "?"

    if k in {"titolo", "title", "sottotitolo", "subtitle", "categoria", "badge", "label", "fonte_visibile"}:
        return text

    if k in TEXT_ENDING_KEYS or any(part in TEXT_ENDING_KEYS for part in re.split(r"[_\-.]+", k)):
        if text[-1] not in ".!?»”":
            text += "."
    return text


def clean_text(value: str, key: str | None) -> str:
    before = str(value or "")
    text = normalize_spaces(before)
    text = apply_accents(text)
    text = apply_contractions(text)
    text = apply_apostrophes(text)
    text = remove_duplicate_words(text)
    text = remove_duplicate_sentences(text)
    text = normalize_spaces(text)
    text = ensure_final_punctuation(text, key)
    text = normalize_spaces(text)
    return text if text else before


def walk_and_clean(value: Any, parent_key: str | None = None, stats: dict[str, int] | None = None) -> Any:
    if stats is None:
        stats = {"checked": 0, "changed": 0}

    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if key_name(k) in TECHNICAL_KEYS:
                result[k] = v
            else:
                result[k] = walk_and_clean(v, k, stats)
        return result

    if isinstance(value, list):
        return [walk_and_clean(item, parent_key, stats) for item in value]

    if isinstance(value, str) and is_visible_key(parent_key):
        stats["checked"] += 1
        cleaned = clean_text(value, parent_key)
        if cleaned != value:
            stats["changed"] += 1
        return cleaned

    return value


def add_metadata(data: dict[str, Any], stats: dict[str, int], file_path: Path) -> dict[str, Any]:
    final = deepcopy(data)

    quality = dict(final.get("controlli_qualita", {}))
    quality[CONTROL_KEY] = {
        "ok": True,
        "nome": CONTROL_NAME,
        "file": str(file_path.relative_to(ROOT)) if file_path.is_relative_to(ROOT) else str(file_path),
        "testi_controllati": stats["checked"],
        "modifiche_visibili": stats["changed"],
        "controlli": [
            "spazi",
            "punteggiatura",
            "accenti_comuni",
            "apostrofi",
            "contrazioni_italiane",
            "parole_duplicate",
            "frasi_duplicate_consecutive",
            "punto_finale",
            "punto_interrogativo_domande",
        ],
    }
    quality["ok"] = bool(quality.get("ok", True))
    final["controlli_qualita"] = quality

    motors = dict(final.get("motori_riutilizzabili", {}))
    motors["lucidatore_linguistico"] = "rag_lucidatore_linguistico_universale_v35m"
    final["motori_riutilizzabili"] = motors

    final["revisione_linguistica_universale_v35m"] = {
        "ok": True,
        "nome": CONTROL_NAME,
        "versione": "rag_lucidatore_linguistico_universale_v35m",
        "creato_il": datetime.now().isoformat(timespec="seconds"),
        "testi_controllati": stats["checked"],
        "modifiche_visibili": stats["changed"],
    }

    return final


def clean_json_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = {"checked": 0, "changed": 0}

    cleaned = walk_and_clean(data, None, stats)
    if not isinstance(cleaned, dict):
        raise RuntimeError(f"JSON non valido per V35M: {path}")

    final = add_metadata(cleaned, stats, path)
    path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "path": path,
        "checked": stats["checked"],
        "changed": stats["changed"],
        "ok": True,
    }


def default_targets() -> list[Path]:
    targets: list[Path] = []

    bases = [
        ROOT / "dist/generated/rag_output_cleaner_finale_v35k",
        ROOT / "dist/generated/rag_pipeline_unica_ufficiale",
    ]

    for base in bases:
        if base.exists():
            targets.extend(sorted(base.rglob("*.json")))

    # Evita duplicati mantenendo ordine.
    seen = set()
    unique = []
    for p in targets:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def write_report(results: list[dict[str, Any]]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# RAG Lucidatore Linguistico Universale V35M",
        "",
        f"- Creato il: {datetime.now().isoformat(timespec='seconds')}",
        f"- File controllati: {len(results)}",
        f"- Testi controllati: {sum(r['checked'] for r in results)}",
        f"- Modifiche visibili: {sum(r['changed'] for r in results)}",
        "",
        "## Controlli eseguiti",
        "",
        "- Spazi doppi e spazi mancanti dopo punteggiatura",
        "- Casi tipo Fonte:Il -> Fonte: Il",
        "- Punteggiatura duplicata o sporca",
        "- Accenti italiani comuni",
        "- Apostrofi comuni",
        "- Contrazioni italiane",
        "- Parole duplicate consecutive",
        "- Frasi duplicate consecutive",
        "- Punto finale nei testi",
        "- Punto interrogativo nelle domande",
        "",
        "## File",
        "",
    ]

    for result in results:
        rel = result["path"].relative_to(ROOT) if result["path"].is_relative_to(ROOT) else result["path"]
        lines.append(f"- `{rel}`: testi {result['checked']}, modifiche {result['changed']}")

    lines += [
        "",
        "ESITO: OK",
        "",
    ]

    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Lucidatore Linguistico Universale V35M")
    parser.add_argument("--file", action="append", default=[], help="JSON specifico da lucidare")
    args = parser.parse_args()

    if args.file:
        targets = []
        for raw in args.file:
            p = Path(raw)
            if not p.is_absolute():
                p = ROOT / p
            targets.append(p)
    else:
        targets = default_targets()

    if not targets:
        raise SystemExit("ERRORE: nessun JSON trovato da lucidare")

    results = []
    print("=== RAG LUCIDATORE LINGUISTICO UNIVERSALE V35M ===")

    for target in targets:
        if not target.exists():
            raise SystemExit(f"ERRORE: file mancante {target}")
        result = clean_json_file(target)
        results.append(result)
        rel = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
        print(f"OK: {rel} - testi {result['checked']} - modifiche {result['changed']}")

    write_report(results)

    print(f"Report: {REPORT.relative_to(ROOT)}")
    print("ESITO: OK")


if __name__ == "__main__":
    main()
