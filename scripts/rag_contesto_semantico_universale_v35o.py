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
REPORT = ROOT / "reports/rag_contesto_semantico_universale_v35o.md"

CONTROL_KEY = "contesto_semantico_universale_v35o"
CONTROL_NAME = "Contesto semantico universale V35O"

TECHNICAL_KEYS = {
    "id", "slug", "key", "chiave", "codice", "code",
    "path", "file", "source_file", "engine", "motore", "script",
    "mappa", "mappa_opzioni", "mappa_opzioni_v35d",
    "controlli", "controlli_qualita", "checks", "quality", "qualita",
    "debug", "metadata", "meta", "hash", "score", "ok",
    "valid", "errore", "errori", "warnings", "versione",
    "creato_il", "pipeline",
}

TEXT_KEYS = {
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

STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "ma", "anche", "come", "che", "quando", "dove",
    "del", "dello", "della", "dei", "degli", "delle",
    "al", "allo", "alla", "ai", "agli", "alle",
    "dal", "dallo", "dalla", "dai", "dagli", "dalle",
    "nel", "nello", "nella", "nei", "negli", "nelle",
    "sul", "sullo", "sulla", "sui", "sugli", "sulle",
    "questo", "questa", "questi", "queste",
    "serve", "aiuta", "può", "puo", "deve", "essere",
    "sono", "viene", "vengono", "fare", "fatto", "modo",
    "più", "piu", "molto", "bene", "male", "importante",
}

DOMAIN_RULES = [
    {
        "tema": "sicurezza informatica",
        "keywords": ["sicurezza", "password", "account", "phishing", "backup", "malware", "dati", "accesso", "autenticazione", "rete", "sistema"],
        "subtopics": [
            ("password e account", ["password", "account", "credenziali", "accesso", "autenticazione"]),
            ("phishing e inganni digitali", ["phishing", "email", "messaggio", "link", "inganno", "truffa"]),
            ("backup e recupero dati", ["backup", "recupero", "copia", "dati", "ripristino"]),
            ("protezione dati e sistemi", ["dati", "sistema", "rete", "malware", "protezione", "sicurezza"]),
        ],
    },
    {
        "tema": "formazione aziendale",
        "keywords": ["azienda", "formazione", "procedura", "processo", "responsabilità", "ruolo", "regola", "operativo"],
        "subtopics": [
            ("procedure operative", ["procedura", "processo", "passaggi", "operativo"]),
            ("ruoli e responsabilità", ["ruolo", "responsabilità", "team", "azienda"]),
            ("apprendimento e verifica", ["formazione", "test", "studio", "verifica"]),
        ],
    },
    {
        "tema": "studio e apprendimento",
        "keywords": ["studio", "domanda", "test", "risposta", "spiegazione", "concetto", "ripasso", "lezione"],
        "subtopics": [
            ("domande e verifica", ["domanda", "test", "risposta", "quiz"]),
            ("riassunto e ripasso", ["riassunto", "ripasso", "concetto", "lezione"]),
        ],
    },
    {
        "tema": "sport e allenamento",
        "keywords": ["allenamento", "sport", "esercizio", "recupero", "forza", "resistenza", "peso", "muscolo"],
        "subtopics": [
            ("programma di allenamento", ["programma", "allenamento", "esercizio"]),
            ("recupero e progressione", ["recupero", "progressione", "carico"]),
        ],
    },
    {
        "tema": "curriculum e profilo professionale",
        "keywords": ["curriculum", "esperienza", "competenza", "lavoro", "profilo", "candidato", "azienda"],
        "subtopics": [
            ("esperienze professionali", ["esperienza", "lavoro", "azienda"]),
            ("competenze e obiettivi", ["competenza", "profilo", "obiettivo"]),
        ],
    },
]

CATEGORY_RULES = [
    ("rischio", ["rischio", "pericolo", "minaccia", "danno", "problema"]),
    ("azione operativa", ["fare", "applicare", "usare", "seguire", "controllare", "verificare", "cambiare", "proteggere"]),
    ("regola", ["deve", "bisogna", "regola", "obbligo", "richiede"]),
    ("spiegazione", ["perché", "perche", "significa", "spiega", "motivo"]),
    ("definizione", ["è", "sono", "definizione", "indica", "rappresenta"]),
    ("esempio", ["esempio", "caso", "situazione"]),
]


def key_name(key: str | None) -> str:
    return str(key or "").lower()


def is_text_key(key: str | None) -> bool:
    k = key_name(key)
    if not k or k in TECHNICAL_KEYS:
        return False
    if k in TEXT_KEYS:
        return True
    return any(part in TEXT_KEYS for part in re.split(r"[_\-.]+", k))


