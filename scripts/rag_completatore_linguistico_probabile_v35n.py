#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_completatore_linguistico_probabile_v35n.md"

CONTROL_KEY = "completatore_linguistico_probabile_v35n"
CONTROL_NAME = "Completatore linguistico probabile V35N"

TECHNICAL_KEYS = {
    "id", "slug", "key", "chiave", "codice", "code",
    "path", "file", "source_file", "engine", "motore", "script",
    "mappa", "mappa_opzioni", "mappa_opzioni_v35d",
    "controlli", "controlli_qualita", "checks", "quality", "qualita",
    "debug", "metadata", "meta", "hash", "score", "ok",
    "valid", "errore", "errori", "warnings", "versione",
    "creato_il", "pipeline",
    "contesto_semantico_v35o",
}

VISIBLE_KEYS = {
    "titolo", "title", "sottotitolo", "subtitle",
    "testo", "text", "contenuto", "content", "descrizione", "description",
    "riassunto", "summary", "paragrafo", "paragraph",
    "domanda", "question", "domanda_visibile",
    "risposta", "answer", "risposta_guida",
    "spiegazione", "explanation", "feedback",
    "opzione", "opzioni", "options", "opzioni_visibili", "risposte", "choices",
    "conclusione", "messaggio_chiave", "fonte_visibile",
    "categoria", "categorie", "categoria_didattica", "sottocategoria",
    "badge", "label", "etichette", "note", "nota",
}

QUESTION_KEYS = {"domanda", "question", "domanda_visibile"}

DIRECT_TYPO_REPLACEMENTS = {
    "coterro": "corretto",
    "coritto": "corretto",
    "corrretto": "corretto",
    "coretto": "corretto",
    "correto": "corretto",
    "corrreto": "corretto",
    "sbaglaito": "sbagliato",
    "sbaglato": "sbagliato",
    "concllusa": "conclusa",
    "coclusa": "conclusa",
    "cocluso": "concluso",
    "nonsia": "non sia",
    "probbabbili": "probabili",
    "probabbili": "probabili",
    "probbabile": "probabile",
    "probabbile": "probabile",
    "pachetto": "pacchetto",
    "riasssunto": "riassunto",
    "generstore": "generatore",
    "qualita": "qualità",
    "perche": "perché",
    "piu": "più",
    "puo": "può",
    "cioe": "cioè",
}

SAFE_DICTIONARY = [
    "corretto", "sbagliato", "conclusa", "concluso", "probabile", "probabili",
    "pacchetto", "riassunto", "generatore", "qualità", "perché", "più", "può",
    "cioè", "documento", "sicurezza", "password", "account", "accesso",
    "dati", "sistemi", "rischio", "procedura", "formazione", "domanda",
    "risposta", "spiegazione", "contesto", "categoria", "sottocategoria",
    "tema", "sottotema", "micro", "concetti", "frase", "parole",
]

SUSPICIOUS_FINALS = {
    "che", "quando", "perché", "perche", "poiché", "poiche",
    "se", "mentre", "dove", "come", "quanto",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "del", "della", "dello", "dei", "degli", "delle",
    "il", "lo", "la", "gli", "le", "un", "una", "uno",
    "senza", "verso", "contro", "durante", "attraverso",
}


