from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Sequence


PHASE = "5.12I.2"
PHASE_LABEL = "FASE 5.12I.2 — CATALOGO UFFICIALE MOTORI QUALITÀ DA LISTA SALVATA"

EXPECTED_OFFICIAL_QM_MOTORS = 64
EXPECTED_REGISTRY_TOTAL_AFTER_H2 = 73

H2_REPORT = Path("reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json")

DEFAULT_JSON_REPORT = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.json")
DEFAULT_MD_REPORT = Path("reports/phase5_12i2_official_quality_motor_catalog_v1.md")


SECTION_LABELS = {
    "card": "Card",
    "summary": "Riassunto",
    "study_questions": "Domande studio",
    "test_quiz": "Test/Quiz",
}

ALL_SECTIONS = ["card", "summary", "study_questions", "test_quiz"]


@dataclass
class OfficialMotor:
    qm_id: str
    number: int
    group: str
    name: str
    what_it_does: str
    universal: str
    used_by_sections: List[str]
    state: str


@dataclass
class SectionRoute:
    section_type: str
    section_label: str
    total_controls_after_h2: int
    quality_matrix_controls: int
    selector_orchestrator_controls: int
    selector_orchestrator_ids: List[str]


@dataclass
class OfficialCatalogReport:
    phase: str
    label: str
    status: str
    official_qm_motors_count: int
    registry_total_after_h2: int
    registry_total_note: str
    motors: List[OfficialMotor]
    section_routes: List[SectionRoute]
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def sections(*items: str) -> List[str]:
    return list(items)


def all_sections() -> List[str]:
    return list(ALL_SECTIONS)


def motor(
    number: int,
    group: str,
    name: str,
    what_it_does: str,
    universal: str,
    used_by_sections: Sequence[str],
    state: str = "attivo",
) -> OfficialMotor:
    return OfficialMotor(
        qm_id=f"qm_{number:03d}",
        number=number,
        group=group,
        name=name,
        what_it_does=what_it_does,
        universal=universal,
        used_by_sections=list(used_by_sections),
        state=state,
    )


