#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import subprocess
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


DATA_URL_RE = re.compile(r"^data:(image/(?:png|jpeg|jpg|webp));base64,(.+)$", re.DOTALL)
MAX_BODY_MB = 220


def safe_filename(name: str, default: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-")
    return clean or default


class PdfExportHandler(SimpleHTTPRequestHandler):
    project_root: Path = Path.cwd()
    tmp_root: Path = Path.cwd() / "tmp" / "pdf_export"

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/export/health":
            self.send_json({"ok": True, "service": "rag_pdf_export_server"})
            return

        # Serve anche i file statici del progetto: demo-rag, JS, HTML, ecc.
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/export/cards-pdf":
            self.send_error(404, "Endpoint non trovato")
            return

        try:
            payload = self.read_json_body()
            pdf_path = self.handle_pdf_export(payload)
            self.send_pdf(pdf_path, payload.get("filename") or "card-generate.pdf")
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        max_bytes = MAX_BODY_MB * 1024 * 1024
        if length <= 0:
            raise ValueError("Body vuoto")
        if length > max_bytes:
            raise ValueError(f"Body troppo grande: {length} byte")

        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def handle_pdf_export(self, payload: dict) -> Path:
        images = payload.get("images")
        if not isinstance(images, list) or not images:
            raise ValueError("Nessuna immagine ricevuta. Il frontend deve inviare images[].dataUrl")

        session_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        session_dir = self.tmp_root / session_id
        images_dir = session_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        for index, item in enumerate(images, start=1):
            data_url = item.get("dataUrl") if isinstance(item, dict) else None
            if not data_url:
                raise ValueError(f"Immagine {index} senza dataUrl")

            match = DATA_URL_RE.match(data_url)
            if not match:
                raise ValueError(f"Immagine {index} non è un data URL immagine valido")

            mime_type = match.group(1)
            encoded = match.group(2)
            extension = ".jpg" if mime_type in {"image/jpeg", "image/jpg"} else ".png"
            if mime_type == "image/webp":
                extension = ".webp"

            binary = base64.b64decode(encoded)
            image_path = images_dir / f"card_{index:02d}{extension}"
            image_path.write_bytes(binary)

        output_pdf = session_dir / "card-generate.pdf"
        json_output = session_dir / "cards-image-only.json"
        title = payload.get("title") or "PDF card generate dalla demo"

        bridge = self.project_root / "scripts" / "genera_pdf_reale_da_card_images.py"
        if not bridge.exists():
            raise FileNotFoundError(f"Script ponte non trovato: {bridge}")

        cmd = [
            "python3",
            str(bridge),
            "--images-dir",
            str(images_dir),
            "--output",
            str(output_pdf),
            "--json-output",
            str(json_output),
            "--title",
            str(title),
            "--project-root",
            str(self.project_root),
        ]
        subprocess.run(cmd, cwd=self.project_root, check=True)

        if not output_pdf.exists() or output_pdf.stat().st_size < 1000:
            raise RuntimeError("PDF non generato o troppo piccolo")

        return output_pdf

    def send_pdf(self, pdf_path: Path, filename: str) -> None:
        download_name = safe_filename(filename, "card-generate.pdf")
        if not download_name.lower().endswith(".pdf"):
            download_name += ".pdf"

        data = pdf_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data: dict, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Server locale per esportare card generate in PDF.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8030, type=int)
    parser.add_argument("--root", default=".", help="Root progetto da servire")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    os.chdir(root)

    PdfExportHandler.project_root = root
    PdfExportHandler.tmp_root = root / "tmp" / "pdf_export"

    server = ThreadingHTTPServer((args.host, args.port), PdfExportHandler)
    print("Motore Scarica PDF Card avviato")
    print(f"Root: {root}")
    print(f"API:  http://{args.host}:{args.port}/api/export/cards-pdf")
    print(f"Demo: http://{args.host}:{args.port}/demo-rag/test-documenti-universale.html")
    print("Stop: Ctrl+C")
    server.serve_forever()


if __name__ == "__main__":
    main()
