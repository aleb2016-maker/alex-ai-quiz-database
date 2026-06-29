# RAG Pipeline Unica Ufficiale

La pipeline unica ufficiale collega automaticamente tutti i motori RAG gia esistenti.

## Obiettivo

Evitare collegamenti manuali tra motori separati.

Da ora in poi l'utente, la pagina web, una app aziendale o un test automatico devono usare un solo entrypoint:

python3 scripts/rag_pipeline_unica_ufficiale.py --input percorso/documento.md

## Catena interna

La pipeline collega automaticamente:

1. Knowledge Base V34B
2. Quality Gate V34D
3. Output da KB clean V34E
4. Bridge motori qualita V35B
5. Motore didattico V35C
6. Motore test V35D
7. Orchestratore V35E
8. Selezionatore V35F
9. Revisore qualita testuale V35G
10. Revisore naturalezza anti-keyword V35I
11. Revisore accordo/pronomi V35J
12. Cleaner finale universale V35K
13. Micro-rifinitura universale V35L

## Regola architetturale

I motori possono restare separati internamente come moduli riutilizzabili, ma non devono piu essere collegati manualmente.

L'uso ufficiale deve passare dalla pipeline unica.

## Output

La pipeline produce un JSON finale pubblico in:

dist/generated/rag_pipeline_unica_ufficiale/<slug>/output_finale_rag_pipeline_unica.json

Il JSON contiene:

- riassunto
- card
- domande studio
- test
- controlli qualita
- metadati dei motori

## Nota tecnica

Il lane interno sicurezza_reale resta per ora una compatibilita tecnica con la catena V35 gia esistente.

L'obiettivo successivo sara eliminare anche questa dipendenza nominale e rendere il lane completamente dinamico per ogni documento.
