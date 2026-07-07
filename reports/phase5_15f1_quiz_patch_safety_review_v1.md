# FASE 5.15F.1.1 - Review sicurezza patch quiz

Status review: **PASS**

## Scopo

Verificare che la patch 5.15F.1 sul quiz sia isolata al percorso `quiz` e non introduca regressioni su `summary`, `cards`, `study_questions`, bridge, UI, Quality Manager o raw output comune.

## Diff esaminato

- File esaminato: `backend/phase5_15b_quality_checked_generators.py`
- Nuovo import: `hashlib`, usato per costruire `answer_check.answer_ok_hash`.
- Hook quiz-only in `run_quality_checked_generator`:
  - `_v515f1_quiz_reanchor_raw_output(raw_output, text)` chiamato solo dentro `if generator == "quiz"`.
  - `_v515f1_quiz_public_output(final_output)` chiamato solo dentro `if generator == "quiz"`.
- Arricchimento payload QM in `_card_payloads`:
  - gli helper `_v515f1_quiz_title`, `_v515f1_quiz_source`, `_v515f1_quiz_context`, `_v515f1_quiz_words` sono usati nel ramo `if generator == "quiz"`.

## Verifica isolamento

Esito: **PASS**

- Ricerca call site `_v515f1_*`: nessun hook operativo verso re-anchor o public sanitizer fuori dal quiz.
- Monkeypatch runtime:
  - `_v515f1_quiz_reanchor_raw_output` e `_v515f1_quiz_public_output` sostituiti con funzioni che sollevano errore.
  - `summary`, `cards`, `study_questions` completano senza invocare tali helper.
- Conclusione: `summary`, `cards`, `study_questions` non passano da `_v515f1_quiz_reanchor_raw_output` o `_v515f1_quiz_public_output`.

## Verifica payload pubblico quiz

Esito: **PASS**

Payload pubblico quiz multi-documento:

- status: `APPROVED`
- approved: `True`
- QM: `63/63`
- defects: `[]`
- chiavi vietate trovate ricorsivamente: `[]`
- `answer_check` presente e usabile su 4/4 domande

Campi non esposti nel payload pubblico:

- `is_correct`
- `correct_option_id`
- `risposta_corretta`
- `answer`

## Test eseguiti

```text
backend/.venv/bin/python -m py_compile backend/phase5_15b_quality_checked_generators.py
```

Esito: **PASS**

```text
backend/.venv/bin/python scripts/run_phase5_15e_approved_outputs_smoke.py
```

Esito: **PASS**

```text
FASE 5.15E approved smoke: status=PASS
- summary: status=APPROVED approved=True qm=55/55 defects=0
- cards: status=APPROVED approved=True qm=60/60 defects=0
- study_questions: status=APPROVED approved=True qm=51/51 defects=0
- quiz: status=APPROVED approved=True qm=63/63 defects=0
```

```text
backend/.venv/bin/python scripts/run_phase5_15d_real_page_generators_smoke.py
```

Esito: **PASS**

```text
FASE 5.15D smoke: status=PASS counts={'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}
```

```text
backend/.venv/bin/python scripts/run_phase5_15f_button_quality_diagnostics.py
```

Esito: **PASS**

```text
Genera Test/Quiz: approved=True engine=full_pipeline_quiz_route63_language_quality_v51418 problems=['nessuno bloccante']
```

## Rischi residui

- Il file `backend/phase5_15b_quality_checked_generators.py` contiene più override storici di `_card_payloads`; la patch si innesta nell'override finale. Funziona ora, ma il file resta fragile per manutenzione futura.
- Gli helper `_v515f1_quiz_question_and_distractors` usano regole lessicali/manuali per scenari clinici e fallback generico. Sono sicuri rispetto al caso diagnosticato, ma andranno generalizzati se i documenti multi-dominio diventano più vari.
- I report baseline 5.15D/5.15E vengono riscritti dagli smoke; questa review non li ripristina per rispetto della regola no rollback.
- Restano fuori scope i problemi diagnostici non quiz: card e study_questions risultano ancora da migliorare in fasi successive.

## Decisione

- Patch quiz isolata: **sì**
- Summary/cards/study_questions intatti rispetto agli hook quiz: **sì**
- Payload quiz pubblico senza leak: **sì**
- `answer_check` presente/usabile: **sì**
- 5.15E: **PASS**
- 5.15D: **PASS**
- 5.15F diagnostica: **PASS**

Consiglio: **committare la patch quiz e il report diagnostico/review**, lasciando a una fase separata il refactor di mantenibilità degli override storici e il miglioramento di `study_questions`.
