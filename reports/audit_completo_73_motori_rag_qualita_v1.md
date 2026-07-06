# Audit completo 73 motori RAG qualità V1

## 1. Stato generale del progetto

- Motori/slot mappati: **73**
- Motori QM spiegati nel catalogo ufficiale: **64**
- Registry totale dichiarato: **73**
- Collegati dedotti da route/report: **64**
- Non collegati o da verificare: **9**
- Smoke test: **23 PASS / 13 FAIL**

Verdetto: **PARZIALE**. Il progetto ha generatori e validatori reali, ma il claim dei 73 motori non è dimostrato come esecuzione runtime unica. Il catalogo ufficiale parla di 64 QM spiegati e 73 elementi di registry/orchestrazione.

## 2. Mappa completa dei 73 motori

| Numero | Nome motore | File | Funzione/classe principale | Tipo motore | Collegato? | A cosa è collegato | Stato | Note |
|---:|---|---|---|---|---|---|---|---|
| 1 | qm_001 - Grammatica italiana corretta | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 2 | qm_002 - Accenti corretti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 3 | qm_003 - Apostrofi corretti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 4 | qm_004 - Punteggiatura corretta | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 5 | qm_005 - Spazi corretti prima/dopo punteggiatura | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 6 | qm_006 - Frasi complete | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 7 | qm_007 - Assenza di frasi spezzate | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | anti-frasi spezzate | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 8 | qm_008 - Assenza di frasi non terminate | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 9 | qm_009 - Assenza di finali sospetti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 10 | qm_010 - Assenza di frasi riempitive | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 11 | qm_011 - Assenza di testo generico | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | anti-generico | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 12 | qm_012 - Assenza di vecchi fallback/demo/test | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | anti-fallback | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 13 | qm_013 - Domande studio naturali | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione domande studio | sì | Card, Domande studio | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 14 | qm_014 - Domande studio utili per ripassare | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione domande studio | sì | Card, Domande studio | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 15 | qm_015 - Risposte guida specifiche | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Card, Domande studio | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 16 | qm_016 - Spiegazioni test chiare | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 17 | qm_017 - Spiegazioni non troppo corte | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 18 | qm_018 - Tono didattico finale | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Riassunto, Card, Domande studio | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 19 | qm_019 - Categorie presenti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 20 | qm_020 - Sottocategorie presenti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 21 | qm_021 - Coerenza tra domanda, risposta e contenuto | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 22 | qm_022 - Niente risposte vaghe | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità didattica | sì | Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 23 | qm_023 - Card scritte bene | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 24 | qm_024 - Card non troppo corte | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 25 | qm_025 - Card non troppo compresse | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 26 | qm_026 - Messaggio chiave completo | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 27 | qm_027 - Riassunto chiaro | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 28 | qm_028 - Punti chiave leggibili | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 29 | qm_029 - Fonti visibili belle | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 30 | qm_030 - Fonti coerenti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 31 | qm_031 - Niente fonti brutte | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 32 | qm_032 - Layout grafico controllato | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 33 | qm_033 - Test separato da card/riassunto/domande studio | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 34 | qm_034 - Opzioni interne validate | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 35 | qm_035 - Opzioni visibili pulite | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 36 | qm_036 - Risposta corretta interna | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 37 | qm_037 - Risposta corretta visibile | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 38 | qm_038 - Mappa sicura tra risposta interna e visibile | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 39 | qm_039 - 4 opzioni per domanda | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 40 | qm_040 - Risposta corretta presente tra le opzioni | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 41 | qm_041 - Distrattori forti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 42 | qm_042 - Niente opzioni duplicate nella stessa domanda | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 43 | qm_043 - Niente ripetizioni globali eccessive | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 44 | qm_044 - Compatibilità obbligatoria col bridge motori quiz V3.5B | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 45 | qm_045 - Duplicati esatti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 46 | qm_046 - Quasi duplicati | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 47 | qm_047 - Ripetizioni inutili | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 48 | qm_048 - Ripetizioni meccaniche tra domande | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 49 | qm_049 - Frasi troppo simili | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 50 | qm_050 - Stesso contenuto ripetuto senza motivo | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 51 | qm_051 - Il compito richiesto deve selezionare i motori giusti | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 52 | qm_052 - Riassunto → motore didattico | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione riassunto | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 53 | qm_053 - Card → motore didattico + layout | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione card | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 54 | qm_054 - Domande studio → motore didattico | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione domande studio | sì | Riassunto, Card, Domande studio | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 55 | qm_055 - Test → bridge quiz + motore test + bridge quiz | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 56 | qm_056 - Completo/PDF/app/web → orchestratore | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 57 | qm_057 - Niente motori inutili | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 58 | qm_058 - Niente output non richiesto | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 59 | qm_059 - Output finale pronto per UI/PDF/app | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 60 | qm_060 - Report qualità sempre leggibile | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | orchestratore | sì | Riassunto, Card, Domande studio, Test/Quiz | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 61 | qm_061 - Naturalezza linguistica anti-keyword | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 62 | qm_062 - Accordo grammaticale e pronomi | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità grammaticale | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 63 | qm_063 - Correzione frasi non finite con contesto | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | validazione quiz | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 64 | qm_064 - Correzione parole scritte male con lettere invertite | reports/phase5_12i2_official_quality_motor_catalog_v1.json | catalog entry / executor se presente | qualità semantica | sì | Riassunto, Card | PARZIALE | Nel catalogo ufficiale; ha executor in connettori/report backend; collegamento finale dedotto da route/quality_report, non da invocazione registry unica. |
| 65 | registry_orchestration_slot_065 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 66 | registry_orchestration_slot_066 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 67 | registry_orchestration_slot_067 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 68 | registry_orchestration_slot_068 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 69 | registry_orchestration_slot_069 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 70 | registry_orchestration_slot_070 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 71 | registry_orchestration_slot_071 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 72 | registry_orchestration_slot_072 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |
| 73 | registry_orchestration_slot_073 | reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json | conteggio registry/orchestrazione | registry | sì | Registry/orchestrazione H.2 | DA VERIFICARE | Slot contato nel totale 73, ma non esiste come motore QM nominato nel catalogo ufficiale; va materializzato o escluso dal claim '73 motori'. |

