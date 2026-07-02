# Validazione Mini LLM Study Pack CLI V2

- Stato: **PASS**
- Errori: `nessuno`

## Risultati

- Engine: `mini_llm_study_pack_v3_quality_gate`
- MD/Public JSON status: `OK`
- MD tempo: `6.777709` ms
- PDF/Public JSON status: `OK`
- PDF tempo: `2.231583` ms
- Conteggi: `{'summary_sentences': 8, 'cards': 6, 'qas': 8, 'test_questions': 6, 'student_test_questions': 6}`
- Markdown studente: `OK`
- Answer key file: `/private/var/folders/s3/q53ggzhn0dj5v3mm46w3bgrr0000gn/T/mini_llm_study_cli_v2_3g1equmk/study_pack_answers.json`

## Test studente esempio

**Domanda:** A cosa servono i backup regolari?

1. Proteggere dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
2. Recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
3. Usare l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
4. Conservare password lunghe e uniche senza doverle ricordare tutte.

## Answer key esempio

- ID: `q01`
- Correct index: `1`
- Answer: Recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.

## Garanzie V2

- Markdown studente senza risposte corrette.
- Public JSON senza answer key.
- Answer key separata su file dedicato.
- Motore collegato a Study Pack V3 Quality Gate.

## Limiti

- Non è ancora LLM neurale generativo.
- Non usa OCR.
- Usa file TXT/MD/PDF testuali.
