# FASE 5.15F.4 - Safety review patch summary multi-documento

Status review: **PASS**

## Scopo

Patch mirata sul pulsante **Genera Riassunto** per migliorare profondita e copertura RAG del caso multi-documento, senza toccare bridge, UI, Quality Manager comune, raw_output comune o altri generatori.

## File modificati

- `backend/phase5_full_pipeline_runtime_v51416.py`
- `reports/phase5_15f_button_quality_diagnostics_v1.json` aggiornato dalla diagnostica richiesta
- `reports/phase5_15f_button_quality_diagnostics_v1.md` aggiornato dalla diagnostica richiesta
- `reports/phase5_15e_approved_outputs_report_v1.json` aggiornato dallo smoke richiesto
- `reports/phase5_15f4_summary_depth_patch_safety_review_v1.md`

## Funzioni aggiunte o modificate

- Aggiunte: `_v515f4_word_count`
- Aggiunte: `_v515f4_document_blocks`
- Aggiunte: `_v515f4_select_document_facts`
- Aggiunte: `_v515f4_fact_chain`
- Aggiunte: `_v515f4_summary_depth_metrics`
- Aggiunte: `_v515f4_build_multidocument_summary`
- Modificata: `run_summary_pipeline`

## Isolamento patch

- La patch entra solo in `run_summary_pipeline`.
- Il ramo nuovo viene attivato solo se `_v515f4_document_blocks` trova almeno due blocchi con intestazione `[Documento ...]`.
- Se il testo non e multi-documento, `run_summary_pipeline` continua a usare il comportamento precedente.
- Nessuna modifica a `backend/phase5_15b_quality_checked_generators.py`.
- Nessuna modifica a bridge, UI/pagina, QM comune, raw_output comune.
- Nessuna modifica ai generatori `cards`, `quiz`, `study_questions`.

## Prima della patch

Il summary multi-doc era tecnicamente approvato, ma la diagnostica rilevava:

- `warnings`: `riassunto_non_copre_abbastanza_sezioni`
- `problemi_rag_osservati`: `riassunto non abbastanza profondo`
- termini attesi coperti: `4/6`
- termini mancanti: `referti`, `audit`

Metriche prima:

| Metrica | Valore |
| --- | ---: |
| parole input | 172 |
| caratteri input | 1195 |
| parole summary | 209 |
| caratteri summary | 1469 |
| ratio parole summary/input | 1.215 |
| ratio caratteri summary/input | 1.229 |
| regola 10% | PASS |
| copertura termini attesi | 4/6 |

Estratto prima:

> Il documento spiega che [Documento A - Protocollo triage ambulatoriale]. In apertura chiarisce anche che il centro medico organizza il triage iniziale con una scheda di priorita, un controllo dei parametri vitali e una verifica dei sintomi riferiti dal paziente. [...] La parte conclusiva rafforza gli elementi di verifica e continuita: Ogni mese il coordinatore confronta tempi di attesa, rivalutazioni mancate e reclami dei pazienti.

## Dopo la patch

Il summary multi-doc ora mantiene separati i documenti e include riferimenti concreti a triage, follow-up, fascicolo, referti, audit e rivalutazioni.

Metriche dopo:

| Metrica | Valore |
| --- | ---: |
| parole input | 172 |
| caratteri input | 1193 |
| parole summary | 235 |
| caratteri summary | 1703 |
| ratio parole summary/input | 1.366 |
| ratio caratteri summary/input | 1.427 |
| parole minime regola 10% | 17 |
| regola 10% | PASS |
| documenti rilevati | 3 |
| documenti coperti | 3 |
| copertura documenti | 1.0 |
| termini attesi coperti | 6/6 |

Estratto dopo:

> Il materiale collega Protocollo triage ambulatoriale, Continuita assistenziale e Audit qualita in un percorso operativo unico. Il riassunto distingue i documenti per conservare contesto, responsabilita e passaggi verificabili. [...] Sul versante di Continuita assistenziale, dopo la visita, il medico consegna un piano di follow-up con terapia, segnali di allarme e canale di contatto. Inoltre, le informazioni essenziali vengono riportate nel fascicolo clinico [...] responsabilita del controllo referti. [...] Per Audit qualita, ogni mese il coordinatore confronta tempi di attesa, rivalutazioni mancate e reclami dei pazienti.

## Esiti test

| Controllo | Esito |
| --- | --- |
| `python -m py_compile backend/phase5_15b_quality_checked_generators.py` | PASS |
| `python -m py_compile backend/phase5_full_pipeline_runtime_v51416.py` | PASS |
| `python -m py_compile scripts/run_phase5_15f_button_quality_diagnostics.py` | PASS |
| `python scripts/run_phase5_15f_button_quality_diagnostics.py` | PASS |
| `python scripts/run_phase5_15e_approved_outputs_smoke.py` | PASS |
| `python scripts/run_phase5_15d_real_page_generators_smoke.py` | PASS |

## Esiti generatori multi-documento

| Generatore | Esito multi-doc | Note |
| --- | --- | --- |
| `summary` | PASS | nessun warning, nessun problema RAG, 55/55 QM |
| `cards` | PASS | nessun warning sul caso multi-doc, 60/60 QM |
| `study_questions` | PASS | nessun warning sul caso multi-doc, 51/51 QM |
| `quiz` | PASS | nessun warning sul caso multi-doc, 63/63 QM |

## Esiti baseline

| Baseline | Esito | Conteggi |
| --- | --- | --- |
| 5.15E | PASS | summary 55/55, cards 60/60, study_questions 51/51, quiz 63/63 |
| 5.15D | PASS | summary 55/55, cards 60/60, study_questions 51/51, quiz 63/63 |
| 5.15F diagnostica | PASS | summary/cards/study/quiz approved |

## Rischi residui

- La patch copre il formato multi-documento esplicito con intestazioni `[Documento ...]`; testi multi-doc senza questa struttura continueranno a usare il summary precedente.
- Per piu di quattro documenti, il summary seleziona al massimo i primi quattro blocchi per evitare output troppo lunghi.
- La diagnostica aggregata segnala ancora `ripetizioni` sulle card per il caso single-document legacy; il caso cards multi-doc resta PASS.

## Raccomandazione

La patch e isolata e verificata. Consiglio: **committare la Fase 5.15F.4** se si accetta che il supporto multi-doc del summary sia legato al formato `[Documento ...]`. Nessuna ulteriore patch necessaria sul summary per il caso diagnostico F.4.
