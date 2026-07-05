from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import LEGACY_QUALITY_MOTORS


REPORT_JSON = ROOT / "reports" / "phase5_9_10_quality_capability_matrix_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_10_quality_capability_matrix_v1.md"


SOURCE_ROOTS = [
    ROOT / "backend",
    ROOT / "scripts",
    ROOT / "demo-rag",
    ROOT / "runtime" / "web",
]


SKIP_PARTS = [
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".bak",
]


CAPABILITIES: List[Dict[str, Any]] = [
    {
        "area": "qualita_testuale",
        "capability": "grammatica_italiana_corretta",
        "keywords": ["grammatica", "qualita_linguistica", "controlla_lingua", "frasi complete"],
    },
    {
        "area": "qualita_testuale",
        "capability": "accenti_corretti",
        "keywords": ["perché", "perchè", "può", "più", "già", "cioè", "così", "però", "qual è", "qual e", "accent"],
    },
    {
        "area": "qualita_testuale",
        "capability": "apostrofi_corretti",
        "keywords": ["apostrof", "un’informazione", "un'idea", "l’utente", "d'accordo"],
    },
    {
        "area": "qualita_testuale",
        "capability": "punteggiatura_spazi",
        "keywords": ["punteggiatura", "spazi", "spazi corretti", "prima/dopo punteggiatura"],
    },
    {
        "area": "qualita_testuale",
        "capability": "frasi_complete_non_spezzate",
        "keywords": ["frasi complete", "frasi spezzate", "non terminate", "finali sospetti", "finiscono con"],
    },
    {
        "area": "qualita_testuale",
        "capability": "no_riempitivi_generico_fallback",
        "keywords": ["riempitive", "generico", "documento analizzato", "contenuti generati", "fallback", "demo", "test"],
    },
    {
        "area": "qualita_testuale",
        "capability": "naturalezza_anti_keyword",
        "keywords": ["naturalezza", "anti-keyword", "antikeyword", "frasi robotiche", "keyword", "valore didattico"],
    },
    {
        "area": "qualita_testuale",
        "capability": "accordo_grammaticale_pronomi",
        "keywords": ["accordo", "genere", "numero", "articoli", "participi", "pronomi"],
    },
    {
        "area": "qualita_testuale",
        "capability": "correzione_frasi_non_finite_con_contesto",
        "keywords": ["frasi non finite", "contesto", "tema", "sottotema", "sottocategorie", "lettere invertite"],
    },

    {
        "area": "qualita_didattica",
        "capability": "domande_studio_naturali_utili",
        "keywords": ["domande studio", "study_questions", "naturali", "ripassare", "answer_guide"],
    },
    {
        "area": "qualita_didattica",
        "capability": "risposte_guida_specifiche",
        "keywords": ["risposte guida", "answer_guide", "specifiche", "niente risposte vaghe"],
    },
    {
        "area": "qualita_didattica",
        "capability": "spiegazioni_test_chiare_non_corte",
        "keywords": ["spiegazioni", "explanation", "explanation_draft", "non troppo corte", "feedback"],
    },
    {
        "area": "qualita_didattica",
        "capability": "tono_didattico_categorie_sottocategorie",
        "keywords": ["tono didattico", "categorie", "sottocategorie", "categoria", "sottocategoria"],
    },
    {
        "area": "qualita_didattica",
        "capability": "coerenza_domanda_risposta_contenuto",
        "keywords": ["coerenza", "domanda", "risposta", "contenuto", "source_facts"],
    },

    {
        "area": "card_riassunto_fonti",
        "capability": "card_scritte_bene_non_corte",
        "keywords": ["card", "contenuto_esplicativo", "message_key", "non troppo corte", "compresse"],
    },
    {
        "area": "card_riassunto_fonti",
        "capability": "messaggio_chiave_completo",
        "keywords": ["messaggio chiave", "message_key", "key_points", "completo"],
    },
    {
        "area": "card_riassunto_fonti",
        "capability": "riassunto_chiaro_punti_chiave",
        "keywords": ["riassunto", "summary", "punti chiave", "key_points", "paragrafi"],
    },
    {
        "area": "card_riassunto_fonti",
        "capability": "fonti_visibili_coerenti_belle",
        "keywords": ["fonte", "fonti", "source_pages", "knowledge_base_json", "documento analizzato"],
    },
    {
        "area": "card_riassunto_fonti",
        "capability": "layout_grafico_controllato",
        "keywords": ["layout", "grafico", "card-graphic", "pdf", "ui"],
    },

    {
        "area": "quiz_test",
        "capability": "test_separato_da_altri_output",
        "keywords": ["test separato", "quiz_draft", "test_quiz", "card", "riassunto", "study_questions"],
    },
    {
        "area": "quiz_test",
        "capability": "opzioni_interne_visibili_validate",
        "keywords": ["opzioni", "options", "opzioni visibili", "opzioni interne", "validate"],
    },
    {
        "area": "quiz_test",
        "capability": "risposta_corretta_interna_visibile_mappa_sicura",
        "keywords": ["correct_option_id", "is_correct", "risposta corretta", "mappa sicura", "bridge"],
    },
    {
        "area": "quiz_test",
        "capability": "quattro_opzioni_risposta_presente",
        "keywords": ["4 opzioni", "quattro opzioni", "len(options)", "correct_option_id", "risposta corretta presente"],
    },
    {
        "area": "quiz_test",
        "capability": "distrattori_forti",
        "keywords": ["distrattori forti", "distrattor", "plausibil", "true_fact", "source_facts"],
    },
    {
        "area": "quiz_test",
        "capability": "no_opzioni_duplicate",
        "keywords": ["opzioni duplicate", "duplicate options", "duplicati", "stessa domanda"],
    },
    {
        "area": "quiz_test",
        "capability": "compatibilita_bridge_quiz",
        "keywords": ["bridge", "V3.5B", "quiz bridge", "rag_bridge", "adapter"],
    },

    {
        "area": "duplicati_ripetizioni",
        "capability": "duplicati_per_tipo_output_e_contesto",
        "keywords": ["duplicati", "quasi duplicati", "ripetizioni", "similar", "soglia_similarita", "contesto"],
    },
    {
        "area": "duplicati_ripetizioni",
        "capability": "ripetizioni_meccaniche_domande",
        "keywords": ["domande troppo ripetitive", "duplicate_ratio", "meccaniche", "quale affermazione"],
    },

    {
        "area": "selezionatore_orchestratore",
        "capability": "seleziona_motori_giusti_per_compito",
        "keywords": ["selezionatore", "orchestratore", "motori giusti", "task", "output richiesto"],
    },
    {
        "area": "selezionatore_orchestratore",
        "capability": "niente_output_non_richiesto",
        "keywords": ["output non richiesto", "niente motori inutili", "solo richiesto"],
    },
    {
        "area": "selezionatore_orchestratore",
        "capability": "output_pronto_ui_pdf_app",
        "keywords": ["ui", "pdf", "app", "web", "output finale", "pronto"],
    },
    {
        "area": "selezionatore_orchestratore",
        "capability": "report_qualita_leggibile",
        "keywords": ["report qualità", "quality_report", "report leggibile", "warnings", "errors"],
    },
]


