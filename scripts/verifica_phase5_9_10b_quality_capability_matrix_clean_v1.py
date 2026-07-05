from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

INPUT_JSON = ROOT / "reports" / "phase5_9_10_quality_capability_matrix_v1.json"
REPORT_JSON = ROOT / "reports" / "phase5_9_10b_quality_capability_matrix_clean_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_10b_quality_capability_matrix_clean_v1.md"


# FASE 5.9.10B — QUALITY CAPABILITY MATRIX CLEAN V1
#
# Scopo:
# - ripulire la matrice 5.9.10 dai falsi positivi keyword-based;
# - non considerare lo script diagnostico stesso come prova;
# - distinguere meglio "motore davvero collegato" da "keyword trovata nel registry";
# - non modificare registry, motori o pipeline.


NOISE_SOURCE_PATH_PARTS = [
    "verifica_phase5_9_10_quality_capability_matrix_v1.py",
    "verifica_phase5_9_10b_quality_capability_matrix_clean_v1.py",
    "reports/",
    "__pycache__",
    ".venv",
]


# Mappa prudente: una capacità è CONNECTED solo se sappiamo quale motore registry
# la copre davvero, non solo perché una keyword appare da qualche parte.
CURATED_CONNECTED_CAPABILITIES: Dict[str, List[str]] = {
    "grammatica_italiana_corretta": [
        "backend.main.pulisci_qualita_linguistica_quiz",
    ],
    "no_riempitivi_generico_fallback": [
        "scripts.rag_revisore_qualita_testuale_v35g.refine_output",
        "scripts.rag_revisore_qualita_testuale_v35g.refine_study",
        "scripts.rag_motore_test_riutilizzabile_v35d.refine_output",
    ],
    "accordo_grammaticale_pronomi": [
        "scripts.rag_revisore_accordo_pronomi_v35j.improve_output",
    ],
    "domande_studio_naturali_utili": [
        "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions",
    ],
    "riassunto_chiaro_punti_chiave": [
        "scripts.rag_cleaner_finale_universale_v35k.clean_output",
        "scripts.rag_revisore_accordo_pronomi_v35j.improve_output",
        "scripts.rag_revisore_qualita_testuale_v35g.refine_output",
    ],
    "distrattori_forti": [
        "backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1",
        "backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1",
    ],
    "spiegazioni_test_chiare_non_corte": [
        "backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1",
    ],
    "ripetizioni_meccaniche_domande": [
        "backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1",
    ],
    "compatibilita_bridge_quiz": [
        "backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1",
    ],
}


# Capacità che NON devono risultare collegate solo perché una keyword appare nel registry.
# Per queste vogliamo adapter/test specifico.
FORCE_REVIEW_CAPABILITIES = {
    "layout_grafico_controllato",
    "output_pronto_ui_pdf_app",
    "fonti_visibili_coerenti_belle",
    "opzioni_interne_visibili_validate",
    "risposta_corretta_interna_visibile_mappa_sicura",
    "quattro_opzioni_risposta_presente",
    "no_opzioni_duplicate",
    "duplicati_per_tipo_output_e_contesto",
    "seleziona_motori_giusti_per_compito",
    "niente_output_non_richiesto",
    "report_qualita_leggibile",
}


def is_noise_source(path: str) -> bool:
    return any(part in path for part in NOISE_SOURCE_PATH_PARTS)


