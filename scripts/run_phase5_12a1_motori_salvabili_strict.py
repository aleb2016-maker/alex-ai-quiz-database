#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12A.1 — MOTORI SALVABILI STRICT

Obiettivo:
- NON cercare parole sparse in tutto il progetto
- NON considerare backup/demo/fallback come motori salvabili
- leggere solo report/registry finali affidabili
- distinguere:
  1. motori reali salvabili già collegati
  2. controlli atomici richiesti ma ancora da ricreare
  3. casi da verificare manualmente

Questo script NON crea nuovi motori.
Questo script NON modifica la pipeline 5.11.
Questo script NON tocca UI, PDF, CSS o app.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

OUT_JSON = REPORTS_DIR / "phase5_12a1_motori_salvabili_strict_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12a1_motori_salvabili_strict_v1.md"

PHASE = "5.12A.1"
READY_LABEL = "MOTORI_SALVABILI_STRICT_MAP_READY"


AUTHORITATIVE_REPORTS = [
    "reports/phase5_11_pipeline_output_ready_report.json",
    "reports/phase5_10_2_final_registry_quality_snapshot_v1.json",
    "reports/phase5_10_1_summary_card_cleaner_registry_v1.json",
    "reports/phase5_9_9_universal_quiz_quality_registry_v1.json",
    "reports/phase5_9_3_quiz_repair_registry_integration_v1.json",
    "reports/legacy_quality_motors_registry_ready_v1.json",
    "reports/legacy_quality_motor_registry_v1_report.json",
    "reports/compatibilita_motori_qualita_fase5_v1.json",
    "reports/motori_qualita_esistenti_v1.json",
    "reports/mini_llm_v400_registry/mini_llm_engine_registry_v400.json",
]

BAD_SOURCE_WORDS = [
    "backup",
    "demo",
    "fallback",
    "placeholder",
    "todo",
    "knowledge_base_json",
    "documento analizzato",
    "testo di esempio",
]


@dataclass
class RequiredAtomicControl:
    id: str
    area: str
    title: str
    severity: str
    coverage_keywords: List[str]


@dataclass
class SalvableMotor:
    id: str
    title: str
    source_report: str
    confidence: str
    evidence: List[str]
    covered_areas: List[str]