def build_official_motors() -> List[OfficialMotor]:
    motors: List[OfficialMotor] = []

    # 1–12: qualità testuale
    motors.extend([
        motor(1, "Controlli qualità testuale", "Grammatica italiana corretta", "Controlla che l’output non contenga errori grammaticali italiani.", "sì", all_sections()),
        motor(2, "Controlli qualità testuale", "Accenti corretti", "Controlla accenti su parole come perché, può, più, già, cioè, così, però, qual è.", "sì", all_sections()),
        motor(3, "Controlli qualità testuale", "Apostrofi corretti", "Controlla apostrofi in forme come un’informazione, un’idea, un’azione, l’utente, d’accordo.", "sì", all_sections()),
        motor(4, "Controlli qualità testuale", "Punteggiatura corretta", "Controlla uso corretto di punti, virgole, due punti, punti interrogativi ed esclamativi.", "sì", all_sections()),
        motor(5, "Controlli qualità testuale", "Spazi corretti prima/dopo punteggiatura", "Controlla spazi doppi, spazi mancanti e spazi errati prima o dopo la punteggiatura.", "sì", all_sections()),
        motor(6, "Controlli qualità testuale", "Frasi complete", "Verifica che le frasi abbiano senso compiuto e struttura completa.", "sì", all_sections()),
        motor(7, "Controlli qualità testuale", "Assenza di frasi spezzate", "Blocca frasi spezzate, tagliate o montate male.", "sì", all_sections()),
        motor(8, "Controlli qualità testuale", "Assenza di frasi non terminate", "Blocca frasi che iniziano ma non arrivano a una chiusura logica.", "sì", all_sections()),
        motor(9, "Controlli qualità testuale", "Assenza di finali sospetti", "Blocca finali sospetti come frasi che finiscono con e, di, con, per, che, del, della.", "sì", all_sections()),
        motor(10, "Controlli qualità testuale", "Assenza di frasi riempitive", "Blocca frasi inutili, decorative, vuote o che allungano senza aggiungere contenuto.", "sì", all_sections()),
        motor(11, "Controlli qualità testuale", "Assenza di testo generico", "Blocca frasi generiche come documento analizzato, contenuti generati, punto centrale quando non sono specifiche.", "sì", all_sections()),
        motor(12, "Controlli qualità testuale", "Assenza di vecchi fallback/demo/test", "Blocca residui di fallback, demo, esempi di test e testi vecchi non derivati dal documento reale.", "sì", all_sections()),
    ])

    # 13–22: qualità didattica
    motors.extend([
        motor(13, "Controlli qualità didattica", "Domande studio naturali", "Verifica che le domande studio siano naturali e non robotiche.", "no", sections("study_questions")),
        motor(14, "Controlli qualità didattica", "Domande studio utili per ripassare", "Verifica che le domande aiutino davvero a ripassare il contenuto.", "no", sections("study_questions")),
        motor(15, "Controlli qualità didattica", "Risposte guida specifiche", "Verifica che le risposte guida siano specifiche, concrete e aderenti al contenuto.", "no", sections("study_questions")),
        motor(16, "Controlli qualità didattica", "Spiegazioni test chiare", "Verifica che le spiegazioni dei quiz siano chiare e comprensibili.", "no", sections("test_quiz")),
        motor(17, "Controlli qualità didattica", "Spiegazioni non troppo corte", "Blocca spiegazioni troppo brevi, vuote o insufficienti.", "no", sections("test_quiz", "study_questions")),
        motor(18, "Controlli qualità didattica", "Tono didattico finale", "Controlla che il tono sia didattico, utile e adatto allo studio.", "no", sections("summary", "study_questions", "test_quiz")),
        motor(19, "Controlli qualità didattica", "Categorie presenti", "Verifica che siano presenti categorie quando servono a organizzare il contenuto.", "no", all_sections()),
        motor(20, "Controlli qualità didattica", "Sottocategorie presenti", "Verifica che siano presenti sottocategorie quando servono a rendere l’output più preciso.", "no", all_sections()),
        motor(21, "Controlli qualità didattica", "Coerenza tra domanda, risposta e contenuto", "Controlla che domanda, risposta e contenuto originale siano coerenti.", "no", sections("study_questions", "test_quiz")),
        motor(22, "Controlli qualità didattica", "Niente risposte vaghe", "Blocca risposte vaghe, generiche o scollegate dal documento.", "no", sections("study_questions", "test_quiz")),
    ])

    # 23–32: card / riassunto / fonti
    motors.extend([
        motor(23, "Controlli card / riassunto / fonti", "Card scritte bene", "Verifica che le card siano scritte bene, leggibili e utili.", "no", sections("card")),
        motor(24, "Controlli card / riassunto / fonti", "Card non troppo corte", "Blocca card troppo povere o con contenuto insufficiente.", "no", sections("card")),
        motor(25, "Controlli card / riassunto / fonti", "Card non troppo compresse", "Blocca card troppo dense, schiacciate o difficili da leggere.", "no", sections("card")),
        motor(26, "Controlli card / riassunto / fonti", "Messaggio chiave completo", "Verifica che il messaggio chiave sia completo e non monco.", "no", sections("card", "summary")),
        motor(27, "Controlli card / riassunto / fonti", "Riassunto chiaro", "Verifica che il riassunto sia chiaro, ordinato e comprensibile.", "no", sections("summary")),
        motor(28, "Controlli card / riassunto / fonti", "Punti chiave leggibili", "Verifica che i punti chiave siano leggibili, utili e non confusi.", "no", sections("card", "summary")),
        motor(29, "Controlli card / riassunto / fonti", "Fonti visibili belle", "Verifica che le fonti siano visibili, pulite e presentate bene.", "no", sections("card", "summary")),
        motor(30, "Controlli card / riassunto / fonti", "Fonti coerenti", "Verifica fonti coerenti, ad esempio Fonte: sezione “Sicurezza informatica”.", "no", sections("card", "summary")),
        motor(31, "Controlli card / riassunto / fonti", "Niente fonti brutte", "Blocca fonti brutte o tecniche come knowledge_base_json o Documento analizzato.", "no", sections("card", "summary")),
        motor(32, "Controlli card / riassunto / fonti", "Layout grafico controllato", "Controlla struttura, layout grafico, leggibilità e ordine visuale.", "no", sections("card")),
    ])

    # 33–44: test separati
    motors.extend([
        motor(33, "Controlli test separati", "Test separato da card/riassunto/domande studio", "Garantisce che il test non venga mischiato con card, riassunto o domande studio.", "no", sections("test_quiz")),
        motor(34, "Controlli test separati", "Opzioni interne validate", "Valida le opzioni interne del quiz prima della visualizzazione.", "no", sections("test_quiz")),
        motor(35, "Controlli test separati", "Opzioni visibili pulite", "Controlla che le opzioni mostrate all’utente siano pulite e leggibili.", "no", sections("test_quiz")),
        motor(36, "Controlli test separati", "Risposta corretta interna", "Verifica che la risposta corretta interna sia presente e valida.", "no", sections("test_quiz")),
        motor(37, "Controlli test separati", "Risposta corretta visibile", "Verifica che la risposta corretta visibile sia coerente con quella interna.", "no", sections("test_quiz")),
        motor(38, "Controlli test separati", "Mappa sicura tra risposta interna e visibile", "Controlla la mappa tra risposta interna, risposta visibile e opzioni.", "no", sections("test_quiz")),
        motor(39, "Controlli test separati", "4 opzioni per domanda", "Verifica che ogni domanda abbia esattamente quattro opzioni.", "no", sections("test_quiz")),
        motor(40, "Controlli test separati", "Risposta corretta presente tra le opzioni", "Verifica che la risposta corretta sia presente tra le opzioni disponibili.", "no", sections("test_quiz")),
        motor(41, "Controlli test separati", "Distrattori forti", "Verifica che i distrattori siano plausibili, forti e non banali.", "no", sections("test_quiz")),
        motor(42, "Controlli test separati", "Niente opzioni duplicate nella stessa domanda", "Blocca duplicati tra le opzioni della stessa domanda.", "no", sections("test_quiz")),
        motor(43, "Controlli test separati", "Niente ripetizioni globali eccessive", "Blocca ripetizioni eccessive tra domande, risposte e opzioni.", "no", sections("test_quiz")),
        motor(44, "Controlli test separati", "Compatibilità obbligatoria col bridge motori quiz V3.5B", "Verifica che il quiz sia compatibile con il bridge motori quiz V3.5B.", "no", sections("test_quiz")),
    ])

    # 45–50: duplicati e ripetizioni
    motors.extend([
        motor(45, "Controlli duplicati e ripetizioni", "Duplicati esatti", "Rileva contenuti esattamente duplicati.", "sì", all_sections()),
        motor(46, "Controlli duplicati e ripetizioni", "Quasi duplicati", "Rileva contenuti quasi identici o troppo sovrapponibili.", "sì", all_sections()),
        motor(47, "Controlli duplicati e ripetizioni", "Ripetizioni inutili", "Blocca ripetizioni che non aggiungono valore.", "sì", all_sections()),
        motor(48, "Controlli duplicati e ripetizioni", "Ripetizioni meccaniche tra domande", "Blocca ripetizioni meccaniche tra domande, soprattutto in domande studio e quiz.", "no", sections("study_questions", "test_quiz")),
        motor(49, "Controlli duplicati e ripetizioni", "Frasi troppo simili", "Rileva frasi troppo simili tra loro.", "sì", all_sections()),
        motor(50, "Controlli duplicati e ripetizioni", "Stesso contenuto ripetuto senza motivo", "Blocca lo stesso contenuto ripetuto senza motivo; distingue però ripetizioni legittime tra sezioni diverse.", "sì", all_sections()),
    ])

    # 51–60: selezionatore / orchestratore
    motors.extend([
        motor(51, "Controlli selezionatore / orchestratore", "Il compito richiesto deve selezionare i motori giusti", "Seleziona i motori corretti in base alla richiesta dell’utente.", "sì", all_sections()),
        motor(52, "Controlli selezionatore / orchestratore", "Riassunto → motore didattico", "Quando l’utente chiede un riassunto, instrada verso i motori didattici e di sintesi corretti.", "no", sections("summary")),
        motor(53, "Controlli selezionatore / orchestratore", "Card → motore didattico + layout", "Quando l’utente chiede card, instrada verso motori didattici e layout.", "no", sections("card")),
        motor(54, "Controlli selezionatore / orchestratore", "Domande studio → motore didattico", "Quando l’utente chiede domande studio, instrada verso motori didattici.", "no", sections("study_questions")),
        motor(55, "Controlli selezionatore / orchestratore", "Test → bridge quiz + motore test + bridge quiz", "Quando l’utente chiede test, instrada verso bridge quiz, motore test e compatibilità quiz.", "no", sections("test_quiz")),
        motor(56, "Controlli selezionatore / orchestratore", "Completo/PDF/app/web → orchestratore", "Quando l’utente chiede output completo, PDF, app o web, passa dal livello orchestratore.", "sì", all_sections()),
        motor(57, "Controlli selezionatore / orchestratore", "Niente motori inutili", "Evita di attivare motori non necessari per il compito richiesto.", "sì", all_sections()),
        motor(58, "Controlli selezionatore / orchestratore", "Niente output non richiesto", "Evita output extra non richiesti dall’utente.", "sì", all_sections()),
        motor(59, "Controlli selezionatore / orchestratore", "Output finale pronto per UI/PDF/app", "Verifica che l’output finale sia pronto per essere usato in UI, PDF o app.", "sì", all_sections(), "da verificare alla fine"),
        motor(60, "Controlli selezionatore / orchestratore", "Report qualità sempre leggibile", "Garantisce che il report qualità sia sempre chiaro, leggibile e utile.", "sì", all_sections(), "da ricreare/collegare"),
    ])

    # 61–64: linguistica avanzata / repair
    motors.extend([
        motor(61, "Controlli linguistici avanzati / repair", "Naturalezza linguistica anti-keyword", "Blocca frasi robotiche, liste grezze di parole chiave e testi meccanici; l’output deve sembrare scritto da una persona.", "sì", all_sections()),
        motor(62, "Controlli linguistici avanzati / repair", "Accordo grammaticale e pronomi", "Verifica genere, numero, articoli, participi e pronomi collegati a titoli e contenuti.", "sì", all_sections()),
        motor(63, "Controlli linguistici avanzati / repair", "Correzione frasi non finite con contesto", "Corregge frasi non finite usando contesto, tema, sottotema e sottocategorie.", "sì", all_sections()),
        motor(64, "Controlli linguistici avanzati / repair", "Correzione parole scritte male con lettere invertite", "Corregge parole scritte male, lettere invertite e micro-errori ortografici.", "sì", all_sections()),
    ])

    return motors