def should_skip(path: Path) -> bool:
    text = str(path)
    return any(part in text for part in SKIP_PARTS)


def collect_registry_text() -> str:
    pieces: List[str] = []

    for spec in LEGACY_QUALITY_MOTORS:
        pieces.append(str(getattr(spec, "motor_id", "")))
        pieces.append(str(getattr(spec, "module_name", "")))
        pieces.append(str(getattr(spec, "function_name", "")))
        pieces.append(str(getattr(spec, "adapter_name", "")))
        pieces.append(str(getattr(spec, "target_kind", "")))

    return "\n".join(pieces)


def collect_source_hits(keywords: List[str]) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    for root in SOURCE_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if should_skip(path):
                continue

            if path.suffix.lower() not in {".py", ".js", ".html", ".css", ".md", ".json"}:
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")
            lower = text.lower()

            matched = [
                keyword for keyword in keywords
                if keyword.lower() in lower
            ]

            if not matched:
                continue

            kind = "backend_or_script"

            if "/demo-rag/" in str(path) or "/runtime/web/" in str(path):
                kind = "frontend_or_runtime_web"

            if "/test_" in str(path) or "/verifica_" in str(path):
                kind = "test_or_diagnostic"

            hits.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "kind": kind,
                    "matched_keywords": sorted(set(matched)),
                    "score": len(matched),
                }
            )

    hits.sort(key=lambda item: item["score"], reverse=True)
    return hits[:20]


