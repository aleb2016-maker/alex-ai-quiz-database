# Mini LLM Universal Current Engine V3.9.6.1

- Stato: **PASS**
- Errori: `nessuno`

## Controlli

- Current senza termini specialistici: `PASS`
- Multi-dominio: `PASS`
- Documento reale: `PASS`
- Study pack quality guard: `PASS`
- Report generati: `6`

## Architettura

- Current Engine V3.9.6.1 usa il bridge V3.9.5.
- Il bridge usa il core universale V3.9.4U.
- I profili specialistici restano separati.
- Il cleaner è safe.
- Lo study pack legacy viene bloccato se produce domande, titoli o opzioni brutte.
- Non sono stati toccati UI, OCR o PDF export.

### sicurezza informatica aziendale

- Status: `PASS`
- Profilo: `informatics_security_v394u`
- Study pack: `SKIPPED`
- Cleaner: `{'used_cleaner': False, 'reason': 'Documento corto: uso testo grezzo per non perdere segnali di dominio.', 'raw_words': 30, 'cleaned_words': 30}`
- Errori: `[]`

### sport e allenamento

- Status: `PASS`
- Profilo: `sport_training_v394u`
- Study pack: `SKIPPED`
- Cleaner: `{'used_cleaner': False, 'reason': 'Documento corto: uso testo grezzo per non perdere segnali di dominio.', 'raw_words': 26, 'cleaned_words': 26}`
- Errori: `[]`

### curriculum e profilo professionale

- Status: `PASS`
- Profilo: `curriculum_profile_v394u`
- Study pack: `SKIPPED`
- Cleaner: `{'used_cleaner': False, 'reason': 'Documento corto: uso testo grezzo per non perdere segnali di dominio.', 'raw_words': 25, 'cleaned_words': 25}`
- Errori: `[]`

### documento scientifico

- Status: `PASS`
- Profilo: `science_document_v394u`
- Study pack: `SKIPPED`
- Cleaner: `{'used_cleaner': False, 'reason': 'Documento corto: uso testo grezzo per non perdere segnali di dominio.', 'raw_words': 25, 'cleaned_words': 25}`
- Errori: `[]`

### documento aziendale

- Status: `PASS`
- Profilo: `business_document_v394u`
- Study pack: `SKIPPED`
- Cleaner: `{'used_cleaner': False, 'reason': 'Documento corto: uso testo grezzo per non perdere segnali di dominio.', 'raw_words': 23, 'cleaned_words': 23}`
- Errori: `[]`

### sicurezza informatica aziendale

- Status: `PASS`
- Profilo: `informatics_security_v394u`
- Study pack: `QUALITY_BLOCKED`
- Cleaner: `{'used_cleaner': True, 'reason': 'Cleaner accettato.', 'raw_words': 1702, 'cleaned_words': 1039, 'raw_profile': 'informatics_security_v394u', 'cleaned_profile': 'informatics_security_v394u'}`
- Errori: `[]`