def read_h2_registry_total() -> int:
    if not H2_REPORT.exists():
        return 0
    data = json.loads(H2_REPORT.read_text(encoding="utf-8"))
    return int(data.get("registry_total_motors", 0))


def build_section_routes() -> List[SectionRoute]:
    selector_ids = [f"qm_{i:03d}" for i in range(51, 59)]
    return [
        SectionRoute("card", "Card", 60, 52, 8, selector_ids),
        SectionRoute("summary", "Riassunto", 55, 47, 8, selector_ids),
        SectionRoute("study_questions", "Domande studio", 51, 43, 8, selector_ids),
        SectionRoute("test_quiz", "Test/Quiz", 63, 55, 8, selector_ids),
    ]


def run_phase5_12i2() -> OfficialCatalogReport:
    defects: List[str] = []
    warnings: List[str] = []

    motors = build_official_motors()
    h2_registry_total = read_h2_registry_total()

    if len(motors) != EXPECTED_OFFICIAL_QM_MOTORS:
        defects.append(f"Motori ufficiali attesi 64, trovati {len(motors)}.")

    expected_ids = [f"qm_{i:03d}" for i in range(1, EXPECTED_OFFICIAL_QM_MOTORS + 1)]
    actual_ids = [motor.qm_id for motor in motors]
    if actual_ids != expected_ids:
        defects.append(f"Sequenza ID errata. Attesi {expected_ids}, trovati {actual_ids}.")

    if h2_registry_total != EXPECTED_REGISTRY_TOTAL_AFTER_H2:
        defects.append(
            f"Registry H.2 atteso 73, trovato {h2_registry_total}. "
            "Controllare report H.2."
        )

    for item in motors:
        if not item.what_it_does.strip():
            defects.append(f"Descrizione mancante per {item.qm_id}.")
        if not item.used_by_sections:
            defects.append(f"Sezioni mancanti per {item.qm_id}.")

    status = (
        "PASS - Fase 5.12I.2: OFFICIAL_QUALITY_MOTOR_CATALOG_READY"
        if not defects
        else "FAIL - Fase 5.12I.2: OFFICIAL_QUALITY_MOTOR_CATALOG_NOT_READY"
    )

    return OfficialCatalogReport(
        phase=PHASE,
        label=PHASE_LABEL,
        status=status,
        official_qm_motors_count=len(motors),
        registry_total_after_h2=h2_registry_total,
        registry_total_note=(
            "Il registry H.2 conta 73 elementi di orchestrazione/route; "
            "la lista ufficiale salvata dei motori qualità contiene 64 motori QM spiegati."
        ),
        motors=motors,
        section_routes=build_section_routes(),
        defects=defects,
        warnings=warnings,
        notes=[
            "Catalogo corretto usando la lista ufficiale salvata dall’utente.",
            "Nessun qm_065–qm_073 viene inventato.",
            "qm_059 e qm_060 sono inclusi come controlli finali selector/orchestrator.",
            "La distinzione corretta è: 64 motori qualità QM spiegati; 73 elementi totali nel registry/orchestrazione H.2.",
        ],
    )


