# Fase 5.12G — Contextual Duplicate Motors V1

- Status: **PASS**
- Approved: `True`
- Ready label: `CONTEXTUAL_DUPLICATE_MOTORS_V512G_READY`
- Generated at: `2026-07-05T16:39:12.443256+00:00`
- Motori ricostruiti: `6`
- Targeted tests passed: `6/6`
- Good case passed: `True`

## Motori ricostruiti

- `qm_045_duplicati_contestuali_duplicati_esatti` — **Duplicati contestuali: duplicati esatti**
  - Type: `validator`
  - Severity: `blocking`

- `qm_046_duplicati_contestuali_quasi_duplicati` — **Duplicati contestuali: quasi duplicati**
  - Type: `validator`
  - Severity: `blocking`

- `qm_047_duplicati_contestuali_ripetizioni_inutili` — **Duplicati contestuali: ripetizioni inutili**
  - Type: `validator`
  - Severity: `blocking`

- `qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande` — **Duplicati contestuali: ripetizioni meccaniche tra domande**
  - Type: `validator`
  - Severity: `blocking`

- `qm_049_duplicati_contestuali_frasi_troppo_simili` — **Duplicati contestuali: frasi troppo simili**
  - Type: `validator`
  - Severity: `blocking`

- `qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo` — **Duplicati contestuali: stesso contenuto ripetuto senza motivo**
  - Type: `validator`
  - Severity: `blocking`

## Targeted tests

- `case_045` — `qm_045_duplicati_contestuali_duplicati_esatti`
  - Passed: `True`
  - Blocking hits: `1`

- `case_046` — `qm_046_duplicati_contestuali_quasi_duplicati`
  - Passed: `True`
  - Blocking hits: `1`

- `case_047` — `qm_047_duplicati_contestuali_ripetizioni_inutili`
  - Passed: `True`
  - Blocking hits: `1`

- `case_048` — `qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande`
  - Passed: `True`
  - Blocking hits: `3`

- `case_049` — `qm_049_duplicati_contestuali_frasi_troppo_simili`
  - Passed: `True`
  - Blocking hits: `1`

- `case_050` — `qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo`
  - Passed: `True`
  - Blocking hits: `3`

## Good case

- Passed: `True`
- Blocking issues: `0`
- Warning issues: `0`

## Scope guard

- ui_pdf_css_app_touched: `False`
- pipeline_5_11_changed: `False`
- existing_59_motors_changed: `False`
- standalone_first: `True`
- contextual_not_global: `True`
- allows_same_concept_with_different_function: `True`
- no_fallback: `True`
- no_demo_output: `True`

## Regola duplicati contestuali

Il controllo non boccia lo stesso concetto quando appare in sezioni diverse con funzioni diverse. Blocca solo duplicati meccanici, inutili o senza motivo.
