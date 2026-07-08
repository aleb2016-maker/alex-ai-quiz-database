# Fase 5.15G.5.2 - UI Backend Real Connection Smoke

Esito: **PASS**

## Collegamento reale
- Endpoint: `http://127.0.0.1:8765/api/generate`
- kind inviato: `interroga_documento`
- text inviato: JSON con `document_text` e `user_question`
- Nessuna risposta hardcoded.
- Nessun fallback/demo.

## Checks
- connector_exists: `True`
- page_exists: `True`
- connector_has_interroga_label: `True`
- connector_calls_real_backend_kind: `True`
- connector_sends_document_text: `True`
- connector_sends_user_question: `True`
- connector_question_textarea: `True`
- connector_bypasses_old_study_motor: `True`
- page_has_question_textarea: `True`
- page_sets_backend_kind: `True`
- page_sends_document_text: `True`
- page_sends_user_question: `True`
- page_fetch_uses_backend_kind: `True`
- page_fetch_uses_backend_text: `True`
- page_renders_document_qa: `True`
- backend_has_ask_document: `True`
- backend_has_interroga_alias: `True`
- backend_calls_g5_engine: `True`
