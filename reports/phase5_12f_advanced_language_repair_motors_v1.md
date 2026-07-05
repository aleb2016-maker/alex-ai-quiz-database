# Fase 5.12F — Advanced Language / Repair Motors V1

- Status: **PASS**
- Approved: `True`
- Ready label: `ADVANCED_LANGUAGE_REPAIR_MOTORS_V512F_READY`
- Generated at: `2026-07-05T16:22:06.072212+00:00`
- Motori ricostruiti: `4`
- Targeted tests passed: `4/4`
- Good case passed: `True`

## Motori ricostruiti

- `qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword` — **Naturalezza linguistica anti-keyword**
  - Type: `validator_repair_suggester`
  - Severity: `blocking`

- `qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi` — **Accordo grammaticale e pronomi**
  - Type: `validator`
  - Severity: `blocking`

- `qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_` — **Repair contestuale frasi non finite usando contesto tema sottotema categorie e sottocategorie**
  - Type: `validator_repair_suggester`
  - Severity: `blocking`

- `qm_064_repair_ortografico_correzione_parole_con_lettere_invertite` — **Repair ortografico parole con lettere invertite**
  - Type: `validator_repair_suggester`
  - Severity: `blocking`

## Targeted tests

- `case_061` — `qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword`
  - Passed: `True`
  - Blocking hits: `1`
  - Repair hits: `0`

- `case_062` — `qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi`
  - Passed: `True`
  - Blocking hits: `2`
  - Repair hits: `0`

- `case_063` — `qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_`
  - Passed: `True`
  - Blocking hits: `2`
  - Repair hits: `2`

- `case_064` — `qm_064_repair_ortografico_correzione_parole_con_lettere_invertite`
  - Passed: `True`
  - Blocking hits: `1`
  - Repair hits: `1`

## Good case

- Passed: `True`
- Blocking issues: `0`
- Warning issues: `0`

## Scope guard

- ui_pdf_css_app_touched: `False`
- pipeline_5_11_changed: `False`
- existing_55_motors_changed: `False`
- standalone_first: `True`
- no_fallback: `True`
- no_demo_output: `True`
- repair_suggestions_only: `True`

## Nota tecnica

Questi motori sono controlli linguistici avanzati universali. Producono anche suggerimenti di repair, ma non modificano automaticamente la pipeline 5.11.
