# Report RAG Micro Rifinitura Universale V3.5L

Scopo: micro-correzioni generali sui campi visibili, non patch su frasi specifiche.

## Regole universali applicate
- tag/categorie duplicate tipo `X · X` -> `X` quando le parti sono davvero uguali
- aperture ripetute tipo `Per verificare...: Per verificare...` rimosse in modo generale
- spazi e punteggiatura visibile normalizzati
- metadati tecnici e id interni ignorati

## Risultati
- OK: dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json - modifiche visibili 1
- OK: dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json - modifiche visibili 0
- OK: dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json - modifiche visibili 1
- OK: dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json - modifiche visibili 0
- OK: dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json - modifiche visibili 0

Errori totali: 0

ESITO: OK
