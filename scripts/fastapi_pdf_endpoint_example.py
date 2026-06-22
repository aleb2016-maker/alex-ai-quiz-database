"""
fastapi_pdf_endpoint_example.py

Esempio di endpoint FastAPI.

Installazione:
    pip install fastapi uvicorn playwright
    python -m playwright install chromium

Avvio:
    uvicorn scripts.fastapi_pdf_endpoint_example:app --reload
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pdf_engine_playwright import genera_pdf_progetto


app = FastAPI(title="Motore PDF RAG")


class PdfRequest(BaseModel):
    html: str


@app.post("/genera-pdf")
async def genera_pdf(req: PdfRequest):
    output_dir = Path("dist/pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"materiale-rag-{uuid4().hex}.pdf"

    await genera_pdf_progetto(req.html, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=output_path.name,
    )
