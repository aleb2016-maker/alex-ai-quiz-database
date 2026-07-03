#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test V3.9.7 - Study Pack Universale V4.
Esegue test multi-dominio e, se presente, test su documento reale RAG.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "mini_llm" / "python" / "runtime" / "mini_llm_universal_study_pack_v4.py"
REPORT_DIR = ROOT / "reports" / "study_pack_universale_v397"


def load_engine():
    spec = importlib.util.spec_from_file_location("study_pack_v4", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare engine: {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SAMPLES = {
    "informatica": """
La gestione degli accessi aziendali richiede password robuste, autenticazione a più fattori e controllo periodico degli utenti autorizzati. 
Il backup dei dati deve essere pianificato con copie separate, verifica del ripristino e responsabilità chiare per il personale tecnico. 
La sicurezza della rete dipende da firewall aggiornati, segmentazione dei servizi e monitoraggio dei tentativi di accesso anomali. 
Il phishing rimane un rischio importante perché sfrutta messaggi credibili, urgenza artificiale e collegamenti verso pagine contraffatte. 
La formazione interna riduce gli errori operativi quando spiega esempi concreti, procedure semplici e segnali di allarme riconoscibili. 
La gestione degli incidenti prevede raccolta delle evidenze, isolamento dei sistemi coinvolti e comunicazione rapida ai responsabili. 
La protezione dei dati personali richiede minimizzazione delle informazioni, autorizzazioni coerenti e registrazione delle attività sensibili. 
Il piano di continuità operativa collega backup, ruoli di emergenza, tempi di ripristino e prove periodiche documentate. 
Gli aggiornamenti software riducono vulnerabilità note quando vengono applicati con priorità, test controllati e tracciamento delle versioni. 
La revisione degli account inattivi evita accessi non necessari e limita l'esposizione a credenziali dimenticate o compromesse.
""",
    "sport": """
Il programma di allenamento combina forza, resistenza e mobilità per migliorare la prestazione senza aumentare inutilmente il rischio di infortunio. 
Il riscaldamento prepara articolazioni e sistema cardiovascolare attraverso esercizi progressivi, controllo della respirazione e movimenti tecnici semplici. 
La scheda di forza organizza serie, ripetizioni e recupero in base al livello dell'atleta e alla qualità del gesto esecutivo. 
Il lavoro di resistenza usa intensità controllate, tempi di recupero misurati e progressione settimanale per costruire continuità. 
La mobilità riduce compensi tecnici perché migliora ampiezza del movimento, controllo posturale e percezione del carico. 
Il recupero dopo le sedute include sonno, idratazione e monitoraggio della fatica per evitare sovraccarico persistente. 
La tecnica degli esercizi deve essere valutata prima di aumentare il carico, soprattutto nei movimenti complessi o veloci. 
Il diario di allenamento registra sensazioni, carichi utilizzati e progressi, così il programma può essere adattato con precisione. 
La prevenzione degli infortuni dipende da gradualità, ascolto dei segnali corporei e correzione tempestiva degli errori ricorrenti. 
La valutazione finale confronta obiettivi iniziali, prestazioni misurate e continuità del lavoro svolto durante il ciclo.
""",

    "informatica_regressione_sp3": """
La sicurezza informatica aziendale protegge dati, dispositivi, account e sistemi digitali attraverso regole operative comprensibili. 
Usare la stessa password su più siti è rischioso perché un servizio violato può esporre anche altri account collegati alla persona. 
Il password manager consente di creare credenziali robuste senza dover ricordare molte password diverse per ogni servizio. 
L'autenticazione a più fattori aggiunge un controllo ulteriore quando una password viene rubata o indovinata da un attaccante. 
I dati sensibili devono essere accessibili solo agli utenti autorizzati, con ruoli coerenti e verifiche periodiche dei permessi. 
Le e-mail sospette devono essere segnalate al reparto IT prima di cliccare link, aprire allegati o inserire credenziali. 
Gli aggiornamenti software riducono vulnerabilità note quando vengono applicati con procedure controllate e tracciamento delle versioni. 
I backup dei dati permettono il ripristino dopo errori, guasti o attacchi, ma devono essere verificati con prove periodiche. 
Non tutti devono poter modificare file critici, accedere a dati sensibili o installare software senza autorizzazione. 
Può essere inserito nella cartella `rag/documenti/` per generare quiz, test e mini-corsi sulla sicurezza informatica aziendale. 
""",
    "aziendale": """
Il processo di onboarding aziendale accompagna il nuovo personale con informazioni chiare, strumenti operativi e referenti identificabili. 
La mappatura delle responsabilità evita sovrapposizioni perché definisce ruoli, tempi decisionali e passaggi di approvazione. 
La comunicazione interna migliora quando le riunioni hanno obiettivi espliciti, verbali sintetici e azioni assegnate a persone precise. 
La gestione dei clienti richiede tracciamento delle richieste, tempi di risposta misurabili e controllo della qualità del servizio erogato. 
Il monitoraggio dei rischi collega probabilità, impatto e azioni preventive per proteggere continuità operativa e reputazione. 
La formazione periodica aggiorna competenze tecniche e comportamenti organizzativi in base ai cambiamenti dei processi. 
Gli indicatori di performance devono essere pochi, comprensibili e collegati a decisioni reali, altrimenti diventano burocrazia. 
La revisione dei fornitori considera affidabilità, costi, sicurezza delle informazioni e capacità di rispettare gli accordi. 
Il miglioramento continuo nasce dalla raccolta dei problemi ricorrenti, dall'analisi delle cause e dalla verifica delle soluzioni adottate. 
La documentazione condivisa riduce dipendenze personali perché rende procedure, criteri e responsabilità accessibili al team.
""",
}


def assert_pack_quality(engine, name: str, text: str) -> dict:
    pack = engine.build_study_pack(text, source_name=f"sample_{name}.md")
    out_json = REPORT_DIR / f"{name}_study_pack.json"
    out_md = REPORT_DIR / f"{name}_study_pack.md"
    out_json.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(engine.render_markdown(pack), encoding="utf-8")

    if pack.get("status") != "OK":
        raise AssertionError(f"{name}: status non OK: {pack.get('quality_errors')}")
    ok, errors = engine.validate_pack(pack, text)
    if not ok:
        raise AssertionError(f"{name}: validazione fallita: {errors}")
    if len(pack.get("card_studio", [])) < 8:
        raise AssertionError(f"{name}: card insufficienti")
    if len(pack.get("domande_guida", [])) < 8:
        raise AssertionError(f"{name}: domande guida insufficienti")
    if len(pack.get("quiz", [])) < 6:
        raise AssertionError(f"{name}: quiz insufficiente")
    if len(pack.get("concetti_chiave", [])) > 10:
        raise AssertionError(f"{name}: troppi concetti chiave esposti; rischia concetti deboli/orfani")

    serialized_concepts = "\n".join(pack.get("concetti_chiave", [])).lower()
    banned_concept_fragments = [
        "significa dati", "dati riservati senza", "servizio viene", "utenti usano",
        "dati dispositivi account", "dispositivi account sistemi", "rete aziendale account",
        "strumenti comportamenti dati", "mini-corsi sicurezza informatica",
        "aziendale account online", "chiaro sistema recuperare", "password altri account",
        "solo password", "aziendale protegge dati", "creare credenziali robuste",
        "poter modificare file", "buona password dovrebbe", "buona password",
        "password dovrebbe", "password dovrebbe contenere", "nuovi utenti aziendali",
        "manuale tecnico avanzato", "salvare password lunghe", "password lunghe uniche",
        "secondo controllo",
    ]
    for fragment in banned_concept_fragments:
        if fragment in serialized_concepts:
            raise AssertionError(f"{name}: concetto chiave brutto/non naturale rilevato: {fragment}")

    for concept in pack.get("concetti_chiave", []):
        if not engine.concept_label_quality(concept):
            raise AssertionError(f"{name}: concetto chiave non valido: {concept}")

    serialized_pack = json.dumps(pack, ensure_ascii=False).lower()
    banned_output_fragments = [
        "rag/documenti", "cartella `", "generare quiz", "generare test",
        "quale ruolo ha", "rispetto a", "??", "è collegato a",
        "strumenti comportamenti", "chiaro sistema recuperare", "password altri account",
        "solo password", "buona password dovrebbe", "buona password",
        "password dovrebbe", "password dovrebbe contenere", "nuovi utenti aziendali",
        "manuale tecnico avanzato",
        "secondo controllo",
    ]
    # Nota SP7: frasi come "salvare password lunghe e uniche" sono corrette
    # quando compaiono come fonte/spiegazione del password manager. Restano vietate
    # solo nei concetti chiave, dove diventerebbero etichette brutte/verbali.
    for fragment in banned_output_fragments:
        if fragment in serialized_pack:
            raise AssertionError(f"{name}: frammento vietato nell'output: {fragment}")

    return pack


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    engine = load_engine()
    results = []

    for name, text in SAMPLES.items():
        pack = assert_pack_quality(engine, name, text)
        results.append({
            "test": name,
            "status": pack["status"],
            "profile": pack["profile"]["primary"],
            "concepts": len(pack["concetti_chiave"]),
            "cards": len(pack["card_studio"]),
            "questions": len(pack["domande_guida"]),
            "quiz": len(pack["quiz"]),
        })

    # Test documento reale, se presente nel repository.
    real_doc = ROOT / "rag" / "documenti" / "documento_rag_sicurezza_informatica_aziendale.md"
    if real_doc.exists():
        text = real_doc.read_text(encoding="utf-8", errors="replace")
        pack = assert_pack_quality(engine, "documento_reale", text)
        results.append({
            "test": "documento_reale",
            "status": pack["status"],
            "profile": pack["profile"]["primary"],
            "concepts": len(pack["concetti_chiave"]),
            "cards": len(pack["card_studio"]),
            "questions": len(pack["domande_guida"]),
            "quiz": len(pack["quiz"]),
        })
    else:
        results.append({
            "test": "documento_reale",
            "status": "SKIPPED",
            "reason": "File rag/documenti/documento_rag_sicurezza_informatica_aziendale.md non presente in questa copia locale.",
        })

    blocked_short = engine.build_study_pack("Test corto senza contenuto sufficiente.", source_name="short.txt")
    if blocked_short.get("status") != "QUALITY_BLOCKED":
        raise AssertionError("Il documento corto doveva essere bloccato da QUALITY_BLOCKED.")
    results.append({"test": "quality_block_documento_corto", "status": "QUALITY_BLOCKED_OK"})

    report_md = REPORT_DIR / "validazione_v397.md"
    lines = ["# Validazione Study Pack Universale V4 - V3.9.7", ""]
    for row in results:
        lines.append(f"- `{row['test']}`: `{row['status']}`" + (f" profilo `{row.get('profile')}`" if row.get("profile") else ""))
    lines.append("")
    lines.append("Esito finale: PASS")
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print("PASS - Study Pack Universale V4 V3.9.7")
    print(f"Report: {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