## 3. Verifica collegamento ai quattro generatori

### 3.1 Generatore Riassunti

- Entry point reale pagina: `POST /api/generate` con `kind=summary`.
- Runtime: `backend/phase5_full_pipeline_runtime_v51416.py`, funzione `run_summary_pipeline`.
- Dichiara route 55 e `all_motors_connected=True`, ma non invoca un registry QM eseguibile; usa gruppi generici hardcoded.
- Smoke: fallisce su breve/tecnico/narrativo; sul documento lungo produce 589 caratteri, non proporzionato.
- Mancano gerarchia concettuale, causa-effetto strutturato, problema-soluzione, paragrafi con ruolo, compressione controllata e controllo narrativo profondo.

### 3.2 Generatore Card

- Runtime: `run_cards_pipeline`; produce SVG e card strutturate.
- È il generatore più stabile negli smoke test: 9/9 PASS.
- Problema: `messaggio_chiave` è una frase generica fissa; il report dichiara 60 motori ma non prova esecuzione dei singoli QM.

### 3.3 Generatore Domande Studio

- Runtime: bridge `build_study_quiz_result` → `q52_build_quality_study_questions` → repair V5.14.17/V5.14.18.
- Funziona su medio/lungo/concetti simili/ripetitivo, ma fallisce su input breve, tecnico, narrativo, generico e lista.
- È separato dal quiz nel rendering, ma condivide la stessa base Q52 e diversi layer di repair.

### 3.4 Generatore Test / Quiz

- Runtime: `q52_build_quality_quiz` + `repair_test_quiz_options_v513d3` + rewrite V5.14.18.
- Critico: la UI renderizza `opt.is_correct` con classe `correct` e simbolo, quindi rivela la risposta corretta.
- Fallisce sugli stessi scenari fragili delle domande studio.

## 4. Test reali eseguiti

Comandi:
- `python3 scripts/run_phase5_14_3_local_backend_bridge.py`
- `python3 - <<'PY' ... urllib.request POST /api/generate per 9 scenari x 4 generatori`