def clean_source_hits(source_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for hit in source_hits:
        path = str(hit.get("path") or "")

        if is_noise_source(path):
            continue

        out.append(hit)

    return out


def curated_registry_hits(capability: str, original_registry_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allowed_motor_ids = set(CURATED_CONNECTED_CAPABILITIES.get(capability, []))

    if not allowed_motor_ids:
        return []

    out: List[Dict[str, Any]] = []

    for hit in original_registry_hits:
        motor_id = str(hit.get("motor_id") or "")

        if motor_id in allowed_motor_ids:
            out.append(hit)

    # Può capitare che la 5.9.10 originale non abbia trovato registry hit
    # perché cercava per keyword, ma noi sappiamo che la capacità è coperta.
    # In quel caso creiamo un hit esplicito e dichiarato.
    existing_ids = {str(hit.get("motor_id") or "") for hit in out}

    for motor_id in allowed_motor_ids:
        if motor_id not in existing_ids:
            out.append(
                {
                    "motor_id": motor_id,
                    "adapter_name": "curated",
                    "target_kind": "curated",
                    "matched_keywords": ["curated_capability_map"],
                }
            )

    return out


def reclassify_row(row: Dict[str, Any]) -> Dict[str, Any]:
    capability = str(row.get("capability") or "")
    source_hits = clean_source_hits(row.get("source_hits") or [])
    registry_hits = curated_registry_hits(capability, row.get("registry_hits") or [])

    status = "NOT_FOUND"

    if capability in FORCE_REVIEW_CAPABILITIES:
        if source_hits:
            status = "EXISTS_NEEDS_ADAPTER_OR_REVIEW"
        else:
            status = "NOT_FOUND"

    elif registry_hits:
        status = "CONNECTED_IN_REGISTRY"

    elif any(hit.get("kind") == "backend_or_script" for hit in source_hits):
        status = "EXISTS_NEEDS_ADAPTER_OR_REVIEW"

    elif any(hit.get("kind") == "frontend_or_runtime_web" for hit in source_hits):
        status = "FRONTEND_OR_UI_ONLY"

    elif any(hit.get("kind") == "test_or_diagnostic" for hit in source_hits):
        status = "TEST_OR_VALIDATOR_ONLY"

    else:
        status = "NOT_FOUND"

    changed = status != row.get("status") or registry_hits != row.get("registry_hits") or source_hits != row.get("source_hits")

    return {
        **row,
        "status_original": row.get("status"),
        "status": status,
        "registry_hits": registry_hits,
        "source_hits": source_hits,
        "cleaning_changed": changed,
    }


def main() -> int:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Report 5.9.10 non trovato: {INPUT_JSON}")

    source_report = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rows = source_report.get("rows") or []

    clean_rows = [reclassify_row(row) for row in rows]

    counts: Dict[str, int] = {}

    for row in clean_rows:
        status = row["status"]
        counts[status] = counts.get(status, 0) + 1

    changed_rows = [
        row for row in clean_rows
        if row.get("cleaning_changed") is True
    ]

    report = {
        "report_name": "phase5_9_10b_quality_capability_matrix_clean_v1",
        "status": "PASS_DIAGNOSTIC",
        "input_report": str(INPUT_JSON.relative_to(ROOT)),
        "capabilities_count": len(clean_rows),
        "counts": counts,
        "changed_rows_count": len(changed_rows),
        "rows": clean_rows,
        "changed_rows": changed_rows,
        "notes": [
            "Diagnostico: non modifica registry, motori o pipeline.",
            "Ripulisce la matrice 5.9.10 dai falsi positivi keyword-based.",
            "CONNECTED_IN_REGISTRY è assegnato solo tramite mappa prudente di capacità effettivamente coperte.",
            "Layout, UI, PDF, fonti e mappa visibile/interna richiedono test/adapter dedicato.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.10B — Quality Capability Matrix Clean V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Capacità mappate: `{len(clean_rows)}`")
    lines.append(f"- Righe riclassificate/ripulite: `{len(changed_rows)}`")
    lines.append("")
    lines.append("## Conteggi puliti\n")
    lines.append("| Stato | Conteggio |")
    lines.append("|---|---:|")

    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | {value} |")

    lines.append("")
    lines.append("## Matrice pulita\n")
    lines.append("| Area | Capacità | Stato originale | Stato pulito | Registry hit | Source hit principali |")
    lines.append("|---|---|---|---|---|---|")

    for row in clean_rows:
        registry_label = ", ".join(
            f"`{hit['motor_id']}`" for hit in row.get("registry_hits", [])[:3]
        ) or "-"

        source_label = ", ".join(
            f"`{hit['path']}`" for hit in row.get("source_hits", [])[:3]
        ) or "-"

        lines.append(
            f"| `{row.get('area')}` "
            f"| `{row.get('capability')}` "
            f"| `{row.get('status_original')}` "
            f"| `{row.get('status')}` "
            f"| {registry_label} "
            f"| {source_label} |"
        )

    lines.append("")
    lines.append("## Lettura operativa corretta\n")
    lines.append("- `CONNECTED_IN_REGISTRY`: capacità davvero coperta da un motore registry conosciuto.")
    lines.append("- `EXISTS_NEEDS_ADAPTER_OR_REVIEW`: codice presente, ma non ancora trasformato in motore universale collegato.")
    lines.append("- `FRONTEND_OR_UI_ONLY`: riguarda UI/PDF/app/browser, non registry backend.")
    lines.append("- `TEST_OR_VALIDATOR_ONLY`: utile come gate, non come motore trasformativo.")
    lines.append("- `NOT_FOUND`: non trovato o nome diverso.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.10B QUALITY CAPABILITY MATRIX CLEAN PASS")
    print(json.dumps(
        {
            "capabilities_count": len(clean_rows),
            "changed_rows_count": len(changed_rows),
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
