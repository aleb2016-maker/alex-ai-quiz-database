# Mini LLM Long Document RAG V3.9 Benchmark

- Stato: **PASS**
- Errori: `nessuno`
- Tempo totale: `37.575625` ms

## Linea di continuità

- V3.8/V3.8.6: qualità semantica e gate.
- V3.15: current stabile.
- Study Pack Current V3: output controllato.
- Output Modes V1: selezione output.
- Long Document RAG V3.9: documenti lunghi.

## Documento lungo simulato

- Pagine: `500`
- Parole: `37350`
- Chunk: `277`
- Build index: `14.492667` ms

## Target compressione

- Riassunto qualità 10%: `50` pagine equivalenti
- Sintesi breve 1%: `5` pagine equivalenti

## Retrieval/Q&A

- Answer status: `OK`
- Frasi risposta: `3`

### Risposta esempio

Il phishing della pagina 1 usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti. Il phishing della pagina 10 usa l'inganno per convincere le persone a fornire credenziali, dati Il phishing della pagina 30 usa

## Riassunto progressivo

- Stato: `OK`
- Frasi quality benchmark: `100`
- Frasi brief benchmark: `24`
- Tempo: `14.398166` ms

### Quality preview

della pagina 102 usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti. documenti aziendali della pagina 107 possono contenere informazioni operative, contratti, credenziali o dati riservati. della pagina 113 servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni accidentali. L'autenticazione a due fattori della pagina 120 rafforza l'accesso con un secondo controllo oltre alla La formazione del personale della pagina 6 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. pagina 129 aiutano a ricostruire incidenti, tentativi di accesso e modifiche importanti. I backup regolari della pagina 3 servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni accidentali. I backup regolari della pagina 124 servono a recuperare informazioni dopo errori, guasti, La classificazione dei dati della pagina 129 distingue informazioni pubbliche, interne, riservate e I registri di backup della pagina 134 permettono di controllare esito, frequenza e integrità personale della pagina 46 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. Le procedure di ripristino della pagina 145 aiutano a ridurre tempi di fermo e perdita di Il phishing della pagina 1 usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti. L'autenticazione a due fattori della pagina 1 rafforza l'accesso con un secondo controllo oltre alla password. I backup regolari della pagina 95 servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni L'

### Brief preview

della pagina 102 usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti. documenti aziendali della pagina 107 possono contenere informazioni operative, contratti, credenziali o dati riservati. della pagina 113 servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni accidentali. L'autenticazione a due fattori della pagina 120 rafforza l'accesso con un secondo controllo oltre alla La formazione del personale della pagina 6 riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. pagina 129 aiutano a ricostruire incidenti, tentativi di accesso e modifiche importanti. I backup regolari della pagina 3 servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni accidentali. I backup regolari della pagina 124 servono a recuperare informazioni dopo errori, guasti, La classificazione dei dati della pagina 129 distingue informazioni pubbliche, interne, riservate e I registri di backup della pagina 

## Study Pack da contesto RAG

- Status: `OK`
- Conteggi: `{'summary_sentences': 8, 'cards': 6, 'qas': 8, 'test_questions': 6, 'student_test_questions': 6}`
- Quality errors: `[]`

## Limiti

- V3.9 valida la struttura lunga su 500 pagine simulate.
- Non è ancora LLM neurale generativo.
- Non è ancora OCR.
- Non genera ancora materialmente 50 pagine complete nel report.
- Il prossimo blocco dovrà migliorare il riassunto progressivo multi-pass.