| Scenario | Output | Esito | Motore | Item | Content len | Note |
|---|---|---|---|---:|---:|---|
| breve | summary | FAIL |  |  |  | HTTP 500 |
| breve | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 3 | 0 |  |
| breve | study | FAIL |  |  |  | HTTP 500 |
| breve | quiz | FAIL |  |  |  | HTTP 500 |
| medio | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 597 |  |
| medio | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 5 | 0 |  |
| medio | study | PASS | full_pipeline_study_route51_language_quality_v51418 | 4 | 0 |  |
| medio | quiz | PASS | full_pipeline_quiz_route63_language_quality_v51418 | 4 | 0 |  |
| lungo | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 589 |  |
| lungo | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 4 | 0 |  |
| lungo | study | PASS | full_pipeline_study_route51_language_quality_v51418 | 4 | 0 |  |
| lungo | quiz | PASS | full_pipeline_quiz_route63_language_quality_v51418 | 4 | 0 |  |
| tecnico | summary | FAIL |  |  |  | HTTP 500 |
| tecnico | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 3 | 0 |  |
| tecnico | study | FAIL |  |  |  | HTTP 500 |
| tecnico | quiz | FAIL |  |  |  | HTTP 500 |
| narrativo | summary | FAIL |  |  |  | HTTP 500 |
| narrativo | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 3 | 0 |  |
| narrativo | study | FAIL |  |  |  | HTTP 500 |
| narrativo | quiz | FAIL |  |  |  | HTTP 500 |
| concetti_simili | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 504 |  |
| concetti_simili | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 4 | 0 |  |
| concetti_simili | study | PASS | full_pipeline_study_route51_language_quality_v51418 | 4 | 0 |  |
| concetti_simili | quiz | PASS | full_pipeline_quiz_route63_language_quality_v51418 | 4 | 0 |  |
| ripetitivo | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 512 |  |
| ripetitivo | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 5 | 0 |  |
| ripetitivo | study | PASS | full_pipeline_study_route51_language_quality_v51418 | 4 | 0 |  |
| ripetitivo | quiz | PASS | full_pipeline_quiz_route63_language_quality_v51418 | 4 | 0 |  |
| generico | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 378 |  |
| generico | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 2 | 0 |  |
| generico | study | FAIL |  |  |  | HTTP 500 |
| generico | quiz | FAIL |  |  |  | HTTP 500 |
| lista | summary | PASS | full_pipeline_summary_route55_all_motors_v51416 | 0 | 450 |  |
| lista | cards | PASS | full_pipeline_cards_60_motors_graphic_v51416 | 4 | 0 |  |
| lista | study | FAIL |  |  |  | HTTP 500 |
| lista | quiz | FAIL |  |  |  | HTTP 500 |

Smoke test esistente: `python3 scripts/run_phase5_14_16_full_pipeline_smoke.py` → **FAIL**, `V51418_LANGUAGE_QUALITY_BLOCKED: study: frase vietata nel testo finale: magazzino stabilisce`.

## 5. Controllo anti-fallback e anti-demo

- La pagina clean non precarica il documento demo e invia il testo della textarea al backend.
- Il bridge blocca input corto e blocca `sicurezza informatica aziendale` se sotto 500 caratteri.
- Restano fixture e indice RAG con `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md` e `rag/indice_rag.json`: innocui se esclusi dalla pagina clean, rischiosi se usati come indice globale default.

## 6. Controllo qualità riassunti veri

Il riassunto attuale è una composizione euristica di frasi/fatti selezionati. È più leggibile di una lista, ma non costruisce davvero tema, sottotemi, gerarchia, causa-effetto, problema-soluzione e paragrafi con funzione. Il documento lungo dimostra il problema: PASS tecnico con output troppo corto.

## 7. Controllo mini motore LLM

Il mini LLM attuale è soprattutto una famiglia di motori euristici/statistici e pipeline di regole. Ha estrazione, ranking leggero, repair, filtri e template. Non mostra apprendimento reale online, training supervisionato integrato, embedding obbligatori nel flusso finale o decoder generativo addestrato. È quindi più un mini motore RAG/regolistico che un mini LLM pieno.

## 8. Come addestrare veramente il mini motore LLM

