"""
test_pdf_engine_playwright.py

Esecuzione:
    python scripts/test_pdf_engine_playwright.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from pdf_engine_playwright import costruisci_documento_html, genera_pdf_progetto


SVG_OMINO_RISCALDAMENTO = """
<svg viewBox="0 0 120 120" aria-hidden="true">
  <rect x="0" y="0" width="120" height="120" rx="24" fill="rgba(255,255,255,0.08)"/>
  <circle cx="43" cy="38" r="14" fill="#f8fafc"/>
  <path d="M43 55 L43 82" stroke="#22d3ee" stroke-width="10" stroke-linecap="round"/>
  <path d="M43 60 L22 48" stroke="#f472b6" stroke-width="10" stroke-linecap="round"/>
  <path d="M43 60 L66 48" stroke="#f472b6" stroke-width="10" stroke-linecap="round"/>
  <path d="M78 30 C103 38 105 70 84 85" fill="none" stroke="#fbbf24" stroke-width="9" stroke-linecap="round"/>
  <path d="M83 85 L82 64 L99 77" fill="none" stroke="#fbbf24" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

SVG_CARDIO = """
<svg viewBox="0 0 120 120" aria-hidden="true">
  <rect x="0" y="0" width="120" height="120" rx="24" fill="rgba(255,255,255,0.08)"/>
  <circle cx="60" cy="30" r="11" fill="#f8fafc"/>
  <path d="M60 43 L38 70" stroke="#22d3ee" stroke-width="10" stroke-linecap="round"/>
  <path d="M60 43 L84 72" stroke="#8b5cf6" stroke-width="10" stroke-linecap="round"/>
  <circle cx="34" cy="74" r="10" fill="#22d3ee"/>
  <circle cx="88" cy="76" r="10" fill="#8b5cf6"/>
</svg>
"""

SVG_FORZA = """
<svg viewBox="0 0 120 120" aria-hidden="true">
  <rect x="0" y="0" width="120" height="120" rx="24" fill="rgba(255,255,255,0.08)"/>
  <rect x="20" y="53" width="18" height="28" rx="5" fill="#94a3b8"/>
  <rect x="82" y="53" width="18" height="28" rx="5" fill="#94a3b8"/>
  <path d="M38 67 H82" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
  <path d="M60 35 V67" stroke="#22d3ee" stroke-width="8" stroke-linecap="round"/>
  <circle cx="60" cy="30" r="9" fill="#f8fafc"/>
</svg>
"""


def card_html(svg: str, badge: str, titolo: str, descrizione: str) -> str:
    return f"""
    <div class="card-grafica">
      <div class="card-icona">{svg}</div>
      <span class="card-badge">{badge}</span>
      <h3>{titolo}</h3>
      <p>{descrizione}</p>
    </div>
    """


def blocco_esercizio(svg: str, badge: str, titolo: str, card_text: str, spiegazione: str) -> str:
    return f"""
    <article class="blocco-esercizio">
      {card_html(svg, badge, titolo, card_text)}
      <div class="testo-affiancato">
        <h3>Spiegazione</h3>
        <p>{spiegazione}</p>
      </div>
    </article>
    """


def costruisci_html_demo() -> str:
    contenuto = f"""
    <section class="pdf-header">
      <h1>Scheda allenamento</h1>
      <p>Materiale generato dal sistema RAG: card, riassunto, test e domande studio.</p>
    </section>

    <section class="sezione-pdf">
      <h2>Card grafiche con riassunto affiancato</h2>

      {blocco_esercizio(
        SVG_OMINO_RISCALDAMENTO,
        "riscaldamento",
        "1. Riscaldamento",
        "Prepara corpo, respiro e articolazioni prima della parte principale.",
        "Il riscaldamento serve ad aumentare gradualmente la temperatura corporea, attivare le articolazioni e preparare il sistema cardiovascolare. Nel documento viene indicato un tempo di 5/10 minuti."
      )}

      {blocco_esercizio(
        SVG_CARDIO,
        "cardio",
        "2. Cardio leggero",
        "Allena resistenza e continuità con uno sforzo aerobico moderato.",
        "Il cardio leggero può essere svolto con camminata, bicicletta o nuoto. La durata indicata è 25/30 minuti e rappresenta la parte aerobica principale."
      )}

      {blocco_esercizio(
        SVG_FORZA,
        "forza",
        "3. Forza e potenziamento",
        "Sviluppa controllo muscolare, stabilità e capacità di sostenere lo sforzo.",
        "Gli esercizi di forza durano 30 minuti e servono a migliorare tono, controllo e resistenza muscolare."
      )}
    </section>

    <section class="sezione-pdf riassunto-lungo">
      <h2>Riassunto lungo</h2>
      <p>La scheda di allenamento presenta una struttura equilibrata: prima prepara il corpo con il riscaldamento, poi introduce una fase cardiovascolare, successivamente inserisce il lavoro di forza e conclude con mobilità, equilibrio e recupero.</p>
      <p>Il punto centrale è la distribuzione del carico. Il documento non propone un'unica attività isolata, ma una sequenza ordinata. Questo aiuta a rendere l'attività più completa e più facile da seguire.</p>
      <p>I giorni rilevati sono lunedì, mercoledì, venerdì, sabato e domenica. La presenza di giorni di riposo indica che il recupero è considerato parte integrante del programma.</p>
      <p>Se il riassunto diventa molto lungo, questa sezione può continuare liberamente su più pagine. A differenza delle card e dei quiz, qui non viene imposto break-inside avoid, perché sarebbe sbagliato bloccare un testo lungo dentro una singola pagina.</p>
    </section>

    <section class="sezione-pdf">
      <h2>Test a risposta multipla</h2>

      <article class="blocco-quiz">
        <h3>1. Qual è lo scopo principale del riscaldamento?</h3>
        <ul class="opzioni-quiz">
          <li>A. Preparare corpo e articolazioni prima dell'attività</li>
          <li>B. Sostituire completamente la fase cardio</li>
          <li>C. Eliminare il bisogno di recupero</li>
          <li>D. Rendere inutile la mobilità finale</li>
        </ul>
      </article>

      <article class="blocco-quiz">
        <h3>2. Quale attività può essere usata per il cardio leggero?</h3>
        <ul class="opzioni-quiz">
          <li>A. Camminata, bicicletta o nuoto</li>
          <li>B. Solo esercizi di equilibrio</li>
          <li>C. Solo stretching passivo</li>
          <li>D. Solo riposo completo</li>
        </ul>
      </article>
    </section>

    <section class="sezione-pdf">
      <h2>Domande studio</h2>

      <article class="domanda-studio">
        <strong>1. Spiega perché il riscaldamento viene prima della parte principale.</strong>
        <div class="spazio-risposta"></div>
      </article>

      <article class="domanda-studio">
        <strong>2. Qual è la differenza tra cardio leggero e lavoro di forza?</strong>
        <div class="spazio-risposta"></div>
      </article>
    </section>
    """
    return costruisci_documento_html(contenuto, titolo="Materiale RAG - demo PDF")


async def main() -> None:
    html = costruisci_html_demo()
    output = Path("dist/pdf/materiale_rag_demo.pdf")
    path = await genera_pdf_progetto(html, output)
    print(f"PDF generato correttamente: {path}")


if __name__ == "__main__":
    asyncio.run(main())
