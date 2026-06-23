# Motore Java PDF RAG - V19

Genera PDF da JSON usando Apache PDFBox.

## Demo

```bash
bash scripts/run_demo_v19.sh
open output/cards-demo-v19.pdf
```

## Da JSON

```bash
bash scripts/run_from_json.sh input.json output.pdf
```

Questa V19 punta a una grafica piu piena: 2 card per pagina, icone grandi, pannello visuale, punti chiave e footer.


Correzione V19: icone ridisegnate con coordinate sicure, elementi sempre dentro il riquadro, badge e numero allineati, rimosse linee decorative basse che sembravano appiccicate al bordo.


## Novita V19

- Supporto a immagini PNG starter per le categorie principali.
- Fallback automatico alle icone vettoriali solo se manca l'immagine.
- Base pronta per future grafiche migliori nel percorso RAG -> JSON -> PDF.


## Migliorie V19

- Sostituite le prime PNG starter con illustrazioni flat più pulite e meno simili ai vecchi disegni vettoriali.
- Rimossa l'icona azienda con rettangoli/porte confuse.
- Priorità alle immagini collegate al titolo della card, per esempio 'Ingresso documento' usa documento invece di edificio generico.
