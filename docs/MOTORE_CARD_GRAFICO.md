# Motore card grafiche

Questo motore genera card formative con grafica coerente rispetto a materia e concetto.

## Obiettivo

Trasformare concetti estratti da documenti, RAG o database quiz in card più belle e riconoscibili.

Esempi:

- Cybersecurity + backup → card con cloud, database e freccia.
- Cybersecurity + password → card con chiave e lucchetto.
- Informatica + database → card con cilindro database.
- AI + RAG → card con stile chip/rete neurale.
- Matematica + derivata → card con curva e tangente.
- Biologia + DNA → card con doppia elica.

## File principali

```text
config/temi_card_materie.json
config/layout_card_grafiche.json
config/icone_concetti_materie.json
config/sinonimi_concetti.json
scripts/motore_card_grafiche.py
scripts/validatore_temi_card.py
scripts/validatore_concetti_card.py
scripts/validatore_card_grafiche_completo.py
```

## Test rapido

```bash
python3 scripts/validatore_card_grafiche_completo.py
open reports/demo_card_grafiche.html
```

## Uso singola card

```bash
python3 scripts/motore_card_grafiche.py   --materia cybersecurity   --concetto backup   --titolo "Concetto chiave: Backup"   --testo "Il backup crea copie dei dati per permettere il ripristino."   --output reports/card_backup.html

open reports/card_backup.html
```

## Integrazione futura nel RAG

Il motore RAG potrà passare al motore card:

- materia rilevata o scelta dall'utente;
- concetto chiave;
- spiegazione breve.

Il motore restituirà una card HTML/SVG pronta per `cards.html` e `cards.json`.
