# Mini LLM Long Document RAG V3.9.1 Semantic Repair Benchmark

- Stato: **PASS**
- Errori: `nessuno`
- Tempo totale: `68.855834` ms

## Linea di continuità

- V3.8/V3.8.6: qualità semantica e gate.
- V3.15: current stabile.
- Study Pack Current V3: output controllato.
- Output Modes V1: selezione output.
- Long Document RAG V3.9.1: semantic repair su documenti lunghi.

## Documento lungo simulato

- Pagine: `500`
- Parole: `37350`
- Frasi valide: `2500`
- Chunk sentence-safe: `270`
- Build index: `48.959125` ms

## Target compressione

- Riassunto qualità 10%: `50` pagine equivalenti
- Sintesi breve 1%: `5` pagine equivalenti

## Answer pulita

- Status: `OK`
- Errori qualità: `[]`

### Risposta esempio

Il phishing della pagina 1 usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti.

## Riassunto progressivo pulito

- Stato: `OK`
- Errori qualità: `[]`
- Frasi quality benchmark: `80`
- Frasi brief benchmark: `20`
- Tempo: `3.780791` ms

### Quality preview

La formazione del personale della pagina 107 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 116 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 127 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 146 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 157 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 166 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 177 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 196 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 207 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 216 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 227 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 246 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 257 riduce errori, dist

### Brief preview

La formazione del personale della pagina 107 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 116 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 127 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 146 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 157 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 166 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 177 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. La formazione del personale della pagina 196 riduce errori, distrazioni e comportamenti rischiosi durant

## Study Pack da contesto RAG

- Status: `OK`
- Conteggi: `{'summary_sentences': 8, 'cards': 6, 'qas': 8, 'test_questions': 6, 'student_test_questions': 6}`
- Semantic errors: `[]`
- Quality errors: `[]`

## Limiti

- V3.9.1 valida la struttura lunga su 500 pagine simulate.
- Non è ancora LLM neurale generativo.
- Non è ancora OCR.
- Non genera ancora materialmente 50 pagine complete nel report.
- Dopo questa blindatura si può fare un test pratico su documento reale.
