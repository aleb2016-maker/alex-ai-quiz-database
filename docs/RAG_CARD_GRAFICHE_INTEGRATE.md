# Integrazione motore card grafiche nel RAG

Questa integrazione collega il motore grafico delle card alla demo RAG.

## Cosa cambia

Nella demo RAG compare un selettore:

```text
Grafica card per materia
- Automatica / rileva dal contenuto
- Cybersecurity
- Informatica
- Intelligenza Artificiale
- Matematica
- Fisica
- Chimica
- Biologia
- Generico
```

Quando vengono generate le card:

- la materia decide colori, badge e stile generale;
- il concetto decide l'icona SVG;
- il file `cards.html` scaricato contiene card colorate e illustrate;
- il file `cards.json` contiene anche materia, concetto, tema e icona.

## Output principali

I download principali del RAG restano:

```text
riassunto.html
riassunto.md
tabelle_concetti.md
tabelle_concetti.csv
cards.html
cards.json
```

Il quiz può restare nella demo come esempio, ma per il motore RAG scaricabile l'obiettivo principale sono riassunti, tabelle e card.
