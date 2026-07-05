# Fase 5.12D — Card Summary Source Quality Motors V1

- Status: **PASS**
- Ready label: `CARD_SUMMARY_SOURCE_QUALITY_MOTORS_V512D_READY`
- Generated at: `2026-07-05T15:52:43.787733+00:00`
- Motori Card/Riassunto/Fonti ricostruiti: `10`
- Targeted tests passed: `10/10`
- Good case passed: `True`

## Motori ricostruiti

- `qm_023_card_riassunto_fonti_card_scritte_bene` — **Card scritte bene**
  - Type: `validator`
  - Severity: `blocking`

- `qm_024_card_riassunto_fonti_card_non_troppo_corte` — **Card non troppo corte**
  - Type: `validator`
  - Severity: `blocking`

- `qm_025_card_riassunto_fonti_card_non_troppo_compresse` — **Card non troppo compresse**
  - Type: `validator`
  - Severity: `blocking`

- `qm_026_card_riassunto_fonti_messaggio_chiave_completo` — **Messaggio chiave completo**
  - Type: `validator`
  - Severity: `blocking`

- `qm_027_card_riassunto_fonti_riassunto_chiaro` — **Riassunto chiaro**
  - Type: `validator`
  - Severity: `blocking`

- `qm_028_card_riassunto_fonti_punti_chiave_leggibili` — **Punti chiave leggibili**
  - Type: `validator`
  - Severity: `blocking`

- `qm_029_card_riassunto_fonti_fonti_visibili_belle` — **Fonti visibili belle**
  - Type: `validator`
  - Severity: `blocking`

- `qm_030_card_riassunto_fonti_fonti_coerenti` — **Fonti coerenti**
  - Type: `validator`
  - Severity: `blocking`

- `qm_031_card_riassunto_fonti_niente_fonti_brutte` — **Niente fonti brutte**
  - Type: `validator`
  - Severity: `blocking`

- `qm_032_card_riassunto_fonti_layout_grafico_controllato` — **Layout grafico controllato**
  - Type: `validator`
  - Severity: `blocking`

## Targeted tests

- `case_023` — `qm_023_card_riassunto_fonti_card_scritte_bene`
  - Passed: `True`
  - Blocking hits: `2`

- `case_024` — `qm_024_card_riassunto_fonti_card_non_troppo_corte`
  - Passed: `True`
  - Blocking hits: `1`

- `case_025` — `qm_025_card_riassunto_fonti_card_non_troppo_compresse`
  - Passed: `True`
  - Blocking hits: `2`

- `case_026` — `qm_026_card_riassunto_fonti_messaggio_chiave_completo`
  - Passed: `True`
  - Blocking hits: `1`

- `case_027` — `qm_027_card_riassunto_fonti_riassunto_chiaro`
  - Passed: `True`
  - Blocking hits: `3`

- `case_028` — `qm_028_card_riassunto_fonti_punti_chiave_leggibili`
  - Passed: `True`
  - Blocking hits: `4`

- `case_029` — `qm_029_card_riassunto_fonti_fonti_visibili_belle`
  - Passed: `True`
  - Blocking hits: `2`

- `case_030` — `qm_030_card_riassunto_fonti_fonti_coerenti`
  - Passed: `True`
  - Blocking hits: `1`

- `case_031` — `qm_031_card_riassunto_fonti_niente_fonti_brutte`
  - Passed: `True`
  - Blocking hits: `1`

- `case_032` — `qm_032_card_riassunto_fonti_layout_grafico_controllato`
  - Passed: `True`
  - Blocking hits: `1`

## Good case

- Passed: `True`
- Blocking issues: `0`
- Warning issues: `0`

## Scope guard

- ui_pdf_css_app_touched: `False`
- pipeline_5_11_changed: `False`
- existing_33_motors_changed: `False`
- standalone_first: `True`
- no_fallback: `True`
- no_demo_output: `True`
- layout_check_is_data_structure_only: `True`

## Nota tecnica

Questi motori sono ricostruiti come controlli Card/Riassunto/Fonti universali. Non sono ancora collegati al registry da 33 motori. Il controllo layout è solo su dati e struttura della card, non su CSS/UI/PDF.