def normalize(text: str) -> str:
    text = str(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def collect_texts(value: Any, parent_key: str | None = None, out: list[str] | None = None) -> list[str]:
    if out is None:
        out = []

    if isinstance(value, dict):
        for k, v in value.items():
            if key_name(k) not in TECHNICAL_KEYS:
                collect_texts(v, k, out)
        return out

    if isinstance(value, list):
        for item in value:
            collect_texts(item, parent_key, out)
        return out

    if isinstance(value, str) and is_text_key(parent_key):
        t = normalize(value)
        if t:
            out.append(t)

    return out


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", text.lower())


def score_words(words: list[str]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for w in words:
        if len(w) < 4:
            continue
        if w in STOPWORDS:
            continue
        scores[w] = scores.get(w, 0) + 1
    return scores


def choose_theme(all_text: str) -> tuple[str, str]:
    low = all_text.lower()
    best_theme = "generale"
    best_score = 0
    best_rule: dict[str, Any] | None = None

    for rule in DOMAIN_RULES:
        score = sum(low.count(k) for k in rule["keywords"])
        if score > best_score:
            best_score = score
            best_theme = rule["tema"]
            best_rule = rule

    if not best_rule:
        return best_theme, "contenuto generale"

    best_subtopic = "contenuto generale"
    best_sub_score = 0

    for name, keys in best_rule["subtopics"]:
        score = sum(low.count(k) for k in keys)
        if score > best_sub_score:
            best_sub_score = score
            best_subtopic = name

    return best_theme, best_subtopic


def choose_category(text: str) -> tuple[str, str]:
    low = text.lower()
    best = "contenuto informativo"
    best_score = 0

    for category, keys in CATEGORY_RULES:
        score = sum(low.count(k) for k in keys)
        if score > best_score:
            best_score = score
            best = category

    if best == "rischio":
        return best, "prevenzione o riduzione del rischio"
    if best == "azione operativa":
        return best, "comportamento da applicare"
    if best == "regola":
        return best, "indicazione da rispettare"
    if best == "spiegazione":
        return best, "motivo o conseguenza"
    if best == "definizione":
        return best, "significato del concetto"
    if best == "esempio":
        return best, "caso concreto"

    return best, "informazione principale"


def extract_micro_concepts(text: str, max_items: int = 6) -> list[str]:
    words = tokens(text)
    clean = [w for w in words if len(w) >= 4 and w not in STOPWORDS]

    phrases: dict[str, int] = {}

    for n in (3, 2):
        for i in range(0, max(0, len(clean) - n + 1)):
            phrase_words = clean[i:i+n]
            if len(set(phrase_words)) < n:
                continue
            phrase = " ".join(phrase_words)
            phrases[phrase] = phrases.get(phrase, 0) + 1

    sorted_phrases = sorted(phrases.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))

    result = []
    for phrase, _score in sorted_phrases:
        if len(result) >= max_items:
            break
        if not any(phrase in existing or existing in phrase for existing in result):
            result.append(phrase)

    if result:
        return result

    scores = score_words(words)
    return [w for w, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:max_items]]


def build_context_for_text(text: str, global_theme: str, global_subtopic: str) -> dict[str, Any]:
    category, subcategory = choose_category(text)
    micro = extract_micro_concepts(text)

    return {
        "tema": global_theme,
        "sottotema": global_subtopic,
        "categoria": category,
        "sottocategoria": subcategory,
        "micro_concetti": micro,
        "oggetto_probabile": choose_object(global_theme, global_subtopic, category, micro),
    }


def choose_object(theme: str, subtopic: str, category: str, micro: list[str]) -> str:
    joined = " ".join(micro).lower()
    base = f"{theme} / {subtopic}"

    if "password" in joined or "account" in joined or "access" in joined:
        return "accessi non autorizzati agli account"
    if "phishing" in joined or "email" in joined or "link" in joined:
        return "tentativi di inganno e furto di dati"
    if "backup" in joined or "recupero" in joined or "dati" in joined:
        return "perdita dei dati o difficoltà di recupero"
    if "procedura" in joined or "processo" in joined:
        return "errori nell'applicazione della procedura"
    if "test" in joined or "domanda" in joined:
        return "comprensione incompleta del contenuto"
    if "allenamento" in joined or "esercizio" in joined:
        return "errori nella gestione dell'allenamento"
    if micro:
        return micro[0]

    if theme == "sicurezza informatica":
        return "dati, account e sistemi"
    if theme == "formazione aziendale":
        return "processi, responsabilità e attività operative"

    return base


