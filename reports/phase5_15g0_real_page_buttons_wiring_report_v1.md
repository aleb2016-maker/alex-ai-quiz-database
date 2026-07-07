# FASE 5.15G.0 - Verifica cablaggio pulsanti pagina reale

Status: **PASS diagnostico**

## Sintesi

La pagina `demo-rag/test-documenti-universale.html` non e UI statica: i quattro pulsanti hanno handler JS inline e chiamano il bridge locale `http://127.0.0.1:8765/api/generate`.

Il problema osservato, cioe click su **Genera riassunto** senza output e badge fermo su `Nessun output ancora`, e compatibile con bridge locale non attivo: la pagina chiama `/health`, disabilita i pulsanti se il bridge non risponde e quindi il click non produce eventi di generazione.

## Comando server corretto

Da root progetto:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source backend/.venv/bin/activate
python scripts/run_phase5_14_3_local_backend_bridge.py
```

In un secondo terminale:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
python -m http.server 8000
```

URL corretto:

```text
http://127.0.0.1:8000/demo-rag/test-documenti-universale.html
```

Anche `http://localhost:8000/demo-rag/test-documenti-universale.html` e usato dagli smoke 5.15D.

## Tabella cablaggio pulsanti

| Pulsante | Identificatore | Handler presente | Funzione chiamata | Backend/bridge chiamato | Output aggiornato | Problema trovato |
| --- | --- | --- | --- | --- | --- | --- |
| Genera riassunto | `button.summary[data-kind="summary"]` | si, `buttons.forEach(... addEventListener("click", ...))` | `generate("summary")` | `POST http://127.0.0.1:8765/api/generate`, poi `run_quality_checked_generator("summary", text)` | si, `renderSummary()` aggiorna `#output` e `#lastEngine` | nessun difetto di cablaggio; se bridge spento il pulsante e disabilitato |
| Genera card | `button.cards[data-kind="cards"]` | si | `generate("cards")` | `POST /api/generate`, poi `run_quality_checked_generator("cards", text)` | si, `renderCards()` aggiorna `#output` e `#lastEngine` | nessun difetto di cablaggio |
| Genera test | `button.quiz[data-kind="quiz"]` | si | `generate("quiz")` | `POST /api/generate`, poi `run_quality_checked_generator("quiz", text)` | si, `renderQuiz()` aggiorna `#output` e `#lastEngine` | nessun difetto di cablaggio; output pubblico usa `answer_check` |
| Genera domande studio | `button.study[data-kind="study"]` | si | `generate("study")` | `POST /api/generate`; bridge normalizza `study -> study_questions` | si, `renderStudy()` aggiorna `#output` e `#lastEngine` | nessun difetto; alias intenzionale |

## Verifica runtime browser reale

Server verificati:

- Bridge: `http://127.0.0.1:8765/health` risponde `200 OK`.
- Pagina: `http://127.0.0.1:8000/demo-rag/test-documenti-universale.html` risponde `200 OK`.

Stato pagina con bridge attivo:

- Banner: `Bridge locale attivo - 127.0.0.1:8765`
- Pulsanti `summary/cards/quiz/study`: abilitati.
- Console browser: nessun errore o warning rilevante.

Esito click reali:

| Click | Badge finale | Output renderizzato |
| --- | --- | --- |
| `summary` | `summary - full_pipeline_summary_route55_all_motors_v51416 - APPROVED - QM 55/55` | `Riassunto reale` |
| `cards` | `cards - full_pipeline_cards_60_motors_graphic_v51416 - APPROVED - QM 60/60` | 8 card grafiche |
| `quiz` | `quiz - full_pipeline_quiz_route63_language_quality_v51418 - APPROVED - QM 63/63` | 4 domande, 16 opzioni |
| `study` | `study - full_pipeline_study_route51_language_quality_v51418 - APPROVED - QM 51/51` | 4 domande studio |

## Endpoint e normalizzazione

La pagina invia:

```json
{
  "kind": "summary|cards|quiz|study",
  "text": "...",
  "strictNoFallback": true,
  "source": "clean_page_v51414"
}
```

Il bridge `scripts/run_phase5_14_3_local_backend_bridge.py` espone:

- `GET /health`
- `POST /api/generate`

La funzione bridge `normalize_quality_kind()` mappa:

- `summary -> summary`
- `cards -> cards`
- `quiz -> quiz`
- `test -> quiz`
- `study -> study_questions`
- `domande_studio -> study_questions`

Poi chiama sempre:

```text
backend.phase5_15b_quality_checked_generators.run_quality_checked_generator
```

## Diagnosi problema utente

Non ho trovato un difetto di cablaggio nei pulsanti. Il comportamento `Nessun output ancora` dopo click indica con alta probabilita una di queste condizioni operative:

1. Bridge `127.0.0.1:8765` non avviato.
2. Pagina aperta prima dell'avvio del bridge e pulsanti rimasti disabilitati fino al successivo health check.
3. Server statico `8000` avviato da una directory diversa, oppure pagina non ricaricata dopo aver acceso il bridge.
4. Testo documento non inserito; in questo caso pero la pagina dovrebbe mostrare errore `Testo troppo corto`, non restare su `Nessun output ancora`.

## Patch

Patch fatta: **no**.

Motivo: i pulsanti risultano gia collegati al bridge e ai generatori stabili. La patch minima proposta, se si volesse migliorare UX, sarebbe solo UI: rendere piu evidente che i pulsanti sono disabilitati quando il bridge e spento e aggiungere un piccolo messaggio accanto al badge output. Non e necessaria per il cablaggio.

## File letti

- `demo-rag/test-documenti-universale.html`
- `demo-rag/phase5-14-ui-buttons-real-connector.js`
- `runtime/web/*.js`
- `scripts/run_phase5_14_3_local_backend_bridge.py`
- `scripts/run_phase5_15d_real_page_generators_smoke.py`
- `backend/phase5_15b_quality_checked_generators.py`
- `backend/phase5_full_pipeline_runtime_v51416.py`

## Raccomandazione

Per riprodurre la pagina reale funzionante, avviare sempre prima il bridge su `8765`, poi il server statico su `8000`, quindi ricaricare la pagina. Nessuna modifica ai motori linguistici o al Quality Manager e necessaria.
