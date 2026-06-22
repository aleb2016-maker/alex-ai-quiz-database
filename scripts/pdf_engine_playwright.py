"""
pdf_engine_playwright.py

Motore PDF professionale HTML-to-PDF per progetto RAG.

Dipendenze:
    pip install playwright
    python -m playwright install chromium

Funzione principale:
    async def genera_pdf_progetto(html_content, output_path, ...)

Caratteristiche:
- Chromium headless via Playwright Async.
- PDF A4 multipagina.
- Sfondi scuri e gradienti preservati.
- Supporto card HTML/CSS/SVG.
- Regole anti-taglio per card, quiz e domande studio.
- Riassunti lunghi liberi di scorrere su più pagine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright


PDF_BASE_CSS = r"""
<style id="rag-pdf-base-css">
  :root {
    --bg-page: #0d0e15;
    --bg-panel: #121827;
    --bg-panel-2: #171f32;
    --border-soft: rgba(255, 255, 255, 0.13);
    --text-main: #f7f7fb;
    --text-muted: #cfd5e6;
    --violet-1: #25124d;
    --violet-2: #4c1d95;
    --green-soft: #28d89a;
    --blue-soft: #38bdf8;
  }

  html,
  body {
    margin: 0;
    padding: 0;
    background: var(--bg-page);
    color: var(--text-main);
    font-family: Arial, Helvetica, sans-serif;
    font-size: 16px;
    line-height: 1.45;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .pdf-documento {
    width: 100%;
    background: var(--bg-page);
  }

  .pdf-header {
    margin-bottom: 18px;
    padding: 18px 22px;
    border-radius: 22px;
    background:
      radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 35%),
      linear-gradient(135deg, #111827 0%, #141b31 100%);
    border: 1px solid var(--border-soft);
  }

  .pdf-header h1 {
    margin: 0 0 8px 0;
    font-size: 30px;
    line-height: 1.12;
  }

  .pdf-header p {
    margin: 0;
    color: var(--text-muted);
    font-weight: 700;
  }

  .sezione-pdf {
    margin-bottom: 18px;
  }

  .sezione-pdf h2 {
    margin: 0 0 12px 0;
    font-size: 24px;
    line-height: 1.2;
  }

  .blocco-esercizio {
    display: flex;
    gap: 18px;
    align-items: stretch;
    margin-bottom: 16px;
    padding: 16px;
    border-radius: 24px;
    background:
      radial-gradient(circle at top left, rgba(40, 216, 154, 0.13), transparent 34%),
      linear-gradient(135deg, #111827 0%, #171f32 100%);
    border: 1px solid var(--border-soft);
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .card-grafica {
    flex: 0 0 235px;
    min-height: 245px;
    padding: 16px;
    border-radius: 24px;
    color: #ffffff;
    background:
      radial-gradient(circle at top left, rgba(139, 92, 246, 0.36), transparent 38%),
      radial-gradient(circle at bottom right, rgba(40, 216, 154, 0.18), transparent 34%),
      linear-gradient(145deg, #25124d 0%, #4c1d95 52%, #21123e 100%);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.28);
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .card-icona {
    height: 96px;
    margin-bottom: 12px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.10);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-icona svg {
    width: 82px;
    height: 82px;
  }

  .card-badge {
    display: inline-block;
    margin-bottom: 10px;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.16);
    font-size: 12px;
    font-weight: 900;
  }

  .card-grafica h3 {
    margin: 0 0 8px 0;
    font-size: 20px;
    line-height: 1.15;
  }

  .card-grafica p {
    margin: 0;
    font-size: 14px;
    line-height: 1.35;
    font-weight: 700;
  }

  .testo-affiancato {
    flex: 1 1 auto;
    min-width: 0;
    padding: 4px 2px;
  }

  .testo-affiancato h3 {
    margin: 0 0 8px 0;
    font-size: 22px;
    line-height: 1.2;
  }

  .testo-affiancato p {
    margin: 0 0 8px 0;
    color: var(--text-muted);
    font-size: 16px;
    line-height: 1.48;
  }

  .riassunto-lungo {
    padding: 18px 22px;
    border-radius: 24px;
    background: var(--bg-panel);
    border: 1px solid var(--border-soft);
    break-inside: auto !important;
    page-break-inside: auto !important;
  }

  .riassunto-lungo h2,
  .riassunto-lungo h3 {
    break-after: avoid;
    page-break-after: avoid;
  }

  .riassunto-lungo p {
    margin: 0 0 11px 0;
    color: var(--text-muted);
    font-size: 16.5px;
    line-height: 1.55;
  }

  .blocco-quiz {
    margin-bottom: 14px;
    padding: 16px 18px;
    border-radius: 20px;
    background: var(--bg-panel-2);
    border: 1px solid var(--border-soft);
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .blocco-quiz h3 {
    margin: 0 0 12px 0;
    font-size: 19px;
    line-height: 1.3;
  }

  .opzioni-quiz {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 9px;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .opzioni-quiz li {
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.07);
    color: var(--text-main);
    font-weight: 700;
  }

  .domanda-studio {
    margin-bottom: 12px;
    padding: 14px 16px;
    border-radius: 18px;
    background: #111a2b;
    border: 1px solid var(--border-soft);
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .domanda-studio strong {
    display: block;
    margin-bottom: 6px;
    font-size: 17px;
  }

  .spazio-risposta {
    min-height: 48px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.055);
    border: 1px dashed rgba(255, 255, 255, 0.18);
  }

  .pagina-card {
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 10mm;
    min-height: 257mm;
    break-after: page;
    page-break-after: always;
  }

  .pagina-card:last-child {
    break-after: auto;
    page-break-after: auto;
  }

  .pagina-card .card-grafica {
    width: 100%;
    min-height: 0;
  }

  @media print {
    html,
    body {
      background: var(--bg-page) !important;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    .pdf-documento {
      background: var(--bg-page) !important;
    }

    .blocco-esercizio,
    .card-grafica,
    .blocco-quiz,
    .domanda-studio {
      break-inside: avoid !important;
      page-break-inside: avoid !important;
    }

    .riassunto-lungo {
      break-inside: auto !important;
      page-break-inside: auto !important;
    }

    h1,
    h2,
    h3 {
      break-after: avoid;
      page-break-after: avoid;
    }

    .opzioni-quiz {
      break-inside: avoid !important;
      page-break-inside: avoid !important;
    }

    @page {
      size: A4 portrait;
      margin: 10mm;
    }
  }

  @media screen and (max-width: 850px) {
    .blocco-esercizio {
      flex-direction: column;
    }

    .card-grafica {
      flex-basis: auto;
      width: 100%;
    }

    .opzioni-quiz {
      grid-template-columns: 1fr;
    }
  }


  /* === FIX SPAZIATURA TITOLI PDF ===
     Evita che titoli come "Test a risposta multipla" e
     "Domande studio" risultino attaccati al bordo sinistro.
  */
  .pdf-documento {
    padding-left: 6px;
    padding-right: 6px;
  }

  .sezione-pdf h2 {
    padding-left: 10px;
    padding-right: 10px;
  }
  /* === FINE FIX SPAZIATURA TITOLI PDF === */



  /* === FIX ALLINEAMENTI E SFONDI PDF ===
     1) Riallinea "Riassunto lungo" al testo sottostante
     2) Rende più omogeneo lo sfondo dei blocchi card + spiegazione
  */
  .pdf-documento {
    padding-left: 6px;
    padding-right: 6px;
  }

  .sezione-pdf h2 {
    margin: 0 0 12px 0;
    padding-left: 10px;
    padding-right: 10px;
  }

  .riassunto-lungo h2 {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .blocco-esercizio {
    overflow: hidden;
    background: linear-gradient(135deg, #101726 0%, #13213a 100%) !important;
  }

  .testo-affiancato {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    min-height: 100%;
    background: transparent !important;
  }
  /* === FINE FIX ALLINEAMENTI E SFONDI PDF === */



  /* === FIX OMBRA BLOCCO ESERCIZIO PDF ===
     Rende omogeneo il fondo del blocco card + spiegazione
     eliminando l'ombra esterna che sporca il lato testo.
  */
  .blocco-esercizio {
    position: relative;
    background: #101b2f !important;
    background-image: none !important;
    overflow: hidden !important;
  }

  .card-grafica {
    box-shadow: none !important;
  }

  .testo-affiancato {
    background: transparent !important;
    box-shadow: none !important;
    position: relative;
    z-index: 2;
  }
  /* === FINE FIX OMBRA BLOCCO ESERCIZIO PDF === */

</style>
"""


def costruisci_documento_html(contenuto_body: str, titolo: str = "Materiale generato RAG") -> str:
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titolo}</title>
  {PDF_BASE_CSS}
</head>
<body>
  <main class="pdf-documento">
    {contenuto_body}
  </main>
</body>
</html>
"""


async def genera_pdf_progetto(
    html_content: str,
    output_path: str | Path,
    *,
    base_url: Optional[str] = None,
    timeout_ms: int = 60_000,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_pronto = html_content

    if "<html" not in html_pronto.lower():
        html_pronto = costruisci_documento_html(
            contenuto_body=html_pronto,
            titolo="Materiale generato RAG",
        )

    if base_url and "<head>" in html_pronto.lower():
        html_pronto = html_pronto.replace(
            "<head>",
            f'<head><base href="{base_url}">',
            1,
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--font-render-hinting=medium",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
        )

        page = await context.new_page()
        page.set_default_timeout(timeout_ms)
        page.set_default_navigation_timeout(timeout_ms)

        try:
            await page.emulate_media(media="print", color_scheme="dark")

            await page.set_content(
                html_pronto,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            try:
                await page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                pass

            await page.evaluate("""
                async () => {
                    if (document.fonts && document.fonts.ready) {
                        await document.fonts.ready;
                    }
                }
            """)

            await page.wait_for_timeout(250)

            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=False,
                margin={
                    "top": "10mm",
                    "right": "10mm",
                    "bottom": "10mm",
                    "left": "10mm",
                },
            )

        finally:
            await context.close()
            await browser.close()

    return output_path


async def genera_pdf_da_file_html(
    html_path: str | Path,
    output_path: str | Path,
    *,
    timeout_ms: int = 60_000,
) -> Path:
    html_path = Path(html_path)
    html_content = html_path.read_text(encoding="utf-8")
    base_url = html_path.parent.resolve().as_uri() + "/"

    return await genera_pdf_progetto(
        html_content,
        output_path,
        base_url=base_url,
        timeout_ms=timeout_ms,
    )