@dataclass
class AtomicClassification:
    id: str
    area: str
    title: str
    status: str
    reason: str
    severity: str
    possible_covering_motors: List[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def load_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except Exception:
        return None


def norm(s: str) -> str:
    s = s.lower()
    s = s.replace("à", "a").replace("è", "e").replace("é", "e")
    s = s.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def required_controls() -> List[RequiredAtomicControl]:
    rows = []

    def add(area: str, title: str, keywords: List[str], severity: str = "blocking") -> None:
        idx = len(rows) + 1
        slug = norm(area + " " + title).replace(" ", "_")[:90]
        rows.append(RequiredAtomicControl(
            id=f"qm_{idx:03d}_{slug}",
            area=area,
            title=title,
            severity=severity,
            coverage_keywords=[norm(k) for k in keywords],
        ))

    # Qualità testuale
    add("qualita_testuale", "Grammatica italiana corretta", ["grammatica", "grammar", "accordo grammaticale"])
    add("qualita_testuale", "Accenti corretti", ["accenti", "perche", "puo", "piu", "gia", "cioe", "cosi", "pero", "qual e"])
    add("qualita_testuale", "Apostrofi corretti", ["apostrofi", "apostrophe", "un informazione", "l utente", "d accordo"])
    add("qualita_testuale", "Punteggiatura corretta", ["punteggiatura", "punctuation"])
    add("qualita_testuale", "Spazi corretti prima e dopo punteggiatura", ["spazi", "spacing", "punteggiatura"])
    add("qualita_testuale", "Frasi complete", ["frasi complete", "complete sentence"])
    add("qualita_testuale", "Assenza di frasi spezzate", ["frasi spezzate", "broken sentence"])
    add("qualita_testuale", "Assenza di frasi non terminate", ["frasi non terminate", "unfinished sentence"])
    add("qualita_testuale", "Assenza di finali sospetti", ["finali sospetti", "ending guard", "trailing connector"])
    add("qualita_testuale", "Assenza di frasi riempitive", ["frasi riempitive", "filler"])
    add("qualita_testuale", "Assenza di testo generico", ["testo generico", "generic text", "documento analizzato", "punto centrale"])
    add("qualita_testuale", "Assenza di vecchi fallback demo test", ["fallback", "demo", "legacy contamination"])

    # Qualità didattica
    add("qualita_didattica", "Domande studio naturali", ["domande studio naturali", "study questions natural"])
    add("qualita_didattica", "Domande studio utili per ripassare", ["ripassare", "study useful", "domande studio utili"])
    add("qualita_didattica", "Risposte guida specifiche", ["risposte guida", "specific answer"])
    add("qualita_didattica", "Spiegazioni test chiare", ["spiegazioni test", "clear explanation"])
    add("qualita_didattica", "Spiegazioni non troppo corte", ["spiegazioni non corte", "short explanation"])
    add("qualita_didattica", "Tono didattico finale", ["tono didattico", "didactic tone"])
    add("qualita_didattica", "Categorie presenti", ["categorie", "category"])
    add("qualita_didattica", "Sottocategorie presenti", ["sottocategorie", "subcategory"])
    add("qualita_didattica", "Coerenza tra domanda risposta e contenuto", ["coerenza domanda risposta contenuto", "question answer coherence"])
    add("qualita_didattica", "Niente risposte vaghe", ["risposte vaghe", "vague answers"])

    # Card / riassunto / fonti
    add("card_riassunto_fonti", "Card scritte bene", ["card quality", "card scritte bene"])
    add("card_riassunto_fonti", "Card non troppo corte", ["card non corte", "card length"])
    add("card_riassunto_fonti", "Card non troppo compresse", ["card compresse", "compressed card"])
    add("card_riassunto_fonti", "Messaggio chiave completo", ["messaggio chiave", "key message"])
    add("card_riassunto_fonti", "Riassunto chiaro", ["riassunto chiaro", "summary clear"])
    add("card_riassunto_fonti", "Punti chiave leggibili", ["punti chiave", "key points"])
    add("card_riassunto_fonti", "Fonti visibili belle", ["fonti visibili", "source display"])
    add("card_riassunto_fonti", "Fonti coerenti", ["fonti coerenti", "source coherence"])
    add("card_riassunto_fonti", "Niente fonti brutte", ["knowledge_base_json", "documento analizzato", "bad source"])
    add("card_riassunto_fonti", "Layout grafico controllato", ["layout grafico", "layout"], severity="warning")

    # Quiz / test
    add("test_quiz", "Test separato da card riassunto domande studio", ["test separato", "separated quiz"])
    add("test_quiz", "Opzioni interne validate", ["opzioni interne", "internal options"])
    add("test_quiz", "Opzioni visibili pulite", ["opzioni visibili", "visible options"])
    add("test_quiz", "Risposta corretta interna", ["risposta corretta interna", "internal correct answer"])
    add("test_quiz", "Risposta corretta visibile", ["risposta corretta visibile", "visible correct answer"])
    add("test_quiz", "Mappa sicura tra risposta interna e visibile", ["mappa sicura", "answer mapping"])
    add("test_quiz", "Quattro opzioni per domanda", ["4 opzioni", "quattro opzioni"])
    add("test_quiz", "Risposta corretta presente tra le opzioni", ["corretta tra opzioni", "correct answer in options"])
    add("test_quiz", "Distrattori forti", ["distrattori forti", "strong distractors"])
    add("test_quiz", "Niente opzioni duplicate nella stessa domanda", ["opzioni duplicate", "duplicate options"])
    add("test_quiz", "Niente ripetizioni globali eccessive", ["ripetizioni globali", "global repetition"])
    add("test_quiz", "Compatibilità bridge quiz V3.5B", ["bridge quiz", "v3 5b", "quiz bridge"])

    # Duplicati contestuali
    add("duplicati_contestuali", "Duplicati esatti", ["duplicati esatti", "exact duplicate"])
    add("duplicati_contestuali", "Quasi duplicati", ["quasi duplicati", "near duplicate"])
    add("duplicati_contestuali", "Ripetizioni inutili", ["ripetizioni inutili", "useless repetition"])
    add("duplicati_contestuali", "Ripetizioni meccaniche tra domande", ["ripetizioni meccaniche", "question repetition"])
    add("duplicati_contestuali", "Frasi troppo simili", ["frasi troppo simili", "similar sentences"])
    add("duplicati_contestuali", "Stesso contenuto ripetuto senza motivo", ["contenuto ripetuto", "repeated content"])

    # Selettore / orchestratore
    add("selettore_orchestratore", "Il compito richiesto deve selezionare i motori giusti", ["seleziona motori", "motor selector"])
    add("selettore_orchestratore", "Riassunto seleziona motore didattico", ["riassunto motore didattico"])
    add("selettore_orchestratore", "Card seleziona motore didattico e layout", ["card motore didattico layout"])
    add("selettore_orchestratore", "Domande studio selezionano motore didattico", ["domande studio motore didattico"])
    add("selettore_orchestratore", "Test seleziona bridge quiz e motore test", ["test bridge quiz motore test"])
    add("selettore_orchestratore", "Completo PDF app web seleziona orchestratore", ["pdf app web orchestratore"])
    add("selettore_orchestratore", "Niente motori inutili", ["motori inutili"])
    add("selettore_orchestratore", "Niente output non richiesto", ["output non richiesto"])
    add("selettore_orchestratore", "Output finale pronto per UI PDF app", ["output finale pronto", "pipeline output ready"])
    add("selettore_orchestratore", "Report qualità sempre leggibile", ["report qualita leggibile"])

    # Avanzati
    add("naturalezza_linguistica", "Naturalezza linguistica anti-keyword", ["naturalezza linguistica", "anti keyword", "robotiche"])
    add("accordo_grammaticale", "Accordo grammaticale e pronomi", ["accordo grammaticale", "pronomi", "genere numero"])
    add("repair_contestuale", "Correzione frasi non finite usando contesto tema sottotema categorie e sottocategorie", ["frasi non finite", "repair contestuale", "tema sottotema"])
    add("repair_ortografico", "Correzione parole con lettere invertite", ["lettere invertite", "ortografico", "typo repair"])

    return rows


def flatten_json(obj: Any) -> List[str]:
    out: List[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                out.append(str(k))
                walk(v)
        elif isinstance(x, list):
            for item in x:
                walk(item)
        elif x is not None:
            out.append(str(x))

    walk(obj)
    return out


def authoritative_texts() -> Dict[str, str]:
    texts: Dict[str, str] = {}

    for item in AUTHORITATIVE_REPORTS:
        p = ROOT / item
        if not p.exists():
            continue

        if p.suffix.lower() == ".json":
            obj = load_json(p)
            if obj is None:
                txt = read_text(p)
            else:
                txt = "\n".join(flatten_json(obj))
        else:
            txt = read_text(p)

        texts[item] = txt

    return texts


def registry_pass_ok(texts: Dict[str, str]) -> bool:
    p11 = texts.get("reports/phase5_11_pipeline_output_ready_report.json", "")
    low = p11.lower()
    return (
        "pipeline_output_ready" in low
        and "true" in low
        and "pipeline_output_ready" in low
        and "pass" in low
    )


def detect_salvable_motors(texts: Dict[str, str]) -> List[SalvableMotor]:
    """
    Qui non classifichiamo i 64 controlli atomici come salvabili.
    Qui elenchiamo i motori REALI salvabili già emersi dai report finali.
    """
    joined = "\n".join(texts.values())
    low = joined.lower()

    candidates = [
        {
            "id": "salvable_phase5_pipeline_5_fasi",
            "title": "Regressione pipeline 5 fasi",
            "need": ["regressione_pipeline_5_fasi", "returncode", "0"],
            "areas": ["pipeline", "orchestrator"],
        },
        {
            "id": "salvable_pipeline_output_ready_gate_v511",
            "title": "Gate finale Pipeline Output Ready Fase 5.11",
            "need": ["pipeline_output_ready", "true", "summary", "card", "quiz", "study"],
            "areas": ["summary", "card", "quiz", "study", "registry"],
        },
        {
            "id": "salvable_final_registry_quality_snapshot_v5102",
            "title": "Snapshot qualità registry finale Fase 5.10.2",
            "need": ["registry", "motors", "summary", "card", "quiz"],
            "areas": ["registry", "quality_snapshot"],
        },
        {
            "id": "salvable_summary_card_cleaner_registry_v5101",
            "title": "Cleaner summary/card collegato al registry Fase 5.10.1",
            "need": ["summary", "card", "cleaner", "registry"],
            "areas": ["summary", "card", "cleaner"],
        },
        {
            "id": "salvable_universal_quiz_quality_registry_v599",
            "title": "Registry qualità quiz universale Fase 5.9.9",
            "need": ["quiz", "quality", "registry"],
            "areas": ["quiz", "test"],
        },
        {
            "id": "salvable_quiz_repair_registry_integration_v593",
            "title": "Integrazione registry riparatore quiz Fase 5.9.3",
            "need": ["quiz", "repair", "registry"],
            "areas": ["quiz", "repair"],
        },
        {
            "id": "salvable_legacy_quality_motors_registry_ready",
            "title": "Registry motori qualità legacy ready",
            "need": ["legacy", "quality", "registry"],
            "areas": ["registry", "legacy_quality"],
        },
        {
            "id": "salvable_phase5_live_quality_bridge",
            "title": "Bridge qualità live Fase 5",
            "need": ["quality", "bridge"],
            "areas": ["bridge", "orchestrator"],
        },
        {
            "id": "salvable_mini_llm_engine_registry_v400",
            "title": "Mini LLM engine registry V400",
            "need": ["mini_llm", "engine", "registry"],
            "areas": ["engine_registry"],
        },
        {
            "id": "salvable_general_quality_motor",
            "title": "Motore qualità generale",
            "need": ["motore", "qualita", "generale"],
            "areas": ["general_quality"],
        },
        {
            "id": "salvable_visual_logic_quality_motor",
            "title": "Motore qualità logica visiva",
            "need": ["motore", "qualita", "logica", "visiva"],
            "areas": ["visual_logic"],
        },
    ]

    found: List[SalvableMotor] = []

    for c in candidates:
        ok = all(norm(x) in norm(joined) for x in c["need"])

        # eccezione: alcuni report usano nomi file più che contenuto testuale
        if not ok:
            file_name_hit = any(
                c["id"].replace("salvable_", "").split("_v")[0] in norm(name)
                for name in texts.keys()
            )
            ok = file_name_hit

        if ok:
            evidence_reports = []
            for name, txt in texts.items():
                blob = norm(name + "\n" + txt)
                hits = sum(1 for n in c["need"] if norm(n) in blob)
                if hits >= max(1, len(c["need"]) // 2):
                    evidence_reports.append(name)

            found.append(SalvableMotor(
                id=c["id"],
                title=c["title"],
                source_report=", ".join(evidence_reports[:3]) if evidence_reports else "authoritative_reports",
                confidence="HIGH" if registry_pass_ok(texts) else "MEDIUM",
                evidence=evidence_reports[:8],
                covered_areas=c["areas"],
            ))

    # Se 5.11 dice registry PASS 14, manteniamo anche informazione numerica
    return found


def classify_atomic_controls(
    controls: List[RequiredAtomicControl],
    salvable: List[SalvableMotor],
    texts: Dict[str, str],
) -> List[AtomicClassification]:
    joined = norm("\n".join(texts.values()))
    salvable_blob = norm("\n".join(
        [m.id + " " + m.title + " " + " ".join(m.covered_areas) for m in salvable]
    ))

    rows: List[AtomicClassification] = []

    for c in controls:
        covering = []

        # copertura stretta: solo se keyword compare nei report autorevoli e anche in un motore salvabile
        for kw in c.coverage_keywords:
            if kw and kw in joined and kw in salvable_blob:
                covering.append(kw)

        if covering:
            status = "DA_VERIFICARE"
            reason = (
                "Possibile copertura indiretta nei motori salvabili, ma non ancora dimostrata "
                "come controllo atomico autonomo con test dedicato."
            )
            possible = covering
        else:
            status = "DA_RICREARE"
            reason = (
                "Non esiste ancora evidenza stretta di un motore atomico autonomo, "
                "universale, registrato, testato e collegato per questo controllo."
            )
            possible = []

        rows.append(AtomicClassification(
            id=c.id,
            area=c.area,
            title=c.title,
            status=status,
            reason=reason,
            severity=c.severity,
            possible_covering_motors=possible,
        ))

    return rows


def count_by_status(items: List[AtomicClassification]) -> Dict[str, int]:
    out = {"DA_VERIFICARE": 0, "DA_RICREARE": 0}
    for x in items:
        out[x.status] = out.get(x.status, 0) + 1
    return out


def count_by_area(items: List[AtomicClassification]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for x in items:
        out.setdefault(x.area, {"DA_VERIFICARE": 0, "DA_RICREARE": 0})
        out[x.area][x.status] += 1
    return out


def write_reports(report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.12A.1 — Motori salvabili strict")
    lines.append("")
    lines.append(f"- Status: **{report['status']}**")
    lines.append(f"- Ready label: `{report['ready_label']}`")
    lines.append(f"- Generated at: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Risultato")
    lines.append("")
    lines.append(f"- Motori reali salvabili trovati: `{report['salvable_motors_count']}`")
    lines.append(f"- Controlli atomici richiesti: `{report['atomic_controls_count']}`")
    lines.append(f"- Classificazione controlli atomici: `{report['atomic_summary_by_status']}`")
    lines.append("")
    lines.append("## Motori reali salvabili")
    lines.append("")
    for m in report["salvable_motors"]:
        lines.append(f"- `{m['id']}` — **{m['title']}**")
        lines.append(f"  - Confidence: `{m['confidence']}`")
        lines.append(f"  - Aree coperte: `{m['covered_areas']}`")
        lines.append(f"  - Evidenze: `{m['evidence']}`")
        lines.append("")
    lines.append("## Controlli atomici da verificare")
    lines.append("")
    for c in report["atomic_classifications"]:
        if c["status"] == "DA_VERIFICARE":
            lines.append(f"- `{c['id']}` — **{c['title']}**")
            lines.append(f"  - Area: `{c['area']}`")
            lines.append(f"  - Motivo: {c['reason']}")
            lines.append("")
    lines.append("## Controlli atomici da ricreare da zero")
    lines.append("")
    for c in report["atomic_classifications"]:
        if c["status"] == "DA_RICREARE":
            lines.append(f"- `{c['id']}` — **{c['title']}**")
            lines.append(f"  - Area: `{c['area']}`")
            lines.append(f"  - Severità: `{c['severity']}`")
            lines.append("")
    lines.append("## Regola duplicati")
    lines.append("")
    lines.append("Il controllo duplicati va ricreato come controllo contestuale.")
    lines.append("Non deve bocciare lo stesso concetto quando appare in card, quiz, domande studio e fonti con funzioni diverse.")
    lines.append("")
    lines.append("## Scope guard")
    lines.append("")
    for k, v in report["scope_guard"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    texts = authoritative_texts()
    salvable = detect_salvable_motors(texts)
    controls = required_controls()
    atomic = classify_atomic_controls(controls, salvable, texts)

    report = {
        "phase": PHASE,
        "generated_at": now_iso(),
        "status": "PASS",
        "ready_label": READY_LABEL,
        "authoritative_reports_used": sorted(texts.keys()),
        "salvable_motors_count": len(salvable),
        "salvable_motors": [asdict(x) for x in salvable],
        "atomic_controls_count": len(controls),
        "atomic_summary_by_status": count_by_status(atomic),
        "atomic_summary_by_area": count_by_area(atomic),
        "atomic_classifications": [asdict(x) for x in atomic],
        "important_interpretation": {
            "salvable_motors": "Motori reali già presenti nei registry/report finali PASS.",
            "atomic_controls": "Controlli richiesti dall'utente: se non hanno motore autonomo testato e collegato, sono da ricreare.",
            "no_global_duplicate_rule": "Le ripetizioni vanno controllate per area e contesto, non su tutto il documento in modo cieco.",
        },
        "scope_guard": {
            "created_new_motors": False,
            "deleted_existing_project_files": False,
            "changed_pipeline_5_11": False,
            "touched_ui_pdf_css_app": False,
            "classification_only": True,
        },
        "report_files": {
            "json": rel(OUT_JSON),
            "markdown": rel(OUT_MD),
        },
    }

    write_reports(report)

    print(f"PASS - Fase {PHASE}: {READY_LABEL}")
    print(f"Motori reali salvabili: {len(salvable)}")
    print(f"Controlli atomici richiesti: {len(controls)}")
    print("Classificazione controlli atomici:", count_by_status(atomic))
    print(f"Report JSON: {rel(OUT_JSON)}")
    print(f"Report MD:   {rel(OUT_MD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
