# Fast Document Q&A + Summary V2 Cache Benchmark

- Stato: **PASS**
- Caratteri documento simulato: `103690`
- Chunk creati: `167`

## Cache

- Primo caricamento: `MISS_BUILT`
- Tempo primo caricamento: `9.877417` ms
- Secondo caricamento: `HIT`
- Tempo cache hit: `1.394750` ms

## Q&A

- Domande testate: `10`
- Risposte OK: `10`
- Q&A media: `0.596500` ms
- Q&A mediana: `0.536250` ms
- Q&A P95: `0.765042` ms
- Q&A max: `0.765042` ms

## Summary

- Summary status: `OK`
- Frasi usate: `10`
- Summary interno: `4.888583` ms
- Summary totale: `4.895750` ms

## Limiti

- Non legge ancora PDF direttamente.
- Non fa OCR.
- Q&A e summary sono ancora extractive.
- Non applica ancora la regola riassunto 10% pagine / sinossi 1%.
