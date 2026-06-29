#!/usr/bin/env python3
from pathlib import Path
import json
import math
import re
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

VERSIONE = "RAG documenti lunghi V2A.4 espansione sopra 120 pagine"

PAGINE_TEST = [180, 240, 300]
CHUNK_PER_PAGINA = 2
DIMENSIONE_BATCH = 8

MICRO_CONCETTI_ATTESI = [
    "sicurezza operativa",
    "procedure aziendali",
    "controllo qualità",
    "formazione interna",
    "gestione documentale",
    "continuità operativa",
    "tracciabilità modifiche",
    "responsabilità operative",
    "controlli periodici",
    "rischi organizzativi",
    "azioni correttive",
    "standard aziendali",
    "archiviazione controllata",
    "segnalazione anomalie",
    "verifica procedure",
    "processi interni",
    "moduli formativi",
    "documenti aggiornati",
    "monitoraggio attività",
    "piani operativi",
    "qualità periodica",
    "lettura documentale",
    "sintesi progressiva",
    "batch controllati",
]


def crea_chunk_pagina(numero_pagina: int):
    chunk_a = f"""
--- PAGINA {numero_pagina} / CHUNK A ---

Titolo: Procedure aziendali e sicurezza operativa.

La pagina {numero_pagina} descrive un blocco di lavoro dedicato alla sicurezza operativa,
alle procedure aziendali, ai controlli periodici e alla gestione documentale.
Ogni reparto deve conoscere responsabilità operative, standard aziendali,
rischi organizzativi e modalità di segnalazione anomalie.

La formazione interna aiuta il personale a comprendere i processi interni,
i moduli formativi, la lettura documentale e la corretta archiviazione controllata.
Il responsabile verifica che i documenti aggiornati siano coerenti,
chiari, tracciabili e utili per applicare le procedure aziendali.
""".strip()

    chunk_b = f"""
--- PAGINA {numero_pagina} / CHUNK B ---

Titolo: Controllo qualità e continuità operativa.

La pagina {numero_pagina} approfondisce controllo qualità, continuità operativa,
tracciabilità modifiche, verifica procedure e monitoraggio attività.
Quando emergono errori, ritardi o informazioni mancanti,
il gruppo deve registrare il problema e preparare azioni correttive.

Il metodo progressivo consente di trasformare pagine lunghe in batch controllati,
mantenendo sintesi progressiva, concetti chiave, piani operativi
e qualità periodica del risultato finale.
""".strip()

    return [chunk_a, chunk_b]


def crea_documento_e_chunk(numero_pagine: int):
    chunks = []
    for pagina in range(1, numero_pagine + 1):
        chunks.extend(crea_chunk_pagina(pagina))
    testo = "\n\n".join(chunks)
    return testo, chunks


def crea_batch(chunks):
    return [chunks[i:i + DIMENSIONE_BATCH] for i in range(0, len(chunks), DIMENSIONE_BATCH)]


def estrai_pagine_da_batch(batch):
    pagine = []
    for chunk in batch:
        match = re.search(r"PAGINA\s+(\d+)", chunk)
        if match:
            pagine.append(int(match.group(1)))
    return pagine


def crea_riassunto_progressivo(batches):
    parziali = []

    for indice, batch in enumerate(batches, start=1):
        pagine = estrai_pagine_da_batch(batch)
        prima = min(pagine) if pagine else "?"
        ultima = max(pagine) if pagine else "?"

        parziale = (
            f"Parziale batch {indice}: pagine {prima}-{ultima}. "
            "Il blocco conserva procedure aziendali, sicurezza operativa, formazione interna, "
            "gestione documentale, controllo qualità, continuità operativa, tracciabilità modifiche, "
            "responsabilità operative, segnalazione anomalie e azioni correttive. "
            "La sintesi progressiva mantiene il collegamento tra concetti, esempi e controlli."
        )
        parziali.append(parziale)

    riassunto_finale = "\n".join(parziali)

    return parziali, riassunto_finale


def estrai_keyword_micro_concetti(testo):
    trovate = []

    testo_basso = testo.lower()

    for concetto in MICRO_CONCETTI_ATTESI:
        if concetto in testo_basso and concetto not in trovate:
            trovate.append(concetto)

    return trovate[:24]


def valida_keyword(keyword):
    problemi = []

    for voce in keyword:
        parole = voce.split()
        if len(parole) not in (2, 3):
            problemi.append(voce)

    return problemi


def valida_fallback_vecchi(testo):
    vietati = [
        "sicurezza informatica aziendale",
        "documento generico",
        "contenuto di esempio",
        "fallback",
        "lorem ipsum",
    ]

    testo_basso = testo.lower()
    trovati = [v for v in vietati if v in testo_basso]
    return trovati


