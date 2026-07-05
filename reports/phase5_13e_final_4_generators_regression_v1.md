# FASE 5.13E — REGRESSIONE AGGREGATA FINALE 4 GENERATORI

Status: `PASS - Fase 5.13E: FINAL_4_GENERATORS_REGRESSION_READY`

## Generatori

| Generatore | Status | Evidenze | Defects | Warnings |
|---|---|---:|---:|---:|
| Card | `PASS` | 2 | 0 | 0 |
| Riassunto | `PASS` | 8 | 0 | 0 |
| Domande studio | `PASS` | 1 | 0 | 0 |
| Test/Quiz | `PASS` | 1 | 0 | 0 |

## Comandi eseguiti

- `5.13C.1 Study Questions 51 connector` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 scripts/run_phase5_13c1_study_questions_real_connector.py`
- `5.13C.2 Study Questions final quality` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 scripts/run_phase5_13c2_study_questions_final_quality_gate.py`
- `5.13D.0.1 Test/Quiz route 63` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 scripts/run_phase5_13d01_test_quiz_route_materializer.py`
- `5.13D.1 Test/Quiz 63 connector` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 scripts/run_phase5_13d1_test_quiz_63_real_connector.py`
- `Real study quiz test` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 backend/test_phase5_study_quiz_v1.py`
- `5.13D.2 Test/Quiz final quality` → returncode `0`
  - comando: `/Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/python3 scripts/run_phase5_13d2_test_quiz_final_quality_gate.py`

## Evidenze

### Card
- `reports/phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json`
- `reports/phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.md`
### Riassunto
- `reports/audit_effetti_premi_ai_its.md`
- `reports/legacy_quality_motor_candidates_v1.json`
- `reports/legacy_quality_motor_candidates_v1.md`
- `reports/legacy_quality_motor_shortlist_v1.json`
- `reports/legacy_quality_motor_shortlist_v1.md`
- `reports/legacy_quality_motor_version_families_v1.json`
- `reports/motori_qualita_esistenti_v1.json`
- `reports/phase5_12a1_motori_salvabili_strict_v1.json`
### Domande studio
- `reports/phase5_13c2_study_questions_final_quality_gate_v1.json`
### Test/Quiz
- `reports/phase5_13d2_test_quiz_final_quality_gate_v1.json`

## Defects

- Nessuno

## Warnings

- Nessuno

## Note

- Questa regressione non modifica UI/PDF/app.
- Card e Riassunto vengono verificati tramite evidenze/report già salvati.
- Domande studio e Test/Quiz vengono verificati con runner reali e test reale.
- Il checkpoint va committato solo se status finale PASS e working tree è controllato.