def registry_hits_for_capability(keywords: List[str]) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    for spec in LEGACY_QUALITY_MOTORS:
        text = "\n".join(
            [
                str(getattr(spec, "motor_id", "")),
                str(getattr(spec, "module_name", "")),
                str(getattr(spec, "function_name", "")),
                str(getattr(spec, "adapter_name", "")),
                str(getattr(spec, "target_kind", "")),
            ]
        ).lower()

        matched = [
            keyword for keyword in keywords
            if keyword.lower() in text
        ]

        if matched:
            hits.append(
                {
                    "motor_id": getattr(spec, "motor_id", ""),
                    "adapter_name": getattr(spec, "adapter_name", ""),
                    "target_kind": getattr(spec, "target_kind", ""),
                    "matched_keywords": sorted(set(matched)),
                }
            )

    return hits


def classify_capability(
    *,
    registry_hits: List[Dict[str, Any]],
    source_hits: List[Dict[str, Any]],
) -> str:
    if registry_hits:
        return "CONNECTED_IN_REGISTRY"

    if any(hit["kind"] == "backend_or_script" for hit in source_hits):
        return "EXISTS_NEEDS_ADAPTER_OR_REVIEW"

    if any(hit["kind"] == "frontend_or_runtime_web" for hit in source_hits):
        return "FRONTEND_OR_UI_ONLY"

    if any(hit["kind"] == "test_or_diagnostic" for hit in source_hits):
        return "TEST_OR_VALIDATOR_ONLY"

    return "NOT_FOUND"


def main() -> int:
    rows: List[Dict[str, Any]] = []

    for capability in CAPABILITIES:
        keywords = capability["keywords"]

        reg_hits = registry_hits_for_capability(keywords)
        src_hits = collect_source_hits(keywords)

        status = classify_capability(
            registry_hits=reg_hits,
            source_hits=src_hits,
        )

        rows.append(
            {
                "area": capability["area"],
                "capability": capability["capability"],
                "status": status,
                "registry_hits": reg_hits,
                "source_hits": src_hits,
                "keywords": keywords,
            }
        )

    counts: Dict[str, int] = {}

    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    report = {
        "report_name": "phase5_9_10_quality_capability_matrix_v1",
        "status": "PASS_DIAGNOSTIC",
        "registry_motors_count": len(LEGACY_QUALITY_MOTORS),
        "capabilities_count": len(CAPABILITIES),
        "counts": counts,
        "rows": rows,
        "notes": [
            "Diagnostico: non modifica registry, motori o pipeline.",
            "Distingue capacità collegate, capacità esistenti ma da adattare, validator/test e frontend.",
            "Serve a non perdere i motori già creati e a decidere le prossime integrazioni.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.10 — Quality Capability Matrix V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Motori registry: `{len(LEGACY_QUALITY_MOTORS)}`")
    lines.append(f"- Capacità mappate: `{len(CAPABILITIES)}`")
    lines.append("")
    lines.append("## Conteggi\n")
    lines.append("| Stato | Conteggio |")
    lines.append("|---|---:|")

    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | {value} |")

    lines.append("")
    lines.append("## Matrice capacità\n")
    lines.append("| Area | Capacità | Stato | Registry hit | Source hit principali |")
    lines.append("|---|---|---|---|---|")

    for row in rows:
        registry_label = ", ".join(
            f"`{hit['motor_id']}`" for hit in row["registry_hits"][:3]
        ) or "-"

        source_label = ", ".join(
            f"`{hit['path']}`" for hit in row["source_hits"][:3]
        ) or "-"

        lines.append(
            f"| `{row['area']}` "
            f"| `{row['capability']}` "
            f"| `{row['status']}` "
            f"| {registry_label} "
            f"| {source_label} |"
        )

    lines.append("")
    lines.append("## Lettura operativa\n")
    lines.append("- `CONNECTED_IN_REGISTRY`: capacità già collegata a un motore registry.")
    lines.append("- `EXISTS_NEEDS_ADAPTER_OR_REVIEW`: codice presente, ma da trasformare/validare prima di collegarlo.")
    lines.append("- `TEST_OR_VALIDATOR_ONLY`: utile come gate, ma non migliora direttamente l'output.")
    lines.append("- `FRONTEND_OR_UI_ONLY`: riguarda UI, PDF, app o comportamento browser.")
    lines.append("- `NOT_FOUND`: capacità non trovata con la ricerca keyword, oppure nome diverso.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.10 QUALITY CAPABILITY MATRIX PASS")
    print(json.dumps(
        {
            "registry_motors_count": len(LEGACY_QUALITY_MOTORS),
            "capabilities_count": len(CAPABILITIES),
            "counts": counts,
        },
        ensure_ascii=False,
        indent=2,
    ))
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
