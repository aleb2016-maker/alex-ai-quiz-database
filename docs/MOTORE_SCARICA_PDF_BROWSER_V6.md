# Motore Scarica PDF browser-only V6

La V6 risolve il taglio delle scritte della V5.

## Logica

- le card restano catturate come immagini intere;
- le sezioni scritte vengono catturate come singoli riquadri;
- il PDF crea una pagina scura;
- disegna il titolo sezione;
- inserisce il riquadro catturato con clipping arrotondato;
- non include la sezione successiva;
- non taglia il testo.

Questa versione evita il crop lungo della pagina che poteva includere pezzi della sezione successiva.
