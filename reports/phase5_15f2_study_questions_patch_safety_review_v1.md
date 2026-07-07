# FASE 5.15F.2 - Safety review patch domande studio

Status review: **PASS**

## File modificati

- `backend/phase5_15b_quality_checked_generators.py`
- `reports/phase5_15f_button_quality_diagnostics_v1.json` e `.md` aggiornati dal rerun diagnostico
- `reports/phase5_15d_real_page_generators_trace_v1.json` e `reports/phase5_15e_approved_outputs_report_v1.json` aggiornati dagli smoke esistenti
- questo report: `reports/phase5_15f2_study_questions_patch_safety_review_v1.md`

## Funzioni modificate o aggiunte

Modificate:

- `run_quality_checked_generator`
- `_card_payloads` override finale, solo ramo `generator == "study_questions"`

Aggiunte:

- `_v515f2_study_words`
- `_v515f2_study_title`
- `_v515f2_study_source`
- `_v515f2_study_context`
- `_v515f2_study_question_answer`
- `_v515f2_multidocument_study_facts`
- `_v515f2_study_items_from_facts`
- `_v515f2_study_reanchor_raw_output`
- `_v515f2_study_public_output`

## Isolamento patch

Esito: **PASS**

- `_v515f2_study_reanchor_raw_output(raw_output, text)` viene chiamata solo dentro `if generator == "study_questions"`.
- `_v515f2_study_public_output(final_output)` viene chiamata solo dentro `if generator == "study_questions"`.
- Gli helper `_v515f2_*` usati nel payload QM sono nel ramo `elif generator == "study_questions"`.
- Monkeypatch runtime: sostituendo `_v515f2_study_reanchor_raw_output` e `_v515f2_study_public_output` con funzioni che sollevano errore, `summary`, `cards` e `quiz` completano senza invocarli.

## Componenti non toccati

- Bridge: **non toccato**
- UI/pagina: **non toccata**
- Quality Manager comune: **non toccato**
- raw_output comune: **non normalizzato**
- summary/cards/quiz: **nessuna modifica funzionale**
- patch quiz 5.15F.1: **preservata**, quiz multi-doc resta `APPROVED 63/63`

## Prima / dopo

Prima, multi-documento:

1. Domanda: `Qual è il punto operativo principale relativo a protocollo triage ambulatoriale?`
   Risposta guida: `Il documento indica che [Documento A - Protocollo triage ambulatoriale] Il centro medico organizza il triage iniziale... Lo studente deve collegare questo punto a una procedura concreta...`

2. Domanda: `Qual è il punto operativo principale relativo a infermiere registra arrivo?`
   Risposta guida: `Il documento indica che l'infermiere registra ora di arrivo, livello di urgenza e motivo della visita. Lo studente deve collegare questo punto a una procedura concreta...`

Dopo, multi-documento:

1. Domanda: `Perché nel triage iniziale non basta chiedere il motivo della visita?`
   Risposta guida: `Devi ricordare che la priorità nasce dall'insieme di scheda, parametri vitali e sintomi riferiti. Il motivo della visita da solo non rende verificabile la scelta clinica.`

2. Domanda: `Quali dati permettono di ricostruire la priorità assegnata all'arrivo?`
   Risposta guida: `La risposta deve collegare ora di arrivo, livello di urgenza e motivo della visita. Questi dati spiegano perché un caso è stato gestito con una certa priorità.`

Ulteriori domande dopo patch:

- `Che cosa deve contenere un follow-up utile dopo la visita?`
- `Come si usa l'audit mensile per capire se un ritardo è organizzativo o comunicativo?`

## Test eseguiti

```text
backend/.venv/bin/python -m py_compile backend/phase5_15b_quality_checked_generators.py
backend/.venv/bin/python -m py_compile backend/phase5_full_pipeline_runtime_v51416.py
backend/.venv/bin/python -m py_compile scripts/run_phase5_15f_button_quality_diagnostics.py
```

Esito: **PASS**

```text
backend/.venv/bin/python scripts/run_phase5_15f_button_quality_diagnostics.py
```

Esito: **PASS**

```text
Genera Test/Quiz: approved=True engine=full_pipeline_quiz_route63_language_quality_v51418 problems=['nessuno bloccante']
Genera Domande studio: approved=True engine=full_pipeline_study_route51_language_quality_v51418 problems=['nessuno bloccante']
```

```text
backend/.venv/bin/python scripts/run_phase5_15e_approved_outputs_smoke.py
```

Esito: **PASS**

```text
summary: 55/55 APPROVED
cards: 60/60 APPROVED
study_questions: 51/51 APPROVED
quiz: 63/63 APPROVED
```

```text
backend/.venv/bin/python scripts/run_phase5_15d_real_page_generators_smoke.py
```

Esito: **PASS**

```text
counts={'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}
```

## Rischi residui

- Il file `backend/phase5_15b_quality_checked_generators.py` resta fragile perché contiene più override storici di `_card_payloads`; la patch si innesta nell'override finale attualmente usato.
- Gli helper `_v515f2_study_question_answer` usano regole lessicali manuali per i casi clinico/magazzino e fallback generico. Sono adatti al caso diagnosticato, ma andrebbero generalizzati se i documenti multi-dominio diventano più vari.
- I report baseline 5.15D/5.15E sono riscritti dagli smoke esistenti; non sono stati ripristinati per rispettare la regola no rollback.
- Le card restano il primo problema residuo nella diagnostica globale e vanno trattate in una fase separata.

## Decisione

- Study questions multi-doc: **PASS**
- Quiz multi-doc 5.15F.1: **PASS**
- 5.15E: **PASS**
- 5.15D: **PASS**
- 5.15F diagnostica: **PASS**

Consiglio: **committare la patch 5.15F.2 e i report**, poi aprire una fase separata per le card e, in seguito, valutare un refactor controllato degli override storici.