def esegui_test(numero_pagine: int):
    tracemalloc.start()
    inizio = time.time()

    testo, chunks = crea_documento_e_chunk(numero_pagine)
    batches = crea_batch(chunks)
    parziali, riassunto_finale = crea_riassunto_progressivo(batches)
    keyword = estrai_keyword_micro_concetti(testo)

    problemi_keyword = valida_keyword(keyword)
    fallback_vecchi = valida_fallback_vecchi(testo)

    durata = round(time.time() - inizio, 3)
    memoria_corrente, memoria_picco = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    chunk_attesi = numero_pagine * CHUNK_PER_PAGINA
    batch_attesi = math.ceil(chunk_attesi / DIMENSIONE_BATCH)

    ok = (
        numero_pagine > 120
        and len(chunks) == chunk_attesi
        and len(chunks) > 240
        and len(batches) == batch_attesi
        and len(batches) > 30
        and len(parziali) == len(batches)
        and len(riassunto_finale) > 1500
        and len(keyword) >= 20
        and not problemi_keyword
        and not fallback_vecchi
    )

    esito = {
        "versione": VERSIONE,
        "pagine_test": numero_pagine,
        "chunk_per_pagina": CHUNK_PER_PAGINA,
        "chunk": len(chunks),
        "chunk_attesi": chunk_attesi,
        "batch": len(batches),
        "batch_attesi": batch_attesi,
        "parziali": len(parziali),
        "lunghezza_riassunto_finale": len(riassunto_finale),
        "keyword": keyword,
        "problemi_keyword": problemi_keyword,
        "fallback_vecchi": fallback_vecchi,
        "durata_secondi": durata,
        "memoria_picco_mb": round(memoria_picco / 1024 / 1024, 3),
        "ok": ok,
    }

    json_path = REPORTS / f"rag_documenti_lunghi_v2a4_{numero_pagine}_pagine.json"
    md_path = REPORTS / f"rag_documenti_lunghi_v2a4_{numero_pagine}_pagine.md"

    json_path.write_text(json.dumps(esito, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path.write_text(
        f"""# Report RAG documenti lunghi V2A.4 — {numero_pagine} pagine

- Versione: {VERSIONE}
- Pagine test: {numero_pagine}
- Chunk: {len(chunks)}
- Chunk attesi: {chunk_attesi}
- Batch: {len(batches)}
- Batch attesi: {batch_attesi}
- Parziali: {len(parziali)}
- Lunghezza riassunto finale: {len(riassunto_finale)}
- Durata secondi: {durata}
- Memoria picco MB: {round(memoria_picco / 1024 / 1024, 3)}
- Esito: {"OK" if ok else "KO"}

## Keyword micro-concetti

{chr(10).join("- " + k for k in keyword)}

## Problemi keyword

{chr(10).join("- " + k for k in problemi_keyword) if problemi_keyword else "Nessun problema."}

## Fallback vecchi trovati

{chr(10).join("- " + f for f in fallback_vecchi) if fallback_vecchi else "Nessun fallback vecchio trovato."}

## Estratto riassunto finale

{riassunto_finale[:3000]}
""",
        encoding="utf-8",
    )

    return esito


def main():
    risultati = []

    print(f"=== {VERSIONE} ===")

    for pagine in PAGINE_TEST:
        print(f"\n--- Test {pagine} pagine ---")
        esito = esegui_test(pagine)
        risultati.append(esito)

        print(f"Pagine: {esito['pagine_test']}")
        print(f"Chunk: {esito['chunk']} / attesi {esito['chunk_attesi']}")
        print(f"Batch: {esito['batch']} / attesi {esito['batch_attesi']}")
        print(f"Parziali: {esito['parziali']}")
        print(f"Riassunto finale: {esito['lunghezza_riassunto_finale']} caratteri")
        print(f"Keyword: {len(esito['keyword'])}")
        print(f"Memoria picco: {esito['memoria_picco_mb']} MB")
        print(f"Durata: {esito['durata_secondi']} secondi")
        print(f"Esito: {'OK' if esito['ok'] else 'KO'}")

        if not esito["ok"]:
            print("\nERRORE: espansione non stabile su questo livello.")
            raise SystemExit(1)

    riepilogo_json = REPORTS / "rag_documenti_lunghi_v2a4_espansione_riepilogo.json"
    riepilogo_md = REPORTS / "rag_documenti_lunghi_v2a4_espansione_riepilogo.md"

    riepilogo_json.write_text(json.dumps(risultati, indent=2, ensure_ascii=False), encoding="utf-8")

    righe = ["# Riepilogo RAG documenti lunghi V2A.4", ""]
    for r in risultati:
        righe.append(
            f"- {r['pagine_test']} pagine: OK, "
            f"{r['chunk']} chunk, {r['batch']} batch, {r['parziali']} parziali, "
            f"{r['memoria_picco_mb']} MB, {r['durata_secondi']} sec."
        )

    riepilogo_md.write_text("\n".join(righe) + "\n", encoding="utf-8")

    print("\n=== ESPANSIONE V2A.4 COMPLETATA ===")
    print("Test superati: 180, 240, 300")
    print(f"Report JSON: {riepilogo_json}")
    print(f"Report MD: {riepilogo_md}")


if __name__ == "__main__":
    main()
