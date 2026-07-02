# Fast Document Q&A + Summary V2 Cache Benchmark

- Stato: **PASS**
- Caratteri documento simulato: `103690`
- Chunk creati: `167`

## Cache

- Primo caricamento: `MISS_BUILT`
- Tempo primo caricamento: `9.872417` ms
- Secondo caricamento: `HIT`
- Tempo cache hit: `1.398792` ms

## Q&A

- Domande testate: `10`
- Risposte OK: `10`
- Q&A media: `0.593254` ms
- Q&A mediana: `0.533604` ms
- Q&A P95: `0.754791` ms
- Q&A max: `0.754791` ms

## Summary

- Summary status: `OK`
- Frasi usate: `10`
- Summary interno: `4.746333` ms
- Summary totale: `4.753459` ms

## Limiti

- Non legge ancora PDF direttamente.
- Non fa OCR.
- Q&A e summary sono ancora extractive.
- Non applica ancora la regola riassunto 10% pagine / sinossi 1%.