def format_sections(values: Sequence[str]) -> str:
    return ", ".join(SECTION_LABELS.get(value, value) for value in values)


def write_json_report(report: OfficialCatalogReport) -> None:
    DEFAULT_JSON_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON_REPORT.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown_report(report: OfficialCatalogReport) -> None:
    lines: List[str] = []

    lines.append(f"# {report.label}")
    lines.append("")
    lines.append(f"Status: `{report.status}`")
    lines.append("")
    lines.append("## Sintesi corretta")
    lines.append("")
    lines.append(f"- Motori qualità ufficiali spiegati: `{report.official_qm_motors_count}`")
    lines.append(f"- Registry totale dopo H.2: `{report.registry_total_after_h2}`")
    lines.append(f"- Nota: {report.registry_total_note}")
    lines.append("")
    lines.append("## Route per sezione")
    lines.append("")
    lines.append("| Sezione | Controlli qualità G.2 | Selector/orchestrator | Totale route | Selector/orchestrator IDs |")
    lines.append("|---|---:|---:|---:|---|")
    for route in report.section_routes:
        ids = ", ".join(f"`{item}`" for item in route.selector_orchestrator_ids)
        lines.append(
            f"| {route.section_label} | {route.quality_matrix_controls} | "
            f"{route.selector_orchestrator_controls} | {route.total_controls_after_h2} | {ids} |"
        )
    lines.append("")
    lines.append("## Lista ufficiale completa dei motori qualità")
    lines.append("")
    lines.append("| QM | Gruppo | Nome | Cosa fa | Universale | Usato da | Stato |")
    lines.append("|---|---|---|---|---|---|---|")
    for item in report.motors:
        lines.append(
            f"| `{item.qm_id}` | {item.group} | {item.name} | {item.what_it_does} | "
            f"{item.universal} | {format_sections(item.used_by_sections)} | {item.state} |"
        )
    lines.append("")
    lines.append("## Defects")
    lines.append("")
    if report.defects:
        for defect in report.defects:
            lines.append(f"- {defect}")
    else:
        lines.append("- Nessuno")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report.warnings:
        for warning in report.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- Nessuno")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    for note in report.notes:
        lines.append(f"- {note}")
    lines.append("")

    DEFAULT_MD_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


def run_and_write_phase5_12i2_report() -> OfficialCatalogReport:
    report = run_phase5_12i2()
    write_json_report(report)
    write_markdown_report(report)
    return report


if __name__ == "__main__":
    result = run_and_write_phase5_12i2_report()

    print(result.status)
    print(f"Official QM motors: {result.official_qm_motors_count}")
    print(f"Registry total after H.2: {result.registry_total_after_h2}")
    print(f"JSON report: {DEFAULT_JSON_REPORT}")
    print(f"Markdown report: {DEFAULT_MD_REPORT}")

    if result.defects:
        print("Defects:")
        for defect in result.defects:
            print(f"- {defect}")
        raise SystemExit(1)

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
