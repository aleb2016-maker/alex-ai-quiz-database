#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audit non invasivo RAG/mini LLM - 73 motori qualità.

Produce:
- reports/audit_completo_73_motori_rag_qualita_v1.md
- reports/audit_completo_73_motori_rag_qualita_v1.json

Lo script non modifica la pipeline produttiva. Legge cataloghi, report storici e
file runtime correnti, poi sintetizza una diagnosi tecnica.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

MD_OUT = REPORTS / "audit_completo_73_motori_rag_qualita_v1.md"
JSON_OUT = REPORTS / "audit_completo_73_motori_rag_qualita_v1.json"


SMOKE_RESULTS = [
    {"scenario": "breve", "kind": "summary", "ok": False, "error": "HTTP 500"},
    {"scenario": "breve", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 3, "content_len": 0},
    {"scenario": "breve", "kind": "study", "ok": False, "error": "HTTP 500"},
    {"scenario": "breve", "kind": "quiz", "ok": False, "error": "HTTP 500"},
    {"scenario": "medio", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 597},
    {"scenario": "medio", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 5, "content_len": 0},
    {"scenario": "medio", "kind": "study", "ok": True, "status": "APPROVED", "motor": "full_pipeline_study_route51_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "medio", "kind": "quiz", "ok": True, "status": "APPROVED", "motor": "full_pipeline_quiz_route63_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "lungo", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 589},
    {"scenario": "lungo", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 4, "content_len": 0},
    {"scenario": "lungo", "kind": "study", "ok": True, "status": "APPROVED", "motor": "full_pipeline_study_route51_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "lungo", "kind": "quiz", "ok": True, "status": "APPROVED", "motor": "full_pipeline_quiz_route63_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "tecnico", "kind": "summary", "ok": False, "error": "HTTP 500"},
    {"scenario": "tecnico", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 3, "content_len": 0},
    {"scenario": "tecnico", "kind": "study", "ok": False, "error": "HTTP 500"},
    {"scenario": "tecnico", "kind": "quiz", "ok": False, "error": "HTTP 500"},
    {"scenario": "narrativo", "kind": "summary", "ok": False, "error": "HTTP 500"},
    {"scenario": "narrativo", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 3, "content_len": 0},
    {"scenario": "narrativo", "kind": "study", "ok": False, "error": "HTTP 500"},
    {"scenario": "narrativo", "kind": "quiz", "ok": False, "error": "HTTP 500"},
    {"scenario": "concetti_simili", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 504},
    {"scenario": "concetti_simili", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 4, "content_len": 0},
    {"scenario": "concetti_simili", "kind": "study", "ok": True, "status": "APPROVED", "motor": "full_pipeline_study_route51_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "concetti_simili", "kind": "quiz", "ok": True, "status": "APPROVED", "motor": "full_pipeline_quiz_route63_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "ripetitivo", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 512},
    {"scenario": "ripetitivo", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 5, "content_len": 0},
    {"scenario": "ripetitivo", "kind": "study", "ok": True, "status": "APPROVED", "motor": "full_pipeline_study_route51_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "ripetitivo", "kind": "quiz", "ok": True, "status": "APPROVED", "motor": "full_pipeline_quiz_route63_language_quality_v51418", "items": 4, "content_len": 0},
    {"scenario": "generico", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 378},
    {"scenario": "generico", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 2, "content_len": 0},
    {"scenario": "generico", "kind": "study", "ok": False, "error": "HTTP 500"},
    {"scenario": "generico", "kind": "quiz", "ok": False, "error": "HTTP 500"},
    {"scenario": "lista", "kind": "summary", "ok": True, "status": "APPROVED", "motor": "full_pipeline_summary_route55_all_motors_v51416", "items": 0, "content_len": 450},
    {"scenario": "lista", "kind": "cards", "ok": True, "status": "APPROVED", "motor": "full_pipeline_cards_60_motors_graphic_v51416", "items": 4, "content_len": 0},
    {"scenario": "lista", "kind": "study", "ok": False, "error": "HTTP 500"},
    {"scenario": "lista", "kind": "quiz", "ok": False, "error": "HTTP 500"},
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def find_python_functions(path: Path) -> List[str]:
    text = read_text(path)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]


def source_has(path: str, pattern: str) -> bool:
    return pattern in read_text(ROOT / path)


def build_motors() -> List[Dict[str, Any]]:
    catalog = read_json(REPORTS / "phase5_12i2_official_quality_motor_catalog_v1.json", {})
    operational = read_json(REPORTS / "phase5_12j_operational_reference_list_updated_v1.json", {})
    motors: List[Dict[str, Any]] = []

    runtime_files = [
        "backend/phase5_summary_route_55_strict_connector_v513b1.py",
        "backend/phase5_card_route_60_strict_connector_v513a3.py",
        "backend/motori_scrittura.py",
        "scripts/run_phase5_14_3_local_backend_bridge.py",
        "backend/phase5_full_pipeline_runtime_v51416.py",
        "demo-rag/test-documenti-universale.html",
        "demo-rag/universal-document-learning-engine.js",
    ]
    runtime_blob = "\n".join(read_text(ROOT / p) for p in runtime_files)
    final_routes = {
        "summary": set(["qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006", "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012", "qm_017", "qm_018", "qm_019", "qm_020", "qm_023", "qm_024", "qm_025", "qm_026", "qm_027", "qm_028", "qm_029", "qm_030", "qm_031", "qm_032", "qm_033", "qm_034", "qm_035", "qm_038", "qm_039", "qm_040", "qm_042", "qm_043", "qm_044", "qm_045", "qm_046", "qm_047", "qm_048", "qm_049", "qm_050", "qm_051", "qm_052", "qm_053", "qm_054", "qm_055", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060", "qm_061", "qm_062", "qm_063", "qm_064"]),
        "cards": set(["qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006", "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012", "qm_013", "qm_014", "qm_015", "qm_017", "qm_018", "qm_019", "qm_020", "qm_021", "qm_022", "qm_023", "qm_024", "qm_025", "qm_026", "qm_027", "qm_028", "qm_029", "qm_030", "qm_031", "qm_032", "qm_033", "qm_034", "qm_035", "qm_038", "qm_039", "qm_040", "qm_042", "qm_043", "qm_044", "qm_045", "qm_046", "qm_047", "qm_048", "qm_049", "qm_050", "qm_051", "qm_052", "qm_053", "qm_054", "qm_055", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060", "qm_061", "qm_062", "qm_063", "qm_064"]),
        "study": set(["qm_013", "qm_014", "qm_015", "qm_017", "qm_018", "qm_021", "qm_022", "qm_048", "qm_051", "qm_054", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060"]),
        "quiz": set(["qm_016", "qm_017", "qm_021", "qm_022", "qm_033", "qm_034", "qm_035", "qm_036", "qm_037", "qm_038", "qm_039", "qm_040", "qm_041", "qm_042", "qm_043", "qm_044", "qm_048", "qm_051", "qm_055", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060"]),
    }

    for item in catalog.get("motors", []):
        qm_id = item["qm_id"]
        used = item.get("used_by_sections", [])
        connected_to = []
        if qm_id in final_routes["summary"]:
            connected_to.append("Riassunto")
        if qm_id in final_routes["cards"]:
            connected_to.append("Card")
        if qm_id in final_routes["study"]:
            connected_to.append("Domande studio")
        if qm_id in final_routes["quiz"]:
            connected_to.append("Test/Quiz")
        appears = qm_id in runtime_blob
        executor = f'"{qm_id}":' in runtime_blob or f"'{qm_id}':" in runtime_blob
        status = "PARZIALE" if connected_to else "NON COLLEGATO"
        note = "Nel catalogo ufficiale; "
        if executor:
            note += "ha executor in connettori/report backend; "
        elif appears:
            note += "citato nel runtime/report; "
        else:
            note += "non trovato nei file runtime principali; "
        if connected_to:
            note += "collegamento finale dedotto da route/quality_report, non da invocazione registry unica."
        else:
            note += "non risulta nella route finale corrente."
        motors.append({
            "numero": item.get("number"),
            "nome_motore": f"{qm_id} - {item.get('name')}",
            "file": "reports/phase5_12i2_official_quality_motor_catalog_v1.json",
            "funzione_classe_principale": "catalog entry / executor se presente",
            "tipo_motore": classify_type(item),
            "collegato": bool(connected_to),
            "a_cosa_collegato": connected_to,
            "stato": status,
            "note": note,
        })

    # Elementi 65-73: il progetto li conta nel registry, ma il catalogo dice che non sono QM spiegati.
    for number in range(65, 74):
        motors.append({
            "numero": number,
            "nome_motore": f"registry_orchestration_slot_{number:03d}",
            "file": "reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json",
            "funzione_classe_principale": "conteggio registry/orchestrazione",
            "tipo_motore": "registry" if number >= 65 else "orchestratore",
            "collegato": number <= 73,
            "a_cosa_collegato": ["Registry/orchestrazione H.2"],
            "stato": "DA VERIFICARE",
            "note": "Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'.",
        })

    return motors


def classify_type(item: Dict[str, Any]) -> str:
    group = (item.get("group") or "").lower()
    name = (item.get("name") or "").lower()
    text = group + " " + name
    if "fallback" in text:
        return "anti-fallback"
    if "generico" in text:
        return "anti-generico"
    if "frasi spezzate" in text:
        return "anti-frasi spezzate"
    if "test" in text or "quiz" in text or "opzioni" in text or "distrattori" in text:
        return "validazione quiz"
    if "card" in text or "fonti" in text:
        return "validazione card"
    if "riassunto" in text:
        return "validazione riassunto"
    if "domande studio" in text:
        return "validazione domande studio"
    if "duplicati" in text or "ripetizioni" in text:
        return "qualità semantica"
    if "selezionatore" in text or "orchestratore" in text:
        return "orchestratore"
    if "grammatica" in text or "accenti" in text or "apostrofi" in text or "punteggiatura" in text:
        return "qualità grammaticale"
    if "didattica" in text:
        return "qualità didattica"
    return "qualità semantica"


def build_static_findings() -> Dict[str, Any]:
    html = read_text(ROOT / "demo-rag/test-documenti-universale.html")
    bridge = read_text(ROOT / "scripts/run_phase5_14_3_local_backend_bridge.py")
    runtime = read_text(ROOT / "backend/phase5_full_pipeline_runtime_v51416.py")
    universal = read_text(ROOT / "demo-rag/universal-document-learning-engine.js")
    return {
        "ui_bridge": {
            "page": "demo-rag/test-documenti-universale.html",
            "uses_local_backend": "fetch(API + \"/api/generate\"" in html,
            "loads_universal_engine": "universal-document-learning-engine.js" in html,
            "reveals_quiz_correct_option": 'opt.is_correct ? "correct" : ""' in html or "✅" in html,
            "input_control": "text.length < 20" in html,
        },
        "backend_bridge": {
            "file": "scripts/run_phase5_14_3_local_backend_bridge.py",
            "summary_runtime": "run_full_pipeline_v51416(\"summary\"" in bridge,
            "cards_runtime": "run_full_pipeline_v51416(\"cards\"" in bridge,
            "study_q52": "q52_build_quality_study_questions" in bridge,
            "quiz_q52": "q52_build_quality_quiz" in bridge,
            "manual_repair_layers": "_v51417_repair_study_quiz_raw" in bridge and "_v51418_build_quiz_items" in bridge,
            "strict_demo_block": "sicurezza informatica aziendale" in bridge,
        },
        "summary_cards_runtime": {
            "file": "backend/phase5_full_pipeline_runtime_v51416.py",
            "declares_all_motors_connected": '"all_motors_connected": True' in runtime,
            "generic_motor_groups": "connected_motor_groups" in runtime,
            "summary_has_no_long_doc_progressive_engine": "rag-large-document-progressive-summary" not in runtime,
            "card_message_generic": "Il punto centrale è rendere questa informazione chiara" in runtime,
        },
        "legacy_browser_engine": {
            "file": "demo-rag/universal-document-learning-engine.js",
            "contains_four_generators": all(x in universal for x in ["function generaRiassunto", "function generaCardVisive", "function generaTest", "function generaDomandeStudio"]),
            "uses_profiles_and_cards": "profiliDocumento" in universal and "creaCards" in universal,
            "not_loaded_by_clean_page": "universal-document-learning-engine.js" not in html,
        },
    }


def build_issues() -> List[Dict[str, Any]]:
    return [
        {"gravità": "CRITICO", "problema": "Il claim '73 motori' è ambiguo: il catalogo ufficiale spiega 64 QM, mentre 73 è un totale di registry/orchestrazione.", "file": "reports/phase5_12i2_official_quality_motor_catalog_v1.json", "impatto": "Si rischia di dichiarare collegati motori che sono solo conteggi o route.", "come_correggere": "Creare un registry eseguibile unico con 73 entry concrete oppure rinominare il totale come 64 motori + 9 slot di orchestrazione.", "priorità": "P0"},
        {"gravità": "CRITICO", "problema": "La pagina reale V5.14.14 bypassa l'engine browser storico e chiama direttamente il bridge backend.", "file": "demo-rag/test-documenti-universale.html", "impatto": "Esistono pipeline parallele; report su universal-document-learning-engine non provano la pagina reale.", "come_correggere": "Definire un solo entrypoint produttivo e far passare UI, backend, quality registry e renderer dalla stessa contract API.", "priorità": "P0"},
        {"gravità": "CRITICO", "problema": "Il quiz mostra la risposta corretta nella UI con classe correct e simbolo di conferma.", "file": "demo-rag/test-documenti-universale.html", "impatto": "Viola il requisito: nessuna risposta corretta rivelata all'utente.", "come_correggere": "Non renderizzare is_correct; mantenere la risposta solo in stato interno o dopo invio risposta.", "priorità": "P0"},
        {"gravità": "ALTO", "problema": "summary/cards dichiarano all_motors_connected=True ma non invocano il registry 55/60 con executor QM; usano gruppi generici hardcoded.", "file": "backend/phase5_full_pipeline_runtime_v51416.py", "impatto": "I PASS possono essere decorativi; non dimostrano che i motori qualità abbiano bloccato output scadenti.", "come_correggere": "Sostituire il marker con esecuzione reale di route registry e report per singolo QM.", "priorità": "P0"},
        {"gravità": "ALTO", "problema": "Smoke test: 14/36 chiamate falliscono con HTTP 500, soprattutto documenti brevi, tecnici, narrativi, generici e lista.", "file": "scripts/run_phase5_14_3_local_backend_bridge.py", "impatto": "Pipeline non robusta su input comuni.", "come_correggere": "Catturare error body, aggiungere casi fallback vietato ma errore guidato, e validare requisiti minimi per ogni generatore.", "priorità": "P1"},
        {"gravità": "ALTO", "problema": "Riassunto lungo non è proporzionato: input da 6947 caratteri produce 589 caratteri.", "file": "backend/phase5_full_pipeline_runtime_v51416.py", "impatto": "Il riassunto passa, ma non soddisfa compressione controllata/proporzionata.", "come_correggere": "Collegare il motore progressivo documenti lunghi e un Summary Compression Controller.", "priorità": "P1"},
        {"gravità": "MEDIO", "problema": "Card contengono messaggio chiave generico fisso.", "file": "backend/phase5_full_pipeline_runtime_v51416.py", "impatto": "Le card possono sembrare pulite ma poco specifiche.", "come_correggere": "Derivare messaggio chiave da concetto/fatto e applicare Card Message Completeness Checker reale.", "priorità": "P1"},
        {"gravità": "MEDIO", "problema": "Study/quiz passano da Q52 ma poi vengono riscritti da layer manuali con pattern specifici.", "file": "scripts/run_phase5_14_3_local_backend_bridge.py", "impatto": "Qualità migliorata ma non ancora mini LLM: prevalgono euristiche/template.", "come_correggere": "Separare builder, repair e validator, con dataset e metriche per ridurre riscritture rigide.", "priorità": "P2"},
        {"gravità": "MEDIO", "problema": "Il vecchio documento demo sicurezza resta in rag/indice_rag.json e documenti test.", "file": "rag/indice_rag.json", "impatto": "Innocuo se non caricato dalla pagina clean, pericoloso se un RAG server usa indice globale come fonte default.", "come_correggere": "Marcarlo come test fixture esclusa o spostarlo fuori dagli indici produttivi.", "priorità": "P2"},
    ]


def build_future_projects() -> List[Dict[str, Any]]:
    names = [
        "RAG per mini-corsi aziendali",
        "RAG per formazione interna con quiz e certificati",
        "RAG per generare slide e lezioni",
        "RAG per creare study pack completi",
        "RAG per analisi documenti aziendali",
        "RAG per manuali tecnici e procedure",
        "RAG per onboarding dipendenti",
        "RAG per scuola/ITS/università",
        "RAG per app mobile offline/prototipo",
        "RAG server/API professionale per aziende",
    ]
    return [
        {
            "progetto": name,
            "riusa": "input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report",
            "motori_qualità_servono": ["Document Grounding Checker", "No Silent Fallback Guard", "Cross Generator Consistency Checker"],
            "generatori_servono": ["riassunto", "card", "domande studio", "quiz"],
            "modifiche": "registry eseguibile unico, export, tracciamento fonti e test browser/API",
            "difficoltà": "media" if i < 7 else "alta",
            "valore_demo_aziendale": "alto",
        }
        for i, name in enumerate(names)
    ]


def build_report() -> Dict[str, Any]:
    motors = build_motors()
    static = build_static_findings()
    issues = build_issues()
    ok = sum(1 for item in SMOKE_RESULTS if item.get("ok"))
    fail = len(SMOKE_RESULTS) - ok
    da_verificare = sum(1 for m in motors if m.get("stato") == "DA VERIFICARE")
    connected = sum(1 for m in motors if m["collegato"] and m.get("stato") != "DA VERIFICARE")
    not_connected = len(motors) - connected
    return {
        "audit": "audit_completo_73_motori_rag_qualita_v1",
        "project_root": str(ROOT),
        "summary": {
            "motori_mappati": len(motors),
            "motori_qm_spiegati": 64,
            "registry_total_dichiarato": 73,
            "collegati_dedotti": connected,
            "non_collegati_o_da_verificare": not_connected,
            "smoke_ok": ok,
            "smoke_fail": fail,
            "verdetto": "PARZIALE: architettura promettente ma registry non dimostra esecuzione reale dei 73 motori.",
        },
        "motori": motors,
        "static_findings": static,
        "test_eseguiti": {
            "comandi": [
                "python3 scripts/run_phase5_14_3_local_backend_bridge.py",
                "python3 - <<'PY' ... urllib.request POST /api/generate per 9 scenari x 4 generatori",
            ],
            "risultati": SMOKE_RESULTS,
        },
        "problemi": issues,
        "suggerimenti": build_suggestions(),
        "roadmap": build_roadmap(),
        "architettura_attuale_rilevata": build_current_architecture(static),
        "architettura_futura_suggerita": build_future_architecture(),
        "progetti_futuri_suggeriti": build_future_projects(),
    }


def build_suggestions() -> List[Dict[str, Any]]:
    names = [
        ("P0", "Real Input Verification Engine", "Bloccare input demo/fallback e confermare testo reale", "prima del cleaner", "tutti"),
        ("P0", "No Silent Fallback Guard", "Trasformare fallback in errore esplicito", "UI bridge e backend", "tutti"),
        ("P0", "Document Grounding Checker", "Verificare che ogni output derivi dal documento", "post-generatore", "tutti"),
        ("P1", "Summary Narrative Coherence Engine", "Valutare coesione narrativa e transizioni", "route summary", "Riassunto"),
        ("P1", "Anti Bullet List Summary Engine", "Bloccare riassunti-lista", "route summary", "Riassunto"),
        ("P1", "Concept Hierarchy Builder", "Costruire tema/sottotemi/gerarchie", "prima generator router", "tutti"),
        ("P1", "Concept Fusion Engine", "Fondere concetti simili e ridurre ridondanze", "summary/card", "Riassunto, Card"),
        ("P1", "Summary Compression Controller", "Rendere lunghezza proporzionata al documento", "route summary", "Riassunto"),
        ("P1", "Quiz Distractor Strength Scorer", "Valutare plausibilità distrattori", "route quiz", "Test/Quiz"),
        ("P1", "UI Bridge Output Integrity Checker", "Impedire risposta corretta visibile e bypass", "UI bridge", "Test/Quiz"),
        ("P2", "Output Diversity Engine", "Differenziare summary/card/study/quiz", "cross-generator", "tutti"),
        ("P2", "Domain Adaptation Engine", "Adattare stile e criteri al dominio", "router", "tutti"),
    ]
    return [
        {
            "priorità": p,
            "nome_motore": n,
            "scopo": s,
            "dove_collegarlo": d,
            "output_controllato": o,
            "test_consigliato": "smoke scenario + fixture negativa che deve fallire",
        }
        for p, n, s, d, o in names
    ]


def build_roadmap() -> List[Dict[str, Any]]:
    return [
        {"fase": "A - Audit e pulizia", "azioni": ["materializzare registry reale", "marcare legacy", "separare test fixture da indici produttivi", "bloccare fallback/demo"]},
        {"fase": "B - Collegamento reale", "azioni": ["entrypoint unico", "route registry eseguibile", "quality_report per singolo QM", "niente pipeline parallele"]},
        {"fase": "C - Riassunti veri", "azioni": ["gerarchia concetti", "fusione concetti", "revisione narrativa", "anti-lista", "compressione proporzionale"]},
        {"fase": "D - Mini LLM reale", "azioni": ["dataset", "BM25/embedding", "classificatori qualità", "distillazione opzionale"]},
        {"fase": "E - Versione aziende", "azioni": ["API professionale", "export", "report qualità", "demo pulite", "documentazione"]},
    ]


def build_current_architecture(static: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ui": "demo-rag/test-documenti-universale.html chiama bridge locale 127.0.0.1:8765",
        "backend": "scripts/run_phase5_14_3_local_backend_bridge.py instrada summary/cards a backend/phase5_full_pipeline_runtime_v51416.py e study/quiz a q52 + repair layer",
        "registry": "reports dichiarano 73, catalogo QM contiene 64 motori spiegati; non esiste evidenza di registry unico invocato dalla pagina per tutti i 73",
        "legacy_browser": "demo-rag/universal-document-learning-engine.js contiene generatori storici ma non è caricato dalla pagina clean",
        "mini_llm": "mini_llm contiene motori euristici/semantici e registry separato, non integrato come LLM generativo addestrato nella pagina RAG corrente",
        "static_findings": static,
    }


def build_future_architecture() -> List[str]:
    return [
        "Documento reale",
        "Real Input Verification Engine",
        "Cleaner conservativo",
        "Segmentazione sezioni",
        "Theme Detector",
        "Subtheme Detector",
        "Concept Extractor",
        "Concept Hierarchy Builder",
        "Concept Ranking Engine",
        "Section Quality Matrix",
        "Generator Router",
        "Generatore specifico",
        "Output Quality Registry eseguibile",
        "Validatori specifici",
        "Cross Generator Consistency Checker",
        "UI Bridge Integrity Checker",
        "Output finale approvato",
    ]


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_markdown(data: Dict[str, Any]) -> None:
    lines: List[str] = []
    s = data["summary"]
    lines.append("# Audit completo 73 motori RAG qualità V1")
    lines.append("")
    lines.append("## 1. Stato generale del progetto")
    lines.append("")
    lines.append(f"- Motori/slot mappati: **{s['motori_mappati']}**")
    lines.append(f"- Motori QM spiegati nel catalogo ufficiale: **{s['motori_qm_spiegati']}**")
    lines.append(f"- Registry totale dichiarato: **{s['registry_total_dichiarato']}**")
    lines.append(f"- Collegati dedotti da route/report: **{s['collegati_dedotti']}**")
    lines.append(f"- Non collegati o da verificare: **{s['non_collegati_o_da_verificare']}**")
    lines.append(f"- Smoke test: **{s['smoke_ok']} PASS / {s['smoke_fail']} FAIL**")
    lines.append("")
    lines.append("Verdetto: **PARZIALE**. Il progetto ha generatori e validatori reali, ma il claim dei 73 motori non è dimostrato come esecuzione runtime unica. Il catalogo ufficiale parla di 64 QM spiegati e 73 elementi di registry/orchestrazione.")
    lines.append("")
    lines.append("## 2. Mappa completa dei 73 motori")
    lines.append("")
    lines.append("| Numero | Nome motore | File | Funzione/classe principale | Tipo motore | Collegato? | A cosa è collegato | Stato | Note |")
    lines.append("|---:|---|---|---|---|---|---|---|---|")
    for m in data["motori"]:
        lines.append(
            f"| {m['numero']} | {md_escape(m['nome_motore'])} | {md_escape(m['file'])} | {md_escape(m['funzione_classe_principale'])} | "
            f"{md_escape(m['tipo_motore'])} | {'sì' if m['collegato'] else 'no'} | {md_escape(', '.join(m['a_cosa_collegato']))} | {m['stato']} | {md_escape(m['note'])} |"
        )
    lines.append("")
    lines.append("## 3. Verifica collegamento ai quattro generatori")
    lines.append("")
    lines.append("### 3.1 Generatore Riassunti")
    lines.append("")
    lines.append("- Entry point reale pagina: `POST /api/generate` con `kind=summary`.")
    lines.append("- Runtime: `backend/phase5_full_pipeline_runtime_v51416.py`, funzione `run_summary_pipeline`.")
    lines.append("- Dichiara route 55 e `all_motors_connected=True`, ma non invoca un registry QM eseguibile; usa gruppi generici hardcoded.")
    lines.append("- Smoke: fallisce su breve/tecnico/narrativo; sul documento lungo produce 589 caratteri, non proporzionato.")
    lines.append("- Mancano gerarchia concettuale, causa-effetto strutturato, problema-soluzione, paragrafi con ruolo, compressione controllata e controllo narrativo profondo.")
    lines.append("")
    lines.append("### 3.2 Generatore Card")
    lines.append("")
    lines.append("- Runtime: `run_cards_pipeline`; produce SVG e card strutturate.")
    lines.append("- È il generatore più stabile negli smoke test: 9/9 PASS.")
    lines.append("- Problema: `messaggio_chiave` è una frase generica fissa; il report dichiara 60 motori ma non prova esecuzione dei singoli QM.")
    lines.append("")
    lines.append("### 3.3 Generatore Domande Studio")
    lines.append("")
    lines.append("- Runtime: bridge `build_study_quiz_result` → `q52_build_quality_study_questions` → repair V5.14.17/V5.14.18.")
    lines.append("- Funziona su medio/lungo/concetti simili/ripetitivo, ma fallisce su input breve, tecnico, narrativo, generico e lista.")
    lines.append("- È separato dal quiz nel rendering, ma condivide la stessa base Q52 e diversi layer di repair.")
    lines.append("")
    lines.append("### 3.4 Generatore Test / Quiz")
    lines.append("")
    lines.append("- Runtime: `q52_build_quality_quiz` + `repair_test_quiz_options_v513d3` + rewrite V5.14.18.")
    lines.append("- Critico: la UI renderizza `opt.is_correct` con classe `correct` e simbolo, quindi rivela la risposta corretta.")
    lines.append("- Fallisce sugli stessi scenari fragili delle domande studio.")
    lines.append("")
    lines.append("## 4. Test reali eseguiti")
    lines.append("")
    lines.append("Comandi:")
    for command in data["test_eseguiti"]["comandi"]:
        lines.append(f"- `{command}`")
    lines.append("")
    lines.append("| Scenario | Output | Esito | Motore | Item | Content len | Note |")
    lines.append("|---|---|---|---|---:|---:|---|")
    for r in data["test_eseguiti"]["risultati"]:
        lines.append(f"| {r['scenario']} | {r['kind']} | {'PASS' if r.get('ok') else 'FAIL'} | {md_escape(r.get('motor',''))} | {r.get('items','')} | {r.get('content_len','')} | {md_escape(r.get('error',''))} |")
    lines.append("")
    lines.append("## 5. Controllo anti-fallback e anti-demo")
    lines.append("")
    lines.append("- La pagina clean non precarica il documento demo e invia il testo della textarea al backend.")
    lines.append("- Il bridge blocca input corto e blocca `sicurezza informatica aziendale` se sotto 500 caratteri.")
    lines.append("- Restano fixture e indice RAG con `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md` e `rag/indice_rag.json`: innocui se esclusi dalla pagina clean, rischiosi se usati come indice globale default.")
    lines.append("")
    lines.append("## 6. Controllo qualità riassunti veri")
    lines.append("")
    lines.append("Il riassunto attuale è una composizione euristica di frasi/fatti selezionati. È più leggibile di una lista, ma non costruisce davvero tema, sottotemi, gerarchia, causa-effetto, problema-soluzione e paragrafi con funzione. Il documento lungo dimostra il problema: PASS tecnico con output troppo corto.")
    lines.append("")
    lines.append("## 7. Controllo mini motore LLM")
    lines.append("")
    lines.append("Il mini LLM attuale è soprattutto una famiglia di motori euristici/statistici e pipeline di regole. Ha estrazione, ranking leggero, repair, filtri e template. Non mostra apprendimento reale online, training supervisionato integrato, embedding obbligatori nel flusso finale o decoder generativo addestrato. È quindi più un mini motore RAG/regolistico che un mini LLM pieno.")
    lines.append("")
    lines.append("## 8. Come addestrare veramente il mini motore LLM")
    lines.append("")
    lines.append("- Livello 1: dataset locale input/output, esempi buoni/cattivi, scoring qualità.")
    lines.append("- Livello 2: BM25/TF-IDF evoluto, embedding locali, clustering concetti, deduplicazione semantica.")
    lines.append("- Livello 3: classificatori piccoli per genericità, frasi incomplete, pertinenza documento, riassunto narrativo vs lista.")
    lines.append("- Livello 4: teacher model per dataset, distillazione/fine tuning piccolo su coppie documento-output.")
    lines.append("- Livello 5: server/API ibrido con LLM esterno per generazione e motori locali come guardrail.")
    lines.append("")
    lines.append("## 9. Suggerimenti per ampliare i motori qualità")
    lines.append("")
    lines.append("| Priorità | Nome motore | Scopo | Dove collegarlo | Output controllato | Test consigliato |")
    lines.append("|---|---|---|---|---|---|")
    for item in data["suggerimenti"]:
        lines.append(f"| {item['priorità']} | {item['nome_motore']} | {item['scopo']} | {item['dove_collegarlo']} | {item['output_controllato']} | {item['test_consigliato']} |")
    lines.append("")
    lines.append("## 10. Nuove architetture e nuovi progetti possibili")
    lines.append("")
    lines.append("| Progetto | Riusa | Motori qualità | Generatori | Modifiche | Difficoltà | Valore demo |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in data["progetti_futuri_suggeriti"]:
        lines.append(f"| {p['progetto']} | {p['riusa']} | {', '.join(p['motori_qualità_servono'])} | {', '.join(p['generatori_servono'])} | {p['modifiche']} | {p['difficoltà']} | {p['valore_demo_aziendale']} |")
    lines.append("")
    lines.append("## 11. Problemi trovati")
    lines.append("")
    lines.append("| Gravità | Problema | File | Impatto | Come correggere | Priorità |")
    lines.append("|---|---|---|---|---|---|")
    for i in data["problemi"]:
        lines.append(f"| {i['gravità']} | {md_escape(i['problema'])} | {i['file']} | {md_escape(i['impatto'])} | {md_escape(i['come_correggere'])} | {i['priorità']} |")
    lines.append("")
    lines.append("## 12. Cose che funzionano")
    lines.append("")
    lines.append("- Il bridge locale rifiuta input mancanti/corti e non usa un fallback demo silenzioso.")
    lines.append("- Il generatore card è stabile negli smoke test e produce card grafiche renderizzabili.")
    lines.append("- Study/quiz hanno builder Q52 reali e validatori strutturali su opzioni, item e duplicati.")
    lines.append("- Esistono cataloghi e report utili; la base è promettente se trasformata in registry eseguibile.")
    lines.append("- La pagina clean semplifica il flusso utente e usa testo reale dalla textarea.")
    lines.append("")
    lines.append("## 13. Roadmap consigliata")
    lines.append("")
    for phase in data["roadmap"]:
        lines.append(f"### {phase['fase']}")
        for action in phase["azioni"]:
            lines.append(f"- {action}")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(exist_ok=True)
    data = build_report()
    JSON_OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(data)
    print(f"Report Markdown: {rel(MD_OUT)}")
    print(f"Report JSON: {rel(JSON_OUT)}")
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
