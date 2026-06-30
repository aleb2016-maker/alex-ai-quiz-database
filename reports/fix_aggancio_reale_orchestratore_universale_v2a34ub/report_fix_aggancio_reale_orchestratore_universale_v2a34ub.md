# V2A34U-B - Aggancio reale orchestratore universale

Problema trovato:
- Il pacchetto universale V2A34U era caricato nella pagina.
- Il ponte V2A34U era presente nel motore principale.
- Però il ponte non veniva chiamato prima del render finale del riassunto.
- Quindi il browser continuava a mostrare il vecchio riassunto estrattivo V2A33.

Correzione applicata:
- Convertita `const sezioniFinali` in `let sezioniFinali` nel punto del riassunto lungo.
- Inserita la chiamata reale a `applicaOrchestratoreRiassuntoUniversaleV2A34U(...)` prima di `renderizzaRiassuntoLungoV2A28(...)`.
- Aggiunta diagnostica `window.__ragRiassuntoUniversaleV2A34UB`.
- Aggiornato solo cache-bust tecnico degli script.

Vincoli rispettati:
- Non modificati pulsanti.
- Non modificata interfaccia grafica.
- Non modificati CSS.
- Non modificati PDF.
- Non modificati card, test o domande studio.
- Non modificati i motori già funzionanti.
