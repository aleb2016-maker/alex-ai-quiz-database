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

## Motore linguistico finale V35M

La pipeline unica ufficiale include anche il lucidatore linguistico universale V35M.

Questo motore passa dopo V35L e rifinisce tutti i testi visibili.

Controlla e corregge:

- spazi doppi
- spazi mancanti dopo punteggiatura
- casi tipo Fonte:Il
- punteggiatura sporca
- accenti comuni
- apostrofi comuni
- contrazioni italiane
- parole duplicate consecutive
- frasi duplicate consecutive
- punto finale nei testi
- punto interrogativo nelle domande

Il motore V35M e riutilizzabile in qualsiasi app che lavora con testi, parole e frasi.

## Contesto semantico universale V35O

La pipeline unica ufficiale include anche il motore di contesto semantico universale V35O.

Questo motore passa dopo V35M e prima di V35N.

Serve a dare al completatore linguistico una base di significato.

Riconosce:

- tema
- sottotema
- categoria
- sottocategoria
- micro-concetti
- oggetto probabile della frase

Il processo e simile a un inverso del generatore di keyword:

- dal testo ricava micro-concetti
- dai micro-concetti ricava contesto
- dal contesto aiuta V35N a completare frasi incomplete

Questo motore sara utile anche per il futuro pulitore OCR, perche l'OCR spesso produce testi tagliati o sporchi che hanno bisogno di un contesto per essere ricostruiti.