- Livello 1: dataset locale input/output, esempi buoni/cattivi, scoring qualità.
- Livello 2: BM25/TF-IDF evoluto, embedding locali, clustering concetti, deduplicazione semantica.
- Livello 3: classificatori piccoli per genericità, frasi incomplete, pertinenza documento, riassunto narrativo vs lista.
- Livello 4: teacher model per dataset, distillazione/fine tuning piccolo su coppie documento-output.
- Livello 5: server/API ibrido con LLM esterno per generazione e motori locali come guardrail.

## 9. Suggerimenti per ampliare i motori qualità

| Priorità | Nome motore | Scopo | Dove collegarlo | Output controllato | Test consigliato |
|---|---|---|---|---|---|
| P0 | Real Input Verification Engine | Bloccare input demo/fallback e confermare testo reale | prima del cleaner | tutti | smoke scenario + fixture negativa che deve fallire |
| P0 | No Silent Fallback Guard | Trasformare fallback in errore esplicito | UI bridge e backend | tutti | smoke scenario + fixture negativa che deve fallire |
| P0 | Document Grounding Checker | Verificare che ogni output derivi dal documento | post-generatore | tutti | smoke scenario + fixture negativa che deve fallire |
| P1 | Summary Narrative Coherence Engine | Valutare coesione narrativa e transizioni | route summary | Riassunto | smoke scenario + fixture negativa che deve fallire |
| P1 | Anti Bullet List Summary Engine | Bloccare riassunti-lista | route summary | Riassunto | smoke scenario + fixture negativa che deve fallire |
| P1 | Concept Hierarchy Builder | Costruire tema/sottotemi/gerarchie | prima generator router | tutti | smoke scenario + fixture negativa che deve fallire |
| P1 | Concept Fusion Engine | Fondere concetti simili e ridurre ridondanze | summary/card | Riassunto, Card | smoke scenario + fixture negativa che deve fallire |
| P1 | Summary Compression Controller | Rendere lunghezza proporzionata al documento | route summary | Riassunto | smoke scenario + fixture negativa che deve fallire |
| P1 | Quiz Distractor Strength Scorer | Valutare plausibilità distrattori | route quiz | Test/Quiz | smoke scenario + fixture negativa che deve fallire |
| P1 | UI Bridge Output Integrity Checker | Impedire risposta corretta visibile e bypass | UI bridge | Test/Quiz | smoke scenario + fixture negativa che deve fallire |
| P2 | Output Diversity Engine | Differenziare summary/card/study/quiz | cross-generator | tutti | smoke scenario + fixture negativa che deve fallire |
| P2 | Domain Adaptation Engine | Adattare stile e criteri al dominio | router | tutti | smoke scenario + fixture negativa che deve fallire |

## 10. Nuove architetture e nuovi progetti possibili

| Progetto | Riusa | Motori qualità | Generatori | Modifiche | Difficoltà | Valore demo |
|---|---|---|---|---|---|---|
| RAG per mini-corsi aziendali | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per formazione interna con quiz e certificati | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per generare slide e lezioni | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per creare study pack completi | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per analisi documenti aziendali | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per manuali tecnici e procedure | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per onboarding dipendenti | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | media | alto |
| RAG per scuola/ITS/università | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | alta | alto |
| RAG per app mobile offline/prototipo | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | alta | alto |
| RAG server/API professionale per aziende | input reale, cleaner, estrazione fatti, generatori summary/card/study/quiz, quality_report | Document Grounding Checker, No Silent Fallback Guard, Cross Generator Consistency Checker | riassunto, card, domande studio, quiz | registry eseguibile unico, export, tracciamento fonti e test browser/API | alta | alto |

## 11. Problemi trovati

