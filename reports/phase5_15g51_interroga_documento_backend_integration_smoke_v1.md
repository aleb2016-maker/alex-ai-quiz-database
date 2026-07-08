# Fase 5.15G.5.1 - Interroga Documento backend integration smoke

Esito: **PASS**

## Casi
- json_answered: generator `interroga_documento`, atteso `ANSWERED`, ottenuto `ANSWERED`, approved `True`, defects `[]`
- json_not_found: generator `ask_document`, atteso `NOT_FOUND_IN_DOCUMENT`, ottenuto `NOT_FOUND_IN_DOCUMENT`, approved `True`, defects `[]`
- marker_answered: generator `domanda_documento`, atteso `ANSWERED`, ottenuto `ANSWERED`, approved `True`, defects `[]`

## Scope
- Study Questions non eliminate.
- UI non collegata in questa fase.
- Integrazione limitata al backend quality generator.
- Il motore usato è `phase5_15g5_document_qa_engine.run_interroga_documento`.
- Lo smoke controlla solo testo utente visibile, non chiavi tecniche JSON.
