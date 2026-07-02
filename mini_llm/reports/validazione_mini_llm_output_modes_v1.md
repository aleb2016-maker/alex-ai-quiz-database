# Validazione Mini LLM Output Modes V1

- Stato: **PASS**
- Errori: `nessuno`

## Modes validati

- `summary`: `OK` in `8.474334` ms
- `cards`: `OK` in `6.811292` ms
- `qa`: `OK` in `6.624333` ms
- `test`: `OK` in `6.473333` ms
- `full`: `OK` in `6.953792` ms

## PDF

- Full PDF status: `OK`
- Full PDF tempo: `2.340084` ms

## Esempi

### Card: Backup regolari

I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.

### Q&A

**D:** A cosa servono i backup regolari?

**R:** I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.

### Test studente

**Domanda:** A cosa servono i backup regolari?

1. Proteggere dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
2. Recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
3. Usare l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
4. Conservare password lunghe e uniche senza doverle ricordare tutte.

## Garanzie

- Mode summary genera solo riassunto.
- Mode cards genera solo card.
- Mode qa genera solo domande e risposte.
- Mode test genera test studente senza risposte corrette.
- Mode full genera tutto il materiale pubblico.
- Answer key separata se richiesta.

## Limiti

- Non ancora RAG 500 pagine.
- Non ancora LLM neurale generativo.
- No OCR.
