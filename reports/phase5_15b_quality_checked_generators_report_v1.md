# FASE 5.15B - Quality checked generators

Status: **PARTIAL**

## Entry point

- File: `backend/phase5_15b_quality_checked_generators.py`
- Funzione: `run_quality_checked_generator(generator_name, input_text)`
- Regola: `all_motors_connected=True` viene emesso solo se esiste `qm_runtime_trace` reale.

## Copertura generatori

- Generatori passati dall'entrypoint unico: 4/4
- Generatori con trace QM reale: 4/4
- Riassunto: 55 QM eseguiti
- Card: 60 QM eseguiti
- Domande studio: 15 QM eseguiti
- Test / Quiz: 24 QM eseguiti

## QM non applicabili

- Riassunto: `qm_013`, `qm_014`, `qm_015`, `qm_016`, `qm_021`, `qm_022`, `qm_036`, `qm_037`, `qm_041`
- Card: `qm_016`, `qm_036`, `qm_037`, `qm_041`
- Domande studio: `qm_001`, `qm_002`, `qm_003`, `qm_004`, `qm_005`, `qm_006`, `qm_007`, `qm_008`, `qm_009`, `qm_010`, `qm_011`, `qm_012`, `qm_016`, `qm_019`, `qm_020`, `qm_023`, `qm_024`, `qm_025`, `qm_026`, `qm_027`, `qm_028`, `qm_029`, `qm_030`, `qm_031`, `qm_032`, `qm_033`, `qm_034`, `qm_035`, `qm_036`, `qm_037`, `qm_038`, `qm_039`, `qm_040`, `qm_041`, `qm_042`, `qm_043`, `qm_044`, `qm_045`, `qm_046`, `qm_047`, `qm_049`, `qm_050`, `qm_052`, `qm_053`, `qm_055`, `qm_061`, `qm_062`, `qm_063`, `qm_064`
- Test / Quiz: `qm_001`, `qm_002`, `qm_003`, `qm_004`, `qm_005`, `qm_006`, `qm_007`, `qm_008`, `qm_009`, `qm_010`, `qm_011`, `qm_012`, `qm_013`, `qm_014`, `qm_015`, `qm_018`, `qm_019`, `qm_020`, `qm_023`, `qm_024`, `qm_025`, `qm_026`, `qm_027`, `qm_028`, `qm_029`, `qm_030`, `qm_031`, `qm_032`, `qm_045`, `qm_046`, `qm_047`, `qm_049`, `qm_050`, `qm_052`, `qm_053`, `qm_054`, `qm_061`, `qm_062`, `qm_063`, `qm_064`

## Bypass rimasti

- La UI non e' stata modificata in questa fase: deve ancora essere instradata esplicitamente verso l'entrypoint 5.15B.
- Il quality_report interno dei generatori precedenti puo' ancora dichiarare all_motors_connected=True; l'entrypoint 5.15B lo rende valido solo con qm_runtime_trace reale.
- Il quiz answer leak non e' stato corretto per richiesta esplicita.
- I 9 slot gia' segnalati in 5.15A restano da materializzare/chiarire fuori da questa fase.

## Problemi rimasti

- Portare i pulsanti/UI o il bridge HTTP a chiamare questo entrypoint unico.
- Correggere in una fase dedicata il leak della risposta nel quiz.
- Decidere se i QM non applicabili a study/quiz debbano avere route dedicate anziche' essere dichiarati NOT_APPLICABLE.

## Casi eseguiti

- breve_valido / summary: status=QUALITY_BLOCKED, approved=False, qm=55, raw_output_present=True
- breve_valido / cards: status=QUALITY_BLOCKED, approved=False, qm=60, raw_output_present=True
- breve_valido / study_questions: status=QUALITY_BLOCKED, approved=False, qm=15, raw_output_present=True
- breve_valido / quiz: status=QUALITY_BLOCKED, approved=False, qm=24, raw_output_present=True
- tecnico / summary: status=QUALITY_BLOCKED, approved=False, qm=55, raw_output_present=True
- tecnico / cards: status=QUALITY_BLOCKED, approved=False, qm=60, raw_output_present=True
- tecnico / study_questions: status=QUALITY_BLOCKED, approved=False, qm=15, raw_output_present=True
- tecnico / quiz: status=QUALITY_BLOCKED, approved=False, qm=24, raw_output_present=True
- narrativo_discorsivo / summary: status=QUALITY_BLOCKED, approved=False, qm=55, raw_output_present=True
- narrativo_discorsivo / cards: status=QUALITY_BLOCKED, approved=False, qm=60, raw_output_present=True
- narrativo_discorsivo / study_questions: status=QUALITY_BLOCKED, approved=False, qm=15, raw_output_present=True
- narrativo_discorsivo / quiz: status=QUALITY_BLOCKED, approved=False, qm=24, raw_output_present=True
