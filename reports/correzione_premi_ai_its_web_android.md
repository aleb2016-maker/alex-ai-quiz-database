# Correzione premi AI ITS Web/Android

## Modifiche applicate

- Web: la vecchia card finale viene rimossa quando parte un nuovo quiz.
- Web: a fine quiz viene generato un nuovo premio anche se il punteggio è identico.
- Web: il premio evita di ripetere subito lo stesso titolo per lo stesso punteggio.
- Web: coriandoli più ampi, fluidi e generati dal basso.
- Demo AI: aggiornati `demo-ai/ai-effects.js` e `demo-ai/ai-effects.css`.
- ZIP Web AI ITS: aggiornati `ai-effects.js`, `ai-effects.css` e riferimenti HTML.
- Android: aggiunti `FinalRewardEngine.kt` e `AiItsRewardEffects.kt` dentro `quizengine/` nello ZIP.
- Android: aggiornato il LEGGIMI con istruzioni reali di integrazione Compose.

## File modificati

- `demo-ai/ai-effects.css`
- `demo-ai/ai-effects.js`
- `demo-ai/index.html`
- `downloads/pacchetto-android-ai-its-finale-semplice.zip`
- `downloads/pacchetto-web-ai-its-demo.zip`
- `runtime/android/AiItsRewardEffects.kt`
- `runtime/android/FinalRewardEngine.kt`
- `runtime/web/ai-effects.css`
- `runtime/web/ai-effects.js`
- `scripts/verifica_premi_ai_its_v2.py`