def normalize_spaces(text: str) -> str:
    text = str(text or "").replace("\u00a0", " ").replace("’", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,;:!?])(?=[^\s»”\")\]\}])", r"\1 ", text)
    return re.sub(r"\s+", " ", text).strip()


def key_name(key: str | None) -> str:
    return str(key or "").lower()


def is_visible_key(key: str | None) -> bool:
    k = key_name(key)
    if not k or k in TECHNICAL_KEYS:
        return False
    if k in VISIBLE_KEYS:
        return True
    return any(part in VISIBLE_KEYS for part in re.split(r"[_\-.]+", k))


def preserve_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def correct_typos(text: str) -> tuple[str, int]:
    changes = 0

    def repl(match: re.Match) -> str:
        nonlocal changes
        word = match.group(0)
        low = word.lower()

        if low in DIRECT_TYPO_REPLACEMENTS:
            changes += 1
            return preserve_case(word, DIRECT_TYPO_REPLACEMENTS[low])

        # Correzione prudente: solo parole abbastanza lunghe e molto simili.
        if len(low) >= 6:
            candidate = difflib.get_close_matches(low, SAFE_DICTIONARY, n=1, cutoff=0.82)
            if candidate and candidate[0] != low:
                changes += 1
                return preserve_case(word, candidate[0])

        return word

    text = re.sub(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", repl, text)
    return text, changes


def last_word(text: str) -> str:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", text.lower())
    return words[-1] if words else ""


def context_object(context: dict | None, text: str) -> str:
    context = context or {}

    obj = str(context.get("oggetto_probabile") or "").strip()
    if obj:
        return obj

    micro = context.get("micro_concetti") or []
    if isinstance(micro, list) and micro:
        return str(micro[0])

    sottotema = str(context.get("sottotema") or "").strip()
    if sottotema:
        return sottotema

    tema = str(context.get("tema") or "").strip()
    if tema and tema != "generale":
        return tema

    low = text.lower()
    if "password" in low or "account" in low:
        return "accessi non autorizzati agli account"
    if "phishing" in low:
        return "tentativi di inganno e furto di dati"
    if "backup" in low or "dati" in low:
        return "perdita o mancato recupero dei dati"
    if "sicurezza" in low:
        return "dati, account e sistemi"

    return "il contenuto descritto"


def completion_for(text: str, final_word: str, context: dict | None) -> str:
    obj = context_object(context, text)

    if final_word in {"perché", "perche", "poiché", "poiche"}:
        return f" aiuta a ridurre il rischio di {obj}"
    if final_word == "quando":
        return " si presenta una situazione concreta"
    if final_word == "che":
        return f" riguarda {obj}"
    if final_word == "se":
        return " la situazione lo richiede"
    if final_word in {"per", "a"}:
        return f" ridurre il rischio di {obj}"
    if final_word in {"di", "del", "della", "dello", "dei", "degli", "delle"}:
        return f" {obj}"
    if final_word in {"con", "in", "su"}:
        return " un criterio coerente"
    if final_word in {"tra", "fra"}:
        return " gli elementi collegati"
    if final_word in {"il", "lo", "la", "gli", "le", "un", "una", "uno"}:
        return " contenuto principale"
    if final_word == "senza":
        return " perdere il significato principale"

    return ""


def complete_suspended_sentence(text: str, key: str | None, context: dict | None) -> tuple[str, bool]:
    k = key_name(key)

    if k in {"titolo", "title", "sottotitolo", "subtitle", "categoria", "badge", "label", "fonte_visibile"}:
        return text, False

    stripped = text.rstrip(" .!?;:,")
    final = last_word(stripped)

    if final not in SUSPICIOUS_FINALS:
        return text, False

    addition = completion_for(stripped, final, context)
    if not addition:
        return text, False

    completed = normalize_spaces(stripped + addition)
    completed = ensure_end(completed, key)
    return completed, completed != text


def complete_generic_closed_sentence(text: str, key: str | None, context: dict | None) -> tuple[str, bool]:
    obj = context_object(context, text)

    replacements = [
        (r"\baiuta a ridurre il rischio\.$", f"aiuta a ridurre il rischio di {obj}."),
        (r"\bserve a ridurre il rischio\.$", f"serve a ridurre il rischio di {obj}."),
        (r"\bpermette di ridurre il rischio\.$", f"permette di ridurre il rischio di {obj}."),
        (r"\baiuta a evitare problemi\.$", f"aiuta a evitare problemi legati a {obj}."),
        (r"\bserve a evitare problemi\.$", f"serve a evitare problemi legati a {obj}."),
    ]

    for pattern, replacement in replacements:
        new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        if new_text != text:
            return normalize_spaces(new_text), True

    return text, False


def ensure_end(text: str, key: str | None) -> str:
    k = key_name(key)
    if not text:
        return text

    if k in QUESTION_KEYS or "domanda" in k or "question" in k:
        return text.rstrip(".!") + "?"

    if k in {"titolo", "title", "sottotitolo", "subtitle", "categoria", "badge", "label", "fonte_visibile"}:
        return text

    if text[-1] not in ".!?»”":
        return text + "."

    return text


def clean_text(value: str, key: str | None, context: dict | None = None) -> tuple[str, dict[str, int]]:
    stats = {"typos": 0, "completed": 0, "changed": 0}

    before = str(value or "")
    text = normalize_spaces(before)

    text, typo_count = correct_typos(text)
    stats["typos"] += typo_count

    text, completed = complete_suspended_sentence(text, key, context)
    if completed:
        stats["completed"] += 1

    text = ensure_end(text, key)

    text, completed_generic = complete_generic_closed_sentence(text, key, context)
    if completed_generic:
        stats["completed"] += 1

    text = normalize_spaces(text)

    if text != before:
        stats["changed"] += 1

    return text, stats


def walk(value: Any, parent_key: str | None, totals: dict[str, int], context: dict | None = None) -> Any:
    if isinstance(value, dict):
        local_context = value.get("contesto_semantico_v35o") if isinstance(value.get("contesto_semantico_v35o"), dict) else context
        result = {}
        for k, v in value.items():
            if key_name(k) in TECHNICAL_KEYS or k == "contesto_semantico_v35o":
                result[k] = v
            else:
                result[k] = walk(v, k, totals, local_context)
        return result

    if isinstance(value, list):
        return [walk(item, parent_key, totals, context) for item in value]

    if isinstance(value, str) and is_visible_key(parent_key):
        totals["checked"] += 1
        cleaned, stats = clean_text(value, parent_key, context)
        totals["typos"] += stats["typos"]
        totals["completed"] += stats["completed"]
        totals["changed"] += stats["changed"]
        return cleaned

    return value


def add_metadata(data: dict[str, Any], totals: dict[str, int], file_path: Path) -> dict[str, Any]:
    final = deepcopy(data)

    quality = dict(final.get("controlli_qualita", {}))
    quality[CONTROL_KEY] = {
        "ok": True,
        "nome": CONTROL_NAME,
        "testi_controllati": totals["checked"],
        "parole_corrette": totals["typos"],
        "frasi_completate": totals["completed"],
        "modifiche_visibili": totals["changed"],
        "usa_contesto_v35o": True,
    }
    quality["ok"] = bool(quality.get("ok", True))
    final["controlli_qualita"] = quality

    motors = dict(final.get("motori_riutilizzabili", {}))
    motors["completatore_linguistico_probabile"] = "rag_completatore_linguistico_probabile_v35n"
    final["motori_riutilizzabili"] = motors

    final["revisione_completamento_linguistico_v35n"] = {
        "ok": True,
        "nome": CONTROL_NAME,
        "creato_il": datetime.now().isoformat(timespec="seconds"),
        **totals,
    }

    return final


def clean_json_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    totals = {"checked": 0, "typos": 0, "completed": 0, "changed": 0}

    cleaned = walk(data, None, totals, None)
    if not isinstance(cleaned, dict):
        raise RuntimeError(f"JSON non valido per V35N: {path}")

    final = add_metadata(cleaned, totals, path)
    path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"path": path, "ok": True, **totals}


def default_targets() -> list[Path]:
    bases = [
        ROOT / "dist/generated/rag_output_cleaner_finale_v35k",
        ROOT / "dist/generated/rag_pipeline_unica_ufficiale",
    ]

    targets = []
    for base in bases:
        if base.exists():
            targets.extend(sorted(base.rglob("*.json")))

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
        "# RAG Completatore Linguistico Probabile V35N",
        "",
        f"- Creato il: {datetime.now().isoformat(timespec='seconds')}",
        f"- File controllati: {len(results)}",
        f"- Testi controllati: {sum(r['checked'] for r in results)}",
        f"- Parole corrette: {sum(r['typos'] for r in results)}",
        f"- Frasi completate: {sum(r['completed'] for r in results)}",
        f"- Modifiche visibili: {sum(r['changed'] for r in results)}",
        "",
        "## Cosa fa",
        "",
        "- Usa il contesto V35O quando presente.",
        "- Completa frasi sospese.",
        "- Completa frasi chiuse ma troppo generiche.",
        "- Corregge parole sbagliate comuni e parole molto simili a un dizionario sicuro.",
        "- Non modifica campi tecnici.",
        "",
        "## File",
        "",
    ]

    for r in results:
        rel = r["path"].relative_to(ROOT) if r["path"].is_relative_to(ROOT) else r["path"]
        lines.append(f"- `{rel}`: testi {r['checked']}, parole {r['typos']}, frasi {r['completed']}, modifiche {r['changed']}")

    lines += ["", "ESITO: OK", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Completatore Linguistico Probabile V35N")
    parser.add_argument("--file", action="append", default=[])
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
        raise SystemExit("ERRORE: nessun JSON trovato per V35N")

    results = []
    print("=== RAG COMPLETATORE LINGUISTICO PROBABILE V35N ===")
    for target in targets:
        if not target.exists():
            raise SystemExit(f"ERRORE: file mancante {target}")
        r = clean_json_file(target)
        results.append(r)
        rel = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
        print(f"OK: {rel} - testi {r['checked']} - parole {r['typos']} - frasi {r['completed']} - modifiche {r['changed']}")

    write_report(results)
    print(f"Report: {REPORT.relative_to(ROOT)}")
    print("ESITO: OK")


if __name__ == "__main__":
    main()