| Gravità | Problema | File | Impatto | Come correggere | Priorità |
|---|---|---|---|---|---|
| CRITICO | Il claim '73 motori' è ambiguo: il catalogo ufficiale spiega 64 QM, mentre 73 è un totale di registry/orchestrazione. | reports/phase5_12i2_official_quality_motor_catalog_v1.json | Si rischia di dichiarare collegati motori che sono solo conteggi o route. | Creare un registry eseguibile unico con 73 entry concrete oppure rinominare il totale come 64 motori + 9 slot di orchestrazione. | P0 |
| CRITICO | La pagina reale V5.14.14 bypassa l'engine browser storico e chiama direttamente il bridge backend. | demo-rag/test-documenti-universale.html | Esistono pipeline parallele; report su universal-document-learning-engine non provano la pagina reale. | Definire un solo entrypoint produttivo e far passare UI, backend, quality registry e renderer dalla stessa contract API. | P0 |
| CRITICO | Il quiz mostra la risposta corretta nella UI con classe correct e simbolo di conferma. | demo-rag/test-documenti-universale.html | Viola il requisito: nessuna risposta corretta rivelata all'utente. | Non renderizzare is_correct; mantenere la risposta solo in stato interno o dopo invio risposta. | P0 |
| ALTO | summary/cards dichiarano all_motors_connected=True ma non invocano il registry 55/60 con executor QM; usano gruppi generici hardcoded. | backend/phase5_full_pipeline_runtime_v51416.py | I PASS possono essere decorativi; non dimostrano che i motori qualità abbiano bloccato output scadenti. | Sostituire il marker con esecuzione reale di route registry e report per singolo QM. | P0 |
| ALTO | Smoke test: 14/36 chiamate falliscono con HTTP 500, soprattutto documenti brevi, tecnici, narrativi, generici e lista. | scripts/run_phase5_14_3_local_backend_bridge.py | Pipeline non robusta su input comuni. | Catturare error body, aggiungere casi fallback vietato ma errore guidato, e validare requisiti minimi per ogni generatore. | P1 |
| ALTO | Riassunto lungo non è proporzionato: input da 6947 caratteri produce 589 caratteri. | backend/phase5_full_pipeline_runtime_v51416.py | Il riassunto passa, ma non soddisfa compressione controllata/proporzionata. | Collegare il motore progressivo documenti lunghi e un Summary Compression Controller. | P1 |
| MEDIO | Card contengono messaggio chiave generico fisso. | backend/phase5_full_pipeline_runtime_v51416.py | Le card possono sembrare pulite ma poco specifiche. | Derivare messaggio chiave da concetto/fatto e applicare Card Message Completeness Checker reale. | P1 |
| MEDIO | Study/quiz passano da Q52 ma poi vengono riscritti da layer manuali con pattern specifici. | scripts/run_phase5_14_3_local_backend_bridge.py | Qualità migliorata ma non ancora mini LLM: prevalgono euristiche/template. | Separare builder, repair e validator, con dataset e metriche per ridurre riscritture rigide. | P2 |
| MEDIO | Il vecchio documento demo sicurezza resta in rag/indice_rag.json e documenti test. | rag/indice_rag.json | Innocuo se non caricato dalla pagina clean, pericoloso se un RAG server usa indice globale come fonte default. | Marcarlo come test fixture esclusa o spostarlo fuori dagli indici produttivi. | P2 |
| ALTO | Lo smoke test esistente V5.14.16 fallisce sul generatore study per blocco qualità linguistica. | scripts/run_phase5_14_16_full_pipeline_smoke.py / scripts/run_phase5_14_3_local_backend_bridge.py | Un test di regressione locale dimostra che la pipeline full non è stabile anche fuori dagli smoke sintetici dell’audit. | Correggere il rewrite V5.14.18 o il testo fixture, poi far fallire/riuscire il test con asserzioni esplicite per study e quiz. | P1 |

## 12. Cose che funzionano

- Il bridge locale rifiuta input mancanti/corti e non usa un fallback demo silenzioso.
- Il generatore card è stabile negli smoke test e produce card grafiche renderizzabili.
- Study/quiz hanno builder Q52 reali e validatori strutturali su opzioni, item e duplicati.
- Esistono cataloghi e report utili; la base è promettente se trasformata in registry eseguibile.
- La pagina clean semplifica il flusso utente e usa testo reale dalla textarea.

## 13. Roadmap consigliata

### A - Audit e pulizia
- materializzare registry reale
- marcare legacy
- separare test fixture da indici produttivi
- bloccare fallback/demo
### B - Collegamento reale
- entrypoint unico
- route registry eseguibile
- quality_report per singolo QM
- niente pipeline parallele
### C - Riassunti veri
- gerarchia concetti
- fusione concetti
- revisione narrativa
- anti-lista
- compressione proporzionale
### D - Mini LLM reale
- dataset
- BM25/embedding
- classificatori qualità
- distillazione opzionale
### E - Versione aziende
- API professionale
- export
- report qualità
- demo pulite
- documentazione
