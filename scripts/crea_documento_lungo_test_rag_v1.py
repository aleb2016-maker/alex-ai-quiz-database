#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "rag" / "documenti"
MD_PATH = OUT_DIR / "test_documento_lungo_aziendale_120_pagine.md"
TXT_PATH = OUT_DIR / "test_documento_lungo_aziendale_120_pagine.txt"

TOPICS = [
    ("sicurezza informatica", "firewall", "segmentazione rete", "monitoraggio accessi"),
    ("onboarding dipendenti", "onboarding", "account iniziali", "formazione guidata"),
    ("gestione incidenti", "incidenti", "triage operativo", "comunicazione escalation"),
    ("backup e ripristino", "backup", "retention dati", "verifica restore"),
    ("privacy e trattamento dati", "privacy", "minimizzazione", "registro trattamenti"),
    ("policy password", "password", "autenticazione forte", "rotazione credenziali"),
    ("phishing e social engineering", "phishing", "segnalazione email", "simulazioni periodiche"),
    ("audit e conformita", "audit", "evidenze controlli", "piano azioni"),
    ("continuità operativa", "continuità operativa", "business continuity", "ripartenza servizi"),
    ("documentazione tecnica", "documentazione tecnica", "runbook", "versionamento procedure"),
    ("ruoli e responsabilita", "ruoli", "matrice RACI", "approvazioni operative"),
    ("workflow interni", "workflow", "passaggi standard", "controlli qualita"),
]

DEPARTMENTS = [
    "Risorse Umane",
    "IT Operations",
    "Sicurezza",
    "Legal e Compliance",
    "Customer Care",
    "Amministrazione",
    "Produzione",
    "Project Management",
]

SCENARIOS = [
    "un nuovo collega accede al gestionale per la prima volta",
    "un responsabile riceve una segnalazione urgente fuori orario",
    "un sistema critico mostra tempi di risposta anomali",
    "un audit interno richiede evidenze entro la giornata",
    "un fornitore chiede accesso temporaneo a un ambiente tecnico",
    "una email sospetta viene inoltrata al team sicurezza",
    "un ripristino da backup deve essere provato prima del rilascio",
    "un reparto aggiorna una procedura usata da molte persone",
]


def paragraph(page: int, topic: str, keyword: str, detail_a: str, detail_b: str, index: int) -> str:
    department = DEPARTMENTS[(page + index) % len(DEPARTMENTS)]
    scenario = SCENARIOS[(page * 2 + index) % len(SCENARIOS)]
    cadence = ["giornaliera", "settimanale", "mensile", "trimestrale"][(page + index) % 4]
    control_code = f"CTRL-{page:03d}-{index + 1}"

    return (
        f"Nel contesto {department}, la sezione {page:03d}.{index + 1} descrive come gestire "
        f"{topic} quando {scenario}. Il riferimento principale e {keyword}, collegato a "
        f"{detail_a} e {detail_b}. La procedura richiede una verifica {cadence}, una traccia "
        f"scritta nel registro operativo e una conferma del responsabile di processo. Ogni "
        f"attivita deve indicare chi ha autorizzato l'azione, quali sistemi sono stati coinvolti, "
        f"quali rischi residui restano aperti e quale evidenza permette di ricostruire la scelta. "
        f"Il controllo {control_code} evita passaggi informali e rende confrontabili i risultati "
        f"tra reparti, sedi e fornitori. Se il controllo non produce evidenze sufficienti, il team "
        f"deve aprire una nota di miglioramento, assegnare una scadenza e ripetere il test entro "
        f"il ciclo successivo."
    )


def build_page(page: int) -> str:
    topic, keyword, detail_a, detail_b = TOPICS[(page - 1) % len(TOPICS)]
    secondary = TOPICS[(page + 3) % len(TOPICS)][1]
    owner = DEPARTMENTS[page % len(DEPARTMENTS)]
    section = f"MAN-AZI-{((page - 1) // 10) + 1:02d}.{((page - 1) % 10) + 1:02d}"
    paragraphs = [paragraph(page, topic, keyword, detail_a, detail_b, i) for i in range(5)]

    checklist = [
        f"- Identificare proprietario, sistemi e dati collegati a {topic}.",
        f"- Applicare il controllo su {keyword} e registrare l'esito nel verbale operativo.",
        f"- Verificare dipendenze con {secondary}, fornitori, utenti interni e strumenti di ticketing.",
        "- Archiviare evidenze, decisioni, tempi di completamento e azioni correttive.",
        "- Riesaminare la procedura quando cambia un ruolo, un rischio o una piattaforma.",
    ]

    case_text = (
        f"Mini caso pratico: il reparto {owner} rileva una deviazione durante una attivita su "
        f"{topic}. Il referente blocca il flusso automatico, informa il responsabile, confronta "
        f"le evidenze con la policy vigente e decide se aprire un incidente, una richiesta di "
        f"cambio o un semplice aggiornamento documentale. La lezione appresa viene collegata a "
        f"{keyword}, {detail_a}, {detail_b} e al piano di continuità operativa."
    )

    keywords = [
        keyword,
        detail_a,
        detail_b,
        secondary,
        "firewall",
        "phishing",
        "backup",
        "privacy",
        "onboarding",
        "incidenti",
        "password",
        "audit",
        "continuità operativa",
    ]

    return "\n\n".join([
        f"--- PAGINA {page:03d} ---",
        f"Titolo pagina {page:03d}: Manuale aziendale - {topic}",
        f"Riferimento sezione: {section}",
        *paragraphs,
        "Elenco operativo:\n" + "\n".join(checklist),
        case_text,
        "Parole chiave: " + ", ".join(dict.fromkeys(keywords)),
    ])


def build_document() -> str:
    header = [
        "# Manuale aziendale completo RAG V1",
        "",
        "Documento sintetico lungo per testare estrazione, pagine logiche, chunk e batch.",
        "Non contiene dati reali e non deve essere collegato alla demo ufficiale.",
        "",
    ]
    pages = [build_page(page) for page in range(1, 121)]
    return "\n".join(header + pages) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    document = build_document()
    MD_PATH.write_text(document, encoding="utf-8")
    TXT_PATH.write_text(document, encoding="utf-8")
    print(f"Creato: {MD_PATH.relative_to(ROOT)} ({len(document)} caratteri)")
    print(f"Creato: {TXT_PATH.relative_to(ROOT)} ({len(document)} caratteri)")


if __name__ == "__main__":
    main()
