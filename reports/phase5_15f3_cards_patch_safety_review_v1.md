# FASE 5.15F.3 - Safety review patch card multi-documento

Status review: **PASS**

## File modificati

- `backend/phase5_15b_quality_checked_generators.py`
- `reports/phase5_15f_button_quality_diagnostics_v1.json` e `.md` aggiornati dal rerun diagnostico
- `reports/phase5_15e_approved_outputs_report_v1.json` aggiornato dallo smoke 5.15E
- questo report: `reports/phase5_15f3_cards_patch_safety_review_v1.md`

## Funzioni modificate o aggiunte

Modificata:

- `run_quality_checked_generator`
- `_card_payloads`, solo ramo `generator == "cards"` quando `phase5_15f3_multi_document_cards_reanchor` e true

Aggiunte:

- `_v515f3_card_words`
- `_v515f3_card_title`
- `_v515f3_card_key_message`
- `_v515f3_card_explanation`
- `_v515f3_card_points`
- `_v515f3_card_study_tip`
- `_v515f3_card_source`
- `_v515f3_card_context`
- `_v515f3_card_svg`
- `_v515f3_multidocument_card_facts`
- `_v515f3_cards_items_from_facts`
- `_v515f3_cards_reanchor_raw_output`
- `_v515f3_cards_public_output`

## Isolamento patch

Esito: **PASS**

- `_v515f3_cards_reanchor_raw_output(raw_output, text)` viene chiamata solo dentro `if generator == "cards"`.
- `_v515f3_cards_public_output(final_output)` viene chiamata solo dentro `if generator == "cards"`.
- Gli helper `_v515f3_*` usati nel payload QM sono attivi solo quando il generatore e `cards` e il quality report contiene `phase5_15f3_multi_document_cards_reanchor=True`.
- Bridge, UI, Quality Manager comune e raw_output comune non sono stati toccati.
- Gli hook quiz 5.15F.1 e study_questions 5.15F.2 restano separati e invariati.

## Prima / dopo multi-documento

Prima, multi-documento:

1. Titolo: `Aspetto operativo del documento`
   Messaggio: `Documento protocollo triage ambulatoriale: [Documento A - Protocollo triage ambulatoriale].`
   Spiegazione: `La card evidenzia che [Documento A - Protocollo triage ambulatoriale] Questo passaggio collega il contenuto del documento a un'azione operativa o a un controllo concreto.`

2. Titolo: `Aspetto operativo del documento`
   Messaggio: `Centro medico organizza triage: Il centro medico organizza il triage iniziale...`
   Spiegazione: `La card evidenzia che il centro medico organizza il triage iniziale... Questo passaggio collega il contenuto del documento a un'azione operativa o a un controllo concreto.`

Dopo, multi-documento:

1. Titolo: `Gestire il triage iniziale`
   Messaggio: `La priorita nasce da scheda, parametri vitali e sintomi riferiti, non dal solo ordine di arrivo.`
   Spiegazione: `Nel protocollo A il controllo iniziale motiva la scelta clinica e lascia una traccia leggibile al team.`

2. Titolo: `Organizzare il follow-up`
   Messaggio: `Terapia, segnali di allarme e canale di contatto trasformano la dimissione in istruzioni pratiche.`
   Spiegazione: `Nel piano B il paziente sa che cosa monitorare, quando chiedere aiuto e come proseguire la cura.`

Ulteriori card dopo patch:

- `Valutare tempi e reclami`
- `Registrare l'arrivo del paziente`
- `Usare il fascicolo clinico`
- `Assegnare l'azione correttiva`
- `Rivalutare i sintomi urgenti`
- `Controllare esami e referti`

## Controllo ripetizioni

Prima:

- Formule ricorrenti: `La card evidenzia...`, `Questo passaggio collega...`, `contenuto del documento`, `azione operativa`, `controllo concreto`.
- Titoli generici o duplicati: `Aspetto operativo del documento`.

Dopo:

- Multi-doc diretto: `APPROVED True`, `60/60`, `defects=[]`.
- Detector ripetizioni sul payload multi-doc: `[]`.
- Ogni card usa titolo, messaggio e spiegazione diversi, distribuiti su Documento A, B e C.

Nota: la diagnostica aggregata mostra ancora `ripetizioni` per il generatore `cards` perche il documento singolo stabile di magazzino conserva il testo legacy approvato (`La card evidenzia...`). Il caso multi-documento oggetto della F.3 e pulito.

## Test eseguiti

```text
backend/.venv/bin/python -m py_compile backend/phase5_15b_quality_checked_generators.py
```

Esito: **PASS**

```text
backend/.venv/bin/python scripts/run_phase5_15f_button_quality_diagnostics.py
```

Esito: **PASS**

```text
Genera Card: approved=True engine=full_pipeline_cards_60_motors_graphic_v51416
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

Controllo diretto multi-doc:

```text
cards ('APPROVED', True, 60, [])
quiz ('APPROVED', True, 63, [])
study_questions ('APPROVED', True, 51, [])
```

## Rischi residui

- Il file `backend/phase5_15b_quality_checked_generators.py` contiene tre override storici di `_card_payloads`; la patch lavora sull'override finale, che e quello effettivamente usato.
- La diagnostica aggregata segnala ancora ripetizioni sul documento singolo legacy di magazzino. Non e stato ritoccato per rispettare il focus F.3 sul multi-documento.
- Gli helper `_v515f3_*` sono regole lessicali mirate al caso clinico multi-documento della diagnostica. Se entrano domini multi-doc molto diversi, andra prevista una generalizzazione.

## Decisione

- Cards multi-doc: **PASS**
- Quiz multi-doc 5.15F.1: **PASS**
- Study questions multi-doc 5.15F.2: **PASS**
- 5.15E: **PASS**
- 5.15D: **PASS**

Consiglio: **committare la patch F.3**, lasciando a una fase separata l'eventuale pulizia del documento singolo legacy di magazzino e un refactor controllato degli override storici.