def add_context_to_node(value: Any, global_theme: str, global_subtopic: str, stats: dict[str, int], parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        result = {}
        local_texts: list[str] = []

        for k, v in value.items():
            if key_name(k) not in TECHNICAL_KEYS:
                local_texts.extend(collect_texts(v, k, []))

        local_text = " ".join(local_texts).strip()

        for k, v in value.items():
            if key_name(k) in TECHNICAL_KEYS:
                result[k] = v
            else:
                result[k] = add_context_to_node(v, global_theme, global_subtopic, stats, k)

        if local_text and "contesto_semantico_v35o" not in result:
            result["contesto_semantico_v35o"] = build_context_for_text(local_text, global_theme, global_subtopic)
            stats["nodes"] += 1

        return result

    if isinstance(value, list):
        return [add_context_to_node(item, global_theme, global_subtopic, stats, parent_key) for item in value]

    return value


def process_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = " ".join(collect_texts(data))
    global_theme, global_subtopic = choose_theme(all_text)

    stats = {
        "nodes": 0,
        "theme": global_theme,
        "subtopic": global_subtopic,
    }

    cleaned = add_context_to_node(data, global_theme, global_subtopic, stats)

    if not isinstance(cleaned, dict):
        raise RuntimeError(f"JSON non valido per V35O: {path}")

    quality = dict(cleaned.get("controlli_qualita", {}))
    quality[CONTROL_KEY] = {
        "ok": True,
        "nome": CONTROL_NAME,
        "tema_documento": global_theme,
        "sottotema_documento": global_subtopic,
        "nodi_con_contesto": stats["nodes"],
        "nota": "Aggiunge tema, sottotema, categoria, sottocategoria, micro-concetti e oggetto probabile ai blocchi testuali.",
    }
    quality["ok"] = bool(quality.get("ok", True))
    cleaned["controlli_qualita"] = quality

    motors = dict(cleaned.get("motori_riutilizzabili", {}))
    motors["contesto_semantico"] = "rag_contesto_semantico_universale_v35o"
    cleaned["motori_riutilizzabili"] = motors

    cleaned["contesto_documento_v35o"] = {
        "ok": True,
        "tema": global_theme,
        "sottotema": global_subtopic,
        "creato_il": datetime.now().isoformat(timespec="seconds"),
    }

    path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "path": path,
        "ok": True,
        **stats,
    }


def default_targets() -> list[Path]:
    bases = [
        ROOT / "dist/generated/rag_output_cleaner_finale_v35k",
        ROOT / "dist/generated/rag_pipeline_unica_ufficiale",
    ]

    targets: list[Path] = []
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
        "# RAG Contesto Semantico Universale V35O",
        "",
        f"- Creato il: {datetime.now().isoformat(timespec='seconds')}",
        f"- File controllati: {len(results)}",
        "",
        "## Cosa fa",
        "",
        "- Riconosce tema documento.",
        "- Riconosce sottotema documento.",
        "- Aggiunge categoria e sottocategoria ai blocchi testuali.",
        "- Estrae micro-concetti da 2 o 3 parole.",
        "- Ricava un oggetto probabile utile al completatore frasi V35N.",
        "- Non modifica i testi visibili.",
        "- Prepara anche una futura base per pulizia OCR contestuale.",
        "",
        "## File",
        "",
    ]

    for result in results:
        rel = result["path"].relative_to(ROOT) if result["path"].is_relative_to(ROOT) else result["path"]
        lines.append(
            f"- `{rel}`: tema `{result['theme']}`, sottotema `{result['subtopic']}`, "
            f"nodi con contesto {result['nodes']}"
        )

    lines += ["", "ESITO: OK", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Contesto Semantico Universale V35O")
    parser.add_argument("--file", action="append", default=[], help="JSON specifico da arricchire con contesto")
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
        raise SystemExit("ERRORE: nessun JSON trovato per V35O")

    results = []
    print("=== RAG CONTESTO SEMANTICO UNIVERSALE V35O ===")

    for target in targets:
        if not target.exists():
            raise SystemExit(f"ERRORE: file mancante {target}")
        result = process_file(target)
        results.append(result)
        rel = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
        print(
            f"OK: {rel} - tema {result['theme']} - sottotema {result['subtopic']} "
            f"- nodi {result['nodes']}"
        )

    write_report(results)

    print(f"Report: {REPORT.relative_to(ROOT)}")
    print("ESITO: OK")


if __name__ == "__main__":
    main()
